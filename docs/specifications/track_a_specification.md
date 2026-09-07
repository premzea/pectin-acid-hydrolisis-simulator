# Track A Specification: Jacketed Stirred Acid Hydrolysis Reactor

## 1. Executive Summary & Philosophy

**Track A** represents the baseline, high-rigor extraction and identification track of the Pectin Digital Twin ecosystem. Its primary objective is **scientific parameter identifiability and thermodynamic/kinetic validation** under carefully controlled, standardized laboratory conditions.

Unlike rapid screening or empirical testing, Track A is engineered as a precision physical measurement instrument designed to feed the Bayesian inference engine of the **V1.3 4-Pool Mechanistic Model**.

```text
=============================================================================================
TRACK A: Precision Identification Pipeline
Feedstock Drying & Milling  -->  Jacketed Stirred Reactor  -->  Quenched Time Aliquots  -->
Offline Reference Assays (AIR, Titration, HPSEC, mHDP) / Secondary Proxies  -->  Bayesian OED Twin
=============================================================================================
```

---

## 2. Feedstock Conditioning Submodel

Track A utilizes standardized, dried, and sieved passion-fruit peel to decouple biological moisture variance from reaction kinetics.

### A. Pre-Processing Specifications
1. **Drying**: Fresh passion fruit rind ($X_{w,0} \approx 81 - 86\%$ wet basis) is dried under forced-air convection at 60 °C until reaching equilibrium moisture:
   $$X_{w,\text{standardized}} \approx 6.0 - 8.0\% \text{ (wet basis)}$$
2. **Comminution & Sieving**: The dried pericarp/mesocarp is knife-milled and classified through standard ASTM mesh sieves into discrete granulometric fractions:
   * Fine fraction: $d_{50} = 150\,\mu\text{m}$ (ASTM 100)
   * Reference fraction: $d_{\text{ref}} = 300\,\mu\text{m}$ (ASTM 50)
   * Coarse fraction: $d_{50} = 600\,\mu\text{m}$ (ASTM 30)
3. **Empirical Transport Modifier**:
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
| **Particle Size** | $d_{50}$ | $150, 300, 600\,\mu\text{m}$ | Sieve analysis / Laser diffraction |

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
  CIRC.   │    (0.5 - 2.0 L)    │
  BATH    │ ┌─────────────────┐ │
 (Julabo/ │ │ Slurry:         │ │
  Huber)  │ │ Dried Rind +    │ │
  =====>  │ │ Citric/Mineral  │ │  =====> Return to Bath
          │ │ Acid Solution   │ │
          │ └─────────────────┘ │
          └──────────┬──────────┘
                     ▼
          QUENCH BOTTOM VALVE
          (Dead-volume-free)
                     │
                     ▼
             0 °C Ice-Water Quench
