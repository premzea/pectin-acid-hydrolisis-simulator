# Domain 1: Biochemical Engineering & Physical Extraction Protocols

**Document Version**: 2.1 (Incorporating Engineering Peer Review)  
**Parent Document**: [`MASTER_DUAL_TRACK_SPECIFICATION.md`](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/MASTER_DUAL_TRACK_SPECIFICATION.md)  
**Target Audience**: Chemical Engineers, Biochemists, Food Technologists, Wet-Lab Operators

---

## 1. Executive Scope & Chemistry Fundamentals

Pectin extraction from passion-fruit (*Passiflora edulis*) peel involves the solubilization and selective chain scission of protopectin anchored within the cell-wall matrix of the pericarp and albedo. Structurally, passion fruit pectin consists predominantly of a **homogalacturonan (HG)** backbone ($\alpha$-(1 $\to$ 4)-linked D-galacturonic acid units), partially methyl-esterified at the C-6 carboxyl group, with neutral sugar side chains (arabinan, galactan, rhamnogalacturonan-I).

This document establishes the physical unit operations, chemical kinetic mechanisms, analytical chemistry standard operating procedures (SOPs), and recovery protocols across both operational tracks, incorporating rigorous peer-review controls:
* **Track A**: Standardized dried peel, closed jacketed stirred reactor with reflux condensation, active pH tracking/dosing, multi-timepoint thermal quenching, and offline reference assays.
* **Track B**: Fresh rind comminution, 40-kHz ultrasound-assisted extraction (UAE) with thermal baseline controls, at-line multi-timepoint spectrophotometry with sample-blank matrix correction, and low-temperature vacuum oven product recovery.

---

## 2. Biomass Conditioning & Comminution Submodels

### A. Track A: Convective Drying & Precision Sieving
To isolate chemical reaction kinetics from raw fruit moisture variations ($X_{w,0} \approx 81 - 86\%$), Track A uses a standardized dry powder:

1. **Forced-Air Dehydration**: Fresh peels are sliced into $2 \times 2\text{ cm}$ strips and dried in a forced-air convection oven at $60^\circ\text{C}$ for 16–24 hours until reaching stable equilibrium moisture ($X_w \approx 0.06 - 0.08\text{ g/g wb}$).
2. **Knife Milling & ASTM Classification**: Dried peels are pulverized using a rotary knife mill and sieved through stacked ASTM testing sieves:
   * Fine cut: $d_{50} = 150\,\mu\text{m}$ (ASTM 100)
   * Reference standard: $d_{\text{ref}} = 300\,\mu\text{m}$ (ASTM 50)
   * Coarse cut: $d_{50} = 600\,\mu\text{m}$ (ASTM 30)
3. **Transport Accessibility Factor**:
   $$\phi_d = \left(\frac{d_{\text{ref}}}{d_{50}}\right)^\alpha \quad (\alpha \in [0.5, 2.0])$$

### B. Track B: Food-Processor Comminution of Fresh Rind
Track B eliminates the energy-intensive pre-drying step, processing fresh peel directly from juice extraction:

1. **Comminution Procedure**: Fresh passion fruit peels (rind + albedo, residual moisture $X_{w,0} \approx 81\text{--}86\%$) are charged into a commercial food processor equipped with S-curved stainless steel blades. Peels are pulsed in 15-second cycles to generate uniform fragments with characteristic dimension $d_{50} \in [500, 2000]\,\mu\text{m}$.
2. **Specific Interfacial Area**:
   $$a_{s,\text{fresh}} = \frac{6}{\rho_s \cdot d_{50}} \cdot \Phi_{s,\text{fresh}} \quad [\text{m}^2/\text{kg}]$$
   where $\Phi_{s,\text{fresh}} \approx 0.65$ is the sphericity shape factor of fresh shredded fragments.
