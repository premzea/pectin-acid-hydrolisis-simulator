# Phase 1 Proxy Calibration & Measurement-Model Validation

**Objective**: Generate a highly diverse, 30-sample paired dataset to calibrate chemometric and rheological proxies ($z$) against expensive physicochemical reference assays ($y$). This establishes the statistical measurement models $p(\mathbf{y} \mid \mathbf{z}, D_{proxy})$ required for the digital twin's time-resolved reactor campaign. 

Crucially, this phase does not just seek correlations; it formally validates the Bayesian measurement hierarchy, including the biases introduced by sample preparation itself.

## 1. Experimental Design (Sample Generation)
To ensure the proxy models generalize, the calibration samples must span the entire thermodynamic state space the digital twin expects to encounter. We will execute 5 dedicated reactor runs, taking 6 time-resolved aliquots per run (Total $N = 30$).

| Run | T (°C) | pH | d₅₀ (µm) | Targeted Domain | Expected Pectin State |
|:---|:---:|:---:|:---:|:---|:---|
| C1 | 50 | 3.0 | 600 | Absolute Minimum Severity | High $M_w$, High $DE$, Low Yield |
| C2 | 95 | 1.5 | 150 | Absolute Maximum Severity | Low $M_w$ (degraded), Low $DE$ |
| C3 | 75 | 2.2 | 300 | Center Point / Interior Trajectory | Moderate $M_w$, Moderate $DE$ |
| C4 | 95 | 3.0 | 300 | High T / Low Acid | Moderate $M_w$, High $DE$ |
| C5 | 50 | 1.5 | 150 | Low T / High Acid | High $M_w$, Low $DE$ |

* **Sampling Schedule**: For every run, withdraw aliquots at $t = 10, 25, 45, 70, 95, 120$ minutes.

## 2. Standardized Aliquot Preparation (The Measurement Model)
The precipitation step is not a neutral preparation; it is a physical separation that can fractionate pectin. We define this as the precipitation recovery bias ($\eta_{precipitation}$). 

Every one of the 30 aliquots must undergo the exact same precipitation protocol so the Bayesian model learns this bias natively.

1. **Withdraw & Quench**: Withdraw precisely 20.0 mL of liquor. Immediately dispense into a pre-chilled tube in a 0 °C ice-water bath.
2. **Precipitation**: Add 40.0 mL of cold 96% ethanol (2 volumes). Stir thoroughly. Rest at 4 °C for 2 hours.
3. **Wash**: Centrifuge to pellet. Discard supernatant. Wash the pellet twice with 70% ethanol to remove unbound sugars and acid.
4. **Dry**: Dry the pellet in a vacuum oven at 60 °C to constant mass. 
5. **Concentration Proxy ($C_{ppt}$)**: Record the dry mass. $C_{ppt} = \frac{m_{dry\_pellet}}{m_{liquor}}$. Note: This is *not* pure pectin yield; it is a concentration metric that feeds the proxy model: $Y_{GalA} = f(C_{ppt}, FTIR)$.

## 3. Analytical Branching (Paired Assays)
The single dried pellet from each of the 30 samples is split to undergo *both* the cheap proxies and the expensive reference assays. This ensures extraction heterogeneity does not confound analytical variance.

### Branch A: Cheap Proxies ($z$)
* **FTIR/DRIFTS**: Scan the dry pellet directly. Record the full spectrum (4000 - 400 cm⁻¹).
* **Simple Viscosity ($t_{flow}$)**: Dissolve a precise mass of the pellet in 0.1 M NaNO₃ buffer. *Crucially, record the exact pellet concentration used ($C_{pellet}$)*. Measure flow time in a standard capillary viscometer at 25.0 °C. The proxy model will test $M_w = f(t_{flow}, C_{pellet})$.

### Branch B: Reference Assays ($y$)
* **HPSEC-MALLS**: Measure true $M_w$ on the buffered solution.
* **Titration**: Measure true $DE$ using the standard saponification protocol.
* **mHDP Colorimetry**: Measure reference $X_{GalA}$ fraction.

*(Note: Explicitly test precipitation fractionation by comparing $M_w$ of the soluble liquor vs the pellet on a subset of extreme samples to quantify $\eta_{precipitation} = f(M_w)$).*

## 4. Statistical Acceptance Criteria
For each target property ($DE$, $M_w$, $X_{GalA}$), train predictive chemometric/empirical models. 

**Validation Method**: Because the 6 time points within a run are highly correlated, random K-fold cross-validation will overfit. We must use **Leave-One-Run-Out (LORO) Cross-Validation**. The model is trained on 4 runs and tested on the 5th entirely unseen trajectory.

**Acceptance Metrics for Routine Reactor Use**:
Evaluate the following on the LORO held-out runs:
1. **RMSEP** (Root Mean Square Error of Prediction): Must be $< 5\%$ for DE/GalA, $< 50$ kDa for MW.
2. **MAE & Bias**: Ensure the residuals are centered at zero. (A low RMSEP with a $+5\%$ systemic bias is unacceptable).
3. **R²**: Explains variance across the severity extremes.
4. **Uncertainty Coverage ($P(y_{true} \in CI_{95\%,proxy})$)**: The most critical metric for the Bayesian twin. Does the proxy's stated 95% confidence interval actually contain the true SEC/Titration value 95% of the time on unseen runs?

## 5. Bayesian Hierarchy Integration
Once validated, the laboratory physical procedure mathematically maps to this Directed Acyclic Graph (DAG) in the digital twin:

$$ \text{Kinetic ODE} \rightarrow (Y, DE, M_w, X_{GalA})_{true} $$
$$ \downarrow \text{Precipitation Bias } (\eta_{precipitation}) $$
$$ (C_{ppt}, \text{Pellet Properties})_{prepared} $$
$$ \downarrow \text{Proxy Model } (\phi) $$
$$ (\text{FTIR}_{spectrum}, t_{flow}, C_{ppt})_{observed} $$

This ensures that the uncertainty from the cheap observables flows rigorously upward to the kinetic parameter estimation ($k_{hyd}, k_{deg}$).
