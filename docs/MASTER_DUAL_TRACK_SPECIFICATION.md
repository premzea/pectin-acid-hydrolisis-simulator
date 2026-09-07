# Master Dual-Track Specification: Pectin Extraction Digital Twin

**Document Version**: 2.0  
**Status**: Architecture & Specification Standard  
**Workspaces**: `pectin-acid-hydrolisis-simulator` | `bioreactor-studio`

---

## 1. Executive Summary & System Mission

This document formally integrates the two operational tracks of the Passion-Fruit Pectin Extraction Digital Twin into a unified cyber-physical framework:

* **Track A (Precision Mechanistic Identification Track)**: Operates a jacketed, stirred batch glass reactor with standardized dried and sieved passion fruit peel ($X_{w} \approx 6\text{--}8\%$, $d_{50} = 150\text{--}600\,\mu\text{m}$) under thermal-acid conditions ($50\text{--}95^\circ\text{C}$, $\text{pH } 1.5\text{--}3.0$, $15\text{--}120\text{ min}$). It collects time-resolved ice-quenched aliquots to feed high-precision offline reference assays (HPSEC-MALLS, titration, mHDP, AIR) and secondary FTIR/viscosity proxies into a Bayesian Optimal Experimental Design (OED) engine.
* **Track B (Rapid UAE & At-Line Soft-Sensor Track)**: Operates an Ultrasound-Assisted Extraction (UAE) bath chamber ($40\text{ kHz}$, controlled acoustic power and dual bath/slurry temperature) using comminuted fresh rind ($X_{w,0} \approx 81\text{--}86\%$, food-processor fragments). Immediately after solid/liquid filtration, an at-line analytical branch executes multi-channel spectrophotometry (**IO Rodeo 8-Channel Colorimeter**) driven by an **Arduino Q** data logger to measure a **Chemical Pectin Proxy** (GalA concentration via carbazole feature shape and Pectin-Equivalent concentration via copper-chelate) in parallel with **Gravimetric Product Recovery** (low-temperature vacuum oven drying), deriving an actionable **GalA-based Composition / Purity Indicator**.

### System Flowchart: Integrated Dual-Track Architecture

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
   Jacketed Glass Reactor (0.5-2 L)                 Ultrasound Bath Chamber (40 kHz)
   Overhead Mechanical Stirring                      Acoustic Cavitation (P_acoustic)
   Thermal Bath Circulation (50-95 °C)              Dual T Control (T_bath, T_slurry)
   Kinetic Acidity (pH 1.5-3.0)                     Nominal Power: 50-300 W
                 │                                             │
     Time-Resolved Quench Aliquots                  Rapid Slurry Filtration
       (t = 15, 45, 90, 120 min)                               │
                 │                                ┌────────────┴────────────┐
                 ▼                                ▼                         ▼
     OFFLINE REFERENCE ASSAYS                 AT-LINE ALICQUOT          BULK FILTRATE
     - AIR Gravimetric Yield (σ=1%)          (m_aliquot ≈ 10 g)       (m_precip ≈ 390 g)
     - USP Titration for DE (σ=2%)                │                         │
     - HPSEC-MALLS for Mw (σ=15 kDa)              ▼                         ▼
     - mHDP Colorimetry for GalA              IO RODEO COLORIMETER     Ethanol Precipitation
                 │                           (8-Channel Vector)             (2:1 v/v)
                 ▼                            - [515, 555, 680] -> GalA     │
        BAYESIAN OED ENGINE                   - [590] -> Pectin-Eq          ▼
      (D-Optimal 10-Run Design)                   │                    Centrifugation
                 │                                ▼                         │
                 ▼                       ARDUINO Q LOGGER                   ▼
      V1.3 4-POOL MECHANISTIC            - GalA mg/L              Low-Temp Vacuum Oven
        DIGITAL TWIN (FMU)               - Pectin-Eq mg/L         (Safe solvent removal)
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
                      - Calibration Provenance Registry
                      - Real-Time HIL Telemetry Dashboard
