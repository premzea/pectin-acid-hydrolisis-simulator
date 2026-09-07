# Domain 3: Software Engineering & Cyber-Physical System Architecture

**Document Version**: 2.0  
**Parent Document**: [`MASTER_DUAL_TRACK_SPECIFICATION.md`](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/MASTER_DUAL_TRACK_SPECIFICATION.md)  
**Target Audience**: Software Engineers, Full-Stack Developers, Embedded/IoT Engineers, UI/UX Designers

---

## 1. Executive Scope & Cyber-Physical Overview

The Bioreactor Studio ecosystem provides the software, embedded firmware, communication middleware, and user interface infrastructure connecting wet-lab hardware (Track A stirred reactor and Track B UAE bath + IO Rodeo colorimeter) with the compiled digital twin simulation engines.

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             REACT 19 FRONTEND (SPA)                              │
│  - Run Configuration (Track A / Track B Switcher)                                │
│  - Real-Time Telemetry Trajectories (Recharts)                                   │
│  - Multi-Channel Colorimeter Soft-Sensor Widget (8-Channel Profile & Gauge)      │
│  - Campaign Active Learning & Techno-Economic Analysis Dashboard                 │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │ WebSocket / REST HTTP
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│                            FASTAPI BACKEND (Python 3.12)                         │
│  - Connection Manager (WebSocket Clients <-> Edge Relays)                        │
│  - FMU Runner (FMI 2.0 Co-Simulation C-Binary via FMPy)                         │
│  - Soft-Sensor Chemometric Engine (Vector Regression & Provenance)               │
│  - SQLite Multi-Tier Database (pectin_extractor.db / pectin_extractor_sim.db)    │
└──────────────────┬─────────────────────────────────────────────┬─────────────────┘
                   │ WebSocket                                   │ Serial / WiFi
                   ▼                                             ▼
┌──────────────────────────────────────┐     ┌─────────────────────────────────────┐
│    HIL SIMULATOR (mock_arduino.py)   │     │    ARDUINO UNO Q BRIDGE RELAY       │
│  - Bang-Bang Thermal Reactor Model   │     │  - Physical RTD & pH Sensor Polling │
│  - FMU Chemistry Stepper (RK4)       │     │  - Ultrasonic Bath State Relay      │
│  - Simulated 8-Channel Telemetry     │     │  - IO Rodeo Serial Interfacing      │
└──────────────────────────────────────┘     └─────────────────────────────────────┘
```

---

## 2. FMU 2.0 Co-Simulation Digital Twin Engine

To eliminate high-latency runtime language dependencies (e.g. Julia/Python JIT overheads), the high-fidelity mechanistic model is compiled into a standalone **FMI 2.0 Co-Simulation C-Shared Library** archive:
📁 `models/PectinHydrolysisTwin.fmu`

### A. Python FMI Interface (`fmu_runner.py`)
Execution is handled via `fmpy`:
1. **Batch Mode (`simulate_fmu_batch`)**:
   Executes non-interactive parameter sensitivity sweeps, DSD screening, and surrogate data generation.
2. **Interactive Stepper Mode (`FMUCoSimulationSession`)**:
   Enables real-time Hardware-in-the-Loop (HIL) stepping:
   * Instantiates the slave binary (`fmu.instantiate()`).
   * Pushes active physical setpoints (`setReal(VR_T_REACTOR, temp_c)`).
   * Steps forward synchronously by $\Delta t$ seconds (`fmu.doStep(current_time, dt)`).
   * Reads back state vector $[P_{\text{matrix}}, P_{\text{sol}}, P_{\text{lowMW}}, P_{\text{loss}}, DE_{\text{sol}}, M_{w,\text{sol}}]$.

---

## 3. Database Schema & First-Class Provenance Architecture

Persistence uses SQLite with WAL (Write-Ahead Logging) enabled. Real runs log to `pectin_extractor.db`; synthetic HIL simulations log to `pectin_extractor_sim.db`.

```text
┌──────────────────────┐         ┌───────────────────────┐
│        runs          │1       *│       readings        │
├──────────────────────┤─────────┼───────────────────────┤
│ run_id (PK)          │         │ id (PK)               │
│ track_type           │         │ run_id (FK)           │
│ device_id            │         │ timestamp_utc         │
│ status               │         │ reactor_T_C           │
│ config_json          │         │ pH                    │
│ start_time           │         │ p_matrix, p_sol, ...  │
└──────────┬───────────┘         └───────────────────────┘
           │1
           │1
