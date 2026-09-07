# Track B Specification: Ultrasound-Assisted Acid Extraction & At-Line Soft Sensor

**Document Version**: 3.2 (Shared Provenance with Fresh Wet Feedstock)  
**Parent Document**: [`MASTER_DUAL_TRACK_SPECIFICATION.md`](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/MASTER_DUAL_TRACK_SPECIFICATION.md)  
**Status**: Canonical Track B Technical Standard  

---

## 1. Executive Summary & Philosophy

**Track B** represents the rapid-turnaround, process-intensification, and at-line analytical track of the Pectin Extraction Digital Twin ecosystem. Its primary objectives are:
1. **Quantifying the net physical enhancement of ultrasound** on acid extraction kinetics:
   $$\Delta Y_{\text{US}} = Y_{\text{acid+thermal+US}} - Y_{\text{acid+thermal}}$$
2. **Deploying calibrated at-line optical soft sensors** (IO Rodeo 8-Channel Colorimeter) to estimate chemical concentrations ($C_{\text{GalA}}$, $C_{\text{pectin-equiv}}$) and purity in minutes rather than days.
3. **Evaluating the energetic and quality tradeoffs** of ultrasonic cavitation (accelerated extraction vs. polymer chain scission).

```text
=============================================================================================
TRACK B: Acoustic Intensification & Rapid Soft-Sensor Pipeline
Shared Fresh Comminution (Lot ID)  -->  Direct Charge of Wet Fragments (Measured d50 Covariate)  -->
40 kHz Ultrasonic Bath Chamber (P_elec in [50, 300] W) + Paired P_elec = 0 Thermal Controls  -->
Solid/Liquid Filtration  -->  At-Line Split Aliquot (IO Rodeo 8-CH Colorimeter, Sample-Blank Corrected)  -->
Rapid Ethanol Precipitation + Low-Temp Vacuum Oven Drying  -->  Incremental Cavitation Twin
=============================================================================================
```

---

## 2. Feedstock State & Covariate Measurement

### A. Shared Provenance Step (Step 0)
Track B begins at the identical physical comminution step as Track A:
* Peels from ripe purple passion fruit (*Passiflora edulis*) are rinsed, tested for moisture via halogen analyzer ($X_{w,0} \in [0.81, 0.86]$), and pulsed in a commercial food processor ($3 \times 15\text{ s}$ pulses, $5\text{ s}$ rest).
* A unique physical lot identifier (`LOT-YYYYMMDD-BATCH`) is logged.

### B. Track B Branch: Direct Fresh Wet Feeding
Unlike Track A, material allocated to Track B receives **no oven drying and no sieving**:
1. **Fresh Fragment Direct Charge**: Wet comminuted peel is charged directly into the acidified bath liquor, preserving native cellular hydration and moisture ($X_{w,0} \approx 81\text{--}86\%$).
2. **Measured (Not Controlled) $d_{50}$ Covariate**:
   * Prior to charging the extraction vessel, a representative subsample of the wet fragments is analyzed for particle size distribution using laser diffraction (wet dispersion) or calibrated wet-sieving.
   * The median physical diameter:
     $$d_{50,\text{measured}} \in [500, 1500]\,\mu\text{m}$$
     is **logged as an observational covariate for each run**, rather than forced into discrete sieved bins.
3. **Effective Liquid-to-Solid Ratio (LSR)**:
   Accounting for the water introduced by the fresh peel:
   $$\text{LSR}_{\text{Track B}} = \frac{m_{\text{water,added}} + m_{\text{fresh}} \cdot X_{w,0}}{m_{\text{fresh}} \cdot (1 - X_{w,0})} \approx 25\text{--}35\text{ mL/g}_{\text{dry}}$$

---

## 3. Extraction Hardware & Cavitation Physics

### A. Ultrasonic Bath Chamber
* **Transducers**: $40\text{ kHz}$ piezoelectric transducers bonded to the tank base.
* **Electrical Power**: $P_{\text{elec}} \in [50, 300]\text{ W}$.
* **Delivered Acoustic Power ($P_{\text{acoustic}}$)**: Directly calibrated via calorimetric solvent characterization ($m_{\text{solvent}} C_p dT/dt$) to determine electromechanical coupling efficiency $\eta = P_{\text{acoustic}} / P_{\text{elec}}$.
* **Mass Balance & Evaporative Loss Check**: Track B vessels must remain tightly sealed during sonication. Pre- and post-run vessel weighing must confirm $< 0.3\%$ mass loss over 60 minutes despite acoustic dissipation heating.

### B. Dual Action of Cavitation on Pectin Extraction
Ultrasound enhances acid extraction through two competing physical mechanisms:
1. **Solubilization Enhancement**: Acoustic microjets collapse against tissue surfaces, peeling diffusion boundary layers and rupturing cells, increasing effective contact area $a_s(d_{50})$ ($k_{\text{ext}}^{\text{US}} > k_{\text{ext}}^{\text{thermal}}$).
2. **Shear-Induced Chain Depolymerization**: High acoustic shear stresses and localized hot spots can cleave $\alpha$-(1 $\to$ 4) glycosidic bonds ($k_{\text{hyd}}^{\text{US}} \ge k_{\text{hyd}}^{\text{thermal}}$), causing molecular weight degradation ($M_w < 100\text{ kDa}$) and reducing gelling quality.

