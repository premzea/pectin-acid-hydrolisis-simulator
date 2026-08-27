# Proxy Measurement Architecture (Secondary Measurement Model)

## 1. The Economic Measurement Problem
The digital twin requires measurements of Molecular Weight ($M_w$), Degree of Esterification ($DE$), and extracted Pectin Yield ($Y_p$) to resolve kinetic ambiguities (e.g., $k_{hyd} \leftrightarrow k_{deg}$). However, assays like HPSEC-MALLS ($M_w$) and rigorous titrations ($DE$) are too slow and expensive to perform on high-frequency time-series aliquots across dozens of batches.

**Solution**: Introduce a two-tier measurement architecture.
$$ \text{Reactor Sample} \rightarrow \text{Standardized Formulation} \rightarrow \text{Cheap Observables } (\mathbf{z}) $$
$$ \mathbf{z} \rightarrow \text{Proxy Model} \rightarrow \text{Predicted Properties } (\mathbf{y}) \pm \sigma_{proxy} $$

## 2. The Bayesian Measurement Model
Rather than treating a proxy as a perfect substitute, it is treated as a probabilistic measurement model. 

Let $\mathbf{y} = [Y_p, DE, M_w]^T$ be the true expensive properties, and $\mathbf{z} = [z_1, z_2, \dots]^T$ be cheap empirical observables. 

1. **Proxy Calibration Phase**: On a small calibration dataset ($D_{proxy}$), we measure both $\mathbf{y}$ and $\mathbf{z}$ to learn proxy parameters $\phi$:
   $$ \mathbf{z}_j \sim p(\mathbf{z} \mid \mathbf{y}_j, \phi) $$
2. **Routine Reactor Inference**: For routine time-resolved aliquots, we only measure $\mathbf{z}$. The proxy posterior:
   $$ p(\mathbf{y} \mid \mathbf{z}, D_{proxy}) $$
   generates a prediction with uncertainty (e.g., $Y_p = 14.2\% \pm 1.1\%$).
3. **Kinetic Integration**: That proxy uncertainty ($\sigma_{proxy}$) naturally propagates into the digital twin's kinetic posterior $p(\theta \mid D)$. This allows us to ingest 10x-100x more time-series data without discarding the uncertainty of the cheap measurement.

## 3. Proxy Candidates & Standardization
Because polymer rheology and spectral properties are heavily confounded by the immediate solvent environment (water, unreacted acid, co-extracted simple sugars), **direct liquor testing is invalid**. Samples must undergo a rapid *Standardized Precipitation* (e.g., rapid ethanol wash and drying) before proxy testing to isolate the pectin polymer.

### The `FTIR + Viscosity` Stack
Based on literature feasibility, the project targets a highly compact, two-instrument measurement stack for routine aliquots:

1. **FTIR / DRIFTS** (Chemical Properties)
   * **Targets**: $DE$ and $X_{GalA}$
   * **Rationale**: Strong literature precedent demonstrating rapid, non-destructive prediction of DE (1-3% error) and GalA content from the carbonyl absorption bands.
   * **Execution**: Performed directly on the dried standardized precipitate.

2. **Capillary / Simple Viscosity** (Molecular Properties)
   * **Targets**: $M_w$
   * **Rationale**: The Mark-Houwink equation mathematically links intrinsic viscosity to molecular weight. Empirical viscosity measurements at standardized concentrations are well-documented proxies for pectin $M_w$.
   * **Execution**: The precipitate is dissolved in a standard buffer at a fixed concentration ($C_p$) prior to flow testing.

*(Note: NIR for bulk yield and standardized gel-collapse tests for functional quality were evaluated but relegated to secondary status due to severe matrix dependencies and multidimensional confounding, respectively).*

## 4. Proxy Discovery Campaign (Milestone 6a)
Before designing the full 14-run reactor campaign, we must discover and validate which proxies have the highest **Value**:
$$ \text{Value} = \frac{\text{Information Gained (reduction in } \sigma_{proxy})}{\text{Cost per sample}} $$

**Protocol**:
1. Generate 20–40 physical samples spanning the full extraction severity space (using the OED boundary conditions).
2. Measure the "Expensive Reference Assays" ($Y_p, DE, M_w$) on all samples.
3. Measure the candidate "Cheap Proxies" ($\mathbf{z}$) on all samples.
4. Train multivariate predictive models: $\mathbf{y} = g(\mathbf{z}) + \epsilon$.
5. Evaluate on held-out samples. Select the winning proxy suite based on the Value metric.

Future reactor runs will then use the winning cheap suite for dense temporal sampling (e.g., every 10 minutes), reserving the expensive reference assays only for calibration anchors (e.g., $t=120$ min) and bulk feedstock characterization.
