# Experimental Data Schema (V1.3)

To bridge the physical laboratory and the Bayesian inference engine, data must be structured relationally. This separates feed-level variability from process-level control and sampling-level observations.

## 1. Batch Record (`batch_record.csv`)
Logs the intact properties of a unique feedstock batch before any extraction runs are performed.

| Column | Type | Units | Description / Lab Origin |
|:---|:---|:---|:---|
| `batch_id` | String | - | Unique identifier (e.g., `B001`) |
| `moisture_pct` | Float | % (wb) | From 105 °C drying to constant mass |
| `d50_um` | Float | µm | Volumetric median particle size |
| `reference_AIR_yield` | Float | kg/kg_dry | Alcohol Insoluble Residue from a standard mild extraction |
| `reference_GalA_pct` | Float | % | GalA fraction of the standard AIR (anchors $P_{matrix,0}$) |
| `reference_DE_pct` | Float | % | DE of the standard mild extract (anchors latent $DE_{matrix}$) |
| `reference_Mw_Da` | Float | Da | HPSEC-MALLS of standard mild extract (anchors latent $M_{w,matrix}$) |

*Note on latent properties: Matrix DE and Matrix MW cannot be measured directly on solid rind. The `reference` values serve as the measurable proxy to set Bayesian priors.*

## 2. Process Run Record (`run_record.csv`)
Logs the macroscopic parameters for a single reactor extraction experiment.

| Column | Type | Units | Description |
|:---|:---|:---|:---|
| `run_id` | String | - | Unique identifier (e.g., `Run_001`) |
| `batch_id` | String | - | Foreign key to `batch_record.csv` |
| `reactor_vol_L` | Float | L | Initial liquid volume |
| `solid_mass_kg` | Float | kg | Initial dry solid mass added |
| `nominal_T` | Float | °C | Target temperature setpoint |
| `nominal_pH` | Float | - | Target pH setpoint |
| `process_log_file` | String | - | Filename for the high-frequency $T(t), pH(t)$ timeseries log |

## 3. High-Frequency Process Log (`process_log/<run_id>.csv`)
Provides the continuous data needed for explicit kinetic integration ($\tau_k = \int k(T(s), pH(s))\,ds$).

| Column | Type | Units | Description |
|:---|:---|:---|:---|
| `time_sec` | Float | s | Seconds since heating onset |
| `actual_T` | Float | °C | From submerged RTD probe |
| `actual_pH` | Float | - | From submerged pH probe |

## 4. Time-Resolved Sample Record (`sample_record.csv`)
Logs the individual aliquots withdrawn from the reactor and their downstream assays.

| Column | Type | Units | Description |
|:---|:---|:---|:---|
| `sample_id` | String | - | Unique identifier (e.g., `S_001_15m`) |
| `run_id` | String | - | Foreign key to `run_record.csv` |
| `quench_time_min` | Float | min | Exact time the aliquot entered the 0 °C quench bath |
| `volume_withdrawn_mL`| Float| mL | Tracked to compute cumulative volume loss |
| `aliquot_yield_pct` | Float | % | Extracted pectin concentration proxy in aliquot |
| `assay_DE_pct` | Float | % | Titration / FTIR result (leave blank if unassayed) |
| `assay_Mw_Da` | Float | Da | HPSEC-MALLS result (leave blank if unassayed) |
| `assay_GalA_pct` | Float | % | mHDP Colorimetric result (leave blank if unassayed) |

*Note: Aliquot yield is a time-resolved concentration measurement. Final gravimetric yield is a separate bulk metric determined downstream after full recovery.*
