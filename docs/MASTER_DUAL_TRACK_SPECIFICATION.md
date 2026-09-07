# Master Dual-Track Specification: Pectin Extraction Digital Twin

**Document Version**: 2.1 (Incorporating Critical Peer Review)  
**Status**: Architecture & Specification Standard  
**Workspaces**: `pectin-acid-hydrolisis-simulator` | `bioreactor-studio`

---

## 1. Executive Summary & System Mission

This document formally integrates the two operational tracks of the Passion-Fruit Pectin Extraction Digital Twin into a unified cyber-physical framework, hardened against experimental and statistical confounding identified during peer review:

* **Track A (Precision Mechanistic Identification Track)**: Operates a jacketed, stirred batch glass reactor fitted with a **water-cooled reflux condenser** (preventing evaporative volume drift at $95^\circ\text{C}$), standardized dried peel ($X_{w} \approx 6\text{--}8\%$, $d_{50} = 150\text{--}600\,\mu\text{m}$), and active pH monitoring/micro-dosing. It executes an enhanced **12-run D-optimal OED campaign** with intermediate $70^\circ\text{C}$ curvature anchors and true process replicates, collecting multi-timepoint quenched aliquots in thin-walled stainless-steel vials to feed offline reference assays (HPSEC-MALLS, titration, mHDP, APSP gravimetric) and calibrated secondary proxies (FTIR PLS, capillary viscometer).
* **Track B (Rapid UAE & At-Line Soft-Sensor Track)**: Operates an Ultrasound-Assisted Extraction (UAE) bath chamber ($40\text{ kHz}$, $\gamma_{US} \equiv 1.0$) using comminuted fresh rind ($X_{w,0} \approx 81\text{--}86\%$, food-processor fragments). It executes a dedicated **10-run UAE OED campaign** featuring paired **fresh-rind thermal baseline controls** ($P_{\text{elec}} = 0\text{ W}$) to cleanly decouple acoustic cavitation from thermal heating and fresh-tissue matrix effects. An at-line analytical branch executes multi-timepoint spectrophotometry (**IO Rodeo 8-Channel Colorimeter**) with **sample-blank matrix pigment subtraction**, measuring a Chemical Pectin Proxy in parallel with Gravimetric Product Recovery to derive an unambiguous **GalA-Based Composition Indicator**.
* **Symmetric Techno-Economic Analysis**: Both tracks interface symmetrically with the TEA engine, allowing extract liquor from either Track A or Track B to be evaluated across all four industrial downstream flowsheets (Hybrid membrane, direct spray drying, conventional evaporation, liquid concentrate).

### System Flowchart: Hardened Dual-Track Architecture

```text
                                PASSION-FRUIT RIND
                                        │
                 ┌──────────────────────┴──────────────────────┐
                 ▼                                             ▼
             TRACK A                                       TRACK B
    (Precision Identification)                     (Rapid UAE & Soft Sensor)
                 │                                             │
      Forced-Air Drying (60 °C)                     Food-Processor Comminution
      Knife Milling & Sieving                       (Fresh rind, X_w ≈ 81-86%,
     (d50 = 150, 300, 600 µm)                        un-dried fragments)
                 │                                             │
   Jacketed Glass Reactor (1.2-2.0 L)               Ultrasound Bath Chamber (40 kHz)
   Reflux Condenser Sealed (Zero Evap)              Acoustic Cavitation (P_acoustic)
   Overhead Mechanical Stirring                      Calorimetric Coupling (η_coupling)
   Active pH Tracking / Micro-Dosing                Dual T Control (T_bath, T_slurry)
   Enhanced 12-Run OED (70 °C Anchor)               Dedicated 10-Run OED (Thermal Baseline)
                 │                                             │
     Time-Resolved Quench Aliquots                  Multi-Timepoint Micro-Aliquots
     (t = 15, 45, 90, 120 min)                      (t = 10, 20, 40, 60 min)
     Thin-wall stainless vials (<15 s)              Rapid Syringe Filtration
                 │                                             │
                 ▼                                ┌────────────┴────────────┐
     OFFLINE REFERENCE ASSAYS                     ▼                         ▼
     - APSP Gravimetric Yield (σ=1%)          AT-LINE ALICQUOT          BULK FILTRATE
     - USP Titration for DE (σ=2%)            Sample-Blank Matrix       m_precipitation_stream
     - HPSEC-MALLS for Mw (σ=15 kDa)          Pigment Subtraction       (Bulk liquor)
     - mHDP Colorimetry for GalA                  │                         │
     CALIBRATED SECONDARY PROXIES                 ▼                         ▼
     - FTIR PLS / Viscometer Models           IO RODEO COLORIMETER      Ethanol Precipitation
                 │                           (8-Channel Net Vector)         (2:1 v/v)
                 ▼                            - [515, 555, 680] -> GalA     │
        TWO-TIER BAYESIAN ENGINE              - [590] -> Pectin-Eq          ▼
      (Σ_total = Σ_obs + Σ_process)               │                    Centrifugation
                 │                                ▼                         │
                 ▼                       ARDUINO Q LOGGER                   ▼
      V1.3 4-POOL MECHANISTIC            - GalA mg/L              Low-Temp Vacuum Oven
        DIGITAL TWIN (FMU)               - Pectin-Eq mg/L         (45 °C, safe solvent removal)
                 │                                │                         │
                 │                                └────────────┬────────────┘
                 │                                             ▼
                 │                                DUAL-TARGET METRIC:
                 │                                GalA Composition Indicator =
                 │                                GalA Mass / Dry Precipitate Mass
                 │                                             │
                 └──────────────────────┬──────────────────────┘
                                        ▼
                           BIOREACTOR STUDIO PLATFORM
                      - Multi-Track Simulation & Control
                      - Unified Provenance Registry (Colorimeter, FTIR, Viscometer)
                      - Real-Time HIL Telemetry Dashboard
                      - Symmetric Techno-Economic Downstream Flowsheet Evaluator
```

