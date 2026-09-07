# Master Dual-Track Specification: Pectin Extraction Digital Twin

**Document Version**: 3.0 (Unified Fresh-Rind Common Feedstock Architecture)  
**Status**: Architecture & Specification Standard  
**Workspaces**: `pectin-acid-hydrolisis-simulator` | `bioreactor-studio`

---

## 1. Executive Summary & Core Architectural Principle

Version 3.0 unifies the entire experimental and digital-twin program under a **common fresh-rind feedstock architecture**. Rather than running Track A on dried powder and Track B on fresh rind—which introduces an intractable confound of drying, cellular collapse, hornification, and milling—both tracks consume the **exact same fresh, food-processed passion-fruit rind**.

```text
                    FRESH PASSION-FRUIT RIND
                              │
                    Standardized comminution
                 (Food processor, measured X_w)
                              │
                     ┌────────┴────────┐
                     │                 │
                     ▼                 ▼
                 TRACK A           TRACK B
            THERMAL REFERENCE   UAE ENHANCEMENT
             (Stirred Reactor)  (Ultrasonic Bath)
                     │                 │
                     │          ┌──────┴──────┐
                     │          │             │
                     │          ▼             ▼
                     │       UAE ON        UAE OFF (Matched Control)
                     │          │             │
                     └──────────┴─────────────┘
                                │
                          SAME ANALYTICS
                     (Analytical Triangle)
                                │
                   ┌────────────┼────────────┐
                   ▼            ▼            ▼
             Gravimetric       GalA      Pectin-Eq
             Solid Yield    (Carbazole)  (Cu-Chelate)
```

### The Causal Elegance of Unified Feedstock
By enforcing an identical starting biomass across both tracks:
1. **Zero Matrix Confounding**: Differences between Track A and Track B reflect genuine physical driving forces (stirred thermal vs. acoustic cavitation), not cellular dehydration history.
2. **Elimination of $\Omega_{\text{fresh}}$**: The empirical matrix correction factor is **deleted from the core V1 model**. Both tracks share the same physical accessibility state $\phi_{\text{feed}}(d_{50})$.
3. **Clean Causal Baseline**: The ultrasound effect is cleanly isolated against the matched fresh thermal control:
   $$\Delta Y_{\text{US}} = Y_{\text{fresh,UAE}} - Y_{\text{fresh,thermal}}$$
4. **Dried Rind Repositioned**: Dried peel is retired as the primary Track A feedstock and retained strictly as an optional secondary characterization study (*"What is the techno-economic and yields impact of eliminating drying?"*).

---

## 2. Track Roles & Operational Summary

### Track A — Thermal Mechanistic Reference
* **Feedstock**: Fresh, food-processed passion-fruit rind (residual moisture $X_{w,0}$ measured per batch).
* **Vessel**: Closed jacketed glass reactor ($1.2\text{--}2.0\text{ L}$) fitted with a water-cooled reflux condenser (zero evaporation).
* **Agitation**: High-torque overhead mechanical stirrer (anchor/pitched-blade turbine, $250\text{--}400\text{ RPM}$).
* **Driving Force**: Conductive thermal heat transfer ($50\text{--}95^\circ\text{C}$) + controlled acidity ($\text{pH } 1.5\text{--}3.0$).
* **Scientific Mission**: Identifies the intrinsic chemical reaction kinetics ($k_{\text{ext}}, k_{\text{hyd}}, k_{\text{deg}}, k_{\text{de}}$, $DE$, $M_w$) on the native fresh pericarp matrix.

### Track B — UAE Enhancement & At-Line Soft Sensor
* **Feedstock**: Identical fresh, food-processed passion-fruit rind from the same comminuted lot.
* **Vessel**: Ultrasound bath chamber ($40\text{ kHz}$, nominal power $P_{\text{elec}} \in [50, 300]\text{ W}$) with dual temperature tracking.
* **Driving Force**: Acoustic cavitation ($P_{\text{acoustic}} = \eta_{\text{coupling}} P_{\text{elec}}$) + sensible acoustic heating.
* **Mandatory Control**: Paired **fresh-rind thermal baseline runs** ($P_{\text{elec}} = 0\text{ W}$, identical fresh slurry in the same bath).
* **Scientific Mission**: Quantifies true incremental acoustic enhancement ($\Delta Y_{\text{US}}$) and calibrates the at-line multi-wavelength soft sensor (**IO Rodeo 8-Channel Colorimeter**).

---

## 3. Epistemological Parameter Classification

