# Domain 3: Software Engineering & Cyber-Physical System Architecture

**Document Version**: 2.1 (Incorporating Systems & Chemometrics Peer Review)  
**Parent Document**: [`MASTER_DUAL_TRACK_SPECIFICATION.md`](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/MASTER_DUAL_TRACK_SPECIFICATION.md)  
**Target Audience**: Software Engineers, Full-Stack Developers, Embedded/IoT Engineers, UI/UX Designers

---

## 1. Executive Scope & Cyber-Physical Overview

The Bioreactor Studio ecosystem provides the software, embedded firmware, communication middleware, and user interface infrastructure connecting wet-lab hardware (Track A stirred reactor with reflux condenser and Track B UAE bath + IO Rodeo colorimeter) with the compiled digital twin simulation engines.

Incorporating rigorous peer-review critiques:
1. **Calibration Provenance Symmetry**: Establishes unified first-class provenance models for **all** secondary proxies across both tracks (Track B IO Rodeo colorimeter, Track A FTIR PLS models, and capillary viscometer Mark-Houwink models).
2. **Techno-Economic Symmetry**: Integrates extract streams from both Track A and Track B into all four industrial downstream separation flowsheets.
3. **Dynamic Vessel Volume Scaling**: Real-time tracking of cumulative aliquot withdrawals with dynamic reaction volume updates.

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             REACT 19 FRONTEND (SPA)                              │
│  - Run Configuration (Track A Reflux/Dosing vs. Track B UAE/Colorimeter)         │
│  - Real-Time Multi-Trace Telemetry (Slurry T, Bath T, Reflux T, pH, Power)       │
│  - Multi-Channel Colorimeter Soft-Sensor Widget (Sample-Blank Vector & Gauge)    │
│  - Symmetric Techno-Economic Downstream Flowsheet Evaluator (Tracks A & B)       │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │ WebSocket / REST HTTP
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                            FASTAPI BACKEND (Python 3.12)                         │
│  - Connection Manager (WebSocket Clients <-> Edge Relays)                        │
│  - FMU Runner (FMI 2.0 Co-Simulation C-Binary via FMPy)                         │
│  - Unified Chemometric Engine (Colorimeter Vectors, FTIR PLS, Viscometer)        │
│  - SQLite Multi-Tier Database (pectin_extractor.db / pectin_extractor_sim.db)    │
└──────────────────┬─────────────────────────────────────────────┬─────────────────┘
                   │ WebSocket                                   │ Serial / WiFi
                   ▼                                             ▼
┌──────────────────────────────────────┐     ┌─────────────────────────────────────┐
│    HIL SIMULATOR (mock_arduino.py)   │     │    ARDUINO UNO Q BRIDGE RELAY       │
│  - Dynamic Reactor Volume Balance    │     │  - Physical RTD & pH Sensor Polling │
│  - FMU Chemistry Stepper (RK4)       │     │  - Reflux Coolant & Dosing Relays   │
│  - Simulated 8-Channel Telemetry     │     │  - IO Rodeo Serial Interfacing      │
└──────────────────────────────────────┘     └─────────────────────────────────────┘
```

---

## 2. FMU 2.0 Co-Simulation Digital Twin Engine

To eliminate high-latency runtime language dependencies, the high-fidelity mechanistic model is compiled into a standalone **FMI 2.0 Co-Simulation C-Shared Library** archive:
📁 `models/PectinHydrolysisTwin.fmu`

### A. Python FMI Interface (`fmu_runner.py`)
Execution is handled via `fmpy`:
1. **Batch Mode (`simulate_fmu_batch`)**:
   Executes non-interactive parameter sensitivity sweeps, DSD screening, and surrogate data generation.
2. **Interactive Stepper Mode (`FMUCoSimulationSession`)**:
   Enables real-time Hardware-in-the-Loop (HIL) stepping:
   * Instantiates the slave binary (`fmu.instantiate()`).
   * Pushes active physical setpoints (`setReal(VR_T_REACTOR, temp_c)`).
   * Dynamically tracks volume withdrawals (`setReal(VR_SLURRY_VOLUME, remaining_v)`).
   * Steps forward synchronously by $\Delta t$ seconds (`fmu.doStep(current_time, dt)`).
   * Reads back state vector $[P_{\text{matrix}}, P_{\text{sol}}, P_{\text{lowMW}}, P_{\text{loss}}, DE_{\text{sol}}, M_{w,\text{sol}}]$.

---

## 3. Database Schema & Unified Provenance Architecture

```text
┌──────────────────────┐         ┌───────────────────────┐
│        runs          │1       *│       readings        │
├──────────────────────┤─────────┼───────────────────────┤
│ run_id (PK)          │         │ id (PK)               │
│ track_type           │         │ run_id (FK)           │
│ device_id            │         │ timestamp_utc         │
│ status               │         │ reactor_T_C, bath_T_C │
│ config_json          │         │ reflux_T_C, pH        │
│ start_time           │         │ p_matrix, p_sol, ...  │
└──────────┬───────────┘         └───────────────────────┘
           │1
           ├───────────────────────────────┬───────────────────────────────┐
           │1                              │1                              │1
           ▼                               ▼                               ▼
