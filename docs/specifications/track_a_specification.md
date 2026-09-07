# Track A Specification: Jacketed Stirred Acid Hydrolysis Reactor

**Document Version**: 3.2 (Shared Provenance with Dried/Sieved Pretreatment)  
**Parent Document**: [`MASTER_DUAL_TRACK_SPECIFICATION.md`](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/MASTER_DUAL_TRACK_SPECIFICATION.md)  
**Status**: Canonical Track A Technical Standard  

---

## 1. Executive Summary & Philosophy

**Track A** represents the baseline, high-rigor extraction and identification track of the Pectin Digital Twin ecosystem. Its primary objective is **scientific parameter identifiability and thermodynamic/kinetic validation** under carefully controlled, standardized laboratory conditions.

Unlike rapid screening or empirical testing, Track A is engineered as a precision physical measurement instrument designed to feed the Bayesian inference engine of the **V1.3 4-Pool Mechanistic Model**.

```text
=============================================================================================
TRACK A: Precision Identification Pipeline
Shared Fresh Comminution (Lot ID)  -->  Forced-Air Drying (60 °C, X_w ~ 6-8%)  -->
Knife-Milling & ASTM Sieve Sizing (150, 300, 600 um)  -->  Jacketed Stirred Reactor  -->
Time-Resolved Ice-Quenched Aliquots (t = 15, 45, 90, 120 min)  -->  Reference Assay Suite  -->
Bayesian Mechanistic Twin (D-Optimal Calibration, kappa approx 27.0)
=============================================================================================
```

---

## 2. Feedstock Conditioning Submodel

Track A utilizes standardized, dried, and sieved passion-fruit peel to decouple biological moisture variance from reaction kinetics.

### A. Pre-Processing Specifications
1. **Shared Provenance Step**: Fresh passion fruit rind is cleaned, moisture-logged ($X_{w,0} \in [0.81, 0.86]$), and comminuted in the food processor ($3 \times 15\text{ s}$ pulses) under a logged physical lot ID (`LOT-YYYYMMDD-BATCH`).
2. **Drying Branch**: From this shared lot, material allocated to Track A is spread on stainless steel trays and dried under forced-air convection at $60^\circ\text{C}$ until reaching equilibrium moisture:
   $$X_{w,\text{standardized}} \approx 6.0\text{--}8.0\% \quad (\text{wet basis})$$
3. **Comminution & Sieving**: The dried pericarp/mesocarp is knife-milled and classified through standard ASTM mesh sieves into discrete granulometric fractions:
   * **Fine fraction**: $d_{50} = 150\,\mu\text{m}$ (ASTM 100)
   * **Reference fraction**: $d_{\text{ref}} = 300\,\mu\text{m}$ (ASTM 50)
   * **Coarse fraction**: $d_{50} = 600\,\mu\text{m}$ (ASTM 30)
4. **Empirical Transport Modifier**:
   $$\phi_d = \left(\frac{d_{\text{ref}}}{d_{50}}\right)^\alpha \quad (\alpha \in [0.5, 2.0])$$

### B. Feedstock Batch Characterization Table
Prior to charging the reactor, each feedstock lot must have the following reference anchors recorded:

| Property | Symbol | Target / Expected Range | Analytical Method |
| :--- | :---: | :---: | :--- |
| **Available Protopectin** | $P_{\text{matrix},0}$ | $0.20 - 0.28\text{ kg/kg}_{\text{dry,feed}}$ | Alcohol Insoluble Residue (AIR) GalA-corrected |
| **Matrix Esterification** | $DE_{\text{reference}}$ | $70 - 78\%$ | Titrimetric saponification on mild reference extract |
| **Matrix Molecular Weight** | $M_{w,\text{reference}}$ | $5.5 \times 10^5 - 7.5 \times 10^5\text{ Da}$ | HPSEC-MALLS on mild reference extract |
| **GalA Fraction** | $X_{\text{GalA,matrix}}$ | $74 - 82\%$ | m-hydroxydiphenyl (mHDP) colorimetry |
| **Residual Moisture** | $X_w$ | $0.06 - 0.08$ | Halogen moisture analyzer (105 °C) |
| **Sieved Particle Size** | $d_{50}$ | $150, 300, 600\,\mu\text{m}$ | ASTM sieve analysis / Laser diffraction |

