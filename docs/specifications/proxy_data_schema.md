# Phase 1 Proxy Calibration Data Schema

This schema defines the structure for logging the results of the paired sample calibration study. 
Because the Proxy Observation ($\mathbf{z}$) and the Reference Assay ($\mathbf{y}$) are measured on the exact same precipitated pellet, the rows represent a single 1:1 paired observation.

## `phase1_paired_observations.csv`

| Column | Type | Units | Description / Origin |
|:---|:---|:---|:---|
| `sample_id` | String | - | Unique physical identifier (e.g., `B002-R07-S03`) |
| `run_id` | String | - | Identifying the reactor trajectory (e.g., `B002-R07`) |
| `aliquot_time_min` | Float | min | Exact quench time |
| `m_liquor` | Float | g | Exact mass of liquor withdrawn (Target: 20.0 g) |
| `m_dry_pellet` | Float | g | Exact mass of the dried AIR pellet |
| `C_ppt` | Float | g/g | $m_{dry\_pellet} / m_{liquor}$. The concentration proxy. |
| `C_pellet` | Float | % w/v | Exact concentration of the pellet dissolved for viscosity testing. |
| `z_t_flow` | Float | s | Simple viscosity flow time. |
| `z_FTIR_file` | String | - | Path to the raw exported FTIR spectrum (e.g., `spectra/C1_10m.csv`) |
| `y_SEC_Mw` | Float | Da | **Reference**: True $M_w$ from HPSEC-MALLS on the dissolved pellet. |
| `y_Titration_DE` | Float | % | **Reference**: True $DE$ from Titration on the pellet. |
| `y_mHDP_GalA` | Float | % | **Reference**: True $X_{GalA}$ from colorimetry on the pellet. |

*(Note: During chemometric modeling, the target is to predict the `y_` columns from the `z_` columns using Leave-One-Run-Out cross-validation grouped by `run_id`).*