---

## 2. Comparative Matrix: Track A vs. Track B (Peer-Reviewed)

| Engineering Dimension | Track A: Jacketed Stirred Reactor | Track B: UAE + At-Line Soft Sensor |
| :--- | :--- | :--- |
| **Primary System Role** | Fundamental mechanistic parameter identification | Rapid empirical screening, soft sensing & optimization |
| **Feedstock State** | Standardized, dried, sieved powder ($X_w \approx 8\%$, $d_{50} = 150\text{--}600\,\mu\text{m}$) | Fresh, food-processed rind ($X_w \approx 81\text{--}86\%$, comminuted fragments) |
| **Tissue Matrix Factor**| Reference standard $\Omega_{\text{matrix}} \equiv 1.0$ | Fresh uncollapsed cellular tissue $\Omega_{\text{fresh}} \approx 1.25\text{--}1.60$ |
| **Vapor / Evaporation Control**| Sealed with water-cooled Dimroth reflux condenser ($< 0.2\%$ loss) | Closed extraction container in ultrasonic bath |
| **pH Operation** | Active continuous logging; micro-dosing pump option | Buffered initial charge; continuous trajectory logging |
| **Working Volume & Aliquots** | $\ge 1.2\text{ L}$ working volume (4 aliquots $\times 12\text{ mL} \le 4.0\%$ total) | $500\text{ g}$ slurry; micro-aliquots ($5\text{ mL} \times 4 \le 4.0\%$ total) |
| **Quenching Mechanics** | Thin-walled stainless-steel immersion vials in $-10^\circ\text{C}$ bath ($< 15\text{ s}$) | Immediate syringe filtration + room temperature cooling |
| **Energy Driving Force** | Thermal conduction through jacket + mechanical shear | Acoustic cavitation ($40\text{ kHz}$, $\gamma_{US} \equiv 1.0$) + acoustic dissipation |
| **Acoustic Decoupling** | Pure thermal baseline by definition | Paired fresh-tissue thermal controls ($P_{\text{elec}} = 0\text{ W}$) |
| **OED Campaign Design** | **12-Run Matrix**: includes $70^\circ\text{C}$ curvature anchor & 2 replicates | **10-Run Matrix**: includes 2 fresh thermal baselines & 2 replicates |
| **Sampling Schedule** | Multi-timepoint time series ($t \in \{15, 45, 90, 120\}\text{ min}$) | Multi-timepoint time series ($t \in \{10, 20, 40, 60\}\text{ min}$) |
| **Spectrophotometric Matrix**| Offline reference assays (HPSEC, titration, APSP, mHDP) | At-line 8-channel IO Rodeo with **sample-blank pigment subtraction** |
| **Secondary Proxy Provenance**| First-class SQLite objects (`ftir_calibrations`, `viscometer_calibrations`)| First-class SQLite object (`colorimeter_calibrations`) with spike recovery |
| **Downstream TEA Scope** | Symmetric access to all 4 industrial flowsheets (Hybrid, Spray, Evap, Liq) | Symmetric access to all 4 industrial flowsheets (Hybrid, Spray, Evap, Liq) |

---

## 3. Modular Architecture: The Three Deep-Dive Domains

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        MASTER DUAL-TRACK SPECIFICATION                                 │
└────────────────────────────────────────────────────────────────────────────────────────┘
          │                                 │                                │
          ▼                                 ▼                                ▼
┌───────────────────────┐       ┌───────────────────────┐        ┌───────────────────────┐
│       DOMAIN 1        │       │       DOMAIN 2        │        │       DOMAIN 3        │
│     BIOCHEMICAL       │       │      STATISTICAL      │        │       SOFTWARE        │
│     ENGINEERING       │       │      MODELING &       │        │     ENGINEERING &     │
│   & WET-LAB SOPS      │       │      CALIBRATION      │        │    CYBER-PHYSICAL     │
├───────────────────────┤       ├───────────────────────┤        ├───────────────────────┤
│ • Reflux condensation │       │ • 4-pool mass ODEs    │        │ • FMU 2.0 Co-Sim C    │
│ • Volume constraints  │       │ • DE & Mw moments     │        │ • SQLite provenance   │
│ • Quench vial cooling │       │ • Sample-blank vector │        │   (Col, FTIR, Visc)   │
│ • APSP yield protocol │       │ • Fixed gamma_US = 1.0│        │ • Dynamic vol balance │
│ • Sample-blank SOP    │       │ • Track A OED (12-run)│        │ • FastAPI endpoints   │
│ • Matrix-spike test   │       │ • Track B OED (10-run)│        │ • WebSocket telemetry │
│ • Fresh thermal base  │       │ • Two-tier variance   │        │ • React UI components │
│ • Vacuum drying SOP   │       │ • Acoustic decoupling │        │ • Symmetric TEA engine│
└───────────────────────┘       └───────────────────────┘        └───────────────────────┘
```

### Domain Document Links:
1. 🔬 [Domain 1: Biochemical Engineering & Physical Extraction Protocol](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/domain_1_biochemical_engineering.md)
2. 📐 [Domain 2: Mathematical Modeling & Statistical Calibration Architecture](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/domain_2_statistical_modeling_and_calibration.md)
3. 💻 [Domain 3: Software Engineering & Cyber-Physical System Architecture](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/domain_3_software_and_cyberphysical_architecture.md)
