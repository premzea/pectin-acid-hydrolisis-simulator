# Proxy Feasibility Matrix

This document evaluates the literature-supported empirical measurements proposed to replace expensive physicochemical assays (SEC-MALLS, Titration, Carbazole) for routine time-resolved reactor aliquots. 

The goal is to select a compact, high-value measurement stack where the Bayesian model propagates proxy uncertainty ($\sigma_{proxy}$) into the kinetic posterior.

## 1. Evaluation Matrix

| Candidate Proxy | Target Property | Sample Prep Required | Equipment Cost | Per-Sample Time | Expected $\sigma_{proxy}$ | Confounding Variables |
|:---|:---|:---|:---|:---|:---|:---|
| **Simple / Capillary Viscosity** | Molecular Weight ($M_w$) | **Standardized Precipitate**. Must be isolated from liquor, dried, and re-dissolved at fixed concentration ($C_p$), pH, and ionic strength. | Low (Capillary viscometer / basic rheometer) | 15–30 min | Moderate (relies on Mark-Houwink constants) | Concentration (must be exact), DE, degree of branching, trace ions |
| **FTIR / DRIFTS** | Degree of Esterification ($DE$) | **Standardized Precipitate (Dried)**. Water absorption overwhelms IR; must dry the AIR pellet. | Medium (FTIR Spectrometer) | < 5 min | 1–3% absolute | Residual moisture, baseline shifts, physical particle size (for DRIFTS) |
| **FTIR / DRIFTS** | Galacturonic Acid ($X_{GalA}$) | Same as above (analyzed simultaneously from same spectrum) | Medium (FTIR) | < 5 min (simultaneous) | Low-Moderate ($R^2 \approx 0.98$ reported) | Overlapping vibrational bands from co-extracted neutral sugars |
| **NIR Spectroscopy** | Pectin Yield / Content | **Direct Liquor** or precipitate | Medium-High (NIR) | < 2 min | High (screening quality, $R^2 \approx 0.63$) | Massive matrix effects (water, soluble sugars, pH, temperature) |
| **Standardized Gel/Collapse Test** | Functional Quality (combines $Y$, $DE$, $M_w$) | **Standardized Formulation**. Must isolate pectin, add fixed sucrose/acid/Ca$^{2+}$, and cool under strict profile. | Low (Texture analyzer or empirical geometry) | 12–24 hrs (curing time) | High (sensitive to curing) | Exact thermal history of the gel, trace multivalent cations, pH micro-variations |

## 2. Selected Primary Measurement Stack: `FTIR + Viscosity`

Based on the value criterion ($Value = \frac{\text{Information Gained}}{\text{Cost}}$), the project adopts the following two-tier architecture:

### Routine Aliquot Testing (High Frequency)
1. **Precipitation Step**: Every aliquot undergoes a rapid Alcohol Insoluble Residue (AIR) precipitation and drying. This eliminates the massive confounding effects of the extraction liquor (water, citric acid, raw sugars).
2. **FTIR Scan**: The dried pellet is scanned. A calibrated chemometric (PLS/PCR) model predicts:
   * $\widehat{DE} \pm \sigma_{DE}$
   * $\widehat{X_{GalA}} \pm \sigma_{GalA}$
3. **Viscosity Test**: The pellet is dissolved in a standard buffer at an exact concentration. Intrinsic/kinematic viscosity predicts:
   * $\widehat{M_w} \pm \sigma_{Mw}$

### Anchor Testing (Low Frequency / Calibration)
Only a small, mathematically selected subset of samples (the proxy calibration set, plus occasional quality-control anchors from the reactor) are sent for:
* **Titration** (True $DE$)
* **HPSEC-MALLS** (True $M_w$)
* **mHDP Colorimetry** (True GalA)

## 3. Implementation Implications
By abandoning the attempt to test the *direct extraction liquor*, we accept a slight increase in sample prep time (the rapid precipitation step). However, this completely standardizes the chemical matrix, unlocking the ability to use FTIR and Capillary Viscosity as highly accurate, theoretically grounded proxies. This reduces the marginal cost of a time-resolved measurement from $\sim$\$100+ (SEC/Titration) to effectively the cost of ethanol and technician time, while the Bayesian digital twin effortlessly handles the residual calibration uncertainty.
