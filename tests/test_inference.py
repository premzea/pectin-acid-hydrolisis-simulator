import numpy as np
import sys

# Ensure pectin is discoverable
sys.path.append("/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/src")

from pectin.inference.model_registry import MODELS
from pectin.inference.campaign_manager import CampaignManager, residuals, log_likelihood, log_prior, log_posterior
from pectin.chemistry.kinetics import KineticParameters

def test_model_schema_mapping():
    schema = MODELS["v2.0-reduced"]
    
    # Check parameters
    assert len(schema.param_names) == 5
    assert "Ea_degradation" in schema.param_names
    
    # Check transforms
    theta_test = np.array([1.0, 0.05, 0.05, 0.05, 40000.0])
    q = schema.transform(theta_test)
    theta_rec = schema.inverse_transform(q)
    
    np.testing.assert_allclose(theta_test, theta_rec, rtol=1e-5)
    
    # Check unpacking
    params = schema.unpack(theta_test)
    assert isinstance(params, KineticParameters)
    
    # Verify fixed constants
    assert params.k_ref_ext == 0.05
    assert params.Ea_ext == 35000.0
    
    # Verify unified activation energies
    assert params.Ea_hyd == 40000.0
    assert params.Ea_deg == 40000.0
    assert params.Ea_de == 40000.0

def test_campaign_manager_initialization():
    cm = CampaignManager(model_id="v2.0-reduced")
    assert cm.model_id == "v2.0-reduced"
    assert len(cm.param_names) == 5
    assert len(cm.theta_true) == 5
