"""
bayesian.py
-----------
Bayesian parameter estimation and uncertainty quantification for the V1.3 kinetic model.
Features:
1. Exact canonical transformed parameterization q = log(theta).
2. Log-likelihood with noise weighting (sigma_Y=0.01, sigma_DE=0.02, sigma_Mw=15,000 Da).
3. Affine-invariant ensemble MCMC sampling via emcee.
4. Posterior parameter distributions and 95% Bayesian Credible Intervals (BCIs).
5. Posterior Predictive Checks (PPC) on independent holdout validation conditions.
"""

from typing import List, Tuple, Dict, Any, Optional
import numpy as np
import pandas as pd
import json
import os
import emcee

from pectin.chemistry.kinetics import KineticParameters
from pectin.calibration.parameterization import (
    PARAM_NAMES,
    PARAM_BOUNDS,
    pack,
    unpack,
    transform,
    inverse_transform,
)
from pectin.calibration.sensitivity import (
    ExperimentCondition,
    forward_model,
    build_noise_weights,
    DEFAULT_SIGMAS,
)
from pectin.calibration.least_squares import fit
from pectin.calibration.experimental_design import generate_candidate_pool

# Ground truth parameters for synthetic test
GROUND_TRUTH_PARAMS = KineticParameters(
    k_ref_ext=0.05, Ea_ext=35000.0, alpha=1.0,
    k_ref_hyd=0.03, Ea_hyd=40000.0,
    k_ref_deg=0.01, Ea_deg=50000.0,
    k_ref_de=0.02,  Ea_de=45000.0,
    n_ext=1.0, n_hyd=1.0, n_deg=1.0, n_de=1.0,
    gamma_citric=0.0, beta_mw=1.0
)

# Prior means (log-space) and standard deviations
PRIOR_MEANS_LOG = np.array([
    np.log(0.05),   # k_ref_ext
    np.log(40000.0), # Ea_ext
    0.0,            # alpha (logit space, center = 1.35)
    np.log(0.03),   # k_ref_hyd
    np.log(45000.0), # Ea_hyd
    np.log(0.01),   # k_ref_deg
    np.log(55000.0), # Ea_deg
    np.log(0.02),   # k_ref_de
    np.log(50000.0), # Ea_de
])

PRIOR_STD_LOG = np.array([
    1.5,  # k_ref_ext (broad order of magnitude)
    0.8,  # Ea_ext (~2x range)
    1.5,  # alpha
    1.5,  # k_ref_hyd
    0.8,  # Ea_hyd
    1.5,  # k_ref_deg
    0.8,  # Ea_deg
    1.5,  # k_ref_de
    0.8,  # Ea_de
])

def log_prior(q: np.ndarray) -> float:
    """
    Gaussian log-prior in transformed space q.
    Enforces hard bounds on unreasonable extremes.
    """
    # Hard unconstrained bounding box check
    if np.any(q < -15.0) or np.any(q > 15.0):
        return -np.inf
        
    diff = (q - PRIOR_MEANS_LOG) / PRIOR_STD_LOG
    return -0.5 * np.sum(diff ** 2)

def log_likelihood(
    q: np.ndarray,
    conditions: List[ExperimentCondition],
    y_obs: np.ndarray,
    w: np.ndarray,
    obs_keys: Tuple[str, ...] = ("Y_GalA_product", "final_DE_product", "final_Mw_product")
) -> float:
    """
    Compute Gaussian log-likelihood for observed data:
    log L = -0.5 * sum [ ((y_sim - y_obs) / sigma)^2 + ln(2*pi*sigma^2) ]
    """
    try:
        y_sim = forward_model(q, conditions, obs_keys)
        if np.any(np.isnan(y_sim)) or np.any(np.isinf(y_sim)):
            return -np.inf
            
        residuals = w * (y_sim - y_obs)
        chi2 = np.sum(residuals ** 2)
        log_norm = np.sum(np.log(w / np.sqrt(2.0 * np.pi)))
        return float(log_norm - 0.5 * chi2)
    except Exception:
        return -np.inf

def log_posterior(
    q: np.ndarray,
    conditions: List[ExperimentCondition],
    y_obs: np.ndarray,
    w: np.ndarray,
    obs_keys: Tuple[str, ...] = ("Y_GalA_product", "final_DE_product", "final_Mw_product")
) -> float:
    """
    Unnormalized log-posterior: log p(q | D) = log p(D | q) + log p(q)
    """
    lp = log_prior(q)
    if not np.isfinite(lp):
        return -np.inf
    ll = log_likelihood(q, conditions, y_obs, w, obs_keys)
    if not np.isfinite(ll):
        return -np.inf
    return float(lp + ll)

