"""
least_squares.py
----------------
Deterministic parameter recovery via nonlinear least squares.
Includes weighted residual calculation, unconstrained/bounded optimization,
and multi-start robustness benchmarking.
"""

from typing import List, Tuple, Dict, Any, Optional
import numpy as np
from scipy.optimize import least_squares
from dataclasses import dataclass

from pectin.calibration.parameterization import (
    PARAM_NAMES,
    pack,
    unpack,
    transform,
    inverse_transform,
    sample_initial_guesses,
)
from pectin.calibration.sensitivity import (
    ExperimentCondition,
    forward_model,
    build_noise_weights,
    DEFAULT_SIGMAS,
)

@dataclass
class FitResult:
    theta_opt: np.ndarray
    q_opt: np.ndarray
    cost: float
    success: bool
    status: int
    message: str
    n_fev: int

def residual_vector(
    q: np.ndarray,
    conditions: List[ExperimentCondition],
    y_obs: np.ndarray,
    w: np.ndarray,
    obs_keys: Tuple[str, ...] = ("Y_GalA_product", "final_DE_product", "final_Mw_product")
) -> np.ndarray:
    """
    Compute noise-weighted residual vector r(q) = w * (y_sim(q) - y_obs).
    """
    try:
        y_sim = forward_model(q, conditions, obs_keys)
        if np.any(np.isnan(y_sim)) or np.any(np.isinf(y_sim)):
            return np.full_like(y_obs, 1e6)
        return w * (y_sim - y_obs)
    except Exception:
        return np.full_like(y_obs, 1e6)

def fit(
    conditions: List[ExperimentCondition],
    y_obs: np.ndarray,
    initial_theta: np.ndarray,
    obs_keys: Tuple[str, ...] = ("Y_GalA_product", "final_DE_product", "final_Mw_product"),
    sigmas: Dict[str, float] = None,
    max_nfev: int = 200,
    ftol: float = 1e-6,
    xtol: float = 1e-6
) -> FitResult:
    """
    Fit the 9 kinetic parameters to observed data using Trust Region Reflective least squares
    in unconstrained transformed space q.
    """
    q0 = transform(initial_theta)
    w = build_noise_weights(conditions, obs_keys, sigmas)
    
    res = least_squares(
        fun=residual_vector,
        x0=q0,
        args=(conditions, y_obs, w, obs_keys),
        method="trf",
        ftol=ftol,
        xtol=xtol,
        max_nfev=max_nfev
    )
    
    q_opt = res.x
    theta_opt = inverse_transform(q_opt)
    
    return FitResult(
        theta_opt=theta_opt,
        q_opt=q_opt,
        cost=float(res.cost),
        success=bool(res.success),
        status=int(res.status),
        message=str(res.message),
        n_fev=int(res.nfev)
    )

@dataclass
class MultiStartSummary:
    mode: str
    n_starts: int
    n_success: int
    theta_true: np.ndarray
    median_recovered: np.ndarray
    relative_errors_pct: np.ndarray
    std_recovered: np.ndarray
    all_recovered: np.ndarray
    all_costs: np.ndarray

def multistart_fit(
    conditions: List[ExperimentCondition],
    theta_true: np.ndarray,
    n_starts: int = 50,
    mode: str = "local",
    obs_keys: Tuple[str, ...] = ("Y_GalA_product", "final_DE_product", "final_Mw_product"),
    sigmas: Dict[str, float] = None,
    add_noise: bool = False,
    seed: int = 42
) -> MultiStartSummary:
    """
    Run multi-start parameter estimation across sampled initial guesses.
    """
    # 1. Generate ground truth noiseless / noisy synthetic observations
    q_true = transform(theta_true)
    y_true = forward_model(q_true, conditions, obs_keys)
    
    if add_noise:
        rng = np.random.default_rng(seed)
        w = build_noise_weights(conditions, obs_keys, sigmas)
        y_obs = y_true + rng.normal(0.0, 1.0 / w)
    else:
        y_obs = y_true
        
    # 2. Sample initial guesses
    guesses = sample_initial_guesses(theta_true, n_samples=n_starts, mode=mode, seed=seed)
    
    recovered_list = []
    costs_list = []
    success_count = 0
    
    for i in range(n_starts):
        theta_init = guesses[i]
        fit_res = fit(
            conditions=conditions,
            y_obs=y_obs,
            initial_theta=theta_init,
            obs_keys=obs_keys,
            sigmas=sigmas
        )
        if fit_res.success:
            success_count += 1
            
        recovered_list.append(fit_res.theta_opt)
        costs_list.append(fit_res.cost)
        
    all_recovered = np.array(recovered_list, dtype=np.float64)
    all_costs = np.array(costs_list, dtype=np.float64)
    
    median_recovered = np.median(all_recovered, axis=0)
    std_recovered = np.std(all_recovered, axis=0)
    rel_errors_pct = np.abs((median_recovered - theta_true) / theta_true) * 100.0
    
    return MultiStartSummary(
        mode=mode,
        n_starts=n_starts,
        n_success=success_count,
        theta_true=theta_true,
        median_recovered=median_recovered,
        relative_errors_pct=rel_errors_pct,
        std_recovered=std_recovered,
        all_recovered=all_recovered,
        all_costs=all_costs
    )
