# Phase 1 Proxy Calibration & Measurement-Model Validation

**Primary Objective**: Calibrate the end-to-end measurement model mapping cheap observables ($z$) to expensive physicochemical reference assays ($y$) on a 30-sample diverse dataset. 
**Secondary Objective**: Quantify whether the precipitation sample preparation step introduces systematic MW/DE-dependent fractionation ($\eta_{precipitation} = f(M_w)$) via a specialized soluble-vs-pellet sub-experiment.

## 1. Experimental Design (Sample Generation)
To ensure the proxy models generalize, the calibration samples must span the entire thermodynamic state space. We will execute 5 dedicated reactor runs, taking 6 time-resolved aliquots per run (Total $N = 30$).

| Run | T (°C) | pH | d₅₀ (µm) | Targeted Domain | Expected Pectin State |
|:---|:---:|:---:|:---:|:---|:---|
| C1 | 50 | 3.0 | 600 | Absolute Minimum Severity | High $M_w$, High $DE$, Low Yield |
| C2 | 95 | 1.5 | 150 | Absolute Maximum Severity (**Stress/extreme-domain**) | Low $M_w$ (degraded), Low $DE$. *May produce pathologically different material.* |
| C3 | 75 | 2.2 | 300 | Center Point / Interior Trajectory | Moderate $M_w$, Moderate $DE$ |
| C4 | 95 | 3.0 | 300 | High T / Low Acid | Moderate $M_w$, High $DE$ |
| C5 | 50 | 1.5 | 150 | Low T / High Acid | High $M_w$, Low $DE$ |

* **Sampling Schedule**: For every run, withdraw aliquots at $t = 10, 25, 45, 70, 95, 120$ minutes.

## 2. Standardized Aliquot Preparation
Every one of the 30 aliquots must undergo the exact same precipitation protocol.

1. **Withdraw & Quench**: Withdraw precisely 20.0 mL of liquor. Immediately dispense into a pre-chilled tube in a 0 °C ice-water bath.
2. **Precipitation**: Add 40.0 mL of cold 96% ethanol (2 volumes). Stir thoroughly. Rest at 4 °C for 2 hours.
3. **Wash**: Centrifuge to pellet. Discard supernatant. Wash the pellet twice with 70% ethanol to remove unbound sugars and acid.
4. **Dry**: Dry the pellet in a vacuum oven at 60 °C to constant mass. 
5. **Concentration Proxy ($C_{ppt}$)**: Record the dry mass. $C_{ppt} = \frac{m_{dry\_pellet}}{m_{liquor}}$. Note: This is *not* pure pectin yield; it feeds the proxy model: $Y_{GalA} = f(C_{ppt}, FTIR)$.

*(Secondary Goal: On 3 samples representing high, medium, and low expected MW, measure $M_w$ of both the soluble supernatant and the precipitated pellet to explicitly determine the precipitation recovery fractionation $\eta_{precipitation}$).*

## 3. Analytical Branching (Paired Assays)
The single dried pellet from each of the 30 samples is split to undergo *both* the cheap proxies and the expensive reference assays. 

### Branch A: Cheap Proxies ($z$)
* **FTIR/DRIFTS**: Scan the dry pellet directly. Record the full spectrum (4000 - 400 cm⁻¹).
* **Simple Viscosity ($t_{flow}$)**: Dissolve a precise mass of the pellet in 0.1 M NaNO₃ buffer. *Crucially, record the exact pellet concentration used ($C_{pellet}$)*. Measure flow time in a standard capillary viscometer at 25.0 °C. The proxy model will test $M_w = f(t_{flow}, C_{pellet})$.

### Branch B: Reference Assays ($y$)
* **HPSEC-MALLS**: Measure true $M_w$ on the buffered solution.
* **Titration**: Measure true $DE$ using the standard saponification protocol.
* **mHDP Colorimetry**: Measure reference $X_{GalA}$ fraction.

## 4. Statistical Acceptance Criteria
For each target property ($DE$, $M_w$, $X_{GalA}$), train predictive models on strictly paired pellet data.

**Validation Method**: **Leave-One-Run-Out (LORO) Cross-Validation**. The model is trained on 4 trajectories and tested on the 5th entirely unseen trajectory.

**Acceptance Metrics for Routine Reactor Use**:
Evaluate the following on the LORO held-out runs:
1. **RMSEP** (Root Mean Square Error of Prediction): Must be $< 5\%$ for DE/GalA, $< 50$ kDa for MW.
2. **Stratified RMSEP**: The proxy must not fail catastrophically at extremes. Report $RMSEP$ for Low, Medium, and High regions of the variable space. (e.g., $RMSEP(M_w < 150 \text{ kDa})$, $RMSEP(150 < M_w < 400 \text{ kDa})$, $RMSEP(M_w > 400 \text{ kDa})$).
3. **MAE & Bias**: Ensure residuals are centered at zero.
4. **R²**: Explains variance across the severity extremes.
5. **Uncertainty Coverage ($P(y_{true} \in CI_{95\%,proxy})$)**: Does the proxy's stated 95% confidence interval actually contain the true SEC/Titration value 95% of the time on unseen runs?

## 5. Bayesian Hierarchy Integration
Once validated, the laboratory physical procedure mathematically maps to three distinct models in the digital twin:

### 1. Process Model
$$ x, \theta \rightarrow \mathbf{y}_{true} $$
### 2. Sample-Preparation Model
$$ \mathbf{y}_{true} \rightarrow \mathbf{y}_{prepared} $$
*(Where $\eta_{precipitation}$ is a parameter/function inside this preparation step)*
### 3. Measurement Model
$$ \mathbf{y}_{prepared} \rightarrow \mathbf{z}_{observed} $$

**Final DAG**:
$$ \text{Kinetic ODE} \rightarrow \mathbf{y}_{true} \rightarrow \mathbf{y}_{prepared} \rightarrow \mathbf{z}_{observed} $$

Where $\mathbf{y} = (Y, DE, M_w, X_{GalA})$ and $\mathbf{z} = (\text{FTIR}, t_{flow}, C_{ppt}, C_{pellet})$.
This formally allows the Bayesian inference to marginalize over the unobserved true properties:
$$ p(\theta \mid z) = \int p(\theta \mid y)\,p(y \mid z)\,dy $$
