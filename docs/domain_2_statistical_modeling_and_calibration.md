# Domain 2: Mathematical Modeling & Statistical Calibration Architecture

**Document Version**: 2.2 (Incorporating Epistemological & Phased Review)  
**Parent Document**: [`MASTER_DUAL_TRACK_SPECIFICATION.md`](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/MASTER_DUAL_TRACK_SPECIFICATION.md)  
**Target Audience**: Bioprocess Modelers, Applied Mathematicians, Chemometricians, Bayesian Statisticians

---

## 1. Executive Scope & Unified Modeling Paradigm

The digital twin conceptualizes pectin extraction as a **single shared chemical reaction cascade** acted upon by **track-specific physical accessibility operators**:

$$\boxed{
\text{Feedstock}
\xrightarrow{\text{Accessibility Operator } \phi_{d,\text{eff}}}
\text{P}_{\text{matrix}}
\xrightarrow{k_{\text{ext}}}
\text{P}_{\text{sol}}
\xrightarrow{k_{\text{hyd}}}
\text{P}_{\text{lowMW}}
\xrightarrow{k_{\text{deg}}}
\text{P}_{\text{loss}}
\xrightarrow{\text{Recovery}}
\text{Recovered Product}
}$$

* **Track A Role**: Identifies the **intrinsic chemical kinetics** ($k_{\text{ext}}, k_{\text{hyd}}, k_{\text{deg}}, k_{\text{de}}$, $DE$, $M_w$) on standardized dried tissue under controlled thermal conditions.
* **Track B Role**: Identifies the **physical transport and tissue accessibility operators** (fresh un-collapsed parenchyma factor $\Omega_{\text{fresh}}$ and acoustic cavitation enhancement $\psi_{US}$) using matched fresh-tissue thermal controls.

---

## 2. Epistemological Parameter Ontology

To prevent unverified hypotheses from masquerading as calibrated parameters, every model variable is classified into one of four distinct epistemic categories:

| Parameter | Symbol | Units | Epistemic Status | Governing Protocol / Prior |
| :--- | :---: | :---: | :--- | :--- |
| **Slurry Temperature** | $T(t)$ | °C | **Directly Measured** | Calibrated PT100 RTD logging ($\ge 0.1\text{ Hz}$) |
| **Reaction Acidity** | $\text{pH}(t)$ | $-$ | **Directly Measured** | Autoclavable glass combination electrode |
| **Precipitated Dry Solids** | $m_{\text{dry\_precipitate}}$ | g | **Directly Measured** | Analytical balance ($\pm 0.1\text{ mg}$) after vacuum drying |
| **Detector Absorbance Vector**| $\mathbf{A}(\lambda)$ | AU | **Directly Measured** | IO Rodeo 8-channel spectrophotometer |
| **Reference Temperature** | $T_{\text{ref}}$ | K | **Standardized by Design** | Fixed at $353.15\text{ K} = 80.0^\circ\text{C}$ |
| **Reference Acidity** | $\text{pH}_{\text{ref}}$ | $-$ | **Standardized by Design** | Fixed at $2.00$ |
| **Reference Particle Diameter**| $d_{\text{ref}}$ | $\mu$m | **Standardized by Design** | Fixed at $300\,\mu\text{m}$ (ASTM 50 mesh) |
| **US Frequency Exponent** | $\gamma_{US}$ | $-$ | **Standardized by Design** | Fixed at $1.0$ (Single-frequency 40 kHz constraint) |
| **Reference Extraction Rate** | $k_{\text{ext,ref}}$ | $\text{min}^{-1}$ | **Calibrated Parameter** | Prior: $\text{LogNormal}(\ln(0.035), 0.3)$ |
| **Extraction Activation Energy** | $E_{\text{ext}}$ | $\text{J/mol}$ | **Calibrated Parameter** | Prior: $\text{Normal}(60000, 10000)$ |
| **Reference Hydrolysis Rate** | $k_{\text{hyd,ref}}$ | $\text{min}^{-1}$ | **Calibrated Parameter** | Prior: $\text{LogNormal}(\ln(0.015), 0.3)$ |
| **Hydrolysis Activation Energy** | $E_{\text{hyd}}$ | $\text{J/mol}$ | **Calibrated Parameter** | Prior: $\text{Normal}(85000, 12000)$ |
| **Reference Degradation Rate** | $k_{\text{deg,ref}}$ | $\text{min}^{-1}$ | **Calibrated Parameter** | Prior: $\text{LogNormal}(\ln(0.005), 0.4)$ |
| **Degradation Activation Energy**| $E_{\text{deg}}$ | $\text{J/mol}$ | **Calibrated Parameter** | Prior: $\text{Normal}(100000, 15000)$ |
| **Particle Scaling Exponent** | $\alpha$ | $-$ | **Calibrated Parameter** | Prior: $\text{Normal}(1.0, 0.2)$ |
| **Fresh Matrix Accessibility** | $\Omega_{\text{fresh}}$ | $-$ | **Hypothesis / Latent Estimand**| Prior: $\text{Normal}(1.35, 0.25)$ (Identified via Track B Controls) |
| **Acoustic Power Delivered** | $P_{\text{acoustic}}$ | W | **Directly Measured (Calorimetry)**| Water solvent calorimetry ($m C_p dT/dt$) |
| **Acoustic Energy Partition** | $P_{\text{therm}} / P_{\text{mech}}$ | $-$ | **Latent / Structurally Unidentified**| Left unpartitioned; model infers net enhancement $\psi_{US}$ |
| **Cavitation Multiplier** | $\kappa_{US}$ | $\text{m}^3/\text{W}$ | **Calibrated Parameter** | Prior: $\text{LogNormal}(\ln(0.05), 0.5)$ |
| **Cavitation Power Exponent** | $\beta_{US}$ | $-$ | **Calibrated Parameter** | Prior: $\text{Normal}(0.75, 0.15)$ |

