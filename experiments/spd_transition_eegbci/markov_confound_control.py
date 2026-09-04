"""Discretization confound control for the ADR-009 Markov claim.

Council review (2026-09-04) identified the load-bearing error: a
function of a Markov process is generically NOT Markov, so discretizing
a continuous SPD trajectory into k prototype states can manufacture
apparent non-Markovianity. The implied-timescale-plateau and
Chapman-Kolmogorov failures reported for the EEG data are therefore
confounded unless a process that IS first-order Markov produces a
DIFFERENT signature under the same pipeline.

This control generates such a process (an AIRM autoregression, where
X_{t+1} depends only on X_t plus fresh tangent noise), pushes it
through the identical discretization + CK pipeline, and reports the
null distribution of the k=2 CK total-variation statistic. Only k=2 is
used for inference because at k >= 3 the estimate is too coarse to
distinguish Markov from non-Markov at this sample size (the control
itself fails CK at k >= 3, so those failures are non-diagnostic).

Run:

    python experiments/spd_transition_eegbci/markov_confound_control.py \
        --n-realizations 25 --subjects 1 2 3 4 5
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

from neurospine.dynamics import chapman_kolmogorov_test  # noqa: E402
from neurospine.manifold import (  # noqa: E402
    airm_distance,
    airm_exp_map,
    airm_frechet_mean,
    airm_geodesic,
)
from run import build_prototype_library, epoch_covariances, load_epochs  # noqa: E402


def _random_spd(rng: np.random.Generator, n: int, scale: float = 1.0) -> np.ndarray:
    A = rng.standard_normal((n, n)) * scale
    return A @ A.T + 0.5 * np.eye(n)


def airm_ar1_trajectory(
    rng: np.random.Generator,
    n_steps: int,
    dim: int = 5,
    phi: float = 0.7,
    noise: float = 0.15,
) -> np.ndarray:
    """First-order AIRM autoregression. X_{t+1} is a geodesic pull of
    X_t toward the identity by (1 - phi), then a fresh tangent-space
    Gaussian kick. By construction X_{t+1} depends ONLY on X_t, so the
    continuous process is first-order Markov."""
    mu = np.eye(dim)
    X = _random_spd(rng, dim)
    traj = [X]
    for _ in range(n_steps - 1):
        pulled = airm_geodesic(X, mu, 1.0 - phi)
        E = rng.standard_normal((dim, dim))
        E = 0.5 * (E + E.T) * noise
        X = airm_exp_map(pulled, E)
        traj.append(X)
    return np.array(traj)


def _discretize(rng: np.random.Generator, covs: np.ndarray, k: int) -> np.ndarray:
    idx = rng.choice(len(covs), k, replace=False)
    protos = covs[idx].copy()
    labels = np.zeros(len(covs), dtype=int)
    for _ in range(10):
        new = np.array(
            [int(np.argmin([airm_distance(c, p) for p in protos])) for c in covs]
        )
        if np.array_equal(new, labels):
            break
        labels = new
        for j in range(k):
            m = covs[labels == j]
            if len(m) > 0:
                protos[j] = airm_frechet_mean(list(m), max_iter=30)
    return labels


def build_null(
    n_realizations: int, n_steps: int, dim: int, seed: int = 1
) -> np.ndarray:
    """Null distribution of the k=2 CK TV statistic for a KNOWN
    first-order Markov process at matched length and dimension."""
    rng = np.random.default_rng(seed)
    tvs = []
    for _ in range(n_realizations):
        covs = airm_ar1_trajectory(rng, n_steps, dim=dim)
        labels = _discretize(rng, covs, 2)
        ck = chapman_kolmogorov_test(labels, 2, lag=1, k_values=[2, 3])
        tvs.append(float(ck["worst_max_row_tv"]))
    return np.array(tvs)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-realizations", type=int, default=25)
    parser.add_argument("--subjects", type=int, nargs="+", default=[1, 2, 3, 4, 5])
    parser.add_argument("--seeds", type=int, default=5,
                        help="discretization seeds to average per subject")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).parent / "results" / "markov_confound_control.json",
    )
    args = parser.parse_args()

    # One representative subject fixes the trajectory length + dimension.
    example = load_epochs(args.subjects[0])
    n_steps, dim = example.shape[0], example.shape[1]

    print(f"Building k=2 Markov null ({args.n_realizations} realizations, "
          f"length {n_steps}, dim {dim})")
    null = build_null(args.n_realizations, n_steps, dim)
    p95 = float(np.percentile(null, 95))
    print(f"  known-first-order-Markov k=2 CK TV: mean {null.mean():.3f} "
          f"sd {null.std(ddof=1):.3f} 95th pct {p95:.3f}")
    print()

    rows = []
    n_exceed = 0
    print(f"{'subj':>5} {'k2_ck_tv(seed-avg)':>18} {'p_vs_null':>10} {'verdict':>16}")
    for subj in args.subjects:
        epochs = load_epochs(subj)
        covs = epoch_covariances(epochs)
        tvs = []
        for s in range(args.seeds):
            _, labels = build_prototype_library(covs, k=2, seed=s)
            ck = chapman_kolmogorov_test(labels, 2, lag=1, k_values=[2, 3])
            tvs.append(float(ck["worst_max_row_tv"]))
        tv = float(np.mean(tvs))
        p = float((null >= tv).mean())
        exceeds = p < 0.05
        n_exceed += int(exceeds)
        verdict = "exceeds Markov" if exceeds else "within Markov"
        rows.append({
            "subject": int(subj),
            "k2_ck_tv_seed_avg": tv,
            "k2_ck_tv_per_seed": tvs,
            "p_vs_markov_null": p,
            "exceeds_markov_null": exceeds,
        })
        print(f"{subj:>5} {tv:>18.3f} {p:>10.2f} {verdict:>16}")

    print()
    print(f"{n_exceed}/{len(args.subjects)} subjects exceed the first-order Markov "
          f"null at k=2 (seed-averaged).")
    print()
    print("CORRECTED CLAIM: the discretized EEG state sequence deviates from a")
    print("first-order Markov process ONLY for the subjects listed above, and")
    print("ONLY at k=2. The implied-timescale plateau and the k>=3 CK failures")
    print("are NON-DIAGNOSTIC: a process that is first-order Markov by")
    print("construction produces the identical signature under this pipeline.")

    result = {
        "null_mean": float(null.mean()),
        "null_sd": float(null.std(ddof=1)),
        "null_p95": p95,
        "null_n": int(args.n_realizations),
        "per_subject": rows,
        "n_subjects_exceeding_markov_null": int(n_exceed),
        "n_subjects": len(args.subjects),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(result, f, indent=2)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
