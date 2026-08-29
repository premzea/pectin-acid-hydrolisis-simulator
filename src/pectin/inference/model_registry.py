import numpy as np
from pectin.chemistry.kinetics import KineticParameters

ALPHA_MIN = 0.2
ALPHA_MAX = 2.5

class ModelSchema:
    def __init__(self, config: dict):
        self.id = config["id"]
        self.name = config["name"]
        self.description = config["description"]
        self.simulator_target = config.get("simulator_target", "simulate_v1")
        
        self.fitted_parameters = config["fitted_parameters"]
        self.fixed_constants = config["fixed_constants"]
        self.parameter_mapping = config["parameter_mapping"]
        
        self.param_names = [p["name"] for p in self.fitted_parameters]
        self.bounds = {p["name"]: p["bounds"] for p in self.fitted_parameters}
        
    def transform(self, theta: np.ndarray) -> np.ndarray:
        """Transforms natural parameters to unconstrained real space (q)."""
        q = np.empty_like(theta, dtype=np.float64)
        for i, name in enumerate(self.param_names):
            if name == "alpha":
                # Logit transform for alpha
                norm_alpha = (theta[i] - ALPHA_MIN) / (ALPHA_MAX - ALPHA_MIN)
                norm_alpha = np.clip(norm_alpha, 1e-6, 1.0 - 1e-6)
                q[i] = np.log(norm_alpha / (1.0 - norm_alpha))
            else:
                # Log transform for kinetics
                q[i] = np.log(theta[i])
        return q

    def inverse_transform(self, q: np.ndarray) -> np.ndarray:
        """Transforms unconstrained space (q) back to natural bounds (theta)."""
        theta = np.empty_like(q, dtype=np.float64)
        for i, name in enumerate(self.param_names):
            if name == "alpha":
                sig = 1.0 / (1.0 + np.exp(-np.clip(q[i], -30.0, 30.0)))
                theta[i] = ALPHA_MIN + sig * (ALPHA_MAX - ALPHA_MIN)
            else:
                b_min, b_max = self.bounds[name]
                # Slight clipping to prevent overflow
                theta[i] = np.clip(np.exp(np.clip(q[i], -15.0, 15.0)), b_min, b_max)
        return theta

    def unpack(self, theta_active: np.ndarray) -> KineticParameters:
        """Maps active parameters into the full KineticParameters dataclass."""
        # 1. Fill base with defaults / standard constants
        base_params = {
            "n_ext": 1.0, "n_hyd": 1.0, "n_deg": 1.0, "n_de": 1.0,
            "gamma_citric": 0.0, "beta_mw": 1.0
        }
        
        # 2. Add fixed constants from schema
        for k, v in self.fixed_constants.items():
            base_params[k] = v
            
        # 3. Map active parameters
        for i, name in enumerate(self.param_names):
            val = theta_active[i]
            # Find all target base params mapped to this active parameter
            for base_k, mapped_name in self.parameter_mapping.items():
                if mapped_name == name:
                    base_params[base_k] = val
                    
        return KineticParameters(**base_params)

# Define schemas
MODELS = {
    "v1.3-full": ModelSchema({
        "id": "v1.3-full",
        "name": "Full 9-Parameter Kinetic Model",
        "description": "Baseline V1.3 model with independent extraction and degradation mechanisms.",
        "simulator_target": "simulate_v1",
        "fitted_parameters": [
            {"name": "k_ref_ext", "bounds": [1e-4, 2.0], "initial": 0.05},
            {"name": "Ea_ext", "bounds": [10000, 150000], "initial": 35000},
            {"name": "alpha", "bounds": [0.2, 2.5], "initial": 1.0},
            {"name": "k_ref_hyd", "bounds": [1e-4, 2.0], "initial": 0.05},
            {"name": "Ea_hyd", "bounds": [10000, 150000], "initial": 40000},
            {"name": "k_ref_deg", "bounds": [1e-4, 2.0], "initial": 0.05},
            {"name": "Ea_deg", "bounds": [10000, 150000], "initial": 40000},
            {"name": "k_ref_de", "bounds": [1e-4, 2.0], "initial": 0.05},
            {"name": "Ea_de", "bounds": [10000, 150000], "initial": 40000}
        ],
        "fixed_constants": {},
        "parameter_mapping": {
            "k_ref_ext": "k_ref_ext", "Ea_ext": "Ea_ext",
            "alpha": "alpha",
            "k_ref_hyd": "k_ref_hyd", "Ea_hyd": "Ea_hyd",
            "k_ref_deg": "k_ref_deg", "Ea_deg": "Ea_deg",
            "k_ref_de": "k_ref_de", "Ea_de": "Ea_de"
        }
    }),
    
    "v2.0-reduced": ModelSchema({
        "id": "v2.0-reduced",
        "name": "Reduced 5-Parameter Model",
        "description": "Anchors extraction to literature values and unifies all acid-catalyzed degradation mechanisms into a single global activation energy.",
        "simulator_target": "simulate_v1",
        "fitted_parameters": [
            {"name": "alpha", "bounds": [0.2, 2.5], "initial": 1.0},
            {"name": "k_ref_hyd", "bounds": [1e-4, 2.0], "initial": 0.05},
            {"name": "k_ref_deg", "bounds": [1e-4, 2.0], "initial": 0.05},
            {"name": "k_ref_de", "bounds": [1e-4, 2.0], "initial": 0.05},
            {"name": "Ea_degradation", "bounds": [10000, 150000], "initial": 40000}
        ],
        "fixed_constants": {
            "k_ref_ext": 0.05,
            "Ea_ext": 35000.0
        },
        "parameter_mapping": {
            "alpha": "alpha",
            "k_ref_hyd": "k_ref_hyd",
            "k_ref_deg": "k_ref_deg",
            "k_ref_de": "k_ref_de",
            "Ea_hyd": "Ea_degradation",
            "Ea_deg": "Ea_degradation",
            "Ea_de": "Ea_degradation"
        }
    })
}
