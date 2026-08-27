"""
posterior_analysis.py
---------------------
Post-MCMC diagnostic analysis:
1. Posterior parameter correlation matrix.
2. Optimum distribution: sample theta^(s) from posterior, optimize, get P(x* | D).
3. Model mismatch test: generate data with perturbed simulator, fit V1.3 model.
"""

from typing import List, Tuple, Dict, Any
import numpy as np
import pandas as pd
import json
import os

from scipy.optimize import differential_evolution

from pectin.chemistry.kinetics import KineticParameters
from pectin.calibration.parameterization import (
    PARAM_NAMES, pack, unpack, transform, inverse_transform,
    sample_initial_guesses
)
from pectin.calibration.sensitivity import (
    ExperimentCondition, forward_model, build_noise_weights, DEFAULT_SIGMAS
)
from pectin.calibration.bayesian import (
    GROUND_TRUTH_PARAMS, log_posterior, sample_posterior
)
from pectin.calibration.least_squares import fit

# ---------------------------------------------------------------------------
# Re-export the calibration conditions from bayesian.py
# ---------------------------------------------------------------------------
CALIBRATION_CONDITIONS = [
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

OBS_KEYS = ("Y_GalA_product", "final_DE_product", "final_Mw_product")


def run_mcmc_and_get_samples(seed: int = 42) -> Tuple[np.ndarray, np.ndarray]:
    """Re-run MCMC to get posterior samples for analysis."""
    theta_true = pack(GROUND_TRUTH_PARAMS)
    q_true = transform(theta_true)

    rng = np.random.default_rng(seed)
    y_cal_clean = forward_model(q_true, CALIBRATION_CONDITIONS)
    w_cal = build_noise_weights(CALIBRATION_CONDITIONS)
    y_cal_noisy = y_cal_clean + rng.normal(0.0, 1.0 / w_cal)

    ls_fit = fit(CALIBRATION_CONDITIONS, y_cal_noisy, theta_true * 1.1)
    q_map = ls_fit.q_opt

    flat_samples, flat_q_samples = sample_posterior(
        conditions=CALIBRATION_CONDITIONS,
        y_obs=y_cal_noisy,
        initial_q=q_map,
        n_walkers=32,
        n_steps=500,
        burn_in=150,
        seed=seed
    )
    return flat_samples, flat_q_samples


# ---------------------------------------------------------------------------
# 1. Posterior Correlation Matrix
# ---------------------------------------------------------------------------

def compute_posterior_correlations(flat_samples: np.ndarray) -> pd.DataFrame:
    """
    Compute and display the posterior parameter correlation matrix.
    """
    corr = np.corrcoef(flat_samples.T)
    df = pd.DataFrame(corr, index=PARAM_NAMES, columns=PARAM_NAMES)
    return df


def report_key_correlations(corr_df: pd.DataFrame) -> None:
    """
    Report the structurally interesting parameter pair correlations.
    """
    pairs = [
        ("k_ref_ext", "Ea_ext",  "Rate-Energy (Extraction)"),
        ("k_ref_hyd", "Ea_hyd",  "Rate-Energy (Hydrolysis)"),
        ("k_ref_deg", "Ea_deg",  "Rate-Energy (Degradation)"),
        ("k_ref_de",  "Ea_de",   "Rate-Energy (De-esterification)"),
        ("k_ref_hyd", "k_ref_deg", "Hydrolysis-Degradation rate coupling"),
        ("Ea_hyd",    "Ea_deg",    "Hydrolysis-Degradation Ea coupling"),
        ("k_ref_ext", "alpha",     "Extraction rate - particle size"),
    ]
    print("\n--- Key Posterior Parameter Correlations ---")
    print(f"{'Pair':<45} {'Corr':>8}")
    print("-" * 55)
    for p1, p2, label in pairs:
        r = corr_df.loc[p1, p2]
        flag = " *** HIGH" if abs(r) > 0.5 else ""
        print(f"{label:<45} {r:>8.3f}{flag}")


# ---------------------------------------------------------------------------
# 2. Optimum Distribution P(x* | D)
# ---------------------------------------------------------------------------

def optimum_from_theta(theta: np.ndarray, DE_min: float = 0.40, MW_min: float = 50000.0) -> Dict:
    """
    Given a single parameter vector theta, find the constrained optimum x*.
    Returns dict with T*, pH*, t* and predicted Y_GalA, DE, Mw.
    """
    q = transform(theta)

    def neg_yield_with_penalty(x):
        cond = ExperimentCondition(
            temperature_celsius=x[0],
            pH=x[1],
            time_min=x[2],
            d50_um=300.0
        )
        try:
            # forward_model returns flat array; single condition => [Y, DE, Mw]
            preds = forward_model(q, [cond])
        except Exception:
            return 1e6
        y_gala, final_de, final_mw = preds[0], preds[1], preds[2]
        penalty = 0.0
        if final_de < DE_min:
            penalty += (DE_min - final_de) * 500
        if final_mw < MW_min:
            penalty += (MW_min - final_mw) / 2000
        return -y_gala + penalty

    bounds = [(45.0, 100.0), (1.2, 4.5), (5.0, 120.0)]
    res = differential_evolution(neg_yield_with_penalty, bounds, seed=0,
                                 popsize=10, maxiter=30, tol=1e-4)
    x = res.x
    cond_opt = ExperimentCondition(x[0], x[1], x[2], 300.0)
    preds = forward_model(q, [cond_opt])  # flat [Y, DE, Mw]

    return {
        "T_opt": float(x[0]),
        "pH_opt": float(x[1]),
        "t_opt": float(x[2]),
        "Y_GalA": float(preds[0]),
        "DE_product": float(preds[1]),
        "Mw_product": float(preds[2]),
    }


def posterior_optimum_distribution(flat_samples: np.ndarray,
                                   n_draws: int = 100,
                                   seed: int = 42) -> pd.DataFrame:
    """
    For each of n_draws posterior samples, find the constrained optimum.
    Returns a DataFrame of optimum distributions.
    """
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(flat_samples), size=n_draws, replace=False)

    print(f"\nComputing posterior optimum distribution ({n_draws} posterior draws)...")
    rows = []
    for i, k in enumerate(idx):
        theta_samp = flat_samples[k]
        try:
            result = optimum_from_theta(theta_samp)
            rows.append(result)
        except Exception:
            pass
        if (i + 1) % 10 == 0:
            print(f"  {i+1}/{n_draws} draws processed...")

    return pd.DataFrame(rows)


