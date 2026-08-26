import numpy as np
from dataclasses import dataclass

@dataclass
class KineticParameters:
    """Parameters for the V1.3 4-pool mass cascade (Ontology mapped)."""
    # Reference Arrhenius formulation (T_ref = 353.15 K, pH_ref = 2.0)
    k_ref_ext: float
    Ea_ext: float
    n_ext: float
    alpha: float
    
    k_ref_hyd: float
    Ea_hyd: float
    n_hyd: float
    
    k_ref_deg: float
    Ea_deg: float
    n_deg: float
    
    k_ref_de: float
    Ea_de: float
    n_de: float
    gamma_citric: float = 0.0
    
    beta_mw: float = 1.0

@dataclass(frozen=True)
class RateConstants:
    k_ext: float
    k_hyd: float
    k_deg: float
    k_de: float
    beta_mw: float

def calculate_rate_constants(
    T_kelvin: float, 
    pH: float, 
    C_citric: float, 
    d50_um: float, 
    params: KineticParameters
) -> RateConstants:
    """
    Calculate the four effective rate constants for V1.3 using reference-state Arrhenius.
    """
    # Input validation
    if T_kelvin <= 0:
        raise ValueError("Temperature must be greater than 0 K")
    if d50_um <= 0:
        raise ValueError("Particle size (d50) must be greater than 0 um")
    if C_citric < 0:
        raise ValueError("Citric acid concentration cannot be negative")
    if not (0 <= pH <= 14):
        raise ValueError("pH must be between 0 and 14")

    R = 8.314462618 # J/(mol K)
    T_ref = 353.15 # 80 C
    pH_ref = 2.0
    
    # 1. Mass transfer empirical modifier
    d_ref = 300.0 # um
    phi_d = (d_ref / d50_um) ** params.alpha
    
    # Temperature and pH modifier components
    def arrhenius_ref(k_ref, Ea, n):
        T_term = np.exp(-Ea / R * (1/T_kelvin - 1/T_ref))
        pH_term = 10**(n * (pH_ref - pH))
        return k_ref * T_term * pH_term
    
    k_ext_chem = arrhenius_ref(params.k_ref_ext, params.Ea_ext, params.n_ext)
    k_ext = k_ext_chem * phi_d
    
    k_hyd = arrhenius_ref(params.k_ref_hyd, params.Ea_hyd, params.n_hyd)
    k_deg = arrhenius_ref(params.k_ref_deg, params.Ea_deg, params.n_deg)
    
    k_de_base = arrhenius_ref(params.k_ref_de, params.Ea_de, params.n_de)
    k_de = k_de_base * (1 + params.gamma_citric * C_citric)
    
    return RateConstants(
        k_ext=k_ext,
        k_hyd=k_hyd,
        k_deg=k_deg,
        k_de=k_de,
        beta_mw=params.beta_mw
    )