---

## 3. Mechanistic 4-Pool Mass ODEs & Property Moments

### A. Normalized Mass Conservation
$$\frac{dP_{\text{matrix}}}{dt} = -k_{\text{ext}} P_{\text{matrix}}$$
$$\frac{dP_{\text{sol}}}{dt} = k_{\text{ext}} P_{\text{matrix}} - k_{\text{hyd}} P_{\text{sol}}$$
$$\frac{dP_{\text{lowMW}}}{dt} = k_{\text{hyd}} P_{\text{sol}} - k_{\text{deg}} P_{\text{lowMW}}$$
$$\frac{dP_{\text{loss}}}{dt} = k_{\text{deg}} P_{\text{lowMW}}$$

Invariant: $\sum_{i} P_i(t) \equiv P_{\text{matrix},0}, \quad \epsilon_M < 10^{-10}$.

### B. Cohort-Correct Moments
* **De-esterification Moments**:
  $$\frac{dQ_{DE,\text{sol}}}{dt} = k_{\text{ext}} P_{\text{matrix}} DE_{\text{matrix}} - k_{\text{de}} Q_{DE,\text{sol}} - k_{\text{hyd}} Q_{DE,\text{sol}}$$
  $$\frac{dQ_{DE,\text{lowMW}}}{dt} = k_{\text{hyd}} Q_{DE,\text{sol}} - k_{\text{de}} Q_{DE,\text{lowMW}} - k_{\text{deg}} Q_{DE,\text{lowMW}}$$
  $$DE_{\text{sol}}(t) = \frac{Q_{DE,\text{sol}}(t)}{P_{\text{sol}}(t)}$$
* **Molecular Weight Moments**:
  $$\frac{dQ_{MW,\text{sol}}}{dt} = k_{\text{ext}} P_{\text{matrix}} M_{w,\text{matrix}} - k_{\text{hyd}} Q_{MW,\text{sol}} - \beta_{MW} k_{\text{hyd}} (Q_{MW,\text{sol}} - M_{w,\text{min}} P_{\text{sol}})$$
  $$M_{w,\text{sol}}(t) = \frac{Q_{MW,\text{sol}}(t)}{P_{\text{sol}}(t)}$$
* **GalA Inventory**:
  $$\frac{dG_{\text{sol}}}{dt} = k_{\text{ext}} P_{\text{matrix}} X_{\text{GalA,matrix}} - k_{\text{hyd}} G_{\text{sol}}$$
  $$X_{\text{GalA,sol}}(t) = \frac{G_{\text{sol}}(t)}{P_{\text{sol}}(t)}$$

---

## 4. Physical Accessibility Operators & Ultrasound Modeling

$$k_{\text{ext,effective}} = k_{\text{ext,chem}}(T, \text{pH}) \cdot \phi_{d,\text{eff}}(d_{50}) \cdot \psi_{US}(P_{\text{acoustic}})$$

### A. Tissue Accessibility Operator ($\phi_{d,\text{eff}}$)
$$\phi_{d,\text{eff}} = \left(\frac{d_{\text{ref}}}{d_{50}}\right)^\alpha \cdot \Omega_{\text{matrix}}$$
* $\Omega_{\text{matrix}} \equiv 1.0$ for standardized dried and sieved powder (Track A).
* $\Omega_{\text{fresh}}$ captures cell wall un-collapsed porosity in raw tissue, identified by comparing fresh thermal baseline runs ($P_{\text{elec}}=0$) with Track A dried runs.

### B. Acoustic Enhancement Operator ($\psi_{US}$)
$$\psi_{US} = 1.0 + \kappa_{US} \left(\frac{P_{\text{acoustic}}}{V_{\text{slurry}}}\right)^{\beta_{US}} \left(\frac{40\text{ kHz}}{f_{US}}\right)^{1.0}$$
* *Unpartitioned Cavitation Formulation*: Rather than guessing a sensible heat split, the twin uses the actual slurry temperature trajectory $T_{\text{slurry}}(t)$ to compute $k_{\text{ext,chem}}(T, \text{pH})$. Any additional extraction rate observed during active sonication is attributed directly to $\psi_{US}$.

