# Master Dual-Track Specification: Pectin Extraction Digital Twin

**Document Version**: 3.1 (Ultrasound-Assisted Acid Extraction Framing)  
**Status**: Architecture & Specification Standard  
**Workspaces**: `pectin-acid-hydrolisis-simulator` | `bioreactor-studio`

---

## 1. Executive Summary & Core Scientific Framing

Version 3.1 establishes the foundational scientific identity of the extraction process:

> **Ultrasound-Assisted Extraction (UAE) is not an alternative extraction chemistry to acid hydrolysis. It is ultrasound-enhanced acid extraction/hydrolysis in an acidified aqueous medium.**

Both tracks operate in the **identical acidified solvent medium (food-grade citric acid)** on the **exact same fresh, food-processed passion-fruit rind**. The underlying acid-catalyzed solubilization and depolymerization chemistry is shared; ultrasound acts as an external physical driving force modifying mass transfer, tissue disruption, and polymer chain cleavage.

```text
                           ACIDIFIED WATER (CITRIC ACID, pH 1.5 - 3.0)
                                                │
                                                ▼
                                    FRESH PASSION-FRUIT RIND
                                 (Measured X_w,0, standardized d50)
                                                │
                         ┌──────────────────────┴──────────────────────┐
                         │                                             │
                         ▼                                             ▼
                     TRACK A                                       TRACK B
            THERMAL ACID EXTRACTION                      ULTRASOUND-ASSISTED ACID
             (Mechanistic Reference)                     EXTRACTION & SOFT SENSOR
                         │                                             │
           Conductive Heating (50-95 °C)                 Conductive Heating + Cavitation (40 kHz)
           Overhead Mechanical Stirring                  Acoustic Microjets & Acoustic Streaming
           Reflux Sealed (Zero Evap)                     Dual T (Bath & Slurry RTD)
                         │                                             │
                         │                                ┌────────────┴────────────┐
                         │                                │                         │
                         │                                ▼                         ▼
                         │                             UAE ACTIVE             MATCHED CONTROL
                         │                            (Sonication ON)         (P_elec = 0, OFF)
                         │                                │                         │
                         └────────────────────────────────┴─────────────────────────┘
                                                          │
                                                SHARED ANALYTICAL BACKBONE
                                                (APSP Yield + GalA + Pectin-Eq + DE + Mw)
```

### The Central Scientific Question
> *How does acoustic cavitation modify the kinetics and product-quality trajectory (Yield, GalA, DE, $M_w$) of citric-acid extraction/hydrolysis of fresh passion-fruit rind relative to purely thermal acid extraction?*

---

## 2. Track Designations & Causal Roles

### Track A: Thermal Acid Extraction — Mechanistic Reference
* **Solvent**: Acidified deionized water (citric acid, $\text{pH } 1.5\text{--}3.0$).
* **Feedstock**: Fresh, food-processed passion-fruit rind ($X_{w,0}$ measured per batch).
* **Vessel**: Closed jacketed glass reactor ($1.2\text{--}2.0\text{ L}$) with water-cooled Dimroth reflux condenser (zero evaporation).
* **Driving Force**: Bulk thermal conduction ($50\text{--}95^\circ\text{C}$) + mechanical shear ($250\text{--}400\text{ RPM}$).
* **Scientific Role**: Identifies the intrinsic thermal-acid kinetics:
  $$k_{\text{ext}}^{\text{thermal}},\quad k_{\text{hyd}}^{\text{thermal}},\quad k_{\text{deg}}^{\text{thermal}},\quad k_{\text{de}}^{\text{thermal}}$$
  and establishes the baseline trajectory of yield, de-esterification, and molecular weight.

### Track B: Ultrasound-Assisted Acid Extraction & Soft Sensor
* **Solvent**: Identical acidified deionized water (same citric acid concentration and pH).
* **Feedstock**: Identical fresh, food-processed passion-fruit rind from the same batch.
* **Vessel**: Ultrasonic bath chamber ($40\text{ kHz}$, nominal power $P_{\text{elec}} \in [50, 300]\text{ W}$).
* **Driving Force**: Thermal conduction + localized acoustic cavitation (transient micro-bubble collapse, microjets, and acoustic streaming).
* **Mandatory Control**: Paired **fresh-rind thermal baseline runs** ($P_{\text{elec}} = 0\text{ W}$, sonication OFF in identical bath).
* **Scientific Role**:
  1. Quantifies the net incremental acoustic benefit holding acid chemistry constant:
     $$\Delta Y_{\text{US}} = Y_{\text{acid+thermal+US}} - Y_{\text{acid+thermal}}$$
  2. Disentangles accelerated solubilization ($k_{\text{ext}}^{\text{US}} > k_{\text{ext}}^{\text{thermal}}$) from unwanted acoustic polymer depolymerization/degradation ($k_{\text{hyd}}^{\text{US}}$, $k_{\text{deg}}^{\text{US}}$, drop in $M_w$).
  3. Calibrates the at-line multi-wavelength soft sensor (**IO Rodeo 8-Channel Colorimeter**).

---

## 3. Kinetic Implication: Dual-Action Ultrasound on the 4-Pool Model

