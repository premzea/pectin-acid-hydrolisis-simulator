"""
identifiability.py
------------------
Experimental design definitions (A through E) and automated identifiability battery.
Computes SVD spectrum, condition numbers, correlation matrices, and runs local/global
multi-start parameter recovery tests.
"""

from typing import List, Tuple, Dict, Any
import numpy as np
import pandas as pd
import os
import json

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
    DEFAULT_SIGMAS,
)
from pectin.calibration.least_squares import (
    multistart_fit,
)

# Ground truth parameter vector theta* for the synthetic study
GROUND_TRUTH_PARAMS = KineticParameters(
    k_ref_ext=0.05, Ea_ext=35000.0, alpha=1.0,
    k_ref_hyd=0.03, Ea_hyd=40000.0,
    k_ref_deg=0.01, Ea_deg=50000.0,
    k_ref_de=0.02,  Ea_de=45000.0,
    n_ext=1.0, n_hyd=1.0, n_deg=1.0, n_de=1.0,
    gamma_citric=0.0, beta_mw=1.0
)

# --- Experimental Design Definitions ---

def design_A() -> List[ExperimentCondition]:
    """
    Design A: Factorial grid (T, pH), single final time (t=60 min), d50=300 um.
    Endpoint observations only (9 experiments).
    """
    conditions = []
    temps = [60.0, 75.0, 90.0]
    phs = [1.5, 2.0, 3.0]
    for T in temps:
        for ph in phs:
            conditions.append(ExperimentCondition(temperature_celsius=T, pH=ph, time_min=60.0, d50_um=300.0))
    return conditions

def design_B() -> List[ExperimentCondition]:
    """
    Design B: Single condition (T=80C, pH=2.0, d50=300 um), multi-point time series.
    Kinetic trajectory (7 experiments).
    """
    times = [5.0, 15.0, 30.0, 45.0, 60.0, 90.0, 120.0]
    return [ExperimentCondition(temperature_celsius=80.0, pH=2.0, time_min=t, d50_um=300.0) for t in times]

def design_C() -> List[ExperimentCondition]:
    """
    Design C: Multi-temperature series (T in [50, 65, 80, 95] C), fixed pH=2.0, d50=300 um.
    Time points [15, 45, 90] min (12 experiments).
    """
    conditions = []
    temps = [50.0, 65.0, 80.0, 95.0]
    times = [15.0, 45.0, 90.0]
    for T in temps:
        for t in times:
            conditions.append(ExperimentCondition(temperature_celsius=T, pH=2.0, time_min=t, d50_um=300.0))
    return conditions

def design_D() -> List[ExperimentCondition]:
    """
    Design D: Multi-particle size (d50 in [150, 300, 600] um) at T=80C, pH=2.0.
    Time points [15, 45, 90] min (9 experiments).
    """
    conditions = []
    sizes = [150.0, 300.0, 600.0]
    times = [15.0, 45.0, 90.0]
    for d50 in sizes:
        for t in times:
            conditions.append(ExperimentCondition(temperature_celsius=80.0, pH=2.0, time_min=t, d50_um=d50))
    return conditions

def design_E() -> List[ExperimentCondition]:
    """
    Design E: Combined Information-Rich Design (14 carefully chosen conditions).
    Spans T (55, 75, 95 C), pH (1.5, 2.5), t (10, 30, 60, 90 min), and d50 (150, 300, 600 um).
    """
    return [
        # Multi-temp & pH dynamics at standard size
        ExperimentCondition(temperature_celsius=55.0, pH=1.5, time_min=30.0, d50_um=300.0),
        ExperimentCondition(temperature_celsius=55.0, pH=1.5, time_min=90.0, d50_um=300.0),
        ExperimentCondition(temperature_celsius=75.0, pH=1.5, time_min=15.0, d50_um=300.0),
        ExperimentCondition(temperature_celsius=75.0, pH=1.5, time_min=60.0, d50_um=300.0),
        ExperimentCondition(temperature_celsius=75.0, pH=2.5, time_min=30.0, d50_um=300.0),
        ExperimentCondition(temperature_celsius=75.0, pH=2.5, time_min=90.0, d50_um=300.0),
        ExperimentCondition(temperature_celsius=95.0, pH=1.5, time_min=10.0, d50_um=300.0),
        ExperimentCondition(temperature_celsius=95.0, pH=1.5, time_min=45.0, d50_um=300.0),
        ExperimentCondition(temperature_celsius=95.0, pH=2.5, time_min=30.0, d50_um=300.0),
        ExperimentCondition(temperature_celsius=95.0, pH=2.5, time_min=75.0, d50_um=300.0),
        # Particle size probes
        ExperimentCondition(temperature_celsius=75.0, pH=2.0, time_min=20.0, d50_um=150.0),
        ExperimentCondition(temperature_celsius=75.0, pH=2.0, time_min=60.0, d50_um=150.0),
        ExperimentCondition(temperature_celsius=75.0, pH=2.0, time_min=20.0, d50_um=600.0),
        ExperimentCondition(temperature_celsius=75.0, pH=2.0, time_min=60.0, d50_um=600.0),
    ]