┌────────────────────────────┐ ┌───────────────────────────┐ ┌───────────────────────────┐
│          uae_runs          │ │     ftir_calibrations     │ │  viscometer_calibrations  │
├────────────────────────────┤ ├───────────────────────────┤ ├───────────────────────────┤
│ run_id (PK, FK)            │ │ calibration_id (PK)       │ │ calibration_id (PK)       │
│ calibration_id_gala (FK)   │ │ analyte ("DE" | "GalA")   │ │ analyte ("Mw")            │
│ calibration_id_pectin (FK) │ │ model_type ("PLS" | "PCR")│ │ model_type ("Mark_Houwink")│
│ fresh_rind_mass_g          │ │ n_components              │ │ K_constant, a_exponent    │
│ water_mass_g               │ │ wavenumber_range_json     │ │ solvent, temperature_c    │
│ fresh_moisture_pct         │ │ coefficients_json         │ │ r_squared, rmsep          │
│ particle_size_um, init_ph  │ │ r_squared, rmsep          │ │ created_at                │
│ us_nominal_power_w         │ │ created_at                │ └───────────────────────────┘
│ acoustic_coupling_eff      │ └───────────────────────────┘
│ sample_blank_spectra_json  │
│ net_spectra_json           │
│ gala_conc_mg_l             │
│ pectin_equiv_conc_mg_l     │
│ gala_composition_indicator │
└──────────┬─────────────────┘
           │*
           │1
           ▼
