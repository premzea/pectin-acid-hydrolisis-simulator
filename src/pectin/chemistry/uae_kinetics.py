"""
Acoustic cavitation kinetics for ultrasound-assisted extraction (UAE).
Implements the dual action of cavitation:
1. Accelerated solubilization / mass transfer: k_ext_US = k_ext_thermal * (1 + kappa_ext * (P_ac / V)^beta_ext)
2. Incremental depolymerization / degradation: k_hyd_US = k_hyd_thermal * (1 + kappa_hyd * (P_ac / V)^beta_hyd)
3. Monomer degradation: k_deg_US = k_deg_thermal * (1 + kappa_deg * (P_ac / V)^beta_deg)

Under thermal control (P_ac = 0), all modifiers collapse identically to 1.0.
Frequency scaling is fixed to gamma_US = 1.0 for single-frequency (40 kHz) hardware.
"""
from dataclasses import dataclass
import numpy as np
from .kinetics import KineticParameters, RateConstants, calculate_rate_constants

@dataclass
class AcousticKineticsParameters:
    """Parameters governing acoustic cavitation effects in UAE."""
    # Base thermal-acid parameters
    base_params: KineticParameters
    
    # Acoustic solubilization
    kappa_ext: float = 0.05       # Volumetric acoustic power coefficient [m^3/W]
    beta_ext: float = 1.0         # Acoustic power exponent (default linear)
    
    # Acoustic depolymerization / shear-induced chain scission
    kappa_hyd: float = 0.02       # Volumetric acoustic power coefficient [m^3/W]
    beta_hyd: float = 1.0
    
    # Acoustic monomer degradation
    kappa_deg: float = 0.005
    beta_deg: float = 1.0
    
    # Nominal hardware frequency
    f_nominal_khz: float = 40.0

@dataclass(frozen=True)
class UAERateConstants:
    """Rate constants for UAE extraction with explicit thermal and acoustic decomposition."""
    k_ext: float
    k_hyd: float
    k_deg: float
    k_de: float
    beta_mw: float
    
    # Thermal baseline rates
    k_ext_thermal: float
    k_hyd_thermal: float
    k_deg_thermal: float
    
    # Ultrasound enhancement factors (psi >= 1.0)
    psi_ext: float
    psi_hyd: float
    psi_deg: float
    
    # Volumetric acoustic power density [W/L]
    acoustic_density_w_per_l: float

def calculate_uae_rate_constants(
    T_kelvin: float,
    pH: float,
    C_citric: float,
    d50_um: float,
    P_acoustic_w: float,
    V_slurry_l: float,
    params: AcousticKineticsParameters,
    f_us_khz: float = 40.0
) -> UAERateConstants:
    """
    Calculate effective rate constants under ultrasound irradiation.
    
    P_acoustic_w is calorimetric delivered acoustic power [W].
    V_slurry_l is total liquid slurry volume [L].
    """
    if P_acoustic_w < 0:
        raise ValueError("Acoustic power cannot be negative.")
    if V_slurry_l <= 0:
        raise ValueError("Slurry volume must be positive.")
    if f_us_khz <= 0:
        raise ValueError("Ultrasound frequency must be positive.")
        
    # 1. Base thermal-acid rate constants
    thermal_rates = calculate_rate_constants(
        T_kelvin=T_kelvin,
        pH=pH,
        C_citric=C_citric,
        d50_um=d50_um,
        params=params.base_params
    )
    
    # 2. Volumetric acoustic power density (W/L)
    power_density = P_acoustic_w / V_slurry_l
    
    # Frequency scaling factor (fixed gamma_US = 1.0 for 40 kHz reference)
    freq_factor = (params.f_nominal_khz / f_us_khz) ** 1.0
    
    if P_acoustic_w == 0.0 or power_density == 0.0:
        psi_ext = 1.0
        psi_hyd = 1.0
        psi_deg = 1.0
    else:
        psi_ext = 1.0 + params.kappa_ext * (power_density ** params.beta_ext) * freq_factor
        psi_hyd = 1.0 + params.kappa_hyd * (power_density ** params.beta_hyd) * freq_factor
        psi_deg = 1.0 + params.kappa_deg * (power_density ** params.beta_deg) * freq_factor
        
    k_ext_eff = thermal_rates.k_ext * psi_ext
    k_hyd_eff = thermal_rates.k_hyd * psi_hyd
    k_deg_eff = thermal_rates.k_deg * psi_deg
    k_de_eff = thermal_rates.k_de  # De-esterification is predominantly chemical
    
    return UAERateConstants(
        k_ext=k_ext_eff,
        k_hyd=k_hyd_eff,
        k_deg=k_deg_eff,
        k_de=k_de_eff,
        beta_mw=thermal_rates.beta_mw,
        k_ext_thermal=thermal_rates.k_ext,
        k_hyd_thermal=thermal_rates.k_hyd,
        k_deg_thermal=thermal_rates.k_deg,
        psi_ext=psi_ext,
        psi_hyd=psi_hyd,
        psi_deg=psi_deg,
        acoustic_density_w_per_l=power_density
    )