def report_optimum_distribution(df_opt: pd.DataFrame) -> None:
    """Report posterior optimum statistics."""
    print("\n--- Posterior Distribution of Process Optimum P(x* | D) ---")
    print(f"  (Based on {len(df_opt)} posterior draws, DE_min=40%, MW_min=50 kDa)\n")

    fields = {
        "T* (degC)": "T_opt",
        "pH*": "pH_opt",
        "t* (min)": "t_opt",
        "Y_GalA* (%)": "Y_GalA",
        "DE_product* (%)": "DE_product",
        "Mw_product* (Da)": "Mw_product",
    }

    scale = {"Y_GalA* (%)": 100, "DE_product* (%)": 100}

    print(f"{'Variable':<20} {'Median':>10} {'2.5%':>10} {'97.5%':>10} {'Std':>10}")
    print("-" * 65)
    for label, col in fields.items():
        data = df_opt[col].values
        sc = scale.get(label, 1.0)
        p50  = np.percentile(data, 50)  * sc
        p025 = np.percentile(data, 2.5) * sc
        p975 = np.percentile(data, 97.5)* sc
        std  = np.std(data)             * sc
        print(f"{label:<20} {p50:>10.2f} {p025:>10.2f} {p975:>10.2f} {std:>10.2f}")


# ---------------------------------------------------------------------------
# 3. Model-Mismatch Test
# ---------------------------------------------------------------------------

