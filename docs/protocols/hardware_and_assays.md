# Reactor Hardware & Analytical Assay Specifications

To execute the `physical_experimental_protocol.md`, the laboratory must meet specific hardware and analytical chemistry requirements. This document outlines the minimum viable setup and Standard Operating Procedures (SOPs) to achieve the required data quality ($\sigma$ targets).

## 1. Reactor Hardware Specification

The reactor must prioritize thermal logging, rapid sampling, and precise pH control over purely automated setpoint tracking.

### A. Core Vessel & Thermal Control
* **Vessel**: 0.5 L to 2.0 L jacketed glass reactor. (Glass is required for visual confirmation of dispersion and fouling).
* **Heating/Cooling**: Circulating bath (e.g., Julabo, Huber) connected to the jacket, capable of ramping from 50 °C to 95 °C in < 5 minutes. 
* **Agitation**: Overhead mechanical stirrer with a pitched-blade or anchor impeller to ensure high-viscosity mixing (avoid magnetic stir bars, which fail at high pectin concentrations).
* **Thermal Logging**: PT100 RTD probe submerged directly in the reaction fluid (not just the jacket return). Logged at $\ge 0.1$ Hz to compute exact thermal exposure ($\tau_k$).

### B. Sampling & Quenching Subsystem
* **Valve**: Dead-volume-free bottom drain valve or a wide-bore syringe/dip-tube. Narrow tubing will clog.
* **Quenching**: Samples ($\approx 10-20$ mL) must be immediately dispensed into pre-chilled tubes resting in an ice-water bath (0 °C), instantly arresting hydrolysis. 
* **Timing**: The timestamp recorded must be the moment the sample hits the quench bath, not the moment the valve opens.

---

## 2. Analytical Assay Standard Operating Procedures (SOPs)

To achieve the necessary signal-to-noise ratio for Bayesian parameter inference, the analytical assays must hit strict variance targets.

### A. Gravimetric Yield ($Y$)
**Target**: $\sigma \approx 1\%$ absolute.
* **Method**: Alcohol Insoluble Residue (AIR) precipitation.
* **Procedure**: 
  1. Add 2 volumes of 96% ethanol to the quenched, filtered liquid sample to precipitate pectin.
  2. Allow to stand at 4 °C for 2 hours.
  3. Centrifuge, wash pellet twice with 70% ethanol to remove soluble sugars and acids.
  4. Dry pellet at 60 °C to constant mass.
* **Note**: Do not dry at > 80 °C to prevent thermal degradation of the dried product prior to downstream analysis.

### B. Degree of Esterification ($DE$)
**Target**: $\sigma \approx 2\%$ absolute.
* **Method**: Titrimetric (USP monographs / FAO JECFA) or FTIR.
* **Procedure (Titration)**:
  1. Dissolve 0.1 g of dried pectin in CO2-free water. Add phenol red indicator.
  2. Titrate with 0.1 M NaOH to the end point ($V_1$, free carboxyl groups).
  3. Add exactly 10.0 mL of 0.25 M NaOH, stir for 15 min at room temp (saponification of esterified groups).
  4. Add exactly 10.0 mL of 0.25 M HCl to neutralize.
  5. Titrate the excess HCl with 0.1 M NaOH ($V_2$, esterified groups).
  6. $DE = \frac{V_2}{V_1 + V_2} \times 100\%$

### C. Molecular Weight ($M_w$)
**Target**: $\sigma \approx 15,000$ Da.
* **Method**: HPSEC-MALLS (High-Performance Size Exclusion Chromatography with Multi-Angle Laser Light Scattering) coupled with Refractive Index (RI) detection.
* **Why MALLS?**: Standard SEC relies on pullulan or dextran calibration curves, which structurally differ from pectin, leading to massive systematic error ($\delta_{model}$). MALLS measures absolute $M_w$ independently of standards.
* **Buffer**: 0.1 M NaNO3 or 0.1 M LiNO3 to prevent pectin aggregation in the column.

### D. Galacturonic Acid Fraction ($X_{GalA}$)
**Target**: $\sigma \approx 2-3\%$.
* **Method**: m-hydroxydiphenyl (mHDP) colorimetric assay (Blumenkrantz & Asboe-Hansen, 1973).
* **Procedure**:
  1. Hydrolyze pectin completely to monomers using concentrated sulfuric acid/tetraborate on ice, then heat at 100 °C for 5 min.
  2. Add mHDP reagent; measure absorbance at 520 nm.
  3. Compare against a pure D-galacturonic acid standard curve.
  4. Carbazole assay is an acceptable alternative but more prone to interference from neutral sugars.

---

## 3. Data Integration Schema

To ensure a seamless handoff between the physical laboratory and the V1.3 digital twin, experimental data must be logged in the exact formats expected by the Bayesian inference engine.

* **Batch Characterization Log**: Must contain `batch_id, pectin_mass, galA_fraction, initial_DE, initial_Mw, d50, moisture`.
* **Process Log**: Timeseries CSV containing `time_sec, setpoint_T, actual_T, setpoint_pH, actual_pH`.
* **Assay Log**: `batch_id, run_id, time_min, yield_pct, DE_pct, Mw_Da` (with blanks for unsampled assays per the asymmetric time-course matrix).
