"""
UAE forward simulator and matched thermal control runner.
Simulates Ultrasound-Assisted Extraction (Track B) side-by-side with matched
thermal controls (P_acoustic = 0 W) using the identical fresh comminuted rind.
"""
from dataclasses import dataclass
from typing import Optional, List, Dict
import numpy as np
from scipy.integrate import solve_ivp

from ..feedstock.mechanical import ShreddedRind
from ..chemistry.kinetics import KineticParameters, RateConstants
from ..chemistry.uae_kinetics import (
    AcousticKineticsParameters,
    calculate_uae_rate_constants,
    UAERateConstants
)
from .model import STATE_NAMES
from .states import SimulationState, SimulationResult

@dataclass
class UAESimulationComparison:
    """Paired comparison between UAE active sonication and matched fresh thermal baseline."""
    uae_result: SimulationResult
    control_result: SimulationResult
    
    # Net enhancement metrics
    delta_yield_apsp: float        # Y_p(UAE) - Y_p(control) [kg/kg_dry]
    relative_yield_increase: float # (Y_UAE - Y_ctrl) / Y_ctrl [%]
    delta_Mw: float                # Mw(UAE) - Mw(control) [Da]
    Mw_retention_ratio: float      # Mw(UAE) / Mw(control)
    acoustic_density_w_per_l: float
    time_min: float

def build_uae_derivative_function(
    rates: UAERateConstants,
    DE_matrix: float,
    Mw_matrix: float,
    X_GalA_matrix: float,
    Mw_min: float = 10000.0
):
    """
    Constructs derivative function using effective UAE rate constants.
    """
    def derivatives(t, y):
        P_matrix, P_sol, P_lowMW, P_loss, Q_DE_sol, Q_DE_lowMW, Q_MW_sol, Q_MW_lowMW, G_sol, G_lowMW, G_loss = y
        
        # 1. Mass Conservation ODEs
        dP_matrix = -rates.k_ext * P_matrix
        dP_sol = rates.k_ext * P_matrix - rates.k_hyd * P_sol
        dP_lowMW = rates.k_hyd * P_sol - rates.k_deg * P_lowMW
        dP_loss = rates.k_deg * P_lowMW
        
        # 2. DE Moments
        dQ_DE_sol = rates.k_ext * P_matrix * DE_matrix - rates.k_de * Q_DE_sol - rates.k_hyd * Q_DE_sol
        dQ_DE_lowMW = rates.k_hyd * Q_DE_sol - rates.k_de * Q_DE_lowMW - rates.k_deg * Q_DE_lowMW
        
        # 3. MW Moments
        dQ_MW_sol = rates.k_ext * P_matrix * Mw_matrix - rates.k_hyd * Q_MW_sol - rates.beta_mw * rates.k_hyd * (Q_MW_sol - Mw_min * P_sol)
        dQ_MW_lowMW = rates.k_hyd * Q_MW_sol - rates.k_deg * Q_MW_lowMW - rates.beta_mw * rates.k_deg * (Q_MW_lowMW - Mw_min * P_lowMW)
        
        # 4. GalA Inventories
        dG_sol = rates.k_ext * P_matrix * X_GalA_matrix - rates.k_hyd * G_sol
        dG_lowMW = rates.k_hyd * G_sol - rates.k_deg * G_lowMW
        dG_loss = rates.k_deg * G_lowMW
        
        return [
            dP_matrix, dP_sol, dP_lowMW, dP_loss,
            dQ_DE_sol, dQ_DE_lowMW,
            dQ_MW_sol, dQ_MW_lowMW,
            dG_sol, dG_lowMW, dG_loss
        ]
    return derivatives

