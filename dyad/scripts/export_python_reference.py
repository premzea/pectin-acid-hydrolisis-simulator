"""
Export reference simulation trajectories from the Python V1.3 digital twin.
These reference trajectories are saved to a JSON fixture to allow bitwise/tolerance
parity testing against the JuliaHub Dyad ModelingToolkit implementation.
"""

import json
import os
from pathlib import Path
import numpy as np

from pectin.feedstock.properties import ConditionedFeedstock
from pectin.chemistry.kinetics import KineticParameters
from pectin.simulator.solver import simulate

def export_reference_runs():
    output_dir = Path(__file__).parent.parent / "tests" / "fixtures"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "python_reference_trajectories.json"
    
    # Standard baseline feedstock
    feedstock = ConditionedFeedstock(
        dry_matter_mass=0.15,
        moisture_fraction=0.08,
        pectin_mass=0.035, # 0.035 / 0.15 = 0.2333 kg/kg_dry_feed
        GalA_fraction=0.78,
        DE=0.745,
        Mw_matrix=654000.0,
        d50_um=300.0
    )
    
    # Standard V1.3 kinetic parameters
    kinetic_params = KineticParameters(
        k_ref_ext=0.035,
        Ea_ext=45000.0,
        n_ext=1.0,
        alpha=1.0,
        k_ref_hyd=0.015,
        Ea_hyd=65000.0,
        n_hyd=1.0,
        k_ref_deg=0.005,
        Ea_deg=75000.0,
        n_deg=1.0,
        k_ref_de=0.012,
        Ea_de=50000.0,
        n_de=1.0,
        gamma_citric=0.0,
        beta_mw=1.0
    )
    
    test_cases = {
        "baseline": {
            "temp_c": 80.0,
            "pH": 2.0,
            "C_citric": 0.1,
            "time_min": 120.0
        },
        "stress_high_severity": {
            "temp_c": 95.0,
            "pH": 1.5,
            "C_citric": 0.2,
            "time_min": 120.0
        },
        "mild_low_severity": {
            "temp_c": 50.0,
            "pH": 3.0,
            "C_citric": 0.05,
            "time_min": 120.0
        }
    }
    
    results = {}
    for name, cond in test_cases.items():
        res = simulate(
            feedstock=feedstock,
            temperature_celsius=cond["temp_c"],
            pH=cond["pH"],
            C_citric=cond["C_citric"],
            time_min=cond["time_min"],
            kinetic_params=kinetic_params,
            recovery_efficiency=0.90
        )
        
        # Subsample to 50 evenly spaced points for compact JSON
        indices = np.linspace(0, len(res.state.time) - 1, 50, dtype=int)
        
        results[name] = {
            "conditions": cond,
            "time_min": [float(res.state.time[i]) for i in indices],
            "P_matrix": [float(res.state.matrix_pectin[i]) for i in indices],
            "P_sol": [float(res.state.soluble_intact_pectin[i]) for i in indices],
            "P_lowMW": [float(res.state.low_mw_pectin[i]) for i in indices],
            "P_loss": [float(res.state.loss_pectin[i]) for i in indices],
            "Q_DE_sol": [float(res.state.Q_DE_sol[i]) for i in indices],
            "Q_DE_lowMW": [float(res.state.Q_DE_lowMW[i]) for i in indices],
            "Q_MW_sol": [float(res.state.Q_MW_sol[i]) for i in indices],
            "Q_MW_lowMW": [float(res.state.Q_MW_lowMW[i]) for i in indices],
            "G_sol": [float(res.state.G_sol[i]) for i in indices],
            "G_lowMW": [float(res.state.G_lowMW[i]) for i in indices],
            "G_loss": [float(res.state.G_loss[i]) for i in indices],
            "final_yield_pct": float(res.Y_p * 100.0),
            "final_DE_product": float(res.final_DE_product),
            "final_Mw_product": float(res.final_Mw_product),
            "max_mass_balance_error": float(res.max_epsilon_M)
        }
        
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
        
    print(f"Successfully exported reference trajectories to {output_file}")

if __name__ == "__main__":
    export_reference_runs()