---

## 5. At-Line Multi-Channel Chemometric Models

IO Rodeo 8-channel array: $\mathbf{A} = [A_{415}, A_{445}, A_{480}, A_{515}, A_{555}, A_{590}, A_{630}, A_{680}]^T$.

### A. Sample-Blank Subtraction
$$\mathbf{A}_{\text{net}}(\lambda) = \mathbf{A}_{\text{developed}}(\lambda) - \mathbf{A}_{\text{sample\_blank}}(\lambda) - A_{\text{turbidity}}(680) \left(\frac{680}{\lambda}\right)^{\alpha_{\text{Rayleigh}}}$$

### B. Concentration Estimators
* **GalA Multi-Wavelength Model**:
  $$C_{\text{GalA,measured}} = w_1 A_{\text{net}}(515) + w_2 A_{\text{net}}(555) + w_3 A_{\text{net}}(680) + d$$
  $$C_{\text{GalA,sample}} = C_{\text{GalA,measured}} \times DF$$
* **Copper-Chelate Pectin-Equivalent Model**:
  $$C_{\text{pectin-equiv,measured}} = \frac{A_{\text{net}}(590) - A_{0,\text{Cu}}}{S_{\text{Cu}}}$$
* **Composition / Purity Proxy**:
  $$I_{\text{GalA}} = \frac{m_{\text{GalA,total}}}{m_{\text{dry\_precipitate,scaled}}}$$

---

## 6. Stage-Gated Experimental & Calibration Hierarchy

To avoid over-engineering software before physical reality is proven, the calibration architecture is strictly stage-gated:

```text
Phase 0: Physical Repeatability Gate (CV_gravimetric < 4%, CV_col < 1.5%)
                            │
                            ▼
Phase 1: Analytical Triangle Backbone (Gravimetric + GalA + Pectin-Eq + Spikes)
                            │
                            ▼
Phase 2: Track A Mechanistic Core (12-run OED -> k_ext, k_hyd, k_deg, DE, Mw)
                            │
                            ▼
Phase 3: Track B Net Enhancement (10-run UAE OED with Fresh Thermal Baselines)
                            │
                            ▼
Phase 4: At-Line Soft-Sensor Online Deployment (Automated UI Inferences)
```

### Phase 1: The Analytical Triangle
Validates the internal consistency of the three primary observables before fitting kinetics:
$$\boxed{\text{Gravimetric Recovery } (m_{\text{dry\_precipitate}}) \longleftrightarrow \text{GalA Concentration } (C_{\text{GalA}}) \longleftrightarrow \text{Pectin-Equivalent } (C_{\text{pectin-equiv}})}$$
* Evaluates matrix spike recoveries ($95\%\text{--}105\%$).
* Correlates $C_{\text{pectin-equiv}}$ against gravimetric recovery across a preliminary 5-point dilution series.

### Phase 2: Track A 12-Run Mechanistic OED Campaign
* Executes the 12-run matrix (with $70^\circ\text{C}$ curvature anchor and center replicates A-10a/b).
* Calibrates $k_{\text{ext,ref}}, E_{\text{ext}}, k_{\text{hyd,ref}}, E_{\text{hyd}}, k_{\text{deg,ref}}, E_{\text{deg}}, k_{\text{de,ref}}, E_{\text{de}}, \alpha$.
* Estimates process execution variance $\mathbf{\Sigma}_{\text{process}}$ from replicate runs.

### Phase 3: Track B 10-Run UAE OED Campaign
* Runs paired fresh-rind thermal baselines (Runs B-1 & B-2 at $P_{\text{elec}} = 0\text{ W}$) to identify $\Omega_{\text{fresh}}$.
* Runs active sonication matrix ($100\text{--}300\text{ W}$, $40\text{--}70^\circ\text{C}$) to identify $\kappa_{US}$ and $\beta_{US}$.
* Evaluates acoustic enhancement:
  $$\Delta Y_{\text{UAE}} = Y_{\text{UAE,fresh}}(T, P_{\text{elec}}) - Y_{\text{thermal,fresh}}(T, 0)$$

---

## 7. Two-Tier Bayesian Likelihood Model

$$\mathbf{\Sigma}_{\text{total}} = \mathbf{\Sigma}_{\text{obs}} + \mathbf{\Sigma}_{\text{process}}$$

$$p(\theta \mid \mathcal{D}) \propto p(\theta) \prod_{j=1}^{N_{\text{runs}}} \prod_{k=1}^{N_{\text{samples}}} \mathcal{N}\left(\mathbf{y}_{j,k}^{\text{obs}} \;\Big|\; \mathbf{y}_{\text{model}}(t_{j,k}; \theta), \mathbf{\Sigma}_{\text{total}}\right)$$

* Sampled via Hamiltonian Monte Carlo (NUTS) across 4 chains of 2,000 warm-up and 2,000 posterior iterations.
* Convergence target: Gelman-Rubin diagnostic $\hat{R} < 1.05$ across all calibrated parameters.