```

---

## 2. Comparative Matrix: Track A vs. Track B

| Engineering Dimension | Track A: Classical Jacketed Reactor | Track B: UAE + At-Line Soft Sensor |
| :--- | :--- | :--- |
| **Primary System Role** | Fundamental mechanistic parameter identification | Rapid empirical screening, soft sensing & optimization |
| **Feedstock State** | Standardized, dried, sieved powder ($X_w \approx 8\%$, $d_{50} = 150\text{--}600\,\mu\text{m}$) | Fresh, food-processed rind ($X_w \approx 81\text{--}86\%$, coarse/fine fragments) |
| **Energy Driving Force** | Thermal conduction through jacket + mechanical shear | Acoustic cavitation ($40\text{ kHz}$) + internal acoustic heating |
| **Residence Time** | 20 to 120 minutes | 10 to 60 minutes |
| **Operating Temperature** | $50^\circ\text{C}$ to $95^\circ\text{C}$ (strictly jacket-driven) | $30^\circ\text{C}$ to $70^\circ\text{C}$ (coupled bath exchange + acoustic dissipation) |
| **Sampling & Aliquoting** | Time-resolved ice-quenched aliquots ($t \in \{15, 45, 90, 120\}\text{ min}$) | Post-filtration stream split ($m_{\text{filtrate\_total}} = m_{\text{aliquot}} + m_{\text{precip}}$) |
| **Analytical Mode** | High-precision offline laboratory assays | Rapid at-line multi-wavelength spectrophotometry |
| **Chemical Target** | Absolute $P_{\text{sol}}$, $DE$, $M_w$, $X_{\text{GalA}}$ | Chemical Pectin Proxy ($C_{\text{GalA}}$ and $C_{\text{pectin-equiv}}$) |
| **Product Recovery** | Industrial flowsheets (Hybrid membrane, spray drying, concentrate) | Standardized 2:1 ethanol precipitation + low-temp vacuum oven |
| **Primary Metric** | Multi-response yield trajectory $Y(t)$, $DE(t)$, $M_w(t)$ | GalA-based Composition Indicator ($m_{\text{GalA,total}} / m_{\text{dry\_precip,scaled}}$) |
| **Digital Twin Hook** | Calibrates reference Arrhenius rates ($k_{\text{ext}}, k_{\text{hyd}}, k_{\text{deg}}, k_{\text{de}}$) | Identifies acoustic efficiency $\eta_{\text{coupling}}$ and enhancement $\psi_{US}$ |

---

## 3. Modular Architecture: The Three Deep-Dive Domains

To enable targeted technical reviews without confounding domain concepts, this master specification links directly to three modular domain documents:

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
│ • Feedstock pre-treat │       │ • 4-pool mass ODEs    │        │ • FMU 2.0 Co-Sim C    │
│ • Hydrolysis vs UAE   │       │ • DE & Mw moments     │        │ • SQLite provenance   │
│ • Acoustic coupling   │       │ • Vector soft sensors │        │ • FastAPI endpoints   │
│ • At-line assays      │       │ • OED Fisher info     │        │ • WebSocket telemetry │
│ • Mass-balance split  │       │ • Bayesian MCMC       │        │ • React UI components │
│ • Vacuum drying SOP   │       │ • Acoustic decoupling │        │ • Arduino Q logger    │
└───────────────────────┘       └───────────────────────┘        └───────────────────────┘
```

### Domain Document Links:
1. 🔬 [Domain 1: Biochemical Engineering & Physical Extraction Protocol](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/domain_1_biochemical_engineering.md)  
   *Target Reviewers*: Chemical engineers, food scientists, biochemists, and wet-lab operators.
2. 📐 [Domain 2: Mathematical Modeling & Statistical Calibration Architecture](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/domain_2_statistical_modeling_and_calibration.md)  
   *Target Reviewers*: Applied mathematicians, bioprocess modelers, chemometricians, and Bayesian statisticians.
3. 💻 [Domain 3: Software Engineering & Cyber-Physical System Architecture](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/domain_3_software_and_cyberphysical_architecture.md)  
   *Target Reviewers*: Software architects, full-stack developers, embedded/IoT engineers, and UI/UX designers.

---

## 4. Cross-Domain Feedback & Review Matrix

Use this matrix to guide domain-specific reviews and approvals:

| Subject Matter Expert | Primary Sections to Review | Key Verification Questions |
| :--- | :--- | :--- |
| **Biochemist / Food Scientist** | [Domain 1](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/domain_1_biochemical_engineering.md) (§2, §4, §5) | Are the carbazole and Cu-chelate assay reagents compatible with passion-fruit polyphenols? Is the vacuum oven temperature profile sufficient to remove ethanol without depolymerization? |
| **Process / Chemical Engineer** | [Domain 1](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/domain_1_biochemical_engineering.md) (§3), [Domain 2](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/domain_2_statistical_modeling_and_calibration.md) (§5) | Does the acoustic coupling efficiency equation ($\eta_{\text{coupling}}$) properly reflect ultrasonic calorimetric losses? Is the thermal vs acoustic decoupling experiment physically sound? |
| **Statistician / Model Engineer**| [Domain 2](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/domain_2_statistical_modeling_and_calibration.md) (§2, §3, §4) | Does the multi-wavelength vector $[A_{515}, A_{555}, A_{680}] \to C_{\text{GalA}}$ properly mitigate turbidity? Is the D-optimal design condition number ($\kappa = 27$) robust to feedstock batch shifts? |
| **Software / Systems Engineer** | [Domain 3](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/domain_3_software_and_cyberphysical_architecture.md) (§2, §3, §4) | Does the SQLite calibration provenance schema capture all necessary parameters? Are the WebSocket frame rates and FastAPI endpoints performant for real-time operation? |