```

### A. Core Specifications
* **Vessel**: $0.5\text{ L}$ to $2.0\text{ L}$ borosilicate glass cylindrical reactor with an external thermal jacket and torispherical bottom. Glass allows visual confirmation of fouling, wall-scaling, and phase dispersion.
* **Thermal Circulation**: Circulating oil/water bath (e.g., Julabo, Huber) rated to $120^\circ\text{C}$ with rapid ramp capability ($< 5\text{ min}$ from $25^\circ\text{C}$ to $95^\circ\text{C}$).
* **Agitation**: High-torque overhead mechanical stirrer coupled to a PTFE anchor impeller or $45^\circ$ pitched-blade turbine ($150 - 450\text{ RPM}$). Magnetic stir bars are strictly prohibited due to decoupling in high-viscosity pectin solutions.
* **Thermal Logging**: Submerged Class A PT100 RTD sensor positioned in the active core reaction volume, logged at $\ge 0.1\text{ Hz}$. This provides the continuous integral exposure:
  $$\tau_k = \int_0^t k(T(s), \text{pH}(s))\,ds$$
* **Kinetic Acidity**: Controlled using food-grade citric acid ($C_{\text{citric}} = 0.05 - 0.50\text{ M}$) or hydrochloric acid ($\text{pH } 1.5 - 3.0$).

---

## 4. Sampling, Quenching & Mass Balance

### A. Non-Destructive Multi-Timepoint Aliquots
To resolve the structural cascade anti-correlation ($k_{\text{hyd}} \leftrightarrow k_{\text{deg}}$), Track A demands time-resolved observations rather than single endpoints:
$$\text{Sampling schedule: } t \in \{15, 45, 90, 120\}\text{ minutes}$$

### B. Quenching Protocol
1. Exact aliquot volume: $V_{\text{aliquot}} \approx 10.0 - 15.0\text{ mL}$ withdrawn through the dead-volume-free bottom drain valve.
2. Immediate immersion: Dispensed directly into centrifuge tubes pre-chilled in an ice-water bath ($0^\circ\text{C}$), cooling the aliquot below $25^\circ\text{C}$ within 10 seconds.
3. Timestamp registration: The logged observation timestamp is the exact second the sample contacts the ice-chilled tube.
4. Total cumulative withdrawal must remain $< 5\%$ of initial reactor slurry mass, or be dynamically balanced in the state equations.

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
          - mHDP Assay (GalA)
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

The V1.3 digital twin was exercised under D-optimality criteria ($\det(FIM)$ maximization), generating the canonical 10-run calibration matrix ($\kappa = 27.0$) and 3 independent validation runs.

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
| **10** | 95 | 2.0 | 300 | 15, 45, 90, 120 | Reference state replication ($T=95^\circ\text{C}, d_{50}=300$) |

### B. 3-Run Independent Validation Matrix (Batch C)
To prevent overfitting and test generalization against genuine feedstock batch variability:

| Run | $T$ (°C) | pH | $d_{50}$ ($\mu$m) | Validation Focus |
| :---: | :---: | :---: | :---: | :--- |
| **11** | 75 | 2.2 | 300 | **Interior Center-Point**: Tests nonlinear model interpolation |
| **12** | 85 | 1.8 | 300 | **Near-Optimum Trajectory**: High yield confirmation zone |
| **13** | 90 | 1.5 | 150 | **Severity Edge**: Stresses thermal depolymerization / degradation cascade |

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
| **Feedstock State** | Standardized, dried, and classified peel ($X_w \approx 8\%$, $d_{50} = 150 - 600\,\mu\text{m}$) | Fresh, comminuted rind ($X_w \approx 81 - 86\%$, food-processor fragments) |
| **Energy Driving Force** | Thermal conduction from jacket ($50 - 95^\circ\text{C}$) + mechanical shear | Acoustic cavitation (40 kHz, $P_{\text{elec}} \to P_{\text{acoustic}}$) + internal acoustic heating |
| **Residence Time** | 20 to 120 minutes | 10 to 60 minutes |
| **Sampling Mode** | Time-resolved ice-quenched aliquots ($t = 15, 45, 90, 120\text{ min}$) | Post-filtration split aliquot ($m_{\text{aliquot}}$ vs $m_{\text{precip}}$) |
| **Primary Analytical Tool**| Offline laboratory assays (HPSEC-MALLS, titration, AIR) | At-line IO Rodeo 8-channel colorimeter ($[A_{515}, A_{555}, A_{680}] \to C_{\text{GalA}}$, $A_{590} \to C_{\text{pectin-eq}}$) |
| **Downstream Recovery** | Industrial flowsheets (Hybrid membrane, evaporative, direct spray) | Rapid 2:1 ethanol precipitation + low-temperature vacuum oven drying |
| **Digital Twin Role** | Identifies fundamental Arrhenius rates ($k_{\text{ext}}, k_{\text{hyd}}, k_{\text{deg}}, k_{\text{de}}$) | Identifies acoustic coupling efficiency $\eta_{\text{coupling}}$ & acoustic enhancement $\psi_{\text{US}}$ |