| Level | Definition | Parameters in This Twin |
| :--- | :--- | :--- |
| **Directly Measured** | Ground truth from physical sensors | Slurry $T(t)$, bath $T(t)$, $\text{pH}(t)$, fresh mass $m_{\text{fresh}}$, water mass $m_{\text{water}}$, batch moisture $X_{w,0}$, raw absorbances $\mathbf{A}(\lambda)$, dry precipitate mass $m_{\text{dry\_precipitate}}$ |
| **Directly Calibrated** | Inferred statistically from data | Arrhenius constants $k_{\text{ext,ref}}, E_{\text{ext}}, k_{\text{hyd,ref}}, E_{\text{hyd}}, k_{\text{deg,ref}}, E_{\text{deg}}, k_{\text{de,ref}}, E_{\text{de}}$, soft-sensor regression weights $\mathbf{w}$ |
| **Standardized Convention** | Fixed by operational design | $T_{\text{ref}} = 80.0^\circ\text{C}$, $\text{pH}_{\text{ref}} = 2.00$, $d_{\text{ref}} = 300\,\mu\text{m}$, $\gamma_{\text{US}} \equiv 1.0$ (fixed single-frequency constraint) |
| **Hypothesis / Latent Estimand** | Unidentified without micro-measurements | Acoustic power partition (left unpartitioned in V1; model directly infers net enhancement $\psi_{\text{US}}$ from matched thermal controls) |

*Normalization Protocol*: Batch moisture $X_{w,0}$ is measured on every physical lot using a halogen moisture analyzer ($105^\circ\text{C}$). Dry mass basis is calculated explicitly:
$$m_{\text{dry}} = m_{\text{fresh}} \cdot (1 - X_{w,0})$$
All state variables in both Track A and Track B normalize to this dry matter mass $[\text{kg/kg}_{\text{dry,feed}}]$.

---

## 4. Stage-Gated Phased Implementation

```text
Phase 0: Physical Sanity Gate (Reflux loss <0.3%, gravimetric CV <4%, colorimeter CV <1.5%)
                            │
                            ▼
Phase 1: Analytical Triangle Backbone (Gravimetric Yield + GalA + Pectin-Eq + Spikes)
                            │
                            ▼
Phase 2: Track A Thermal Mechanistic Core (12 runs on Fresh Rind -> k_ext, k_hyd, k_deg)
                            │
                            ▼
Phase 3: Track B Net Enhancement (10 runs on Same Fresh Rind with P_elec = 0 Controls)
                            │
                            ▼
Phase 4: At-Line Soft-Sensor Online Deployment (Automated UI Inferences & Advising)
```

---

## 5. Comparative Specification Matrix (v3.0)

| Engineering Dimension | Track A: Thermal Reference | Track B: UAE & Soft Sensor |
| :--- | :--- | :--- |
| **Feedstock State** | Fresh comminuted rind ($X_w$ measured per batch, $d_{50} \in [500, 2000]\,\mu\text{m}$) | **Identical fresh comminuted rind** from same batch |
| **Comminution Method** | Standardized food-processor pulsing protocol | **Same standardized food-processor protocol** |
| **Solvent Ratio (LSR)** | $m_{\text{water}} / [m_{\text{fresh}} (1 - X_w)] \approx 30\text{--}40\text{ mL/g}_{\text{dry}}$ | **Identical liquid-to-solid ratio** |
| **Vapor Control** | Water-cooled Dimroth reflux condenser ($< 0.2\%$ loss) | Closed container in ultrasonic bath |
| **Acidity Control** | Continuous electrode logging; micro-dosing pump option | Buffered initial charge; continuous trajectory logging |
| **Working Volume** | $\ge 1.2\text{ L}$ working volume ($4 \times 12\text{ mL} \le 4.0\%$ total) | $500\text{ g}$ slurry ($4 \times 5\text{ mL} \le 4.0\%$ total) |
| **Quench Mechanics** | Thin-walled stainless vials in $-10^\circ\text{C}$ bath ($< 15\text{ s}$) | Immediate syringe filtration + room temperature cooling |
| **Energy Driving Force** | Thermal conduction through jacket + mechanical shear | Acoustic cavitation ($40\text{ kHz}$) + sensible acoustic heating |
| **Matched Control** | Serves as the primary thermal reference | Paired fresh-rind thermal controls ($P_{\text{elec}} = 0\text{ W}$) |
| **Sampling Schedule** | Multi-timepoint time series ($t \in \{15, 45, 90, 120\}\text{ min}$) | Multi-timepoint time series ($t \in \{10, 20, 40, 60\}\text{ min}$) |
| **Analytical Suite** | Shared Analytical Triangle (APSP, GalA, Pectin-Eq, DE, Mw) | Shared Analytical Triangle (APSP, GalA, Pectin-Eq) |
| **Downstream TEA Scope** | Symmetric evaluation across all 4 flowsheets | Symmetric evaluation across all 4 flowsheets |

---

## 6. Modular Domain Specifications

Detailed technical documentation is modularized into three dedicated domain specifications:
1. 🔬 [Domain 1: Biochemical Engineering & Physical Extraction Protocol](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/domain_1_biochemical_engineering.md)
2. 📐 [Domain 2: Mathematical Modeling & Statistical Calibration Architecture](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/domain_2_statistical_modeling_and_calibration.md)
3. 💻 [Domain 3: Software Engineering & Cyber-Physical System Architecture](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/domain_3_software_and_cyberphysical_architecture.md)
