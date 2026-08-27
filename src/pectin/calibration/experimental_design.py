"""
experimental_design.py
----------------------
Optimal Experimental Design (OED) for the 9-parameter V1.3 pectin hydrolysis system.
Implements:
1. Candidate pool generation across operational ranges (T, pH, d50, time).
2. Bayesian D-Optimal forward selection: max log(det(F_prior + sum F_i)).
3. Marginal information gain trajectory (N=1 to N=20).
4. Prediction-oriented (V-optimal) evaluation around target operational optimum.
"""

from typing import List, Tuple, Dict, Any, Optional
import numpy as np
import pandas as pd
import json
import os

from pectin.chemistry.kinetics import KineticParameters
from pectin.calibration.parameterization import (
    PARAM_NAMES,
    pack,
    unpack,
    transform,
)
from pectin.calibration.sensitivity import (
    ExperimentCondition,
    analyze_sensitivity,
    compute_jacobian,
    build_noise_weights,
    DEFAULT_SIGMAS,
)

# Reference ground truth parameter vector
REFERENCE_PARAMS = KineticParameters(
    k_ref_ext=0.05, Ea_ext=35000.0, alpha=1.0,
    k_ref_hyd=0.03, Ea_hyd=40000.0,
    k_ref_deg=0.01, Ea_deg=50000.0,
    k_ref_de=0.02,  Ea_de=45000.0,
    n_ext=1.0, n_hyd=1.0, n_deg=1.0, n_de=1.0,
    gamma_citric=0.0, beta_mw=1.0
)

def generate_candidate_pool() -> List[ExperimentCondition]:
    """
    Generate a discrete grid of physically realizable candidate reactor experiments.
    Spans:
      - 6 temperatures: [50, 60, 70, 80, 90, 95] °C
      - 4 pH levels: [1.5, 2.0, 2.5, 3.0]
      - 3 particle sizes: [150, 300, 600] um
      - 8 residence times: [5, 10, 20, 30, 45, 60, 90, 120] min
    Total: 576 candidate points.
    """
    temps = [50.0, 60.0, 70.0, 80.0, 90.0, 95.0]
    phs = [1.5, 2.0, 2.5, 3.0]
    sizes = [150.0, 300.0, 600.0]
    times = [5.0, 10.0, 20.0, 30.0, 45.0, 60.0, 90.0, 120.0]
    
    candidates = []
    for T in temps:
        for ph in phs:
            for d50 in sizes:
                for t in times:
                    candidates.append(
                        ExperimentCondition(
                            temperature_celsius=T,
                            pH=ph,
                            time_min=t,
                            d50_um=d50
                        )
                    )
    return candidates

def precompute_candidate_fims(
    candidates: List[ExperimentCondition],
    q_ref: np.ndarray,
    obs_keys: Tuple[str, ...] = ("Y_GalA_product", "final_DE_product", "final_Mw_product"),
    sigmas: Dict[str, float] = None
) -> List[np.ndarray]:
    """
    Precompute the 9x9 Fisher Information Matrix contribution F_i = S_tilde_i^T * S_tilde_i
    for each candidate experiment i.
    """
    if sigmas is None:
        sigmas = DEFAULT_SIGMAS
        
    fims = []
    for cond in candidates:
        J = compute_jacobian(q_ref, [cond], obs_keys)
        w = build_noise_weights([cond], obs_keys, sigmas)
        S_tilde = J * w[:, np.newaxis]
        F_i = S_tilde.T @ S_tilde
        fims.append(F_i)
        
    return fims

def build_prior_fim(prior_std_log: float = 2.0) -> np.ndarray:
    """
    Construct a weak uninformative Bayesian prior Fisher Information Matrix.
    F_prior = diag(1 / sigma_prior^2).
    A prior std of 2.0 in log-space corresponds to a wide order-of-magnitude prior.
    """
    n_params = len(PARAM_NAMES)
    var_prior = prior_std_log ** 2
    return np.eye(n_params, dtype=np.float64) / var_prior

def sequential_d_optimal_selection(
    candidates: List[ExperimentCondition],
    fims: List[np.ndarray],
    budget: int = 16,
    prior_fim: Optional[np.ndarray] = None
) -> Tuple[List[int], List[float], List[np.ndarray]]:
    """
    Sequential greedy forward D-optimal selection.
    At each step k, selects the candidate j that maximizes log(det(F_current + F_j)).
    
    Returns:
      - selected_indices: list of candidate indices chosen in order
      - logdet_trajectory: evolution of log(det(F_post)) at each step
      - cumulative_fims: history of accumulated FIMs
    """
    if prior_fim is None:
        prior_fim = build_prior_fim(prior_std_log=2.0)
        
    n_candidates = len(candidates)
    F_current = prior_fim.copy()
    
    selected_indices = []
    logdet_trajectory = []
    cumulative_fims = []
    
    # Track available candidates (allows replication if needed, or unique selection)
    available_mask = np.ones(n_candidates, dtype=bool)
    
    for step in range(budget):
        best_gain = -np.inf
        best_idx = -1
        best_F_next = None
        
        for i in range(n_candidates):
            if not available_mask[i]:
                continue
                
            F_test = F_current + fims[i]
            # Numerically stable logdet via slogdet
            sign, logdet = np.linalg.slogdet(F_test)
            if sign > 0 and logdet > best_gain:
                best_gain = logdet
                best_idx = i
                best_F_next = F_test
                
        if best_idx == -1:
            break
            
        selected_indices.append(best_idx)
        logdet_trajectory.append(best_gain)
        F_current = best_F_next
        cumulative_fims.append(F_current)
        available_mask[best_idx] = False # No duplicate experiments in initial set
        
    return selected_indices, logdet_trajectory, cumulative_fims