┌──────────┴────────────────────────────────────────────────┐
│                           uae_runs                        │
├───────────────────────────────────────────────────────────┤
│ run_id (PK, FK -> runs)                                   │
│ calibration_id_gala (FK -> colorimeter_calibrations)      │
│ calibration_id_pectin (FK -> colorimeter_calibrations)    │
│ fresh_rind_mass_g, water_mass_g, fresh_moisture_pct       │
│ particle_size_um, initial_ph, extraction_temp_c           │
│ bath_temp_c, us_frequency_khz, us_nominal_power_w         │
│ acoustic_coupling_eff, extraction_time_min                │
│ filtrate_total_mass_g, analytical_aliquot_mass_g          │
│ precipitation_stream_mass_g, dilution_factor              │
│ raw_spectra_json (8-channel absorbances)                  │
│ gala_conc_mg_l, pectin_equiv_conc_mg_l                    │
│ precipitated_dry_mass_g, gravimetric_yield_pct            │
│ gala_composition_indicator                                │
└──────────────────────────┬────────────────────────────────┘
                           │*
                           │1
┌──────────────────────────┴────────────────────────────────┐
│                  colorimeter_calibrations                 │
├───────────────────────────────────────────────────────────┤
│ calibration_id (PK)                                       │
│ analyte ("GalA" | "pectin_equivalent")                    │
│ assay_chemistry ("carbazole_sulfuric" | "copper_chelate") │
│ standard_identity ("D-GalA monohydrate 98%")              │
│ standard_concentrations_json                              │
│ replicate_absorbances_json                                │
│ wavelengths_used_json ([515, 555, 680])                   │
│ model_type ("multichannel_linear_regression")             │
│ coefficients_json (weights [a, b, c], intercept d)        │
│ r_squared, rmsep                                          │
│ linear_range_min_mg_l, linear_range_max_mg_l              │
│ reagent_batch_id, instrument_id ("IO_Rodeo_01")           │
│ temperature_c, created_at                                 │
└───────────────────────────────────────────────────────────┘
```

### Table 1: `colorimeter_calibrations` (Provenance Object)
Guarantees that every analytical result can be traced back to its specific standard series, reagent batch, and instrument channel calibration:
```sql
CREATE TABLE IF NOT EXISTS colorimeter_calibrations (
    calibration_id TEXT PRIMARY KEY,
    analyte TEXT NOT NULL,
    assay_chemistry TEXT NOT NULL,
    standard_identity TEXT NOT NULL,
    standard_concentrations_json TEXT NOT NULL,
    replicate_absorbances_json TEXT NOT NULL,
    wavelengths_used_json TEXT NOT NULL,
    model_type TEXT NOT NULL,
    coefficients_json TEXT NOT NULL,
    r_squared REAL NOT NULL,
    rmsep REAL,
    linear_range_min_mg_l REAL NOT NULL,
    linear_range_max_mg_l REAL NOT NULL,
    reagent_batch_id TEXT,
    instrument_id TEXT NOT NULL,
    temperature_c REAL,
    created_at TEXT NOT NULL
);
```

### Table 2: `uae_runs` (Arduino Q Experiment Logger)
Records the full physical process, mass balance, spectrophotometry, and recovery results for Track B:
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

## 4. Real-Time Communication Protocols & Bridge Relay

### A. WebSocket Connection Architecture (`main.py`)
* `/ws/arduino/{device_id}`: Dedicated full-duplex tunnel for edge controllers (physical Arduino Uno Q or mock simulator).
* `/ws/frontend`: Broadcast channel pushing 1 Hz real-time telemetry frames to all connected React clients.

### B. Live Telemetry Frame Schema (JSON)
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
  "pH": 2.15,
  "ultrasound_active": true,
  "ultrasound_power_w": 180.0,
  "true": {
    "p_matrix": 0.124,
    "p_sol": 0.158,
    "p_low_mw": 0.012,
    "p_loss": 0.003
  }
}
```

### C. Arduino Uno Q Hardware Bridge Relay (`uno_q_bridge_relay.py`)
Connects the physical Arduino Uno Q development board to the backend over USB Serial or WiFi:
* Polls ADC pins for PT100 amplifier (MAX31865) and industrial pH electrode (E-201-C).
* Commands digital solid-state relays (SSRs) for the heating elements and ultrasonic bath power.
* Interfaces with the IO Rodeo Multichannel Colorimeter over USB UART to trigger at-line sample acquisition.

---

## 5. REST API Specifications (`main.py`)

