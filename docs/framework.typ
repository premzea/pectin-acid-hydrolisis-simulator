#import "@preview/merman:0.2.0": *

== From Mechanistic Models to Self-Learning Experimental Systems: A Bayesian Framework for Scientific Process Optimization
<from-mechanistic-models-to-self-learning-experimental-systems-a-bayesian-framework-for-scientific-process-optimization>
Mechanistic Modeling, Identifiability, Optimal Experimental Design,
Proxy Measurements, Surrogate ML, Bayesian Inference, and Closed-Loop
Learning

== 1. Executive Overview
== The Central Problem
<executive-overview-the-central-problem>
In modern scientific discovery and process engineering, we routinely
encounter a fundamental bottleneck: optimizing a complex physical system
where experiments are highly expensive, time-consuming, or destructive,
and the underlying physical or chemical phenomena are only partially
understood. When data are sparse and measurements are slow, traditional
trial-and-error exploration or unguided grid searches become
prohibitively costly. Furthermore, physical observations are invariably
corrupted by sensor noise, and our model parameters carry deep,
intrinsic uncertainties. If we cannot quantify what our models do not
know, we risk making catastrophic or highly sub-optimal decisions during
process scale-up.
== The Central Philosophy To overcome these
limitations, we must abandon the naive paradigm of treating a physical
system as a black box---where one simply collects a fixed grid of data,
fits a generic machine learning model, and hopes for accurate
predictions. Instead, this document presents a unified framework for a
structured scientific learning system.

#quote(block: true)[
  *Don't simply collect data and fit a black-box model. Build a system that knows what it knows, identifies what it does not know, chooses informative experiments, leverages cheap proxy measurements, and dynamically updates itself as new evidence arrives.*
]

== The Unified System Architecture
<the-unified-system-architecture>
The self-learning framework is cyclical and adaptive. It tightly couples
physical intuition with statistical rigor across ten core phases:

#mermaid(
  ```
  graph TD
    A[Mechanistic Model Formulation] --> B[Numerical Verification & Sanity Checks]
    B --> C[Identifiability Analysis SVD / FIM]
    C --> D[Optimal Experimental Design OED]
    D --> E[Executing Physical Experiments]
    E --> F[Proxy / Measurement Calibration Models]
    F --> G[Bayesian Parameter Inference MCMC]
    G --> H[Model Discrepancy & Validation Assessments]
    H --> I[Uncertainty-Aware Optimization & ML Surrogates]
    I --> J[Active Learning / Next-Best Action Selection]
    J -->|Loop Back to OED| D
  ```,
)

== Roles and Interactions of the Core Components
<roles-and-interactions-of-the-core-components>
- Mechanistic Modeling: Encapsulates established physical laws (e.g.,
  mass conservation, thermodynamics, reaction kinetics) using Ordinary
  Differential Equations (ODEs). It guarantees physical plausibility
  (such as mass conservation and state positivity) even when
  extrapolating far outside the training data.
- Identifiability Analysis: Determines whether the available sensor
  measurements contain sufficient information to uniquely resolve the
  parameters of our mechanistic model. It maps out mathematical
  "sloppiness"---directions in parameter space where completely
  different values yield identical experimental observations.
- Optimal Experimental Design (OED): Uses mathematical sensitivities to
  algorithmically select the most informative experimental inputs (e.g.,
  temperature, time, concentrations). It ensures that every dollar spent
  on physical trials directly collapses parameter uncertainty along the
  sloppiest directions.
- Proxy Measurement Models: Bridges the gap between what we wish to
  measure (expensive, slow, destructive offline metrics) and what we can
  easily monitor (cheap, rapid online surrogates like spectroscopy,
  refractive index, or pH).
- Bayesian Inference: Replaces rigid, single-point parameter estimates
  with full joint probability distributions ($p\(theta divides D\)$). It
  naturally combines prior scientific literature with noisy, sparse data
  to map exactly how well each parameter is known.
- Model Discrepancy and Validation: Explicitly tests the structural
  flaws of the model. It quantifies systematic deviations between
  reality and mathematical assumptions, preventing the learning loop
  from becoming overconfident in a wrong model structure.
- Surrogate Machine Learning and Active Learning: Accelerates the
  closed-loop optimization cycle. While running a complex ODE model or
  full Bayesian inference can be computationally intensive, a fast
  Gaussian Process (GP) or neural network surrogate can approximate the
  system's behavior. Combined with an acquisition function, it evaluates
  thousands of candidate designs per second to identify the single
  next-best experiment that balances exploiting known high-performing
  regions with exploring unknown operational spaces.

== 2. The Core Distinction: Forward vs.~Inverse Problems
<the-core-distinction-forward-vs.-inverse-problems>
To design a self-learning system, one must master the mathematical
asymmetry between moving from causes to effects, versus moving from
effects back to causes. \#\# Mathematical Definitions

#mermaid(
  ```
  graph LR
    subgraph FORWARD PROBLEM
      direction LR
      A[Inputs x + Parameters theta] --> B[Model]
      B --> C[Observations y]
    end
    subgraph INVERSE PROBLEM
      direction LR
      A2[Observations y + Inputs x] --> B2[Algorithm]
      B2 --> C2[Parameters theta]
    end
  ```,
)


#mermaid(
  ```
  graph LR
    subgraph FORWARD PROBLEM
      direction LR
      A[Inputs x + Parameters theta] --> B[Model]
      B --> C[Observations y]
    end
    subgraph INVERSE PROBLEM
      direction LR
      A2[Observations y + Inputs x] --> B2[Algorithm]
      B2 --> C2[Parameters theta]
    end
  ```,
)
The Forward Problem is mathematically deterministic and well-posed.
Given a vector of operating inputs $x$ and a concrete vector of physical
parameters $theta$, we evaluate a forward operator $cal(F)$ (such as an
analytical equation or a numerical ODE integrator) to uniquely predict
the experimental observations $y$:

$ y = cal(F)\(x\,theta\)+ epsilon.alt $

where $epsilon.alt$ represents random measurement noise. If $cal(F)$ is
properly defined, a single unique output $y$ always exists for a given
pair of $x$ and $theta$. The Inverse Problem is fundamentally ill-posed,
highly non-linear, and non-unique. Given a set of experimental inputs
$x$ and real-world observations $y$, we seek to reconstruct the
underlying physical parameters $theta$:

$ theta = cal(F)^(- 1)\(y\,x\) $

Inverse problems are extraordinarily difficult because the mapping
$cal(F)^(- 1)$ is frequently one-to-many. Vastly different, physically
distinct parameter sets $theta_A$ and $theta_B$ can yield identical or
indistinguishable forward outputs $y$, hiding within the noise window
$epsilon.alt$. \#\# Kinetic Counterexample: Simple Sequential Reaction
Consider a basic chemical cascade where component $A$ transforms into
intermediate $B$ with rate constant $k_1$, which then degrades into
waste product $C$ with rate constant $k_2$:

