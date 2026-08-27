#set page(
  paper: "us-letter",
  margin: (x: 1.25in, y: 1.25in),
  header: align(right)[
    #text(8pt, fill: luma(120))[Pectin Extraction Digital Twin -- V1.4 Comprehensive Research Report]
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
    Hybrid Mechanistic & Bayesian Optimization System for Passion-Fruit Pectin Extraction
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
text("Mechanistic ODE Model") 
arrow.r text("Identifiability & OED") 
arrow.r text("Proxy Calibration") 
arrow.r text("Physical Reactor Campaign") 
arrow.r text("Bayesian Parameter Learning")
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
The state equations combine strict normalized mass conservation [$#text("kg/kg")_{"dry,feed"}$] with mass-weighted moments to track intensive properties ($M_w, DE$) dynamically.
$ (d P_{"sol"}) / (d t) &= k_{"ext"} P_{"matrix"} - k_{"hyd"} P_{"sol"} $
$ (d P_{"lowMW"}) / (d t) &= k_{"hyd"} P_{"sol"} - k_{"deg"} P_{"lowMW"} $

Kinetics are parameterized via an Arrhenius reference-state formulation ($T_{"ref"} = 353.15$ K, $p H_{"ref"} = 2.0$) to dramatically improve the numerical conditioning of the Bayesian inference.

= Structural Identifiability & OED
The serial cascade induces a severe identifiability problem: a fast extraction/fast degradation trajectory looks mathematically identical to a slow extraction/slow degradation trajectory if observed only at the process endpoint.

== Bayesian Optimal Experimental Design (OED)
By computing the Fisher Information Matrix (FIM) over the 10-dimensional parameter space, we designed an exact 10-run protocol that minimizes the determinant of the posterior covariance matrix (D-optimal design). 

The OED algorithm specifically mandates *time-resolved* observation (sampling at $t=15, 45, 90, 120$ min) and pushes the thermodynamic boundaries (e.g., $95^circ$C/pH 1.5 vs $50^circ$C/pH 3.0) to break the $k_{"hyd"} <-> k_{"deg"}$ correlation. The resulting design achieved an excellent condition number ($kappa approx 27.0$).

= Hierarchical Measurement Architecture
The time-resolved OED campaign requires 6 samples per run. Performing conventional SEC-MALLS (for $M_w$), Titration (for $DE$), and mHDP Colorimetry (for GalA purity) on every aliquot is economically unviable. 

We solve this using a Bayesian Proxy Measurement Model. The physical experiment is segmented into a preparation layer and an observation layer.

== The Preparation Model & Precipitation Bias
Direct measurement of raw reactor liquor is invalid due to massive spectral and rheological confounding by unreacted acid, trace metal ions, and simple sugars. All samples undergo **Standardized Alcohol Precipitation**. 

This is not a neutral step. Ethanol fractionation can selectively recover high-$M_w$ pectin while leaving low-$M_w$ fragments in solution. We model this as $\eta_{"precipitation"} = f(M_w, DE)$. The proxy must be calibrated on the exact same precipitated material to absorb this physical bias natively.

== The Proxy Observation Model
We deploy two ultra-fast, low-cost sensors on the standardized precipitate:
1. *FTIR/DRIFTS Spectroscopy*: A chemometric PLS model maps the full mid-IR spectrum to $DE$ and GalA fraction.
2. *Capillary Viscometry*: The flow time ($t_{"flow"}$) at a strictly recorded concentration ($C_{"pellet"}$) is mapped to $M_w$ using passion-fruit-specific empirical constants, replacing the fragile assumption of universal Mark-Houwink parameters.

== Bayesian Integration
The measurement hierarchy resolves into a clean Directed Acyclic Graph (DAG):
$ text("Kinetic ODE") arrow.r y_{"true"} arrow.r y_{"prepared"} arrow.r z_{"observed"} $

Where $y = (Y, DE, M_w, X_{"GalA"})$ and $z = (text("FTIR"), t_{"flow"}, C_{"ppt"}, C_{"pellet"})$.
This formulation allows the digital twin to naturally consume the empirical proxy uncertainty via the Root Mean Square Error of Prediction (RMSEP) derived from a Leave-One-Run-Out (LORO) validation experiment:
$ p(theta mid z) = integral p(theta mid y) p(y mid z) dy $

= Physical Implementation & Minimum Viable Laboratory (MVP)
The hierarchical measurement architecture directly enables a decentralized, low-capital laboratory strategy. By mathematically separating high-frequency proxies from low-frequency ground-truth anchors, the physical execution requires minimal in-house capital expenditure.

== Equipment Sourcing Strategy
The project relies on a hybrid execution model, partnering with university core facilities for spectral and chromatographic capabilities:

1. *In-House (Own / Operate)*: 
   - 1.0 -- 2.0 L jacketed glass reactor (sized to prevent S:L ratio drift during 120 mL cumulative sampling).
   - Continuous RTD temperature logging and pH meters.
   - Standardized precipitation equipment (centrifuge, vacuum oven).
   - Calibrated analytical balance (Critical: drives the entire mass-basis of the kinetic ODE).
   - Capillary viscometer and UV-Vis spectrophotometer (initial cheap proxy and GalA anchor).
2. *University / Core Facility Access*: 
   - ATR-FTIR Spectrometer (High-frequency chemical proxy).
   - HPSEC-MALLS (Low-frequency $M_w$ anchor).

Expensive automated bioreactors, inline FTIR sensors, and sophisticated rheometers are explicitly deferred. The proxy models adapt to the manual but highly standardized benchtop data.

== Analytical Discipline & Traceability
The true bottleneck is not analytical hardware, but data traceability. The Bayesian inference engine requires an unbroken relational chain linking the final measurement back to the thermodynamic history of the extraction. 

The primary key for all data ingestion is the composite `SampleID` (e.g., `B002-R07-S03`). This uniquely binds a physical pellet to:
$ t_{"aliquot"} + T(t) + p H(t) + m_{"liquor"} + m_{"pellet"} $
If this chain is broken, the sample's process history cannot be assigned reliably, rendering it unsuitable for kinetic inference.

= Conclusion & Execution Map
The mechanistic model has been mathematically verified, structural identifiability resolved via D-optimal design, and the measurement architecture strictly defined. By framing the laboratory itself as a probabilistic parameter inside the digital twin, the project is insulated from the capital costs and physical biases that typically derail bioreactor optimization.

The immediate physical step is the **Phase 1 Proxy Calibration**, generating 30 paired observations across 5 OED extreme trajectories to construct the $p(y mid z)$ measurement likelihoods. Once the chemometric and rheological proxies are validated against the SEC/Titration anchors, the system proceeds to the dense 14-run kinetic reactor campaign for final parameter closure.
