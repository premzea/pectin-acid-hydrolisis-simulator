from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Union

class DownstreamFlowsheet(str, Enum):
    HYBRID_MEMBRANE_SOLVENT = "hybrid"
    ZERO_SOLVENT_DIRECT_DRYING = "direct_drying"
    CONVENTIONAL_EVAPORATIVE = "conventional"
    LIQUID_CONCENTRATE = "liquid_concentrate"

# Aliases for backward compatibility
SeparationFlowsheet = DownstreamFlowsheet
SeparationRoute = DownstreamFlowsheet
Route = DownstreamFlowsheet

class SeparationPhysics(BaseModel):
    ethanol_recovery_pct: float = 0.95  # 95% recovery rate in distillation
    uf_flux_lmh: float = 25.0           # L/m2/h
    uf_operating_time_h: float = 8.0    # hours per batch
    uf_power_kw_per_m2: float = 2.0     # 2 kW/m2 membrane power
    evaporation_thermal_mj_per_kg: float = 2.5  # ~2.5 MJ/kg water evaporation

class SeparationResult(BaseModel):
    flowsheet: DownstreamFlowsheet
    route: DownstreamFlowsheet # alias for backward compat
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
    flowsheet: Optional[Union[DownstreamFlowsheet, str]] = None,
    liters_extract: float = 20000.0,
    kg_pectin_extracted: float = 100.0,
    physics: Optional[SeparationPhysics] = None,
    route: Optional[Union[DownstreamFlowsheet, str]] = None # alias
) -> SeparationResult:
    """
    Algebraic mass and energy balance for downstream separation flowsheets (process trains).
    
    Flowsheet Configurations:
      1. HYBRID_MEMBRANE_SOLVENT ("hybrid"):
         MF Clarification -> UF/DF 10x volume reduction -> 1:1 ethanol precipitation -> Drying (95% recovery)
      2. ZERO_SOLVENT_DIRECT_DRYING ("direct_drying"):
         MF Clarification -> UF/DF Diafiltration -> Direct thermal spray drying. Zero ethanol (98% recovery)
      3. CONVENTIONAL_EVAPORATIVE ("conventional"):
         MF Clarification -> 80% thermal evaporation -> 2:1 bulk ethanol precipitation -> Drying (90% recovery)
    """
    if physics is None:
        physics = SeparationPhysics()
        
    target_fs = flowsheet or route or DownstreamFlowsheet.HYBRID_MEMBRANE_SOLVENT
    if isinstance(target_fs, str):
        if target_fs in ["conventional", "conventional_evaporative"]:
            target_fs = DownstreamFlowsheet.CONVENTIONAL_EVAPORATIVE
        elif target_fs in ["direct_drying", "zero_solvent_direct_drying", "direct_spray_drying"]:
            target_fs = DownstreamFlowsheet.ZERO_SOLVENT_DIRECT_DRYING
        elif target_fs in ["liquid_concentrate", "liquid"]:
            target_fs = DownstreamFlowsheet.LIQUID_CONCENTRATE
        else:
            target_fs = DownstreamFlowsheet.HYBRID_MEMBRANE_SOLVENT

    ethanol_consumed_l = 0.0
    ethanol_used_l = 0.0
    permeate_vol = 0.0
    retentate_vol = 0.0
    membrane_area_m2 = 0.0
    evaporation_water_kg = 0.0
    drying_water_kg = 0.0
    uf_electricity_kwh = 0.0
    evaporation_thermal_mj = 0.0
    
    # 1. CONVENTIONAL EVAPORATIVE TRAIN
    if target_fs == DownstreamFlowsheet.CONVENTIONAL_EVAPORATIVE:
        evaporation_water_kg = liters_extract * 0.80
        remaining_liquor = liters_extract - evaporation_water_kg
        
        ethanol_used_l = remaining_liquor * 2.0
        ethanol_consumed_l = ethanol_used_l * (1.0 - physics.ethanol_recovery_pct)
        
        drying_water_kg = kg_pectin_extracted * 1.0
        kg_recovered = kg_pectin_extracted * 0.90
        recovery_fraction = 0.90
        
    # 2. HYBRID MEMBRANE-SOLVENT TRAIN
    elif target_fs == DownstreamFlowsheet.HYBRID_MEMBRANE_SOLVENT:
        permeate_vol = liters_extract * 0.90
        retentate_vol = liters_extract * 0.10
        
        membrane_area_m2 = permeate_vol / (physics.uf_flux_lmh * physics.uf_operating_time_h)
        uf_electricity_kwh = membrane_area_m2 * physics.uf_power_kw_per_m2 * physics.uf_operating_time_h
        
        ethanol_used_l = retentate_vol * 1.0
        ethanol_consumed_l = ethanol_used_l * (1.0 - physics.ethanol_recovery_pct)
        
        drying_water_kg = kg_pectin_extracted * 1.0
        kg_recovered = kg_pectin_extracted * 0.95
        recovery_fraction = 0.95
        
    # 3. ZERO-SOLVENT DIRECT DRYING TRAIN
    elif target_fs == DownstreamFlowsheet.ZERO_SOLVENT_DIRECT_DRYING:
        permeate_vol = liters_extract * 0.90
        retentate_vol = liters_extract * 0.10
        
        membrane_area_m2 = permeate_vol / (physics.uf_flux_lmh * physics.uf_operating_time_h)
        uf_electricity_kwh = membrane_area_m2 * physics.uf_power_kw_per_m2 * physics.uf_operating_time_h
        
        ethanol_used_l = 0.0
        ethanol_consumed_l = 0.0
        
        drying_water_kg = retentate_vol
        kg_recovered = kg_pectin_extracted * 0.98
        recovery_fraction = 0.98
        
    # 4. LIQUID CONCENTRATE FORMULATION
    elif target_fs == DownstreamFlowsheet.LIQUID_CONCENTRATE:
        # Clarification + UF/DF to concentrate to a liquid product, zero final drying
        permeate_vol = liters_extract * 0.90
        retentate_vol = liters_extract * 0.10
        
        membrane_area_m2 = permeate_vol / (physics.uf_flux_lmh * physics.uf_operating_time_h)
        uf_electricity_kwh = membrane_area_m2 * physics.uf_power_kw_per_m2 * physics.uf_operating_time_h
        
        ethanol_used_l = 0.0
        ethanol_consumed_l = 0.0
        
        # KEY SAVINGS: Zero drying water, leaving the retentate as the liquid product base
        drying_water_kg = 0.0
        kg_recovered = kg_pectin_extracted * 0.98
        recovery_fraction = 0.98
        
    else:
        raise ValueError(f"Unknown downstream flowsheet: {target_fs}")
        
    if evaporation_water_kg > 0:
        evaporation_thermal_mj = evaporation_water_kg * physics.evaporation_thermal_mj_per_kg

    return SeparationResult(
        flowsheet=target_fs,
        route=target_fs,
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
