# Proxy Measurement Architecture (Secondary Measurement Model)

## 1. The Economic Measurement Problem
The digital twin requires measurements of Molecular Weight ($M_w$), Degree of Esterification ($DE$), and extracted Pectin Yield ($Y_p$) to resolve kinetic ambiguities (e.g., $k_{hyd} \leftrightarrow k_{deg}$). However, assays like HPSEC-MALLS ($M_w$) are too slow and expensive to perform on high-frequency time-series aliquots.

**Solution**: Introduce a probabilistic measurement hierarchy.
$$ \text{Reactor Sample} \rightarrow \text{Standardized Precipitation} \rightarrow \text{Cheap Observables } (\mathbf{z}) $$
$$ \mathbf{z} \rightarrow \text{Proxy Model (PLS/PCR)} \rightarrow \text{Predicted Properties } (\mathbf{y}) \pm RMSEP $$

## 2. The Bayesian Measurement Model
Rather than treating a proxy as a perfect substitute, it is treated as a probabilistic measurement model. 

Let $\mathbf{y} = [Y_p, DE, M_w]^T$ be the true expensive properties, and $\mathbf{z} = [z_{FTIR}, z_{\eta}, \dots]^T$ be cheap empirical observables. 

1. **Proxy Calibration Phase**: On a calibration dataset ($D_{proxy}$), we measure both $\mathbf{y}$ and $\mathbf{z}$ to learn proxy parameters $\phi$:
   $$ \mathbf{z}_j \sim p(\mathbf{z} \mid \mathbf{y}_j, \phi) $$
2. **Routine Reactor Inference**: For routine time-resolved aliquots, we only measure $\mathbf{z}$. The proxy posterior:
   $$ p(\mathbf{y} \mid \mathbf{z}, D_{proxy}) $$
   generates a prediction with uncertainty (e.g., $M_w = 420 \text{ kDa} \pm 18 \text{ kDa}$, where $18$ is the RMSEP from cross-validation).
3. **Kinetic Integration**: That proxy uncertainty naturally propagates into the digital twin's kinetic posterior $p(\theta \mid D)$. This allows us to ingest 10x-100x more time-series data without discarding the uncertainty of the cheap measurement.

## 3. Proxy Candidates & Standardization
Because polymer rheology and spectral properties are heavily confounded by the immediate solvent environment (water, unreacted acid, co-extracted simple sugars), **direct liquor testing is invalid**. Samples must undergo a rapid *Standardized Precipitation* (e.g., rapid ethanol wash and drying) before proxy testing to isolate the pectin polymer.

### Critical Warning: Precipitation Bias ($\eta_{precipitation}$)
Standardized precipitation is a processing operation. Low-molecular-weight pectin fragments may precipitate less efficiently in alcohol than high-MW chains. If this occurs, the proxy sample systematically underrepresents $P_{lowMW}$, which would severely bias the Bayesian inference of the degradation rate ($k_{deg}$). 
**Requirement**: The paired proxy calibration study *must* use the exact same precipitation protocol as the routine aliquots to capture and model this recovery bias natively.

### The `FTIR + Viscosity` Candidate Stack
These are literature-supported candidates that require a passion-fruit-specific paired calibration study.

1. **FTIR / DRIFTS** (Chemical Properties)
   * **Targets**: $DE$ and $X_{GalA}$
   * **Rationale**: Literature demonstrates rapid prediction of DE and GalA from carbonyl absorption bands. 
   * **Execution**: Performed directly on the dried standardized precipitate. Do not constrain the model to hand-picked peak ratios; utilize the full spectrum via chemometric PLS or PCR.

2. **Capillary / Simple Viscosity** (Molecular Properties)
   * **Targets**: $M_w$
   * **Rationale**: The Mark-Houwink equation links intrinsic viscosity to molecular weight. However, the constants ($K, a$) are highly system-dependent and break down for $M_w > 10^5$ Da. Our expected range ($50 - 700$ kDa) absolutely requires a passion-fruit specific calibration mapping $\eta_{proxy} \rightarrow M_{w,SEC}$.
   * **Execution**: Tested as an ultra-cheap fixed-concentration flow time ($t_{flow}$) or a full dilution series intrinsic viscosity ($[\eta]$).

## 4. Proxy Discovery Campaign (Milestone 6a)
Before designing the full 14-run reactor campaign, we must calibrate the proxy models over the **entire operational space**.

**Protocol**:
1. Generate 20–40 physical samples spanning the full OED severity space (e.g., $DE \approx 40-80\%$, $M_w \approx 50-700$ kDa).
2. For each sample, split the aliquot into parallel analytical branches:
   * **Branch A (Cheap)**: Standardized Precipitation $\rightarrow$ FTIR, Viscosity ($t_{flow}$)
   * **Branch B (Reference)**: Standardized Precipitation $\rightarrow$ DE Titration, SEC-MALLS, mHDP GalA Colorimetry
3. Train multivariate chemometric models (PLS, PCR, nonlinear) predicting Branch B targets from Branch A signals.
4. Calculate the Root Mean Square Error of Prediction (**RMSEP**) on strictly held-out cross-validation folds. 
5. Select the proxy suite based on $\text{Value} = \frac{\text{Information Gained (reduction in uncertainty)}}{\text{Cost per sample}}$.
