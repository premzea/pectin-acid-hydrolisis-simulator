#set page(
  paper: "us-letter",
  margin: (x: 1.25in, y: 1.25in),
  header: align(right)[
    #text(8pt, fill: luma(120))[Hybrid Mechanistic, Bayesian Inference & Optimization System -- Research Blueprint]
  ],
)

#set text(
  font: ("New Computer Modern", "Linux Libertine"),
  size: 11pt,
  lang: "en"
)

#set heading(numbering: "1.1.")
#show heading: it => [
  #set text(font: "Inter", weight: "bold", fill: rgb("#1d3557"))
  #v(1em)
  #it
  #v(0.5em)
]

#show math.equation: set text(font: "New Computer Modern Math")
#set par(justify: true, leading: 0.65em)

#align(center)[
  #text(size: 22pt, font: "Inter", weight: "bold", fill: rgb("#1d3557"))[
    Hybrid Mechanistic, Bayesian Inference & Optimization System for Passion-Fruit Pectin Extraction
  ]
  
  #v(1em)
  
  #text(size: 14pt, font: "Inter", fill: luma(80))[
    Research & Experimental Design Blueprint
  ]
  
  #v(3em)
]

#outline(indent: auto)
#pagebreak()

= Executive Summary
This document synthesizes the complete research architecture for building a digital twin of passion-fruit pectin extraction. The architecture bridges a strict mechanistic kinetic model with a Bayesian Optimal Experimental Design (OED) framework. To solve the fundamental bottleneck of expensive laboratory analytics, the system employs a hierarchical proxy measurement model, allowing dense time-series data collection using cost-effective chemometric and rheological sensors.

The sequence of this research project is explicitly defined as:
$
text("Mechanistic Model") 
arrow.r text("Synthetic Recovery") 
arrow.r text("OED") 
arrow.r text("Proxy Calibration") \
  
arrow.r text("Physical Experiment") 
arrow.r text("Bayesian Update")
arrow.r text("Optimization")
$

= Mechanistic Reactor Model (V1.3)
== Compartmental Cascade
The extraction is modeled as a 4-pool cascading mass transfer system. The cascade structure forces a critical structural tradeoff between extraction speed and product degradation.

