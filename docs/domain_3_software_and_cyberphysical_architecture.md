# Domain 3: Software Engineering & Cyber-Physical System Architecture

**Document Version**: 3.2 (Shared Comminution Provenance with Diverging Pretreatment Data Models)  
**Parent Document**: [`MASTER_DUAL_TRACK_SPECIFICATION.md`](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/MASTER_DUAL_TRACK_SPECIFICATION.md)  
**Target Audience**: Software Engineers, Full-Stack Developers, Embedded/IoT Engineers, UI/UX Designers

---

## 1. Executive Scope & Cyber-Physical Overview

The Bioreactor Studio software suite orchestrates experimental data logging, physical sensor ingestion, and digital twin simulation across both operational tracks using a **shared biological lot provenance data model** with diverging downstream physical state representations:

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             REACT 19 FRONTEND (SPA)                              │
│  - Run Configuration (Shared Comminution Lot -> Track A Dried vs Track B Fresh)   │
│  - Real-Time Multi-Trace Telemetry (Slurry T, Bath T, Reflux T, pH, Power)       │
│  - Multi-Channel Colorimeter Soft-Sensor Widget (Sample-Blank Vector & Gauge)    │
│  - Symmetric Downstream Techno-Economic Flowsheet Evaluator                      │
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

## 2. Provenance & Feedstock Data Schema (`runs` & `uae_runs`)

Both tracks reference a shared comminution lot ID (`provenance_lot_id`), while tracking their specific physical states (Track A: dried moisture & sieved size; Track B: fresh moisture & measured covariate size):

```sql
ALTER TABLE runs ADD COLUMN provenance_lot_id TEXT; -- e.g. 'LOT-20260907-A'
ALTER TABLE runs ADD COLUMN fresh_rind_mass_g REAL;
ALTER TABLE runs ADD COLUMN batch_moisture_fraction REAL;
ALTER TABLE runs ADD COLUMN dried_moisture_fraction REAL; -- Track A dried moisture (~0.06-0.08)
ALTER TABLE runs ADD COLUMN sieved_d50_um REAL;          -- Track A discrete sieved cuts (150, 300, 600)
ALTER TABLE runs ADD COLUMN measured_d50_um REAL;        -- Track B measured covariate
ALTER TABLE runs ADD COLUMN track_type TEXT;             -- 'track_a_thermal' or 'track_b_uae'
```

### Table 1: `uae_runs` (Track B Logger)
```sql
CREATE TABLE IF NOT EXISTS uae_runs (
    run_id TEXT PRIMARY KEY,
    provenance_lot_id TEXT NOT NULL,
    calibration_id_gala TEXT,
    calibration_id_pectin TEXT,
    fresh_wet_mass_g REAL NOT NULL,
    moisture_fraction REAL NOT NULL,
    d50_measured_um REAL NOT NULL,       -- Measured covariate (not controlled)
    c_citric REAL NOT NULL,
    pH REAL NOT NULL,
    temperature_c REAL NOT NULL,
    p_acoustic_w REAL NOT NULL,
    f_us_khz REAL DEFAULT 40.0,
    v_slurry_l REAL NOT NULL,
    is_control INTEGER DEFAULT 0,        -- 1 for P_elec = 0 matched thermal controls
    start_time TEXT NOT NULL,
    end_time TEXT,
    yield_apsp REAL,
    mw_product REAL,
    de_product REAL,
    gala_purity REAL,
    config_json TEXT,
    FOREIGN KEY(run_id) REFERENCES runs(run_id)
);
```

### Table 2: Unified Provenance Tables
1. `colorimeter_calibrations`: Ingests multi-wavelength standard series, fits $[A_{\text{net}}(515), A_{\text{net}}(555), A_{\text{net}}(680)] \to C_{\text{GalA}}$, checks spike recovery, registers linear limits $[C_{\min}, C_{\max}]$.
2. `colorimeter_measurements`: Time-series logging of developed, copper, and sample-blank spectra, with calculated net absorbances and dilution advisories.
3. `ftir_calibrations`: Secondary offline FTIR / DRIFTS models for ester and carboxyl functional groups.
4. `viscometer_calibrations`: Mark-Houwink constants ($K, a$) for capillary viscometer molecular weight estimation.

---

## 3. Real-Time Telemetry Frame Schema (JSON)

```json
{
  "kind": "telemetry",
  "device_id": "UNO-Q-01",
  "run_id": "RUN-2026-09-07-01",
  "provenance_lot_id": "LOT-20260907-A",
  "timestamp_arduino": 1845000,
  "sim_time_min": 30.75,
  "track_type": "track_b_uae",
  "is_thermal_control": false,
  "reactor_T_C": 58.4,
  "bath_T_C": 60.1,
  "reflux_T_C": 16.2,
  "pH": 2.15,
  "ultrasound_active": true,
  "ultrasound_power_w": 80.0,
  "measured_d50_um": 920.0,
  "active_reactor_volume_ml": 580.0,
  "true": {
    "p_matrix": 0.124,
    "p_sol": 0.158,
    "p_low_mw": 0.012,
    "p_loss": 0.003
  }
}
```

---

## 4. REST API Specifications (`main.py`)

1. **`POST /api/colorimeter/calibrations`**: Registers an 8-channel calibration object with sample-blank subtraction.
2. **`POST /api/colorimeter/measure`**: Ingests developed and blank spectra, computes net absorbance vector, validates dynamic range ($0.05\text{--}1.50\text{ AU}$), and returns $C_{\text{GalA}}$, $C_{\text{pectin-equiv}}$, and dilution advisory.
3. **`POST /api/uae/simulate`**: Forward simulation of Track B given fresh rind mass, measured moisture $X_{w,0}$, delivered acoustic power $P_{\text{acoustic}}$, volume, and duration.
4. **`POST /api/uae/runs/record`**: Commits a completed Track B run record into `uae_runs` with paired control flag.
5. **`POST /api/economics/evaluate`**: Symmetric techno-economic analysis evaluating extract liquor from either track across 4 downstream routes.

---

## 5. Bioreactor Studio UI Integration (`src/frontend`)

* **`RunConfigScreen.jsx`**:
  - Captures shared provenance lot ID, fresh rind mass, and initial moisture $X_{w,0}$.
  - Toggle between:
    - **Track A (Thermal Mechanistic Reference)**: Controls dried/sieved granulometry ($d_{50} \in \{150, 300, 600\}\,\mu\text{m}$), mechanical stirring ($250\text{--}400\text{ RPM}$), and Dimroth reflux sealing.
    - **Track B (UAE & Soft Sensor)**: Controls acoustic power ($P_{\text{acoustic}} \in [0, 200]\text{ W}$), bath temperature, paired control flag ($P_{\text{elec}} = 0\text{ W}$), and logs the measured wet $d_{50}$ covariate.
* **`ColorimeterSoftSensorWidget.jsx`**:
  Renders live 8-channel Developed vs. Sample-Blank spectra, net absorbance profile, concentration readouts, and the radial **GalA Composition / Purity Proxy** gauge.
