import time
import numpy as np
import pandas as pd
from multiprocessing import Pool
from pectin.chemistry.kinetics import KineticParameters
from pectin.feedstock.properties import FreshRind
from pectin.feedstock.conditioning import condition_feedstock
from pectin.simulator.solver import simulate

# Fixed Kinetic Parameters for the V1.3 Simulator
PARAMS = KineticParameters(
    k_ref_ext=0.05, Ea_ext=35000, n_ext=1.0, alpha=1.0,
    k_ref_hyd=0.03, Ea_hyd=40000, n_hyd=1.0,
    k_ref_deg=0.01, Ea_deg=50000, n_deg=1.0,
    k_ref_de=0.02,  Ea_de=45000,  n_de=1.0, gamma_citric=0.0,
    beta_mw=1.0
)

# Standard Fresh Rind directly from pulp-processing
RAW_RIND = FreshRind(
    wet_mass=500.0,
    moisture_fraction=0.85, # 85% moisture
    pectin_content_dry_basis=0.2, 
    GalA_fraction_of_pectin=0.78,
    initial_DE=0.745,
    initial_Mw=654000.0
)
# Fixed V1 Conditioning
FEEDSTOCK = condition_feedstock(RAW_RIND, target_moisture=0.08, d50_um=300.0)

def run_single_simulation(args):
    """Worker function for multiprocessing."""
    T_ext, pH, C_citric, time_min = args
    
    res = simulate(
        feedstock=FEEDSTOCK,
        temperature_celsius=T_ext,
        pH=pH,
        C_citric=C_citric,
        time_min=time_min,
        kinetic_params=PARAMS
    )
    
    return {
        'temperature': T_ext,
        'pH': pH,
        'C_citric': C_citric,
        'time_min': time_min,
        'Y_p': res.Y_p,
        'Y_GalA_product': res.Y_GalA_product,
        'final_DE_product': res.final_DE_product,
        'final_Mw_product': res.final_Mw_product,
        'epsilon_M': res.epsilon_M
    }

def generate_dataset(n_samples=10000):
    np.random.seed(42)
    print(f"Generating {n_samples} virtual experiments...")
    
    # Process variables (Extraction only for V1 optimization)
    T_ext_vals = np.random.uniform(45.0, 100.0, n_samples)
    pH_vals = np.random.uniform(1.2, 4.5, n_samples)
    C_citric_vals = np.random.uniform(0.05, 0.5, n_samples)
    time_vals = np.random.uniform(5.0, 120.0, n_samples)
    
    tasks = list(zip(T_ext_vals, pH_vals, C_citric_vals, time_vals))
    
    start_time = time.time()
    
    with Pool() as pool:
        results = pool.map(run_single_simulation, tasks)
        
    df = pd.DataFrame(results)
    
    output_path = 'artifacts/synthetic/synthetic_dataset.csv'
    df.to_csv(output_path, index=False)
    
    elapsed = time.time() - start_time
    print(f"Generated dataset in {elapsed:.1f} seconds.")
    print(f"Saved to {output_path}")

if __name__ == '__main__':
    generate_dataset(n_samples=10000)
