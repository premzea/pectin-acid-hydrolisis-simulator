# Domain 2: Mathematical Modeling & Statistical Calibration Architecture

**Document Version**: 2.1 (Incorporating Statistical Peer Review)  
**Parent Document**: [`MASTER_DUAL_TRACK_SPECIFICATION.md`](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/MASTER_DUAL_TRACK_SPECIFICATION.md)  
**Target Audience**: Bioprocess Modelers, Applied Mathematicians, Chemometricians, Bayesian Statisticians

---

## 1. Executive Scope

This document specifies the mathematical formulations, state-space representations, chemometric soft-sensor vector models, Fisher Information optimal experimental design (OED), and Bayesian parameter inference pipelines of the Pectin Digital Twin ecosystem.

Incorporating rigorous peer-review critiques, this specification resolves key identifiability challenges:
1. Formulates dedicated **OED calibration matrices with true process replicates** for both Track A and Track B.
2. Resolves structural unidentifiability by explicitly fixing the single-transducer frequency exponent ($\gamma_{US} \equiv 1.0$).
3. Introduces a two-tier observation variance model ($\mathbf{\Sigma}_{\text{total}} = \mathbf{\Sigma}_{\text{obs}} + \mathbf{\Sigma}_{\text{process}}$) separating analytical measurement error from run-to-run execution variance.
4. Harmonizes particle accessibility across fresh and dried tissue using a biological matrix integrity factor ($\Omega_{\text{matrix}}$).

---

## 2. The 4-Pool Mechanistic Mass-Transfer Model

### A. State Definitions & Mass Conservation
The extraction and depolymerization cascade is modeled across four distinct, mutually exclusive mass pools, normalized to dry feedstock mass $[\text{kg/kg}_{\text{dry,feed}}]$:

```text
  Protopectin in Plant Matrix (P_matrix)
                    │
                    │ k_ext (T, pH, d50, P_acoustic, Ω_matrix)
                    ▼
       Soluble Intact Pectin (P_sol) ───────────────┐
                    │                               │
                    │ k_hyd (T, pH)                 │ Quality Properties:
                    ▼                               │ DE, Mw, X_GalA
         Low-MW Oligomers (P_lowMW)                 │
                    │                               │
                    │ k_deg (T, pH)                 │
                    ▼                               ▼
        Degraded End Products (P_loss)       Product Recovery
```

#### Differential Equations
1. **Solubilization**:
   $$\frac{dP_{\text{matrix}}}{dt} = -k_{\text{ext}} P_{\text{matrix}}$$
2. **Hydrolysis**:
   $$\frac{dP_{\text{sol}}}{dt} = k_{\text{ext}} P_{\text{matrix}} - k_{\text{hyd}} P_{\text{sol}}$$
3. **Depolymerization**:
   $$\frac{dP_{\text{lowMW}}}{dt} = k_{\text{hyd}} P_{\text{sol}} - k_{\text{deg}} P_{\text{lowMW}}$$
4. **Unrecoverable Degradation**:
   $$\frac{dP_{\text{loss}}}{dt} = k_{\text{deg}} P_{\text{lowMW}}$$

#### Conservation Invariant
Total mass inventory is strictly conserved at all time points:
$$P_{\text{tot}}(t) = P_{\text{matrix}}(t) + P_{\text{sol}}(t) + P_{\text{lowMW}}(t) + P_{\text{loss}}(t) \equiv P_{\text{matrix},0}$$
$$\frac{d P_{\text{tot}}}{dt} = 0, \quad \epsilon_M = |P_{\text{matrix},0} - P_{\text{tot}}(t)| < 10^{-10}$$

---

## 3. Cohort-Correct Property Moments

Because pectin continuously solubilizes from the plant matrix throughout the batch, molecules in the soluble pool possess heterogeneous reaction exposure histories. Property dynamics are therefore tracked using mass-weighted zero-order and first-order moments.