---

## 3. Extraction Reactor Hardware & Controls

Track A operates in a dedicated, instrumented jacketed glass batch reactor.

```text
               OVERHEAD STIRRER
              (Anchor / Pitched Blade)
                     │
                     ▼
          ┌─────────────────────┐  <--- PT100 RTD Probe (submerged)
          │  JACKETED REACTOR   │  <--- Combined pH Probe
  CIRC.   │    (1.2 - 2.0 L)    │  <--- Water-Cooled Dimroth Condenser (<0.2% loss)
  BATH    │ ┌─────────────────┐ │
 (Julabo/ │ │ Slurry:         │ │
  Huber)  │ │ Dried Rind +    │ │
  =====>  │ │ Citric Acid Sol │ │  =====> Return to Bath
          │ └─────────────────┘ │
          └──────────┬──────────┘
                     ▼
          QUENCH BOTTOM VALVE
          (Dead-volume-free)
                     │
                     ▼
          0 °C Ice-Water / Glycol Quench
```

### Core Specifications
* **Vessel**: $1.2\text{ L}$ to $2.0\text{ L}$ borosilicate glass cylindrical reactor with an external thermal jacket and torispherical bottom. Glass allows visual confirmation of fouling, wall-scaling, and phase dispersion.
* **Vapor Control**: Water-cooled Dimroth reflux condenser ($15^\circ\text{C}$ coolant) guaranteeing $< 0.2\%$ mass loss over 120 minutes at $95^\circ\text{C}$.
* **Thermal Circulation**: Circulating bath rated to $120^\circ\text{C}$ with rapid ramp capability ($< 5\text{ min}$ from $25^\circ\text{C}$ to $95^\circ\text{C}$).
* **Agitation**: High-torque overhead mechanical stirrer coupled to a PTFE anchor impeller or $45^\circ$ pitched-blade turbine ($250\text{--}400\text{ RPM}$). Magnetic stir bars are strictly prohibited due to decoupling in high-viscosity pectin slurries.
* **Thermal Logging**: Submerged Class A PT100 RTD sensor positioned in the active core reaction volume, logged at $\ge 0.1\text{ Hz}$. This provides the continuous integral exposure:
  $$\tau_k = \int_0^t k(T(s), \text{pH}(s))\,ds$$
* **Kinetic Acidity**: Controlled using food-grade citric acid ($C_{\text{citric}} = 0.05 - 0.50\text{ M}$) with initial charge and continuous electrode tracking ($\text{pH } 1.5 - 3.0$).

---

## 4. Sampling, Quenching & Mass Balance

### A. Non-Destructive Multi-Timepoint Aliquots
To resolve the structural cascade anti-correlation ($k_{\text{hyd}} \leftrightarrow k_{\text{deg}}$), Track A demands time-resolved observations rather than single endpoints:
$$\text{Sampling schedule: } t \in \{15, 45, 90, 120\}\text{ minutes}$$

### B. Quenching Protocol
1. Exact aliquot volume: $V_{\text{aliquot}} \approx 10.0 - 12.0\text{ mL}$ withdrawn through the dead-volume-free bottom drain valve.
2. Immediate immersion: Dispensed directly into thin-walled stainless-steel tubes pre-chilled in a glycol bath ($-10^\circ\text{C}$), cooling the aliquot below $25^\circ\text{C}$ in $< 15\text{ seconds}$.
3. Timestamp registration: The logged observation timestamp is the exact second the sample contacts the chilled tube.
4. Total cumulative withdrawal must remain $\le 4.0\%$ of initial reactor slurry mass ($4 \times 12\text{ mL} = 48\text{ mL}$ out of $\ge 1.2\text{ L}$).

---

## 5. Analytical Assay Suite

Track A pairs physical sampling with high-precision analytical assays to satisfy digital twin noise targets:

```text
 quenched aliquot
        │
        ▼
   Centrifugation (4,000 RPM, 10 min)
        │
   ┌────┴───────────────────────────┐
   ▼                                ▼
 Solid Spent Cake              Liquid Extract
                                    │
                  ┌─────────────────┴─────────────────┐
                  ▼                                   ▼
          OFFLINE REFERENCE ASSAYS           RAPID SECONDARY PROXY
          - AIR Gravimetric (Yield)          - Standardized Ethanol Wash
          - USP/FAO Titration (DE)           - FTIR / DRIFTS (DE, GalA)
          - HPSEC-MALLS-RI (Mw)              - Capillary Viscometer (Mw)
          - mHDP / Carbazole (GalA)
```