$ A arrow.r^(k_1) B arrow.r^(k_2) C $

If an experimenter only measures the concentration of the intermediate
product $B$ at a single, late timestamp $t_(upright("end"))$, the
forward calculation easily yields a specific concentration
$B\(t_(upright("end"))\)$. However, solving the inverse problem to find
$k_1$ and $k_2$ from that single endpoint is impossible. A fast
production rate coupled with a fast degradation rate
($k_1 gt.double 0\,k_2 gt.double 0$) can result in the exact same
late-stage concentration of $B$ as a very slow production rate coupled
with a slow degradation rate ($k_1 approx 0\,k_2 approx 0$). The problem
is underdetermined; the parameters are structurally non-identifiable
from that specific data footprint. \#\# The Running Example:
Passion-Fruit Pectin Acid-Hydrolysis Throughout this document, we ground
these abstract concepts in a real-world chemical optimization problem:
the extraction and degradation of pectin from passion-fruit peel waste
via acid hydrolysis. Pectin is a high-value structural polysaccharide
used as a gelling agent. Its yield and quality depend on a multi-step
reaction cascade where protopectin inside the plant matrix is dissolved,
broken down into functional polymers, and ultimately destroyed by
over-hydrolysis. We represent this via a four-pool structural kinetic
cascade:

$
  upright("P")_(upright("matrix")) arrow.r^(k_(upright("ext"))) upright("P")_(upright("sol")) arrow.r^(k_(upright("hyd"))) upright("P")_(upright("lowMW")) arrow.r^(k_(upright("deg"))) upright("P")_(upright("loss"))
$

Where:

- $upright("P")_(upright("matrix"))$ is the insoluble protopectin locked
  within the passion-fruit peel matrix.
- $upright("P")_(upright("sol"))$ is the extracted,
  high-molecular-weight soluble pectin (the highly prized target product
  responsible for premium gelling properties).
- $upright("P")_(upright("lowMW"))$ is over-hydrolyzed,
  low-molecular-weight pectin fragments (which possess poor gelling
  behavior but still count toward total extracted carbohydrate mass).
- $upright("P")_(upright("loss"))$ represents total degradation products
  (furfural derivatives, monosaccharides, and char) resulting from
  aggressive acid and thermal exposure.

The speed of these transitions is governed by three
temperature-dependent kinetic rate constants:

+ $k_(upright("ext"))$: The extraction rate constant moving pectin from
  the solid matrix into solution.
+ $k_(upright("hyd"))$: The hydrolysis rate constant cleaving large
  polymer chains into functional but smaller segments.
+ $k_(upright("deg"))$: The thermal/acid degradation rate constant
  destroying the carbohydrate structure.

== The Deception of Black-Box Metrics ($R^2$)
<the-deception-of-black-box-metrics-r2>
Suppose an experimenter records only two metrics at the end of a
60-minute extraction batch: Total Pectin Yield (the sum of
$upright("P")_(upright("sol")) + upright("P")_(upright("lowMW"))$) and
Apparent Viscosity (which correlates with the average molecular weight).
A standard machine learning model or an unconstrained optimization
algorithm can easily be trained on this data. It might achieve a
spectacular coefficient of determination ($R^2 = 0.99$) on the forward
predictions of yield. However, this high $R^2$ is deeply deceptive. It
provides a false sense of security because it says absolutely nothing
about parameter identifiability. Because the data are only collected at
the batch endpoint ($t = 60 upright(" min")$), a scenario with a
massive, rapid extraction rate accompanied by aggressive degradation
($k_(upright("ext")) gt.double 0\,k_(upright("deg")) gt.double 0$) will
produce an identical endpoint yield to a scenario with a sluggish
extraction rate and negligible degradation
($k_(upright("ext")) approx 0\,k_(upright("deg")) approx 0$). The
forward surrogate model successfully interpolates the surface curve
($R^2 approx 1$), but its internal parameter values are highly
inaccurate. If you attempt to use that model to scale up the reactor
volume, alter the heating profile, or predict behavior at
$t = 15 upright(" min")$, the model will fail catastrophically because
it did not solve the true inverse problem. It merely memorized a
non-unique forward mapping.

== 3. Mechanistic Process Modeling\#\# Anatomy of a Mechanistic Model
<mechanistic-process-modeling-anatomy-of-a-mechanistic-model>
Unlike empirical black-box equations (such as polynomials, random
forests, or deep neural networks) which simply fit lines to arbitrary
shapes, a mechanistic model derives its mathematical form directly from
physical constraints and structural hypotheses. A standard
continuous-time mechanistic process model is formalized as a system of
parameterized ordinary differential equations:

$ frac(d upright(bold(w)), d t) = upright(bold(f))\(upright(bold(w))\(t\)\,upright(bold(x))\(t\)\,bold(theta)\) $

$ upright(bold(y))\(t\)= upright(bold(g))\(upright(bold(w))\(t\)\,upright(bold(x))\(t\)\,bold(theta)\) $

Where:

- $upright(bold(w))\(t\)in bb(R)^(n_w)$ is the vector of internal system
  states (e.g., true, unobserved physical concentrations inside the
  reactor phase).
- $upright(bold(x))\(t\)in bb(R)^(n_x)$ is the vector of inputs or
  control variables manipulated by the investigator (e.g., setpoint
  temperature $T$, acid concentration or $upright("pH")$,
  solid-to-liquid ratio, raw material particle size $d_p$).
- $bold(theta) in bb(R)^(n_theta)$ is the vector of invariant physical
  parameters (e.g., pre-exponential frequency factors, activation
  energies, mass transfer coefficients).
- $upright(bold(y))\(t\)in bb(R)^(n_y)$ is the vector of observables or
  measurements generated by instruments. Crucially, $upright(bold(y))$
  is often a lower-dimensional projection of $upright(bold(w))$
  corrupted by noise, as we rarely measure every internal state
  directly.
- $upright(bold(f))$ represents the structural transition vector field
  dictated by conservation laws.
- $upright(bold(g))$ represents the measurement mapping function.

== The Pectin 4-Pool Kinetic Differential Equations
<the-pectin-4-pool-kinetic-differential-equations>
Applying this formal structure to our acid-hydrolysis cascade, we define
our four states as mass fractions normalized to the total initial
insoluble protopectin available in the peel matrix:

$
  upright(bold(w))\(t\)= mat(delim: "[", P_(upright("matrix"))\(t\); P_(upright("sol"))\(t\); P_(upright("lowMW"))\(t\); P_(upright("loss"))\(t\))
$

The governing system of non-linear differential equations is formulated
as:

$ frac(d P_(upright("matrix")), d t) = - k_(upright("ext"))\(T\,d_p\)dot.op P_(upright("matrix")) $

$
  frac(d P_(upright("sol")), d t) = k_(upright("ext"))\(T\,d_p\)dot.op P_(upright("matrix")) - k_(upright("hyd"))\(T\,upright("pH")\)dot.op P_(upright("sol"))
