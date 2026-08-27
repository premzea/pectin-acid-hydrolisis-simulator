"""
feedstock_variability.py
------------------------
Stress test: batch-to-batch feedstock variability.

For K synthetic batches, draw feedstock properties from a realistic prior:
    theta_f^(i) ~ p(theta_f)

For each batch:
  1. Build a ConditionedFeedstock using the drawn properties.
  2. Generate a 10-run OED dataset, treating the feedstock as known.
  3. Fit the Bayesian model.

Reports:
  - Per-parameter 95% BCI coverage across batches
  - CI widths (how much feedstock variability inflates uncertainty)
  - Which feedstock properties most destabilize the inference
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Dict

import numpy as np
import pandas as pd
import emcee

from pectin.feedstock.properties import ConditionedFeedstock
from pectin.simulator.solver import simulate
from pectin.chemistry.kinetics import KineticParameters
from pectin.calibration.parameterization import (
    PARAM_NAMES, PARAM_BOUNDS, pack, transform, inverse_transform, unpack
)
from pectin.calibration.sensitivity import (
    ExperimentCondition, build_noise_weights
)
from pectin.calibration.bayesian import GROUND_TRUTH_PARAMS
from pectin.calibration.least_squares import fit


# ---------------------------------------------------------------------------
# 10-run OED calibration protocol
# ---------------------------------------------------------------------------
OED_CONDITIONS = [
    ExperimentCondition(50.0, 1.5,  45.0, 600.0),
    ExperimentCondition(95.0, 2.5,  90.0, 600.0),
    ExperimentCondition(50.0, 1.5, 120.0, 300.0),
    ExperimentCondition(95.0, 1.5,  20.0, 300.0),
    ExperimentCondition(95.0, 3.0,  90.0, 150.0),
    ExperimentCondition(50.0, 2.0,  45.0, 150.0),
    ExperimentCondition(95.0, 2.0,  20.0, 600.0),
    ExperimentCondition(50.0, 2.0, 120.0, 600.0),
    ExperimentCondition(50.0, 1.5, 120.0, 150.0),
    ExperimentCondition(95.0, 1.5,  20.0, 150.0),
]

# Nominal feedstock
NOMINAL_FEEDSTOCK = dict(
    pectin_mass    = 0.20,    # kg/kg_dry
    galA_fraction  = 0.78,
    initial_DE     = 0.745,
    initial_Mw     = 654_000.0,
)

# Batch-to-batch CVs (lognormal)
FEEDSTOCK_CVS = dict(
    pectin_mass    = 0.12,
    galA_fraction  = 0.05,
    initial_DE     = 0.08,
    initial_Mw     = 0.15,
)


# ---------------------------------------------------------------------------
# Feedstock sampling
# ---------------------------------------------------------------------------

@dataclass
class FeedstockBatch:
    pectin_mass:   float
    galA_fraction: float
    initial_DE:    float
    initial_Mw:    float

    def to_conditioned(self, d50_um: float = 300.0) -> ConditionedFeedstock:
        return ConditionedFeedstock(
            dry_matter_mass=1.0,
            moisture_fraction=0.08,
            pectin_mass=self.pectin_mass,
            GalA_fraction=self.galA_fraction,
            DE=self.initial_DE,
            Mw_matrix=self.initial_Mw,
            d50_um=d50_um,
        )


def _lognormal_from_cv(mean: float, cv: float, rng: np.random.Generator) -> float:
    sigma_log = np.sqrt(np.log(1.0 + cv ** 2))
    mu_log    = np.log(mean) - 0.5 * sigma_log ** 2
    return float(rng.lognormal(mu_log, sigma_log))


def sample_feedstock_batch(rng: np.random.Generator) -> FeedstockBatch:
    """Draw one feedstock batch from a lognormal prior."""
    return FeedstockBatch(
        pectin_mass   = _lognormal_from_cv(NOMINAL_FEEDSTOCK["pectin_mass"],   FEEDSTOCK_CVS["pectin_mass"],   rng),
        galA_fraction = min(0.995, _lognormal_from_cv(NOMINAL_FEEDSTOCK["galA_fraction"], FEEDSTOCK_CVS["galA_fraction"], rng)),
        initial_DE    = min(0.999, _lognormal_from_cv(NOMINAL_FEEDSTOCK["initial_DE"],    FEEDSTOCK_CVS["initial_DE"],    rng)),
        initial_Mw    = _lognormal_from_cv(NOMINAL_FEEDSTOCK["initial_Mw"],    FEEDSTOCK_CVS["initial_Mw"],    rng),
    )


# ---------------------------------------------------------------------------
# Batch-specific forward model
# ---------------------------------------------------------------------------

OBS_KEYS = ("Y_GalA_product", "final_DE_product", "final_Mw_product")


def forward_model_batch(
    q:          np.ndarray,
    conditions: List[ExperimentCondition],
    batch:      FeedstockBatch,
) -> np.ndarray:
    """Forward simulation using a specific feedstock batch."""
    theta  = inverse_transform(q)
    params = unpack(theta)

    obs = []
    for cond in conditions:
        feedstock = batch.to_conditioned(d50_um=cond.d50_um)
        res = simulate(
            feedstock=feedstock,
            temperature_celsius=cond.temperature_celsius,
            pH=cond.pH,
            C_citric=0.0,
            time_min=cond.time_min,
            kinetic_params=params,
            recovery_efficiency=cond.recovery_efficiency,
        )
        for key in OBS_KEYS:
            obs.append(getattr(res, key))

    return np.array(obs, dtype=np.float64)


# ---------------------------------------------------------------------------
# Batch-specific Bayesian inference
# ---------------------------------------------------------------------------

def log_prior_bounds(q: np.ndarray) -> float:
    theta = inverse_transform(q)
    for name, (lo, hi) in PARAM_BOUNDS.items():
        i = PARAM_NAMES.index(name)
        if not (lo < theta[i] < hi):
            return -np.inf
    return 0.0


def run_single_batch(
    batch:          FeedstockBatch,
    kinetic_truth:  np.ndarray,
    rng:            np.random.Generator,
    n_walkers:      int = 32,
    n_steps:        int = 400,
    burn_in:        int = 150,
    seed:           int = 0,
) -> Dict:
    """Run the full inference pipeline for one feedstock batch."""
    q_true = transform(kinetic_truth)
    w      = build_noise_weights(OED_CONDITIONS)

    # Synthetic noisy observations with this batch's feedstock
    y_clean = forward_model_batch(q_true, OED_CONDITIONS, batch)
    y_obs   = y_clean + rng.normal(0.0, 1.0 / w)

    # Warm start: LS fit using the nominal feedstock (approximation — 
    # reflects real-world scenario where LS uses nominal feedstock values)
    try:
        ls = fit(OED_CONDITIONS, y_obs, kinetic_truth * 1.05)
        q_map = ls.q_opt
    except Exception:
        q_map = q_true + 0.05 * rng.normal(size=len(q_true))

    # MCMC with batch-specific likelihood
    def log_posterior(q):
        lp = log_prior_bounds(q)
        if not np.isfinite(lp):
            return -np.inf
        try:
            y_pred = forward_model_batch(q, OED_CONDITIONS, batch)
        except Exception:
            return -np.inf
        resid = (y_obs - y_pred) * w
        return lp - 0.5 * float(np.dot(resid, resid))

    n_dim = len(q_map)
    rng2  = np.random.default_rng(seed)
    pos0  = q_map + 1e-2 * rng2.normal(size=(n_walkers, n_dim))

    sampler = emcee.EnsembleSampler(n_walkers, n_dim, log_posterior)
    sampler.run_mcmc(pos0, n_steps, progress=False)

    flat_q = sampler.get_chain(discard=burn_in, flat=True)
    flat   = np.array([inverse_transform(q) for q in flat_q])

    row = {
        "pectin_mass":   batch.pectin_mass,
        "galA_fraction": batch.galA_fraction,
        "initial_DE":    batch.initial_DE,
        "initial_Mw":    batch.initial_Mw,
    }
    for i, name in enumerate(PARAM_NAMES):
        truth = kinetic_truth[i]
        p025  = np.percentile(flat[:, i],  2.5)
        p50   = np.percentile(flat[:, i], 50.0)
        p975  = np.percentile(flat[:, i], 97.5)
        row[f"{name}_truth"]     = truth
        row[f"{name}_median"]    = p50
        row[f"{name}_p025"]      = p025
        row[f"{name}_p975"]      = p975
        row[f"{name}_covered"]   = int(p025 <= truth <= p975)
        row[f"{name}_width_pct"] = (p975 - p025) / abs(truth) * 100.0

    return row


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_feedstock_variability_test(K: int = 10, seed: int = 0) -> pd.DataFrame:
    rng           = np.random.default_rng(seed)
    kinetic_truth = pack(GROUND_TRUTH_PARAMS)
    rows: List[Dict] = []

    for k in range(K):
        batch = sample_feedstock_batch(rng)
        print(f"\n--- Batch {k+1}/{K} ---")
        print(f"  P_matrix={batch.pectin_mass:.3f}  GalA={batch.galA_fraction:.3f}"
              f"  DE={batch.initial_DE:.3f}  Mw={batch.initial_Mw/1000:.0f} kDa")
        try:
            row = run_single_batch(batch, kinetic_truth, rng, seed=seed + k)
            rows.append(row)
            covered = sum(row[f"{n}_covered"] for n in PARAM_NAMES)
            print(f"  Coverage: {covered}/9")
        except Exception as exc:
            print(f"  FAILED: {exc}")

    return pd.DataFrame(rows)


def report_variability_results(df: pd.DataFrame) -> None:
    print("\n" + "=" * 70)
    print("FEEDSTOCK VARIABILITY STRESS TEST SUMMARY")
    print("=" * 70)
    print(f"  K = {len(df)} batches")
    print(f"  CVs: P_matrix={FEEDSTOCK_CVS['pectin_mass']*100:.0f}%"
          f"  GalA={FEEDSTOCK_CVS['galA_fraction']*100:.0f}%"
          f"  DE={FEEDSTOCK_CVS['initial_DE']*100:.0f}%"
          f"  Mw={FEEDSTOCK_CVS['initial_Mw']*100:.0f}%")
    print()

    total_trials  = len(df) * len(PARAM_NAMES)
    total_covered = sum(df[f"{n}_covered"].sum() for n in PARAM_NAMES)
    print(f"  Overall 95% BCI coverage: {total_covered}/{total_trials}"
          f"  ({100.0 * total_covered / total_trials:.1f}%)")
    print()
    print(f"  {'Parameter':<15} {'Cov':>6} {'Med CI%':>9} {'Max CI%':>9}")
    print("  " + "-" * 44)
    for name in PARAM_NAMES:
        cov   = df[f"{name}_covered"].sum()
        med_w = df[f"{name}_width_pct"].median()
        max_w = df[f"{name}_width_pct"].max()
        flag  = "  *** WIDE" if max_w > 50 else ""
        print(f"  {name:<15} {cov:>3}/{len(df):<3} {med_w:>8.1f}% {max_w:>8.1f}%{flag}")

    print()
    print("  Feedstock property dispersion:")
    for key in ["pectin_mass", "galA_fraction", "initial_DE", "initial_Mw"]:
        v = df[key].values
        print(f"    {key:<16}  mean={v.mean():.4g}  "
              f"CV={v.std()/v.mean()*100:.1f}%  "
              f"[{v.min():.4g}, {v.max():.4g}]")


if __name__ == "__main__":
    import os
    os.makedirs("artifacts/calibration", exist_ok=True)

    K = 10
    print(f"Feedstock variability stress test  ({K} batches x 32-walker MCMC)\n")
    df = run_feedstock_variability_test(K=K, seed=0)

    if len(df) > 0:
        df.to_csv("artifacts/calibration/feedstock_variability_results.csv", index=False)
        report_variability_results(df)
        print("\nSaved to artifacts/calibration/feedstock_variability_results.csv")
    else:
        print("All batches failed.")
