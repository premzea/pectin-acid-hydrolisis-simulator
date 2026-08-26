from dataclasses import dataclass
from typing import Optional

@dataclass
class FreshRind:
    """Fresh passion-fruit rind directly from pulp-processing."""
    wet_mass: float
    moisture_fraction: float # e.g. 0.81 - 0.86 for fresh
    pectin_content_dry_basis: float 
    GalA_fraction_of_pectin: float
    initial_DE: float
    initial_Mw: float
    
    def __post_init__(self):
        if not 0.0 <= self.moisture_fraction < 1.0:
            raise ValueError("moisture_fraction must be in [0, 1).")
        if self.wet_mass <= 0:
            raise ValueError("wet_mass must be positive.")
        if not 0.0 <= self.pectin_content_dry_basis <= 1.0:
            raise ValueError("pectin_content_dry_basis must be in [0, 1].")
        if not 0.0 <= self.GalA_fraction_of_pectin <= 1.0:
            raise ValueError("GalA_fraction_of_pectin must be in [0, 1].")
        if not 0.0 <= self.initial_DE <= 1.0:
            raise ValueError("initial_DE must be in [0, 1].")
        if self.initial_Mw <= 0:
            raise ValueError("initial_Mw must be positive.")
    
    @property
    def dry_matter_mass(self) -> float:
        return self.wet_mass * (1.0 - self.moisture_fraction)
        
    @property
    def absolute_pectin_mass(self) -> float:
        return self.dry_matter_mass * self.pectin_content_dry_basis

@dataclass
class ConditionedFeedstock:
    """Rind that has been physically dried and milled, ready for extraction."""
    dry_matter_mass: float
    moisture_fraction: float
    pectin_mass: float
    GalA_fraction: float
    DE: float
    Mw_matrix: float
    d50_um: float
    
    def __post_init__(self):
        if not 0.0 <= self.moisture_fraction < 1.0:
            raise ValueError("moisture_fraction must be in [0, 1).")
        if self.dry_matter_mass <= 0:
            raise ValueError("dry_matter_mass must be positive.")
        if self.pectin_mass <= 0:
            raise ValueError("pectin_mass must be positive.")
        if not 0.0 <= self.GalA_fraction <= 1.0:
            raise ValueError("GalA_fraction must be in [0, 1].")
        if not 0.0 <= self.DE <= 1.0:
            raise ValueError("DE must be in [0, 1].")
        if self.Mw_matrix <= 0:
            raise ValueError("Mw_matrix must be positive.")
        if self.d50_um <= 0:
            raise ValueError("d50_um must be positive.")
    
    @property
    def total_mass(self) -> float:
        """Total physical mass entering the reactor (dry matter + residual moisture)."""
        return self.dry_matter_mass / (1.0 - self.moisture_fraction)
