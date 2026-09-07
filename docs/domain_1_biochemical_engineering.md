# Domain 1: Biochemical Engineering & Physical Extraction Protocols

**Document Version**: 2.0  
**Parent Document**: [`MASTER_DUAL_TRACK_SPECIFICATION.md`](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/MASTER_DUAL_TRACK_SPECIFICATION.md)  
**Target Audience**: Chemical Engineers, Biochemists, Food Technologists, Wet-Lab Operators

---

## 1. Executive Scope & Chemistry Fundamentals

Pectin extraction from passion-fruit (*Passiflora edulis*) peel involves the solubilization and selective chain scission of protopectin anchored within the cell-wall matrix of the pericarp and albedo. Structurally, passion fruit pectin consists predominantly of a **homogalacturonan (HG)** backbone ($\alpha$-(1 $\to$ 4)-linked D-galacturonic acid units), partially methyl-esterified at the C-6 carboxyl group, with neutral sugar side chains (arabinan, galactan, rhamnogalacturonan-I).

This document establishes the physical unit operations, chemical kinetic mechanisms, analytical chemistry standard operating procedures (SOPs), and recovery protocols across both operational tracks:
* **Track A**: Standardized dried peel, thermal-acid stirred reactor, time-resolved quenching, and offline reference analytical assays.
* **Track B**: Fresh rind comminution, 40-kHz ultrasound-assisted extraction (UAE), at-line multi-wavelength spectrophotometry, and low-temperature vacuum oven product recovery.

---

## 2. Biomass Conditioning & Comminution Submodels

### A. Track A: Convective Drying & Precision Sieving
To isolate chemical reaction kinetics from raw fruit moisture variations ($X_{w,0} \approx 81 - 86\%$), Track A uses a standardized dry powder:

1. **Forced-Air Dehydration**: Fresh peels are sliced into $2 \times 2\text{ cm}$ strips and dried in a forced-air convection oven at $60^\circ\text{C}$ for 16–24 hours until reaching stable moisture ($X_w \le 0.08\text{ g/g wb}$).
2. **Knife Milling & ASTM Classification**: Dried peels are pulverized using a rotary knife mill and sieved through stacked ASTM testing sieves:
   * Fine cut: $d_{50} = 150\,\mu\text{m}$ (passes 100 mesh)
   * Reference standard: $d_{\text{ref}} = 300\,\mu\text{m}$ (passes 50 mesh)
   * Coarse cut: $d_{50} = 600\,\mu\text{m}$ (passes 30 mesh)
3. **Transport Accessibility Factor**:
   $$\phi_d = \left(\frac{d_{\text{ref}}}{d_{50}}\right)^\alpha \quad (\alpha \in [0.5, 2.0])$$

### B. Track B: Food-Processor Comminution of Fresh Rind
Track B eliminates the energy-intensive pre-drying step, processing fresh peel directly from juice extraction:

1. **Comminution Procedure**: Fresh passion fruit peels (rind + albedo, residual moisture $X_{w,0} \approx 81\text{--}86\%$) are charged into a commercial food processor equipped with S-curved stainless steel blades. Peels are pulsed in 15-second cycles to generate uniform fragments with characteristic dimension $d_{50} \in [500, 2000]\,\mu\text{m}$.
2. **Specific Interfacial Area**:
   $$a_s = \frac{6}{\rho_s \cdot d_{50}} \cdot \Phi_s \quad [\text{m}^2/\text{kg}]$$
   where $\Phi_s \approx 0.65$ is the sphericity shape factor of shredded fragments.
3. **Slurry Formulation**:
   * Fresh rind wet mass: $m_{\text{fresh}}$ (e.g., $100.0\text{ g}$)
   * Extraction water mass: $m_{\text{water}}$ (e.g., $500.0\text{ g}$)
   * Effective liquid-to-solid ratio on dry basis:
     $$\text{LSR} = \frac{m_{\text{water}} + m_{\text{fresh}} \cdot X_{w,0}}{m_{\text{fresh}} \cdot (1 - X_{w,0})} \approx 30\text{--}40\text{ mL/g}_{\text{dry}}$$
   * Initial acidification: Acidified to setpoint pH ($1.5 - 3.0$) using food-grade citric acid ($0.05 - 0.20\text{ M}$) or $0.1\text{ M HCl}$.

---

## 3. Extraction Reaction Operations & Physical Mechanisms

```text
               TRACK A                                       TRACK B
      THERMAL ACID HYDROLYSIS                        ULTRASOUND-ASSISTED (UAE)
   ┌─────────────────────────────┐               ┌─────────────────────────────┐
   │ Convective & Conductive     │               │ Acoustic Cavitation (40 kHz)│
   │ Heat Transfer from Jacket   │               │ Transient Bubble Collapse   │
   │ Steady Bulk Shear Agitation │               │ Localized Microjets         │
   │ Arrhenius-Driven Kinetics   │               │ Enhanced Mass Transfer      │
   └─────────────────────────────┘               └─────────────────────────────┘
```