### C. Mandatory Paired Thermal Control (P_elec = 0 W)
* Every ultrasound run is paired with an identical fresh-rind run conducted with sonication turned OFF ($P_{\text{elec}} = 0\text{ W}$) in the same bath at matched slurry temperature and run time.
* **Baseline Discipline**: $\Delta Y_{\text{US}}$ is calculated **only** against this paired fresh thermal control — **never against Track A**:
  $$\Delta Y_{\text{US}} = Y_{\text{acid+thermal+US}} - Y_{\text{acid+thermal}}$$
* Track A rate constants serve as informative priors / mechanistic bounds in the Bayesian digital twin, not literal baseline substitutes; a formal bridging factor relating fresh and dried states is explicitly deferred.

---

## 4. Analytical Backbone & At-Line Soft Sensor

Track B integrates the **IO Rodeo 8-Channel Multi-Wavelength Colorimeter** directly at the solid/liquid separation line:

### A. Matrix-Corrected Net Absorbance
Native carotenoids and flavonoids in fresh passion-fruit peel absorb strongly between 450–550 nm. An unreacted sample-blank tube is mandatory:
$$\mathbf{A}_{\text{net}}(\lambda) = \mathbf{A}_{\text{developed}}(\lambda) - \mathbf{A}_{\text{sample\_blank}}(\lambda) - A_{\text{turbidity}}(680) \left(\frac{680}{\lambda}\right)^{\alpha_{\text{Rayleigh}}}$$

### B. Soft-Sensor Inversion
* **GalA Carbazole Assay**: Inverts net absorbance at 515 and 555 nm to determine GalA concentration ($C_{\text{GalA}}$ in g/L).
* **Copper-Chelate Assay**: Inverts net absorbance at 630 nm to determine intact pectin-equivalent concentration ($C_{\text{pectin-equiv}}$ in g/L).
* **Dynamic Dilution Advisor**: Checks Beer-Lambert linearity ($0.05\text{--}1.50\text{ AU}$). If clipping occurs, advises $DF \times N$ re-dilution.
* **Purity Proxy**: Computes GalA composition ratio $I_{\text{GalA}} = C_{\text{GalA}} / C_{\text{pectin-equiv}}$.

---

## 5. Comparative Summary: Track B vs. Track A

| Dimension | Track B (UAE + At-Line Soft Sensor) | Track A (Classical Jacketed Reactor) |
| :--- | :--- | :--- |
| **Shared Provenance Step** | Food-processor comminution ($X_{w,0} \in [0.81, 0.86]$, $d_{50} \in [500, 1500]\,\mu\text{m}$, lot ID logged) | **Identical common comminution lot ID** |
| **Feedstock State** | **Fresh wet fragments** ($X_w \approx 81\text{--}86\%$, un-dried, measured $d_{50}$ covariate) | **Dried, knife-milled, and classified** ($X_w \approx 6\text{--}8\%$, $d_{50} \in \{150, 300, 600\}\,\mu\text{m}$) |
| **Primary Objective** | Rapid screening, acoustic enhancement, at-line control | Precision Arrhenius kinetics & structural model identification |
| **Energy Driving Force** | Thermal conduction + acoustic cavitation ($40\text{ kHz}$) | Thermal conduction ($50\text{--}95^\circ\text{C}$) + mechanical shear |
| **Vapor Control** | Sealed vessel in bath + mass balance check ($< 0.3\%$ mass loss) | Water-cooled Dimroth reflux condenser ($< 0.2\%$ mass loss) |
| **Matched Control** | Internal fresh-rind thermal controls ($P_{\text{elec}} = 0\text{ W}$) | Serves as primary thermal reference |
| **Primary Analytical Tool**| At-line IO Rodeo 8-channel colorimeter (matrix corrected) | Offline laboratory assays (HPSEC-MALLS, titration, AIR) |
| **Downstream Recovery** | Rapid 2:1 ethanol precipitation + low-temp vacuum drying | Industrial flowsheets (Hybrid membrane, evaporative, direct spray) |

---

## 6. Open Architectural Gaps (Phase 3 Deliverables)

1. **Acoustic Frequency Exponent $\gamma_{\text{US}}$**: Single-frequency hardware ($40\text{ kHz}$) cannot structurally identify the frequency-scaling exponent $\gamma_{\text{US}}$. It is fixed by convention to $\gamma_{\text{US}} \equiv 1.0$ until multi-frequency hardware is introduced.
2. **Track B Algorithmic OED Table**: Track B currently operates across defined factor bounds ($T \in [50, 75]^\circ\text{C}$, $\text{pH} \in [1.8, 2.8]$, $P_{\text{acoustic}} \in [20, 120]\text{ W}$, $t \in [10, 60]\text{ min}$) with paired controls. A formal D-optimal experimental design table for Track B is a **pending Phase 3 deliverable**.