$

$
  frac(d P_(upright("lowMW")), d t) = k_(upright("hyd"))\(T\,upright("pH")\)dot.op P_(upright("sol")) - k_(upright("deg"))\(T\,upright("pH")\)dot.op P_(upright("lowMW"))
$

$ frac(d P_(upright("loss")), d t) = k_(upright("deg"))\(T\,upright("pH")\)dot.op P_(upright("lowMW")) $

The kinetics are explicitly driven by environmental inputs. The rate
constants follow a modified Arrhenius formulation to capture the
non-linear impacts of Temperature ($T$, in Kelvin) and chemical
catalysts ($upright("pH")$ or particle size $d_p$):

$
  k_(upright("ext"))\(T\,d_p\)= A_(upright("ext")) dot.op (1 / d_p)^alpha dot.op exp (- frac(E_(a\,upright("ext")), R dot.op T))
$

$
  k_(upright("hyd"))\(T\,upright("pH")\)= A_(upright("hyd")) dot.op (10^(- upright("pH")))^beta dot.op exp (- frac(E_(a\,upright("hyd")), R dot.op T))
$

$
  k_(upright("deg"))\(T\,upright("pH")\)= A_(upright("deg")) dot.op (10^(- upright("pH")))^gamma dot.op exp (- frac(E_(a\,upright("deg")), R dot.op T))
$

Where $R$ is the universal gas constant, $A_i$ are the pre-exponential
frequency factors, $E_(a\,i)$ are the activation energies, and
$alpha\,beta\,gamma$ are scaling exponents representing mass transfer
and acid-catalysis intensities. \#\# The Value of Lumped, Abstracted
Frameworks Real passion-fruit pectin does not exist as three neat,
isolated molecular categories. It is a highly heterogeneous polydisperse
polymer network containing hundreds of distinct chain lengths, branching
degrees, and esterification patterns. Our 4-pool model is fundamentally
an abstracted lumped model. It condenses an infinite-dimensional polymer
molecular weight distribution into four discrete operational
"compartments." Despite being molecularly incomplete, lumped models are
remarkably powerful tools for process engineering. They avoid the
computational intractability and over-parameterization of tracking
thousands of individual polymer lengths. Instead, they focus entirely on
macroscopic engineering metrics. By capturing the primary, dominant
pathways of mass transport and chemical transformation, they remain
highly predictive for industrial control, provided their parameters are
rigorously identified. \#\# Physical Constraints and Mathematical
Invariants A primary advantage of mechanistic formulations over
black-box models is their intrinsic adherence to physical laws. This
provides stability when extrapolating to unmeasured operating
conditions. \#\# 1. Conservation Invariants Because the 4-pool
differential equations describe a closed mass cascade where mass leaving
one pool must immediately enter the next, the total mass is conserved
perfectly at every point in time. Summing the vector field yields:

$ frac(d, d t) (P_(upright("matrix")) + P_(upright("sol")) + P_(upright("lowMW")) + P_(upright("loss"))) = 0 $

Integrating this expression from $t = 0$ with initial conditions
$upright(bold(w))\(0\)=\[1\,0\,0\,0\]^T$ reveals a strict linear
invariant:

$ sum_(i = 1)^4 w_i\(t\)= 1.0 quad forall t gt.eq 0 $

If a machine learning algorithm predicts a total mass sum of $1.05$ or
$0.92$, it violates the first law of thermodynamics. The mechanistic
model renders such physical impossibilities mathematically impossible.
\#\# 2. Strict State Positivity Because concentrations cannot be
negative, the model's equations naturally enforce a lower bound at zero.
For any pool $w_i$, its outflow rate is directly proportional to its
current concentration ($w_i$). As any pool approaches zero, its
evacuation rate drops smoothly to zero:

$ lim_(w_i arrow.r 0^(+)) frac(d w_i, d t) gt.eq 0 $

This mathematical structure guarantees that if the system initializes
with non-negative mass ($upright(bold(w))\(0\)gt.eq upright(bold(0))$),
all states remain strictly positive
($upright(bold(w))\(t\)in\[0\,1\]^4$) across all time horizons
$t in\[0\,oo\)$. Empirical models like polynomials frequently dip into
unphysical negative predictions when extrapolating into harsh processing
regions.

== 4. Model Verification vs.~Model Validation
<model-verification-vs.-model-validation>
Engineers frequently conflate verification and validation, using them
interchangeably. In scientific machine learning and system
identification, they represent distinct, non-overlapping tasks.

#mermaid(
  ```
  graph TD
    subgraph MATHEMATICAL DESIGN
      direction TB
      A[Is the software correct?] --> B[CODE VERIFICATION]
      B --> C[Checks for bugs, typos, and numerical integration accuracy]
    end
    subgraph PHYSICAL REALITY
      direction TB
      D[Is the science correct?] --> E[MODEL VALIDATION]
      E --> F[Compares model outputs against real experimental data]
    end
  ```,
)

== Code Verification
<code-verification>
Verification asks: "Did we build the model right?" It is a purely
mathematical and software engineering exercise. It verifies that the
computer code accurately solves the intended underlying differential
equations without numerical errors, typos, or software bugs.
Verification is completely indifferent to whether the chemistry
represents real passion-fruit peels. It checks only that the
mathematical engine operates correctly. \#\# 1. Conservation and
Positivity Tests Run the ODE solver at extreme edge-case settings (e.g.,
$T = 400^compose upright("C")$, $upright("pH") = - 1.0$). Assert via
unit tests that $sum w_i\(t\)= 1.00000$ to double-precision tolerance
and that no state ever goes negative. If mass leaks, your solver
tolerance is too loose or you made a typo in the vector field equations.
\#\# 2. Synthetic Parameter Recovery (The "Twin" Test) Before using
real-world data, generate a synthetic data footprint.

- Step A: Define a known, hidden vector of "true" parameters
  $bold(theta)_(upright("true"))$.
- Step B: Run the forward model to generate synthetic clean data tracks
  $upright(bold(y))_(upright("clean"))$.
- Step C: Corrupt these tracks with artificial Gaussian noise to
  simulate a real sensor:
  $upright(bold(y))_(upright("noisy")) = upright(bold(y))_(upright("clean")) + cal(N)\(0\,sigma^2\)$.
- Step D: Pass $upright(bold(y))_(upright("noisy"))$ into your parameter
  optimization or Bayesian inference engine, starting from random
  initial guesses.

