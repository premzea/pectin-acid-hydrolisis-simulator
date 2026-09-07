# Master Dual-Track Specification: Pectin Extraction Digital Twin

**Document Version**: 3.2 (Shared Provenance with Diverging Feedstock Conditioning)  
**Status**: Architecture & Specification Standard  
**Workspaces**: `pectin-acid-hydrolisis-simulator` | `bioreactor-studio`

---

## Document Changelog

| Version | Date | Key Architectural Decisions & Rationale |
| :---: | :---: | :--- |
| **v3.2** | 2026-09-07 | **Shared Comminution Provenance + Diverging Pretreatment**: Established a single physical batch provenance point at food-processor comminution ($X_{w,0} \in [0.81, 0.86]$, $d_{50} \in [500, 1500]\,\mu\text{m}$, lot ID logged). Diverged pretreatment thereafter: Track A branches to convective drying (60 °C to $X_w \approx 6\text{--}8\%$), knife-milling, and sieving ($d_{50} \in \{150, 300, 600\}\,\mu\text{m}$) restoring the canonical 10-run D-optimal + 3 validation matrix ($\kappa \approx 27.0$). Track B remains on fresh wet fragments with measured (covariate) $d_{50}$. Decoupled cross-track baselines: $\Delta Y_{\text{US}}$ is computed strictly against Track B's paired $P_{\text{elec}} = 0\text{ W}$ fresh thermal control. Track A kinetics provide Bayesian priors, not literal baseline substitutes; bridging factor deferred. Added Track B evaporative-loss check to Phase 0. Documented open gaps: $\gamma_{\text{US}}$ identifiability and Track B OED table. Added optional 2–3 run fresh Track A cross-check arm. |
| **v3.1** | 2026-09-07 | Ultrasound framed strictly as ultrasound-enhanced acid extraction in citric acid medium (not alternative chemistry). Formulated dual-action acoustic kinetics on 4-pool cascade. |
| **v3.0** | 2026-09-06 | Unified Dual-Track digital twin architecture separating Track A (mechanistic reference) and Track B (UAE + soft sensor). |

---

## 1. Executive Summary & Core Scientific Framing

Version 3.2 solidifies the physical and epistemological boundary between Track A and Track B:

> **Ultrasound-Assisted Extraction (UAE) is ultrasound-enhanced acid extraction/hydrolysis in an acidified aqueous solvent (citric acid, pH 1.5–3.0). Both tracks share an initial physical provenance step (food-processor comminution of fresh rind), but diverge in downstream pretreatment to fulfill complementary scientific objectives.**

```text
                                 FRESH PASSION-FRUIT RIND
                                            │
                           Rinse, Clean, Halogen Moisture Log
                                 X_w,0 in [0.81, 0.86]
                                            │
                           Shared Provenance Comminution
                    (Pulsed Food Processor, 3x15s, d50 in [500, 1500] um)
                                 Log Lot ID: LOT-YYYYMMDD-X
                                            │
                     ┌──────────────────────┴──────────────────────┐
                     │                                             │
                     ▼                                             ▼
                 TRACK A BRANCH                                TRACK B BRANCH
         Drying, Milling & Sieve Sizing                      Fresh Wet Fragments
      (Forced-air 60 °C to X_w ~ 6-8%;                   (No drying, no sieving;
     ASTM Sieving: 150, 300, 600 um)                   Measured d50 as covariate)
                     │                                             │
                     ▼                                             ▼
         THERMAL ACID EXTRACTION                       ULTRASOUND-ASSISTED ACID
          (Mechanistic Reference)                      EXTRACTION & SOFT SENSOR
      Jacketed Stirred Glass Reactor                 40 kHz Ultrasonic Bath Chamber
      Conductive Heating (50-95 °C)                  Acoustic Cavitation + Heating
      Reflux Sealed (<0.2% mass loss)                Closed Sealed Vessel (<0.3% loss)
                     │                                             │
                     │                                ┌────────────┴────────────┐
                     │                                │                         │
                     │                                ▼                         ▼
                     │                            UAE ACTIVE              MATCHED CONTROL
                     │                         (Sonication ON)           (P_elec = 0, OFF)
                     │                                │                         │
                     └────────────────────────────────┴─────────────────────────┘
                                                      │
                                           SHARED ANALYTICAL BACKBONE
                                   (APSP Yield + GalA + Pectin-Eq + DE + Mw)
```