### A. Track A: Jacketed Stirred Glass Reactor
* **Vessel Geometry**: $0.5\text{--}2.0\text{ L}$ torispherical-bottom borosilicate vessel equipped with an outer heating/cooling jacket.
* **Agitation Mechanics**: Overhead mechanical stirrer with a PTFE anchor or $45^\circ$ pitched-blade turbine operating at $250 - 400\text{ RPM}$. This eliminates stagnation zones in high-viscosity mucilaginous pectin slurries.
* **Thermal History Tracking**: Class-A PT100 RTD probe immersed in the core slurry volume logs real-time temperature at $\ge 0.1\text{ Hz}$.
* **Reaction Kinetics**: Modeled via reference Arrhenius formulation ($T_{\text{ref}} = 353.15\text{ K}$, $\text{pH}_{\text{ref}} = 2.0$):
  $$k_i = k_{i,\text{ref}} \exp\left[-\frac{E_i}{R}\left(\frac{1}{T_K} - \frac{1}{T_{\text{ref}}}\right)\right] 10^{n_i(\text{pH}_{\text{ref}} - \text{pH})}$$

### B. Track B: Ultrasound Bath Chamber (UAE)
* **Acoustic Field**: $40\text{ kHz}$ piezoelectric ultrasonic transducer array mounted to the base of an isothermal water bath.
* **Acoustic Power Coupling**:
  Distinguishes nominal electrical input power from delivered acoustic power:
  $$P_{\text{acoustic}} = \eta_{\text{coupling}} \cdot P_{\text{elec}}$$
  where $P_{\text{elec}} \in [50, 300]\text{ W}$ and $\eta_{\text{coupling}} \in [0.15, 0.35]$ is the electro-acoustic calorimetric efficiency.
* **Cavitation Kinetics Enhancement**:
  Acoustic cavitation generates transient micro-bubbles whose violent implosions disrupt plant parenchymal cell walls and strip boundary-layer diffusion resistance:
  $$\psi_{US} = 1.0 + \kappa_{US} \left(\frac{P_{\text{acoustic}}}{V_{\text{slurry}}}\right)^{\beta_{US}} \left(\frac{40\text{ kHz}}{f_{US}}\right)^{\gamma_{US}}$$
  Effective extraction rate: $k_{\text{ext,UAE}} = k_{\text{ext,\text{chem}}} \cdot \psi_{US} \cdot \phi_d$.
* **Acoustic Dissipation & Slurry Thermal Decoupling**:
  All dissipated acoustic energy converts to sensible heat:
  $$Q_{US} = P_{\text{acoustic}} \quad [\text{W}]$$
  Dynamic slurry energy balance:
  $$\rho C_p V_{\text{slurry}} \frac{dT_{\text{slurry}}}{dt} = U A (T_{\text{bath}} - T_{\text{slurry}}) + P_{\text{acoustic}}$$
  *Experimental Requirement*: To decouple thermal acceleration from genuine acoustic cavitation, the physical campaign executes paired thermal controls:
  $$\text{UAE Net Kinetic Benefit} = Y_{\text{UAE}}(T_{\text{slurry}}, P_{\text{elec}}) - Y_{\text{thermal}}(T_{\text{slurry}}, P_{\text{elec}} = 0)$$

---

## 4. Solid / Liquid Separation & Aliquot Mass Balance

Immediately following extraction, the hot slurry must be separated into spent solids and clear pectin liquor.

```text
                  EXTRACTED SLURRY
                         │
                         ▼
             Solid / Liquid Filtration
      (100-mesh nylon bag + vacuum Büchner)
                         │
       ┌─────────────────┴─────────────────┐
       ▼                                   ▼
  SPENT RESIDUE                      TOTAL FILTRATE
 (Wet cake solids)                m_filtrate_total (g)
                                           │
                         ┌─────────────────┴─────────────────┐
                         ▼                                   ▼
                  AT-LINE ALIQUOT                   MAIN RECOVERY STREAM
             m_analytical_aliquot (g)            m_precipitation_stream (g)
             (~10-15 g for colorimetry)          (Bulk liquor to precipitation)
```

### Strict Mass-Balance Inventory
To ensure mathematical consistency across analytical concentrations and gravimetric yields:
1. **Gross Filtrate**: $m_{\text{filtrate\_total}} = m_{\text{analytical\_aliquot}} + m_{\text{precipitation\_stream}}$.
2. **Aliquot Withdrawal**: An aliquot ($10.0\text{ g}$) is immediately withdrawn and cooled to $20^\circ\text{C}$ for at-line spectrophotometry.
3. **Stream Scaling**: The dry mass of precipitate obtained from $m_{\text{precipitation\_stream}}$ is mathematically scaled to the total filtrate basis:
   $$m_{\text{dry\_precipitate,scaled}} = m_{\text{dry\_precipitate,recovered}} \cdot \left(\frac{m_{\text{filtrate\_total}}}{m_{\text{precipitation\_stream}}}\right)$$