DESIGNS = {
    "Design A (Endpoint Factorial)": design_A,
    "Design B (Time Series)": design_B,
    "Design C (Temperature Series)": design_C,
    "Design D (Particle Size Series)": design_D,
    "Design E (Combined Info-Rich)": design_E,
}

def run_battery(n_multistarts: int = 20, seed: int = 42) -> Dict[str, Any]:
    """
    Run full identifiability and parameter recovery battery across Designs A-E.
    """
    theta_true = pack(GROUND_TRUTH_PARAMS)
    q_true = transform(theta_true)
    
    os.makedirs("artifacts/calibration", exist_ok=True)
    report_data = {}
    
    print("=" * 80)
    print("      V1.3 KINETIC PARAMETER IDENTIFIABILITY & RECOVERY BATTERY")
    print("=" * 80)
    print(f"Ground truth theta*:\n{dict(zip(PARAM_NAMES, [f'{v:.4g}' for v in theta_true]))}\n")
    
    for name, design_fn in DESIGNS.items():
        print("-" * 80)
        print(f"Executing: {name}")
        conditions = design_fn()
        n_exp = len(conditions)
        n_obs = n_exp * 3 # (Y_GalA, DE, Mw)
        print(f"  Experiments: {n_exp} | Observations: {n_obs}")
        
        # 1. Sensitivity, FIM, and SVD Analysis
        S_tilde, diag = analyze_sensitivity(q_true, conditions)
        
        s = diag.singular_values
        cond_num = diag.condition_number
        print(f"  Condition Number kappa(F): {cond_num:.2e}")
        print(f"  Singular Values (sigma_1 to sigma_9):")
        s_str = ", ".join([f"{val:.2e}" for val in s])
        print(f"    [{s_str}]")
        print(f"  Dynamic Range (sigma_9 / sigma_1): {s[-1] / s[0]:.2e}")
        
        # 2. Local Multistart Recovery Test (Noiseless)
        print(f"\n  Running Local Multistart Recovery ({n_multistarts} starts, ~25% perturbation)...")
        summary_local = multistart_fit(
            conditions=conditions,
            theta_true=theta_true,
            n_starts=n_multistarts,
            mode="local",
            seed=seed
        )
        
        # 3. Global Multistart Recovery Test (Noiseless)
        print(f"  Running Global Multistart Recovery ({n_multistarts} starts, physical bounds)...")
        summary_global = multistart_fit(
            conditions=conditions,
            theta_true=theta_true,
            n_starts=n_multistarts,
            mode="global",
            seed=seed
        )
        
        # Build Parameter Recovery Summary Table
        table_rows = []
        for i, pname in enumerate(PARAM_NAMES):
            truth = theta_true[i]
            med_loc = summary_local.median_recovered[i]
            err_loc = summary_local.relative_errors_pct[i]
            sd_loc = summary_local.std_recovered[i]
            
            med_glob = summary_global.median_recovered[i]
            err_glob = summary_global.relative_errors_pct[i]
            
            _, classif, std_err = diag.identifiability_ranking[i]
            
            # Simple identifiability judgment: < 5% error on local and well-conditioned
            identifiable = "Yes" if err_loc < 5.0 and std_err < 0.50 else "Weak/No"
            
            table_rows.append({
                "Parameter": pname,
                "Truth": truth,
                "Local Est (Median)": med_loc,
                "Local Err (%)": err_loc,
                "Global Err (%)": err_glob,
                "Classif (FIM)": classif,
                "Identifiable?": identifiable
            })
            
        df_table = pd.DataFrame(table_rows)
        print("\n" + df_table.to_string(index=False))
        print("-" * 80)
        
        # Save design artifacts
        clean_name = name.split()[1].lower() # a, b, c, d, e
        csv_path = f"artifacts/calibration/identifiability_{clean_name}.csv"
        df_table.to_csv(csv_path, index=False)
        
        report_data[name] = {
            "n_experiments": n_exp,
            "n_observations": n_obs,
            "condition_number": cond_num,
            "singular_values": s.tolist(),
            "singular_ratio": float(s[-1] / s[0]),
            "correlation_matrix": diag.correlation_matrix.tolist(),
            "local_recovery_success": summary_local.n_success,
            "global_recovery_success": summary_global.n_success,
            "table": table_rows
        }
        
    with open("artifacts/calibration/identifiability_summary.json", "w") as f:
        json.dump(report_data, f, indent=4)
    print("\nSaved all summary artifacts to artifacts/calibration/")
    return report_data

if __name__ == "__main__":
    run_battery(n_multistarts=10)