### Baseline Separation & Epistemological Discipline
1. **Track B Net Acoustic Enhancement ($\Delta Y_{\text{US}}$)**:
   $$\Delta Y_{\text{US}} = Y_{\text{acid+thermal+US}} - Y_{\text{acid+thermal}}$$
   is computed **strictly and exclusively against Track B's own internal $P_{\text{elec}} = 0\text{ W}$ fresh-rind thermal control** at matched bath temperature and duration — **never against Track A**.
2. **Role of Track A Kinetics**: Track A's identified rate constants ($k_{\text{ext}}^{\text{thermal}}, k_{\text{hyd}}^{\text{thermal}}, k_{\text{deg}}^{\text{thermal}}, k_{\text{de}}^{\text{thermal}}$) derived from dried/sieved feedstock serve as **informative priors and mechanistic structure** for the Bayesian digital twin, not as literal empirical substitutes for Track B's thermal baseline.
3. **Deferred Quantitative Bridging Term**: A quantitative bridging term (such as a fresh-versus-dried cellular accessibility factor $\Omega_{\text{state}}$ on $k_{\text{ext}}$) relating dried/sieved tissue to fresh/wet cellular fragments is a **deliberately deferred future modeling task**, not an implicit current assumption.

---

## 2. Track Designations & Causal Roles

### Common Provenance Point (Step 0)
* Fresh passion-fruit rind is rinsed, tested for initial moisture ($X_{w,0} \in [0.81, 0.86]$ via halogen analyzer at $105^\circ\text{C}$), and comminuted in a food processor using three 15-second pulse cycles with 5-second rest intervals ($d_{50} \in [500, 1500]\,\mu\text{m}$).
* A standardized physical lot identifier (`LOT-YYYYMMDD-BATCH`) is logged at this stage. Downstream Track A and Track B runs reference this ID, ensuring cross-track traceability to a common biological origin.

### Track A: Thermal Acid Extraction — Mechanistic Reference
* **Solvent**: Acidified deionized water (citric acid, $\text{pH } 1.5\text{--}3.0$).
* **Pretreatment**: Forced-air convective oven drying at $60^\circ\text{C}$ to equilibrium moisture ($X_w \approx 6.0\text{--}8.0\%$), knife-milling, and ASTM sieve classification into discrete fractions: $d_{50} \in \{150, 300, 600\}\,\mu\text{m}$.
* **Vessel**: Closed jacketed borosilicate glass reactor ($1.2\text{--}2.0\text{ L}$) with water-cooled Dimroth reflux condenser ($< 0.2\%$ evaporative loss).
* **Driving Force**: Bulk thermal conduction ($50\text{--}95^\circ\text{C}$) + mechanical shear ($250\text{--}400\text{ RPM}$).
* **Scientific Role**: Identifies intrinsic thermal-acid Arrhenius kinetics, activation energies ($E_{\text{ext}}, E_{\text{hyd}}, E_{\text{deg}}$), and the particle-diffusion exponent ($\alpha$) in the transport modifier:
  $$\phi_d = \left(\frac{d_{\text{ref}}}{d_{50}}\right)^\alpha \quad (d_{\text{ref}} = 300\,\mu\text{m})$$

### Track B: Ultrasound-Assisted Acid Extraction & Soft Sensor
* **Solvent**: Identical acidified deionized water (citric acid, setpoint pH).
* **Pretreatment**: **None post-food-processing**. Fresh, wet fragments charged directly into the extraction bath.
* **Covariate Measurement**: The actual $d_{50}$ of the wet fragments is **measured per batch** (via wet-sieving or laser diffraction) and logged as an observational covariate, not an actively controlled variable.
* **Vessel**: Ultrasonic bath chamber ($40\text{ kHz}$, $P_{\text{elec}} \in [50, 300]\text{ W}$, with calorimetric acoustic power $P_{\text{acoustic}}$).
* **Driving Force**: Thermal conduction + localized acoustic cavitation (microjets, shockwaves, micro-streaming).
* **Mandatory Control**: Paired **fresh-rind thermal baseline runs** ($P_{\text{elec}} = 0\text{ W}$, sonication OFF) in the identical bath at matched slurry temperature.
* **Scientific Role**:
  1. Quantifies true incremental cavitation benefit ($\Delta Y_{\text{US}}$) against matched fresh thermal controls.
  2. Informs acoustic modifiers ($\kappa_{\text{ext}}, \kappa_{\text{hyd}}$) tracking the tradeoff between accelerated extraction and polymer degradation ($M_w$).
  3. Calibrates the at-line multi-wavelength soft sensor (**IO Rodeo 8-Channel Colorimeter**).

