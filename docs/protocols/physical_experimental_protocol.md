# Physical Experimental Protocol & Reactor Specification (V1.0)

**Objective**: This document translates the computational identifiability and optimal experimental design (OED) findings of the V1.3 digital twin into a concrete physical measurement plan. The reactor is specified here not merely as an extraction device, but as an **instrument built specifically to identify and validate the model**.

---

## 1. Feedstock Characterization (Batch Identity)
The computational stress test proved that variations in starting protopectin mass, esterification, and molecular weight heavily influence the signal-to-noise ratio of the kinetic inference. Feedstock properties are not optional metadata; they are **mandatory model inputs**.

For every experimental batch (e.g., `B001`, `B002`), the following must be characterized before any extraction runs:

| Property | Symbol | Importance | Analytical Target |
|:---|:---:|:---|:---|
| **Available Pectin** | $P_{matrix,0}$ | Critical (scales entire yield signal) | Gravimetric/Alcohol Insoluble Residue |
| **Matrix MW** | $M_{w,matrix}$ | Critical (dictates hydrolysis precision) | HPSEC-MALLS or Viscometry |
| **Matrix DE** | $DE_{matrix}$ | Critical (dictates de-esterification precision)| Titration or FTIR |
| **GalA Fraction** | $X_{GalA,matrix}$ | High (purity baseline) | Carbazole assay / Colorimetric |
| **Moisture** | $X_{w,0}$ | Baseline normalization | Moisture analyzer (e.g., 105 °C to constant mass) |
| **Particle Size** | $d_{50}$ | Empirical mass transfer scaling | Laser diffraction or standard sieves |

---

## 2. Reactor Hardware Requirements
The reactor must be optimized for **control + sampling + traceability**. 

### A. Control & Logging
The kinetic integration $\tau_k = \int_0^t k(T(s),pH(s))\,ds$ requires exact thermal history, not just setpoints.
* **Temperature**: Continuous logging of $T(t)$ inside the reaction fluid to capture ramp-up/cool-down transients.
* **pH**: Continuous logging of $pH(t)$, or precise tracking of acid dosing if buffered.
* **Agitation**: Sufficient to ensure uniform suspension (preventing localized thermal/pH gradients).

### B. Sampling Subsystem
Endpoint-only measurements cannot resolve the hydrolysis/degradation cascade tradeoff. Time-resolved sampling is a core capability.
* **Non-destructive withdrawal**: Ability to pull samples without altering the remaining reactor volume ratio or heat transfer.
* **Rapid Quenching**: Extracted samples must be immediately quenched (e.g., rapid cooling to < 20 °C or neutralization) to lock the exact reaction time $t$.
* **Traceability**: Precise timestamping of the exact quench time, not the nominal intended time.

---

## 3. The 14-Run Campaign Architecture
The experimental campaign utilizes an 8-10 run calibration set, plus 2-4 genuinely independent validation runs to test interpolation and feedstock generalization.

### Calibration Set (Batch A)
Execute the exact 10-run D-optimal design to maximize information entropy and decorrelate activation energies. 

| Run | T (°C) | pH | t (min) | d₅₀ (µm) | Purpose |
|:---:|:---:|:---:|:---:|:---:|:---|
| 1-2 | 50, 95 | 1.5, 2.5 | 45, 90 | 600 | Temperature/pH boundary pairings |
| 3-4 | 50, 95 | 1.5, 1.5 | 120, 20 | 300 | Asymmetric time extremes |
| 5-7 | 95, 50, 95 | 3.0, 2.0, 2.0 | 90, 45, 20 | 150-600 | Extreme pairing anchors |
| 8-10| 50, 50, 95 | 2.0, 1.5, 1.5 | 120, 120, 20 | 600-150 | Particle size / low-T extended |

### Validation Set (Batch A & Batch B)
Hold out 4 runs from the calibration algorithm to test scientific generalization.

| Run | Feedstock | T (°C) | pH | t (min) | d₅₀ (µm) | Validation Objective |
|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| 11 | **Batch A** | 75 | 2.2 | 60 | 300 | **Interior Interpolation** (Center-point test) |
| 12 | **Batch A** | 85 | 1.8 | 40 | 300 | **Near-Optimum** (Test trajectory toward high yield) |
| 13 | **Batch B** | 90 | 1.5 | 90 | 150 | **Severity Edge / Feedstock Generalization** (Test degradation cascade on new material) |
| 14 | **Batch B** | 60 | 2.8 | 120| 600 | **Low-Yield Edge / Feedstock Generalization** (Test extraction limit on new material) |

---

## 4. Time-Course Sampling Plan & Assays
To resolve the $k_{hyd} \leftrightarrow k_{deg}$ ambiguity while managing analytical costs, the sampling schedule is asymmetric.

For each reactor run (e.g., a 120-minute run), draw samples at specific intervals.

| Sampling Stage | Target Time (min) | Gravimetric Yield ($Y$) | Degree of Esterification ($DE$) | Molecular Weight ($M_w$) |
|:---|:---:|:---:|:---:|:---:|
| **Early** | 10 - 20 | ✓ | ✓ | ✓ |
| **Intermediate** | 45 - 60 | ✓ | ✓ | [Reserve sample, do not assay initially] |
| **Late** | 90 - 120 | ✓ | ✓ | ✓ |

*Rationale:* 
* Yield and DE are relatively fast/cheap assays and should be tracked continuously to capture extraction and de-esterification kinetics.
* MW ($M_w$) via SEC/GPC is expensive and slow. Measuring early and late bounds the hydrolysis rate. Intermediate samples are physically taken and quenched, but only analyzed if the model fit shows high residual uncertainty in the intermediate trajectory.

### Analytical Noise Targets
The experimental protocols for the assays should be engineered to meet or exceed these historical variances:
* **Yield**: $\sigma \approx 1\%$ absolute
* **DE**: $\sigma \approx 2\%$ absolute
* **MW**: $\sigma \approx 15,000$ Da
