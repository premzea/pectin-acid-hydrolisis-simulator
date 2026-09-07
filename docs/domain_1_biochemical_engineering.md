# Domain 1: Biochemical Engineering & Physical Extraction Protocols

**Document Version**: 3.1 (Ultrasound-Assisted Acid Extraction Framing)  
**Parent Document**: [`MASTER_DUAL_TRACK_SPECIFICATION.md`](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/MASTER_DUAL_TRACK_SPECIFICATION.md)  
**Target Audience**: Chemical Engineers, Biochemists, Food Technologists, Wet-Lab Operators

---

## 1. Executive Scope & Chemistry Fundamentals

Pectin extraction from passion-fruit (*Passiflora edulis*) peel involves the solubilization and selective chain scission of protopectin anchored within the cell-wall matrix of the pericarp and albedo. Structurally, passion fruit pectin consists predominantly of a **homogalacturonan (HG)** backbone ($\alpha$-(1 $\to$ 4)-linked D-galacturonic acid units), partially methyl-esterified at the C-6 carboxyl group, with neutral sugar side chains (arabinan, galactan, rhamnogalacturonan-I).

### The Shared Acid-Medium Mechanism
A critical scientific principle governs both tracks:
> **Ultrasound-Assisted Extraction (UAE) is not an alternative extraction chemistry. It is ultrasound-enhanced acid extraction in an acidified aqueous solvent.**

Low pH (food-grade citric acid, $\text{pH } 1.5\text{--}3.0$) provides the chemical driving force for:
1. Protonation of carboxylate ions, neutralizing negative charge repulsion.
2. Acid-catalyzed cleavage of covalent and ionic bonds anchoring protopectin to cellulose and hemicellulose microfibrils.
3. Partial de-esterification and chain scission of the solubilized polymer.

