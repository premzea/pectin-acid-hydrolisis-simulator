# Pectin Extraction Model Specification (V1.3 Digital Twin)

Based on rigorous review of passion-fruit literature, this document formally defines the V1.3 mathematical architecture. It explicitly separates mass states from chemical properties using mass-weighted property moments, establishes a strict four-pool conservation of the modeled pectin-derived mass inventory, clarifies parameter ontology, and transitions the calibration architecture toward Bayesian parameter inference.

## 1. Initial State: Fresh Rind ($F_0$)
The initial state defines the normalized dry-feed basis and the chemical/physical properties inherited by the conditioned feedstock.

* $X_{w,0}$: Initial moisture content (wet basis) $\approx 0.81 - 0.86$
* $P_{matrix,0}$: Initial available protopectin content [kg/kg_dry,feed]
* $X_{GalA,matrix}$: GalA fraction of the matrix pectin
* $DE_{matrix}$: Degree of esterification of the matrix pectin
* $M_{w,matrix}$: Molecular weight of matrix-associated pectin

**Explicit Initial Conditions (Masses):**
* $P_{matrix}(0) = P_{matrix,0}$
* $P_{sol}(0) = P_{lowMW}(0) = P_{loss}(0) = 0$
* $G_{matrix}(0) = P_{matrix,0} \cdot X_{GalA,matrix}$
* $G_{sol}(0) = G_{lowMW}(0) = G_{loss}(0) = 0$
* $Q_{DE,sol}(0) = 0$
* $M_{w,sol}(0) = M_{w,matrix}$

*Note: Literature reports for extracted passion-fruit pectin ($DE \approx 74.5\%$, $M_w \approx 6.54 \times 10^5$ Da, GalA $\approx 78\%$) are **Informative Priors for the extracted-product properties**, not assumptions about the fresh rind polymer. DE and MW for the soluble pool are properties of the material currently residing in the pool.*

## 2. Feedstock Conditioning Submodel

**A. Drying**
Moisture removal modeled via an effective diffusion rate:
$$ \frac{dX_w}{dt} = -k_d(T_{air}, v_{air}) \cdot (X_w - X_{w, eq}) $$
*(Note: V1 will not simultaneously infer drying kinetics with extraction parameters. The first experimental campaign will use a standardized dried feedstock with $X_{w,final} \approx 8\%$ and $d_{50} \approx 300\mu m$.)*

**B. Milling**
Reduces the bulk dried rind to a characteristic particle size $d_{50} \text{ (µm)}$. The model uses a fixed reference size:
$$ d_{ref} = 300 \text{ µm} $$

## 3. Acid Extraction Submodel

### Conceptual Architecture (4-Pool Mass Transfer)

```text
Feedstock
    │
    ▼
P_matrix
    │
    │ k_ext(T,pH,d50)
    ▼
P_sol ───────────────┐
    │                │
    │ k_hyd          │ properties
    ▼                │
P_lowMW              │ DE, MW, GalA
    │                │
    │ k_deg          │
    ▼                ▼
P_loss          product quality
```

**Terminology:**
* **Hydrolysis** ($k_{hyd}$): Continuous acid-catalyzed chain scission within the soluble pectin population. Material crossing the model's threshold is transferred to the low-MW lumped compartment.
* **Degradation** ($k_{deg}$): Low-MW pectin -> non-pectic soluble products.

### Differential Equations (Normalized Mass Conservation)
All $P_i$ variables use a consistent normalized mass convention [kg/kg_dry,feed].

1. **Solubilization:** $\frac{dP_{matrix}}{dt} = -k_{ext} P_{matrix}$
2. **Hydrolysis:** $\frac{dP_{sol}}{dt} = k_{ext} P_{matrix} - k_{hyd} P_{sol}$
3. **Depolymerization:** $\frac{dP_{lowMW}}{dt} = k_{hyd} P_{sol} - k_{deg} P_{lowMW}$
4. **Unrecoverable Loss:** $\frac{dP_{loss}}{dt} = k_{deg} P_{lowMW}$

**Invariants & Diagnostics:**
* Analytical Identity: $\frac{d P_{tot}}{dt} = 0$ where $P_{tot} = P_{matrix} + P_{sol} + P_{lowMW} + P_{loss}$
* The total modeled pectin-derived mass accounting inventory is strictly conserved.
* $\epsilon_M = P_{matrix, 0} - P_{tot} \approx 0$
* $G_{matrix,0} = G_{matrix} + G_{sol} + G_{lowMW} + G_{loss}$
* **Positivity & Bounds**: $P_i(t) \ge 0$, $0 \le DE_i \le 1$, $0 \le X_{GalA,i} \le 1$, $M_w \ge M_{w,min} > 0$.

