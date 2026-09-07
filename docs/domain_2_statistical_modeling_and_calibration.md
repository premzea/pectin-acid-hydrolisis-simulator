# Domain 2: Mathematical Modeling & Statistical Calibration Architecture

**Document Version**: 2.0  
**Parent Document**: [`MASTER_DUAL_TRACK_SPECIFICATION.md`](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/MASTER_DUAL_TRACK_SPECIFICATION.md)  
**Target Audience**: Bioprocess Modelers, Applied Mathematicians, Chemometricians, Bayesian Statisticians

---

## 1. Executive Scope

This document specifies the mathematical formulations, state-space representations, chemometric soft-sensor vector models, Fisher Information optimal experimental design (OED), and Bayesian parameter inference pipelines of the Pectin Digital Twin ecosystem.

The twin integrates:
1. A **4-pool mechanistic kinetic model** governing mass conservation and property moments.
2. An **at-line multi-wavelength chemometric soft sensor** mapping multi-channel spectrophotometric vectors directly to chemical concentrations ($C_{\text{GalA}}$, $C_{\text{pectin-equiv}}$).
3. A **Bayesian calibration engine** that infers reference Arrhenius rates, activation energies, particle accessibility scaling, and ultrasonic coupling parameters with full posterior uncertainty quantification.

---

## 2. The 4-Pool Mechanistic Mass-Transfer Model

### A. State Definitions & Mass Conservation
The extraction and depolymerization cascade is modeled across four distinct, mutually exclusive mass pools, normalized to dry feedstock mass $[\text{kg/kg}_{\text{dry,feed}}]$:

```text
  Protopectin in Plant Matrix (P_matrix)
                    │
                    │ k_ext (T, pH, d50, P_acoustic)
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

To stabilize non-linear numerical parameter inference, rate constants are parameterized relative to an uncoupled reference state ($T_{\text{ref}} = 353.15\text{ K} = 80^\circ\text{C}$, $\text{pH}_{\text{ref}} = 2.0$):

$$k_i(T, \text{pH}) = k_{i,\text{ref}} \exp\left[-\frac{E_i}{R}\left(\frac{1}{T_K} - \frac{1}{T_{\text{ref}}}\right)\right] 10^{n_i(\text{pH}_{\text{ref}} - \text{pH})}$$

### A. Granulometric Transport Scaling
$$\phi_d(d_{50}) = \left(\frac{d_{\text{ref}}}{d_{50}}\right)^\alpha \quad (d_{\text{ref}} = 300\,\mu\text{m})$$

### B. Phenomenological Ultrasound Cavitation Enhancement
In Track B, acoustic cavitation intensifies cell rupture and micro-mixing:
$$P_{\text{acoustic}} = \eta_{\text{coupling}} \cdot P_{\text{elec}}$$
$$\psi_{US} = 1.0 + \kappa_{US} \left(\frac{P_{\text{acoustic}}}{V_{\text{slurry}}}\right)^{\beta_{US}} \left(\frac{40\text{ kHz}}{f_{US}}\right)^{\gamma_{US}}$$
$$k_{\text{ext,effective}} = k_{\text{ext,chem}}(T, \text{pH}) \cdot \phi_d(d_{50}) \cdot \psi_{US}(P_{\text{acoustic}})$$

---

## 5. At-Line Multi-Channel Vector Soft Sensor

Rather than interpolating to an unmeasured synthetic wavelength (e.g. $530\text{ nm}$), the soft sensor models the multi-wavelength detector response of the **IO Rodeo 8-Channel Multichannel Colorimeter**:
$$\mathbf{A} = [A_{415}, A_{445}, A_{480}, A_{515}, A_{555}, A_{590}, A_{630}, A_{680}]^T$$

```text
  Raw 8-Channel Vector A
            │
            ▼
  Turbidity & Baseline Subtraction (A_680)
            │
  ┌─────────┴─────────────────────────────────┐
  ▼                                           ▼
Carbazole Feature Bracket                Copper-Chelate Band
[A_515, A_555, A_680]                           [A_590]
  │                                           │
  ▼                                           ▼
Multi-Wavelength Vector Regression       Single-Channel Inversion
C_GalA = a*A_515 + b*A_555 + c*A_680 + d C_pectin-eq = (A_590 - A_0) / S
  │                                           │
  └─────────────────────┬─────────────────────┘
                        ▼
             Dynamic Range Check:
           C_measured in [C_min, C_max]
                        │
                        ▼
             Dilution Factor Scaling:
               C_sample = C_measured * DF