---

## 5. Analytical Chemistry Standard Operating Procedures (SOPs)

### A. Track A: Primary Offline Reference Assays

#### SOP A-1: Alcohol Insoluble Residue (AIR) Gravimetric Yield
1. Mix $10.0\text{ mL}$ of quenched extract with $20.0\text{ mL}$ of $96\%\,(\text{v/v})$ ethanol.
2. Incubate at $4^\circ\text{C}$ for 2 hours to achieve full polymer flocculation.
3. Centrifuge at $4,000 \times g$ for 10 minutes. Decant supernatant.
4. Wash pellet twice with $15\text{ mL}$ of $70\%\,(\text{v/v})$ ethanol to leach monosaccharides and organic acids.
5. Dry pellet at $60^\circ\text{C}$ under vacuum ($100\text{ mbar}$) to constant weight. Precision target: $\sigma \le 1.0\%$.

#### SOP A-2: Degree of Esterification (DE) via USP Double-Titration
1. Dissolve $100.0\text{ mg}$ of dried pectin in $50.0\text{ mL}$ of $\text{CO}_2$-free deionized water. Add 2 drops of phenol red indicator.
2. Titrate free carboxyl groups with standardized $0.100\text{ M NaOH}$ to the persistent pink endpoint ($V_1$).
3. Add exactly $10.0\text{ mL}$ of $0.250\text{ M NaOH}$, stopper tightly, and stir at $25^\circ\text{C}$ for 15 minutes to saponify methyl-ester groups.
4. Add exactly $10.0\text{ mL}$ of $0.250\text{ M HCl}$ to neutralize excess base.
5. Titrate liberated carboxyl groups with $0.100\text{ M NaOH}$ to endpoint ($V_2$).
6. Calculate:
   $$DE = \frac{V_2}{V_1 + V_2} \times 100\% \quad (\text{Target } \sigma \le 2.0\%)$$

#### SOP A-3: Molecular Weight via HPSEC-MALLS-RI
* Column: Agilent PL aquagel-OH 40/50 guard and analytical series.
* Mobile Phase: $0.1\text{ M NaNO}_3 + 0.02\%\,\text{NaN}_3$ at $0.5\text{ mL/min}$, $35^\circ\text{C}$.
* Detection: Multi-Angle Laser Light Scattering (MALLS, $\lambda = 658\text{ nm}$) + Differential Refractive Index ($dn/dc = 0.146\text{ mL/g}$).
* Target Precision: $\sigma \le 15,000\text{ Da}$ at $500\text{ kDa}$.

---

### B. Track B: At-Line Colorimetric Soft Sensors (IO Rodeo 8-Channel)

Track B deploys rapid, calibrated soft sensors on the filtered liquor prior to alcohol precipitation.

#### SOP B-1: Galacturonic Acid (GalA) Carbazole Multi-Channel Assay
* Principle: Uronic acids heated in concentrated sulfuric acid form 5-formyl-2-furancarboxylic acid, which condenses with carbazole to yield a pink chromophore (absorption band peaking near $530\text{ nm}$).
* Multi-Channel Vector Detection: The IO Rodeo Multichannel Colorimeter reads 8 discrete visible channels:
  $$\mathbf{A} = [A_{415}, A_{445}, A_{480}, A_{515}, A_{555}, A_{590}, A_{630}, A_{680}]$$
  The carbazole peak is captured via the dual-channel bracket $[A_{515}, A_{555}]$, while $A_{680}$ captures optical turbidity/scattering from residual suspended colloids.
* Reagent Preparation:
  - Reagent A: Sodium tetraborate ($0.025\text{ M}$) in concentrated $\text{H}_2\text{SO}_4$ ($98\%$).
  - Reagent B: Carbazole ($0.1\%\,\text{w/v}$) in absolute ethanol.
* Assay Execution:
  1. Pipette $0.5\text{ mL}$ of diluted extract into a borosilicate tube resting in ice water.
  2. Add $3.0\text{ mL}$ of Reagent A. Vortex gently.
  3. Heat in a boiling water bath ($100^\circ\text{C}$) for exactly 10 minutes. Cool to room temperature.
  4. Add $0.1\text{ mL}$ of Reagent B. Vortex thoroughly.
  5. Allow color development in the dark for 15 minutes.
  6. Transfer to standard $10\text{ mm}$ cuvette and insert into the IO Rodeo instrument.