def mismatch_delta(condition: ExperimentCondition, scale: float = 0.04) -> float:
    """
    Systematic model discrepancy: a nonlinear T/pH interaction on yield
    not captured by V1.3.
    delta = +scale * sin(pi * (T-50)/(95-50)) * sin(pi * (pH-1.5)/(3.0-1.5))
    This peaks at intermediate T/pH and is zero at the design extremes.
    """
    T_norm = (condition.temperature_celsius - 50.0) / (95.0 - 50.0)
    pH_norm = (condition.pH - 1.5) / (3.0 - 1.5)
    return scale * np.sin(np.pi * T_norm) * np.sin(np.pi * pH_norm)


def run_model_mismatch_test(flat_samples_baseline: np.ndarray, seed: int = 42) -> None:
    """
    Generate synthetic data from V1.3 + structured discrepancy delta(x).
    Fit the V1.3 Bayesian model without delta(x).
    Report parameter bias and PPC coverage degradation.
    """
    theta_true = pack(GROUND_TRUTH_PARAMS)
    q_true = transform(theta_true)
    rng = np.random.default_rng(seed)

    w_cal = build_noise_weights(CALIBRATION_CONDITIONS)
    y_clean = forward_model(q_true, CALIBRATION_CONDITIONS, OBS_KEYS)

    # Inject mismatch only on Y_GalA (index 0 of each triplet)
    y_mismatch = y_clean.copy()
    for i, cond in enumerate(CALIBRATION_CONDITIONS):
        delta = mismatch_delta(cond)
        y_mismatch[i * 3] += delta  # perturb GalA yield only

    y_obs = y_mismatch + rng.normal(0.0, 1.0 / w_cal)

    # Fit the unperturbed V1.3 Bayesian model to the mismatch-contaminated data
    ls_fit = fit(CALIBRATION_CONDITIONS, y_obs, theta_true * 1.1)
    q_map = ls_fit.q_opt

    flat_mis, flat_q_mis = sample_posterior(
        conditions=CALIBRATION_CONDITIONS,
        y_obs=y_obs,
        initial_q=q_map,
        n_walkers=32,
        n_steps=400,
        burn_in=150,
        seed=seed
    )

    # Compare posteriors: mismatch vs. baseline
    print("\n--- Model-Mismatch Test ---")
    print("  Synthetic data = V1.3 + nonlinear T/pH interaction on GalA yield (delta ~ 4%)")
    print(f"  {'Parameter':<15} {'Truth':>10} {'Baseline Med':>14} {'Mismatch Med':>14} {'Bias':>10} {'Covered?':>10}")
    print("  " + "-" * 76)

    for i, name in enumerate(PARAM_NAMES):
        truth = theta_true[i]
        med_base = np.median(flat_samples_baseline[:, i])
        p025_mis = np.percentile(flat_mis[:, i], 2.5)
        p975_mis = np.percentile(flat_mis[:, i], 97.5)
        med_mis  = np.median(flat_mis[:, i])
        bias_pct = (med_mis - truth) / truth * 100
        covered  = "YES" if (p025_mis <= truth <= p975_mis) else "NO ***"
        print(f"  {name:<15} {truth:>10.4g} {med_base:>14.4g} {med_mis:>14.4g} {bias_pct:>9.1f}% {covered:>10}")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    os.makedirs("artifacts/calibration", exist_ok=True)

    print("Re-running MCMC to obtain posterior samples for analysis...")
    flat_samples, flat_q_samples = run_mcmc_and_get_samples(seed=42)

    # 1. Posterior correlations
    corr_df = compute_posterior_correlations(flat_samples)
    report_key_correlations(corr_df)
    corr_df.to_csv("artifacts/calibration/posterior_correlation_matrix.csv")
    print("\nFull correlation matrix saved to artifacts/calibration/posterior_correlation_matrix.csv")

    # 2. Optimum distribution
    df_opt = posterior_optimum_distribution(flat_samples, n_draws=80, seed=42)
    report_optimum_distribution(df_opt)
    df_opt.to_csv("artifacts/calibration/posterior_optimum_distribution.csv", index=False)
    print("Optimum distribution saved to artifacts/calibration/posterior_optimum_distribution.csv")

    # 3. Model mismatch test
    run_model_mismatch_test(flat_samples, seed=42)