If the optimization algorithm cannot accurately recover
$bold(theta)_(upright("true"))$ from noise-free or low-noise synthetic
data, it is mathematically impossible for it to succeed with real-world
data. Failing a synthetic recovery test indicates structural
non-identifiability or a broken optimization algorithm. \#\# Model
Validation Validation asks: "Did we build the right model?" It is a
scientific and empirical exercise. It evaluates whether our verified
mathematical equations accurately capture real-world physics and
chemistry. Passing software unit tests and successfully recovering
parameters from synthetic data does not prove the underlying chemistry
is correct. It merely proves your internal computational pipeline is
self-consistent. If your model assumes pectin degrades via a first-order
kinetic pathway ($k_(upright("deg")) dot.op P_(upright("lowMW"))$), but
real pectin actually degrades via an autocatalytic or multi-molecular
pathway, your code will run perfectly, pass verification unit tests, and
yet fail validation. Validation requires collecting independent data
from physical experiments that were never used to train the model, and
checking if the model's predictions align with reality.

== 5. Identifiability
<identifiability>
Before attempting parameter estimation, we must determine if our
parameters can actually be recovered from the data we plan to collect.
This is the study of identifiability. \#\# Structural vs.~Practical
Identifiability

- Structural Identifiability: Analyzes the ideal mathematical structure
  of the equations under the assumption of perfect, continuous,
  noise-free observations ($sigma = 0\,t in\[0\,oo\)$). It answers: In a
  world with perfect data, does the mapping from parameter space to
  observation space remain one-to-one? If two distinct parameters
  mathematically collapse to the exact same observation curve, the model
  is structurally non-identifiable. This represents a fundamental flaw
  in how the equations are written.
- Practical Identifiability: Assumes the model is structurally sound,
  but acknowledges that real experiments yield only a handful of
  discrete, highly noisy measurements ($t_1\,t_2\,dots.h\,t_N$). It
  answers: Can we accurately resolve these parameters given our limited
  sample size and sensor noise?

== Parameter Compensation and "Sloppy" Directions
<parameter-compensation-and-sloppy-directions>
In complex systems, parameters rarely act in complete isolation.
Instead, they often compensate for one another. For instance, an
increase in a reaction rate constant can be almost perfectly offset by a
corresponding change in an activation energy or a mass transfer
coefficient. This creates a flat valley or "trough" in the optimization
landscape. The individual parameters cannot be uniquely resolved; only
their combined ratio or product is identifiable. The direction along the
valley floor is known as a sloppy direction, whereas the steep walls of
the valley represent stiff directions.

#mermaid(
  ```
  graph TD
    subgraph Parameter Identifiability SVD
      A[Stiff Direction: High Sensitivity] --- B((Parameter Estimate))
      B --- C[Sloppy Direction: Parameter compensation valley]
    end
  ```,
)



== The Sensitivity Matrix
<the-sensitivity-matrix>
The primary tool for diagnosing local identifiability is the Sensitivity
Matrix, $upright(bold(S))$. It tracks how much each predicted
observation $y_i$ shifts at a specific time step $t_k$ when a parameter
$theta_j$ is perturbed slightly:

$ S_(k\,j) = frac(partial y_i\(t_k\), partial theta_j) $

Because different parameters use vastly different physical units (e.g.,
pre-exponential factors can be on the order of
$10^13 upright(" s")^(- 1)$ while activation energies are around
$10^5 upright(" J/mol")$), direct raw sensitivities are uninterpretable
and scale-dependent. We must convert them into dimensionless logarithmic
sensitivities:

$ tilde(S)_(k\,j) = frac(partial y_i\(t_k\), partial ln theta_j) = theta_j frac(partial y_i\(t_k\), partial theta_j) $

The value $tilde(S)_(k\,j)$ represents the absolute change in the
predicted measurement caused by a $100 %$ relative change in parameter
$theta_j$, making direct comparisons across different physical scales
possible. \#\# The Fisher Information Matrix (FIM) The Fisher
Information Matrix ($upright(bold(F))$) condenses these sensitivities
across all sample points and factors in the instrument's measurement
uncertainty. Assuming independent, identically distributed Gaussian
measurement noise with variance $sigma^2$, the FIM is computed as:

$
  upright(bold(F)) = upright(bold(S))^T upright(bold(W)) upright(bold(S)) = 1 / sigma^2 upright(bold(S))^T upright(bold(S))
$

Where $upright(bold(W))$ is a weighting matrix (typically the inverse of
the noise covariance matrix). The FIM holds a profound physical meaning:
according to the Cramér-Rao Bound, the inverse of the Fisher Information
Matrix sets the absolute lower bound on the variance-covariance matrix
of any unbiased parameter estimator:

$ upright(bold(C o v))\(bold(theta)\)gt.eq upright(bold(F))^(- 1) $

- If a model has massive information, the entries of $upright(bold(F))$
  are large, $upright(bold(F))^(- 1)$ is small, and parameter
  uncertainty shrinks.
- If the entries of $upright(bold(F))$ approach zero, or if
  $upright(bold(F))$ is singular, the parameter uncertainty explodes to
  infinity.

== Singular Value Decomposition (SVD) of the FIM
<singular-value-decomposition-svd-of-the-fim>
To diagnose exactly which parameters are compensating for each other, we
compute the Singular Value Decomposition of our scaled sensitivity
matrix or the corresponding FIM:

$ upright(bold(F)) = upright(bold(V)) bold(Sigma) upright(bold(V))^T $

Where:

- $bold(Sigma) = upright("diag")\(sigma_1\,sigma_2\,dots.h\,sigma_(n_theta)\)$
  contains the sorted singular values
  ($sigma_1 gt.eq sigma_2 gt.eq dots.h gt.eq sigma_(n_theta)$).
- $upright(bold(V))$ is an orthogonal matrix whose columns
  $upright(bold(v))_i$ represent the principal axes of the parameter
  uncertainty ellipsoid.

== Physical Interpretation
<physical-interpretation>
$ upright("The Condition Number ") kappa = sigma_(upright("maximum")) / sigma_(upright("minimum")) $

If $kappa > 10^4$, the matrix is numerically ill-conditioned. The
right-singular vectors $upright(bold(v))_i$ corresponding to the
smallest singular values ($sigma_(upright("minimum"))$) define the
near-null space or the sloppy parameter combinations. If a vector
$upright(bold(v))_(n_theta)$ has large coefficients for both $theta_3$
and $theta_5$, it explicitly informs the engineer that $theta_3$ and
$theta_5$ cannot be isolated from the current experimental setup; only
their combined interaction is visible. \#\# Running Pectin Example:
Arrhenius Parameter Correlation When fitting our pectin kinetics,
optimization algorithms often uncover a massive, near-perfect linear
correlation ($r > 0.99$) between the pre-exponential frequency factor
and the activation energy within the hydrolysis and degradation loops:

$
  ln A_(upright("hyd")) arrow.l.r E_(a\,upright("hyd")) quad upright("and") quad ln A_(upright("deg")) arrow.l.r E_(a\,upright("deg"))
$

Physically, this occurs because experiments are often conducted across a
relatively narrow temperature window (e.g., $70^compose upright("C")$ to
$90^compose upright("C")$). Over this short range, an overestimation of
the baseline reaction velocity ($ln A$) can be perfectly counterbalanced
by an overestimation of the thermal barrier ($E_a$), resulting in an
identical reaction rate constant $k\(T\)$ inside that narrow window. The
SVD analysis will reveal a clear sloppy direction: a highly elongated
uncertainty ellipse. To break this correlation, the engineer must
redesign the experiment to include wider temperature extremes, forcing
the model to dissociate the baseline velocity from the thermal
sensitivity.