┌────────────────────────────┐
│  colorimeter_calibrations  │
├────────────────────────────┤
│ calibration_id (PK)        │
│ analyte, assay_chemistry   │
│ standard_identity          │
│ standard_concentrations    │
│ sample_blank_subtraction   │
│ coefficients_json          │
│ r_squared, rmsep           │
│ linear_range_min/max_mg_l  │
│ reagent_batch_id           │
│ instrument_id, created_at  │
└────────────────────────────┘
```

### Table 1: `colorimeter_calibrations` (Track B Provenance)
```sql
CREATE TABLE IF NOT EXISTS colorimeter_calibrations (
    calibration_id TEXT PRIMARY KEY,
    analyte TEXT NOT NULL,
    assay_chemistry TEXT NOT NULL,
    standard_identity TEXT NOT NULL,
    standard_concentrations_json TEXT NOT NULL,
    replicate_absorbances_json TEXT NOT NULL,
    wavelengths_used_json TEXT NOT NULL,
    sample_blank_subtraction INTEGER DEFAULT 1,
    model_type TEXT NOT NULL,
    coefficients_json TEXT NOT NULL,
    r_squared REAL NOT NULL,
    rmsep REAL,
    linear_range_min_mg_l REAL NOT NULL,
    linear_range_max_mg_l REAL NOT NULL,
    matrix_spike_recovery_pct REAL,
    reagent_batch_id TEXT,
    instrument_id TEXT NOT NULL,
    temperature_c REAL,
    created_at TEXT NOT NULL
);
```

### Table 2: `ftir_calibrations` (Track A Secondary Proxy Provenance)
```sql
CREATE TABLE IF NOT EXISTS ftir_calibrations (
    calibration_id TEXT PRIMARY KEY,
    analyte TEXT NOT NULL,
    model_type TEXT NOT NULL, -- 'PLS' or 'PCR'
    n_components INTEGER NOT NULL,
    wavenumber_range_json TEXT NOT NULL,
    coefficients_json TEXT NOT NULL,
    r_squared REAL NOT NULL,
    rmsep REAL NOT NULL,
    spectrometer_model TEXT NOT NULL,
    created_at TEXT NOT NULL
);
```

### Table 3: `viscometer_calibrations` (Track A Secondary Proxy Provenance)
```sql
CREATE TABLE IF NOT EXISTS viscometer_calibrations (
    calibration_id TEXT PRIMARY KEY,
    analyte TEXT NOT NULL,
    model_type TEXT NOT NULL, -- 'Mark_Houwink'
    k_constant REAL NOT NULL,
    a_exponent REAL NOT NULL,
    solvent TEXT NOT NULL,
    temperature_c REAL NOT NULL,
    rmsep REAL,
    r_squared REAL,
    created_at TEXT NOT NULL
);
```

### Table 4: `uae_runs` (Arduino Q Experiment Logger)
```sql
CREATE TABLE IF NOT EXISTS uae_runs (
    run_id TEXT PRIMARY KEY,
    calibration_id_gala TEXT,
    calibration_id_pectin TEXT,
    fresh_rind_mass_g REAL NOT NULL,
    water_mass_g REAL NOT NULL,
    fresh_moisture_pct REAL NOT NULL,
    particle_size_um REAL NOT NULL,
    initial_ph REAL NOT NULL,
    extraction_temp_c REAL NOT NULL,
    bath_temp_c REAL NOT NULL,
    us_frequency_khz REAL DEFAULT 40.0,
    us_nominal_power_w REAL NOT NULL,
    acoustic_coupling_eff REAL DEFAULT 0.25,
    extraction_time_min REAL NOT NULL,
    filtrate_total_mass_g REAL NOT NULL,
    analytical_aliquot_mass_g REAL NOT NULL,
    precipitation_stream_mass_g REAL NOT NULL,
    dilution_factor REAL NOT NULL,
    raw_spectra_json TEXT NOT NULL,
    sample_blank_spectra_json TEXT NOT NULL,
    net_spectra_json TEXT NOT NULL,
    gala_conc_mg_l REAL NOT NULL,
    pectin_equiv_conc_mg_l REAL NOT NULL,
    precipitated_dry_mass_g REAL NOT NULL,
    gravimetric_yield_pct REAL NOT NULL,
    gala_composition_indicator REAL NOT NULL,
    notes TEXT,
    FOREIGN KEY(run_id) REFERENCES runs(run_id),
    FOREIGN KEY(calibration_id_gala) REFERENCES colorimeter_calibrations(calibration_id),
    FOREIGN KEY(calibration_id_pectin) REFERENCES colorimeter_calibrations(calibration_id)
);
```

---

## 4. Real-Time Middleware & Edge Integration

### A. Live Telemetry Frame Schema (JSON)
```json
{
  "kind": "telemetry",
  "device_id": "UNO-Q-01",
  "run_id": "RUN-2026-09-B001",
  "timestamp_arduino": 1845000,
  "sim_time_min": 30.75,
  "track_type": "uae_colorimetric",
  "reactor_T_C": 58.4,
  "bath_T_C": 60.1,
  "reflux_T_C": 16.2,
  "pH": 2.15,
  "ultrasound_active": true,
  "ultrasound_power_w": 180.0,
  "active_reactor_volume_ml": 1164.0,
  "true": {
    "p_matrix": 0.124,
    "p_sol": 0.158,
    "p_low_mw": 0.012,
    "p_loss": 0.003
  }
}
```

---

## 5. REST API Architecture (`main.py`)

### A. Colorimeter Calibration Management
* **`POST /api/colorimeter/calibrations`**:
  Fit multi-channel regression from calibration standards with sample-blank subtraction:
  * Ingests standards and sample-blank spectra.
  * Fits $[A_{\text{net}}(515), A_{\text{net}}(555), A_{\text{net}}(680)] \to C_{\text{GalA}}$.
  * Computes $R^2$, RMSEP, and checks matrix spike recovery.
  * Persists object to `colorimeter_calibrations`.

### B. At-Line Measurement & Soft Sensing
* **`POST /api/colorimeter/measure`**:
  * Ingests developed tube and sample-blank tube spectra.
  * Subtracts baseline and computes net absorbance vector $\mathbf{A}_{\text{net}}$.
  * Evaluates linear range status and advises dilution factor adjustments ($DF \times N$).

### C. Symmetric Techno-Economic Downstream Evaluation
* **`POST /api/economics/evaluate`**:
  Accepts extract liquor from **either Track A or Track B** and evaluates downstream separation:
  ```json
  {
    "track_source": "Track_B_UAE",
    "liters_extract": 20000.0,
    "kg_pectin_extracted": 120.0,
    "gala_composition_indicator": 0.78,
    "flowsheet": "hybrid"
  }
  ```
  *Evaluates all 4 standard trains*:
  1. `hybrid`: MF + UF/DF 10× volume reduction + 1:1 ethanol precipitation + drying.
  2. `direct_drying`: MF + Diafiltration + direct spray drying (zero solvent).
  3. `conventional`: MF + 80% evaporation + 2:1 ethanol precipitation + drying.
  4. `liquid_concentrate`: MF + UF to 6–8% Brix + formulation.

---

## 6. Bioreactor Studio Frontend SPA Architecture (`src/frontend`)

1. **`RunConfigScreen.jsx`**:
   * *Track A Panel*: Target jacket $T$, mechanical stirring RPM, ASTM sieve fraction ($150, 300, 600\,\mu\text{m}$), reflux condenser active status toggle, and aliquot volume constraint validator ($< 5\%$).
   * *Track B Panel*: Fresh peel mass, water mass, food-processor comminution size, 40-kHz nominal power slider ($0\text{--}300\text{ W}$), and paired thermal control flag ($P_{\text{elec}} = 0$).
2. **`ColorimeterSoftSensorWidget.jsx`**:
   * Renders dual spectral traces: Developed Tube vs. Sample-Blank Tube.
   * Visualizes Net Absorbance Vector $\mathbf{A}_{\text{net}}$ across all 8 IO Rodeo channels.
   * Displays GalA Concentration ($C_{\text{GalA}}$), Pectin-Equivalent Concentration ($C_{\text{pectin-equiv}}$), and Matrix Spike Recovery indicator.
   * Radial **GalA-Based Composition Indicator** gauge with threshold badges.
3. **`EconomicsScreen.jsx`**:
   * Side-by-side comparison of CAPEX, OPEX, and net margins for Track A vs. Track B across all four downstream recovery routes.