---

## 3. Kinetic Implication: Dual-Action Ultrasound on the 4-Pool Model

Ultrasound acts on the shared 4-pool depolymerization cascade:

$$\boxed{
\text{P}_{\text{matrix}}
\xrightarrow{k_{\text{ext}}}
\text{P}_{\text{sol}}
\xrightarrow{k_{\text{hyd}}}
\text{P}_{\text{lowMW}}
\xrightarrow{k_{\text{deg}}}
\text{P}_{\text{loss}}
}$$

* **Extraction Rate (Solubilization)**:
  $$k_{\text{ext}}^{\text{US}} = k_{\text{ext}}^{\text{thermal}}(T, \text{pH}) \cdot a_s(d_{50}) \cdot \left[1 + \kappa_{\text{ext}} \left(\frac{P_{\text{acoustic}}}{V_{\text{slurry}}}\right)^{\beta_{\text{ext}}}\right]$$
  *(where $a_s(d_{50})$ is the fresh-tissue specific surface area covariate).*
* **Chain Scission / Hydrolysis Rate**:
  $$k_{\text{hyd}}^{\text{US}} = k_{\text{hyd}}^{\text{thermal}}(T, \text{pH}) \cdot \left[1 + \kappa_{\text{hyd}} \left(\frac{P_{\text{acoustic}}}{V_{\text{slurry}}}\right)^{\beta_{\text{hyd}}}\right]$$
* **Monomer Degradation Rate**:
  $$k_{\text{deg}}^{\text{US}} = k_{\text{deg}}^{\text{thermal}}(T, \text{pH}) \cdot \left[1 + \kappa_{\text{deg}} \left(\frac{P_{\text{acoustic}}}{V_{\text{slurry}}}\right)^{\beta_{\text{deg}}}\right]$$

### Pareto Optimization Requirement
High acoustic power accelerates mass transfer ($k_{\text{ext}}^{\text{US}}$) but risks hydrolyzing polymer chains ($k_{\text{hyd}}^{\text{US}}$), causing severe molecular weight loss ($M_w < 100\text{ kDa}$). Optimization requires simultaneous fitting of the response vector:
$$\mathbf{y} = [Y_{\text{APSP}}, C_{\text{GalA}}, DE, M_w]^T$$

---

## 4. Stage-Gated Phased Implementation

```text
Phase 0: Physical Sanity Gate (Track A reflux <0.2%, Track B sealed loss <0.3%, gravimetric CV <4%, colorimeter CV <1.5%)
                            │
                            ▼
Phase 1: Analytical Triangle Backbone (Gravimetric Yield + GalA + Pectin-Eq + Spikes)
                            │
                            ▼
Phase 2: Track A Thermal Mechanistic Core (10-run D-optimal + 3 validation runs on Dried/Sieved Rind)
                            │
                            ▼
Phase 3: Track B UAE Acid Enhancement (UAE Active vs. P_elec = 0 Matched Controls on Fresh Rind)
                            │
                            ▼
Phase 4: At-Line Soft-Sensor Online Deployment (Automated UI Inferences & Advising)
```

---

## 5. Comparative Specification Matrix (v3.2)