def run_experimental_design_study(max_budget: int = 16) -> Dict[str, Any]:
    """
    Execute full D-optimal experimental design pipeline:
    1. Grid candidate space.
    2. Compute individual sensitivities.
    3. Run greedy forward selection.
    4. Compute marginal information gain curve.
    5. Evaluate the final recommended protocol.
    """
    theta_ref = pack(REFERENCE_PARAMS)
    q_ref = transform(theta_ref)
    
    print("=" * 80)
    print("      V1.3 BAYESIAN D-OPTIMAL EXPERIMENTAL DESIGN (OED) OPTIMIZER")
    print("=" * 80)
    
    candidates = generate_candidate_pool()
    print(f"Generated discrete candidate pool: {len(candidates)} experimental conditions")
    print("Computing candidate sensitivities and Fisher Information Matrices...")
    
    fims = precompute_candidate_fims(candidates, q_ref)
    prior_fim = build_prior_fim(prior_std_log=2.0)
    
    print(f"\nRunning sequential greedy D-optimal selection for budget N = {max_budget}...")
    selected_indices, logdets, cum_fims = sequential_d_optimal_selection(
        candidates, fims, budget=max_budget, prior_fim=prior_fim
    )
    
    # Calculate marginal gains
    initial_logdet = np.linalg.slogdet(prior_fim)[1]
    marginal_gains = []
    prev_logdet = initial_logdet
    for ld in logdets:
        marginal_gains.append(ld - prev_logdet)
        prev_logdet = ld
        
    # Build recommended experimental protocol table
    table_rows = []
    print("\nRecommended Sequential Experimental Protocol:")
    print("-" * 80)
    for step, (idx, ld, mg) in enumerate(zip(selected_indices, logdets, marginal_gains), 1):
        cond = candidates[idx]
        F_step = cum_fims[step - 1]
        s_vals = np.linalg.svd(F_step, compute_uv=False)
        cond_num = s_vals[0] / max(s_vals[-1], 1e-15)
        
        row = {
            "Run #": step,
            "T (°C)": cond.temperature_celsius,
            "pH": cond.pH,
            "d50 (um)": cond.d50_um,
            "Time (min)": cond.time_min,
            "log|F|": round(float(ld), 2),
            "Marginal Gain": round(float(mg), 2),
            "kappa(F)": f"{cond_num:.1e}",
            "sigma_min": f"{np.sqrt(s_vals[-1]):.2f}"
        }
        table_rows.append(row)
        
    df_protocol = pd.DataFrame(table_rows)
    print(df_protocol.to_string(index=False))
    print("-" * 80)
    
    # Final FIM diagnostics for selected set
    F_final = cum_fims[-1]
    s_final = np.sqrt(np.linalg.svd(F_final - prior_fim, compute_uv=False)) # Data-only singular values
    
    print("\n--- Final OED Set Diagnostics (Data-Only FIM) ---")
    print(f"  Condition number kappa(F): {(s_final[0]/s_final[-1])**2:.2f}")
    print(f"  Singular spectrum (sigma_1 .. sigma_9):")
    print(f"    [{', '.join([f'{v:.2f}' for v in s_final])}]")
    print(f"  Singular ratio (sigma_9 / sigma_1): {s_final[-1]/s_final[0]:.3f}")
    
    # Save artifacts
    os.makedirs("artifacts/calibration", exist_ok=True)
    df_protocol.to_csv("artifacts/calibration/d_optimal_protocol.csv", index=False)
    
    results = {
        "budget": max_budget,
        "selected_conditions": [
            {
                "run": i + 1,
                "temperature": candidates[idx].temperature_celsius,
                "pH": candidates[idx].pH,
                "d50_um": candidates[idx].d50_um,
                "time_min": candidates[idx].time_min,
                "logdet": float(ld),
                "marginal_gain": float(mg)
            }
            for i, (idx, ld, mg) in enumerate(zip(selected_indices, logdets, marginal_gains))
        ],
        "final_singular_values": s_final.tolist(),
        "final_condition_number": float((s_final[0]/s_final[-1])**2)
    }
    
    with open("artifacts/calibration/d_optimal_summary.json", "w") as f:
        json.dump(results, f, indent=4)
        
    print("\nSaved design protocol to artifacts/calibration/d_optimal_protocol.csv")
    return results

if __name__ == "__main__":
    run_experimental_design_study(max_budget=16)