### A. Colorimeter Calibration Management
* **`POST /api/colorimeter/calibrations`**:
  Fit multi-channel regression from calibration standards and register provenance object:
  ```json
  {
    "analyte": "GalA",
    "assay_chemistry": "carbazole_sulfuric",
    "standard_identity": "D-(+)-Galacturonic acid monohydrate >=97%",
    "standards": [
      {"conc_mg_l": 0.0, "absorbances": {"515": 0.041, "555": 0.038, "680": 0.012}},
      {"conc_mg_l": 50.0, "absorbances": {"515": 0.215, "555": 0.198, "680": 0.014}},
      {"conc_mg_l": 100.0, "absorbances": {"515": 0.421, "555": 0.385, "680": 0.015}},
      {"conc_mg_l": 200.0, "absorbances": {"515": 0.812, "555": 0.745, "680": 0.016}},
      {"conc_mg_l": 400.0, "absorbances": {"515": 1.580, "555": 1.450, "680": 0.018}}
    ],
    "linear_range": [10.0, 350.0],
    "instrument_id": "IO_Rodeo_01",
    "reagent_batch_id": "CARB-2026-09-A"
  }
  ```
  *Response*: `{"status": "success", "calibration_id": "CAL-GALA-2026-09-01", "r_squared": 0.9987, "coefficients": {"515": 0.00392, "555": -0.00045, "680": -0.0021, "intercept": -0.082}}`.

* **`GET /api/colorimeter/calibrations/active`**:
  Retrieves active calibration objects for GalA and Pectin-Equivalent assays.

### B. At-Line Measurement & Soft Sensing
* **`POST /api/colorimeter/measure`**:
  ```json
  {
    "raw_spectra": {
      "415": 0.124, "445": 0.156, "480": 0.210,
      "515": 0.642, "555": 0.589, "590": 0.320,
      "630": 0.045, "680": 0.022
    },
    "dilution_factor": 50.0,
    "calibration_id_gala": "CAL-GALA-2026-09-01",
    "calibration_id_pectin": "CAL-PECTIN-2026-09-01"
  }
  ```
  *Response*:
  ```json
  {
    "gala_measured_mg_l": 158.4,
    "gala_sample_mg_l": 7920.0,
    "pectin_equiv_measured_mg_l": 182.1,
    "pectin_equiv_sample_mg_l": 9105.0,
    "range_status": "VALID",
    "recommended_df": 50.0,
    "turbidity_index_680": 0.022
  }
  ```

### C. UAE Process Simulation & Logging
* **`POST /api/uae/simulate`**:
  Forward simulation of Track B given fresh rind mass, water mass, power, frequency, and time.
* **`POST /api/uae/runs/record`**:
  Commits a completed Arduino Q experiment record into `uae_runs`.

---

## 6. Bioreactor Studio UI Architecture (`src/frontend`)

The Single Page Application is built using **React 19**, **Vite**, **Tailwind CSS**, and **Recharts**:

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                       App.jsx                                          │
│ ┌────────────────────────────────────────────────────────────────────────────────────┐ │
│ │                                    Header.jsx                                      │ │
│ └────────────────────────────────────────────────────────────────────────────────────┘ │
│                                          │                                             │
│       ┌─────────────────┬────────────────┴────────────────┬─────────────────┐          │
│       ▼                 ▼                                 ▼                 ▼          │
│ RunConfigScreen   ActiveRunScreen               EconomicsScreen   SimulationCampaign   │
│ (Track A/B Form)  - Live Temperature & pH       (Techno-Economic  (Active Learning     │
│                   - Trajectory Chart             Downstream TEA)   Bayesian Tuning)    │
│                   - ColorimeterSoftSensorWidget                                        │
│                     * 8-Channel Bar Chart                                              │
│                     * Concentration Readouts                                           │
│                     * GalA Purity Gauge                                                │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Component Breakdown
1. **`RunConfigScreen.jsx`**:
   Includes a tabbed workflow selector:
   * *Track A*: Jacket temperature setpoint, stirring RPM, standardized particle size ($150, 300, 600\,\mu\text{m}$), and quench interval schedule.
   * *Track B*: Fresh peel mass, water mass, food-processor comminution size, 40-kHz nominal power slider ($50\text{--}300\text{ W}$), bath temperature, and analytical dilution factor.
2. **`ColorimeterSoftSensorWidget.jsx`**:
   * Visualizes 8 discrete spectral bars with colored wavelength bands.
   * Displays primary GalA concentration ($C_{\text{GalA}}$) with calibration tag.
   * Displays secondary Pectin-equivalent concentration ($C_{\text{pectin-equiv}}$).
   * Renders the **GalA Composition / Purity Indicator** radial gauge:
     $$\text{Purity Ratio} = \frac{\text{GalA Mass (Chemical)}}{\text{Dry Precipitate Mass (Gravimetric)}}$$
     Color-coded: Green ($> 75\%$, high purity), Yellow ($55\text{--}75\%$, commercial grade), Red ($< 55\%$, high co-extractives).
