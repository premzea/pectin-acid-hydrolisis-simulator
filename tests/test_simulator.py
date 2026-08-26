import pytest
import numpy as np
from pectin.chemistry.kinetics import KineticParameters
from pectin.feedstock.properties import FreshRind
from pectin.feedstock.conditioning import condition_feedstock
from pectin.simulator.solver import simulate
from pectin.chemistry.kinetics import calculate_rate_constants

def create_base_feedstock(d50_um=300.0):
    raw_rind = FreshRind(
        wet_mass=500.0,
        moisture_fraction=0.8,
        pectin_content_dry_basis=0.2,
        GalA_fraction_of_pectin=0.78,
        initial_DE=0.745,
        initial_Mw=654000.0
    )
    return condition_feedstock(
        fresh_rind=raw_rind,
        target_moisture=0.08,
        d50_um=d50_um
    )

def create_base_params():
    return KineticParameters(
        k_ref_ext=0.05, Ea_ext=35000, n_ext=1.0, alpha=1.0,
        k_ref_hyd=0.03, Ea_hyd=40000, n_hyd=1.0,
        k_ref_deg=0.01, Ea_deg=50000, n_deg=1.0,
        k_ref_de=0.02,  Ea_de=45000,  n_de=1.0, gamma_citric=0.0,
        beta_mw=1.0
    )

def test_simulator_invariants():
    feedstock = create_base_feedstock()
    params = create_base_params()
    
    res = simulate(
        feedstock=feedstock,
        temperature_celsius=80.0,
        pH=2.0,
        C_citric=0.0,
        time_min=60.0,
        kinetic_params=params,
        recovery_efficiency=0.90
    )
    
    # 1. Mass conservation
    assert res.max_epsilon_M < 1e-10
    
    # 2. GalA conservation
    assert res.max_epsilon_G < 1e-10
    
    # 3. Positivity
    states = res.state
    assert np.all(states.matrix_pectin >= -1e-12)
    assert np.all(states.soluble_intact_pectin >= -1e-12)
    assert np.all(states.low_mw_pectin >= -1e-12)
    assert np.all(states.loss_pectin >= -1e-12)
    assert np.all(states.G_sol >= -1e-12)
    assert np.all(states.G_lowMW >= -1e-12)
    assert np.all(states.G_loss >= -1e-12)
    
    # 4. Recovery invariant
    np.testing.assert_allclose(res.Y_GalA_product, 0.90 * res.Y_GalA_extract, rtol=1e-6)
    
    # 5. Product properties
    P_sol = res.final_P_sol
    P_lowMW = res.final_P_lowMW
    expected_product_DE = (res.final_DE_sol * P_sol + res.final_DE_lowMW * P_lowMW) / (P_sol + P_lowMW)
    np.testing.assert_allclose(res.final_DE_product, expected_product_DE, rtol=1e-6)
    
    expected_product_MW = (res.final_Mw_sol * P_sol + res.final_Mw_lowMW * P_lowMW) / (P_sol + P_lowMW)
    np.testing.assert_allclose(res.final_Mw_product, expected_product_MW, rtol=1e-6)
    
    # Basic physically bounded outputs
    assert res.final_DE_sol <= feedstock.DE
    assert res.final_Mw_sol <= 654000.0
    assert 0 <= res.final_DE_product <= 1.0

def test_reference_state_rates():
    # At T=353.15K (80C), pH=2, d50=300
    params = create_base_params()
    rates = calculate_rate_constants(80.0 + 273.15, 2.0, 0.0, 300.0, params)
    
    np.testing.assert_allclose(rates.k_ext, 0.05)
    np.testing.assert_allclose(rates.k_hyd, 0.03)
    np.testing.assert_allclose(rates.k_deg, 0.01)
    np.testing.assert_allclose(rates.k_de, 0.02)

def test_particle_size_effect():
    params = create_base_params()
    # Base rate at 300um
    rates_300 = calculate_rate_constants(80.0 + 273.15, 2.0, 0.0, 300.0, params)
    # Higher rate at 150um
    rates_150 = calculate_rate_constants(80.0 + 273.15, 2.0, 0.0, 150.0, params)
    
    assert rates_150.k_ext > rates_300.k_ext
