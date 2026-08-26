import pytest
import numpy as np
from pectin.chemistry.kinetics import calculate_rate_constants, KineticParameters, RateConstants

def test_reference_state():
    """Test that at reference conditions (80C, pH 2.0), rates match the prefactors."""
    params = KineticParameters(
        k_ref_ext=0.05, Ea_ext=35000, n_ext=1.0, alpha=1.0,
        k_ref_hyd=0.03, Ea_hyd=40000, n_hyd=1.0,
        k_ref_deg=0.01, Ea_deg=50000, n_deg=1.0,
        k_ref_de=0.02,  Ea_de=45000,  n_de=1.0, gamma_citric=0.0,
        beta_mw=1.0
    )
    
    rates = calculate_rate_constants(
        T_kelvin=353.15,
        pH=2.0,
        C_citric=0.0,
        d50_um=300.0,
        params=params
    )
    
    np.testing.assert_allclose(rates.k_ext, 0.05, atol=1e-10)
    np.testing.assert_allclose(rates.k_hyd, 0.03, atol=1e-10)
    np.testing.assert_allclose(rates.k_deg, 0.01, atol=1e-10)
    np.testing.assert_allclose(rates.k_de, 0.02, atol=1e-10)

def test_particle_size_scaling():
    """Test that particle size empirically scales the extraction rate properly."""
    params = KineticParameters(
        k_ref_ext=0.05, Ea_ext=35000, n_ext=1.0, alpha=1.0,
        k_ref_hyd=0.03, Ea_hyd=40000, n_hyd=1.0,
        k_ref_deg=0.01, Ea_deg=50000, n_deg=1.0,
        k_ref_de=0.02,  Ea_de=45000,  n_de=1.0, gamma_citric=0.0,
        beta_mw=1.0
    )
    
    # 1. d50 < 300 um => phi_d > 1 => k_ext > k_ref
    rates_small = calculate_rate_constants(353.15, 2.0, 0.0, 150.0, params)
    assert rates_small.k_ext > 0.05
    
    # 2. d50 > 300 um => phi_d < 1 => k_ext < k_ref
    rates_large = calculate_rate_constants(353.15, 2.0, 0.0, 600.0, params)
    assert rates_large.k_ext < 0.05
    
    # 3. alpha = 0 => phi_d = 1
    params_no_scale = KineticParameters(
        k_ref_ext=0.05, Ea_ext=35000, n_ext=1.0, alpha=0.0,
        k_ref_hyd=0.03, Ea_hyd=40000, n_hyd=1.0,
        k_ref_deg=0.01, Ea_deg=50000, n_deg=1.0,
        k_ref_de=0.02,  Ea_de=45000,  n_de=1.0, gamma_citric=0.0,
        beta_mw=1.0
    )
    rates_no_scale = calculate_rate_constants(353.15, 2.0, 0.0, 150.0, params_no_scale)
    np.testing.assert_allclose(rates_no_scale.k_ext, 0.05, atol=1e-10)

def test_input_validation():
    """Test that physically invalid inputs raise ValueErrors."""
    params = KineticParameters(
        k_ref_ext=0.05, Ea_ext=35000, n_ext=1.0, alpha=1.0,
        k_ref_hyd=0.03, Ea_hyd=40000, n_hyd=1.0,
        k_ref_deg=0.01, Ea_deg=50000, n_deg=1.0,
        k_ref_de=0.02,  Ea_de=45000,  n_de=1.0, gamma_citric=0.0,
        beta_mw=1.0
    )
    
    with pytest.raises(ValueError, match="Temperature must be greater than 0"):
        calculate_rate_constants(0.0, 2.0, 0.0, 300.0, params)
        
    with pytest.raises(ValueError, match="Particle size .* greater than 0"):
        calculate_rate_constants(353.15, 2.0, 0.0, -10.0, params)
        
    with pytest.raises(ValueError, match="Citric acid .* negative"):
        calculate_rate_constants(353.15, 2.0, -0.5, 300.0, params)
        
    with pytest.raises(ValueError, match="pH must be between 0 and 14"):
        calculate_rate_constants(353.15, -1.0, 0.0, 300.0, params)
