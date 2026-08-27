"""
sensitivity.py
--------------
Finite-difference Jacobian calculation, noise-weighted sensitivity matrix,
Fisher Information Matrix (FIM), SVD diagnostics, and parameter correlation matrix.
"""

from typing import List, Tuple, Dict, Any, NamedTuple
import numpy as np
from dataclasses import dataclass

from pectin.feedstock.properties import FreshRind, ConditionedFeedstock
from pectin.feedstock.conditioning import condition_feedstock
from pectin.simulator.solver import simulate
from pectin.calibration.parameterization import (
    PARAM_NAMES,
    pack,
    unpack,
    transform,
    inverse_transform,
)

# Standard experimental condition
@dataclass(frozen=True)
class ExperimentCondition:
    temperature_celsius: float
    pH: float
    time_min: float
    d50_um: float = 300.0
    recovery_efficiency: float = 0.90

# Standard measurement uncertainty standard deviations (sigma)
DEFAULT_SIGMAS = {
    "Y_GalA_product": 0.01,    # 1 percentage-point absolute error in yield
    "final_DE_product": 0.02,  # 2 percentage-point error in DE (titration/FTIR)
    "final_Mw_product": 15000.0 # 15 kDa error in Mw (GPC/SEC)
}

def create_reference_feedstock(d50_um: float = 300.0) -> ConditionedFeedstock:
    """Create reference feedstock for synthetic simulation."""
    rind = FreshRind(
        wet_mass=500.0,
        moisture_fraction=0.85,
        pectin_content_dry_basis=0.20,
        GalA_fraction_of_pectin=0.78,
        initial_DE=0.745,
        initial_Mw=654000.0
    )
    return condition_feedstock(rind, target_moisture=0.08, d50_um=d50_um)

def forward_model(
    q: np.ndarray,
    conditions: List[ExperimentCondition],
    obs_keys: Tuple[str, ...] = ("Y_GalA_product", "final_DE_product", "final_Mw_product")
) -> np.ndarray:
    """
    Run forward simulations for a list of conditions given unconstrained parameter vector q.
    Returns flattened array of stacked observations.
    """
    theta = inverse_transform(q)
    params = unpack(theta)
    
    obs_list = []
    for cond in conditions:
        feedstock = create_reference_feedstock(d50_um=cond.d50_um)
        res = simulate(
            feedstock=feedstock,
            temperature_celsius=cond.temperature_celsius,
            pH=cond.pH,
            C_citric=0.0,
            time_min=cond.time_min,
            kinetic_params=params,
            recovery_efficiency=cond.recovery_efficiency
        )
        for key in obs_keys:
            obs_list.append(getattr(res, key))
            
    return np.array(obs_list, dtype=np.float64)

def build_noise_weights(
    conditions: List[ExperimentCondition],
    obs_keys: Tuple[str, ...] = ("Y_GalA_product", "final_DE_product", "final_Mw_product"),
    sigmas: Dict[str, float] = None
) -> np.ndarray:
    """
    Construct diagonal inverse standard deviation vector (W^{1/2}) for observations.
    """
    if sigmas is None:
        sigmas = DEFAULT_SIGMAS
        
    weights = []
    for _ in conditions:
        for key in obs_keys:
            sigma = sigmas[key]
            weights.append(1.0 / sigma)
            
    return np.array(weights, dtype=np.float64)

def compute_jacobian(
    q: np.ndarray,
    conditions: List[ExperimentCondition],
    obs_keys: Tuple[str, ...] = ("Y_GalA_product", "final_DE_product", "final_Mw_product"),
    eps: float = 1e-4
) -> np.ndarray:
    """
    Compute numerical central finite-difference Jacobian matrix S = dy / dq
    where q is the unconstrained 9-parameter vector.
    
    Shape: (N_obs, 9)
    """
    n_params = len(q)
    
    # Base evaluation
    y0 = forward_model(q, conditions, obs_keys)
    n_obs = len(y0)
    
    J = np.empty((n_obs, n_params), dtype=np.float64)
    
    for j in range(n_params):
        q_plus = q.copy()
        q_minus = q.copy()
        q_plus[j] += eps
        q_minus[j] -= eps
        
        y_plus = forward_model(q_plus, conditions, obs_keys)
        y_minus = forward_model(q_minus, conditions, obs_keys)
        
        J[:, j] = (y_plus - y_minus) / (2.0 * eps)
        
    return J

@dataclass
class IdentifiabilityDiagnostics:
    singular_values: np.ndarray
    condition_number: float
    fim: np.ndarray
    covariance: np.ndarray
    correlation_matrix: np.ndarray
    right_singular_vectors: np.ndarray
    identifiability_ranking: List[Tuple[str, str, float]] # (param, classification, relative_uncertainty)

def analyze_sensitivity(
    q: np.ndarray,
    conditions: List[ExperimentCondition],
    obs_keys: Tuple[str, ...] = ("Y_GalA_product", "final_DE_product", "final_Mw_product"),
    sigmas: Dict[str, float] = None,
    rcond: float = 1e-12
) -> Tuple[np.ndarray, IdentifiabilityDiagnostics]:
    """
    Perform full noise-weighted sensitivity, SVD, and Fisher Information Matrix analysis.
    """
    # 1. Compute raw Jacobian in transformed space
    J = compute_jacobian(q, conditions, obs_keys)
    
    # 2. Apply observation noise weighting: S_tilde = W^{1/2} * J
    w = build_noise_weights(conditions, obs_keys, sigmas)
    S_tilde = J * w[:, np.newaxis]
    
    # 3. Fisher Information Matrix: F = S_tilde^T * S_tilde
    F = S_tilde.T @ S_tilde
    
    # 4. Singular Value Decomposition: S_tilde = U * Sigma * V^T
    U, s, Vt = np.linalg.svd(S_tilde, full_matrices=False)
    V = Vt.T
    
    # Condition number kappa(F) = (s_max / s_min)^2
    s_max = s[0]
    s_min = s[-1] if s[-1] > 1e-15 else 1e-15
    cond_number = (s_max / s_min) ** 2
    
    # 5. Regularized / Pseudoinverse Covariance: C = (S_tilde^T S_tilde)^+ = V * Sigma^{-2} * V^T
    s_inv2 = np.array([1.0 / (val**2) if val > rcond * s_max else 0.0 for val in s])
    Cov = (V * s_inv2) @ V.T
    
    # 6. Parameter Correlation Matrix: R_jk = Cov_jk / sqrt(Cov_jj * Cov_kk)
    std_errors = np.sqrt(np.maximum(np.diag(Cov), 1e-15))
    Corr = Cov / (std_errors[:, np.newaxis] @ std_errors[np.newaxis, :])
    Corr = np.clip(Corr, -1.0, 1.0)
    
    # 7. Classify parameter identifiability
    ranking = []
    for idx, name in enumerate(PARAM_NAMES):
        std_err = std_errors[idx]
        # In transformed log-space, std_err directly represents fractional parameter uncertainty
        if std_err < 0.20:
            classification = "Well-identified"
        elif std_err < 1.0:
            classification = "Weakly identified"
        else:
            classification = "Practically unidentifiable"
        ranking.append((name, classification, float(std_err)))
        
    diagnostics = IdentifiabilityDiagnostics(
        singular_values=s,
        condition_number=float(cond_number),
        fim=F,
        covariance=Cov,
        correlation_matrix=Corr,
        right_singular_vectors=V,
        identifiability_ranking=ranking
    )
    
    return S_tilde, diagnostics
