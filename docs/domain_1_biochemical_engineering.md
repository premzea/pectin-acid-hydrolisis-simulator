# Domain 1: Biochemical Engineering & Physical Extraction Protocols

**Document Version**: 3.2 (Shared Comminution Provenance with Diverging Pretreatment)  
**Parent Document**: [`MASTER_DUAL_TRACK_SPECIFICATION.md`](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/MASTER_DUAL_TRACK_SPECIFICATION.md)  
**Target Audience**: Chemical Engineers, Biochemists, Food Technologists, Wet-Lab Operators

---

## 1. Executive Scope & Chemistry Fundamentals

Pectin extraction from passion-fruit (*Passiflora edulis*) peel involves the solubilization and selective chain scission of protopectin anchored within the cell-wall matrix of the pericarp and albedo. Structurally, passion fruit pectin consists predominantly of a **homogalacturonan (HG)** backbone ($\alpha$-(1 $\to$ 4)-linked D-galacturonic acid units), partially methyl-esterified at the C-6 carboxyl group, with neutral sugar side chains (arabinan, galactan, rhamnogalacturonan-I).

### The Shared Acid-Medium Mechanism
A critical scientific principle governs both tracks:
> **Ultrasound-Assisted Extraction (UAE) is not an alternative extraction chemistry. It is ultrasound-enhanced acid extraction in an acidified aqueous solvent (citric acid, pH 1.5–3.0).**

Low pH provides the chemical driving force for:
1. Protonation of carboxylate ions, neutralizing negative charge repulsion.
2. Acid-catalyzed cleavage of covalent and ionic bonds anchoring protopectin to cellulose and hemicellulose microfibrils.
3. Partial de-esterification and chain scission of the solubilized polymer.

Both tracks share the same biological starting lot and food-grade citric acid medium, but **diverge in physical feedstock conditioning post-food-processing** to satisfy complementary engineering objectives:
* **Track A** isolates intrinsic chemical kinetics and particle-diffusion limits using standardized **dried, milled, and sieved fractions**.
* **Track B** evaluates ultrasonic cavitation and at-line soft-sensor performance using **fresh, wet fragments**.

---

## 2. Shared Provenance & Diverging Feedstock Protocols

```text
                               FRESH PASSION-FRUIT RIND
                                          │
                        Rinse, Clean, Halogen Moisture Log
                              X_w,0 in [0.81, 0.86]
                                          │
                        Shared Provenance Comminution
                 (Food Processor: 3x15s pulses, 5s rest)
                              Log Lot ID: LOT-YYYYMMDD-X
                                          │
                   ┌──────────────────────┴──────────────────────┐
                   │                                             │
                   ▼                                             ▼
               TRACK A BRANCH                                TRACK B BRANCH
        Drying, Milling & Sieve Sizing                     Fresh Wet Fragments
      - Convective drying: 60 °C to X_w ~ 6-8%           - Direct charge to bath
      - Knife-milled                                     - Measured d50 (laser diffraction
      - ASTM Sieving: d50 in {150, 300, 600} um            or wet sieving) logged as covariate
```

### A. Shared Step 0: Initial Batch Reception & Food-Processor Comminution
1. **Feedstock Selection**: Peels from ripe purple passion fruit (*Passiflora edulis*) are rinsed with deionized water to remove residual pulp and dirt, and drained.
2. **Moisture Determination**: Three representative $5.0\text{ g}$ subsamples are tested using a halogen moisture analyzer ($105^\circ\text{C}$ to constant weight) to record the precise batch moisture fraction:
   $$X_{w,0} \in [0.81, 0.86] \quad (\text{logged per physical batch})$$
   Dry biomass equivalent:
   $$m_{\text{dry}} = m_{\text{fresh}} \cdot (1 - X_{w,0})$$
3. **Standardized Comminution**: Peels are charged into a commercial food processor equipped with S-curved stainless-steel blades. Peels are pulsed in three 15-second cycles with 5-second rest intervals to generate fresh wet fragments ($d_{50} \in [500, 1500]\,\mu\text{m}$).
4. **Lot Registration**: A unique physical lot identifier (`LOT-YYYYMMDD-BATCH`) is assigned to this comminuted material. Both Track A and Track B runs record this lot ID to maintain traceability to a common biological origin.

---

