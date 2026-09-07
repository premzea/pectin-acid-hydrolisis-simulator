# Master Dual-Track Specification: Pectin Extraction Digital Twin

**Document Version**: 2.2 (Incorporating Epistemological & Phased Review)  
**Status**: Architecture & Specification Standard  
**Workspaces**: `pectin-acid-hydrolisis-simulator` | `bioreactor-studio`

---

## 1. Executive Summary & System Philosophy

This document integrates the two operational tracks of the Passion-Fruit Pectin Extraction Digital Twin into an epistemologically grounded cyber-physical framework:

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

Rather than modeling ultrasound as an alien chemical reaction, the digital twin models **a single shared chemical depolymerization cascade acted upon by track-specific physical accessibility operators**:

* **Track A (Precision Mechanistic Identification Track)**:
  * *Question*: *What are the fundamental chemical kinetics of extraction, chain scission, degradation, and de-esterification?*
  * *Method*: Jacketed stirred glass reactor ($1.2\text{--}2.0\text{ L}$) with water-cooled reflux condenser (zero evaporation), standardized dried peel ($X_w \approx 8\%$, $d_{50} = 150\text{--}600\,\mu\text{m}$), and active pH monitoring/micro-dosing.
  * *Campaign*: Refined 12-run D-optimal OED matrix with intermediate $70^\circ\text{C}$ curvature anchor and true process replicates.
  * *Measurements*: Time-resolved quenched aliquots (thin-walled stainless vials, $<15\text{ s}$) feeding offline reference assays (HPSEC-MALLS, titration, mHDP, APSP gravimetric) and calibrated secondary proxies (FTIR, capillary viscometer).
* **Track B (Rapid UAE & At-Line Soft-Sensor Track)**:
  * *Question*: *Can we achieve rapid extraction in fresh native rind, and can inexpensive optical measurements infer the product state?*
  * *Method*: Ultrasound bath chamber ($40\text{ kHz}$, $\gamma_{US} \equiv 1.0$) using fresh, un-dried rind comminuted in a food processor ($X_{w,0} \approx 81\text{--}86\%$, fragments).
  * *Campaign*: 10-run UAE OED matrix featuring paired **fresh-rind thermal baseline controls** ($P_{\text{elec}} = 0\text{ W}$) to cleanly isolate acoustic cavitation without drying-history confounding.
  * *Measurements*: Multi-timepoint at-line spectrophotometry (**IO Rodeo 8-Channel Colorimeter**) with **sample-blank matrix pigment subtraction**, measuring a Chemical Pectin Proxy (GalA and Pectin-Equivalent) alongside Gravimetric Recovery to compute the **GalA Composition / Purity Proxy**.

---

## 2. Epistemological Grounding: Separating Fact from Model

| Level | Definition | Examples in This Digital Twin |
| :--- | :--- | :--- |
| **Directly Measured** | Ground truth recorded with calibrated sensors | $T_{\text{slurry}}(t)$, $\text{pH}(t)$, gross masses, raw absorbances $\mathbf{A}(\lambda)$, dry precipitate mass |
| **Directly Calibrated** | Inferred statistically from experimental datasets | $k_{\text{ext,ref}}$, $E_{\text{ext}}$, $k_{\text{hyd,ref}}$, $E_{\text{hyd}}$, soft-sensor regression weights $\mathbf{w}$ |
| **Standardized Convention** | Fixed by operational design | $T_{\text{ref}} = 80^\circ\text{C}$, $\text{pH}_{\text{ref}} = 2.0$, $d_{\text{ref}} = 300\,\mu\text{m}$, $\gamma_{US} \equiv 1.0$ (fixed single-frequency) |
| **Hypothesis / Prior** | Mechanistic guide; **not** treated as hard truth | Partition of $P_{\text{acoustic}}$ into heat vs. mechanical work; fresh accessibility factor $\Omega_{\text{fresh}}$ |

*Methodological Rule*: The model does **not** hardcode an arbitrary 88/12 sensible-heat/cavitation partition. Acoustic power is measured calorimetrically ($P_{\text{acoustic}}$), and the net cavitation benefit is inferred directly from the matched fresh thermal control:
$$\Delta Y_{\text{UAE}} = Y_{\text{UAE,fresh}}(T, P_{\text{elec}}) - Y_{\text{thermal,fresh}}(T, P_{\text{elec}} = 0)$$

---

## 3. Stage-Gated Project Hierarchy (Preventing Over-Engineering)

