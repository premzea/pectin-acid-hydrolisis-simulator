from .properties import FreshRind, ConditionedFeedstock

def condition_feedstock(
    fresh_rind: FreshRind, 
    target_moisture: float, 
    d50_um: float
) -> ConditionedFeedstock:
    """End-to-end conditioning pipeline for V1 (physical state changes)."""
    if target_moisture >= fresh_rind.moisture_fraction:
        raise ValueError("Target moisture must be less than initial moisture")
        
    dry_mass = fresh_rind.dry_matter_mass
    
    return ConditionedFeedstock(
        dry_matter_mass=dry_mass,
        moisture_fraction=target_moisture,
        pectin_mass=fresh_rind.absolute_pectin_mass,
        GalA_fraction=fresh_rind.GalA_fraction_of_pectin,
        DE=fresh_rind.initial_DE,
        Mw_matrix=fresh_rind.initial_Mw,
        d50_um=d50_um
    )
