# Domain 2: Mathematical Modeling & Statistical Calibration Architecture

**Document Version**: 3.0 (Unified Fresh-Rind Feedstock Architecture)  
**Parent Document**: [`MASTER_DUAL_TRACK_SPECIFICATION.md`](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/MASTER_DUAL_TRACK_SPECIFICATION.md)  
**Target Audience**: Bioprocess Modelers, Applied Mathematicians, Chemometricians, Bayesian Statisticians

---

## 1. Unified Modeling Paradigm: Shared Fresh-Rind Cascade

The digital twin models pectin extraction as a **single shared chemical reaction cascade** occurring within the **native fresh pericarp tissue**, acted upon by track-specific physical driving forces:

$$\boxed{
\text{Fresh Feedstock}
\xrightarrow{\text{Accessibility } \phi_{\text{feed}}(d_{50})}
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

* **Track A Role**: Identifies the **intrinsic chemical kinetics** ($k_{\text{ext}}, k_{\text{hyd}}, k_{\text{deg}}, k_{\text{de}}$, $DE$, $M_w$) on native fresh tissue under controlled stirred thermal conditions.
* **Track B Role**: Identifies the **acoustic cavitation enhancement operator** ($\psi_{US}(P_{\text{acoustic}})$) against the matched fresh thermal control:
  $$\Delta Y_{\text{US}} = Y_{\text{fresh,UAE}}(T, P_{\text{elec}}) - Y_{\text{fresh,thermal}}(T, P_{\text{elec}} = 0)$$

*Elimination of $\Omega_{\text{matrix}}$*: Because both tracks consume identical fresh food-processed rind, the cross-track matrix factor is **deleted from V1**. Both tracks share the identical biological starting state.

---

## 2. Epistemological Parameter Ontology (v3.0)

| Parameter | Symbol | Units | Epistemic Status | Governing Protocol / Prior |
| :--- | :---: | :---: | :--- | :--- |
| **Slurry Temperature** | $T(t)$ | °C | **Directly Measured** | Calibrated PT100 RTD logging ($\ge 0.1\text{ Hz}$) |
| **Reaction Acidity** | $\text{pH}(t)$ | $-$ | **Directly Measured** | Autoclavable glass combination electrode |
| **Batch Moisture Fraction** | $X_{w,0}$ | $-$ | **Directly Measured** | Halogen moisture analyzer ($105^\circ\text{C}$ per batch) |
| **Precipitated Dry Solids** | $m_{\text{dry\_precipitate}}$ | g | **Directly Measured** | Analytical balance ($\pm 0.1\text{ mg}$) after vacuum drying |
| **Detector Absorbance Vector**| $\mathbf{A}(\lambda)$ | AU | **Directly Measured** | IO Rodeo 8-channel spectrophotometer |
| **Reference Temperature** | $T_{\text{ref}}$ | K | **Standardized by Design** | Fixed at $353.15\text{ K} = 80.0^\circ\text{C}$ |
| **Reference Acidity** | $\text{pH}_{\text{ref}}$ | $-$ | **Standardized by Design** | Fixed at $2.00$ |
| **Reference Fragment Size** | $d_{\text{ref}}$ | $\mu$m | **Standardized by Design** | Fixed at $1000\,\mu\text{m}$ (fresh shredding reference) |
| **US Frequency Exponent** | $\gamma_{US}$ | $-$ | **Standardized by Design** | Fixed at $1.0$ (Single-frequency 40 kHz constraint) |
| **Reference Extraction Rate** | $k_{\text{ext,ref}}$ | $\text{min}^{-1}$ | **Calibrated Parameter** | Prior: $\text{LogNormal}(\ln(0.035), 0.3)$ |
| **Extraction Activation Energy** | $E_{\text{ext}}$ | $\text{J/mol}$ | **Calibrated Parameter** | Prior: $\text{Normal}(60000, 10000)$ |
| **Reference Hydrolysis Rate** | $k_{\text{hyd,ref}}$ | $\text{min}^{-1}$ | **Calibrated Parameter** | Prior: $\text{LogNormal}(\ln(0.015), 0.3)$ |
| **Hydrolysis Activation Energy** | $E_{\text{hyd}}$ | $\text{J/mol}$ | **Calibrated Parameter** | Prior: $\text{Normal}(85000, 12000)$ |
| **Reference Degradation Rate** | $k_{\text{deg,ref}}$ | $\text{min}^{-1}$ | **Calibrated Parameter** | Prior: $\text{LogNormal}(\ln(0.005), 0.4)$ |
| **Degradation Activation Energy**| $E_{\text{deg}}$ | $\text{J/mol}$ | **Calibrated Parameter** | Prior: $\text{Normal}(100000, 15000)$ |
| **Particle Scaling Exponent** | $\alpha$ | $-$ | **Calibrated Parameter** | Prior: $\text{Normal}(1.0, 0.2)$ |
| **Acoustic Power Delivered** | $P_{\text{acoustic}}$ | W | **Directly Measured (Calorimetry)**| Water solvent calorimetry ($m C_p dT/dt$) |
| **Acoustic Energy Partition** | $P_{\text{therm}} / P_{\text{mech}}$ | $-$ | **Latent / Structurally Unidentified**| Left unpartitioned; model infers net enhancement $\psi_{US}$ |
| **Cavitation Multiplier** | $\kappa_{US}$ | $\text{m}^3/\text{W}$ | **Calibrated Parameter** | Prior: $\text{LogNormal}(\ln(0.05), 0.5)$ |
| **Cavitation Power Exponent** | $\beta_{US}$ | $-$ | **Calibrated Parameter** | Prior: $\text{Normal}(0.75, 0.15)$ |

---

## 3. Mechanistic 4-Pool Mass ODEs & Property Moments

### A. Normalized Mass Conservation
Mass pools are normalized to dry feedstock mass $[\text{kg/kg}_{\text{dry,feed}}]$ where $m_{\text{dry}} = m_{\text{fresh}} \cdot (1 - X_{w,0})$:
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

## 4. Physical Transport & Kinetics Modifiers

$$k_{\text{ext,effective}} = k_{\text{ext,chem}}(T, \text{pH}) \cdot \phi_{\text{feed}}(d_{50}) \cdot \psi_{US}(P_{\text{acoustic}})$$

### A. Fresh Tissue Comminution Modifier ($\phi_{\text{feed}}$)
$$\phi_{\text{feed}}(d_{50}) = \left(\frac{d_{\text{ref}}}{d_{50}}\right)^\alpha \quad (d_{\text{ref}} = 1000\,\mu\text{m})$$
Identical across Track A and Track B.

### B. Acoustic Cavitation Modifier ($\psi_{US}$)
$$\psi_{US} = 1.0 + \kappa_{US} \left(\frac{P_{\text{acoustic}}}{V_{\text{slurry}}}\right)^{\beta_{US}} \left(\frac{40\text{ kHz}}{f_{US}}\right)^{1.0}$$
* Track A: $P_{\text{acoustic}} \equiv 0 \implies \psi_{US} \equiv 1.0$.
* Track B Control: $P_{\text{acoustic}} \equiv 0 \implies \psi_{US} \equiv 1.0$ (Matched fresh thermal baseline).
* Track B Active Sonication: $\psi_{US} > 1.0$ (Captures pure incremental cavitation benefit).

---

## 5. The Shared Analytical Triangle

Both Track A and Track B feed the **identical analytical triangle**:

$$\boxed{
\text{Gravimetric Recovery } (m_{\text{dry\_precipitate}})
\longleftrightarrow
\text{GalA Concentration } (C_{\text{GalA}})
\longleftrightarrow
\text{Pectin-Equivalent } (C_{\text{pectin-equiv}})
}$$

1. **Sample-Blank Net Absorbance Vector**:
   $$\mathbf{A}_{\text{net}}(\lambda) = \mathbf{A}_{\text{developed}}(\lambda) - \mathbf{A}_{\text{sample\_blank}}(\lambda) - A_{\text{turbidity}}(680) \left(\frac{680}{\lambda}\right)^{\alpha_{\text{Rayleigh}}}$$
2. **GalA Multi-Wavelength Model**:
   $$C_{\text{GalA,measured}} = w_1 A_{\text{net}}(515) + w_2 A_{\text{net}}(555) + w_3 A_{\text{net}}(680) + d$$
   $$C_{\text{GalA,sample}} = C_{\text{GalA,measured}} \times DF$$
3. **Copper-Chelate Pectin-Equivalent Model**:
   $$C_{\text{pectin-equiv,measured}} = \frac{A_{\text{net}}(590) - A_{0,\text{Cu}}}{S_{\text{Cu}}}$$
4. **GalA Composition / Purity Proxy**:
   $$I_{\text{GalA}} = \frac{m_{\text{GalA,total}}}{m_{\text{dry\_precipitate,scaled}}}$$

---

## 6. Stage-Gated Experimental & Calibration Hierarchy

```text
Phase 0: Physical Repeatability Gate (CV_gravimetric < 4%, CV_col < 1.5%)
                            │
                            ▼
Phase 1: Analytical Triangle Backbone (Gravimetric + GalA + Pectin-Eq + Spikes)
                            │
                            ▼
Phase 2: Track A Thermal Mechanistic Core (12 runs on Fresh Rind -> k_ext, k_hyd, k_deg)
                            │
                            ▼
Phase 3: Track B Net Enhancement (10 runs on Same Fresh Rind with P_elec = 0 Controls)
                            │
                            ▼
Phase 4: At-Line Soft-Sensor Online Deployment (Automated UI Inferences)
```

---

## 7. Two-Tier Bayesian Likelihood Model

$$\mathbf{\Sigma}_{\text{total}} = \mathbf{\Sigma}_{\text{obs}} + \mathbf{\Sigma}_{\text{process}}$$

$$p(\theta \mid \mathcal{D}) \propto p(\theta) \prod_{j=1}^{N_{\text{runs}}} \prod_{k=1}^{N_{\text{samples}}} \mathcal{N}\left(\mathbf{y}_{j,k}^{\text{obs}} \;\Big|\; \mathbf{y}_{\text{model}}(t_{j,k}; \theta), \mathbf{\Sigma}_{\text{total}}\right)$$

* Sampled via Hamiltonian Monte Carlo (NUTS) across 4 chains of 2,000 warm-up and 2,000 posterior iterations.
* True process variance $\mathbf{\Sigma}_{\text{process}}$ is isolated directly from center-point replicate runs (A-10a/b and B-4a/b).