```

### A. GalA Multi-Wavelength Vector Regression
The carbazole-galacturonic acid chromophore spans a broad visible absorption envelope with peak absorption near $530\text{ nm}$. The IO Rodeo colorimeter brackets this band with its $515\text{ nm}$ and $555\text{ nm}$ bandpass filters. Optical turbidity and scattering from colloidal particles are anchored at $680\text{ nm}$:

$$C_{\text{GalA,measured}} = \mathbf{w}^T \mathbf{A}_{\text{sub}} + d = w_1 A_{515} + w_2 A_{555} + w_3 A_{680} + d$$

### B. Copper-Chelate Pectin-Equivalent Model
For the copper-chelate assay, intact pectin coordination absorbs strongly in the yellow-orange band ($590\text{ nm}$):
$$C_{\text{pectin-equiv,measured}} = \frac{A_{590} - A_{0,\text{Cu}}}{S_{\text{Cu}}}$$

### C. Sample Scaling & Dynamic Range Control
$$C_{\text{sample}} = C_{\text{measured}} \times DF$$

Every calibration object defines its verified linear domain:
$$\mathcal{D}_{\text{cal}} = [C_{\text{linear,min}}, C_{\text{linear,max}}]$$
* **Range Diagnostic Function**:
  $$\text{Flag}(C_{\text{meas}}) = \begin{cases} \text{VALID}, & C_{\text{linear,min}} \le C_{\text{meas}} \le C_{\text{linear,max}} \\ \text{LOW\_SIGNAL}, & C_{\text{meas}} < C_{\text{linear,min}} \\ \text{SATURATION\_WARNING}, & C_{\text{meas}} > C_{\text{linear,max}} \implies \text{Dilute by } \left\lceil\frac{C_{\text{meas}}}{0.5 \cdot C_{\text{linear,max}}}\right\rceil \end{cases}$$

---

## 6. Optimal Experimental Design (OED) & Structural Identifiability

### A. Fisher Information Matrix (FIM)
For an experimental design $\xi = \{(T_j, \text{pH}_j, d_{50,j}, t_{j,k})\}$, the Fisher Information Matrix is:
$$\mathbf{F}(\theta) = \sum_{j=1}^{N_{\text{runs}}} \sum_{k=1}^{N_{\text{samples}}} \mathbf{S}_{j,k}^T \mathbf{\Sigma}_{\text{obs}}^{-1} \mathbf{S}_{j,k}$$
where $\mathbf{S}_{j,k} = \frac{\partial \mathbf{y}(t_{j,k}; \theta)}{\partial \theta}$ is the sensitivity matrix evaluated at prior nominal parameters $\theta_0$, and $\mathbf{\Sigma}_{\text{obs}} = \text{diag}(\sigma_{Y}^2, \sigma_{DE}^2, \sigma_{Mw}^2, \sigma_{\text{GalA}}^2)$.

### B. D-Optimality Criterion & Condition Number
The experimental space is optimized to maximize parameter volume:
$$\xi^* = \arg\max_\xi \det(\mathbf{F}(\theta))$$
Design ill-conditioning is evaluated via the eigenvalue spectrum:
$$\kappa(\mathbf{F}) = \frac{\lambda_{\max}(\mathbf{F})}{\lambda_{\min}(\mathbf{F})}$$

### C. Breaking the $k_{\text{hyd}} \leftrightarrow k_{\text{deg}}$ Structural Anti-Correlation
In single-endpoint experiments, the intermediate low-MW pectin pool cannot be separated from unrecoverable degradation products, resulting in a severe structural anti-correlation:
$$\text{Corr}(k_{\text{hyd}}, k_{\text{deg}}) = -0.85, \quad \text{Corr}(E_{\text{hyd}}, E_{\text{deg}}) = -0.85$$

Track A eliminates this ambiguity by enforcing **time-resolved multi-observable sampling**:
* **Early time ($t = 15\text{ min}$)**: Dominant $k_{\text{ext}}$ and $M_{w,\text{matrix}}$ solubilization.
* **Intermediate time ($t = 45\text{ min}$)**: Hydrolysis chain scission without extensive degradation.
* **Late time ($t = 90, 120\text{ min}$)**: Thermal degradation and terminal loss.
Re-computing the FIM over the time-resolved 10-run protocol compresses the condition number from $\kappa = 52.0$ down to $\kappa = 27.0$.

### D. Decoupling Acoustic Cavitation from Sensible Heating
In Track B, ultrasound produces simultaneous mechanical cavitation and thermal acoustic dissipation ($Q_{US} = P_{\text{acoustic}}$). To isolate the kinetic cavitation multiplier $\psi_{US}$:
$$\Delta Y_{\text{UAE}}(T) = Y_{\text{UAE}}(T, P_{\text{elec}}) - Y_{\text{thermal}}(T, P_{\text{elec}} = 0)$$
By conducting paired runs at matched internal slurry temperatures, the Bayesian likelihood uniquely isolates $\kappa_{US}$ from $E_{\text{ext}}$.

---

## 7. Bayesian Parameter Estimation Architecture

### A. Parameter Ontology & Prior Distributions

| Parameter | Symbol | Units | Prior Distribution $p(\theta)$ | Physical Interpretation |
| :--- | :---: | :---: | :--- | :--- |
| **Reference Extraction Rate** | $k_{\text{ext,ref}}$ | $\text{min}^{-1}$ | $\text{LogNormal}(\ln(0.035), 0.3)$ | Solubilization at 80 °C, pH 2.0 |
| **Extraction Activation Energy** | $E_{\text{ext}}$ | $\text{J/mol}$ | $\text{Normal}(60000, 10000)$ | Temperature sensitivity of extraction |
| **Reference Hydrolysis Rate** | $k_{\text{hyd,ref}}$ | $\text{min}^{-1}$ | $\text{LogNormal}(\ln(0.015), 0.3)$ | Chain scission at 80 °C, pH 2.0 |
| **Hydrolysis Activation Energy** | $E_{\text{hyd}}$ | $\text{J/mol}$ | $\text{Normal}(85000, 12000)$ | Temperature sensitivity of hydrolysis |
| **Reference Degradation Rate** | $k_{\text{deg,ref}}$ | $\text{min}^{-1}$ | $\text{LogNormal}(\ln(0.005), 0.4)$ | Monomer degradation at 80 °C, pH 2.0 |
| **Degradation Activation Energy**| $E_{\text{deg}}$ | $\text{J/mol}$ | $\text{Normal}(100000, 15000)$ | Temperature sensitivity of degradation |
| **Reference De-esterification Rate**| $k_{\text{de,ref}}$ | $\text{min}^{-1}$ | $\text{LogNormal}(\ln(0.012), 0.25)$ | Saponification rate at 80 °C, pH 2.0 |
| **De-esterification Activation Energy**| $E_{\text{de}}$ | $\text{J/mol}$ | $\text{Normal}(50000, 8000)$ | Temperature sensitivity of de-esterification |
| **Particle Scaling Exponent** | $\alpha$ | $-$ | $\text{Normal}(1.0, 0.2)$ | Boundary layer accessibility scaling |
| **Acoustic Coupling Efficiency** | $\eta_{\text{coupling}}$ | $-$ | $\text{Beta}(4.0, 12.0)$ | Calorimetric transfer efficiency ($15\text{--}35\%$) |
| **Cavitation Multiplier** | $\kappa_{US}$ | $\text{m}^3/\text{W}$ | $\text{LogNormal}(\ln(0.05), 0.5)$ | Kinetic acceleration per acoustic watt |

### B. Bayesian Posterior Likelihood Formulation
Given physical experimental observations $\mathcal{D} = \{(\mathbf{y}_{j,k}^{\text{obs}}, \mathbf{\Sigma}_{j,k})\}$, the posterior probability density is:
$$p(\theta \mid \mathcal{D}) \propto p(\theta) \prod_{j=1}^{N_{\text{runs}}} \prod_{k=1}^{N_{\text{samples}}} \mathcal{N}\left(\mathbf{y}_{j,k}^{\text{obs}} \;\Big|\; \mathbf{y}_{\text{model}}(t_{j,k}; \theta), \mathbf{\Sigma}_{j,k}\right)$$

Sampling is executed using Hamiltonian Monte Carlo (HMC) with the No-U-Turn Sampler (NUTS), generating 4 parallel chains of 2,000 warm-up and 2,000 posterior iterations.

### C. Posterior Predictive Consistency (PPC)
Model validity is confirmed when independently held-out validation experiments (Runs 11–13) satisfy:
$$\mathbf{y}_{\text{validation}}^{\text{obs}} \in \text{BCI}_{95\%}\left(p(\mathbf{y}_{\text{pred}} \mid \mathcal{D})\right)$$
where $\text{BCI}_{95\%}$ is the $95\%$ Bayesian Credible Interval of the posterior predictive distribution.
