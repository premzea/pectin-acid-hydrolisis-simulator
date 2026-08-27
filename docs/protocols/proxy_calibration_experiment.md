# Proxy Calibration Experiment (Phase 1 Physical Protocol)

**Objective**: Generate a highly diverse, 30-sample paired dataset to calibrate chemometric and rheological proxies ($z$) against expensive physicochemical reference assays ($y$). This establishes the statistical measurement models $p(\mathbf{y} \mid \mathbf{z}, D_{proxy})$ required for the digital twin's time-resolved reactor campaign.

## 1. Experimental Design (Sample Generation)
To ensure the proxy models generalize, the calibration samples must span the entire thermodynamic state space the digital twin expects to encounter. We will execute 5 dedicated reactor runs, taking 6 time-resolved aliquots per run (Total $N = 30$).

| Run | T (°C) | pH | d₅₀ (µm) | Targeted Domain | Expected Pectin State |
|:---|:---:|:---:|:---:|:---|:---|
| C1 | 50 | 3.0 | 600 | Absolute Minimum Severity | High $M_w$, High $DE$, Low Yield |
| C2 | 95 | 1.5 | 150 | Absolute Maximum Severity | Low $M_w$ (degraded), Low $DE$ |
| C3 | 75 | 2.2 | 300 | Center Point | Moderate $M_w$, Moderate $DE$ |
| C4 | 95 | 3.0 | 300 | High T / Low Acid | Moderate $M_w$, High $DE$ |
| C5 | 50 | 1.5 | 150 | Low T / High Acid | High $M_w$, Low $DE$ |

* **Sampling Schedule**: For every run, withdraw aliquots at $t = 10, 25, 45, 70, 95, 120$ minutes.

## 2. Standardized Aliquot Preparation (Crucial)
Every one of the 30 aliquots must undergo the exact same precipitation protocol to lock in the recovery bias ($\eta_{precipitation}$) and eliminate the liquor matrix (water, citric acid, raw sugars).

1. **Withdraw & Quench**: Withdraw precisely 20.0 mL of liquor. Immediately dispense into a pre-chilled tube in a 0 °C ice-water bath.
2. **Precipitation**: Add 40.0 mL of cold 96% ethanol (2 volumes). Stir thoroughly. Rest at 4 °C for 2 hours.
3. **Wash**: Centrifuge to pellet. Discard supernatant. Wash the pellet twice with 70% ethanol to remove unbound sugars and acid.
4. **Dry**: Dry the pellet in a vacuum oven at 60 °C to constant mass. 
5. **Yield Proxy**: Record the dry mass. $Y_{aliquot} = \frac{\text{Dry Pellet Mass}}{\text{Initial 20 mL Liquor Mass}}$.

## 3. Analytical Branching (Paired Assays)
The dried pellet from each of the 30 samples is split to undergo *both* the cheap proxies and the expensive reference assays.

### Branch A: Cheap Proxies ($z$)
* **FTIR/DRIFTS**: Scan the dry pellet directly. Record the full spectrum (4000 - 400 cm⁻¹).
* **Simple Viscosity ($t_{flow}$)**: Dissolve a precise mass of the pellet to exactly $0.5\% \text{ w/v}$ in 0.1 M NaNO₃ buffer. Measure flow time in a standard capillary viscometer at 25.0 °C.

### Branch B: Reference Assays ($y$)
* **HPSEC-MALLS**: Measure true $M_w$ on the $0.5\%$ buffered solution.
* **Titration**: Measure true $DE$ using the standard saponification protocol.
* **mHDP Colorimetry**: Measure true $X_{GalA}$ fraction.

## 4. Statistical Acceptance Criteria
For each target property ($DE$, $M_w$, $X_{GalA}$), we will train a predictive model (e.g., PLS regression for FTIR spectra, nonlinear regression for viscosity).

The proxy is evaluated based on its **Root Mean Square Error of Prediction (RMSEP)**, calculated using strictly held-out data (e.g., 5-fold cross-validation, keeping time-series points from the same run grouped to prevent data leakage).

**Acceptance Thresholds for Routine Reactor Use**:
* **DE (from FTIR)**: Accept if RMSEP $< 5\%$ absolute.
* **GalA (from FTIR)**: Accept if RMSEP $< 5\%$ absolute.
* **MW (from Viscosity)**: Accept if RMSEP $< 50,000$ Da.

*If a proxy meets these criteria, it is approved to replace the expensive reference assay for the 14-run time-resolved reactor campaign. Its RMSEP becomes the $\sigma_{proxy}$ variance passed to the Bayesian likelihood function. If a proxy fails to meet these criteria, the corresponding expensive assay must be retained for the main campaign.*