3. **Cross-Track Harmonization & Tissue Matrix Factor**:
   Drying collapses cellular porosity and hornifies pectin fibrils. To harmonize the transport scaling across tracks without conflating physical mechanisms:
   $$\phi_{d,\text{eff}} = \left(\frac{d_{\text{ref}}}{d_{50}}\right)^\alpha \cdot \Omega_{\text{matrix}}$$
   where $\Omega_{\text{matrix}} \equiv 1.0$ for standardized dried peel (Track A) and $\Omega_{\text{matrix}} = \Omega_{\text{fresh}} \approx 1.25\text{--}1.60$ for fresh uncollapsed cellular parenchyma (Track B), identified via fresh-tissue thermal control runs.
4. **Slurry Formulation**:
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
   │ Reflux Condenser Sealed     │               │ Acoustic Cavitation (40 kHz)│
   │ Convective & Conductive Heat│               │ Transient Bubble Collapse   │
   │ Steady Bulk Shear Agitation │               │ Dual T (Bath & Slurry RTD)  │
   │ Active pH Logging / Dosing  │               │ Matched Thermal Baseline    │
   └─────────────────────────────┘               └─────────────────────────────┘
```

### A. Track A: Jacketed Stirred Glass Reactor (Engineering Hardening)
1. **Reflux Evaporation Control**:
   * *Critical Engineering Control*: To prevent water vapor loss at $95^\circ\text{C}$ over 120 min (which causes progressive concentration drift of acid molarity and slurry density), the reactor head is fitted with a **water-cooled Dimroth/Graham reflux condenser** operated with $15^\circ\text{C}$ coolant. Evaporative volume loss is maintained at $< 0.2\%$ over 2 hours.
2. **Active pH Mode & Carboxyl Group Tracking**:
   * Saponification of methyl esters during extraction releases free galacturonic carboxyl groups ($-\text{COOH}$), causing acid-base drift.
   * *Protocol*: The reactor logs continuous $\text{pH}(t)$ via an autoclavable glass combination electrode. For constant-pH studies, an automated peristaltic micro-dosing pump dispenses $0.25\text{ M NaOH}$ / $0.25\text{ M citric acid}$. If un-dosed, the continuous $\text{pH}(t)$ trajectory is explicitly ingested into the numerical kinetic integral $\tau_k = \int_0^t k(T(s), \text{pH}(s))\,ds$.
3. **Vessel Working Volume & Aliquot Budget Constraints**:
   * Nominal vessel size: $2.0\text{ L}$ (preferred working volume: $1.2\text{--}1.5\text{ L}$).
   * For a $1.2\text{ L}$ charge, 4 aliquots $\times 12.0\text{ mL} = 48.0\text{ mL}$ total ($4.0\%$ cumulative withdrawal, strictly meeting the $< 5\%$ non-destructive limit).
   * For $0.5\text{ L}$ bench vessels, micro-centrifuge aliquots of $3.5\text{ mL}$ ($14.0\text{ mL}$ total $= 2.8\%$) are enforced, and dynamic liquid volume scaling is updated at every step:
     $$V_{\text{reactor}}(t_{k+1}) = V_{\text{reactor}}(t_k) - V_{\text{aliquot},k}$$
4. **Thermal Quenching Protocol**:
   * Aliquots ($10 - 12\text{ mL}$) are withdrawn into **thin-walled stainless-steel immersion vials** pre-chilled in a circulated glycol-water bath at $-10^\circ\text{C}$.
   * Rapid mechanical swirling cools the slurry from $95^\circ\text{C}$ to $< 25^\circ\text{C}$ in $15 \pm 3\text{ seconds}$ (verified by micro-thermocouple). The verified quench cooling transient is logged and accounted for in early timepoints ($t=15\text{ min}$).

---

### B. Track B: Ultrasound Bath Chamber (UAE) & Thermal Baseline
1. **Acoustic Field & Transducer Configuration**:
   * $40\text{ kHz}$ piezoelectric transducer array bonded to the tank base, delivering nominal electrical power $P_{\text{elec}} \in [50, 300]\text{ W}$.
   * Frequency exponent $\gamma_{US}$ is **fixed to $\gamma_{US} \equiv 1.0$** from literature consensus (single-frequency 40 kHz systems cannot identify frequency scaling).
2. **Calorimetric Acoustic Power & Sensible Heat Fraction**:
   * Acoustic power delivered to the fluid is determined by solvent water calorimetry:
     $$P_{\text{acoustic}} = m_{\text{cal}} C_p \left(\frac{dT}{dt}\right)_{\text{initial}}$$
     giving coupling efficiency $\eta_{\text{coupling}} = P_{\text{acoustic}} / P_{\text{elec}} \approx 0.18\text{--}0.32$.
   * Sensible heat dissipation fraction $\xi_{\text{thermal}} \approx 0.88$ (the remaining $12\%$ performs cavitational mechanical shear, cell disruption, and acoustic streaming work):
     $$Q_{US} = \xi_{\text{thermal}} \cdot P_{\text{acoustic}}$$
3. **RTD Placement & Ultrasonic Artifact Suppression**:
   * Slurry PT100 probe is housed in a thin PTFE vibration-damping sleeve positioned centrally in the vessel, $3\text{ cm}$ above the bottom, avoiding acoustic standing wave antinodes.
   * Readings are validated by brief 5-second acoustic power pauses at sampling intervals.
4. **Mandatory In-Track Thermal Control Run**:
   * *Critical Engineering Control*: To prevent confounding ultrasound cavitation with fresh-vs-dried feedstock matrix differences, Track B includes mandatory **Fresh-Rind Thermal Baseline Runs** ($P_{\text{elec}} = 0\text{ W}$, identical fresh slurry, heated in the same bath):
     $$\text{Pure Acoustic Enhancement} = Y_{\text{UAE,fresh}}(T, P_{\text{elec}}) - Y_{\text{thermal,fresh}}(T, P_{\text{elec}} = 0)$$

---

## 4. Solid / Liquid Separation & Aliquot Mass Balance

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
2. **Time-Resolved Sampling Schedule for Track B**:
   Rather than relying on a single endpoint, Track B extracts $5.0\text{ mL}$ micro-aliquots through an in-situ PTFE dip tube at:
   $$t \in \{10, 20, 40, 60\}\text{ minutes}$$
   providing full trajectory resolution for $k_{\text{ext,UAE}}$ within a single batch run.
3. **Stream Scaling**:
   $$m_{\text{dry\_precipitate,scaled}} = m_{\text{dry\_precipitate,recovered}} \cdot \left(\frac{m_{\text{filtrate\_total}}}{m_{\text{precipitation\_stream}}}\right)$$

---

## 5. Analytical Chemistry Standard Operating Procedures (SOPs)

### A. Track A: Primary Offline Reference Assays

#### SOP A-1: Alcohol-Precipitated Soluble Pectin (APSP) Gravimetric Yield
*(Formerly labeled "AIR gravimetric" — renamed to eliminate food science ambiguity with matrix insoluble residue)*:
1. Centrifuge the quenched reaction slurry at $4,000 \times g$ for 15 minutes to separate clear supernatant liquor from spent solid cake.
2. Mix $10.0\text{ mL}$ of supernatant liquor with $20.0\text{ mL}$ of absolute ethanol ($2:1\text{ v/v}$, final ethanol $\ge 64\%$).
3. Incubate at $4^\circ\text{C}$ for 2 hours for complete flocculation.
4. Filter precipitate through pre-weighed Whatman GF/A glass microfiber filters.
5. Wash twice with $15\text{ mL}$ of $70\%\,(\text{v/v})$ ethanol to leach monosaccharides, organic acids, and salts.
6. Dry filter cake at $60^\circ\text{C}$ under vacuum ($100\text{ mbar}$) to constant weight. Precision target: $\sigma \le 1.0\%$.

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

#### SOP B-1: GalA Carbazole Assay with Sample-Blank Matrix Correction
* *Matrix Pigment Interference Problem*: Passion fruit peel extract carries flavonoids and carotenoids absorbing in the $450\text{--}550\text{ nm}$ region. Turbidity correction at $680\text{ nm}$ removes scattering but does not correct for native dissolved pigments.
* *Sample-Blank Protocol*:
  For every extract sample, two tubes are prepared:
  1. **Color Development Tube**: Sample + Sulfuric Acid/Tetraborate ($100^\circ\text{C}$, 10 min) + Carbazole Reagent.
  2. **Sample-Blank Tube**: Sample + Sulfuric Acid/Tetraborate ($100^\circ\text{C}$, 10 min) + Pure Ethanol (no carbazole).
* *Net Absorbance Vector*:
  $$\mathbf{A}_{\text{net}}(\lambda) = \mathbf{A}_{\text{developed}}(\lambda) - \mathbf{A}_{\text{sample\_blank}}(\lambda) - A_{\text{turbidity}}(680) \cdot \left(\frac{680}{\lambda}\right)^{\alpha_{\text{Rayleigh}}}$$
* Multi-Channel Vector Model:
  $$C_{\text{GalA,measured}} = a \cdot A_{\text{net}}(515) + b \cdot A_{\text{net}}(555) + c \cdot A_{\text{net}}(680) + d \quad [\text{mg/L}]$$
  $$C_{\text{GalA,filtrate}} = C_{\text{GalA,measured}} \times DF$$

#### SOP B-2: Matrix-Spike Recovery Validation
During each analytical batch, a real passion fruit extract is spiked with analytical D-galacturonic acid ($+50\text{ mg/L}$ and $+100\text{ mg/L}$). Recovery must fall within $95\%\text{--}105\%$:
$$\text{Spike Recovery} = \frac{C_{\text{spiked}} - C_{\text{unspiked}}}{C_{\text{added}}} \times 100\%$$

#### SOP B-3: Copper-Chelate Pectin-Equivalent Assay
* Principle: Intact pectin forms a soluble coordination complex with $\text{Cu}^{2+}$ ions at alkaline pH, altering copper d-d transition absorption at $590\text{ nm}$.
* Designation: Explicitly recorded as **Pectin-Equivalent Concentration** ($C_{\text{pectin-equiv}}$) until validated against gravimetric reference standards.
* Multi-Channel Readout:
  $$C_{\text{pectin-equiv,measured}} = \frac{A_{\text{net}}(590) - A_{0,\text{Cu}}}{S_{\text{Cu}}} \quad [\text{mg/L}]$$
  $$C_{\text{pectin-equiv,filtrate}} = C_{\text{pectin-equiv,measured}} \times DF$$

---

## 6. Downstream Product Recovery & Vacuum Drying

1. **Alcohol Precipitation**: Chilled $96\%\,(\text{v/v})$ ethanol is added at a $2:1\text{ (v/v)}$ ratio under vigorous mechanical stirring. Pectin agglomerates into a fibrous floating curd.
2. **Equilibration**: Allowed to stand at $4^\circ\text{C}$ for 60 minutes to complete precipitation.
3. **Cake Separation**: Vacuum filtration through a coarse sintered glass funnel or Miracloth.
4. **Ethanol Wash**: Pellet is washed once with $70\%\,(\text{v/v})$ ethanol to rinse trapped monosaccharides.
5. **Low-Temperature Vacuum Oven Drying**:
   * *Critical Control*: Operating at $45^\circ\text{C}$ and $50\text{--}100\text{ mbar}$ vacuum for 12 hours ensures rapid ethanol evaporation without thermal degradation or Maillard browning.

---

## 7. Dual-Target Performance Metric: GalA Composition Indicator

1. **Chemical Recovery** (GalA extracted in liquor):
   $$m_{\text{GalA,total}} = C_{\text{GalA,filtrate}} \cdot \left(\frac{m_{\text{filtrate\_total}}}{\rho_{\text{filtrate}}}\right) \cdot 10^{-3} \quad [\text{g}]$$
2. **Gravimetric Solids Recovery** (Dry precipitate mass):
   $$m_{\text{dry\_precipitate,scaled}} = m_{\text{dry\_precipitate,recovered}} \cdot \left(\frac{m_{\text{filtrate\_total}}}{m_{\text{precipitation\_stream}}}\right) \quad [\text{g}]$$
3. **GalA-Based Composition / Purity Indicator**:
   $$I_{\text{GalA}} = \frac{m_{\text{GalA,total}}}{m_{\text{dry\_precipitate,scaled}}}$$
