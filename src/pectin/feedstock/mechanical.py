"""
Mechanical conditioning module for fresh passion-fruit rind.
Handles fresh rind comminution, dry-matter calculations, and particle size distribution.
"""
from dataclasses import dataclass
import numpy as np
from .properties import FreshRind, ConditionedFeedstock

@dataclass
class ShreddedRind:
    """
    Fresh passion-fruit rind shredded/comminuted via food processor.
    Retains fresh moisture content (X_w,0 ~ 0.81 - 0.86) while establishing
    a characteristic particle size d50 (microns).
    """
    fresh_rind: FreshRind
    d50_um: float = 1000.0  # Default reference comminution size (1000 um = 1.0 mm)
    cutting_time_s: float = 45.0
    
    def __post_init__(self):
        if self.d50_um <= 0:
            raise ValueError("d50_um must be positive.")
        if self.cutting_time_s < 0:
            raise ValueError("cutting_time_s cannot be negative.")

    @property
    def wet_mass(self) -> float:
        return self.fresh_rind.wet_mass

    @property
    def moisture_fraction(self) -> float:
        return self.fresh_rind.moisture_fraction

    @property
    def dry_matter_mass(self) -> float:
        """Dry matter mass: m_dry = m_fresh * (1 - X_w,0)."""
        return self.fresh_rind.dry_matter_mass

    @property
    def absolute_pectin_mass(self) -> float:
        return self.fresh_rind.absolute_pectin_mass

    @property
    def GalA_fraction(self) -> float:
        return self.fresh_rind.GalA_fraction_of_pectin

    @property
    def DE(self) -> float:
        return self.fresh_rind.initial_DE

    @property
    def Mw_matrix(self) -> float:
        return self.fresh_rind.initial_Mw

    def to_conditioned_feedstock(self) -> ConditionedFeedstock:
        """
        Convert to ConditionedFeedstock directly for unified reactor modeling
        without oven drying.
        """
        return ConditionedFeedstock(
            dry_matter_mass=self.dry_matter_mass,
            moisture_fraction=self.moisture_fraction,
            pectin_mass=self.absolute_pectin_mass,
            GalA_fraction=self.GalA_fraction,
            DE=self.DE,
            Mw_matrix=self.Mw_matrix,
            d50_um=self.d50_um
        )

def comminute_fresh_rind(
    wet_mass_g: float,
    moisture_fraction: float = 0.84,
    pectin_content_dry_basis: float = 0.22,
    GalA_fraction: float = 0.78,
    initial_DE: float = 0.72,
    initial_Mw: float = 650000.0,
    d50_um: float = 1000.0,
    cutting_time_s: float = 45.0
) -> ShreddedRind:
    """
    Standardized food-processor comminution of fresh passion-fruit rind.
    Creates a ShreddedRind instance with verified physical invariants.
    """
    fresh = FreshRind(
        wet_mass=wet_mass_g,
        moisture_fraction=moisture_fraction,
        pectin_content_dry_basis=pectin_content_dry_basis,
        GalA_fraction_of_pectin=GalA_fraction,
        initial_DE=initial_DE,
        initial_Mw=initial_Mw
    )
    return ShreddedRind(
        fresh_rind=fresh,
        d50_um=d50_um,
        cutting_time_s=cutting_time_s
    )
