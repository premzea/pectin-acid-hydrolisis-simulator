from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from pectin.separation import SeparationRoute, Route, SeparationResult, SeparationPhysics, simulate_separation

def ph_to_citric_wt_fraction(ph: float) -> float:
    """
    Calculate the citric acid mass fraction (kg acid / kg water) required to achieve target extraction pH.
    Uses triprotic citric acid dissociation equilibrium:
      MW = 192.12 g/mol, Ka1 = 7.4e-4 (pKa1 = 3.13)
      [H+] = 10^(-pH)
      C_citric_M = [H+] * (1 + [H+] / Ka1)
      C_citric_g_per_L = C_citric_M * 192.12
      wt_fraction = C_citric_g_per_L / 1000.0
    Clamped to realistic boundaries [0.001, 0.05] (0.1% to 5.0% wt).
    """
    ph = max(1.2, min(6.0, float(ph)))
    h_plus = 10.0 ** (-ph)
    ka1 = 7.4e-4
    c_molar = h_plus * (1.0 + (h_plus / ka1))
    c_g_per_l = c_molar * 192.12
    wt_fraction = c_g_per_l / 1000.0
    return max(0.001, min(0.05, float(wt_fraction)))

class MarketPreset(BaseModel):
    name: str
    price_usd_per_kg: float

MARKET_PRESETS = [
    MarketPreset(name="Downside / Commodity", price_usd_per_kg=10.0),
    MarketPreset(name="Base / Colombian Industrial", price_usd_per_kg=14.0),
    MarketPreset(name="Premium / Differentiated", price_usd_per_kg=18.0)
]

class MarketPricing(BaseModel):
    preset_name: Optional[str] = None
    custom_price_usd_per_kg: Optional[float] = None
    
    def get_price(self) -> float:
        if self.custom_price_usd_per_kg is not None:
            return self.custom_price_usd_per_kg
        for preset in MARKET_PRESETS:
            if preset.name == self.preset_name:
                return preset.price_usd_per_kg
        # Fallback to base
        return 14.0

class CostAssumptions(BaseModel):
    # Process inputs (per unit)
    feedstock_usd_per_kg: float = 0.0
    citric_acid_usd_per_kg: float = 1.20
    water_usd_per_l: float = 0.002
    electricity_usd_per_kwh: float = 0.15
    thermal_energy_usd_per_mj: float = 0.02
    
    # Downstream separation unit costs
    drying_usd_per_kg_water: float = 0.05
    separation_usd_per_l: float = 0.01
    ethanol_usd_per_l: float = 3.25
    membrane_usd_per_m2: float = 50.0
    membrane_lifespan_batches: int = 100
    uf_electricity_usd_per_kwh: float = 0.15
    
    # Process defaults
    default_target_ph: float = 2.2
    default_liquid_ratio: float = 15.0
    
    # Legacy Recovery / Purification (fallback)
    purification_usd_per_kg_pectin: float = 2.00

class DownstreamCostBreakdown(BaseModel):
    ethanol_cost_usd: float = 0.0
    membrane_amortization_usd: float = 0.0
    uf_power_cost_usd: float = 0.0
    evaporation_energy_cost_usd: float = 0.0
    drying_cost_usd: float = 0.0
    total_downstream_cost_usd: float = 0.0

class BatchEconomicsResult(BaseModel):
    route: SeparationRoute
    batch_dry_peel_kg: float
    kg_pectin_extracted: float
    kg_finished_pectin: float
    
    upstream_cost_usd: float
    downstream_cost_usd: float
    total_process_cost_usd: float
    
    revenue_usd: float
    economic_contribution_usd: float
    break_even_max_process_cost_usd: float
    price_used_usd: float
    
    citric_acid_used_kg: float
    water_used_l: float
    
    separation_physics: SeparationResult
    downstream_costs: DownstreamCostBreakdown