### A. Degree of Esterification (DE) Moments
Let $Q_{DE,i} = P_i \cdot DE_i$ be the total esterified mass equivalent:
$$\frac{dQ_{DE,\text{sol}}}{dt} = k_{\text{ext}} P_{\text{matrix}} DE_{\text{matrix}} - k_{\text{de}} Q_{DE,\text{sol}} - k_{\text{hyd}} Q_{DE,\text{sol}}$$
$$\frac{dQ_{DE,\text{lowMW}}}{dt} = k_{\text{hyd}} Q_{DE,\text{sol}} - k_{\text{de}} Q_{DE,\text{lowMW}} - k_{\text{deg}} Q_{DE,\text{lowMW}}$$
$$DE_{\text{sol}}(t) = \frac{Q_{DE,\text{sol}}(t)}{P_{\text{sol}}(t)}, \quad DE_{\text{lowMW}}(t) = \frac{Q_{DE,\text{lowMW}}(t)}{P_{\text{lowMW}}(t)}$$
*Note*: This formulation avoids numerical singularities as $P_{\text{sol}} \to 0$ and naturally preserves bounds $0 \le DE \le 1$.

### B. Molecular Weight (Mw) Moments
Let $Q_{MW,i} = P_i \cdot M_{w,i}$ be the mass-weighted molecular weight moment:
$$\frac{dQ_{MW,\text{sol}}}{dt} = k_{\text{ext}} P_{\text{matrix}} M_{w,\text{matrix}} - k_{\text{hyd}} Q_{MW,\text{sol}} - \beta_{MW} k_{\text{hyd}} (Q_{MW,\text{sol}} - M_{w,\text{min}} P_{\text{sol}})$$
$$\frac{dQ_{MW,\text{lowMW}}}{dt} = k_{\text{hyd}} Q_{MW,\text{sol}} - k_{\text{deg}} Q_{MW,\text{lowMW}} - \beta_{MW} k_{\text{deg}} (Q_{MW,\text{lowMW}} - M_{w,\text{min}} P_{\text{lowMW}})$$
$$M_{w,\text{sol}}(t) = \frac{Q_{MW,\text{sol}}(t)}{P_{\text{sol}}(t)}$$
where $M_{w,\text{min}} = 10,000\text{ Da}$ represents the lower limit of polymeric pectin integrity, and $\beta_{MW} \approx 1.0$ controls chain scission sensitivity.

### C. GalA Conservation Inventory
Let $G_i = P_i \cdot X_{\text{GalA},i}$ represent the absolute mass of D-galacturonic acid:
$$\frac{dG_{\text{sol}}}{dt} = k_{\text{ext}} P_{\text{matrix}} X_{\text{GalA,matrix}} - k_{\text{hyd}} G_{\text{sol}}$$
$$\frac{dG_{\text{lowMW}}}{dt} = k_{\text{hyd}} G_{\text{sol}} - k_{\text{deg}} G_{\text{lowMW}}$$
$$\frac{dG_{\text{loss}}}{dt} = k_{\text{deg}} G_{\text{lowMW}}$$
$$X_{\text{GalA,sol}}(t) = \frac{G_{\text{sol}}(t)}{P_{\text{sol}}(t)}$$

---

## 4. Reaction Kinetics & Environmental Modifiers

Rate constants are parameterized relative to an uncoupled reference state ($T_{\text{ref}} = 353.15\text{ K} = 80^\circ\text{C}$, $\text{pH}_{\text{ref}} = 2.0$):

$$k_i(T, \text{pH}) = k_{i,\text{ref}} \exp\left[-\frac{E_i}{R}\left(\frac{1}{T_K} - \frac{1}{T_{\text{ref}}}\right)\right] 10^{n_i(\text{pH}_{\text{ref}} - \text{pH})}$$

### A. Harmonized Interfacial Transport Modifier
$$\phi_{d,\text{eff}}(d_{50}) = \left(\frac{d_{\text{ref}}}{d_{50}}\right)^\alpha \cdot \Omega_{\text{matrix}}$$
* $\Omega_{\text{matrix}} \equiv 1.0$ for standardized dried and sieved powder (Track A).
* $\Omega_{\text{matrix}} = \Omega_{\text{fresh}} \approx 1.25\text{--}1.60$ for fresh un-collapsed tissue (Track B), estimated from paired fresh thermal controls.

