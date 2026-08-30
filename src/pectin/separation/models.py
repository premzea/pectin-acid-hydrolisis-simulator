from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional

class SeparationRoute(str, Enum):
    CONVENTIONAL = "conventional"
    HYBRID = "hybrid"
    DIRECT_DRYING = "direct_drying"

# Alias for backward compatibility
Route = SeparationRoute

class SeparationPhysics(BaseModel):
    ethanol_recovery_pct: float = 0.95  # 95% recovery rate in distillation
    uf_flux_lmh: float = 25.0           # L/m2/h
    uf_operating_time_h: float = 8.0    # hours per batch
    uf_power_kw_per_m2: float = 2.0     # 2 kW/m2 membrane power
    evaporation_thermal_mj_per_kg: float = 2.5  # ~2.5 MJ/kg water evaporation

class SeparationResult(BaseModel):
    route: SeparationRoute
    kg_pectin_extracted: float
    kg_pectin_recovered: float
    yield_recovery_fraction: float
    
    liters_extract: float
    permeate_volume_l: float = 0.0
    retentate_volume_l: float = 0.0
    membrane_area_m2: float = 0.0
    
    ethanol_used_l: float = 0.0
    ethanol_consumed_l: float = 0.0
    
    evaporation_water_kg: float = 0.0
    drying_water_kg: float = 0.0
    
    uf_electricity_kwh: float = 0.0
    evaporation_thermal_mj: float = 0.0

def simulate_separation(
    route: SeparationRoute,
    liters_extract: float,
    kg_pectin_extracted: float,
    physics: Optional[SeparationPhysics] = None
) -> SeparationResult:
    """
    Algebraic mass and energy balance for downstream separation routes.
    
    Routes:
      1. CONVENTIONAL: Evaporate 80% water, then 2:1 ethanol precipitation (90% pectin recovery)
      2. HYBRID: UF/DF 10x volume reduction, then 1:1 ethanol precipitation (95% pectin recovery)
      3. DIRECT_DRYING: UF/DF 10x volume reduction, zero ethanol, direct thermal drying (98% recovery)
    """
    if physics is None:
        physics = SeparationPhysics()
        
    ethanol_consumed_l = 0.0
    ethanol_used_l = 0.0
    permeate_vol = 0.0
    retentate_vol = 0.0
    membrane_area_m2 = 0.0
    evaporation_water_kg = 0.0
    drying_water_kg = 0.0
    uf_electricity_kwh = 0.0
    evaporation_thermal_mj = 0.0
    
    # 1. CONVENTIONAL (Route 3)
    if route == SeparationRoute.CONVENTIONAL or route == "conventional":
        # Evaporate 80% water prior to precipitation
        evaporation_water_kg = liters_extract * 0.80
        remaining_liquor = liters_extract - evaporation_water_kg
        
        # 2 volumes ethanol per volume liquor
        ethanol_used_l = remaining_liquor * 2.0
        ethanol_consumed_l = ethanol_used_l * (1.0 - physics.ethanol_recovery_pct)
        
        # Drying remaining moisture cake (assumed ~1:1 water to pectin)
        drying_water_kg = kg_pectin_extracted * 1.0
        
        # 90% recovery of soluble pectin
        kg_recovered = kg_pectin_extracted * 0.90
        recovery_fraction = 0.90
        
    # 2. HYBRID (Route 2)
    elif route == SeparationRoute.HYBRID or route == "hybrid":
        # UF concentration: 10x volume reduction (90% permeate, 10% retentate)
        permeate_vol = liters_extract * 0.90
        retentate_vol = liters_extract * 0.10
        
        membrane_area_m2 = permeate_vol / (physics.uf_flux_lmh * physics.uf_operating_time_h)
        uf_electricity_kwh = membrane_area_m2 * physics.uf_power_kw_per_m2 * physics.uf_operating_time_h
        
        # 1 volume ethanol per volume retentate
        ethanol_used_l = retentate_vol * 1.0
        ethanol_consumed_l = ethanol_used_l * (1.0 - physics.ethanol_recovery_pct)
        
        drying_water_kg = kg_pectin_extracted * 1.0
        kg_recovered = kg_pectin_extracted * 0.95
        recovery_fraction = 0.95
        
    # 3. DIRECT DRYING (Route 1)
    elif route == SeparationRoute.DIRECT_DRYING or route == "direct_drying":
        permeate_vol = liters_extract * 0.90
        retentate_vol = liters_extract * 0.10
        
        membrane_area_m2 = permeate_vol / (physics.uf_flux_lmh * physics.uf_operating_time_h)
        uf_electricity_kwh = membrane_area_m2 * physics.uf_power_kw_per_m2 * physics.uf_operating_time_h
        
        # Zero ethanol
        ethanol_used_l = 0.0
        ethanol_consumed_l = 0.0
        
        # Direct thermal drying of entire concentrated retentate
        drying_water_kg = retentate_vol
        kg_recovered = kg_pectin_extracted * 0.98
        recovery_fraction = 0.98
        
    else:
        raise ValueError(f"Unknown separation route: {route}")
        
    if evaporation_water_kg > 0:
        evaporation_thermal_mj = evaporation_water_kg * physics.evaporation_thermal_mj_per_kg

    return SeparationResult(
        route=SeparationRoute(route),
        kg_pectin_extracted=kg_pectin_extracted,
        kg_pectin_recovered=kg_recovered,
        yield_recovery_fraction=recovery_fraction,
        liters_extract=liters_extract,
        permeate_volume_l=permeate_vol,
        retentate_volume_l=retentate_vol,
        membrane_area_m2=membrane_area_m2,
        ethanol_used_l=ethanol_used_l,
        ethanol_consumed_l=ethanol_consumed_l,
        evaporation_water_kg=evaporation_water_kg,
        drying_water_kg=drying_water_kg,
        uf_electricity_kwh=uf_electricity_kwh,
        evaporation_thermal_mj=evaporation_thermal_mj
    )
