import joblib
import numpy as np
import os
import sys
from scipy.optimize import differential_evolution

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))
from pectin.feedstock.properties import FreshRind
from pectin.feedstock.conditioning import condition_feedstock
from pectin.chemistry.kinetics import KineticParameters
from pectin.simulator.solver import simulate

def optimize():
    # 1. Load the trained surrogate model
    model_path = 'artifacts/models/rf_v1.joblib'
    if not os.path.exists(model_path):
        raise FileNotFoundError("Surrogate model not found. Run train_surrogate.py first.")
    
    surrogate = joblib.load(model_path)
    print("Loaded ML Surrogate Model.")
    
    DE_min = 0.40   # 40%
    MW_min = 50000.0 # 50 kDa
    
    def objective(x):
        # features = ['temperature', 'pH', 'time_min']
        x = x.reshape(1, -1)
        preds = surrogate.predict(x)
        # targets = ['Y_GalA_product', 'final_DE_product', 'final_Mw_product']
        
        y_gala = preds[:, 0][0]
        final_de = preds[:, 1][0]
        final_mw = preds[:, 2][0]
        
        # Maximize Y_GalA_product subject to constraints
        penalty = 0.0
        if final_de < DE_min:
            penalty += (DE_min - final_de) * 1000
        if final_mw < MW_min:
            penalty += (MW_min - final_mw) / 1000
            
        return -y_gala + penalty # Minimize negative yield + penalty

    # Bounds: T, pH, time
    bounds = np.array([
        [45.0, 100.0], # T
        [1.2, 4.5],    # pH
        [5.0, 120.0]   # time
    ])

    print("Running Differential Evolution on surrogate...")
    result = differential_evolution(objective, bounds, seed=42, popsize=20, maxiter=50)
    
    best_x = result.x
    best_preds = surrogate.predict(best_x.reshape(1, -1))[0]
    
    print("\n--- Surrogate Optimum ---")
    print(f"  Temperature: {best_x[0]:.1f} °C")
    print(f"  pH:          {best_x[1]:.2f}")
    print(f"  Time:        {best_x[2]:.1f} min")
    print("\nSurrogate Predicted Outcomes:")
    print(f"  GalA Yield:  {best_preds[0]*100:.2f}%")
    print(f"  Product DE:  {best_preds[1]*100:.2f}%")
    print(f"  Product MW:  {best_preds[2]:.0f} Da")
    
    print("\n--- Verifying with Exact Simulator ---")
    # Feedstock & Params
    feedstock = condition_feedstock(
        fresh_rind=FreshRind(500.0, 0.85, 0.20, 0.78, 0.745, 654000.0),
        target_moisture=0.08, d50_um=300.0
    )
    params = KineticParameters(
        k_ref_ext=0.05, Ea_ext=35000, n_ext=1.0, alpha=1.0,
        k_ref_hyd=0.03, Ea_hyd=40000, n_hyd=1.0,
        k_ref_deg=0.01, Ea_deg=50000, n_deg=1.0,
        k_ref_de=0.02,  Ea_de=45000,  n_de=1.0, gamma_citric=0.0,
        beta_mw=1.0
    )
    
    res = simulate(
        feedstock=feedstock,
        temperature_celsius=best_x[0],
        pH=best_x[1],
        C_citric=0.0,
        time_min=best_x[2],
        kinetic_params=params
    )
    
    print(f"  GalA Yield:  {res.Y_GalA_product*100:.2f}% (Abs Discrepancy: {abs(res.Y_GalA_product - best_preds[0])*100:.2f}%)")
    print(f"  Product DE:  {res.final_DE_product*100:.2f}% (Abs Discrepancy: {abs(res.final_DE_product - best_preds[1])*100:.2f}%)")
    print(f"  Product MW:  {res.final_Mw_product:.0f} Da (Abs Discrepancy: {abs(res.final_Mw_product - best_preds[2]):.0f} Da)")

if __name__ == '__main__':
    optimize()