### B. Phenomenological Ultrasound Cavitation Enhancement
$$P_{\text{acoustic}} = \eta_{\text{coupling}} \cdot P_{\text{elec}}$$
$$\psi_{US} = 1.0 + \kappa_{US} \left(\frac{P_{\text{acoustic}}}{V_{\text{slurry}}}\right)^{\beta_{US}} \left(\frac{40\text{ kHz}}{f_{US}}\right)^{\gamma_{US}}$$
* *Structural Identifiability Constraint*: Because the bath transducer is single-frequency ($40\text{ kHz}$), $\gamma_{US}$ is mathematically unidentifiable from single-instrument data. It is **fixed to $\gamma_{US} \equiv 1.0$** based on acoustic cavitation literature consensus.
$$k_{\text{ext,effective}} = k_{\text{ext,chem}}(T, \text{pH}) \cdot \phi_{d,\text{eff}}(d_{50}) \cdot \psi_{US}(P_{\text{acoustic}})$$

---

## 5. At-Line Multi-Channel Vector Chemometric Model

The at-line soft sensor ingests the 8-channel detector array from the **IO Rodeo Multichannel Colorimeter**:
$$\mathbf{A} = [A_{415}, A_{445}, A_{480}, A_{515}, A_{555}, A_{590}, A_{630}, A_{680}]^T$$

### A. Sample-Blank Net Absorbance Vector
To prevent native passion-fruit carotenoid/flavonoid pigments from biasing the carbazole peak, the model subtracts an unreacted sample-blank:
$$\mathbf{A}_{\text{net}}(\lambda) = \mathbf{A}_{\text{developed}}(\lambda) - \mathbf{A}_{\text{sample\_blank}}(\lambda) - A_{\text{turbidity}}(680) \left(\frac{680}{\lambda}\right)^{\alpha_{\text{Rayleigh}}}$$

### B. Multi-Wavelength Vector Regression
$$C_{\text{GalA,measured}} = w_1 A_{\text{net}}(515) + w_2 A_{\text{net}}(555) + w_3 A_{\text{net}}(680) + d$$
$$C_{\text{GalA,filtrate}} = C_{\text{GalA,measured}} \times DF$$

### C. Copper-Chelate Pectin-Equivalent Model
$$C_{\text{pectin-equiv,measured}} = \frac{A_{\text{net}}(590) - A_{0,\text{Cu}}}{S_{\text{Cu}}}$$

### D. Dynamic Linear Range Verification & Dilution Advisory
Each calibration object registers its verified linear domain $\mathcal{D}_{\text{cal}} = [C_{\text{linear,min}}, C_{\text{linear,max}}]$.
$$\text{Status}(C_{\text{meas}}) = \begin{cases} \text{VALID}, & C_{\text{linear,min}} \le C_{\text{meas}} \le C_{\text{linear,max}} \\ \text{LOW\_SIGNAL}, & C_{\text{meas}} < C_{\text{linear,min}} \\ \text{RANGE\_EXCEEDED}, & C_{\text{meas}} > C_{\text{linear,max}} \implies \text{Advise: } DF \times \left\lceil\frac{C_{\text{meas}}}{0.5 \cdot C_{\text{linear,max}}}\right\rceil \end{cases}$$

---

## 6. Optimal Experimental Design (OED) Campaigns

### A. Track A: Refined 12-Run Calibration Matrix (with Curvature & Replicates)
To address Arrhenius temperature curvature, low-severity anchoring, and process variance:
* Adds an **intermediate temperature anchor** ($70^\circ\text{C}$) to decouple $k_{\text{ref}}$ and activation energy $E$.
* Adds a **mild asymptotic baseline run** ($50^\circ\text{C}, \text{pH } 3.0$).
* Adds **two true process replicates** (Runs 10a & 10b) to estimate $\mathbf{\Sigma}_{\text{process}}$.

