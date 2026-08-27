"""
parameterization.py
------------------
Canonical parameter vector definitions, log/bounded transformations,
and packing/unpacking utilities for the 9-parameter V1.3 kinetic system.
"""

from typing import List, Tuple, Dict, Any
import numpy as np
from dataclasses import dataclass
from pectin.chemistry.kinetics import KineticParameters

# Canonical 9-parameter names
PARAM_NAMES: List[str] = [
    "k_ref_ext",
    "Ea_ext",
    "alpha",
    "k_ref_hyd",
    "Ea_hyd",
    "k_ref_deg",
    "Ea_deg",
    "k_ref_de",
    "Ea_de",
]

# Physical bounds for natural parameter space
PARAM_BOUNDS: Dict[str, Tuple[float, float]] = {
    "k_ref_ext": (1e-4, 2.0),       # min^-1
    "Ea_ext": (1e4, 1.5e5),        # J/mol
    "alpha": (0.2, 2.5),           # dimensionless
    "k_ref_hyd": (1e-4, 2.0),       # min^-1
    "Ea_hyd": (1e4, 1.5e5),        # J/mol
    "k_ref_deg": (1e-4, 2.0),       # min^-1
    "Ea_deg": (1e4, 1.5e5),        # J/mol
    "k_ref_de": (1e-4, 2.0),        # min^-1
    "Ea_de": (1e4, 1.5e5),         # J/mol
}

# Alpha bounds for logit-like transform
ALPHA_MIN = 0.2
ALPHA_MAX = 2.5

def pack(params: KineticParameters) -> np.ndarray:
    """Convert KineticParameters dataclass to natural parameter numpy vector."""
    return np.array([
        params.k_ref_ext,
        params.Ea_ext,
        params.alpha,
        params.k_ref_hyd,
        params.Ea_hyd,
        params.k_ref_deg,
        params.Ea_deg,
        params.k_ref_de,
        params.Ea_de,
    ], dtype=np.float64)

def unpack(vec: np.ndarray) -> KineticParameters:
    """Convert natural parameter numpy vector to KineticParameters dataclass."""
    return KineticParameters(
        k_ref_ext=float(vec[0]),
        Ea_ext=float(vec[1]),
        alpha=float(vec[2]),
        k_ref_hyd=float(vec[3]),
        Ea_hyd=float(vec[4]),
        k_ref_deg=float(vec[5]),
        Ea_deg=float(vec[6]),
        k_ref_de=float(vec[7]),
        Ea_de=float(vec[8]),
        # Fixed V1.3 constants:
        n_ext=1.0,
        n_hyd=1.0,
        n_deg=1.0,
        n_de=1.0,
        gamma_citric=0.0,
        beta_mw=1.0,
    )

def transform(theta: np.ndarray) -> np.ndarray:
    """
    Transform natural parameter vector theta to unconstrained space q:
    - Positive scale parameters (k, Ea) -> log(theta)
    - Alpha bounded in [ALPHA_MIN, ALPHA_MAX] -> logit transform
    """
    q = np.empty_like(theta, dtype=np.float64)
    # Log transforms for k and Ea
    q[0] = np.log(theta[0]) # k_ref_ext
    q[1] = np.log(theta[1]) # Ea_ext
    
    # Bounded logit transform for alpha
    norm_alpha = (theta[2] - ALPHA_MIN) / (ALPHA_MAX - ALPHA_MIN)
    norm_alpha = np.clip(norm_alpha, 1e-6, 1.0 - 1e-6)
    q[2] = np.log(norm_alpha / (1.0 - norm_alpha))
    
    q[3] = np.log(theta[3]) # k_ref_hyd
    q[4] = np.log(theta[4]) # Ea_hyd
    q[5] = np.log(theta[5]) # k_ref_deg
    q[6] = np.log(theta[6]) # Ea_deg
    q[7] = np.log(theta[7]) # k_ref_de
    q[8] = np.log(theta[8]) # Ea_de
    return q

def inverse_transform(q: np.ndarray) -> np.ndarray:
    """
    Transform unconstrained parameter vector q back to natural space theta.
    """
    theta = np.empty_like(q, dtype=np.float64)
    # k_ref: [1e-5, 5.0] min^-1
    theta[0] = np.clip(np.exp(np.clip(q[0], -11.5, 1.6)), 1e-5, 5.0)
    # Ea: [5e3, 2.5e5] J/mol
    theta[1] = np.clip(np.exp(np.clip(q[1], 8.5, 12.5)), 5e3, 2.5e5)
    
    # Inverse logit for alpha: [0.2, 2.5]
    sig = 1.0 / (1.0 + np.exp(-np.clip(q[2], -30.0, 30.0)))
    theta[2] = ALPHA_MIN + sig * (ALPHA_MAX - ALPHA_MIN)
    
    # k_hyd, Ea_hyd
    theta[3] = np.clip(np.exp(np.clip(q[3], -11.5, 1.6)), 1e-5, 5.0)
    theta[4] = np.clip(np.exp(np.clip(q[4], 8.5, 12.5)), 5e3, 2.5e5)
    
    # k_deg, Ea_deg
    theta[5] = np.clip(np.exp(np.clip(q[5], -11.5, 1.6)), 1e-5, 5.0)
    theta[6] = np.clip(np.exp(np.clip(q[6], 8.5, 12.5)), 5e3, 2.5e5)
    
    # k_de, Ea_de
    theta[7] = np.clip(np.exp(np.clip(q[7], -11.5, 1.6)), 1e-5, 5.0)
    theta[8] = np.clip(np.exp(np.clip(q[8], 8.5, 12.5)), 5e3, 2.5e5)
    return theta

def sample_initial_guesses(
    theta_true: np.ndarray,
    n_samples: int = 50,
    mode: str = "local",
    seed: int = 42
) -> np.ndarray:
    """
    Sample initial parameter vectors in natural space.
    - 'local': Lognormal perturbation around theta_true (sigma=0.25, ~25% deviation).
    - 'global': Broad uniform/log-uniform sampling across physical parameter bounds.
    """
    rng = np.random.default_rng(seed)
    samples = np.empty((n_samples, len(theta_true)), dtype=np.float64)
    
    if mode == "local":
        for i in range(n_samples):
            mult = rng.lognormal(mean=0.0, sigma=0.25, size=len(theta_true))
            samp = theta_true * mult
            samp[2] = np.clip(theta_true[2] + rng.normal(0, 0.2), ALPHA_MIN + 0.05, ALPHA_MAX - 0.05)
            for j, name in enumerate(PARAM_NAMES):
                b_min, b_max = PARAM_BOUNDS[name]
                samp[j] = np.clip(samp[j], b_min, b_max)
            samples[i] = samp
            
    elif mode == "global":
        for i in range(n_samples):
            samp = np.empty(len(theta_true), dtype=np.float64)
            for j, name in enumerate(PARAM_NAMES):
                b_min, b_max = PARAM_BOUNDS[name]
                if name == "alpha":
                    samp[j] = rng.uniform(b_min, b_max)
                else:
                    samp[j] = np.exp(rng.uniform(np.log(b_min), np.log(b_max)))
            samples[i] = samp
    else:
        raise ValueError(f"Unknown sampling mode: {mode}. Use 'local' or 'global'.")
        
    return samples