To ensure software complexity never outpaces physical experimental reality, execution proceeds through 5 strict gates:

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│ PHASE 0: Physical Sanity Check Gate                                              │
│ - Zero reflux loss (<0.3%), thermal stability (±0.5 °C), pH stability            │
│ - Filtration repeatability (CV < 2.5%), vacuum dry mass repeatability (CV < 4.0%)│
│ - STOP: If physical CV is bad, do not run high-dimensional Bayesian models!      │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │ Pass Phase 0 Gate
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: Analytical Triangle Backbone                                            │
│ - Validate internal consistency: [Gravimetric Recovery <-> GalA <-> Pectin-Eq]   │
│ - Matrix-spike recovery on real extract (95% - 105% recovery target)             │
│ - Verify sample-blank pigment subtraction eliminates native carotenoid bias      │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │ Pass Phase 1 Gate
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: Track A Mechanistic Core Campaign                                       │
│ - Execute 12-run OED matrix (70 °C anchor, low-T asymptote, center replicates)   │
│ - Estimate intrinsic Arrhenius rates (k_ext, k_hyd, k_deg, k_de, DE, Mw)         │
│ - Decompose variance: Σ_total = Σ_obs + Σ_process                                │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │ Pass Phase 2 Gate
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│ PHASE 3: Track B Net Enhancement Campaign                                        │
│ - Execute paired fresh thermal baselines (P_elec = 0) to identify Ω_fresh        │
│ - Execute active sonication matrix (100-300 W) to identify κ_US and β_US         │
│ - Quantify true acoustic enhancement: ΔY_UAE(T) = Y_UAE(T, P) - Y_thermal(T, 0) │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │ Pass Phase 3 Gate
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│ PHASE 4: At-Line Soft-Sensor Online Deployment                                   │
│ - Deploy IO Rodeo 8-channel automated inference in Bioreactor Studio UI          │
│ - Real-time dilution advising, range enforcement, and GalA Composition Gauge     │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Master Comparative Matrix (Hardened)

| Dimension | Track A: Jacketed Stirred Reactor | Track B: UAE + At-Line Soft Sensor |
| :--- | :--- | :--- |
| **Scientific Objective** | Identifies intrinsic reaction kinetics | Identifies fresh tissue accessibility & acoustic enhancement |
| **Feedstock State** | Standardized, dried, sieved powder ($X_w \approx 8\%$, $d_{50} = 150\text{--}600\,\mu\text{m}$) | Fresh, food-processed rind ($X_w \approx 81\text{--}86\%$, comminuted fragments) |
| **Tissue Matrix Factor**| Reference standard $\Omega_{\text{matrix}} \equiv 1.0$ | Fresh uncollapsed cellular tissue $\Omega_{\text{fresh}} \approx 1.25\text{--}1.60$ (estimand) |
| **Evaporation Control** | Water-cooled Dimroth reflux condenser ($< 0.2\%$ mass loss) | Closed container in ultrasonic bath |
| **Acidity Control** | Active continuous logging; micro-dosing pump option | Buffered initial charge; continuous trajectory logging |
| **Working Volume** | $\ge 1.2\text{ L}$ working volume (4 aliquots $\times 12\text{ mL} \le 4.0\%$ total) | $500\text{ g}$ slurry; micro-aliquots ($5\text{ mL} \times 4 \le 4.0\%$ total) |
| **Quench Mechanics** | Thin-walled stainless vials in $-10^\circ\text{C}$ bath ($< 15\text{ s}$) | Immediate syringe filtration + room temperature cooling |
| **Driving Force** | Thermal conduction through jacket + mechanical shear | Acoustic cavitation ($40\text{ kHz}$, $\gamma_{US} \equiv 1.0$) + acoustic dissipation |
| **Acoustic Decoupling** | Pure thermal baseline by definition | Paired fresh-tissue thermal controls ($P_{\text{elec}} = 0\text{ W}$) |
| **OED Calibration** | **12-Run Matrix**: includes $70^\circ\text{C}$ curvature anchor & 2 replicates | **10-Run Matrix**: includes 2 fresh thermal baselines & 2 replicates |
| **Sampling Mode** | Time-resolved ice-quenched aliquots ($t \in \{15, 45, 90, 120\}\text{ min}$) | Time-resolved micro-aliquots ($t \in \{10, 20, 40, 60\}\text{ min}$) |
| **Spectrophotometry** | Offline reference assays (HPSEC, titration, APSP, mHDP) | At-line 8-channel IO Rodeo with **sample-blank pigment subtraction** |
| **Proxy Provenance** | SQLite tables (`ftir_calibrations`, `viscometer_calibrations`) | SQLite table (`colorimeter_calibrations`) with matrix spike records |
| **Downstream TEA Scope** | Evaluates all 4 industrial flowsheets (Hybrid, Spray, Evap, Liq) | Evaluates all 4 industrial flowsheets (Hybrid, Spray, Evap, Liq) |

---

## 5. Modular Domain Specifications

Detailed technical documentation is modularized into three dedicated domain specifications:
1. 🔬 **[Domain 1: Biochemical Engineering & Physical Extraction Protocol](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/domain_1_biochemical_engineering.md)**
2. 📐 **[Domain 2: Mathematical Modeling & Statistical Calibration Architecture](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/domain_2_statistical_modeling_and_calibration.md)**
3. 💻 **[Domain 3: Software Engineering & Cyber-Physical System Architecture](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/domain_3_software_and_cyberphysical_architecture.md)**
