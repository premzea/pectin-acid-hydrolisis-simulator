# Domain 2: Mathematical Modeling & Statistical Calibration Architecture

**Document Version**: 3.1 (Ultrasound-Assisted Acid Extraction Framing)  
**Parent Document**: [`MASTER_DUAL_TRACK_SPECIFICATION.md`](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/MASTER_DUAL_TRACK_SPECIFICATION.md)  
**Target Audience**: Bioprocess Modelers, Applied Mathematicians, Chemometricians, Bayesian Statisticians

---

## 1. Unified Modeling Paradigm: Shared Acid-Catalyzed Cascade

The digital twin models pectin extraction as a **single shared acid-catalyzed depolymerization cascade**, wherein ultrasound acts as an external physical driving force modifying both mass transfer and polymer degradation:

$$\boxed{
\text{Fresh Feedstock}
\xrightarrow{\phi_{\text{feed}}(d_{50})}
\text{P}_{\text{matrix}}
\xrightarrow{k_{\text{ext}}(T, \text{pH}, P_{\text{US}})}
\text{P}_{\text{sol}}
\xrightarrow{k_{\text{hyd}}(T, \text{pH}, P_{\text{US}})}
\text{P}_{\text{lowMW}}
\xrightarrow{k_{\text{deg}}(T, \text{pH}, P_{\text{US}})}
\text{P}_{\text{loss}}
\xrightarrow{\text{Recovery}}
\text{Recovered Product}
}$$

### Dual-Action Ultrasound Formulation
Cavitation microjets accelerate solid-liquid mass transfer, while acoustic shear forces accelerate chain depolymerization:
1. **Solubilization Rate**:
   $$k_{\text{ext}}^{\text{US}} = k_{\text{ext}}^{\text{thermal}}(T, \text{pH}) \cdot \phi_{\text{feed}}(d_{50}) \cdot \left[1 + \kappa_{\text{ext}} \left(\frac{P_{\text{acoustic}}}{V_{\text{slurry}}}\right)^{\beta_{\text{ext}}}\right]$$
2. **Hydrolysis / Chain Scission Rate**:
   $$k_{\text{hyd}}^{\text{US}} = k_{\text{hyd}}^{\text{thermal}}(T, \text{pH}) \cdot \left[1 + \kappa_{\text{hyd}} \left(\frac{P_{\text{acoustic}}}{V_{\text{slurry}}}\right)^{\beta_{\text{hyd}}}\right]$$
3. **Monomer Degradation Rate**:
   $$k_{\text{deg}}^{\text{US}} = k_{\text{deg}}^{\text{thermal}}(T, \text{pH}) \cdot \left[1 + \kappa_{\text{deg}} \left(\frac{P_{\text{acoustic}}}{V_{\text{slurry}}}\right)^{\beta_{\text{deg}}}\right]$$

*Identifiability Strategy*:
* In **Track A** (and Track B controls where $P_{\text{acoustic}} \equiv 0$), all acoustic multipliers $\kappa_i \equiv 0$. This identifies pure thermal-acid Arrhenius rates ($k_{i,\text{ref}}, E_i$).
* In **Track B Active Sonication**, the acoustic multipliers ($\kappa_{\text{ext}}, \kappa_{\text{hyd}}$) are inferred by fitting the combined response vector:
  $$\mathbf{y} = [Y_{\text{APSP}}, C_{\text{GalA}}, DE, M_w]^T$$
  preventing false optimization of apparent yield at the expense of destroyed molecular weight ($M_w$).

---

## 2. Mechanistic 4-Pool Mass ODEs & Property Moments

Mass pools normalize to dry feedstock mass $[\text{kg/kg}_{\text{dry,feed}}]$ with $m_{\text{dry}} = m_{\text{fresh}} \cdot (1 - X_{w,0})$:
$$\frac{dP_{\text{matrix}}}{dt} = -k_{\text{ext}} P_{\text{matrix}}$$
$$\frac{dP_{\text{sol}}}{dt} = k_{\text{ext}} P_{\text{matrix}} - k_{\text{hyd}} P_{\text{sol}}$$
$$\frac{dP_{\text{lowMW}}}{dt} = k_{\text{hyd}} P_{\text{sol}} - k_{\text{deg}} P_{\text{lowMW}}$$
$$\frac{dP_{\text{loss}}}{dt} = k_{\text{deg}} P_{\text{lowMW}}$$