### B. Track A Feedstock Conditioning: Drying, Milling & Sieving
Following food processing, material allocated to Track A undergoes controlled drying and classification:
1. **Forced-Air Drying**: Fresh fragments are spread in a single layer on stainless-steel trays and dried in a forced-air convection oven at $60^\circ\text{C}$ until reaching equilibrium moisture:
   $$X_{w,\text{Track A}} \approx 6.0\text{--}8.0\% \quad (\text{wet basis})$$
2. **Knife-Milling & Sieving**: The dried pericarp/mesocarp is knife-milled and classified through standard ASTM mesh sieves into three discrete granulometric fractions:
   * **Fine fraction**: $d_{50} = 150\,\mu\text{m}$ (ASTM 100)
   * **Reference fraction**: $d_{\text{ref}} = 300\,\mu\text{m}$ (ASTM 50)
   * **Coarse fraction**: $d_{50} = 600\,\mu\text{m}$ (ASTM 30)
3. **Liquid-to-Solid Ratio (LSR)**:
   $$\text{LSR}_{\text{Track A}} = \frac{m_{\text{water}}}{m_{\text{dry}}} \approx 15\text{--}25\text{ mL/g}_{\text{dry}}$$

---

### C. Track B Feedstock Conditioning: Fresh Wet Fragments with Measured Covariate
Material allocated to Track B receives **no oven-drying and no sieving**:
1. **Direct Charging**: Wet comminuted fragments are transferred directly from the food processor to the ultrasonic extraction vessel.
2. **Measured $d_{50}$ Covariate**: Prior to charging, a representative subsample of the wet fragments is analyzed for particle size distribution via wet-sieving or laser diffraction (e.g., Malvern Mastersizer with wet dispersion unit). The resulting median diameter:
   $$d_{50,\text{measured}} \in [500, 1500]\,\mu\text{m}$$
   is **recorded per run as an observational covariate**, acknowledging that comminution produces a natural distribution rather than discrete sieved cuts.
3. **Effective Liquid-to-Solid Ratio (LSR)**:
   Accounting for the high native water content of the fresh rind:
   $$\text{LSR}_{\text{Track B}} = \frac{m_{\text{water,added}} + m_{\text{fresh}} \cdot X_{w,0}}{m_{\text{fresh}} \cdot (1 - X_{w,0})} \approx 25\text{--}35\text{ mL/g}_{\text{dry}}$$

---

## 3. Extraction Operations: Thermal vs. Acoustic-Acid Physics

### A. Track A: Thermal Acid Extraction (Mechanistic Reference)
* **Vessel**: $1.2\text{--}2.0\text{ L}$ torispherical jacketed borosilicate glass vessel.
* **Reflux Vapor Control**: Fitted with a water-cooled Dimroth condenser ($15^\circ\text{C}$ coolant) guaranteeing $< 0.2\%$ evaporative loss over 120 minutes.
* **Agitation**: Overhead mechanical stirrer with PTFE anchor or pitched-blade turbine ($250\text{--}400\text{ RPM}$).
* **Instrumentation**: Submerged Class-A PT100 RTD ($\ge 0.1\text{ Hz}$) logging thermal exposure $\tau_k = \int k(T, \text{pH})\,ds$; continuous glass combination pH electrode.
* **Sampling Protocol**: Non-destructive time-series aliquots withdrawn at $t \in \{15, 45, 90, 120\}\text{ min}$ ($4 \times 12\text{ mL} \le 4.0\%$ total slurry volume).
* **Thermal Quenching**: Withdrawn into thin-walled stainless-steel immersion vials in a $-10^\circ\text{C}$ glycol bath, cooling below $25^\circ\text{C}$ in $< 15\text{ seconds}$.

### B. Track B: Ultrasound-Assisted Acid Extraction (UAE)
* **Acoustic Field**: $40\text{ kHz}$ transducer array bonded to tank base, delivering nominal electrical power $P_{\text{elec}} \in [50, 300]\text{ W}$.
* **Delivered Acoustic Power**: Calorimetrically calibrated via solvent temperature rise:
  $$P_{\text{acoustic}} = m_{\text{solvent}} C_p \left(\frac{dT}{dt}\right)_{t \to 0}$$
* **Acoustic Mechanism**:
  1. *Solubilization Acceleration*: Cavitation microjets perforate cellular barriers, enhancing effective solid-liquid contact area $a_s(d_{50})$.
  2. *Depolymerization / Chain Scission*: Hydrodynamic shear stresses cleave glycosidic bonds, accelerating molecular weight degradation ($k_{\text{hyd}}^{\text{US}} \ge k_{\text{hyd}}^{\text{thermal}}$).