class EconomicsEngine:
    def __init__(self, costs: Optional[CostAssumptions] = None, market: Optional[MarketPricing] = None):
        self.costs = costs or CostAssumptions()
        self.market = market or MarketPricing()
        
    def evaluate_batch(
        self,
        batch_kg: float,
        yield_kg_per_kg_peel: float,
        route: SeparationRoute = SeparationRoute.HYBRID,
        liquid_ratio: Optional[float] = None,
        target_ph: Optional[float] = None,
        c_citric_wt_fraction: Optional[float] = None,
        temp_c: float = 85.0
    ) -> BatchEconomicsResult:
        """
        Full TEA simulation for an extraction & downstream separation batch.
        Integrates upstream reactor consumption with dynamic citric acid requirement and pectin.separation physics.
        """
        ratio = liquid_ratio if liquid_ratio is not None else self.costs.default_liquid_ratio
        ph = target_ph if target_ph is not None else self.costs.default_target_ph
        
        if c_citric_wt_fraction is None:
            c_citric_wt = ph_to_citric_wt_fraction(ph)
        else:
            c_citric_wt = c_citric_wt_fraction
            
        kg_extracted_theoretical = batch_kg * yield_kg_per_kg_peel
        liters_water = batch_kg * ratio
        kg_citric = liters_water * c_citric_wt
        kwh_upstream_elec = batch_kg * 1.5 * (temp_c / 85.0)
        
        # Upstream variable costs
        upstream_cost = 0.0
        upstream_cost += batch_kg * self.costs.feedstock_usd_per_kg
        upstream_cost += liters_water * self.costs.water_usd_per_l
        upstream_cost += kg_citric * self.costs.citric_acid_usd_per_kg
        upstream_cost += kwh_upstream_elec * self.costs.electricity_usd_per_kwh
        upstream_cost += liters_water * self.costs.separation_usd_per_l
        
        # Downstream separation physics from pectin.separation
        sep_result = simulate_separation(
            route=route,
            liters_extract=liters_water,
            kg_pectin_extracted=kg_extracted_theoretical
        )
        
        # Calculate downstream financial costs from physical flows
        ethanol_cost = sep_result.ethanol_consumed_l * self.costs.ethanol_usd_per_l
        membrane_amort = (
            (sep_result.membrane_area_m2 * self.costs.membrane_usd_per_m2 / max(1, self.costs.membrane_lifespan_batches))
            if sep_result.membrane_area_m2 > 0 else 0.0
        )
        uf_power_cost = sep_result.uf_electricity_kwh * self.costs.uf_electricity_usd_per_kwh
        evap_cost = sep_result.evaporation_thermal_mj * self.costs.thermal_energy_usd_per_mj
        drying_cost = sep_result.drying_water_kg * self.costs.drying_usd_per_kg_water
        
        downstream_cost = ethanol_cost + membrane_amort + uf_power_cost + evap_cost + drying_cost
        total_process_cost = upstream_cost + downstream_cost
        
        kg_finished = sep_result.kg_pectin_recovered
        price_per_kg = self.market.get_price()
        revenue = kg_finished * price_per_kg
        contribution = revenue - total_process_cost
        break_even_cost = revenue
        
        return BatchEconomicsResult(
            route=sep_result.route,
            batch_dry_peel_kg=batch_kg,
            kg_pectin_extracted=kg_extracted_theoretical,
            kg_finished_pectin=kg_finished,
            upstream_cost_usd=upstream_cost,
            downstream_cost_usd=downstream_cost,
            total_process_cost_usd=total_process_cost,
            revenue_usd=revenue,
            economic_contribution_usd=contribution,
            break_even_max_process_cost_usd=break_even_cost,
            price_used_usd=price_per_kg,
            citric_acid_used_kg=kg_citric,
            water_used_l=liters_water,
            separation_physics=sep_result,
            downstream_costs=DownstreamCostBreakdown(
                ethanol_cost_usd=ethanol_cost,
                membrane_amortization_usd=membrane_amort,
                uf_power_cost_usd=uf_power_cost,
                evaporation_energy_cost_usd=evap_cost,
                drying_cost_usd=drying_cost,
                total_downstream_cost_usd=downstream_cost
            )
        )

    def calculate_yield(self, p_sol: float, p_lowmw: float, n_recovery: float) -> float:
        extracted = p_sol + p_lowmw
        return extracted * n_recovery

    def calculate_process_cost(self, 
                               kg_dry_peel: float, 
                               liters_water: float, 
                               kg_citric: float, 
                               kwh_electricity: float, 
                               kg_water_removed: float,
                               kg_finished_pectin: float) -> float:
        cost = 0.0
        cost += kg_dry_peel * self.costs.feedstock_usd_per_kg
        cost += liters_water * self.costs.water_usd_per_l
        cost += kg_citric * self.costs.citric_acid_usd_per_kg
        cost += kwh_electricity * self.costs.electricity_usd_per_kwh
        cost += liters_water * self.costs.separation_usd_per_l
        cost += kg_water_removed * self.costs.drying_usd_per_kg_water
        cost += kg_finished_pectin * self.costs.purification_usd_per_kg_pectin
        return cost

    def calculate_contribution(self, 
                               kg_finished_pectin: float, 
                               total_process_cost: float) -> float:
        revenue = kg_finished_pectin * self.market.get_price()
        return revenue - total_process_cost

    def calculate_break_even_cost(self, kg_finished_pectin: float) -> float:
        return kg_finished_pectin * self.market.get_price()
