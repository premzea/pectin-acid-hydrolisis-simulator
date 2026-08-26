import numpy as np
import pandas as pd
import pymc as pm
import pytensor.tensor as pt
from pytensor.compile.ops import as_op
import arviz as az
import matplotlib.pyplot as plt
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))
from pectin.feedstock.conditioning import condition_feedstock
from pectin.feedstock.properties import FreshRind
from pectin.simulator.solver import simulate
from pectin.chemistry.kinetics import KineticParameters

# Ground truth parameter values for comparison (from generate_dataset.py)
TRUE_PARAMS = {
    'k_ref_ext': 0.05, 'Ea_ext': 35000, 'alpha': 1.0,
    'k_ref_hyd': 0.03, 'Ea_hyd': 40000,
    'k_ref_deg': 0.01, 'Ea_deg': 50000,
    'k_ref_de': 0.02,  'Ea_de': 45000
}

def load_calibration_data(n_samples=20, random_seed=42):
    """Load a subset of the dataset for fast MCMC calibration demonstration."""
    csv_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "experiments", "synthetic_dataset.csv")
    df = pd.read_csv(csv_path)
    
    # Stratified sampling across temperature to ensure good coverage
    df = df.sort_values('temperature')
    indices = np.linspace(0, len(df)-1, n_samples).astype(int)
    df_subset = df.iloc[indices].copy()
    return df_subset

