# Minimum Viable Laboratory (MVP) Configuration & Procurement Strategy

The Bayesian proxy architecture shifts the bottleneck of pectin optimization from capital-intensive analytical hardware to **analytical discipline and traceability**. By relying on probabilistic measurement models, we can cleanly divide the physical program into an inexpensive in-house operation and outsourced ground-truth anchoring.

## 1. Capital Strategy: In-House vs. University vs. Outsourced

By leveraging university core facilities for spectral and chromatographic capabilities, the required in-house capital expenditure is remarkably lean.

### Own / Operate (In-House)
$$ \text{1-2 L Reactor} + \text{Sensors} + \text{Precipitation} + \text{Calibrated Balance} + \text{Capillary Viscosity} + \text{UV-Vis/Titration} $$

### University / Core Facility Access
$$ \text{ATR-FTIR} + \text{HPSEC-MALLS} $$
*(Acquiring sustained core-facility access for ATR-FTIR is the single largest capital-saving opportunity. Purchase an in-house FTIR only if sustained access cannot be secured).*

---

## 2. Procurement & Access Checklist

| Capability | Minimum Equipment | Sourcing Strategy | Rationale |
|:---|:---|:---|:---|
| **Controlled Extraction** | 1.0–2.0 L jacketed glass reactor, overhead stirring | **Own** | Preferred over 0.5 L, as withdrawing six 20 mL aliquots (120 mL total) will significantly alter the S:L ratio of smaller vessels. |
| **Temperature Logging** | RTD/thermocouple + continuous data logger | **Own** | Kinetic integration requires exact $T(t)$ history. |
| **Acidity Control** | Lab pH meter + appropriate probe | **Own** | Essential for extraction acidity control. |
| **Mass Tracking** | Calibrated Analytical Balance | **Own** | **Critical Instrument**: Errors in $m_{feed}$ or $m_{pellet}$ propagate directly into the Bayesian likelihood via the $C_{ppt}$ proxy. Consistency matters more than extreme precision. |
| **Sampling & Quenching** | Port/syringe, pre-chilled tubes, ice bath | **Own** | Ensures extraction is frozen at the precise timestamp ($t_{aliquot}$). |
| **Standardized Prep** | Bench centrifuge, ethanol, vacuum/drying oven | **Own** | Required to execute rapid precipitation. |
| **Proxy 1: Molecular** | Capillary Viscometer + water bath | **Own** | Inexpensive candidate proxy for $M_w$. |
| **Proxy 2: Chemical** | **ATR-FTIR** Spectrometer | **University** | Generates DE and GalA chemometric predictions. |
| **Anchor 1: GalA/DE** | UV-Vis Spectrophotometer, Titration glassware | **Own** | Ground truth anchors; cheap enough to own. |
| **Anchor 2: MW** | HPSEC-MALLS | **Outsource / Univ.** | Send the Phase 1 proxy calibration pellets out. |

## 3. Anti-Requirements (Do Not Buy Initially)
For Phase 1 and the initial Digital Twin calibration, capital should **not** be deployed on:
* **Sophisticated Rheometers**: Defer unless Phase 1 shows that capillary viscometry cannot meet the MW-proxy acceptance criteria.
* **In-house ATR-FTIR / SEC-MALLS**: Defer unless core-facility access is impossible.
* Automated robotic liquid handling, inline FTIR, or custom automated process-control systems.

## 4. The Hidden Capability: Analytical Discipline
The most expensive hardware cannot save a poorly tracked sample. The digital twin requires rigorous relational data tracking mapping every physical aliquot back to its exact thermodynamic history.

The primary key for all data must be the unique **Sample ID**. For example: `B002-R07-S03` uniquely identifies Batch 2, Run 7, Sample 3.

For every single sample, this ID must link to the exact process metadata:
$$ \text{SampleID} \rightarrow t_{aliquot} + T(t) + pH(t) + m_{liquor} + m_{pellet} $$

This strict traceability is formalized in the `proxy_data_schema.md` artifact. If this chain is broken (e.g., exact quench time is not recorded), the sample may no longer be suitable for kinetic inference because its process history cannot be assigned reliably.
