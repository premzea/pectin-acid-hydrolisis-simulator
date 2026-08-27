# Minimum Viable Laboratory (MVP) Configuration

The Bayesian proxy architecture shifts the bottleneck of pectin optimization from capital-intensive analytical hardware to **analytical discipline and traceability**. By relying on probabilistic measurement models, we can cleanly divide the physical program into an inexpensive in-house operation and outsourced ground-truth anchoring.

## 1. Capital Strategy: In-House vs. Outsourced

### In-House Capability (High-Frequency / Proxy)
$$ \text{Reactor} + \text{Sensors} + \text{Precipitation/Drying} + \text{ATR-FTIR} + \text{Capillary Viscometry} + \text{UV-Vis/Titration} $$

### Outsourced Capability (Low-Frequency / Calibration Anchor)
$$ \text{HPSEC-MALLS} $$
*(Selected samples from the Proxy Calibration phase are mailed to a university core facility. Routine runs require zero in-house SEC capability).*

---

## 2. Minimum Viable Equipment List

| Capability | Minimum Equipment | Rationale | Frequency |
|:---|:---|:---|:---|
| **Controlled Extraction** | 0.5–2 L jacketed glass reactor, overhead stirring | Allows repeatable execution of the OED boundary conditions (T, pH, time). | Every run |
| **Temperature Logging** | RTD/thermocouple + continuous data logger | The kinetic integration $\int k(T)\,dt$ requires exact $T(t)$ history, not just the nominal setpoint. | Continuous |
| **Acidity Control** | Lab pH meter + appropriate probe | Essential for extraction acidity control and tracking. | Every run |
| **Sampling & Quenching** | Syringe/port, pre-chilled tubes, ice bath | Ensures extraction is frozen at the precise timestamp ($t_{aliquot}$). | Every sample |
| **Standardized Prep** | Bench centrifuge, ethanol, drying oven, analytical balance | Required to execute the rapid precipitation standard, eliminating liquor matrix confounders. | Every sample |
| **Proxy 1: Chemical** | **ATR-FTIR** Spectrometer | Generates the spectra for the DE and GalA chemometric predictions. ATR is operationally simpler than DRIFTS. | Most samples |
| **Proxy 2: Molecular** | Capillary Viscometer + water bath | Generates the flow time ($t_{flow}$) proxy for $M_w$. | Most samples |
| **Anchor 1: GalA** | UV-Vis Spectrophotometer | Ground truth for the mHDP colorimetric GalA assay. | Calibration subset |
| **Anchor 2: DE** | Basic Titration Setup | Ground truth for DE. | Calibration subset |

## 3. Anti-Requirements (Do Not Buy)
For Phase 1 and the initial Digital Twin calibration, capital should **not** be deployed on:
* Automated robotic liquid handling
* Inline FTIR (the standardized precipitation step requires offline testing anyway)
* Sophisticated rheometers (capillary viscometry is sufficient)
* In-house SEC-MALLS ($100k+ capital cost)
* Custom automated process-control systems

## 4. The Hidden Capability: Analytical Discipline
The most expensive hardware cannot save a poorly tracked sample. The digital twin requires rigorous relational data tracking mapping every physical aliquot back to its exact thermodynamic history.

For every single sample, the following must travel unbroken through the laboratory:
$$ \text{Batch ID} + \text{Run ID} + t_{aliquot} + T(t) + pH(t) + m_{liquor} + m_{pellet} $$

This strict traceability is formalized in the `proxy_data_schema.md` artifact. If this chain is broken (e.g., exact quench time is not recorded, or the sample is not mapped to the continuous $T(t)$ log), the sample is mathematically useless to the Bayesian inference engine.