def run_bayesian_calibration(n_samples=20, tune=200, draws=200):
    """
    Run PyMC Bayesian Inference using a gradient-free sampler (DEMetropolisZ)
    so we can seamlessly use the SciPy black-box ODE solver.
    """
    df = load_calibration_data(n_samples=n_samples)
    
    # Process variables
    T_obs = df['temperature'].values
    pH_obs = df['pH'].values
    C_citric_obs = df['C_citric'].values
    time_obs = df['time_min'].values
    
    # Experimental Observations
    Yield_obs = df['Y_GalA_product'].values
    DE_obs = df['final_DE_sol'].values
    Mw_obs = df['final_Mw_lowMW'].values

    # Base Feedstock
    raw_rind = FreshRind(
        wet_mass=500.0,
        moisture_fraction=0.8,
        pectin_content_dry_basis=0.2,
        GalA_fraction_of_pectin=0.75,
        initial_DE=74.5,
        initial_Mw=654000.0
    )
    feedstock = condition_feedstock(raw_rind, target_moisture=0.08, d50_um=300.0)

    # Wrap the SciPy ODE solver in a PyTensor operation
    @as_op(itypes=[pt.dvector], otypes=[pt.dmatrix])
    def simulate_experiments(theta):
        # theta unpacks 9 calibrated parameters
        (k_ref_ext, Ea_ext, alpha,
         k_ref_hyd, Ea_hyd,
         k_ref_deg, Ea_deg,
         k_ref_de, Ea_de) = theta

        params = KineticParameters(
            k_ref_ext=k_ref_ext, Ea_ext=Ea_ext, n_ext=1.0, alpha=alpha,
            k_ref_hyd=k_ref_hyd, Ea_hyd=Ea_hyd, n_hyd=1.0,
            k_ref_deg=k_ref_deg, Ea_deg=Ea_deg, n_deg=1.0,
            k_ref_de=k_ref_de,  Ea_de=Ea_de,  n_de=1.0, gamma_citric=0.5, # We use 0.5 for synthetic data generation matching
            beta_mw=1.0 # Fixed V1
        )
        
        preds = []
        for T, p, C, t in zip(T_obs, pH_obs, C_citric_obs, time_obs):
            res = simulate(
                feedstock=feedstock,
                temperature_celsius=T,
                pH=p,
                C_citric=C,
                time_min=t,
                kinetic_params=params
            )
            # We predict Yield, DE, Mw
            preds.append([res.Y_GalA_product, res.final_DE_sol, res.final_Mw_lowMW])
            
        return np.array(preds, dtype=np.float64)

    print(f"Starting PyMC model with {n_samples} experimental observations...")
    
    with pm.Model() as model:
        # 1. Priors for Reference Rates (k_ref) at 80C, pH 2.0
        # Since they must be positive, we use LogNormal priors
        # We center them loosely around 0.05
        k_ref_ext = pm.LogNormal('k_ref_ext', mu=np.log(0.05), sigma=1.0)
        k_ref_hyd = pm.LogNormal('k_ref_hyd', mu=np.log(0.05), sigma=1.0)
        k_ref_deg = pm.LogNormal('k_ref_deg', mu=np.log(0.05), sigma=1.0)
        k_ref_de  = pm.LogNormal('k_ref_de',  mu=np.log(0.05), sigma=1.0)
        
        # 2. Priors for Activation Energies (Ea)
        # Typically between 20,000 and 100,000 J/mol
        Ea_ext = pm.Normal('Ea_ext', mu=40000, sigma=15000)
        Ea_hyd = pm.Normal('Ea_hyd', mu=40000, sigma=15000)
        Ea_deg = pm.Normal('Ea_deg', mu=40000, sigma=15000)
        Ea_de  = pm.Normal('Ea_de',  mu=40000, sigma=15000)
        
        # 3. Particle Size Scaling
        alpha = pm.Normal('alpha', mu=1.0, sigma=0.5)
        
        # Pack parameters into a vector for the PyTensor Op
        theta = pt.as_tensor_variable([
            k_ref_ext, Ea_ext, alpha,
            k_ref_hyd, Ea_hyd,
            k_ref_deg, Ea_deg,
            k_ref_de, Ea_de
        ])
        
        # Predicted matrix: Shape (N, 3) -> Yield, DE, Mw
        predictions = simulate_experiments(theta)
        
        # Observation noises (weakly informative priors)
        sigma_Y = pm.HalfNormal('sigma_Y', sigma=0.1)
        sigma_DE = pm.HalfNormal('sigma_DE', sigma=5.0)
        sigma_Mw = pm.HalfNormal('sigma_Mw', sigma=50000.0)
        
        # Likelihoods
        Y_hat = pm.Normal('Y_hat', mu=predictions[:, 0], sigma=sigma_Y, observed=Yield_obs)
        DE_hat = pm.Normal('DE_hat', mu=predictions[:, 1], sigma=sigma_DE, observed=DE_obs)
        Mw_hat = pm.Normal('Mw_hat', mu=predictions[:, 2], sigma=sigma_Mw, observed=Mw_obs)

        # Run MCMC
        # Since we use a black-box ODE (no gradients), NUTS won't work.
        # DEMetropolisZ is a highly efficient gradient-free sampler for correlated spaces.
        step = pm.DEMetropolisZ()
        
        print("Sampling posterior...")
        trace = pm.sample(draws=draws, tune=tune, step=step, chains=4, cores=4, return_inferencedata=True)
    
    # Save trace
    trace_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "experiments", "pymc_trace.nc")
    az.to_netcdf(trace, trace_path)
    print(f"Saved trace to {trace_path}")
    
    # Print summary comparison
    print("\n--- Calibration Results vs Ground Truth ---")
    summary = az.summary(trace, var_names=['k_ref_ext', 'Ea_ext', 'k_ref_hyd', 'Ea_hyd', 'k_ref_deg', 'Ea_deg', 'k_ref_de', 'Ea_de', 'alpha'])
    
    # Merge True params for display
    summary['Ground Truth'] = [TRUE_PARAMS[k] for k in summary.index]
    print(summary[['mean', 'sd', 'Ground Truth', 'r_hat']])
    
if __name__ == "__main__":
    # Test run with small numbers to verify it builds and runs
    run_bayesian_calibration(n_samples=10, tune=100, draws=100)
