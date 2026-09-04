"""State-count sweep: separate statistical power from model mis-specification.

The Chapman-Kolmogorov test can fail for two very different reasons:

1. **Power.** Too few observed transitions relative to the number of
   free parameters in the transition matrix. With `k` states there are
   `k(k-1)` free parameters; with `n` epochs there are `n-1`
   transitions. Below roughly 10 transitions per parameter the
   estimate is too noisy for CK to be meaningful.
2. **Model mis-specification.** The process genuinely is not
   first-order Markov on the observed state alphabet, no matter how
   much data you give it.

These have opposite signatures under a state-count sweep. If it is
power, CK should PASS at small `k` (where obs-per-parameter is high)
and fail at large `k`. If it is mis-specification, CK should fail at
every `k`.

Run:

    python experiments/spd_transition_eegbci/state_count_sweep.py \
        --subjects 1 2 3 4 5 --k-values 2 3 4 6 8
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "instrument" / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from neurospine.dynamics import (  # noqa: E402
    chapman_kolmogorov_test,
    implied_timescales,
)
from run import (  # noqa: E402
    build_prototype_library,
    epoch_covariances,
    load_epochs,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subjects", type=int, nargs="+", default=[1, 2, 3, 4, 5])
    parser.add_argument("--k-values", type=int, nargs="+", default=[2, 3, 4, 6, 8])
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).parent / "results" / "state_count_sweep.json",
    )
    args = parser.parse_args()

    rows = []
    print(f"{'subj':>5} {'k':>3} {'n_trans':>8} {'free_p':>7} {'obs/p':>7} "
          f"{'ck_tv':>7} {'ck_ok':>6} {'plateau':>8}")
    for subj in args.subjects:
        epochs = load_epochs(subj)
        covs = epoch_covariances(epochs)
        n_trans = len(covs) - 1
        for k in args.k_values:
            _, labels = build_prototype_library(covs, k=k, seed=0)
            free_p = k * (k - 1)
            ck = chapman_kolmogorov_test(labels, k, lag=1, k_values=[2, 3])
            its = implied_timescales(
                labels, k, lags=[1, 2, 3, 4, 6, 8], n_timescales=1
            )
            row = {
                "subject": int(subj),
                "k": int(k),
                "n_transitions": int(n_trans),
                "free_parameters": int(free_p),
                "obs_per_parameter": float(n_trans / free_p),
                "ck_worst_row_tv": float(ck["worst_max_row_tv"]),
                "ck_passes": bool(ck["passes_conventional_threshold"]),
                "plateau_detected": bool(its["plateau_detected"]),
                "slowest_timescale_cv": float(its["slowest_timescale_cv"]),
            }
            rows.append(row)
            print(f"{subj:>5} {k:>3} {n_trans:>8} {free_p:>7} "
                  f"{row['obs_per_parameter']:>7.1f} {row['ck_worst_row_tv']:>7.3f} "
                  f"{str(row['ck_passes']):>6} {str(row['plateau_detected']):>8}")

    # Verdict logic.
    well_powered = [r for r in rows if r["obs_per_parameter"] >= 20.0]
    ck_pass_when_powered = sum(1 for r in well_powered if r["ck_passes"])
    any_plateau = sum(1 for r in rows if r["plateau_detected"])

    print()
    print(f"configurations with >= 20 obs/parameter: {len(well_powered)}")
    print(f"  of those, CK passes: {ck_pass_when_powered}")
    print(f"implied-timescale plateau detected in {any_plateau}/{len(rows)} configs")
    clean = [r for r in well_powered if r["ck_passes"] and r["ck_worst_row_tv"] < 0.08]
    print(f"  of the {ck_pass_when_powered} CK passes, {len(clean)} are clean "
          f"(TV < 0.08) and {ck_pass_when_powered - len(clean)} are marginal "
          f"(TV within 0.02 of the 0.1 threshold)")
    print()
    # The implied-timescale plateau is the more fundamental criterion:
    # it tests whether ANY lag makes the process Markov, whereas CK at
    # a single lag can pass trivially when k is tiny (k=2 leaves only
    # 2 free parameters, so T(1)^k and T(k) are forced close). Weight
    # the plateau result accordingly, and treat CK passes that sit
    # within 0.02 of the 0.1 threshold as marginal rather than clean.
    marginal_band = 0.02
    clean_ck_passes = [
        r for r in well_powered
        if r["ck_passes"] and r["ck_worst_row_tv"] < 0.1 - marginal_band
    ]

    if any_plateau == 0 and not clean_ck_passes:
        verdict = (
            "MODEL MIS-SPECIFICATION. No implied-timescale plateau appears "
            f"in any of {len(rows)} configurations, and no well-powered "
            "configuration passes Chapman-Kolmogorov cleanly (CK passes "
            "that sit within 0.02 of the threshold are counted as "
            "marginal). Insufficient data does not explain the failure: "
            "it persists at high observations-per-parameter. The process "
            "is not first-order Markov on this state alphabet at any "
            "tested resolution."
        )
    elif well_powered and len(clean_ck_passes) == len(well_powered) and any_plateau > 0:
        verdict = (
            "STATISTICAL POWER. CK passes cleanly whenever the estimate is "
            "well-powered and a plateau is detectable, so the earlier "
            "failures were a data-per-parameter problem, not a model "
            "problem."
        )
    else:
        verdict = (
            f"MIXED. {any_plateau}/{len(rows)} configurations show a "
            f"plateau and {len(clean_ck_passes)}/{len(well_powered)} "
            "well-powered configurations pass CK cleanly. Inspect the "
            "per-subject rows; the answer may be subject-dependent."
        )
    print(f"VERDICT: {verdict}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump({"rows": rows, "verdict": verdict}, f, indent=2)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