| Run ID | $T$ (°C) | pH | $d_{50}$ ($\mu$m) | Sample Times (min) | Design Objective |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **A-1** | 95 | 1.5 | 600 | 15, 45, 90, 120 | Severe extraction boundary; separates $E_{\text{ext}}$ from $\alpha$ |
| **A-2** | 50 | 1.5 | 150 | 15, 45, 90, 120 | Low $T$, high acidity, small particle |
| **A-3** | 95 | 2.5 | 150 | 15, 45, 90, 120 | High $T$, moderate pH, small particle |
| **A-4** | 50 | 1.5 | 600 | 15, 45, 90, 120 | Low $T$, high acidity, large particle |
| **A-5** | 70 | 2.0 | 300 | 15, 45, 90, 120 | **Intermediate $T$ anchor**: tests Arrhenius curvature |
| **A-6** | 50 | 3.0 | 300 | 15, 45, 90, 120 | **Mild asymptote anchor**: near-zero degradation baseline |
| **A-7** | 95 | 2.5 | 600 | 15, 45, 90, 120 | High $T$, low acidity, large particle |
| **A-8** | 50 | 2.0 | 150 | 15, 45, 90, 120 | Low $T$, moderate pH anchor |
| **A-9** | 95 | 3.0 | 150 | 15, 45, 90, 120 | High $T$, mild pH boundary |
| **A-10a**| 80 | 2.0 | 300 | 15, 45, 90, 120 | Center-point reference state (Replicate 1) |
| **A-10b**| 80 | 2.0 | 300 | 15, 45, 90, 120 | **True Process Replicate**: estimates run-to-run variance |
| **A-11** | 95 | 2.0 | 300 | 15, 45, 90, 120 | High-temperature validation anchor |

---

### B. Track B: Dedicated UAE OED Calibration Matrix (10 Runs)
To identify acoustic coupling ($\eta_{\text{coupling}}$), cavitation scaling ($\kappa_{US}, \beta_{US}$), and thermal enhancement ($\Delta Y_{\text{UAE}}$):
* Includes **two fresh-rind thermal controls** ($P_{\text{elec}} = 0\text{ W}$) to cleanly decouple thermal extraction from ultrasound.
* Features **time-resolved in-situ sampling** ($t \in \{10, 20, 40, 60\}\text{ min}$) for each run.
* Includes **two true process replicates** (Runs B-4a & B-4b).

| Run ID | $P_{\text{elec}}$ (W) | $T_{\text{bath}}$ (°C) | Comminution $d_{50}$ | Sample Times (min) | Design Objective |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **B-1** | **0 (OFF)** | 55 | Fine ($600\,\mu\text{m}$) | 10, 20, 40, 60 | **Thermal baseline on fresh rind** (pure thermal $Y$) |
| **B-2** | **0 (OFF)** | 70 | Fine ($600\,\mu\text{m}$) | 10, 20, 40, 60 | **High-T thermal baseline** (separates matrix from US) |
| **B-3** | 100 | 40 | Fine ($600\,\mu\text{m}$) | 10, 20, 40, 60 | Low power, mild temperature cavitation |
| **B-4a**| 200 | 55 | Fine ($600\,\mu\text{m}$) | 10, 20, 40, 60 | Reference UAE condition (Replicate 1) |
| **B-4b**| 200 | 55 | Fine ($600\,\mu\text{m}$) | 10, 20, 40, 60 | **True Process Replicate**: estimates US bath variance |
| **B-5** | 300 | 40 | Fine ($600\,\mu\text{m}$) | 10, 20, 40, 60 | Maximum acoustic power at low bulk temperature |
| **B-6** | 300 | 70 | Fine ($600\,\mu\text{m}$) | 10, 20, 40, 60 | Severe combined acoustic-thermal boundary |
| **B-7** | 200 | 55 | Coarse ($1500\,\mu\text{m}$) | 10, 20, 40, 60 | Particle size sensitivity in acoustic field |
| **B-8** | 100 | 70 | Coarse ($1500\,\mu\text{m}$) | 10, 20, 40, 60 | Low power, high $T$, coarse tissue interaction |
| **B-9** | 200 | 40 | Coarse ($1500\,\mu\text{m}$) | 10, 20, 40, 60 | Low $T$, intermediate power, large tissue |

---

## 7. Two-Tier Bayesian Inference Architecture

### A. Observation Noise Model
Rather than assuming target sensor noise is the sole source of error, the likelihood model combines analytical assay error with process execution variance:
$$\mathbf{\Sigma}_{\text{total}} = \mathbf{\Sigma}_{\text{obs}} + \mathbf{\Sigma}_{\text{process}}$$

* **$\mathbf{\Sigma}_{\text{obs}}$ (Analytical Assay Precision)**:
  - $\sigma_{\text{yield,obs}} = 0.01$ (1% absolute)
  - $\sigma_{DE,\text{obs}} = 0.02$ (2% absolute)
  - $\sigma_{Mw,\text{obs}} = 15,000\text{ Da}$
  - $\sigma_{\text{GalA,obs}} = 0.025$ (2.5% absolute)