Invariant: $\sum_{i} P_i(t) \equiv P_{\text{matrix},0}, \quad \epsilon_M < 10^{-10}$.

### Cohort-Correct Moments
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

## 3. Epistemological Parameter Ontology (v3.1)

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
| **Reference Extraction Rate** | $k_{\text{ext,ref}}$ | $\text{min}^{-1}$ | **Calibrated Parameter** | Prior: $\text{LogNormal}(\ln(0.035), 0.3)$ |
| **Extraction Activation Energy** | $E_{\text{ext}}$ | $\text{J/mol}$ | **Calibrated Parameter** | Prior: $\text{Normal}(60000, 10000)$ |
| **Reference Hydrolysis Rate** | $k_{\text{hyd,ref}}$ | $\text{min}^{-1}$ | **Calibrated Parameter** | Prior: $\text{LogNormal}(\ln(0.015), 0.3)$ |
| **Hydrolysis Activation Energy** | $E_{\text{hyd}}$ | $\text{J/mol}$ | **Calibrated Parameter** | Prior: $\text{Normal}(85000, 12000)$ |
| **Reference Degradation Rate** | $k_{\text{deg,ref}}$ | $\text{min}^{-1}$ | **Calibrated Parameter** | Prior: $\text{LogNormal}(\ln(0.005), 0.4)$ |
| **Degradation Activation Energy**| $E_{\text{deg}}$ | $\text{J/mol}$ | **Calibrated Parameter** | Prior: $\text{Normal}(100000, 15000)$ |
| **Particle Scaling Exponent** | $\alpha$ | $-$ | **Calibrated Parameter** | Prior: $\text{Normal}(1.0, 0.2)$ |
| **Acoustic Power Delivered** | $P_{\text{acoustic}}$ | W | **Directly Measured (Calorimetry)**| Water solvent calorimetry ($m C_p dT/dt$) |
| **Acoustic Solubilization Coeff**| $\kappa_{\text{ext}}$ | $\text{m}^3/\text{W}$ | **Calibrated Parameter** | Prior: $\text{LogNormal}(\ln(0.05), 0.5)$ |
| **Acoustic Hydrolysis Coeff** | $\kappa_{\text{hyd}}$ | $\text{m}^3/\text{W}$ | **Calibrated Parameter** | Prior: $\text{LogNormal}(\ln(0.02), 0.5)$ |

---

## 4. The Shared Analytical Backbone

Both Track A and Track B feed the **identical analytical backbone**:

$$\boxed{
\text{Gravimetric Recovery } (m_{\text{dry\_precipitate}})
\longleftrightarrow
\text{GalA Concentration } (C_{\text{GalA}})
\longleftrightarrow
\text{Pectin-Equivalent } (C_{\text{pectin-equiv}})
\longleftrightarrow
\text{DE \& } M_w
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

## 5. Two-Tier Bayesian Inference Architecture

$$\mathbf{\Sigma}_{\text{total}} = \mathbf{\Sigma}_{\text{obs}} + \mathbf{\Sigma}_{\text{process}}$$

$$p(\theta \mid \mathcal{D}) \propto p(\theta) \prod_{j=1}^{N_{\text{runs}}} \prod_{k=1}^{N_{\text{samples}}} \mathcal{N}\left(\mathbf{y}_{j,k}^{\text{obs}} \;\Big|\; \mathbf{y}_{\text{model}}(t_{j,k}; \theta), \mathbf{\Sigma}_{\text{total}}\right)$$

* Multi-response vector $\mathbf{y} = [Y_{\text{APSP}}, C_{\text{GalA}}, DE, M_w]^T$.
* Sampled via Hamiltonian Monte Carlo (NUTS) across 4 chains of 2,000 warm-up and 2,000 posterior iterations.
* Convergence target: $\hat{R} < 1.05$ across all calibrated parameters.