| Dimension | Track A: Thermal Acid Reference | Track B: Ultrasound-Assisted Acid & Soft Sensor |
| :--- | :--- | :--- |
| **Shared Provenance Step** | Common food-processor comminution ($X_{w,0} \in [0.81, 0.86]$, $d_{50} \in [500, 1500]\,\mu\text{m}$, lot ID logged) | **Identical common comminution lot ID** |
| **Feedstock State** | **Dried, knife-milled, and classified** ($X_w \approx 6\text{--}8\%$, $d_{50} \in \{150, 300, 600\}\,\mu\text{m}$) | **Fresh wet fragments** ($X_w \approx 81\text{--}86\%$, un-dried, measured $d_{50}$ logged as covariate) |
| **Solvent Medium** | Citric acid aqueous solution ($\text{pH } 1.5\text{--}3.0$) | **Identical citric acid aqueous solution** |
| **Liquid-to-Solid Ratio (LSR)**| $m_{\text{water}} / m_{\text{dry}} = 15\text{--}25\text{ mL/g}_{\text{dry}}$ | $(m_{\text{water}} + m_{\text{fresh}} X_{w,0}) / m_{\text{dry}} \approx 25\text{--}35\text{ mL/g}_{\text{dry}}$ |
| **Vapor Control** | Water-cooled Dimroth reflux condenser ($< 0.2\%$ mass loss) | Sealed vessel in bath + mass balance check ($< 0.3\%$ mass loss) |
| **Acidity Control** | Continuous electrode logging; micro-dosing pump option | Buffered initial charge; continuous trajectory logging |
| **Working Volume** | $\ge 1.2\text{ L}$ working volume ($4 \times 12\text{ mL} \le 4.0\%$ total) | $500\text{ g}$ slurry ($4 \times 5\text{ mL} \le 4.0\%$ total) |
| **Energy Driving Force** | Thermal conduction ($50\text{--}95^\circ\text{C}$) + mechanical shear | Thermal conduction + acoustic cavitation ($40\text{ kHz}$) |
| **Matched Control** | Serves as primary thermal reference | Internal fresh-rind thermal controls ($P_{\text{elec}} = 0\text{ W}$) |
| **Sampling Schedule** | Multi-timepoint time series ($t \in \{15, 45, 90, 120\}\text{ min}$) | Multi-timepoint time series ($t \in \{10, 20, 40, 60\}\text{ min}$) |
| **Analytical Suite** | Shared Analytical Backbone (APSP, GalA, Pectin-Eq, DE, Mw) | Shared Analytical Backbone (APSP, GalA, Pectin-Eq, DE, Mw) |
| **Techno-Economics** | Baseline thermal-acid OPEX/CAPEX across 4 flowsheets | Incremental ultrasound electricity/capital vs. yield/quality gain |

---

## 6. Optional Cross-Check Arm: Fresh-Feedstock Track A Runs

To empirically evaluate whether kinetics identified on dried/sieved peel extrapolate to fresh tissue before a formal mathematical bridging term is developed, an optional cross-check arm is defined:
* **Protocol**: Execute 2–3 runs in the Track A jacketed stirred reactor using **undried, fresh food-processed rind** from the shared provenance lot (e.g., at $75^\circ\text{C}$, $\text{pH } 2.2$, $t = 60\text{ min}$).
* **Status**: Resource-dependent and optional. It does **not** alter or replace the primary 10+3 calibration matrix of Track A.

---

## 7. Open Architectural Items (Documented Gaps)

1. **Acoustic Frequency Exponent $\gamma_{\text{US}}$**:
   Single-frequency hardware ($40\text{ kHz}$) cannot structurally identify the frequency-scaling exponent $\gamma_{\text{US}}$ in:
   $$\psi_{\text{US}} = 1 + \kappa_{\text{ext}} \left(\frac{P_{\text{acoustic}}}{V}\right)^\beta \left(\frac{40\text{ kHz}}{f_{\text{US}}}\right)^{\gamma_{\text{US}}}$$
   The parameter is fixed by convention to $\gamma_{\text{US}} \equiv 1.0$ and documented in Domain 2 as structurally unidentifiable without multi-frequency experimental data.
2. **Track B Optimal Experimental Design Table**:
   While Track A features a mathematically derived 10-run D-optimal design matrix, Track B currently specifies screening ranges without an algorithmic D-optimal run table. Formulating the full OED matrix for Track B is a **pending Phase 3 deliverable**.

---

## 8. Modular Domain Specifications

1. 🔬 [Domain 1: Biochemical Engineering & Physical Extraction Protocols](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/domain_1_biochemical_engineering.md)
2. 📐 [Domain 2: Mathematical Modeling & Statistical Calibration Architecture](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/domain_2_statistical_modeling_and_calibration.md)
3. 💻 [Domain 3: Software Engineering & Cyber-Physical System Architecture](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/domain_3_software_and_cyberphysical_architecture.md)
4. 📄 [Track A Canonical Specification](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/specifications/track_a_specification.md)