== 6. Experimental Design as an Information Problem
<experimental-design-as-an-information-problem>
Data shouldn't be collected passively. We must explicitly design
experiments to maximize the information content of our Fisher
Information Matrix. \#\# Classical vs.~Information-Based Designs

- Factorial / Space-Filling Designs (e.g., Latin Hypercube Sampling):
  Spread points evenly across the input space. While effective for
  empirical black-box modeling, they are highly inefficient for
  mechanistic systems because they spend precious resources sampling
  uninformative regions where reactions have either stalled or gone to
  complete degradation.
- Information-Based Designs (Optimal Experimental Design - OED):
  Evaluate the sensitivity matrix of the underlying ODE model. They
  intentionally target regions where the sensitivities
  $frac(partial y, partial theta)$ are maximized, actively focusing
  experimental efforts where the model's parameters are most sensitive
  to observation.

== Alphabetic Optimality Criteria
<alphabetic-optimality-criteria>
OED operates by converting the multi-dimensional Fisher Information
Matrix $upright(bold(F))$ into a single scalar metric
$Phi\(upright(bold(F))\)$ to be optimized:

#figure(
  align(center)[#table(
    columns: (33.33%, 33.33%, 33.33%),
    align: (auto, auto, auto),
    table.header(
      [Criterion],
      [Mathematical Formulation],
      [Physical
        Optimization Objective],
    ),
    table.hline(),
    [D-Optimality],
    [$max ln det\(upright(bold(F))\)$],
    [Minimizes the
      total volume of the parameter confidence ellipsoid.],
    [A-Optimality],
    [$min upright("Tr")\(upright(bold(F))^(- 1)\)$],
    [Minimizes
      the average variance of the parameter estimates.],
    [E-Optimality],
    [$max lambda_min\(upright(bold(F))\)$],
    [Maximizes
      the minimum eigenvalue, directly shortening the longest (sloppiest)
      uncertainty axis.],
  )],
  kind: table,
)

== Why D-Optimality is Preferred Numerically
<why-d-optimality-is-preferred-numerically>
The D-optimality criterion maximizes the log-determinant of the FIM:

$ Phi_D = ln det\(upright(bold(F))\) $

Taking the logarithm transforms a product of eigenvalues into a sum,
which provides significant numerical stability. It prevents
computational underflow or overflow when dealing with parameters
spanning multiple orders of magnitude. Geometrically, maximizing the
determinant is equivalent to minimizing the volume of the joint
parameter uncertainty region. \#\# Running Pectin Example: The Value of
Strategic Sampling An automated D-optimal experimental design algorithm
applied to our passion-fruit pectin model reveals intuitive physical
insights:

- Temperature Extremes Identify Activation Energies: The algorithm
  avoids moderate temperatures ($80^compose upright("C")$) and instead
  places experiments at the absolute operational boundaries
  ($60^compose upright("C")$ and $100^compose upright("C")$). This
  maximum spread provides the necessary leverage to break the
  correlation between $ln A$ and $E_a$.
- Particle Size Extremes Isolate $alpha$: To isolate the mass transfer
  scaling parameter $alpha$, the system couples very small, finely
  ground peel particles with large, unground peel chunks. This directly
  exposes how physical dimensions limit the extraction rate constant
  $k_(upright("ext"))$.
- Early and Intermediate Residence Times Distinguish Hydrolysis from
  Degradation: If an engineer only samples at the end of a batch
  ($t = 60 upright(" min")$), the functional pectin pool
  $upright("P")_(upright("sol"))$ has already degraded into
  $upright("P")_(upright("lowMW"))$ and
  $upright("P")_(upright("loss"))$. The D-optimal algorithm corrects
  this by scheduling frequent, rapid sampling events at
  $t = 3\,7\,upright(" and ") 15 upright(" minutes")$. These early
  snapshots capture the rapid rise of $upright("P")_(upright("sol"))$
  before degradation dominates, cleanly separating $k_(upright("hyd"))$
  from $k_(upright("deg"))$.

== Greedy Sequential Selection vs.~Global Optimization
<greedy-sequential-selection-vs.-global-optimization>
- Global Optimization: Solves for a comprehensive matrix of experimental
  runs simultaneously before entering the laboratory. While
  mathematically rigorous, it is brittle. It assumes your initial
  nominal parameter guesses are accurate. If those initial guesses are
  wrong, the global design can perform poorly.
- Greedy Sequential Selection: Executes one single optimal experiment
  (or a small batch) at a time. The resulting data are immediately
  processed through the inference engine to update the parameter
  estimates. The system then re-calculates the next single best
  experiment based on this updated knowledge. This adaptive approach
  protects the system against poor initial parameter guesses.

== Practical Operational Constraints
<practical-operational-constraints>
An unconstrained algorithm might suggest operating at a destructive
$upright("pH")$ of $- 0.5$, running a reaction for 10 hours, or taking
samples every 3 seconds. Real self-learning systems must incorporate
physical and operational boundaries directly into their optimization
constraints:

$ max_(upright(bold(x)) in cal(X)) ln det upright(bold(F))\(upright(bold(x))\) $

$
  upright("Subject to: ") cases(delim: "{", 2.0 lt.eq upright("pH") lt.eq 4.5 & upright("(Corrosion/safety boundary)"), 60^compose upright("C") lt.eq T lt.eq 100^compose upright("C") & upright("(Atmospheric boiling limits)"), Delta t_(upright("sampling")) gt.eq 2 upright(" min") & upright("(Human/autosampler speed limits)"))
$

== 7. Bayesian Inference from First Principles
<bayesian-inference-from-first-principles>
When dealing with sparse, noisy data, single-point parameter estimates
(like Maximum Likelihood Estimation) are insufficient. They offer no
insight into parameter uncertainty or correlations. We use Bayesian
inference to treat parameters as probability distributions rather than
fixed points. \#\# The Foundational Mechanics Bayesian inference updates
our prior beliefs about a system after confronting them with real-world
data. It is governed by Bayes' Theorem:

$ p\(bold(theta) divides D\)= frac(p\(D divides bold(theta)\)thin p\(bold(theta)\), p\(D\)) $

Where:

- $p\(bold(theta)\)$ is the Prior Distribution. It encapsulates
  everything we know about the parameters before conducting the current
  experiment (e.g., thermodynamic laws, literature values for similar
  reactions).
- $p\(D divides bold(theta)\)$ is the Likelihood Function. It measures
  the probability that our instruments would record the observed data
  $D$ if the true parameters were exactly $bold(theta)$.
- $p\(bold(theta) divides D\)$ is the Posterior Distribution. This is
  our ultimate destination: the updated joint probability distribution
  reflecting our refined knowledge of the parameters.
