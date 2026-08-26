from dataclasses import dataclass
import numpy as np

# Note: Feedstock is now handled by pectin.feedstock.properties.ConditionedFeedstock

from ..chemistry.kinetics import RateConstants

@dataclass
class SimulationState:
    """Time-series data for the extraction simulation."""
    time: np.ndarray
    
    # 4-Pool Mass States
    matrix_pectin: np.ndarray         # P_matrix
    soluble_intact_pectin: np.ndarray # P_sol
    low_mw_pectin: np.ndarray         # P_lowMW
    loss_pectin: np.ndarray           # P_loss
    
    # Moments (Cohort-Correct)
    Q_DE_sol: np.ndarray
    Q_DE_lowMW: np.ndarray
    Q_MW_sol: np.ndarray
    Q_MW_lowMW: np.ndarray
    
    # GalA Inventories
    G_sol: np.ndarray
    G_lowMW: np.ndarray
    G_loss: np.ndarray
    
    # Diagnostics
    total_pectin: np.ndarray
    total_galA: np.ndarray
    mass_balance_error: np.ndarray
    galA_balance_error: np.ndarray

@dataclass
class SimulationResult:
    """Summary of the extraction outcome and metrics."""
    # The full time-series state
    state: SimulationState
    
    # Effective kinetics
    rates: RateConstants
    
    # End-of-run Mass states
    final_P_matrix: float
    final_P_sol: float
    final_P_lowMW: float
    final_P_loss: float
    
    # Diagnostics
    epsilon_M: float
    epsilon_G: float
    max_epsilon_M: float
    max_epsilon_G: float
    
    # End-of-run Properties
    final_DE_sol: float
    final_DE_lowMW: float
    final_Mw_sol: float
    final_Mw_lowMW: float
    
    # GalA Tracking
    final_G_matrix: float
    final_G_sol: float
    final_G_lowMW: float
    final_G_loss: float
    
    # Tier 1 Yield Metrics
    P_product: float
    G_product: float
    final_DE_product: float
    final_Mw_product: float
    Y_p: float
    Y_GalA_extract: float
    Y_GalA_product: float
    Purity_GalA: float