def simulate_uae_run(
    shredded_rind: ShreddedRind,
    temperature_celsius: float,
    pH: float,
    C_citric: float,
    time_min: float,
    P_acoustic_w: float,
    V_slurry_l: float,
    acoustic_params: AcousticKineticsParameters,
    f_us_khz: float = 40.0,
    recovery_efficiency: float = 0.90,
    n_points: int = 500
) -> SimulationResult:
    """
    Simulate a single UAE extraction run (either active sonication or thermal control).
    """
    T_kelvin = temperature_celsius + 273.15
    d50_um = shredded_rind.d50_um
    
    P_matrix_0 = shredded_rind.absolute_pectin_mass / shredded_rind.dry_matter_mass
    DE_matrix = shredded_rind.DE
    Mw_matrix = shredded_rind.Mw_matrix
    X_GalA_matrix = shredded_rind.GalA_fraction
    Mw_min = 10000.0
    
    # Calculate effective rates
    rates = calculate_uae_rate_constants(
        T_kelvin=T_kelvin,
        pH=pH,
        C_citric=C_citric,
        d50_um=d50_um,
        P_acoustic_w=P_acoustic_w,
        V_slurry_l=V_slurry_l,
        params=acoustic_params,
        f_us_khz=f_us_khz
    )
    
    y0 = np.array([
        P_matrix_0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0
    ])
    
    t_span = (0.0, time_min)
    t_eval = np.linspace(0.0, time_min, num=n_points)
    
    model_func = build_uae_derivative_function(
        rates=rates,
        DE_matrix=DE_matrix,
        Mw_matrix=Mw_matrix,
        X_GalA_matrix=X_GalA_matrix,
        Mw_min=Mw_min
    )
    
    sol = solve_ivp(
        fun=model_func,
        t_span=t_span,
        y0=y0,
        t_eval=t_eval,
        method='LSODA',
        rtol=1e-7,
        atol=1e-10
    )
    
    if not sol.success:
        raise RuntimeError(f"UAE Simulation failed: {sol.message}")
        
    P_matrix_t = sol.y[0]
    P_sol_t = sol.y[1]
    P_lowMW_t = sol.y[2]
    P_loss_t = sol.y[3]
    Q_DE_sol_t = sol.y[4]
    Q_DE_lowMW_t = sol.y[5]
    Q_MW_sol_t = sol.y[6]
    Q_MW_lowMW_t = sol.y[7]
    G_sol_t = sol.y[8]
    G_lowMW_t = sol.y[9]
    G_loss_t = sol.y[10]
    
    P_tot_t = P_matrix_t + P_sol_t + P_lowMW_t + P_loss_t
    epsilon_M_t = P_matrix_0 - P_tot_t
    
    G_matrix_t = P_matrix_t * X_GalA_matrix
    G_tot_t = G_matrix_t + G_sol_t + G_lowMW_t + G_loss_t
    G_matrix_0 = P_matrix_0 * X_GalA_matrix
    epsilon_G_t = G_matrix_0 - G_tot_t
    
    state = SimulationState(
        time=sol.t,
        matrix_pectin=P_matrix_t,
        soluble_intact_pectin=P_sol_t,
        low_mw_pectin=P_lowMW_t,
        loss_pectin=P_loss_t,
        Q_DE_sol=Q_DE_sol_t,
        Q_DE_lowMW=Q_DE_lowMW_t,
        Q_MW_sol=Q_MW_sol_t,
        Q_MW_lowMW=Q_MW_lowMW_t,
        G_sol=G_sol_t,
        G_lowMW=G_lowMW_t,
        G_loss=G_loss_t,
        total_pectin=P_tot_t,
        total_galA=G_tot_t,
        mass_balance_error=epsilon_M_t,
        galA_balance_error=epsilon_G_t
    )
    
    final_P_matrix = float(P_matrix_t[-1])
    final_P_sol = float(P_sol_t[-1])
    final_P_lowMW = float(P_lowMW_t[-1])
    final_P_loss = float(P_loss_t[-1])
    
    epsilon_M = float(epsilon_M_t[-1])
    max_epsilon_M = float(np.max(np.abs(epsilon_M_t)))
    epsilon_G = float(epsilon_G_t[-1])
    max_epsilon_G = float(np.max(np.abs(epsilon_G_t)))
    
    # Derived properties
    DE_sol = float(Q_DE_sol_t[-1] / final_P_sol) if final_P_sol > 1e-12 else DE_matrix
    DE_lowMW = float(Q_DE_lowMW_t[-1] / final_P_lowMW) if final_P_lowMW > 1e-12 else DE_matrix
    Mw_sol = float(Q_MW_sol_t[-1] / final_P_sol) if final_P_sol > 1e-12 else Mw_matrix
    Mw_lowMW = float(Q_MW_lowMW_t[-1] / final_P_lowMW) if final_P_lowMW > 1e-12 else Mw_min
    
    # Target Metrics
    P_product = recovery_efficiency * (final_P_sol + final_P_lowMW)
    Y_p = P_product
    
    G_sol = float(G_sol_t[-1])
    G_lowMW = float(G_lowMW_t[-1])
    G_matrix = float(G_matrix_t[-1])
    G_loss = float(G_loss_t[-1])
    
    G_product = recovery_efficiency * (G_sol + G_lowMW)
    
    if (final_P_sol + final_P_lowMW) > 1e-12:
        final_DE_product = float((Q_DE_sol_t[-1] + Q_DE_lowMW_t[-1]) / (final_P_sol + final_P_lowMW))
        final_Mw_product = float((Q_MW_sol_t[-1] + Q_MW_lowMW_t[-1]) / (final_P_sol + final_P_lowMW))
    else:
        final_DE_product = DE_matrix
        final_Mw_product = Mw_matrix
        
    Purity_GalA = float((G_sol + G_lowMW) / (final_P_sol + final_P_lowMW)) if (final_P_sol + final_P_lowMW) > 1e-12 else X_GalA_matrix
    Y_GalA_extract = float((G_sol + G_lowMW) / G_matrix_0) if G_matrix_0 > 0 else 0.0
    Y_GalA_product = float(G_product / G_matrix_0) if G_matrix_0 > 0 else 0.0
    
    # Wrap rate constants for SimulationResult
    std_rates = RateConstants(
        k_ext=rates.k_ext,
        k_hyd=rates.k_hyd,
        k_deg=rates.k_deg,
        k_de=rates.k_de,
        beta_mw=rates.beta_mw
    )
    
    return SimulationResult(
        state=state,
        rates=std_rates,
        final_P_matrix=final_P_matrix,
        final_P_sol=final_P_sol,
        final_P_lowMW=final_P_lowMW,
        final_P_loss=final_P_loss,
        epsilon_M=epsilon_M,
        epsilon_G=epsilon_G,
        max_epsilon_M=max_epsilon_M,
        max_epsilon_G=max_epsilon_G,
        final_DE_sol=DE_sol,
        final_DE_lowMW=DE_lowMW,
        final_Mw_sol=Mw_sol,
        final_Mw_lowMW=Mw_lowMW,
        final_G_matrix=G_matrix,
        final_G_sol=G_sol,
        final_G_lowMW=G_lowMW,
        final_G_loss=G_loss,
        P_product=P_product,
        G_product=G_product,
        final_DE_product=final_DE_product,
        final_Mw_product=final_Mw_product,
        Y_p=Y_p,
        Y_GalA_extract=Y_GalA_extract,
        Y_GalA_product=Y_GalA_product,
        Purity_GalA=Purity_GalA
    )