- $p\(D\)= integral_Theta p\(D divides bold(theta)\)p\(bold(theta)\)d bold(theta)$
  is the Evidence or Marginal Likelihood. It acts as a normalizing
  constant ensuring the posterior integrates to $1.0$.

== Defining the Likelihood Function
<defining-the-likelihood-function>
Let our real physical observations at discrete times be corrupted by
independent Gaussian measurement noise:

$
  y_(upright("observed"))\(t_k\)= y_(upright("model"))\(t_k\,bold(theta)\)+ epsilon.alt_k\,quad epsilon.alt_k tilde.op cal(N)\(0\,sigma^2\)
$

The likelihood of observing a dataset of $N$ measurements given the
parameter vector $bold(theta)$ is computed by taking the product of
their individual Gaussian probability densities:

$
  p\(D divides bold(theta)\,sigma\)= product_(k = 1)^N 1 / sqrt(2 pi sigma^2) exp (- frac((y_(upright("observed")) \( t_k \) - y_(upright("model")) \( t_k \, bold(theta) \))^2, 2 sigma^2))
$

Taking the natural logarithm turns this product into a computationally
stable sum of squares:

$
  ln p\(D divides bold(theta)\,sigma\)= - N / 2 ln\(2 pi\)- N ln\(sigma\)- frac(1, 2 sigma^2) sum_(k = 1)^N (y_(upright("observed")) \( t_k \) - y_(upright("model")) \( t_k \, bold(theta) \))^2
$

This reveals why minimizing the sum of squared errors in standard
regression is mathematically equivalent to maximizing the log-likelihood
under an assumption of homoscedastic Gaussian noise. \#\# Informative
vs.~Uninformative Priors The choice of prior defines the starting point
of our learning system:

```
graph TD
  subgraph Uninformative Prior
    A[Uniform / Broad distribution]
  end
  subgraph Informative Prior
    B[Gaussian / Literature Bound]
  end
```
)

- Uninformative Priors (Flat/Uniform): Used when there is no prior data
  for a parameter. We assign a wide uniform distribution,
  $p\(theta\)tilde.op upright("Uniform")\(theta_min\,theta_max\)$,
  stating that any value within this range is equally probable.
- Informative Priors: Used when leveraging historical data or physics
  constraints. If literature states that the activation energy for
  pectin hydrolysis typically falls near $85 upright(" kJ/mol")$ with a
  known standard deviation, we use a Gaussian prior:
  $p\(E_(a\,upright("hyd"))\)tilde.op cal(N)\(mu = 85000\,sigma^2 = 5000^2\)$.
  This prevents the model from wasting computational cycles exploring
  unphysical or structurally impossible parameter regimes.

== Markov Chain Monte Carlo (MCMC) Sampling
<markov-chain-monte-carlo-mcmc-sampling>
For complex systems of differential equations, calculating the
denominator
$p\(D\)= integral p\(D divides bold(theta)\)p\(bold(theta)\)d bold(theta)$
is analytically impossible because the integration space has too many
dimensions. We bypass this bottleneck using Markov Chain Monte Carlo
(MCMC) algorithms, such as the Metropolis-Hastings or Hamiltonian Monte
Carlo (HMC) samplers. MCMC draws representative random samples directly
from the unnormalized posterior
$p\(D divides bold(theta)\)p\(bold(theta)\)$. \#\# The
Metropolis-Hastings Step-by-Step Algorithm

+ Initialize: Pick a starting parameter vector $bold(theta)^(\(0\))$
  randomly or from a preliminary optimization run.
+ Propose: For iteration $m$, propose a new candidate parameter vector
  $bold(theta)^(*)$ by drawing from a symmetric proposal distribution
  (like a random walk walk:
  $bold(theta)^(*) tilde.op cal(N)\(bold(theta)^(\(m - 1\))\,upright(bold(Sigma))_p\)$).
+ Compute the Acceptance Ratio: Calculate the probability ratio $alpha$
  of the proposed parameter set against the current parameter set:

$
  alpha = min (1 \, frac(p\(D divides bold(theta)^(*)\)p\(bold(theta)^(*)\), p\(D divides bold(theta)^(\(m - 1\))\)p\(bold(theta)^(\(m - 1\))\)))
$

Notice that the intractable term $p\(D\)$ cancels out completely. 4.
Accept or Reject: Draw a uniform random number
$u tilde.op upright("Uniform")\(0\,1\)$. \* If $u lt.eq alpha$, Accept
the proposal: set $bold(theta)^(\(m\)) = bold(theta)^(*)$. \* If
$u > alpha$, Reject the proposal: retain the old position
$bold(theta)^(\(m\)) = bold(theta)^(\(m - 1\))$. 5. Loop: Repeat steps
2--4 for hundreds of thousands of iterations. After discarding the
initial "burn-in" phase, the resulting chain of samples forms an exact
empirical map of the joint posterior distribution
$p\(bold(theta) divides D\)$.

== 8. Proxy and Measurement Calibration Models\#\# The Measurement Bottleneck
<proxy-and-measurement-calibration-models-the-measurement-bottleneck>
To update our model parameters, the inference engine requires data for
the individual states ($upright("P")_(upright("sol"))$,
$upright("P")_(upright("lowMW"))$). However, measuring
high-molecular-weight pectin directly requires High-Performance
Size-Exclusion Chromatography (HPSEC), alcohol precipitation, and
multi-angle light scattering. These analytical techniques require
extensive preparation, take hours to complete, and cost significant
labor and material. They cannot provide the rapid feedback needed for
automated, real-time optimization. \#\# The Proxy Solution To accelerate
the loop, we introduce proxy measurements: cheap, non-destructive,
instantaneous indicators that can be monitored continuously online
(e.g., Fourier-Transform Infrared Spectroscopy (FTIR), Total Soluble
Solids via Refractive Index ($""^compose upright("Brix")$), online fluid
density, or simple medium $upright("pH")$).

#mermaid(
  ```
  graph LR
    A[TRUE METRIC: High-MW Pectin Pool] -.->|Calibration| B[PROXY INDICATOR: FTIR Spectrum Absorbance]
  ```,
)


== Mathematical Calibration Mappings
<mathematical-calibration-mappings>
We establish a mathematical calibration model (such as Partial Least
Squares Regression \[PLS\] or a Gaussian Process) to infer the true
state vector $upright(bold(w))$ from the raw proxy spectra or sensor
arrays $upright(bold(z))$:

$
  upright(bold(w))_(upright("estimated")) = cal(M)_(upright("calib"))\(upright(bold(z))\)+ bold(epsilon.alt)_(upright("proxy"))
$

For our pectin project, an FTIR spectrometer measures absorbance across
a range of wavenumbers
$upright(bold(z)) =\[A_(nu_1)\,A_(nu_2)\,dots.h\,A_(nu_P)\]$. The
calibration model isolates the fingerprint region for galacturonic acid
ester linkages ($1740 upright(" cm")^(- 1)$ and
$1630 upright(" cm")^(- 1)$) to predict real-time concentrations:

$ hat(P)_(upright("sol"))\(t\)= beta_0 + sum_(j = 1)^P beta_j dot.op A_(nu_j)\(t\) $

== Compounding Uncertainty Analysis
<compounding-uncertainty-analysis>
A common mistake is treating proxy estimates as absolute truth, ignoring
the calibration error $bold(epsilon.alt)_(upright("proxy"))$. If a proxy
model has an $R^2 = 0.90$ with a root-mean-square error
$sigma_(upright("proxy"))$, this measurement uncertainty must be
propagated directly into the likelihood function of the Bayesian
parameter inference engine.

$ sigma_(upright("total"))^2 = sigma_(upright("instrument"))^2 + sigma_(upright("proxy_calibration"))^2 $

By adding the proxy calibration error to the overall noise budget, the
Bayesian framework automatically dampens overconfidence. It recognizes
that proxy data are indirect, adjusting the posterior distributions to
reflect this uncertainty until confirmed by slower, more authoritative
offline analysis.

== 9. Model Discrepancy: Handling Systematic Flaws\#\# The Reality of Structural Deficit
<model-discrepancy-handling-systematic-flaws-the-reality-of-structural-deficit>
All models are approximations. No matter how clean your data collection
or how extensive your MCMC sampling, your mechanistic ODE model will
never perfectly represent reality. If our 4-pool model assumes that
temperature impacts are perfectly Arrhenius, but a real physical reactor
exhibits localized temperature gradients or alternative unmodeled
side-reactions, the model suffers from Model Discrepancy. \#\# The
Danger of Ignoring Discrepancy If model discrepancy is ignored, the
Bayesian inference engine will try to compensate for structural flaws by
forcing parameters to take on unphysical, biased values to fit the data.
For instance, the optimizer might force the activation energy $E_a$ to
an impossible value just to minimize the residual errors caused by poor
mixing. This ruins the model's ability to extrapolate accurately to new
scale-up volumes. \#\# Kennedy-O'Hagan (KOH) Formulation To correct for
structural deficits without destroying the physical meaning of our
parameters, we deploy the Kennedy-O'Hagan framework. We model the
real-world physical system $y_(upright("real"))\(x\)$ as the sum of our
mechanistic ODE model plus an explicit, non-parametric statistical
discrepancy term:

$ y_(upright("real"))\(x\)= y_(upright("model"))\(x\,bold(theta)\)+ delta\(x\)+ epsilon.alt $

Where:

- $y_(upright("model"))\(x\,bold(theta)\)$ is the core mechanistic
  backbone.
- $delta\(x\)$ is the model discrepancy function, modeled as a flexible
  Gaussian Process (GP).
- $epsilon.alt$ is the standard experimental measurement noise.

The discrepancy term $delta\(x\)$ acts as a mathematical sponge. It
absorbs systematic, structured errors that the ODE model cannot capture,
preventing those errors from biasing your physical parameter estimates
$bold(theta)$.

#mermaid(
```
graph TD
  A["Real-World Data"] --> B["Complete System Response<br/>y_real(x)"]
  B --> C["Mechanistic ODE Model y_model(x, θ)<br/>• Captures primary physical laws<br/>• Mass balance, Arrhenius kinetics"]
  B --> D["Discrepancy GP δ(x)<br/>• Absorbs unmodeled phenomena<br/>• Mixing anomalies, side reactions"]
```
)

== Discrepancy Diagnostics: Residual Analysis
<discrepancy-diagnostics-residual-analysis>
To diagnose whether deviations are caused by random noise or structural
model flaws, we analyze the prediction residuals over time:

$ e\(t_k\)= y_(upright("observed"))\(t_k\)- y_(upright("model"))\(t_k\,hat(bold(theta))\) $

- Random Noise (No Discrepancy): The residuals $e\(t_k\)$ fluctuate
  randomly around zero with no discernable pattern. The autocorrelation
  function drops immediately to zero.
- Structural Discrepancy: The residuals exhibit clear, smooth, wave-like
  trends (e.g., the model consistently overpredicts yield at early times
  and underpredicts at late times). This structured pattern indicates
  that the model's equations are missing a key physical or chemical
  mechanism.

== 10. Uncertainty-Aware Optimization and Closed-Loop Active Learning
<uncertainty-aware-optimization-and-closed-loop-active-learning>
Once the Bayesian parameters and model discrepancies are mapped, the
system can autonomously guide its next steps using active learning. \#\#
The Optimization Objective Our engineering goal is to find the optimal
operating inputs
$upright(bold(x))^(*) =\[T\,upright("pH")\,d_p\,t_(upright("batch"))\]^T$
that maximize a specified performance metric, such as the pure
functional pectin yield while minimizing raw material costs and
degradation:

$
  upright("Objective Function ") f\(upright(bold(x))\)= P_(upright("sol"))\(upright(bold(x))\)- omega_1 dot.op P_(upright("loss"))\(upright(bold(x))\)- omega_2 dot.op upright("Cost")\(upright(bold(x))\)
$

== Machine Learning Surrogates (Gaussian Processes)
<machine-learning-surrogates-gaussian-processes>
Evaluating our complex system of ODEs and propagating full Bayesian
parameter distributions for thousands of candidate designs during
optimization is computationally expensive. To accelerate this process,
we construct a Gaussian Process (GP) Surrogate Model. The GP directly
learns the mapping from inputs $upright(bold(x))$ to the optimization
objective $f\(upright(bold(x))\)$, drawing on the historical database of
past physical runs. Crucially, a GP does not just predict a single
value; it provides a full Gaussian probability distribution for its
predictions at any point in the input space, defined by a mean
$mu\(upright(bold(x))\)$ and an explicit variance
$sigma^2\(upright(bold(x))\)$:

$
  hat(f)\(upright(bold(x))\)tilde.op cal(G P) (mu \( upright(bold(x)) \) \, k \( upright(bold(x)) \, upright(bold(x))' \))
$

== The Exploration-Exploitation Dilemma and Acquisition Functions
<the-exploration-exploitation-dilemma-and-acquisition-functions>
To choose the next experiment, the system must balance two competing
strategies:

- Exploitation: Sampling in regions where the model predicts a high mean
  outcome ($mu\(upright(bold(x))\)$ is maximized), fine-tuning known
  high-performing areas.
- Exploration: Sampling in regions where the model's uncertainty is
  massive ($sigma\(upright(bold(x))\)$ is maximized), exploring unknown
  territory to discover new opportunities or correct model blind spots.

We manage this balance using an Acquisition Function
($alpha\(upright(bold(x))\)$). The optimization algorithm evaluates this
function across thousands of candidate designs, selecting the single
point where $alpha\(upright(bold(x))\)$ is maximized as the next
experiment. \#\# 1. Upper Confidence Bound (UCB)

$ alpha_(upright("UCB"))\(upright(bold(x))\)= mu\(upright(bold(x))\)+ kappa dot.op sigma\(upright(bold(x))\) $

Where $kappa$ is a user-defined tuning parameter.

- Setting a small $kappa$ forces the system to prioritize exploitation
  (high $mu$).
- Setting a large $kappa$ forces the system to prioritize exploration
  (high $sigma$).

== 2. Expected Improvement (EI)
<expected-improvement-ei>
The Expected Improvement criterion calculates the expectation of
improving over the current best-known experimental result
$f\(upright(bold(x))^(+)\)$:

$
  alpha_(upright("EI"))\(upright(bold(x))\)= bb(E) [max \( 0 \, hat(f) \( upright(bold(x)) \) - f \( upright(bold(x))^(+) \) \)]
$

Using the properties of the Gaussian distribution, this integrates
analytically to:

$
  alpha_(upright("EI"))\(upright(bold(x))\)=\(mu\(upright(bold(x))\)- f\(upright(bold(x))^(+)\)\)Phi\(Z\)+ sigma\(upright(bold(x))\)phi.alt\(Z\)
$

Where $Phi\(dot.op\)$ and $phi.alt\(dot.op\)$ are the standard normal
cumulative distribution and probability density functions, and $Z$ is
defined as:

$ Z = frac(mu\(upright(bold(x))\)- f\(upright(bold(x))^(+)\), sigma\(upright(bold(x))\)) $

The left term scales with the predicted improvement in performance
(exploitation), while the right term scales directly with the local
model uncertainty (exploration). This elegant mathematical trade-off
prevents the system from getting stuck in local optima.

#figure(
  image("assets/acquisition_tradeoff.svg", width: 95%),
  caption: [The Exploration-Exploitation Tradeoff in Bayesian Optimization: Gaussian Process surrogate posterior with 95% credible bounds (top) and Acquisition Function landscape (bottom), demonstrating Candidate A (exploitation of high mean) vs Candidate B (exploration of high uncertainty).]
)


#mermaid(
  ```
  graph LR
    subgraph Acquisition Value alpha
      direction LR
      A[Exploit High Mean]
      B[Explore High Uncertainty]
    end
    CandidateA[Candidate A] --> A
    CandidateB[Candidate B] --> B
  ```,
)

== The Autonomous Closed Loop in Practice
<the-autonomous-closed-loop-in-practice>
When operating fully closed-loop, the self-learning framework executes
these steps autonomously:

+ Evaluate: The GP surrogate evaluates the Expected Improvement
  $alpha_(upright("EI"))\(upright(bold(x))\)$ across a vast grid of
  candidate operating conditions.
+ Select: It identifies the optimal next experiment
  $upright(bold(x))_(upright("next"))$ that maximizes the acquisition
  function.
+ Execute: The automated laboratory platform adjusts the process
  controls to matches $upright(bold(x))_(upright("next"))$, running the
  physical extraction.
+ Monitor: Online proxy sensors (such as FTIR or refractive index) track
  the reaction progress in real time.
+ Infer: The MCMC engine processes the new data footprint, updating the
  joint posterior parameter distributions $p\(bold(theta) divides D\)$
  and re-calibrating the discrepancy function $delta\(x\)$.
+ Repeat: The GP surrogate updates its predictions based on the new
  knowledge, and the loop repeats until the optimization target is
  reached or the uncertainty collapses below your target threshold.

== 11. Methodological Mapping
<methodological-mapping>
To apply this architecture to other domains, one must clearly separate the generic mathematical framework from the domain-specific parameters of the pectin application.

#align(center)[
  #table(
    columns: (1fr, 1.2fr),
    stroke: 0.5pt + luma(180),
    fill: (col, row) => if row == 0 { rgb("eef3f8") } else { none },
    align: (col, row) => (left + horizon),
    inset: (x: 10pt, y: 8pt),
    table.header(
      [*Generic Methodology Backbone*],
      [*Pectin Case Study (Domain-Specific)*]
    ),
    [ *Conservation-Invariant ODEs* ],
    [ 4-Pool Carbohydrate Mass Fractions ($upright("P")_(upright("matrix")) arrow.r upright("P")_(upright("sol")) arrow.r upright("P")_(upright("lowMW")) arrow.r upright("P")_(upright("loss"))$) ],

    [ *Logarithmic Sensitivity Matrix & SVD* ],
    [ Arrhenius frequency factor ($ln A$) and activation energy ($E_a$) identifiability ],

    [ *D-Optimality Criterion Maximization* ],
    [ Informative dynamic sample extraction times ($t_1, t_2, dots, t_N$) ],

    [ *Bayesian MCMC Posterior Sampling* ],
    [ Informative priors from polysaccharide literature ],

    [ *Proxy Calibration & Noise Budgeting* ],
    [ High-throughput FTIR / $degree upright("Brix")$ calibration for yield & molecular weight ],

    [ *Kennedy–O'Hagan Discrepancy Capture* ],
    [ Statistical GP correction for non-ideal reactor mixing & side-reactions ],

    [ *Bayesian GP Optimization (UCB / EI)* ],
    [ Active exploration vs. exploitation to maximize functional high-MW pectin yield ]
  )
]

The core mathematical architecture of this self-learning system is
universal. By replacing the pectin ODEs with thermodynamic, electrical,
or biological equations, the exact same pipeline can optimize battery
cells, fermentation batches, material synthesis pathways, or
pharmaceutical formulations. \#\# Summary Checklist for Implementation

- Verify the Code: Confirm that your ODE solver satisfies mass
  conservation invariants and strict state positivity at extreme
  parameter settings before introducing experimental data.
- Analyze Identifiability: Calculate the dimensionless logarithmic
  sensitivity matrix $tilde(upright(bold(S)))$ and perform an SVD to
  catch parameter compensation and sloppy directions early.
- Drive Experiments via OED: Use D-optimality
  ($max ln det upright(bold(F))$) to select experimental conditions that
  target your model's blind spots, rather than relying on standard
  uniform grids.
- Quantify Full Uncertainty: Use MCMC sampling to generate complete
  joint posterior distributions instead of single-point estimates, and
  propagate proxy calibration errors directly into your noise budget.
- Account for Model Flaws: Use the Kennedy-O'Hagan framework to isolate
  structural model discrepancy, preventing systematic physics errors
  from biasing your physical parameters.
- Balance Exploration and Exploitation: Couple a Gaussian Process
  surrogate with an acquisition function like Expected Improvement to
  safely and efficiently navigate complex processing spaces.

To help implement this system for your specific research goals, please
let me know:

- What physical states and control inputs define your system?
- Do you have an existing system of differential or algebraic equations,
  or are you starting from scratch?
- What measurement tools are available (e.g., direct offline analysis or
  online proxy sensors)?

I can help write the core Python code for the sensitivity equations,
configure your MCMC sampler, or build the acquisition loop.