### Cohort-Correct Properties (Moments)
Because pectin continuously enters the soluble pool, material has experienced different cumulative exposures. We model properties using mass-weighted moments.

* **De-esterification Moments:**
  $\frac{dQ_{DE,sol}}{dt} = k_{ext} P_{matrix} DE_{matrix} - k_{de} Q_{DE,sol} - k_{hyd} Q_{DE,sol}$
  $\frac{dQ_{DE,lowMW}}{dt} = k_{hyd} Q_{DE,sol} - k_{de} Q_{DE,lowMW} - k_{deg} Q_{DE,lowMW}$
  $DE_{sol} = \frac{Q_{DE,sol}}{P_{sol}}$ , $DE_{lowMW} = \frac{Q_{DE,lowMW}}{P_{lowMW}}$
  *(Note: V1 assumes the de-esterification rate constant is identical for soluble intact and low-MW pectin.)*

* **Molecular Weight Moments:**
  $\frac{dQ_{MW,sol}}{dt} = k_{ext} P_{matrix} M_{w,matrix} - k_{hyd} Q_{MW,sol} - \beta_{MW} k_{hyd} (Q_{MW,sol} - M_{w,min} P_{sol})$
  $\frac{dQ_{MW,lowMW}}{dt} = k_{hyd} Q_{MW,sol} - k_{deg} Q_{MW,lowMW} - \beta_{MW} k_{deg} (Q_{MW,lowMW} - M_{w,min} P_{lowMW})$
  $M_{w,sol} = \frac{Q_{MW,sol}}{P_{sol}}$ , $M_{w,lowMW} = \frac{Q_{MW,lowMW}}{P_{lowMW}}$
  *(Note: This moment formulation elegantly avoids the $1 / P$ singularity at $t=0$. The $k_{deg}$ term implies degradation continues reducing MW toward $M_{w,min}$ in the low-MW transition zone.)*

### Kinetics & Empirical Extraction Modifiers
Temperature and acidity are parameterized using a reference-state formulation to improve parameter inference numerical stability by decoupling prefactors and activation energies. The model architecture reserves an explicit citric-acid concentration effect ($C_{citric}$) on de-esterification; this effect is disabled in V1 by fixing $\gamma_{citric} = 0$.

* **Effective Extraction Rate:** $k_{ext} = k_{ext,chem} \phi_d$
* **Empirical Transport Modifier:** $\phi_d = (d_{ref} / d_{50})^\alpha$ *(Note: This is an empirical lumped accessibility/transport correction, not a mechanistic diffusion coefficient.)*
* **Reference State:** $T_{ref} = 353.15$ K (80 °C), $pH_{ref} = 2.0$
* **Reference Arrhenius Form:**
  $$ k = k_{ref} \exp\left[-\frac{E}{R}\left(\frac{1}{T_K} - \frac{1}{T_{ref}}\right)\right] 10^{n(pH_{ref} - pH)} $$
* **De-esterification:** $k_{de} = k_{de,ref} \exp\left[-\frac{E_{de}}{R}\left(\frac{1}{T_K} - \frac{1}{T_{ref}}\right)\right] 10^{n_{de}(pH_{ref} - pH)} (1 + \gamma_{citric} C_{citric})$

## 4. Target Metrics (Normalized)
The downstream recovery factor ($\eta_{recovery}$) is applied at the product stage to account for precipitation/washing/drying losses.

* **Gravimetric Yield:** 
  $Y_p = \eta_{recovery} (P_{sol} + P_{lowMW})$ 
* **GalA Inventories (Tracking Moments):** 
  $\frac{dG_{sol}}{dt} = k_{ext} P_{matrix} X_{GalA,matrix} - k_{hyd} P_{sol} X_{GalA,sol}$
  $\frac{dG_{lowMW}}{dt} = k_{hyd} P_{sol} X_{GalA,sol} - k_{deg} P_{lowMW} X_{GalA,lowMW}$
  $\frac{dG_{loss}}{dt} = k_{deg} P_{lowMW} X_{GalA,lowMW}$
  $X_{GalA,i} = \frac{G_i}{P_i}$
  *(Note: In V1, the GalA fraction of matrix-associated pectin is constant during solubilization.)*
