from ..chemistry.kinetics import calculate_rate_constants, KineticParameters

STATE_NAMES = (
    "P_matrix",
    "P_sol",
    "P_lowMW",
    "P_loss",
    "Q_DE_sol",
    "Q_DE_lowMW",
    "Q_MW_sol",
    "Q_MW_lowMW",
    "G_sol",
    "G_lowMW",
    "G_loss",
)

def build_derivative_function(
    T_kelvin: float, pH: float, C_citric: float, d50_um: float, 
    DE_matrix: float, Mw_matrix: float, X_GalA_matrix: float, Mw_min: float,
    params: KineticParameters
):
    """
    Returns the ODE derivative function for the 4-pool system.
    """
    rates = calculate_rate_constants(T_kelvin, pH, C_citric, d50_um, params)
    
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
        # Note: Material leaving P_sol takes its GalA fraction (G_sol / P_sol). 
        # k_hyd * P_sol * (G_sol / P_sol) = k_hyd * G_sol.
        dG_lowMW = rates.k_hyd * G_sol - rates.k_deg * G_lowMW
        dG_loss = rates.k_deg * G_lowMW
        
        return [dP_matrix, dP_sol, dP_lowMW, dP_loss, 
                dQ_DE_sol, dQ_DE_lowMW, 
                dQ_MW_sol, dQ_MW_lowMW, 
                dG_sol, dG_lowMW, dG_loss]
        
    return derivatives