def simulate_paired_uae_comparison(
    shredded_rind: ShreddedRind,
    temperature_celsius: float,
    pH: float,
    C_citric: float,
    time_min: float,
    P_acoustic_w: float,
    V_slurry_l: float,
    acoustic_params: AcousticKineticsParameters,
    f_us_khz: float = 40.0,
    recovery_efficiency: float = 0.90
) -> UAESimulationComparison:
    """
    Runs active UAE sonication paired with a matched fresh thermal baseline (P_acoustic = 0 W)
    at the identical temperature, pH, particle size, and run duration.
    """
    # 1. Active UAE run
    uae_res = simulate_uae_run(
        shredded_rind=shredded_rind,
        temperature_celsius=temperature_celsius,
        pH=pH,
        C_citric=C_citric,
        time_min=time_min,
        P_acoustic_w=P_acoustic_w,
        V_slurry_l=V_slurry_l,
        acoustic_params=acoustic_params,
        f_us_khz=f_us_khz,
        recovery_efficiency=recovery_efficiency
    )
    
    # 2. Matched fresh thermal control run (P_acoustic = 0 W)
    ctrl_res = simulate_uae_run(
        shredded_rind=shredded_rind,
        temperature_celsius=temperature_celsius,
        pH=pH,
        C_citric=C_citric,
        time_min=time_min,
        P_acoustic_w=0.0,
        V_slurry_l=V_slurry_l,
        acoustic_params=acoustic_params,
        f_us_khz=f_us_khz,
        recovery_efficiency=recovery_efficiency
    )
    
    # Comparisons
    delta_yield = uae_res.Y_p - ctrl_res.Y_p
    rel_yield = (delta_yield / ctrl_res.Y_p * 100.0) if ctrl_res.Y_p > 0 else 0.0
    delta_mw = uae_res.final_Mw_product - ctrl_res.final_Mw_product
    mw_retention = (uae_res.final_Mw_product / ctrl_res.final_Mw_product) if ctrl_res.final_Mw_product > 0 else 1.0
    power_density = P_acoustic_w / V_slurry_l
    
    return UAESimulationComparison(
        uae_result=uae_res,
        control_result=ctrl_res,
        delta_yield_apsp=delta_yield,
        relative_yield_increase=rel_yield,
        delta_Mw=delta_mw,
        Mw_retention_ratio=mw_retention,
        acoustic_density_w_per_l=power_density,
        time_min=time_min
    )
