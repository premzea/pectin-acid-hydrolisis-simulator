# PectinDyad: Julia V1.3 Scientific Model Port & Parity Harness

This directory contains the Julia / **ModelingToolkit.jl (MTK)** scientific modeling track for passion-fruit pectin acid hydrolysis.

It operates in parallel with the Python baseline (`src/pectin`), adhering to a strict **6-Gate Progression** to guarantee mathematical and data parity before introducing digital-twin, surrogate, or UDE infrastructure.

---

## 1. The 6-Gate Implementation Progression

| Gate | Deliverable | Hard Pass Condition | Status |
| :---: | :--- | :--- | :---: |
| **0** | **Shared Contract** | `docs/specifications/v1_3_contract.json` versioned specification. | **Passed** |
| **1** | **Julia V1.3 Reaction Model** | Standalone MTK / ODE system in Julia; mass conservation $\sum P_i = P_0$ holds within $10^{-8}$. | **Completed** |
| **2** | **Python ↔ Julia Parity** | **HARD GATE**: Forward-state relative $L_\infty < 10^{-4}$, $DE < 10^{-3}$, $M_w < 0.1\%$. | **Harness ready** |
| **3** | **AD / Sensitivity Validation** | ForwardDiff sensitivity discrepancy $< 10^{-3}$; solve-time benchmark vs. Scipy LSODA. | **Pending Gate 2** |
| **4** | **Reactor Coupling & Forcing** | Ingest continuous $T(t), \text{pH}(t)$ dynamic splines & load cell mass depletion. | **Pending Gate 3** |
| **5** | **Calibration & OED Re-Targeting** | Recompute $F = S^T \Sigma_{\text{proxy}}^{-1} S$ with empirical Phase 1 proxy covariance. | **Pending Gate 4** |
| **6** | **UDE Discrepancy & FMU** | Deploy UDE only if physical Batch C data warrants it; export standalone FMU. | **Deferred** |

---

## 2. Directory Layout

```
dyad/
├── Project.toml               # Julia package dependencies
├── install_julia.sh           # Helper script to install Julia & Juliaup
├── src/
│   ├── PectinDyad.jl          # Top-level module
│   ├── kinetics.jl            # Reference-state Arrhenius kinetics
│   ├── simulator.jl           # High-performance simulation runner
│   ├── components/
│   │   ├── reaction_network.jl# MTK 4-pool mass & property moment components
│   │   └── sensors.jl         # Soft-sensor observation model & FIM computation
│   └── surrogates/
│       └── ude_discrepancy.jl # SciML Universal Differential Equation (UDE) model
├── scripts/
│   └── export_python_reference.py # Generates Python reference fixtures
└── tests/
    ├── fixtures/
    │   └── python_reference_trajectories.json
    ├── test_parity.jl         # Automated Python-vs-Julia parity verification
    └── runtests.jl            # Test entry point
```

---

## 3. Quickstart & Testing

### A. Install Julia in WSL
If Julia is not yet installed on your system:
```bash
bash dyad/install_julia.sh
```

### B. Run the Cross-Language Parity Test
To verify that the Dyad ODE solver reproduces the Python V1.3 outputs down to floating-point tolerance:
```bash
julia --project=dyad -e 'using Pkg; Pkg.instantiate(); Pkg.test()'
```

### C. Regenerating Reference Data
If you modify the Python V1.3 kinetics in `src/pectin/`, update the test fixtures by running:
```bash
PYTHONPATH=src python3 dyad/scripts/export_python_reference.py
```

---

## 4. Modeling in Dyad Studio

To explore and edit this system visually in **Dyad Studio**:
1. Install the **Dyad Studio** (JuliaSim) extension in VS Code.
2. Open the `dyad/` folder in VS Code.
3. The component definitions in `src/components/reaction_network.jl` can be visualized as block diagrams, connected to thermal fluid jacket components, and calibrated directly against reactor telemetry data.
