"""
Multi-wavelength colorimetric soft-sensor module for at-line pectin characterization.
Supports the IO Rodeo 8-channel spectrophotometer (410, 450, 480, 515, 555, 590, 630, 680 nm).

Key features:
1. Matrix correction via unreacted sample blank:
   A_net(lambda) = A_developed(lambda) - A_sample_blank(lambda) - A_turbidity(680) * (680/lambda)^alpha_Rayleigh
2. Calibrated soft-sensor inversions:
   - GalA concentration (carbazole assay, primary peak ~525 nm / 515 & 555 channels)
   - Pectin-equivalent concentration (copper-chelate assay, ~630-680 nm)
3. Quality checks:
   - Dynamic range clipping detection (Beer-Lambert linear limits: 0.05 to 1.50 AU)
   - Dilution advisor for high-absorbance out-of-range samples
   - Consistency check between GalA and total pectin
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import numpy as np

# Standard 8 channels on the IO Rodeo multi-channel colorimeter (nm)
COLORIMETER_CHANNELS = [410, 450, 480, 515, 555, 590, 630, 680]

@dataclass
class ChannelCalibration:
    """Univariate or multivariate regression coefficients for a specific assay."""
    assay_name: str
    slope: float  # d(Concentration) / d(Absorbance) [g/L per AU]
    intercept: float = 0.0
    primary_wavelength_nm: int = 525
    r_squared: float = 0.999
    valid_absorbance_min: float = 0.05
    valid_absorbance_max: float = 1.50

@dataclass
class ColorimeterMeasurement:
    """Raw 8-channel absorbance measurement from an assay cuvette."""
    channel_absorbance: Dict[int, float]
    dilution_factor: float = 1.0  # Dilution factor applied before cuvette loading (e.g. 5.0 for 1:5 dilution)
    
    def __post_init__(self):
        if self.dilution_factor <= 0:
            raise ValueError("dilution_factor must be positive.")

@dataclass
class SoftSensorResult:
    """Inferred chemical concentrations and diagnostic flags from the soft sensor."""
    C_GalA_g_per_l: float
    C_pectin_equiv_g_per_l: float
    GalA_purity_index: float  # C_GalA / C_pectin_equiv
    
    # Net corrected absorbances at key wavelengths
    A_net_515: float
    A_net_555: float
    A_net_630: float
    A_net_680: float
    
    # Turbidity diagnostic
    turbidity_680: float
    
    # Quality and advisory flags
    is_within_linear_range: bool
    dilution_advisory: Optional[str] = None
    suggested_dilution_factor: Optional[float] = None
    warnings: List[str] = field(default_factory=list)

class ColorimetricSoftSensor:
    """
    At-line soft sensor implementing dual-assay matrix-corrected spectrophotometry.
    """
    def __init__(
        self,
        gala_calibration: Optional[ChannelCalibration] = None,
        pectin_calibration: Optional[ChannelCalibration] = None,
        rayleigh_exponent: float = 4.0
    ):
        # Default carbazole calibration (GalA in g/L per AU at ~525 nm, combining 515 & 555)
        self.gala_cal = gala_calibration or ChannelCalibration(
            assay_name="carbazole_GalA",
            slope=0.450,  # 0.45 g/L GalA per AU
            intercept=0.005,
            primary_wavelength_nm=525,
            r_squared=0.998,
            valid_absorbance_min=0.05,
            valid_absorbance_max=1.50
        )
        
        # Default copper-chelate calibration (Pectin-equivalent in g/L per AU at ~630 nm)
        self.pectin_cal = pectin_calibration or ChannelCalibration(
            assay_name="copper_chelate_pectin",
            slope=0.850,  # 0.85 g/L Pectin per AU
            intercept=0.010,
            primary_wavelength_nm=630,
            r_squared=0.997,
            valid_absorbance_min=0.05,
            valid_absorbance_max=1.50
        )
        
        self.rayleigh_exponent = rayleigh_exponent

    def correct_net_absorbance(
        self,
        developed: ColorimeterMeasurement,
        blank: Optional[ColorimeterMeasurement] = None
    ) -> Dict[int, float]:
        """
        Calculates matrix-corrected net absorbance across all channels:
        A_net(lambda) = A_dev(lambda) - A_blank(lambda) - A_turbidity(680) * (680/lambda)^alpha
        """
        net_abs = {}
        turbidity_ref = 0.0
        
        # Turbidity estimation at 680 nm (where chromophores have minimal chemical absorbance)
        raw_dev_680 = developed.channel_absorbance.get(680, 0.0)
        raw_blank_680 = blank.channel_absorbance.get(680, 0.0) if blank else 0.0
        # Turbidity in blank or baseline
        turbidity_ref = max(0.0, raw_blank_680)
        
        for w in COLORIMETER_CHANNELS:
            a_dev = developed.channel_absorbance.get(w, 0.0)
            a_blank = blank.channel_absorbance.get(w, 0.0) if blank else 0.0
            
            # Rayleigh scattering baseline subtraction
            scatter_correction = turbidity_ref * ((680.0 / w) ** self.rayleigh_exponent) * 0.1
            
            net = a_dev - a_blank - scatter_correction
            net_abs[w] = max(0.0, net)
            
        return net_abs

    def evaluate(
        self,
        carbazole_developed: ColorimeterMeasurement,
        copper_developed: ColorimeterMeasurement,
        sample_blank: Optional[ColorimeterMeasurement] = None
    ) -> SoftSensorResult:
        """
        Evaluate full soft sensor from paired carbazole (GalA) and copper-chelate (pectin) assays
        with an unreacted sample blank tube.
        """
        warnings = []
        
        # 1. Net absorbance corrections
        carbazole_net = self.correct_net_absorbance(carbazole_developed, sample_blank)
        copper_net = self.correct_net_absorbance(copper_developed, sample_blank)
        
        # 2. Extract key channel absorbances
        a_515 = carbazole_net.get(515, 0.0)
        a_555 = carbazole_net.get(555, 0.0)
        a_630 = copper_net.get(630, 0.0)
        a_680 = copper_net.get(680, 0.0)
        
        # Representative GalA absorbance (interpolation/average between 515 and 555 for 525 peak)
        a_gala_rep = 0.5 * (a_515 + a_555)
        # Representative Pectin absorbance
        a_pectin_rep = a_630
        
        # 3. Check Beer-Lambert linearity bounds on developed cuvettes
        is_linear = True
        raw_carb_peak = max(carbazole_developed.channel_absorbance.get(515, 0.0),
                            carbazole_developed.channel_absorbance.get(555, 0.0))
        raw_cu_peak = copper_developed.channel_absorbance.get(630, 0.0)
        
        dilution_adv = None
        suggested_dilution = None
        
        if raw_carb_peak > self.gala_cal.valid_absorbance_max or raw_cu_peak > self.pectin_cal.valid_absorbance_max:
            is_linear = False
            max_abs = max(raw_carb_peak, raw_cu_peak)
            suggested_factor = np.ceil(max_abs / 0.8) * carbazole_developed.dilution_factor
            dilution_adv = (
                f"Absorbance ({max_abs:.2f} AU) exceeds linear Beer-Lambert threshold (1.50 AU). "
                f"Prepare a 1:{int(suggested_factor)} dilution and re-read."
            )
            suggested_dilution = suggested_factor
            warnings.append("Absorbance saturation / non-linear Beer-Lambert regime.")
        elif raw_carb_peak < self.gala_cal.valid_absorbance_min:
            warnings.append("Low absorbance (<0.05 AU) approaching limit of quantitation (LOQ).")
            
        # 4. Invert to concentrations in original sample liquor [g/L]
        # In-cuvette concentration * dilution_factor
        c_gala_cuvette = max(0.0, self.gala_cal.slope * a_gala_rep + self.gala_cal.intercept)
        c_gala_liquor = c_gala_cuvette * carbazole_developed.dilution_factor
        
        c_pectin_cuvette = max(0.0, self.pectin_cal.slope * a_pectin_rep + self.pectin_cal.intercept)
        c_pectin_liquor = c_pectin_cuvette * copper_developed.dilution_factor
        
        # 5. Composition / Purity index
        if c_pectin_liquor > 0:
            purity = c_gala_liquor / c_pectin_liquor
        else:
            purity = 0.0
            
        if purity > 1.05:
            warnings.append(f"GalA concentration exceeds total pectin-equivalent (ratio={purity:.2f}). Check calibration blank.")
            
        turbidity_680 = sample_blank.channel_absorbance.get(680, 0.0) if sample_blank else 0.0
        if turbidity_680 > 0.30:
            warnings.append(f"High sample turbidity at 680 nm ({turbidity_680:.2f} AU). Pre-filtration recommended.")
            
        return SoftSensorResult(
            C_GalA_g_per_l=c_gala_liquor,
            C_pectin_equiv_g_per_l=c_pectin_liquor,
            GalA_purity_index=purity,
            A_net_515=a_515,
            A_net_555=a_555,
            A_net_630=a_630,
            A_net_680=a_680,
            turbidity_680=turbidity_680,
            is_within_linear_range=is_linear,
            dilution_advisory=dilution_adv,
            suggested_dilution_factor=suggested_dilution,
            warnings=warnings
        )