def sample_posterior(
    conditions: List[ExperimentCondition],
    y_obs: np.ndarray,
    initial_q: np.ndarray,
    n_walkers: int = 32,
    n_steps: int = 600,
    burn_in: int = 200,
    seed: int = 42
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Run MCMC sampling using emcee.
    Returns:
      - flat_samples: (N_samples, 9) in natural parameter space theta
      - flat_q_samples: (N_samples, 9) in transformed space q
    """
    rng = np.random.default_rng(seed)
    n_dim = len(initial_q)
    w = build_noise_weights(conditions)
    
    # Initialize walkers in a tight ball around initial MAP/LS estimate
    pos0 = initial_q + 1e-2 * rng.normal(size=(n_walkers, n_dim))
    
    sampler = emcee.EnsembleSampler(
        n_walkers,
        n_dim,
        log_posterior,
        args=(conditions, y_obs, w)
    )
    
    print(f"Running MCMC ({n_walkers} walkers, {n_steps} steps, burn-in={burn_in})...")
    sampler.run_mcmc(pos0, n_steps, progress=True)
    
    flat_q_samples = sampler.get_chain(discard=burn_in, flat=True)
    
    # Transform to natural parameter space
    flat_samples = np.empty_like(flat_q_samples)
    for i in range(len(flat_q_samples)):
        flat_samples[i] = inverse_transform(flat_q_samples[i])
        
    return flat_samples, flat_q_samples

def evaluate_posterior_predictive(
    flat_q_samples: np.ndarray,
    validation_conditions: List[ExperimentCondition],
    y_val_true: np.ndarray,
    n_subsamples: int = 150,
    seed: int = 42
) -> Dict[str, Any]:
    """
    Perform Posterior Predictive Checks (PPC) on holdout validation conditions.
    Computes 95% Bayesian Credible Intervals on simulated responses.
    """
    rng = np.random.default_rng(seed)
    idx_choice = rng.choice(len(flat_q_samples), size=n_subsamples, replace=False)
    
    val_predictions = []
    for idx in idx_choice:
        q_samp = flat_q_samples[idx]
        y_pred = forward_model(q_samp, validation_conditions)
        val_predictions.append(y_pred)
        
    val_predictions = np.array(val_predictions) # Shape: (n_subsamples, N_obs_val)
    
    p025 = np.percentile(val_predictions, 2.5, axis=0)
    p500 = np.percentile(val_predictions, 50.0, axis=0)
    p975 = np.percentile(val_predictions, 97.5, axis=0)
    
    # Check coverage: does the 95% predictive interval contain the true value?
    inside_coverage = (y_val_true >= p025) & (y_val_true <= p975)
    coverage_pct = np.mean(inside_coverage) * 100.0
    
    return {
        "p025": p025.tolist(),
        "median": p500.tolist(),
        "p975": p975.tolist(),
        "coverage_pct": float(coverage_pct),
        "inside_coverage": inside_coverage.tolist()
    }

def run_bayesian_calibration():
    """
    Full Bayesian Calibration Pipeline:
    1. Take the 10-run OED calibration set + 4 holdout validation conditions.
    2. Generate noisy synthetic data (sigma_Y=0.01, sigma_DE=0.02, sigma_Mw=15,000 Da).
    3. Run least squares to find MAP start.
    4. Run MCMC to infer parameter posteriors.
    5. Compute 95% BCIs and check if true theta* lies within intervals.
    6. Perform Posterior Predictive Validation on holdout conditions.
    """
    theta_true = pack(GROUND_TRUTH_PARAMS)
    q_true = transform(theta_true)
    
    # 1. Define 10-run OED Calibration Design
    cal_conditions = [
        ExperimentCondition(50.0, 1.5, 45.0, 600.0),
        ExperimentCondition(95.0, 2.5, 90.0, 600.0),
        ExperimentCondition(50.0, 1.5, 120.0, 300.0),
        ExperimentCondition(95.0, 1.5, 20.0, 300.0),
        ExperimentCondition(95.0, 3.0, 90.0, 150.0),
        ExperimentCondition(50.0, 2.0, 45.0, 150.0),
        ExperimentCondition(95.0, 2.0, 20.0, 600.0),
        ExperimentCondition(50.0, 2.0, 120.0, 600.0),
        ExperimentCondition(50.0, 1.5, 120.0, 150.0),
        ExperimentCondition(95.0, 1.5, 20.0, 150.0),
    ]
    
    # 2. Define 4 Independent Holdout Validation Conditions (Intermediate operating space)
    val_conditions = [
        ExperimentCondition(70.0, 2.0, 45.0, 300.0),
        ExperimentCondition(80.0, 1.8, 30.0, 300.0),
        ExperimentCondition(65.0, 2.5, 60.0, 150.0),
        ExperimentCondition(85.0, 1.5, 15.0, 600.0),
    ]
    
    print("=" * 80)
    print("      V1.3 BAYESIAN MCMC CALIBRATION & UNCERTAINTY QUANTIFICATION")
    print("=" * 80)
    print(f"Calibration Experiments: {len(cal_conditions)} (30 observations)")
    print(f"Holdout Validation Experiments: {len(val_conditions)} (12 observations)")
    
    # Generate noisy synthetic observations
    rng = np.random.default_rng(42)
    y_cal_clean = forward_model(q_true, cal_conditions)
    w_cal = build_noise_weights(cal_conditions)
    y_cal_noisy = y_cal_clean + rng.normal(0.0, 1.0 / w_cal)
    
    y_val_clean = forward_model(q_true, val_conditions)
    
    # 3. Find MAP / initial guess via least squares
    print("\nEstimating initial MAP parameter mode via nonlinear least squares...")
    ls_fit = fit(cal_conditions, y_cal_noisy, theta_true * 1.1)
    q_map = ls_fit.q_opt
    
    # 4. Run MCMC
    flat_samples, flat_q_samples = sample_posterior(
        conditions=cal_conditions,
        y_obs=y_cal_noisy,
        initial_q=q_map,
        n_walkers=32,
        n_steps=500,
        burn_in=150,
        seed=42
    )
    
    # 5. Parameter Posterior Statistics
    print("\n--- Posterior Parameter Distributions (95% BCI) ---")
    rows = []
    for i, name in enumerate(PARAM_NAMES):
        truth = theta_true[i]
        chain = flat_samples[:, i]
        p025 = np.percentile(chain, 2.5)
        p50 = np.percentile(chain, 50.0)
        p975 = np.percentile(chain, 97.5)
        
        covered = "YES" if (p025 <= truth <= p975) else "NO"
        
        rows.append({
            "Parameter": name,
            "Truth": f"{truth:.4g}",
            "Posterior Median": f"{p50:.4g}",
            "2.5% BCI": f"{p025:.4g}",
            "97.5% BCI": f"{p975:.4g}",
            "Truth in 95% BCI?": covered
        })
        
    df_params = pd.DataFrame(rows)
    print(df_params.to_string(index=False))
    
    # 6. Posterior Predictive Check on Holdout Validation Data
    print("\n--- Posterior Predictive Check (PPC) on Holdout Validation Set ---")
    ppc_res = evaluate_posterior_predictive(flat_q_samples, val_conditions, y_val_clean)
    print(f"Validation Observation Coverage (95% Interval): {ppc_res['coverage_pct']:.1f}%")
    
    obs_names = ["Yield (GalA)", "DE (product)", "Mw (product)"]
    val_table = []
    for c_idx, cond in enumerate(val_conditions):
        for o_idx, oname in enumerate(obs_names):
            k = c_idx * 3 + o_idx
            truth_val = y_val_clean[k]
            p025_val = ppc_res['p025'][k]
            p50_val = ppc_res['median'][k]
            p975_val = ppc_res['p975'][k]
            
            # Format nicely
            if "Mw" in oname:
                val_table.append({
                    "Condition": f"T={cond.temperature_celsius}C, pH={cond.pH}, t={cond.time_min}m",
                    "Metric": oname,
                    "Truth": f"{truth_val:.0f} Da",
                    "PPC Median (95% CI)": f"{p50_val:.0f} [{p025_val:.0f} - {p975_val:.0f}]",
                    "Valid?": "YES" if (p025_val <= truth_val <= p975_val) else "NO"
                })
            else:
                val_table.append({
                    "Condition": f"T={cond.temperature_celsius}C, pH={cond.pH}, t={cond.time_min}m",
                    "Metric": oname,
                    "Truth": f"{truth_val*100:.2f}%",
                    "PPC Median (95% CI)": f"{p50_val*100:.2f}% [{p025_val*100:.2f}% - {p975_val*100:.2f}%]",
                    "Valid?": "YES" if (p025_val <= truth_val <= p975_val) else "NO"
                })
                
    df_val = pd.DataFrame(val_table)
    print(df_val.to_string(index=False))
    
    # Save artifacts
    os.makedirs("artifacts/calibration", exist_ok=True)
    df_params.to_csv("artifacts/calibration/bayesian_posterior_parameters.csv", index=False)
    df_val.to_csv("artifacts/calibration/bayesian_validation_ppc.csv", index=False)
    
    print("\nSaved Bayesian calibration and validation artifacts to artifacts/calibration/")

if __name__ == "__main__":
    run_bayesian_calibration()