### Analytical Noise Targets ($\sigma$)

| Observable | Analytical Method | Target $\sigma$ | Identifiability Purpose |
| :--- | :--- | :---: | :--- |
| **Extract Yield** ($Y_p$) | Alcohol Insoluble Residue (AIR), dried at 60 °C | $\sigma = 0.01$ (1% abs) | Identifies $k_{\text{ext,ref}}$ and activation energy $E_{\text{ext}}$ |
| **Degree of Esterification** ($DE$) | USP double-titration (saponification with 0.25M NaOH) | $\sigma = 0.02$ (2% abs) | Uniquely identifies de-esterification rate $k_{\text{de}}$ |
| **Molecular Weight** ($M_w$) | HPSEC-MALLS (dn/dc = 0.146 mL/g) | $\sigma = 15,000\text{ Da}$ | Breaks the $k_{\text{hyd}} \leftrightarrow k_{\text{deg}}$ structural anti-correlation |
| **GalA Purity** ($X_{\text{GalA}}$) | m-hydroxydiphenyl (mHDP) at 520 nm | $\sigma = 0.025$ (2.5% abs) | Verifies pectin backbone conservation |

---

## 6. Optimal Experimental Design (OED) Campaign

The V1.3 digital twin was exercised under D-optimality criteria ($\det(\mathbf{FIM})$ maximization across the 13-parameter model with 4-timepoint tracking), generating the canonical 10-run calibration matrix ($\kappa(\mathbf{FIM}) \approx 27.0$) and 3 independent validation runs.

*Mathematical Formulation*:
* Factors: Temperature $T \in [50, 95]^\circ\text{C}$, Acidity $\text{pH} \in [1.5, 3.0]$, Particle size $d_{50} \in [150, 600]\,\mu\text{m}$.
* Normalized coded coordinates: $x_T = (T - 72.5)/22.5$, $x_{\text{pH}} = (\text{pH} - 2.25)/0.75$, $x_d = \log_2(d_{50}/300.0)$.
* The normalized main-effects design matrix condition number is $\kappa(\mathbf{X}_{\text{main}}) = 3.49$, and the full 13-parameter sensitivity Fisher Information Matrix achieves $\kappa(\mathbf{FIM}) \approx 27.0$ (eliminating near-null sensitivity directions).

### A. 10-Run Calibration Protocol (Batches A & B)

| Run | $T$ (°C) | pH | $d_{50}$ ($\mu$m) | Sample Times (min) | Design Objective |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **1** | 95 | 1.5 | 600 | 15, 45, 90, 120 | Extreme severity + large particle (separates $E_{\text{ext}}$ from $\alpha$) |
| **2** | 50 | 1.5 | 150 | 15, 45, 90, 120 | Low $T$, high acidity, small particle |
| **3** | 95 | 2.5 | 150 | 15, 45, 90, 120 | High $T$, moderate pH, small particle |
| **4** | 50 | 1.5 | 600 | 15, 45, 90, 120 | Low $T$, high acidity, large particle |
| **5** | 95 | 2.0 | 600 | 15, 45, 90, 120 | Intermediate severity anchor |
| **6** | 50 | 2.0 | 150 | 15, 45, 90, 120 | Low $T$, moderate pH anchor |
| **7** | 95 | 2.5 | 600 | 15, 45, 90, 120 | High $T$, low acidity, large particle |
| **8** | 50 | 1.5 | 300 | 15, 45, 90, 120 | Center-particle low $T$ anchor |
| **9** | 95 | 3.0 | 150 | 15, 45, 90, 120 | High $T$, mild pH boundary |
| **10** | 95 | 2.0 | 300 | 15, 45, 90, 120 | Reference state replication ($T=95^\circ\text{C}, d_{50}=300\,\mu\text{m}$) |

### B. 3-Run Independent Validation Matrix (Batch C)
To prevent overfitting and test generalization against genuine feedstock batch variability:

| Run | $T$ (°C) | pH | $d_{50}$ ($\mu$m) | Validation Focus |
| :---: | :---: | :---: | :---: | :--- |
| **11** | 75 | 2.2 | 300 | **Interior Center-Point**: Tests nonlinear model interpolation |
| **12** | 85 | 1.8 | 300 | **Near-Optimum Trajectory**: High yield confirmation zone |
| **13** | 90 | 1.5 | 150 | **Severity Edge**: Stresses thermal depolymerization / degradation cascade |

### C. Optional Cross-Check Arm: Fresh Feedstock Exploration
* **Purpose**: Empirically evaluate whether kinetics identified on dried/sieved peel extrapolate to the fresh tissue state Track B utilizes before a formal mathematical bridging term is developed.
* **Scope**: 2–3 runs in the Track A jacketed reactor using **undried, fresh food-processed fragments** directly from the shared provenance lot (e.g., $75^\circ\text{C}$, $\text{pH } 2.2$, $t = 60\text{ min}$).
* **Execution Status**: Resource-dependent and optional. It does **not** alter or replace the core 10-run calibration + 3-run validation matrix.

---

## 7. Downstream Separation & Techno-Economics

Bulk extract exiting the Track A reactor undergoes one of four standardized downstream recovery routes:
1. **Hybrid Membrane-Solvent (`hybrid`)**: Microfiltration clarification $\to$ 10× Ultrafiltration/Diafiltration $\to$ 1:1 ethanol precipitation $\to$ convective drying (95% recovery).
2. **Zero-Solvent Direct Drying (`direct_drying`)**: MF clarification $\to$ Diafiltration concentration $\to$ Direct spray drying (98% recovery, zero ethanol use).
3. **Conventional Evaporative (`conventional`)**: MF clarification $\to$ 80% thermal vacuum evaporation $\to$ 2:1 ethanol precipitation $\to$ drying (90% recovery).
4. **Liquid Concentrate (`liquid_concentrate`)**: MF clarification $\to$ Ultrafiltration concentration to 6–8% Brix $\to$ preservative stabilization $\to$ liquid formulation (zero alcohol, zero drying).

---

## 8. Comparative Matrix: Track A vs. Track B

| Dimension | Track A (Classical Jacketed Reactor) | Track B (UAE + At-Line Soft Sensor) |
| :--- | :--- | :--- |
| **Primary Objective** | Mechanistic parameter identification & model validation | Rapid screening, process optimization & at-line control |
| **Feedstock State** | Standardized, dried, and sieved peel ($X_w \approx 6\text{--}8\%$, $d_{50} \in \{150, 300, 600\}\,\mu\text{m}$) | Fresh wet comminuted rind ($X_w \approx 81\text{--}86\%$, un-dried, measured $d_{50}$ covariate) |
| **Energy Driving Force** | Thermal conduction from jacket ($50 - 95^\circ\text{C}$) + mechanical shear | Acoustic cavitation (40 kHz, $P_{\text{elec}} \to P_{\text{acoustic}}$) + internal acoustic heating |
| **Vapor Control** | Water-cooled Dimroth reflux condenser ($< 0.2\%$ mass loss) | Sealed vessel in bath + mass balance check ($< 0.3\%$ mass loss) |
| **Sampling Mode** | Time-resolved ice-quenched aliquots ($t = 15, 45, 90, 120\text{ min}$) | Post-filtration split aliquot ($m_{\text{aliquot}}$ vs $m_{\text{precip}}$) |
| **Primary Analytical Tool**| Offline laboratory assays (HPSEC-MALLS, titration, AIR) | At-line IO Rodeo 8-channel colorimeter ($[A_{515}, A_{555}, A_{680}] \to C_{\text{GalA}}$, $A_{630} \to C_{\text{pectin-eq}}$) |
| **Downstream Recovery** | Industrial flowsheets (Hybrid membrane, evaporative, direct spray) | Rapid 2:1 ethanol precipitation + low-temperature vacuum oven drying |
| **Digital Twin Role** | Identifies fundamental Arrhenius rates ($k_{\text{ext}}, k_{\text{hyd}}, k_{\text{deg}}, k_{\text{de}}$) | Identifies acoustic cavitation modifiers $\kappa_{\text{ext}}, \kappa_{\text{hyd}}$ against paired $P_{\text{elec}}=0$ controls |
