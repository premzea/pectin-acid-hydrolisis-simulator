# Physical Experimental Protocol & Reactor Specification (V1.0)

**Objective**: This document translates the computational identifiability and optimal experimental design (OED) findings of the V1.3 digital twin into a concrete physical measurement plan. The reactor is specified here not merely as an extraction device, but as an **instrument built specifically to identify and validate the model**.

---

## 1. Feedstock Characterization (Batch Identity)
The computational stress test proved that variations in starting protopectin mass, esterification, and molecular weight heavily influence the signal-to-noise ratio of the kinetic inference. Feedstock properties are not optional metadata; they are **mandatory model inputs**.

For every experimental batch (e.g., `B001`, `B002`), the following must be characterized before any extraction runs. Note the critical distinction between measurable *reference extracts* and unmeasurable *latent matrix* properties.

| Property | Symbol | Importance | Analytical Target |
|:---|:---:|:---|:---|
| **Available Pectin** | $P_{matrix,0}$ | Critical | Must use a pectin-specific proxy (e.g., GalA content of AIR). Unadjusted Alcohol Insoluble Residue ($P_{AIR}$) overestimates pectin due to neutral sugars. |
| **Reference MW** | $M_{w,reference}$ | Critical | Measures MW of a standard mild extract to anchor the latent model property $M_{w,matrix}$. (Direct intact SEC is impossible). |
| **Reference DE** | $DE_{reference}$ | Critical | Measures DE of a standard mild extract to anchor latent $DE_{matrix}$. |
| **GalA Fraction** | $X_{GalA,product}$ | High | Carbazole/mHDP colorimetry on standard extract. (Must be validated against neutral sugar interference). |
| **Moisture** | $X_{w,0}$ | Baseline | Moisture analyzer (e.g., 105 °C to constant mass) |
| **Particle Size** | $d_{50}$ | Empirical | Laser diffraction or standard sieves |

---

## 2. Reactor Hardware Requirements
The reactor must be optimized for **control + sampling + traceability**. 

### A. Control & Logging
The kinetic integration $\tau_k = \int_0^t k(T(s),pH(s))\,ds$ requires exact thermal history, not just setpoints.
* **Temperature**: Continuous logging of $T(t)$ inside the reaction fluid to capture ramp-up/cool-down transients.
* **pH**: Continuous logging of $pH(t)$, or precise tracking of acid dosing if buffered.
* **Agitation**: Sufficient to ensure uniform suspension (preventing localized thermal/pH gradients).

### B. Sampling Subsystem
* **Non-destructive withdrawal**: Sample withdrawal affects the $S:L$ ratio. Either keep cumulative sampled volume $<5\%$ of total volume, or explicitly record `volume_withdrawn_mL` for every sample to update the mass/volume conservation equations.
* **Rapid Quenching**: Extracted samples must be immediately quenched (e.g., rapid cooling to < 20 °C or neutralization) to lock the exact reaction time $t$.
* **Traceability**: Precise timestamping of the exact quench time, not the nominal intended time.

---

## 3. The Time-Resolved Calibration Campaign
The original OED assumed single-endpoint observations. The physical design embraces **time-resolved** observation (measuring at $t=15, 45, 90, 120$ min). Re-running the D-optimal design solver over the time-resolved trajectory yielded the following verbatim 10-run protocol ($\kappa = 27.0$).

### Calibration Set (Distributed over Batches A & B)
To estimate kinetics robustly across feedstock variations, distribute these 10 runs across at least two feedstock batches.

| Run | T (°C) | pH | d₅₀ (µm) | Sample Times (min) |
|:---:|:---:|:---:|:---:|:---|
| 1 | 95 | 1.5 | 600 | 15, 45, 90, 120 |
| 2 | 50 | 1.5 | 150 | 15, 45, 90, 120 |
| 3 | 95 | 2.5 | 150 | 15, 45, 90, 120 |
| 4 | 50 | 1.5 | 600 | 15, 45, 90, 120 |
| 5 | 95 | 2.0 | 600 | 15, 45, 90, 120 |
| 6 | 50 | 2.0 | 150 | 15, 45, 90, 120 |
| 7 | 95 | 2.5 | 600 | 15, 45, 90, 120 |
| 8 | 50 | 1.5 | 300 | 15, 45, 90, 120 |
| 9 | 95 | 3.0 | 150 | 15, 45, 90, 120 |
| 10 | 95 | 2.0 | 300 | 15, 45, 90, 120 |

### Validation Set (Batch C - Independent Feedstock)
To rigorously test if the digital twin generalizes (i.e. distinguishing kinetic variation from feedstock variation), the validation runs should be performed on a completely independent feedstock batch.

| Run | T (°C) | pH | d₅₀ (µm) | Sample Times | Validation Objective |
|:---:|:---:|:---:|:---:|:---:|:---|
| 11 | 75 | 2.2 | 300 | 15, 45, 90, 120 | **Interior Interpolation** (Center-point test) |
| 12 | 85 | 1.8 | 300 | 15, 45, 90, 120 | **Near-Optimum** (Trajectory toward high yield) |
| 13 | 90 | 1.5 | 150 | 15, 45, 90, 120 | **Severity Edge** (Test degradation cascade) |

---

## 4. Analytical Assays
For every timestamped sample aliquot (15, 45, 90, 120 min), measure the following:

| Observable | Purpose | Assay Target Noise |
|:---|:---|:---|
| **Aliquot Yield Concentration** | Tracks extraction progress. Distinct from final bulk gravimetric yield. | $\sigma \approx 1\%$ absolute |
| **DE (Degree of Esterification)** | Directly calibrates $k_{de}$. Very strong signal. | $\sigma \approx 2\%$ absolute |
| **MW (Molecular Weight)** | Breaks the $k_{hyd} \leftrightarrow k_{deg}$ ambiguity. | $\sigma \approx 15,000$ Da |

### Analytical Noise Targets
The experimental protocols for the assays should be engineered to meet or exceed these historical variances:
* **Yield**: $\sigma \approx 1\%$ absolute
* **DE**: $\sigma \approx 2\%$ absolute
* **MW**: $\sigma \approx 15,000$ Da