* **Purity:** $Purity_{GalA} = X_{GalA,product}$
* **Useful GalA Recovery:** 
  $Y_{GalA,extract} = \frac{G_{sol} + G_{lowMW}}{G_{matrix, 0}}$ 
  $Y_{GalA,product} = \frac{\eta_{recovery}(G_{sol} + G_{lowMW})}{G_{matrix, 0}}$

## 5. Parameter Ontology Table
To avoid mathematical ambiguity, all parameters are strictly assigned an ontology classification.

| Symbol | Meaning | Units | Anchor / Range | Classification |
| :--- | :--- | :--- | :--- | :--- |
| $T$ | Extraction Temperature | °C | 45–100 °C | Controlled Process Variable |
| $pH$ | Kinetic Acidity | pH | 1.2–4.5 | Controlled Process Variable |
| $C_{citric}$ | Acid Concentration | mol/L | Initial design range = 0.05–0.5 M | Controlled Process Variable |
| $t$ | Extraction Time | min | 5–120 min | Controlled Process Variable |
| $X_{w,0}$ | Fresh Moisture | % wb | 81–86% | Measured |
| $d_{50}$ | Particle Size | µm | 149–500 µm | Measured |
| $d_{ref}$ | Reference Size | µm | 300 µm | Fixed |
| $M_{w,matrix}$| MW of matrix-associated pectin | Da | $6.54\times10^5$ | Informative prior / Inferred |
| $k_{ext,ref}, k_{hyd,ref}, k_{deg,ref}, k_{de,ref}$ | Reference Rates (at 80°C, pH 2.0) | min⁻¹ | TBD | Calibrated |
| $E_{ext}, E_{hyd}, E_{deg}, E_{de}$ | Activation Energies | J/mol | TBD | Calibrated |
| $n_{ext}, n_{hyd}, n_{deg}, n_{de}$ | Acidity Orders | - | 1.0 | Fixed V1 |
| $\alpha$ | Particle Size Scaling | - | 0.5–2.0 | Calibrated |
| $\beta_{MW}$ | Hydrolysis-to-MW sensitivity | - | 1.0 | Fixed V1 |
| $\gamma_{citric}$ | Citric DE Multiplier | L/mol | 0.0 | Fixed V1 |
| $\eta_{recovery}$| Recovery Efficiency | - | 0.90 | Measured / Fixed Protocol |

**Physical Constants:**
* $R = 8.314462618 \text{ J/mol K}$
* $T_K = T_C + 273.15$
* $T_{ref} = 353.15$ K
* $pH_{ref} = 2.0$

---

## 6. Validated Computational Results (Synthetic Data Pipeline)

### Status: Synthetic closed-loop validation complete.
> The computational inference workflow is validated under the assumed V1.3 data-generating model. The reactor will determine whether V1.3 is a good model of reality.

### Milestone sequence completed

```
V1.3 mechanistic model
        ↓
Forward simulator verification (mass conservation ε < 1e-10)
        ↓
Synthetic-data generation
        ↓
RF surrogate validation (R² > 0.995)
        ↓
Parameter sensitivity / identifiability (Designs A→E)
        ↓
D-optimal experiment design (10-run protocol, κ(F) = 52)
        ↓
Synthetic Bayesian calibration validation (9/9 BCI, 100% PPC)
        ↓
   ★ READY FOR PHYSICAL EXPERIMENTS ★
   (as model-testing/calibration system, not yet a validated digital twin)
```

### Precise status claims

| Claim | Status |
|:---|:---|
| **Synthetic Bayesian recovery validated**: sampler recovers $\theta^*$ from data generated by the same model | YES |
| **Posterior predictive consistency**: independently held-out synthetic observations fall within 95% predictive intervals | YES (12/12) |
| **Computational inference workflow validated** | YES |
| **Scientific calibration to real chemistry** | NOT YET — requires reactor data |
| **Digital twin validated for prediction** | NOT YET |

### Posterior parameter correlation findings

| Correlation | Value | Interpretation |
|:---|:---:|:---|
| $Corr(k_{ext}, E_{ext})$ | 0.27 | Modest — reference parameterization working |
| $Corr(k_{hyd}, E_{hyd})$ | 0.28 | Modest |
| $Corr(k_{deg}, E_{deg})$ | 0.31 | Modest — OED design effective |
| $Corr(k_{de}, E_{de})$ | 0.46 | Moderate-high |
| $Corr(k_{hyd}, k_{deg})$ | **−0.85** | Structural cascade constraint |
| $Corr(E_{hyd}, E_{deg})$ | **−0.85** | Structural cascade constraint |

