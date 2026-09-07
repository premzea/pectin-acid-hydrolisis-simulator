"""
Comprehensive unit test suite for UAE pipeline:
- Fresh comminution (mechanical.py)
- UAE acoustic kinetics (uae_kinetics.py)
- Colorimetric soft sensor (colorimeter.py)
- Paired UAE simulation & thermal control comparison (uae_simulator.py)
"""
import pytest
import numpy as np

from pectin.feedstock.mechanical import comminute_fresh_rind, ShreddedRind
from pectin.chemistry.kinetics import KineticParameters
from pectin.chemistry.uae_kinetics import (
    AcousticKineticsParameters,
    calculate_uae_rate_constants
)
from pectin.sensors.colorimeter import (
    ColorimetricSoftSensor,
    ColorimeterMeasurement,
    ChannelCalibration
)
from pectin.simulator.uae_simulator import (
    simulate_uae_run,
    simulate_paired_uae_comparison
)

def create_fresh_test_rind(wet_mass=500.0, moisture=0.84, d50=1000.0):
    return comminute_fresh_rind(
        wet_mass_g=wet_mass,
        moisture_fraction=moisture,
        pectin_content_dry_basis=0.22,
        GalA_fraction=0.78,
        initial_DE=0.72,
        initial_Mw=650000.0,
        d50_um=d50,
        cutting_time_s=45.0
    )

def create_test_acoustic_params():
    base = KineticParameters(
        k_ref_ext=0.04, Ea_ext=40000, n_ext=1.0, alpha=1.0,
        k_ref_hyd=0.015, Ea_hyd=45000, n_hyd=1.0,
        k_ref_deg=0.005, Ea_deg=55000, n_deg=1.0,
        k_ref_de=0.02, Ea_de=42000, n_de=1.0, gamma_citric=0.0,
        beta_mw=1.0
    )
    return AcousticKineticsParameters(
        base_params=base,
        kappa_ext=0.05,
        beta_ext=1.0,
        kappa_hyd=0.02,
        beta_hyd=1.0,
        kappa_deg=0.005,
        beta_deg=1.0,
        f_nominal_khz=40.0
    )

# --- 1. Feedstock Tests ---
def test_fresh_rind_comminution():
    rind = create_fresh_test_rind(wet_mass=500.0, moisture=0.84, d50=1000.0)
    # Dry matter should equal 500 * (1 - 0.84) = 80 g
    assert np.isclose(rind.dry_matter_mass, 80.0)
    # Pectin mass = 80 * 0.22 = 17.6 g
    assert np.isclose(rind.absolute_pectin_mass, 17.6)
    
    conditioned = rind.to_conditioned_feedstock()
    assert np.isclose(conditioned.dry_matter_mass, 80.0)
    assert np.isclose(conditioned.moisture_fraction, 0.84)
    assert np.isclose(conditioned.d50_um, 1000.0)

# --- 2. Acoustic Kinetics Tests ---
def test_acoustic_kinetics_collapse_under_zero_power():
    params = create_test_acoustic_params()
    rates = calculate_uae_rate_constants(
        T_kelvin=353.15,
        pH=2.0,
        C_citric=0.05,
        d50_um=1000.0,
        P_acoustic_w=0.0,
        V_slurry_l=2.0,
        params=params
    )
    # At P_acoustic = 0 W, psi factors must be exactly 1.0
    assert rates.psi_ext == 1.0
    assert rates.psi_hyd == 1.0
    assert rates.psi_deg == 1.0
    assert np.isclose(rates.k_ext, rates.k_ext_thermal)
    assert np.isclose(rates.k_hyd, rates.k_hyd_thermal)
    assert np.isclose(rates.k_deg, rates.k_deg_thermal)

def test_acoustic_kinetics_enhancement():
    params = create_test_acoustic_params()
    rates = calculate_uae_rate_constants(
        T_kelvin=353.15,
        pH=2.0,
        C_citric=0.05,
        d50_um=1000.0,
        P_acoustic_w=100.0,  # 100 W in 2 L = 50 W/L
        V_slurry_l=2.0,
        params=params
    )
    # 50 W/L with kappa_ext=0.05 -> psi_ext = 1 + 0.05 * 50 = 3.5
    assert rates.psi_ext > 1.0
    assert np.isclose(rates.psi_ext, 3.5)
    assert rates.k_ext > rates.k_ext_thermal
    # Depolymerization is also accelerated
    assert rates.psi_hyd > 1.0
    assert np.isclose(rates.psi_hyd, 1 + 0.02 * 50)