* **$\mathbf{\Sigma}_{\text{process}}$ (Run-to-Run Process Variance)**:
  Directly estimated from the paired replicates (Runs A-10a/b and B-4a/b):
  - $\sigma_{\text{yield,process}} \approx 0.015$ (biomass packing & solid-liquid separation losses)
  - $\sigma_{\text{acoustic,process}} \approx 0.05 \cdot P_{\text{acoustic}}$ (transducer coupling variability)

### B. Bayesian Prior & Parameter Table

| Parameter | Symbol | Units | Prior Distribution $p(\theta)$ | Inference Status |
| :--- | :---: | :---: | :--- | :--- |
| **Reference Extraction Rate** | $k_{\text{ext,ref}}$ | $\text{min}^{-1}$ | $\text{LogNormal}(\ln(0.035), 0.3)$ | Calibrated |
| **Extraction Activation Energy** | $E_{\text{ext}}$ | $\text{J/mol}$ | $\text{Normal}(60000, 10000)$ | Calibrated |
| **Reference Hydrolysis Rate** | $k_{\text{hyd,ref}}$ | $\text{min}^{-1}$ | $\text{LogNormal}(\ln(0.015), 0.3)$ | Calibrated |
| **Hydrolysis Activation Energy** | $E_{\text{hyd}}$ | $\text{J/mol}$ | $\text{Normal}(85000, 12000)$ | Calibrated |
| **Reference Degradation Rate** | $k_{\text{deg,ref}}$ | $\text{min}^{-1}$ | $\text{LogNormal}(\ln(0.005), 0.4)$ | Calibrated |
| **Degradation Activation Energy**| $E_{\text{deg}}$ | $\text{J/mol}$ | $\text{Normal}(100000, 15000)$ | Calibrated |
| **Reference De-esterification Rate**| $k_{\text{de,ref}}$ | $\text{min}^{-1}$ | $\text{LogNormal}(\ln(0.012), 0.25)$ | Calibrated |
| **De-esterification Activation Energy**| $E_{\text{de}}$ | $\text{J/mol}$ | $\text{Normal}(50000, 8000)$ | Calibrated |
| **Particle Scaling Exponent** | $\alpha$ | $-$ | $\text{Normal}(1.0, 0.2)$ | Calibrated |
| **Fresh Matrix Accessibility** | $\Omega_{\text{fresh}}$ | $-$ | $\text{Normal}(1.35, 0.15)$ | Calibrated (Track B) |
| **Acoustic Coupling Efficiency** | $\eta_{\text{coupling}}$ | $-$ | $\text{Beta}(4.0, 12.0)$ | Calibrated (Track B) |
| **Sensible Thermal Fraction** | $\xi_{\text{thermal}}$ | $-$ | $\text{Normal}(0.88, 0.04)$ | Fixed / Calorimetric |
| **Cavitation Multiplier** | $\kappa_{US}$ | $\text{m}^3/\text{W}$ | $\text{LogNormal}(\ln(0.05), 0.5)$ | Calibrated (Track B) |
| **Cavitation Power Exponent** | $\beta_{US}$ | $-$ | $\text{Normal}(0.75, 0.15)$ | Calibrated (Track B) |
| **Frequency Exponent** | $\gamma_{US}$ | $-$ | $1.0$ | **Fixed Literature** |

### C. Posterior Sampling via NUTS
The posterior distribution is explored using Hamiltonian Monte Carlo (HMC) with the No-U-Turn Sampler (NUTS) across 4 chains $\times 2,000$ draws:
$$p(\theta \mid \mathcal{D}) \propto p(\theta) \prod_{j=1}^{N_{\text{runs}}} \prod_{k=1}^{N_{\text{samples}}} \mathcal{N}\left(\mathbf{y}_{j,k}^{\text{obs}} \;\Big|\; \mathbf{y}_{\text{model}}(t_{j,k}; \theta), \mathbf{\Sigma}_{\text{total}}\right)$$
Convergence criteria: $\hat{R} < 1.05$ and effective sample size $\text{ESS} > 400$ across all parameters.
