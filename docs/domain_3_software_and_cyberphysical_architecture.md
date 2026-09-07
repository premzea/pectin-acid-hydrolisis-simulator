# Domain 3: Software Engineering & Cyber-Physical System Architecture

**Document Version**: 3.0 (Unified Fresh-Rind Feedstock Architecture)  
**Parent Document**: [`MASTER_DUAL_TRACK_SPECIFICATION.md`](file:///Z:/home/eduzea/projects/pectin-extraction/pectin-acid-hydrolisis-simulator/docs/MASTER_DUAL_TRACK_SPECIFICATION.md)  
**Target Audience**: Software Engineers, Full-Stack Developers, Embedded/IoT Engineers, UI/UX Designers

---

## 1. Executive Scope & Cyber-Physical Overview

The Bioreactor Studio software suite orchestrates experimental data logging, physical sensor ingestion, and digital twin simulation across both operational tracks using a **unified fresh-rind feedstock data model**:

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             REACT 19 FRONTEND (SPA)                              │
│  - Run Configuration (Common Fresh Rind -> Track A Thermal vs Track B UAE)       │
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

## 2. Common Fresh-Rind Data Schema (`runs` & `uae_runs`)

Because both tracks use fresh food-processed rind, core biomass fields are normalized across all runs in SQLite:

```sql
ALTER TABLE runs ADD COLUMN fresh_rind_mass_g REAL;
ALTER TABLE runs ADD COLUMN batch_moisture_fraction REAL;
ALTER TABLE runs ADD COLUMN water_mass_g REAL;
ALTER TABLE runs ADD COLUMN dry_matter_mass_g REAL;
ALTER TABLE runs ADD COLUMN fragment_size_d50_um REAL;
ALTER TABLE runs ADD COLUMN track_type TEXT; -- 'track_a_thermal' or 'track_b_uae'
```

### Table 1: `uae_runs` (Track B Logger)
```sql
CREATE TABLE IF NOT EXISTS uae_runs (
    run_id TEXT PRIMARY KEY,
    calibration_id_gala TEXT,
    calibration_id_pectin TEXT,
    fresh_rind_mass_g REAL NOT NULL,
    water_mass_g REAL NOT NULL,
    fresh_moisture_pct REAL NOT NULL,
    dry_matter_mass_g REAL NOT NULL,
    particle_size_um REAL NOT NULL,
    initial_ph REAL NOT NULL,
    extraction_temp_c REAL NOT NULL,
    bath_temp_c REAL NOT NULL,
    is_thermal_control INTEGER DEFAULT 0, -- 1 for P_elec = 0 matched controls
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

### Table 2: Unified Provenance Tables
1. `colorimeter_calibrations`: Ingests multi-wavelength standard series, fits $[A_{\text{net}}(515), A_{\text{net}}(555), A_{\text{net}}(680)] \to C_{\text{GalA}}$, checks spike recovery, registers linear limits $[C_{\min}, C_{\max}]$.
2. `ftir_calibrations`: PLS/PCR models for secondary offline solid state analysis.
3. `viscometer_calibrations`: Mark-Houwink parameters for molecular weight estimation.

---

## 3. Real-Time Telemetry Frame Schema (JSON)

```json
{
  "kind": "telemetry",
  "device_id": "UNO-Q-01",
  "run_id": "RUN-2026-09-FRESH-01",
  "timestamp_arduino": 1845000,
  "sim_time_min": 30.75,
  "track_type": "track_b_uae",
  "is_thermal_control": false,
  "reactor_T_C": 58.4,
  "bath_T_C": 60.1,
  "reflux_T_C": 16.2,
  "pH": 2.15,
  "ultrasound_active": true,
  "ultrasound_power_w": 180.0,
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

1. **`POST /api/colorimeter/calibrations`**:
   Registers a first-class calibration object with sample-blank subtraction and matrix-spike verification.
2. **`POST /api/colorimeter/measure`**:
   Ingests developed tube and sample-blank tube spectra, computes net absorbance vector, validates linear range, and returns $C_{\text{GalA}}$, $C_{\text{pectin-equiv}}$, and dilution advisory.
3. **`POST /api/uae/simulate`**:
   Forward simulation of Track B given fresh rind mass, measured moisture $X_{w,0}$, acoustic power, and time.
4. **`POST /api/uae/runs/record`**:
   Commits a completed Arduino Q experiment record into `uae_runs`.
5. **`POST /api/economics/evaluate`**:
   Symmetric techno-economic analysis evaluating extract liquor from either track across all 4 industrial downstream routes.

---

## 5. Bioreactor Studio UI Integration (`src/frontend`)

* **`RunConfigScreen.jsx`**:
  A unified **Fresh Feedstock Header** captures $m_{\text{fresh}}$, measured moisture $X_{w,0}$, and food-processor fragment size $d_{50}$. A clean toggle selects between:
  - **Track A (Thermal Mechanistic Reference)**: Jacketed reactor stirring RPM, reflux status, and quench aliquot schedule.
  - **Track B (UAE & Soft Sensor)**: Ultrasonic nominal power slider ($0\text{--}300\text{ W}$), bath temperature, and paired thermal control flag ($P_{\text{elec}} = 0\text{ W}$).
* **`ColorimeterSoftSensorWidget.jsx`**:
  Renders live 8-channel Developed vs. Sample-Blank spectra, net absorbance profile, concentration readouts, and the radial **GalA Composition / Purity Proxy** gauge.