Track A and Track B share the **exact same fresh passion-fruit rind** and the **exact same citric acid medium**. Track A identifies the baseline thermal-acid response, while Track B introduces ultrasound to accelerate mass transfer and tissue permeabilization.

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
```

---

## 2. Common Fresh-Rind Conditioning Protocol

1. **Feedstock Selection**: Peels from ripe purple passion fruit (*Passiflora edulis*) are rinsed with deionized water to remove residual pulp and dirt, and drained.
2. **Moisture Determination**: Three representative $5.0\text{ g}$ subsamples are tested using a halogen moisture analyzer ($105^\circ\text{C}$ to constant weight) to record the precise batch moisture fraction:
   $$X_{w,0} \in [0.81, 0.86] \quad (\text{logged per physical batch})$$
   Dry biomass equivalent:
   $$m_{\text{dry}} = m_{\text{fresh}} \cdot (1 - X_{w,0})$$
3. **Standardized Comminution**: Peels are charged into a commercial food processor equipped with S-curved stainless-steel blades. Peels are pulsed in three 15-second cycles with 5-second rest intervals to achieve a characteristic fragment size $d_{50} \in [500, 1500]\,\mu\text{m}$.
4. **Slurry Preparation**:
   * Wet rind mass: $m_{\text{fresh}}$ (e.g., $100.0\text{ g}$ fresh rind $\approx 15.0\text{--}18.0\text{ g}$ dry matter)
   * Deionized water: $m_{\text{water}}$ (e.g., $500.0\text{ g}$)
   * Effective liquid-to-solid ratio:
     $$\text{LSR} = \frac{m_{\text{water}} + m_{\text{fresh}} \cdot X_{w,0}}{m_{\text{dry}}} \approx 30\text{--}35\text{ mL/g}_{\text{dry}}$$
   * Acidification: Brought to setpoint pH ($1.5\text{--}3.0$) using food-grade citric acid ($0.05\text{--}0.20\text{ M}$) or $0.1\text{ M HCl}$.

---

## 3. Extraction Operations: Thermal vs. Acoustic-Acid Physics

### A. Track A: Thermal Acid Extraction (Mechanistic Reference)
* **Vessel**: $1.2\text{--}2.0\text{ L}$ torispherical jacketed borosilicate glass vessel.
* **Reflux Vapor Control**: Fitted with a water-cooled Dimroth/Graham condenser ($15^\circ\text{C}$ coolant) guaranteeing $< 0.2\%$ evaporative loss over 120 minutes.
* **Agitation**: Overhead mechanical stirrer with a PTFE anchor or pitched-blade turbine ($250\text{--}400\text{ RPM}$).
* **Instrumentation**: Submerged Class-A PT100 RTD ($\ge 0.1\text{ Hz}$) logging thermal exposure $\tau_k = \int k(T, \text{pH})\,ds$; continuous glass pH electrode logging.
* **Aliquot Budget**: Minimum working volume $\ge 1.2\text{ L}$. Four aliquots $\times 12.0\text{ mL} = 48.0\text{ mL} \le 4.0\%$ cumulative withdrawal.
* **Thermal Quenching**: Aliquots drawn into thin-walled stainless-steel immersion vials in a $-10^\circ\text{C}$ glycol bath, cooling to $< 25^\circ\text{C}$ in $15 \pm 3\text{ seconds}$.

### B. Track B: Ultrasound-Assisted Acid Extraction (UAE)
* **Acoustic Field**: $40\text{ kHz}$ transducer array bonded to tank base, delivering nominal electrical power $P_{\text{elec}} \in [50, 300]\text{ W}$.
* **Dual Physical Action of Ultrasound**:
  1. *Solubilization Acceleration*: Transient acoustic cavitation bubbles collapse near plant cell surfaces, creating microjets ($v > 100\text{ m/s}$) that perforate parenchymal cell walls and strip boundary-layer mass-transfer resistance ($k_{\text{ext}}^{\text{US}} > k_{\text{ext}}^{\text{thermal}}$).
  2. *Polymer Degradation Risk*: Intense hydrodynamic shear stresses and localized thermal hotspots around collapsing cavities can induce chain scission of solubilized pectin molecules ($k_{\text{hyd}}^{\text{US}} \ge k_{\text{hyd}}^{\text{thermal}}$), reducing molecular weight ($M_w$) and altering $DE$.
* **Quality Optimization Imperative**:
  * *Higher yield is not automatically better.*
  * Aggressive sonication can yield high apparent pectin mass that is severely degraded ($M_w < 100\text{ kDa}$), losing gelling and emulsifying capacity.
  * Tracking **Yield + GalA + DE + Molecular Weight** simultaneously is essential to identify the Pareto-optimal extraction regime.
* **Mandatory Fresh Thermal Control**: Every ultrasound condition is paired with an identical fresh-rind run with sonication turned OFF ($P_{\text{elec}} = 0\text{ W}$) in the same bath at matched fluid temperature.

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

1. **Gross Filtrate**: $m_{\text{filtrate\_total}} = m_{\text{analytical\_aliquot}} + m_{\text{precipitation\_stream}}$.
2. **Stream Scaling**:
   $$m_{\text{dry\_precipitate,scaled}} = m_{\text{dry\_precipitate,recovered}} \cdot \left(\frac{m_{\text{filtrate\_total}}}{m_{\text{precipitation\_stream}}}\right)$$

---

## 5. The Shared Analytical Backbone

Both Track A and Track B feed the **identical analytical backbone**:

$$\boxed{
\text{Gravimetric Recovery } (m_{\text{dry\_precipitate}})
\longleftrightarrow
\text{GalA Concentration } (C_{\text{GalA}})
\longleftrightarrow
\text{Pectin-Equivalent } (C_{\text{pectin-equiv}})
\longleftrightarrow
\text{DE \& } M_w
}$$

### A. Alcohol-Precipitated Soluble Pectin (APSP) Gravimetric Yield
1. Mix $10.0\text{ mL}$ of clear supernatant liquor with $20.0\text{ mL}$ of absolute ethanol ($2:1\text{ v/v}$, final ethanol $\ge 64\%$).
2. Incubate at $4^\circ\text{C}$ for 2 hours for complete flocculation.
3. Filter precipitate through pre-weighed Whatman GF/A glass microfiber filters.
4. Wash twice with $15\text{ mL}$ of $70\%\,(\text{v/v})$ ethanol to rinse soluble impurities.
5. Dry filter cake at $45^\circ\text{C}$ under vacuum ($100\text{ mbar}$) to constant weight ($m_{\text{dry\_precipitate}}$). Target $\sigma \le 1.0\%$.

### B. GalA Carbazole Multi-Channel Assay with Sample-Blank Correction
1. **Sample-Blank Tube**: Extract sample + Sulfuric acid/tetraborate ($100^\circ\text{C}, 10\text{ min}$) + Pure ethanol (no carbazole). Reads native flavonoid/carotenoid pigments.
2. **Color Development Tube**: Extract sample + Sulfuric acid/tetraborate ($100^\circ\text{C}, 10\text{ min}$) + Carbazole reagent. Reads total chromophore.
3. **Net Absorbance Vector**:
   $$\mathbf{A}_{\text{net}}(\lambda) = \mathbf{A}_{\text{developed}}(\lambda) - \mathbf{A}_{\text{sample\_blank}}(\lambda) - A_{\text{turbidity}}(680) \left(\frac{680}{\lambda}\right)^{\alpha_{\text{Rayleigh}}}$$
4. **Multi-Wavelength Model**:
   $$C_{\text{GalA,measured}} = w_1 A_{\text{net}}(515) + w_2 A_{\text{net}}(555) + w_3 A_{\text{net}}(680) + d$$
   $$C_{\text{GalA,filtrate}} = C_{\text{GalA,measured}} \times DF$$
5. **Matrix-Spike Validation**: Spiked recoveries of $+50\text{ mg/L}$ and $+100\text{ mg/L}$ GalA must fall within $95\%\text{--}105\%$.

### C. Copper-Chelate Pectin-Equivalent Assay
* Evaluates intact pectin coordination at $590\text{ nm}$:
  $$C_{\text{pectin-equiv,measured}} = \frac{A_{\text{net}}(590) - A_{0,\text{Cu}}}{S_{\text{Cu}}}$$
  $$C_{\text{pectin-equiv,filtrate}} = C_{\text{pectin-equiv,measured}} \times DF$$

### D. Degree of Esterification (DE) & Molecular Weight ($M_w$)
* $DE$ measured via USP double-titration (saponification with $0.25\text{ M NaOH}$).
* $M_w$ measured via HPSEC-MALLS-RI ($dn/dc = 0.146\text{ mL/g}$).
* *Key Diagnostic Ratio*:
  $$\text{Degradation Index} = \frac{M_{w,\text{UAE}}}{M_{w,\text{thermal}}}$$
  captures whether ultrasound enhancement was achieved without excessive chain scission.

---

## 6. Phase 0 Physical Repeatability Checklist

| Operational Check | Acceptance Target | Diagnostic Procedure |
| :--- | :--- | :--- |
| **Batch Moisture $X_{w,0}$ Repeatability** | Triplicate readings $\text{SD} < 0.005$ | Halogen moisture analyzer (105 °C) |
| **Thermal Control Stability** | $\pm 0.5^\circ\text{C}$ at steady state | Continuous logging at 80 °C for 60 min |
| **pH Stability / Tracking** | Drift $< 0.10\text{ pH}$ units | Autoclavable probe in stirred buffer |
| **Reflux Evaporative Loss** | $< 0.3\%$ mass loss over 120 min | Weighing reactor before and after run at 95 °C |
| **Filtration Mass Recovery** | Filtrate mass repeatability $CV < 2.5\%$ | Standardized Büchner vacuum filtration |
| **Precipitation & Drying** | Dry solids mass $CV < 4.0\%$ | 5 identical aliquots precipitated and vacuum-dried |
| **Colorimeter Reproducibility**| Absorbance repeatability $CV < 1.5\%$ | 5 repeated readings of identical GalA standard |
