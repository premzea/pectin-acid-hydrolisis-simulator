import os, sys
sys.path.insert(0, 'src')
import numpy as np
import pandas as pd
from pectin.calibration.parameterization import pack, transform, unpack, inverse_transform
from pectin.calibration.bayesian import GROUND_TRUTH_PARAMS
from pectin.calibration.sensitivity import create_reference_feedstock
from pectin.simulator.solver import simulate
from pectin.calibration.sensitivity import DEFAULT_SIGMAS

# Grid definition
T_grid = [50.0, 65.0, 80.0, 95.0]
pH_grid = [1.5, 2.0, 2.5, 3.0]
d50_grid = [150.0, 300.0, 600.0]
sample_times = [15.0, 45.0, 90.0, 120.0]

candidates = [(T, pH, d) for T in T_grid for pH in pH_grid for d in d50_grid]

# Noise model for the 12 observations (4 times x 3 observables)
w_single = np.array([1.0/DEFAULT_SIGMAS["Y_GalA_product"], 
                     1.0/DEFAULT_SIGMAS["final_DE_product"], 
                     1.0/DEFAULT_SIGMAS["final_Mw_product"]])
W = np.tile(w_single, len(sample_times))

q_true = transform(pack(GROUND_TRUTH_PARAMS))
eps = 1e-5
n_dim = len(q_true)
n_obs = len(sample_times) * 3

def get_jacobian(cand):
    J = np.zeros((n_obs, n_dim))
    
    # Base
    p_base = unpack(inverse_transform(q_true))
    fs = create_reference_feedstock(d50_um=cand[2])
    base_obs = []
    for t in sample_times:
        r = simulate(fs, cand[0], cand[1], 0.0, t, p_base)
        base_obs.extend([r.Y_GalA_product, r.final_DE_product, r.final_Mw_product])
    base_obs = np.array(base_obs)
    
    for i in range(n_dim):
        q_eps = q_true.copy()
        q_eps[i] += eps
        p_eps = unpack(inverse_transform(q_eps))
        obs_eps = []
        for t in sample_times:
            r = simulate(fs, cand[0], cand[1], 0.0, t, p_eps)
            obs_eps.extend([r.Y_GalA_product, r.final_DE_product, r.final_Mw_product])
        J[:, i] = (np.array(obs_eps) - base_obs) / eps
    return J

print("Precomputing Jacobians for time-resolved runs...")
F_candidates = []
for i, cand in enumerate(candidates):
    J = get_jacobian(cand)
    J_w = J * W[:, None]
    F = J_w.T @ J_w
    F_candidates.append((cand, F))

# Greedy D-optimal selection
n_runs = 10
selected = []
F_current = np.eye(n_dim) * 1e-6 # small regularization

print("\nSelecting time-resolved OED runs...")
for step in range(n_runs):
    best_idx = -1
    best_obj = -np.inf
    
    for i, (cand, F_cand) in enumerate(F_candidates):
        F_test = F_current + F_cand
        obj = np.linalg.slogdet(F_test)[1]
        if obj > best_obj:
            best_obj = obj
            best_idx = i
            
    cand, F_best = F_candidates[best_idx]
    selected.append(cand)
    F_current += F_best
    
    # Add a penalty to prevent picking the exact same run again if possible 
    # (though sometimes exact replicates are optimal, we prefer diversity)
    F_candidates[best_idx] = (cand, F_best * 0.01)
    
    cond_num = np.linalg.cond(F_current)
    print(f"Run {step+1}: T={cand[0]}, pH={cand[1]}, d50={cand[2]}  -> logdet={best_obj:.2f}, cond={cond_num:.1e}")

print("\nSelected Verbatim Protocol:")
print("Run | T (°C) | pH | d50 (µm) | Sample Times (min)")
print("---|---|---|---|---")
for i, cand in enumerate(selected):
    print(f"{i+1:2d}  | {cand[0]:4.0f} | {cand[1]:4.1f} | {cand[2]:4.0f} | 15, 45, 90, 120")
