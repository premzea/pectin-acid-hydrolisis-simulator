import numpy as np
from scipy.integrate import solve_ivp
from .model import build_derivative_function, STATE_NAMES
from .states import SimulationState, SimulationResult
from ..feedstock.properties import ConditionedFeedstock
from ..chemistry.kinetics import KineticParameters

def simulate(
    feedstock: ConditionedFeedstock,
    temperature_celsius: float,
    pH: float,
    C_citric: float,
    time_min: float,
    kinetic_params: KineticParameters,
    recovery_efficiency: float = 0.90
) -> SimulationResult:
    """
    Run a V1.3 4-pool mass-balance extraction simulation with cohort-correct property moments.
    """
    T_kelvin = temperature_celsius + 273.15
    d50_um = feedstock.d50_um
    
    # Normalizing the absolute pectin mass by the dry feed mass to produce kg/kg_dry_feed
    P_matrix_0 = feedstock.pectin_mass / feedstock.dry_matter_mass
    DE_matrix = feedstock.DE
    Mw_matrix = feedstock.Mw_matrix
    Mw_min = 10000.0
    X_GalA_matrix = feedstock.GalA_fraction
    
    # Initial states y0 (11 dimensions matching STATE_NAMES)
    y0 = np.array([
        P_matrix_0, # P_matrix
        0.0,        # P_sol
        0.0,        # P_lowMW
        0.0,        # P_loss
        0.0,        # Q_DE_sol
        0.0,        # Q_DE_lowMW
        0.0,        # Q_MW_sol
        0.0,        # Q_MW_lowMW
        0.0,        # G_sol
        0.0,        # G_lowMW
        0.0         # G_loss
    ])
    
    t_span = (0.0, time_min)
    t_eval = np.linspace(0.0, time_min, num=500)
    
    model_func = build_derivative_function(
        T_kelvin=T_kelvin,
        pH=pH,
        C_citric=C_citric,
        d50_um=d50_um,
        DE_matrix=DE_matrix,
        Mw_matrix=Mw_matrix,
        X_GalA_matrix=X_GalA_matrix,
        Mw_min=Mw_min,
        params=kinetic_params
    )
    
    from ..chemistry.kinetics import calculate_rate_constants
    rates = calculate_rate_constants(T_kelvin, pH, C_citric, d50_um, kinetic_params)
    
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
        raise RuntimeError(f"Simulation failed: {sol.message}")
    
    # Unpack time-series
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
    
    # Trajectory Diagnostics
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
    
    # End-of-run values
    final_P_matrix = P_matrix_t[-1]
    final_P_sol = P_sol_t[-1]
    final_P_lowMW = P_lowMW_t[-1]
    final_P_loss = P_loss_t[-1]
    
    # Diagnostics (Mass & GalA invariants)
    epsilon_M = epsilon_M_t[-1]
    max_epsilon_M = np.max(np.abs(epsilon_M_t))
    
    epsilon_G = epsilon_G_t[-1]
    max_epsilon_G = np.max(np.abs(epsilon_G_t))
    
    # Derived Properties (Guarding against division-by-zero singularities at early t)
    DE_sol = Q_DE_sol_t[-1] / final_P_sol if final_P_sol > 1e-12 else DE_matrix
    DE_lowMW = Q_DE_lowMW_t[-1] / final_P_lowMW if final_P_lowMW > 1e-12 else DE_matrix
    Mw_sol = Q_MW_sol_t[-1] / final_P_sol if final_P_sol > 1e-12 else Mw_matrix
    Mw_lowMW = Q_MW_lowMW_t[-1] / final_P_lowMW if final_P_lowMW > 1e-12 else Mw_min
    
    # Target Metrics
    P_product = recovery_efficiency * (final_P_sol + final_P_lowMW)
    Y_p = P_product
    
    G_sol = G_sol_t[-1]
    G_lowMW = G_lowMW_t[-1]
    G_matrix = G_matrix_t[-1]
    G_loss = G_loss_t[-1]
    
    G_product = recovery_efficiency * (G_sol + G_lowMW)
    
    # Product property moments (mass-weighted)
    if (final_P_sol + final_P_lowMW) > 1e-12:
        final_DE_product = (Q_DE_sol_t[-1] + Q_DE_lowMW_t[-1]) / (final_P_sol + final_P_lowMW)
        final_Mw_product = (Q_MW_sol_t[-1] + Q_MW_lowMW_t[-1]) / (final_P_sol + final_P_lowMW)
    else:
        final_DE_product = DE_matrix
        final_Mw_product = Mw_matrix
    
    # Purity is GalA of the recovered product
    Purity_GalA = (G_sol + G_lowMW) / (final_P_sol + final_P_lowMW) if (final_P_sol + final_P_lowMW) > 1e-12 else X_GalA_matrix
    
    Y_GalA_extract = (G_sol + G_lowMW) / G_matrix_0 if G_matrix_0 > 0 else 0.0
    Y_GalA_product = G_product / G_matrix_0 if G_matrix_0 > 0 else 0.0
    
    return SimulationResult(
        state=state,
        rates=rates,
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
