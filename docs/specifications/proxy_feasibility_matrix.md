# Proxy Feasibility Matrix

This document evaluates the literature-supported empirical measurements proposed to augment or replace expensive physicochemical assays (SEC-MALLS, Titration). 

The goal is to select a high-value measurement stack where the Bayesian model propagates proxy uncertainty ($\sigma_{proxy}$) into the kinetic posterior, noting that **these are candidate proxies requiring passion-fruit-specific paired calibration**, not universally accurate constants.

## 1. Evaluation Matrix

| Candidate Proxy | Target Property | Sample Prep Required | Per-Sample Time | Expected RMSEP (from Cross-Validation) | Value (Information / Cost) |
|:---|:---|:---|:---|:---|:---|
| **Simple Flow Time ($t_{flow}$)** | $M_w$ (Screening) | **Standardized Precipitate**. Dissolved at fixed concentration, pH, temp. | 5–10 min | To be measured (High variance expected) | **High** (Ultra-cheap, fast empirical screening) |
| **Intrinsic Viscosity ($[\eta]$)** | $M_w$ (Quantitative) | **Standardized Precipitate**. Dilution series required. | 30–45 min | To be measured (relies on Mark-Houwink $K, a$ calibration) | **High** (Strong theoretical basis, but constants break down at $>10^5$ Da without specific calibration) |
| **FTIR / DRIFTS** | $DE$ & $X_{GalA}$ | **Standardized Precipitate (Dried)**. | < 5 min | To be measured (Lit suggests 1–3% DE error) | **Very High** (Full-spectrum chemometrics PLS/PCR yields multiple targets simultaneously) |
| **mHDP Colorimetry** | $X_{GalA}$ (Anchor) | Direct or precipitate | 20 min | $\approx 2-3\%$ (Lit target) | **Medium** (Better suited as a medium-frequency anchor assay than a high-frequency proxy) |
| **Standardized Gel Test** | $Q_{functional}$ | **Standardized Formulation**. Fixed sucrose/pH/Ca$^{2+}$, controlled cooling. | 12–24 hrs | N/A (Direct functional metric) | **High** (Does not predict yield directly, but differentiates product quality for optimization) |

## 2. Proposed Measurement Hierarchy

Instead of performing every assay on every sample, the digital twin architecture uses a tiered measurement hierarchy:

1. **High-Frequency (Every Reactor Aliquot)**:
   * **FTIR Spectrum** $\rightarrow \widehat{DE}, \widehat{X_{GalA}}$ (via full-spectrum chemometrics like PLS/PCR, not just a single peak ratio).
   * **Simple Flow Time ($t_{flow}$)** $\rightarrow \widehat{M_w}$ (rapid empirical screening at fixed concentration).
2. **Medium-Frequency (Selected Checkpoints)**:
   * **mHDP Colorimetry** $\rightarrow$ True $X_{GalA}$ (To anchor the FTIR GalA model and correct for neutral sugar interference).
   * **Titration** $\rightarrow$ True $DE$ (To anchor the FTIR DE model).
3. **Low-Frequency (Calibration Anchors & Feedstock)**:
   * **SEC-MALLS** $\rightarrow$ True $M_w$.
4. **Occasional / Optimization Target**:
   * **Standardized Gel/Texture** $\rightarrow Q_{functional}$. Allows the optimizer to distinguish between two runs that have identical GalA yield but different gelation qualities.

## 3. Bayesian Implementation Rule
The uncertainty fed into the Bayesian digital twin ($\sigma_{proxy}$) is **never a literature assumption**. It must be strictly defined as the Root Mean Square Error of Prediction (**RMSEP**) derived from the held-out cross-validation set during the Proxy Discovery Campaign. 

The Bayesian model then natively consumes these as probability distributions (e.g., $M_w \sim \mathcal{N}(420, RMSEP^2)$), seamlessly downgrading the influence of the cheap proxy relative to a true SEC-MALLS anchor.