* Multi-Channel Vector Model:
  $$C_{\text{GalA,measured}} = a \cdot A_{515} + b \cdot A_{555} + c \cdot A_{680} + d \quad [\text{mg/L}]$$
  $$C_{\text{GalA,filtrate}} = C_{\text{GalA,measured}} \times DF$$

#### SOP B-2: Copper-Chelate Pectin-Equivalent Assay
* Principle: Intact pectin forms a soluble coordination complex with $\text{Cu}^{2+}$ ions at alkaline pH, altering copper d-d transition absorption at $590\text{ nm}$.
* Designation: Explicitly recorded as **Pectin-Equivalent Concentration** ($C_{\text{pectin-equiv}}$) until validated against gravimetric reference standards.
* Multi-Channel Readout:
  $$C_{\text{pectin-equiv,measured}} = \frac{A_{590} - A_{0,\text{Cu}}}{S_{\text{Cu}}} \quad [\text{mg/L}]$$
  $$C_{\text{pectin-equiv,filtrate}} = C_{\text{pectin-equiv,measured}} \times DF$$

#### SOP B-3: Dilution Scheme & Calibration Range Control
* Reference Range: Analytical calibration curve valid from $0\text{ to } 400\text{ mg/L}$ (recommended linear zone: $25\text{--}300\text{ mg/L}$).
* Expected Filtrate Concentration: $3,000\text{--}8,000\text{ mg/L}$ total pectin.
* Standard Dilution Factor: $DF = 20\times\text{ or } 50\times$ using deionized water.
* Range Enforcement: If $C_{\text{measured}} > C_{\text{max,linear}}$, the software automatically flags:
  > *"Reading exceeds validated calibration range. Increase dilution factor by $2.5\times$."*

---

## 6. Downstream Product Recovery & Vacuum Drying

Following analytical aliquoting, the main filtrate stream ($m_{\text{precipitation\_stream}}$) enters recovery:

1. **Alcohol Precipitation**: Chilled $96\%\,(\text{v/v})$ ethanol is added at a $2:1\text{ (v/v)}$ ratio under vigorous mechanical stirring. Pectin agglomerates into a fibrous floating curd.
2. **Equilibration**: Allowed to stand at $4^\circ\text{C}$ for 60 minutes to complete precipitation.
3. **Cake Separation**: Vacuum filtration through a coarse sintered glass funnel or Miracloth.
4. **Ethanol Wash**: Pellet is washed once with $70\%\,(\text{v/v})$ ethanol to rinse trapped monosaccharides.
5. **Low-Temperature Vacuum Oven Drying**:
   * *Critical Requirement*: Avoid high thermal exposure ($> 60^\circ\text{C}$), which causes thermal degradation, loss of ester groups, and caramelization of co-precipitated sugars.
   * *Operating Profile*: $45^\circ\text{C}$ at $50\text{--}100\text{ mbar}$ vacuum for 12 hours until constant weight ($m_{\text{dry\_precipitate}}$).

---

## 7. Dual-Target Performance Metric: GalA Composition Indicator

Track B provides two independent recovery perspectives:
1. **Chemical Recovery** (GalA extracted in liquor):
   $$m_{\text{GalA,total}} = C_{\text{GalA,filtrate}} \cdot \left(\frac{m_{\text{filtrate\_total}}}{\rho_{\text{filtrate}}}\right) \cdot 10^{-3} \quad [\text{g}]$$
2. **Gravimetric Solids Recovery** (Dry precipitate mass):
   $$m_{\text{dry\_precipitate,scaled}} = m_{\text{dry\_precipitate,recovered}} \cdot \left(\frac{m_{\text{filtrate\_total}}}{m_{\text{precipitation\_stream}}}\right) \quad [\text{g}]$$
3. **GalA-Based Composition / Purity Indicator**:
   $$I_{\text{GalA}} = \frac{m_{\text{GalA,total}}}{m_{\text{dry\_precipitate,scaled}}}$$

### Diagnostic Interpretation Table

| Indicator Range ($I_{\text{GalA}}$) | Chemical Interpretation | Digital Twin Feedback |
| :--- | :--- | :--- |
| **$I_{\text{GalA}} \ge 0.75$** | **High-Purity Pectin Extraction**: Extract is rich in intact homogalacturonan with minimal co-extracted non-pectic solids. | Extraction severity is optimal; hydrolysis and degradation are restrained. |
| **$0.55 \le I_{\text{GalA}} < 0.75$** | **Standard Crude Pectin**: Normal commercial-grade precipitate containing expected neutral side chains and trace polyphenols. | Baseline operating zone. |
| **$I_{\text{GalA}} < 0.55$** | **High Co-Extractive Burden**: Bulk precipitate mass is inflated by co-extracted free sugars, hemicelluloses, proteins, or salts. | Warns against false "high-yield" conclusions; prompts adjustment of acidity or ethanol washing. |