#align(center)[
  #grid(
    columns: (auto, auto),
    column-gutter: 2em,
    row-gutter: 0.8em,
    align: (center + horizon, left + horizon),
    
    rect(fill: rgb("f8f9fa"), stroke: luma(100), radius: 4pt, inset: 8pt)[*Matrix Pectin* \ ($P_{"matrix"}$)],
    [],
    
    [$#sym.arrow.b ~ k_{"ext"}$],
    [],
    
    rect(fill: rgb("e9ecef"), stroke: luma(100), radius: 4pt, inset: 8pt)[*Soluble Intact Pectin* \ ($P_{"sol"}$)],
    text(fill: luma(80))[$#sym.arrow.l.dashed$ *Properties:* $D E_{"sol"}, M_{w,"sol"}$],
    
    [$#sym.arrow.b ~ k_{"hyd"}$],
    [],
    
    rect(fill: rgb("dee2e6"), stroke: luma(100), radius: 4pt, inset: 8pt)[*Low-MW Pectin* \ ($P_{"lowMW"}$)],
    text(fill: luma(80))[$#sym.arrow.l.dashed$ *Derived Props:* $D E_{"lowMW"}, M_{w,"lowMW"}$],
    
    [$#sym.arrow.b ~ k_{"deg"}$],
    [],
    
    rect(fill: rgb("ced4da"), stroke: luma(100), radius: 4pt, inset: 8pt)[*Unrecoverable Loss* \ ($P_{"loss"}$)],
    []
  )
]

== Kinetic Equations (Mass & Moments)
The state equations combine strict normalized mass conservation [$#text("kg/kg")_{"dry,feed"}$] with mass-weighted moments to track intensive properties ($M_w, D E$) dynamically.
$ (d P_{"sol"}) / (d t) &= k_{"ext"} P_{"matrix"} - k_{"hyd"} P_{"sol"} $
$ (d P_{"lowMW"}) / (d t) &= k_{"hyd"} P_{"sol"} - k_{"deg"} P_{"lowMW"} $

Kinetics are parameterized via an Arrhenius reference-state formulation ($T_{"ref"} = 353.15$ K, $p H_{"ref"} = 2.0$) to dramatically improve the numerical conditioning of the Bayesian inference.

== Parameter Ontology
To avoid mathematical ambiguity, all parameters are strictly assigned an ontology classification.

#align(center)[
#table(
  columns: (auto, auto, auto, auto, auto),
  align: (center, left, center, center, center),
  
  [*Symbol*], [*Meaning*], [*Units*], [*V1 Range*], [*Classification*],
  [$T$], [Extraction Temperature], [°C], [45 -- 100 °C], [Controlled Process Variable],
  [$p H$], [Kinetic Acidity], [pH], [1.2 -- 4.5], [Controlled Process Variable],
  [$t$], [Extraction Time], [min], [5 -- 120 min], [Controlled Process Variable],
  [$d_{50}$], [Particle Size], [μm], [149 -- 600 μm], [Measured State],
  [$M_{w,"matrix"}$], [MW of matrix pectin], [Da], [$6.54 times 10^5$], [Informative Prior],
  [$k_{i,"ref"}$], [Reference Rates], [$\text{min}^{-1}$], [TBD], [Calibrated],
  [$E_{i}$], [Activation Energies], [J/mol], [TBD], [Calibrated],
  [$n_{i}$], [Acidity Orders], [-], [1.0], [Fixed V1],
  [$\alpha$], [Particle Size Scaling], [-], [0.5 -- 2.0], [Calibrated]
)
]

= Structural Identifiability & OED
The serial cascade induces a severe identifiability problem: a fast extraction/fast degradation trajectory looks mathematically identical to a slow extraction/slow degradation trajectory if observed only at the process endpoint.

== Bayesian Optimal Experimental Design (OED)
By computing the Fisher Information Matrix (FIM) over the 9-dimensional parameter space, we designed an exact 10-run protocol that minimizes the determinant of the posterior covariance matrix (D-optimal design). 

The OED analysis strongly favors time-resolved observation, particularly at early and intermediate residence times, to break the $k_{"hyd"} <-> k_{"deg"}$ correlation. It pushes the boundary conditions of the operating space (e.g., 95 °C/pH 1.5 vs 50 °C/pH 3.0). For the final 10-run protocol utilizing 4-point time-resolved tracking, the selected protocol substantially improves the conditioning of the inverse problem, eliminating near-null sensitivity directions and achieving a condition number of $kappa approx 27.0$.

The explicit 10-run protocol defined by the solver is as follows (distribute across 2 baseline feedstock batches):
#align(center)[
#table(
  columns: (auto, auto, auto, auto, auto),
  align: (center, center, center, center, left),
  [*Run*], [*T (°C)*], [*pH*], [*$d_{50}$ (μm)*], [*Sample Times (min)*],
  [1], [95], [1.5], [600], [15, 45, 90, 120],
  [2], [50], [1.5], [150], [15, 45, 90, 120],
  [3], [95], [2.5], [150], [15, 45, 90, 120],
  [4], [50], [1.5], [600], [15, 45, 90, 120],
  [5], [95], [2.0], [600], [15, 45, 90, 120],
  [6], [50], [2.0], [150], [15, 45, 90, 120],
  [7], [95], [2.5], [600], [15, 45, 90, 120],
  [8], [50], [1.5], [300], [15, 45, 90, 120],
  [9], [95], [3.0], [150], [15, 45, 90, 120],
  [10], [95], [2.0], [300], [15, 45, 90, 120]
)
]

= Hierarchical Measurement Architecture
The time-resolved OED campaign requires 6 samples per run. Performing conventional SEC-MALLS (for $M_w$), Titration (for $D E$), and mHDP Colorimetry (for GalA purity) on every aliquot is economically unviable. 

We solve this using a Bayesian Proxy Measurement Model. The physical experiment is segmented into a preparation layer and an observation layer.

== The Preparation Model & Precipitation Bias
Direct measurement of raw reactor liquor is strongly confounded by the extraction matrix (unreacted acid, trace metal ions, simple sugars) and is therefore not the preferred basis for routine proxy measurements. All proxy samples undergo **Standardized Alcohol Precipitation**. 

This is not a neutral step. Ethanol fractionation can selectively recover high-$M_w$ pectin while leaving low-$M_w$ fragments in solution. We model this recovery bias as $eta_{"precipitation"} = f(M_w, D E)$. The proxy must be calibrated on the exact same precipitated material to absorb this physical bias natively.

== The Proxy Observation Model
We deploy two ultra-fast, low-cost sensors on the standardized precipitate:
1. *FTIR/DRIFTS Spectroscopy*: A chemometric PLS model maps the full mid-IR spectrum to $D E$ and GalA fraction.
2. *Capillary Viscometry*: The flow time ($t_{"flow"}$) at a strictly recorded concentration ($C_{"pellet"}$) provides a low-cost MW proxy calibrated directly against HPSEC-MALLS on the same passion-fruit pectin material, avoiding reliance on universal Mark-Houwink constants.

== Proxy Calibration & Acceptance Criteria
To ensure the proxy models generalize, the calibration samples must span the entire operating space. We execute 5 dedicated reactor runs, taking 6 time-resolved aliquots per run (Total $N = 30$).

