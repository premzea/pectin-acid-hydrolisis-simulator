#set page(
  paper: "us-letter",
  margin: (x: 1.25in, y: 1.25in),
  header: align(right)[
    #text(8pt, fill: luma(120))[Pectin Extraction Digital Twin -- V1.3 Research Report]
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
    Hybrid Mechanistic & Machine-Learning \ Optimization System for Pectin Extraction
  ]
  
  #v(1em)
  
  #text(size: 14pt, font: "Inter", fill: luma(80))[
    Virtual Reactor (V1.3 Digital Twin) Mathematical Specification
  ]
  
  #v(3em)
]

#outline(indent: auto)
#pagebreak()

= Initial & Boundary Conditions ($t=0$)
The initial state establishes the mathematical invariants for the fresh rind mass balance. 

- $X_{w,0}$: Initial moisture content (wet basis) $approx 0.81 - 0.86$
- $P_{"matrix",0}$: Initial available protopectin content [$#text("kg/kg")_{"dry,feed"}$]
- $X_{"GalA,matrix"}$: GalA fraction of the matrix pectin
- $D E_{"matrix"}$: Degree of esterification of the matrix pectin

*Explicit Initial Conditions (Masses):*
- $P_{"matrix"}(0) = P_{"matrix",0}$
- $P_{"sol"}(0) = P_{"lowMW"}(0) = P_{"loss"}(0) = 0$
- $G_{"matrix"}(0) = P_{"matrix",0} dot X_{"GalA,matrix"}$
- $G_{"sol"}(0) = G_{"lowMW"}(0) = G_{"loss"}(0) = 0$
- $Q_{D E,"sol"}(0) = 0$
- $M_{w,"sol"}(0) = M_{w,"matrix"}$

_Note: Literature reports for extracted passion-fruit pectin ($D E approx 74.5%$, $M_w approx 6.54 times 10^5$ Da, GalA $approx 78%$) are **Informative Priors for the extracted-product properties**, not assumptions about the fresh rind polymer. DE and MW for the soluble pool are properties of the material entering the pool and are undefined until $P_{"sol"} > 0$._

= Feedstock Conditioning Submodel
== Drying
Moisture removal is tracked explicitly:
$ (d X_w) / (d t) = -k_d (T_{"air"}, v_{"air"}) dot (X_w - X_{w, "eq"}) $

== Milling
Milling reduces the bulk dried rind to a characteristic particle size ($d_{50}$). The model uses a fixed reference size for V1:
$ d_{"ref"} = 300 #text(" μm") $

= Acid Extraction Submodel

== Conceptual Architecture
The physical extraction is modeled as a 4-pool mass transfer system, distinguishing strictly between *mass inventories* (states) and *chemical attributes* (properties).

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

*Terminology:*
- *Hydrolysis* ($k_{"hyd"}):$ Continuous acid-catalyzed chain scission within the soluble pectin population. Material crossing the model's threshold is transferred to the low-MW lumped compartment.
- *Degradation* ($k_{"deg"}):$ Low-MW pectin $arrow.r$ non-pectic soluble products.

== Differential Equations (Normalized Mass Conservation)
All $P_i$ variables use a consistent normalized mass convention [$#text("kg/kg")_{"dry,feed"}$]. 

1. *Solubilization:* $ (d P_{"matrix"}) / (d t) = -k_{"ext"} P_{"matrix"} $
2. *Hydrolysis:* $ (d P_{"sol"}) / (d t) = k_{"ext"} P_{"matrix"} - k_{"hyd"} P_{"sol"} $
3. *Depolymerization:* $ (d P_{"lowMW"}) / (d t) = k_{"hyd"} P_{"sol"} - k_{"deg"} P_{"lowMW"} $
4. *Unrecoverable Loss:* $ (d P_{"loss"}) / (d t) = k_{"deg"} P_{"lowMW"} $

*Invariants & Diagnostics:*
- *Analytical Identity:* $ (d P_{"tot"}) / (d t) = 0 $ where $P_{"tot"} = P_{"matrix"} + P_{"sol"} + P_{"lowMW"} + P_{"loss"}$.
  _The total modeled pectin-derived mass accounting inventory is strictly conserved._
- *Conservation Check:* $ epsilon_M = P_{"matrix", 0} - P_{"tot"} approx 0 $
- *Positivity & Bounds*: $P_i(t) >= 0$, $0 <= D E_i <= 1$, $0 <= X_{"GalA",i} <= 1$, $M_w >= M_{w,"min"} > 0$.

== Cohort-Correct Properties (Moments)
Because pectin continuously enters the soluble pool, material has experienced different cumulative exposures. We model properties using mass-weighted moments.

- *De-esterification Moments:*
  $ (d Q_{D E,"sol"}) / (d t) = k_{"ext"} P_{"matrix"} D E_{"matrix"} - k_{"de"} Q_{D E,"sol"} - k_{"hyd"} Q_{D E,"sol"} $
  $ (d Q_{D E,"lowMW"}) / (d t) = k_{"hyd"} Q_{D E,"sol"} - k_{"de"} Q_{D E,"lowMW"} - k_{"deg"} Q_{D E,"lowMW"} $
  $ D E_{"sol"} = Q_{D E,"sol"} / P_{"sol"} $ , $ D E_{"lowMW"} = Q_{D E,"lowMW"} / P_{"lowMW"} $
  _Note: V1.3 assumes the de-esterification rate constant is identical for soluble intact and low-MW pectin._

- *Molecular Weight Moments:*
  $ (d Q_{M W,"sol"}) / (d t) = k_{"ext"} P_{"matrix"} M_{w,"matrix"} - k_{"hyd"} Q_{M W,"sol"} - beta_{"MW"} k_{"hyd"} (Q_{M W,"sol"} - M_{w,"min"} P_{"sol"}) $
  $ (d Q_{M W,"lowMW"}) / (d t) = k_{"hyd"} Q_{M W,"sol"} - k_{"deg"} Q_{M W,"lowMW"} - beta_{"MW"} k_{"deg"} (Q_{M W,"lowMW"} - M_{w,"min"} P_{"lowMW"}) $
  $ M_{w,"sol"} = Q_{M W,"sol"} / P_{"sol"} $ , $ M_{w,"lowMW"} = Q_{M W,"lowMW"} / P_{"lowMW"} $
  _Note: This moment formulation elegantly avoids the $1 / P$ singularity at $t=0$. The $k_{"deg"}$ term implies degradation continues reducing MW toward $M_{w,"min"}$ in the low-MW transition zone._

== Kinetics & Empirical Extraction Modifiers
Temperature and acidity are parameterized using a reference-state formulation to improve parameter inference numerical stability by decoupling prefactors and activation energies. The model architecture reserves an explicit citric-acid concentration effect ($C_{"citric"}$) on de-esterification; this effect is disabled in V1.3 by fixing $gamma_{"citric"} = 0$.

- *Effective Extraction Rate:* $k_{"ext"} = k_{"ext,chem"} phi_d$
- *Empirical Transport Modifier:* $phi_d = (d_{"ref"} / d_{50})^alpha$ \
  _Note: This is an empirical lumped accessibility/transport correction, not a mechanistic diffusion coefficient._
- *Reference State:* $T_{"ref"} = 353.15$ K, $p H_{"ref"} = 2.0$
- *Reference Arrhenius Form:* \
  $ k = k_{"ref"} exp[-E/R (1 / T_K - 1 / T_{"ref"})] 10^{n(p H_{"ref"} - p H)} $
- *De-esterification:* \
  $ k_{"de"} = k_{"de,ref"} exp[-E_{"de"}/R (1 / T_K - 1 / T_{"ref"})] 10^{n_{"de"}(p H_{"ref"} - p H)} (1 + gamma_{"citric"} C_{"citric"}) $

= Target Metrics (Normalized)
The downstream recovery factor ($eta_{"recovery"}$) is applied at the product stage to account for precipitation/washing/drying losses.

- *Gravimetric Yield:* 
  $Y_p = eta_{"recovery"} (P_{"sol"} + P_{"lowMW"})$
- *GalA Inventories (Tracking Moments):* 
  $ (d G_{"sol"}) / (d t) = k_{"ext"} P_{"matrix"} X_{"GalA,matrix"} - k_{"hyd"} P_{"sol"} X_{"GalA,sol"} $
  $ (d G_{"lowMW"}) / (d t) = k_{"hyd"} P_{"sol"} X_{"GalA,sol"} - k_{"deg"} P_{"lowMW"} X_{"GalA,lowMW"} $
  $ (d G_{"loss"}) / (d t) = k_{"deg"} P_{"lowMW"} X_{"GalA,lowMW"} $
  $X_{"GalA", i} = G_i / P_i$ \
  _Note: In V1, the GalA fraction of matrix-associated pectin is constant during solubilization._
- *Purity:* $"Purity"_{"GalA"} = X_{"GalA,product"} $
- *Useful GalA Recovery:* 
  $Y_{"GalA,extract"} = (G_{"sol"} + G_{"lowMW"}) / G_{"matrix",0}$ 
  $Y_{"GalA,product"} = (eta_{"recovery"} (G_{"sol"} + G_{"lowMW"})) / G_{"matrix",0}$

= Parameter Ontology Table
To avoid mathematical ambiguity, all parameters are strictly assigned an ontology classification.

#align(center)[
#table(
  columns: (auto, auto, auto, auto, auto),
  align: (center, left, center, center, center),
  
  [*Symbol*], [*Meaning*], [*Units*], [*V1 Anchor/Range*], [*Classification*],
  [$T$], [Extraction Temperature], [°C], [45 -- 100 °C], [Controlled Process Variable],
  [$p H$], [Kinetic Acidity], [pH], [1.2 -- 4.5], [Controlled Process Variable],
  [$C_{"citric"}$], [Acid Concentration], [mol/L], [Initial design range = 0.05 -- 0.5 M], [Controlled Process Variable],
  [$t$], [Extraction Time], [min], [5 -- 120 min], [Controlled Process Variable],
  [$X_{w,0}$], [Fresh Moisture], [% wb], [81 -- 86%], [Measured],
  [$d_{50}$], [Particle Size], [μm], [149 -- 500 μm], [Measured],
  [$d_{"ref"}$], [Reference Particle Size], [μm], [300 μm], [Fixed],
  [$M_{w,"matrix"}$], [MW of matrix pectin], [Da], [$6.54 times 10^5$], [Informative prior / Inferred],
  [$k_{"ext,ref"}$, $k_{"hyd,ref"}$, $k_{"deg,ref"}$, $k_{"de,ref"}$], [Reference Rates], [$"min"^(-1)$], [TBD], [Calibrated],
  [$E_{"ext"}$, $E_{"hyd"}$, $E_{"deg"}$, $E_{"de"}$], [Activation Energies], [J/mol], [TBD], [Calibrated],
  [$n_{"ext"}$, $n_{"hyd"}$, $n_{"deg"}$, $n_{"de"}$], [Acidity Orders], [-], [1.0], [Fixed V1],
  [$alpha$], [Particle Size Scaling], [-], [0.5 -- 2.0], [Calibrated],
  [$beta_{"MW"}$], [Hydrolysis-to-MW sensitivity], [-], [1.0], [Fixed V1],
  [$gamma_{"citric"}$], [Citric DE Multiplier], [L/mol], [0.0], [Fixed V1],
  [$eta_{"recovery"}$], [Recovery Efficiency], [-], [0.90], [Measured / Fixed Protocol],
)
]

_Physical Constants:_ \
$R = 8.314462618 " J/mol K"$ \
$T_K = T_"C" + 273.15$ \
$T_{"ref"} = 353.15$ K \
$p H_{"ref"} = 2.0$
