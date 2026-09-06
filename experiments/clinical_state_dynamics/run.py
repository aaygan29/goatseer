"""ADHD vs typically-developing: does the disorder alter brain-state
DYNAMICS, as a group comparison with confound control?

This is NOT a cross-subject classifier. It is a two-sample comparison of
group-level dynamics summaries (entropy rate, spectral gap, mean dwell
time, metastable-community count) computed from each subject's own
discretized Schaefer-100 regional trajectory, with a permutation null on
the group difference and mandatory confound control for site and motion
(ADHD-200 is strongly confounded by both; see ADR-022).

Design
------

1. Fetch ADHD-200 (`neurospine.io.fetch_adhd`), inspect the phenotypic
   table for diagnosis (`DX`), site (`Site`), and a motion proxy (mean
   framewise displacement, computed here directly from the confound file
   if not already provided as a column).
2. Per subject: Schaefer-100 regional time series via
   `NiftiLabelsMasker`, confound regression using the subject's provided
   confound file (same pattern as
   `experiments/thought_propagation/build_augmented_connectome.py`).
3. Standardize each region's time series (z-score across time), k-means
   into `--n-states` discrete states.
4. `neurospine.dynamics.estimate_transition_matrix` on the state
   sequence -> `entropy_rate`, `spectral_gap`, mean dwell time (1 / (1 -
   mean diagonal) in TRs), metastable-community count via
   `perron_cluster_analysis` (count of eigenvalues of T with modulus
   above a spectral-gap-relative threshold, capped at `--k-metastable`).
5. Group comparison (ADHD vs control) on each summary, under the
   confound control selected by `--confound-control`:
     - `single-site`: restrict to the single largest site (drops the
       site confound by construction; motion is reported, not adjusted).
     - `residualize`: fit OLS of the summary on site (dummy-coded) and
       mean FD pooled across the full sample, test the RESIDUAL's group
       difference (removes both confounds' linear contribution).
6. Permutation null: shuffle the diagnosis label within site (or
   overall, if `single-site`) 5000 times, recompute the group mean
   difference each time, two-sided p-value.

Run:

    python3 experiments/clinical_state_dynamics/run.py \
        --n-subjects 40 --n-states 5 --confound-control residualize
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "instrument" / "src"))

from neurospine.dynamics import (  # noqa: E402
    entropy_rate,
    estimate_transition_matrix,
    perron_cluster_analysis,
    spectral_gap,
)

RNG_SEED = 0


# --------------------------------------------------------------------
# Phenotypic inspection / motion proxy
# --------------------------------------------------------------------


def mean_fd_from_confounds(confound_path: str) -> float:
    """Mean framewise displacement computed from the subject's nilearn
    ADHD-200 confound file when the phenotypic table has no motion
    column. nilearn's ADHD confound files carry six motion-parameter
    columns (three translations, three rotations); FD is the sum of
    absolute frame-to-frame differences (rotations converted to an
    approximate arc length via a 50mm head radius, the standard
    Power et al. 2012 convention).
    """
    df = pd.read_csv(confound_path, sep=r"\s+", engine="python")
    cols = [c for c in df.columns if not c.lower().startswith("global")]
    motion = df[cols].to_numpy(dtype=float)
    if motion.shape[1] >= 6:
        d = np.diff(motion[:, :6], axis=0)
        d[:, 3:6] *= 50.0  # rotation (rad) -> arc length (mm) at r=50mm
        fd = np.abs(d).sum(axis=1)
    else:
        d = np.diff(motion, axis=0)
        fd = np.abs(d).sum(axis=1)
    return float(fd.mean())


# --------------------------------------------------------------------
# Per-subject dynamics summary
# --------------------------------------------------------------------


def subject_dynamics_summary(
    func_path: str,
    confound_path: str,
    masker,
    n_states: int,
    k_metastable: int,
    seed: int,
) -> dict:
    from sklearn.cluster import KMeans

    ts = masker.fit_transform(func_path, confounds=confound_path)
    mu = ts.mean(axis=0, keepdims=True)
    sd = ts.std(axis=0, keepdims=True)
    sd[sd == 0] = 1.0
    ts_z = (ts - mu) / sd

    km = KMeans(n_clusters=n_states, n_init=10, random_state=seed)
    state_seq = km.fit_predict(ts_z)

    T = estimate_transition_matrix(state_seq, n_states, laplace=1.0 / 1024)
    h_rate = entropy_rate(T)
    gap = spectral_gap(T)
    dwell = float(1.0 / max(1.0 - np.mean(np.diag(T)), 1e-6))

    eigvals = np.linalg.eigvals(T)
    moduli = np.sort(np.abs(eigvals))[::-1]
    # Number of eigenvalues (beyond the stationary one) whose modulus
    # exceeds half the leading spectral gap: an intrinsic estimate of
    # how many metastable communities the chain supports, capped by
    # k_metastable and used only to size the PCCA call.
    n_meta = 1
    for lam in moduli[1:k_metastable]:
        if lam > 0.5:
            n_meta += 1
    labels = perron_cluster_analysis(T, max(1, min(n_meta, k_metastable)))
    n_communities = int(len(np.unique(labels)))

    return {
        "entropy_rate": h_rate,
        "spectral_gap": gap,
        "mean_dwell_time": dwell,
        "n_metastable_communities": float(n_communities),
        "n_timepoints": int(ts.shape[0]),
    }


# --------------------------------------------------------------------
# Group comparison
# --------------------------------------------------------------------


def residualize(y: np.ndarray, site: np.ndarray, mean_fd: np.ndarray) -> np.ndarray:
    """OLS-residualize `y` on site dummies + mean FD (+ intercept)."""
    site_dummies = pd.get_dummies(pd.Series(site), drop_first=True).to_numpy(dtype=float)
    X = np.column_stack([np.ones(len(y)), mean_fd, site_dummies])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return y - X @ beta


def permutation_test(
    values: np.ndarray,
    group: np.ndarray,
    site: np.ndarray | None,
    n_perm: int,
    rng: np.random.Generator,
) -> tuple[float, float]:
    """Two-sided permutation test on the ADHD-minus-control mean
    difference. When `site` is given, the label is shuffled WITHIN
    site (a stratified permutation) so the null preserves the
    site/group correlation structure rather than only the marginal
    group sizes.
    """
    adhd_mask = group == 1
    obs = float(values[adhd_mask].mean() - values[~adhd_mask].mean())

    null = np.empty(n_perm)
    idx_by_site = None
    if site is not None:
        idx_by_site = {s: np.where(site == s)[0] for s in np.unique(site)}

    for p in range(n_perm):
        perm_group = group.copy()
        if idx_by_site is not None:
            for _, idx in idx_by_site.items():
                perm_group[idx] = rng.permutation(group[idx])
        else:
            perm_group = rng.permutation(group)
        pa = perm_group == 1
        null[p] = values[pa].mean() - values[~pa].mean()

    p_value = float((np.abs(null) >= abs(obs)).mean())
    return obs, p_value


def cohens_d(values: np.ndarray, group: np.ndarray) -> float:
    a = values[group == 1]
    c = values[group == 0]
    n1, n2 = len(a), len(c)
    pooled_sd = np.sqrt(
        ((n1 - 1) * a.var(ddof=1) + (n2 - 1) * c.var(ddof=1)) / max(n1 + n2 - 2, 1)
    )
    if pooled_sd == 0:
        return 0.0
    return float((a.mean() - c.mean()) / pooled_sd)


# --------------------------------------------------------------------
# Main
# --------------------------------------------------------------------


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-subjects", type=int, default=40)
    ap.add_argument("--n-rois", type=int, default=100)
    ap.add_argument("--n-states", type=int, default=5)
    ap.add_argument("--k-metastable", type=int, default=4)
    ap.add_argument("--n-perm", type=int, default=5000)
    ap.add_argument(
        "--confound-control",
        choices=["single-site", "residualize"],
        default="residualize",
    )
    ap.add_argument(
        "--out", type=Path,
        default=Path(__file__).parent / "results" / "clinical_state_dynamics.json",
    )
    args = ap.parse_args()

    from nilearn.datasets import fetch_atlas_schaefer_2018
    from nilearn.maskers import NiftiLabelsMasker

    from neurospine.io import fetch_adhd

    print(f"[clinical] fetching ADHD-200 (n={args.n_subjects})")
    d = fetch_adhd(n_subjects=args.n_subjects)
    pheno = d.phenotypic.copy()

    # The nilearn phenotypic table (`site`, `adhd`/`tdc`, `MeanFD`) does not
    # cover every functional scan returned by fetch_adhd (some sites in the
    # func/confounds arrays have no matching phenotypic row in this reduced
    # CSV); align by the numeric subject id embedded in each func filename
    # and DROP scans with no phenotypic match rather than guess a label.
    pheno_by_subject = {int(s): row for s, row in zip(pheno["Subject"], pheno.to_dict("records"))}
    func_subject_ids = [
        int(re.search(r"(\d+)", Path(f).name).group(1)) for f in d.func
    ]
    matched_idx = [i for i, sid in enumerate(func_subject_ids) if sid in pheno_by_subject]
    dropped = len(d.func) - len(matched_idx)
    print(
        f"[clinical] {len(matched_idx)}/{len(d.func)} functional scans have a "
        f"matching phenotypic row ({dropped} dropped: no diagnosis/site/motion "
        "label available for those scans)"
    )

    diagnosis = np.array(
        [int(pheno_by_subject[func_subject_ids[i]]["adhd"]) for i in matched_idx]
    )
    site = np.array(
        [str(pheno_by_subject[func_subject_ids[i]]["site"]) for i in matched_idx]
    )
    mean_fd = np.array(
        [float(pheno_by_subject[func_subject_ids[i]]["MeanFD"]) for i in matched_idx]
    )
    func_paths = [d.func[i] for i in matched_idx]
    confound_paths = [d.confounds[i] for i in matched_idx]

    n_adhd = int(diagnosis.sum())
    n_control = int(len(diagnosis) - n_adhd)
    site_counts = pd.Series(site).value_counts().to_dict()
    print(f"[clinical] N analyzed = {len(diagnosis)}  (ADHD {n_adhd}, control {n_control})")
    print(f"[clinical] site distribution: {site_counts}")
    print(
        f"[clinical] mean FD by group (phenotypic MeanFD column): ADHD "
        f"{mean_fd[diagnosis == 1].mean():.4f}, control {mean_fd[diagnosis == 0].mean():.4f}"
    )

    keep = np.arange(len(diagnosis))
    control_desc = ""
    if args.confound_control == "single-site":
        largest_site = pd.Series(site).value_counts().idxmax()
        keep = np.where(site == largest_site)[0]
        control_desc = f"single-site restriction to site {largest_site!r} (n={len(keep)})"
        print(f"[clinical] confound control: {control_desc}")
    else:
        control_desc = "residualize summaries on site dummies + mean FD (OLS), test residual group difference"
        print(f"[clinical] confound control: {control_desc}")

    print(f"[clinical] fetching Schaefer-{args.n_rois} atlas")
    atlas = fetch_atlas_schaefer_2018(n_rois=args.n_rois, yeo_networks=7, resolution_mm=2)
    masker = NiftiLabelsMasker(labels_img=atlas.maps, standardize="zscore_sample", verbose=0)

    rows = []
    for i in keep:
        func_path = func_paths[i]
        conf_path = confound_paths[i]
        try:
            summary = subject_dynamics_summary(
                func_path, conf_path, masker, args.n_states, args.k_metastable, seed=RNG_SEED
            )
        except Exception as exc:  # noqa: BLE001
            print(f"[clinical]   subject {i} FAILED: {exc}")
            continue
        summary["subject_idx"] = int(i)
        summary["diagnosis"] = int(diagnosis[i])
        summary["site"] = str(site[i])
        summary["mean_fd"] = float(mean_fd[i])
        rows.append(summary)
        print(
            f"[clinical]   subject {i} ({'ADHD' if diagnosis[i] else 'control'}, "
            f"site {site[i]}): entropy_rate={summary['entropy_rate']:.3f} "
            f"gap={summary['spectral_gap']:.3f} dwell={summary['mean_dwell_time']:.2f} "
            f"communities={summary['n_metastable_communities']:.0f}"
        )

    df = pd.DataFrame(rows)
    df.to_csv(Path(__file__).parent / "results" / "subject_summaries.csv", index=False)

    rng = np.random.default_rng(RNG_SEED)
    metrics = ["entropy_rate", "spectral_gap", "mean_dwell_time", "n_metastable_communities"]
    results = {
        "n_subjects_total": int(len(diagnosis)),
        "n_subjects_analyzed": int(len(df)),
        "n_adhd": n_adhd,
        "n_control": n_control,
        "site_distribution": site_counts,
        "mean_fd_by_group": {
            "adhd": float(mean_fd[diagnosis == 1].mean()),
            "control": float(mean_fd[diagnosis == 0].mean()),
        },
        "confound_control": args.confound_control,
        "confound_control_description": control_desc,
        "n_permutations": args.n_perm,
        "comparisons": {},
    }

    group = df["diagnosis"].to_numpy()
    site_arr = df["site"].to_numpy()
    fd_arr = df["mean_fd"].to_numpy()

    for metric in metrics:
        y = df[metric].to_numpy(dtype=float)
        if args.confound_control == "residualize":
            y_test = residualize(y, site_arr, fd_arr)
            perm_site = site_arr if len(np.unique(site_arr)) > 1 else None
        else:
            y_test = y
            perm_site = None  # single site already; nothing to stratify on

        d_effect = cohens_d(y_test, group)
        obs_diff, p_value = permutation_test(y_test, group, perm_site, args.n_perm, rng)
        results["comparisons"][metric] = {
            "adhd_mean_raw": float(y[group == 1].mean()),
            "control_mean_raw": float(y[group == 0].mean()),
            "observed_diff_tested": obs_diff,
            "cohens_d": d_effect,
            "permutation_p": p_value,
        }
        print(
            f"[clinical] {metric}: ADHD-control diff (tested) = {obs_diff:+.4f}, "
            f"d = {d_effect:+.3f}, perm p = {p_value:.4f}"
        )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[clinical] wrote {args.out}")


if __name__ == "__main__":
    main()