> The hydrolysis/degradation anti-correlation is a structural consequence of the cascade architecture and the current observable set. It may be partially reduced by time-resolved measurements, but complete separation may require richer observations or a different state representation. It is not simply a design failure.

### Posterior optimum distribution $P(x^* \mid D)$

| Variable | Median | 95% CI |
|:---|:---:|:---:|
| $T^*$ | 45.0°C | [45.0, 45.1] |
| $\text{pH}^*$ | 1.62 | [1.24, 1.74] |
| $t^*$ | 89.5 min | [37.7, 118.1] |
| $Y_{\text{GalA}}^*$ | 77.4% | [76.4, 78.2%] |

> **Important:** $T^*$ is boundary-limited at $T_{min} = 45°C$ — V1.3 has not identified an interior temperature optimum. Lower temperature is always better within the allowed domain under the current model. This does not mean 45°C is the physical optimum; the model may overstate thermal degradation or understate high-T extraction benefit. Record as: *temperature optimum is boundary-limited in V1.3.*

> The broad $t^*$ interval [37.7, 118.1 min] directly reflects the $k_{hyd} \leftrightarrow k_{deg}$ anti-correlation. Time-resolved reactor measurements are the primary tool to resolve it.

### Model-mismatch robustness

A 4% nonlinear T/pH interaction discrepancy ($\delta(x) = 0.04\sin(\pi\hat{T})\sin(\pi\hat{\text{pH}})$) was injected into GalA yield. The V1.3 Bayesian model fitted to contaminated data:

- **9/9 parameters covered** within 95% BCI
- Maximum parameter bias: **5.3%** on $k_{hyd,ref}$ (physically expected — discrepancy aligns with the hydrolysis sensitivity direction)
- Degradation pair bias: **−1 to −3%** (did not cascade, due to OED extreme-condition anchoring)

> V1.3 shows modest parameter bias under the tested 4% nonlinear T/pH interaction discrepancy. This does not establish general misspecification robustness. The test characterizes robustness to one specific perturbation geometry.

---

## 7. Reactor Experimental Protocol

### Required before physical experiments

1. **Feedstock variability stress test** — batch-to-batch variation in $P_{matrix,0}$, $X_{GalA}$, $DE$, $M_w$ may dominate over model discrepancy as the primary uncertainty source.

2. **Reserve validation runs** — use 8–10 runs for calibration, hold 2–4 genuinely independent conditions (interior, near optimum, high-severity edge) as external validation.

### Priority measurement strategy

Time-course data break the $k_{hyd} \leftrightarrow k_{deg}$ ambiguity:

```
Early time:        Y(t), DE(t), Mw(t)
Intermediate time: Y(t), DE(t)
Late time:         Y(t), DE(t), Mw(t)
```

Endpoint-only measurements cannot fully separate the hydrolysis/degradation cascade pair.

### 10-run OED calibration protocol (D-optimal, $\kappa(F) = 52$)

| Run | T (°C) | pH | t (min) | d₅₀ (µm) |
|:---:|:---:|:---:|:---:|:---:|
| 1 | 50 | 1.5 | 45 | 600 |
| 2 | 95 | 2.5 | 90 | 600 |
| 3 | 50 | 1.5 | 120 | 300 |
| 4 | 95 | 1.5 | 20 | 300 |
| 5 | 95 | 3.0 | 90 | 150 |
| 6 | 50 | 2.0 | 45 | 150 |
| 7 | 95 | 2.0 | 20 | 600 |
| 8 | 50 | 2.0 | 120 | 600 |
| 9 | 50 | 1.5 | 120 | 150 |
| 10 | 95 | 1.5 | 20 | 150 |

Key structure: extreme T pairing (50°C vs 95°C), extreme d₅₀ pairing (150 vs 600 µm), short early times at high T, long times at low T.

### Observation noise model (assumed for calibration)

| Observation | $\sigma$ | Rationale |
|:---|:---:|:---|
| $Y_{\text{GalA}}$ | 0.01 | 1% absolute yield |
| $DE_{\text{product}}$ | 0.02 | 2% absolute DE |
| $M_{w,\text{product}}$ | 15,000 Da | ~3% at 500 kDa |