* **Mandatory Paired Thermal Control**: Every sonicated run is paired with an identical fresh-rind run with ultrasound turned OFF ($P_{\text{elec}} = 0\text{ W}$) in the same bath at matched fluid temperature and duration.
* **Mass Balance & Evaporative Loss Check**: Track B vessels must be sealed and weighed before and after sonication; mass loss due to vapor venting must remain $< 0.3\%$ over 60 minutes despite acoustic self-heating.

---

## 4. Solid / Liquid Separation & Mass Accounting

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

1. **Filtrate Mass Balance**: $m_{\text{filtrate\_total}} = m_{\text{analytical\_aliquot}} + m_{\text{precipitation\_stream}}$.
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

1. **Alcohol-Precipitated Soluble Pectin (APSP) Gravimetric Yield**:
   - Precipitated with $2:1\text{ (v/v)}$ absolute ethanol ($\ge 64\%$ final ethanol) at $4^\circ\text{C}$ for 2 hours.
   - Filtered through pre-weighed Whatman GF/A filters, washed with $70\%$ ethanol, vacuum-dried at $45^\circ\text{C}$ ($100\text{ mbar}$) to constant weight ($\sigma \le 1.0\%$).
2. **GalA Carbazole Assay with Sample-Blank Correction**:
   - Sample-blank tube (sample + $\text{H}_2\text{SO}_4$/tetraborate + ethanol, no carbazole) corrects for native carotenoid/flavonoid matrix pigments:
     $$\mathbf{A}_{\text{net}}(\lambda) = \mathbf{A}_{\text{developed}}(\lambda) - \mathbf{A}_{\text{sample\_blank}}(\lambda) - A_{\text{turbidity}}(680) \left(\frac{680}{\lambda}\right)^{\alpha_{\text{Rayleigh}}}$$
   - Multi-wavelength regression: $C_{\text{GalA}} = w_1 A_{\text{net}}(515) + w_2 A_{\text{net}}(555) + w_3 A_{\text{net}}(680) + d$.
   - Matrix-spike validation target: $95\%\text{--}105\%$ recovery on $+50$ and $+100\text{ mg/L}$ spikes.
3. **Copper-Chelate Pectin-Equivalent Assay**:
   - Measures intact pectin polymer chelation at $630\text{ nm}$ ($A_{\text{net}}(630) \to C_{\text{pectin-equiv}}$).
4. **Degree of Esterification ($DE$) & Molecular Weight ($M_w$)**:
   - $DE$ measured via USP double-titration (saponification with $0.25\text{ M NaOH}$).
   - $M_w$ measured via HPSEC-MALLS-RI ($dn/dc = 0.146\text{ mL/g}$).

---

## 6. Phase 0 Physical Repeatability Checklist

| Operational Check | Track | Acceptance Target | Diagnostic Procedure |
| :--- | :---: | :--- | :--- |
| **Batch Moisture $X_{w,0}$ Repeatability** | Both | Triplicate readings $\text{SD} < 0.005$ | Halogen moisture analyzer ($105^\circ\text{C}$) |
| **Comminution Particle Size $d_{50}$** | Track B | Measured $d_{50}$ logged ($\text{RSD} < 10\%$) | Laser diffraction or wet-sieving of wet fragments |
| **Thermal Control Stability** | Track A | $\pm 0.5^\circ\text{C}$ at steady state | Continuous PT100 logging at 80 °C for 60 min |
| **Track A Reflux Evaporative Loss** | Track A | $< 0.2\%$ mass loss over 120 min | Pre- and post-run vessel weighing at 95 °C with Dimroth condenser |
| **Track B Vapor Mass-Balance Check** | Track B | $< 0.3\%$ mass loss over 60 min | Pre- and post-run sealed container weighing under active sonication |
| **pH Stability / Tracking** | Both | Drift $< 0.10\text{ pH}$ units | Autoclavable electrode in stirred citric acid buffer |
| **Filtration Mass Recovery** | Both | Filtrate mass repeatability $CV < 2.5\%$ | Standardized Büchner vacuum filtration |
| **Precipitation & Drying** | Both | Dry solids mass $CV < 4.0\%$ | 5 identical aliquots precipitated and vacuum-dried |
| **Colorimeter Reproducibility**| Both | Absorbance repeatability $CV < 1.5\%$ | 5 repeated readings of identical GalA standard |