# --- 3. UAE Simulator & Paired Comparison Tests ---
def test_uae_simulator_invariants():
    rind = create_fresh_test_rind()
    params = create_test_acoustic_params()
    
    res = simulate_uae_run(
        shredded_rind=rind,
        temperature_celsius=65.0,
        pH=2.2,
        C_citric=0.05,
        time_min=30.0,
        P_acoustic_w=60.0,
        V_slurry_l=1.5,
        acoustic_params=params
    )
    
    # 1. Mass conservation
    assert res.max_epsilon_M < 1e-9
    # 2. GalA conservation
    assert res.max_epsilon_G < 1e-9
    # 3. Positivity
    assert np.all(res.state.matrix_pectin >= -1e-12)
    assert np.all(res.state.soluble_intact_pectin >= -1e-12)
    assert np.all(res.state.low_mw_pectin >= -1e-12)
    assert np.all(res.state.loss_pectin >= -1e-12)
    # 4. Product properties within bounds
    assert 0.0 <= res.final_DE_product <= 1.0
    assert 10000.0 <= res.final_Mw_product <= 650000.0

def test_paired_uae_comparison():
    rind = create_fresh_test_rind()
    params = create_test_acoustic_params()
    
    comp = simulate_paired_uae_comparison(
        shredded_rind=rind,
        temperature_celsius=65.0,
        pH=2.2,
        C_citric=0.05,
        time_min=30.0,
        P_acoustic_w=80.0,
        V_slurry_l=2.0,
        acoustic_params=params
    )
    
    # Ultrasound must increase initial extraction yield relative to matched thermal control
    assert comp.delta_yield_apsp > 0
    assert comp.relative_yield_increase > 0
    # Intense cavitation leads to some molecular weight reduction
    assert comp.Mw_retention_ratio <= 1.0001
    assert comp.control_result.Y_p > 0

# --- 4. Colorimetric Soft-Sensor Tests ---
def test_soft_sensor_matrix_correction_and_evaluation():
    sensor = ColorimetricSoftSensor()
    
    # Raw cuvette readings with matrix interference (e.g. carotenoids absorbing at 450-515)
    sample_blank = ColorimeterMeasurement(
        channel_absorbance={
            410: 0.15, 450: 0.12, 480: 0.08, 515: 0.04,
            555: 0.02, 590: 0.01, 630: 0.01, 680: 0.02
        },
        dilution_factor=1.0
    )
    
    carbazole_dev = ColorimeterMeasurement(
        channel_absorbance={
            410: 0.20, 450: 0.25, 480: 0.40, 515: 0.85,
            555: 0.70, 590: 0.15, 630: 0.05, 680: 0.03
        },
        dilution_factor=5.0  # 1:5 dilution applied
    )
    
    copper_dev = ColorimeterMeasurement(
        channel_absorbance={
            410: 0.18, 450: 0.15, 480: 0.10, 515: 0.06,
            555: 0.04, 590: 0.20, 630: 0.65, 680: 0.50
        },
        dilution_factor=5.0
    )
    
    result = sensor.evaluate(
        carbazole_developed=carbazole_dev,
        copper_developed=copper_dev,
        sample_blank=sample_blank
    )
    
    # Net absorbance must be positive and subtracted properly
    assert result.A_net_515 > 0
    assert result.A_net_555 > 0
    assert result.A_net_630 > 0
    assert result.C_GalA_g_per_l > 0
    assert result.C_pectin_equiv_g_per_l > 0
    assert result.is_within_linear_range is True
    assert result.dilution_advisory is None

def test_soft_sensor_saturation_warning():
    sensor = ColorimetricSoftSensor()
    
    # Saturated cuvette reading (> 1.50 AU)
    saturated_carb = ColorimeterMeasurement(
        channel_absorbance={
            515: 1.85, 555: 1.60, 680: 0.05
        },
        dilution_factor=1.0
    )
    copper = ColorimeterMeasurement(
        channel_absorbance={630: 0.50, 680: 0.02},
        dilution_factor=1.0
    )
    blank = ColorimeterMeasurement(
        channel_absorbance={515: 0.02, 555: 0.01, 630: 0.01, 680: 0.01},
        dilution_factor=1.0
    )
    
    result = sensor.evaluate(
        carbazole_developed=saturated_carb,
        copper_developed=copper,
        sample_blank=blank
    )
    
    assert result.is_within_linear_range is False
    assert result.dilution_advisory is not None
    assert result.suggested_dilution_factor is not None
    assert result.suggested_dilution_factor > 1.0
    assert any("saturation" in w.lower() for w in result.warnings)