#align(center)[
#table(
  columns: (auto, auto, auto, auto, auto, auto),
  align: (center, center, center, center, left, left),
  [*Run*], [*T (°C)*], [*pH*], [*$d_{50}$ (μm)*], [*Targeted Domain*], [*Expected State*],
  [C1], [50], [3.0], [600], [Absolute Min Severity], [High $M_w$, High $D E$],
  [C2], [95], [1.5], [150], [Absolute Max (Stress)], [Low $M_w$, Low $D E$],
  [C3], [75], [2.2], [300], [Interior Trajectory], [Moderate $M_w$, Mod $D E$],
  [C4], [95], [3.0], [300], [High T / Low Acid], [Moderate $M_w$, High $D E$],
  [C5], [50], [1.5], [150], [Low T / High Acid], [High $M_w$, Low $D E$]
)
]
*Sampling Schedule*: Withdrawn at $t = 10, 25, 45, 70, 95, 120$ minutes.

Because time points within a single run are autocorrelated, standard cross-validation will overfit. We mandate **Leave-One-Run-Out (LORO) Cross-Validation**. 
*Acceptance Metrics*:
1. *RMSEP*: Must be $< 5\%$ absolute for $D E$/GalA, and $< 50$ kDa for $M_w$.
2. *Stratified RMSEP*: The proxy must not fail catastrophically at extremes (e.g., reported separately for low/med/high ranges).
3. *MAE & Bias*: Residuals must be centered at zero.
4. *Uncertainty Coverage*: The proxy's 95% CI must contain the true reference value 95% of the time on unseen runs ($P(y_{"true"} \in C I_{95\%,"proxy"})$).

== Bayesian Integration
The measurement hierarchy resolves into a clean Directed Acyclic Graph (DAG):
$ text("Kinetic ODE") arrow.r y_{"true"} arrow.r y_{"prepared"} arrow.r z_{"observed"} $

Where $y = (Y, D E, M_w, X_{"GalA"})$ and $z = (text("FTIR"), t_{"flow"}, C_{"ppt"}, C_{"pellet"})$.
Then the posterior over kinetic parameters is obtained by marginalizing the latent physicochemical state:
$ p(theta mid z, x) prop p(theta) integral p(z mid y) p(y mid theta, x) d y $

= Physical Implementation & Minimum Viable Laboratory (MVP)
The hierarchical measurement architecture directly enables a decentralized, low-capital laboratory strategy. By mathematically separating high-frequency proxies from low-frequency ground-truth anchors, the physical execution requires minimal in-house capital expenditure.

== Equipment Sourcing Strategy
The project relies on a hybrid execution model, partnering with university core facilities for spectral and chromatographic capabilities:

1. *In-House (Own / Operate)*: 
   - 1.0 -- 2.0 L jacketed glass reactor (sized to prevent S:L ratio drift during 120 mL cumulative sampling).
   - Continuous RTD temperature logging and pH meters.
   - Standardized precipitation equipment (centrifuge, vacuum oven).
   - Calibrated analytical balance (Critical: drives the entire mass-basis of the kinetic ODE).
   - Capillary viscometer and UV-Vis spectrophotometer.
2. *University / Core Facility Access*: 
   - ATR-FTIR Spectrometer (High-frequency chemical proxy).
   - HPSEC-MALLS (Low-frequency $M_w$ anchor).

Expensive automated bioreactors, inline FTIR sensors, and sophisticated rheometers are explicitly deferred. 

== Analytical Discipline & Traceability
The Bayesian inference engine requires an unbroken relational chain linking the final measurement back to the thermodynamic history of the extraction. 

The primary key for all data ingestion is the composite `SampleID` (e.g., `B002-R07-S03`). This uniquely binds a physical pellet to:
$ t_{"aliquot"} + T(t) + p H(t) + m_{"liquor"} + m_{"pellet"} $
If this chain is broken, the sample may no longer be suitable for kinetic inference because its process history cannot be assigned reliably.

= Conclusion & Execution Map
The mechanistic model has been mathematically verified, structural identifiability resolved via D-optimal design, and the measurement architecture strictly defined. By explicitly modeling sample preparation and measurement uncertainty as part of the Bayesian observation hierarchy, the project is insulated from the capital costs and physical biases that typically derail bioreactor optimization.

The reactor is specified here not merely as a machine producing pectin, but as an experimental measurement instrument built specifically for identifying a dynamic model.

The immediate physical step is the **Phase 1 Proxy Calibration**, generating 30 paired observations across 5 OED extreme trajectories to construct the $p(y mid z)$ measurement likelihoods. Once the chemometric and rheological proxies are validated against the SEC/Titration anchors, the system proceeds to the **10-run OED-selected calibration campaign plus 4 independent validation runs** for final parameter closure.