Ultrasound does not create a separate chemical network. It modifies the rate constants of the shared 4-pool cascade:

$$\boxed{
\text{P}_{\text{matrix}}
\xrightarrow{k_{\text{ext}}(T, \text{pH}, P_{\text{US}})}
\text{P}_{\text{sol}}
\xrightarrow{k_{\text{hyd}}(T, \text{pH}, P_{\text{US}})}
\text{P}_{\text{lowMW}}
\xrightarrow{k_{\text{deg}}(T, \text{pH}, P_{\text{US}})}
\text{P}_{\text{loss}}
}$$

1. **Enhanced Solubilization**: Acoustic microjets peel boundary-layer diffusion resistance and rupture parenchymal cell walls:
   $$k_{\text{ext}}^{\text{US}} > k_{\text{ext}}^{\text{thermal}}$$
2. **Acoustic Polymer Degradation Risk**: High-intensity cavitation produces localized shear stresses and radical formation that can cleave $\alpha$-(1 $\to$ 4) glycosidic bonds, accelerating depolymerization:
   $$k_{\text{hyd}}^{\text{US}} \ge k_{\text{hyd}}^{\text{thermal}}, \quad k_{\text{deg}}^{\text{US}} \ge k_{\text{deg}}^{\text{thermal}}$$
3. **Quality Trajectory Tradeoff**:
   * *Higher gravimetric yield is not automatically better.*
   * Over-sonication can produce high apparent yield with severely collapsed molecular weight ($M_w < 100\text{ kDa}$) and altered $DE$, destroying gelling quality.
   * Therefore, simultaneous tracking of **Yield + GalA + DE + Molecular Weight** is mathematically necessary to optimize the acoustic extraction window.

---

## 4. Stage-Gated Phased Implementation

```text
Phase 0: Physical Sanity Gate (Reflux loss <0.3%, gravimetric CV <4%, colorimeter CV <1.5%)
                            │
                            ▼
Phase 1: Analytical Triangle Backbone (Gravimetric Yield + GalA + Pectin-Eq + Spikes)
                            │
                            ▼
Phase 2: Track A Thermal Acid Mechanistic Core (12 runs on Fresh Rind in Citric Acid)
                            │
                            ▼
Phase 3: Track B UAE Acid Enhancement (10 runs with Sonication ON vs OFF Controls)
                            │
                            ▼
Phase 4: At-Line Soft-Sensor Online Deployment (Automated UI Inferences & Advising)
```

---

## 5. Comparative Specification Matrix (v3.1)

| Dimension | Track A: Thermal Acid Reference | Track B: Ultrasound-Assisted Acid & Soft Sensor |
| :--- | :--- | :--- |
| **Solvent Medium** | Citric acid aqueous solution ($\text{pH } 1.5\text{--}3.0$) | **Identical citric acid aqueous solution** |
| **Feedstock State** | Fresh comminuted rind ($X_w$ measured per batch) | **Identical fresh comminuted rind** from same batch |
| **Solvent Ratio (LSR)** | $m_{\text{water}} / [m_{\text{fresh}} (1 - X_w)] \approx 30\text{--}35\text{ mL/g}_{\text{dry}}$ | **Identical liquid-to-solid ratio** |
| **Vapor Control** | Water-cooled Dimroth reflux condenser ($< 0.2\%$ loss) | Closed container in ultrasonic bath |
| **Acidity Control** | Continuous electrode logging; micro-dosing pump option | Buffered initial charge; continuous trajectory logging |
| **Working Volume** | $\ge 1.2\text{ L}$ working volume ($4 \times 12\text{ mL} \le 4.0\%$ total) | $500\text{ g}$ slurry ($4 \times 5\text{ mL} \le 4.0\%$ total) |
| **Energy Driving Force** | Thermal conduction ($50\text{--}95^\circ\text{C}$) + mechanical shear | Thermal conduction + acoustic cavitation ($40\text{ kHz}$) |
| **Matched Control** | Serves as the primary thermal reference | Paired fresh-rind thermal controls ($P_{\text{elec}} = 0\text{ W}$) |
| **Sampling Schedule** | Multi-timepoint time series ($t \in \{15, 45, 90, 120\}\text{ min}$) | Multi-timepoint time series ($t \in \{10, 20, 40, 60\}\text{ min}$) |
| **Analytical Suite** | Shared Analytical Backbone (APSP, GalA, Pectin-Eq, DE, Mw) | Shared Analytical Backbone (APSP, GalA, Pectin-Eq, DE, Mw) |
| **Techno-Economics** | Baseline thermal-acid OPEX/CAPEX across 4 flowsheets | Incremental ultrasound electricity/capital vs. yield/quality gain |

---

## 6. Modular Domain Specifications

Detailed technical documentation is modularized into three dedicated domain specifications:
1. 🔬 [Domain 1: Biochemical Engineering & Physical Extraction Protocol](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/domain_1_biochemical_engineering.md)
2. 📐 [Domain 2: Mathematical Modeling & Statistical Calibration Architecture](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/domain_2_statistical_modeling_and_calibration.md)
3. 💻 [Domain 3: Software Engineering & Cyber-Physical System Architecture](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/domain_3_software_and_cyberphysical_architecture.md)
