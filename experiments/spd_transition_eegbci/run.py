"""Real-data run for ADR-009: estimate a thought-trajectory transition
matrix on the PhysioNet EEG-BCI motor-imagery dataset.

Pipeline per subject:

1. Download runs 4 and 6 (motor imagery: right vs left fist) via
   `mne.datasets.eegbci`. About 30 MB.
2. Bandpass 8-30 Hz, re-reference to average, select a small
   sensorimotor channel set.
3. Window the continuous signal into 2-second non-overlapping epochs.
4. Compute one SPD covariance matrix per epoch.
5. Learn a k-medoids-like prototype library on the AIRM distance to
   the Frechet mean of a small init subset.
6. Discretize each epoch to the nearest prototype under AIRM.
7. Estimate the transition matrix on the discretized sequence.
8. Report: stationary distribution, entropy rate, spectral gap,
   effective dimension, metastable-basin labels. Numerically verify
   row-stochasticity and that pi @ T equals pi within tolerance.

Run:

    make -C experiments/spd_transition_eegbci run

or directly:

    python experiments/spd_transition_eegbci/run.py --subject 1

Output: prints a JSON summary to stdout and writes it to
`results/summary_subject-<N>.json` under the experiment dir.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

# Add instrument/src to path so `neurospine` imports cleanly when
# running the script directly.
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "instrument" / "src"))

from neurospine.dynamics import summarize_trajectory  # noqa: E402
from neurospine.manifold import (  # noqa: E402
    airm_distance,
    airm_frechet_mean,
)


SENSORIMOTOR_CHANNELS = ["C3", "C4", "Cz", "Fz", "Pz"]


def load_epochs(subject: int, epoch_seconds: float = 2.0) -> np.ndarray:
    """Return `(n_epochs, n_channels, n_samples)` from PhysioNet
    EEG-BCI runs 4 and 6 for `subject`. Filtered 8-30 Hz, common
    average reference, selected sensorimotor channels."""
    import mne
    from mne.datasets import eegbci

    files = eegbci.load_data(
        subject, runs=[4, 6], update_path=True, verbose="ERROR"
    )
    raws = [mne.io.read_raw_edf(f, preload=True, verbose="ERROR") for f in files]
    raw = mne.concatenate_raws(raws)
    eegbci.standardize(raw)
    raw.set_montage("standard_1020", on_missing="ignore")
    raw.pick(SENSORIMOTOR_CHANNELS, verbose="ERROR")
    raw.set_eeg_reference("average", projection=False, verbose="ERROR")
    raw.filter(8.0, 30.0, fir_design="firwin", verbose="ERROR")

    sfreq = raw.info["sfreq"]
    n_samples_per_epoch = int(round(epoch_seconds * sfreq))
    data = raw.get_data()  # (n_channels, n_samples)
    n_channels, n_total = data.shape
    n_epochs = n_total // n_samples_per_epoch
    trimmed = data[:, : n_epochs * n_samples_per_epoch]
    epochs = trimmed.reshape(n_channels, n_epochs, n_samples_per_epoch).transpose(1, 0, 2)
    return epochs


def epoch_covariances(epochs: np.ndarray, ridge: float = 1e-3) -> np.ndarray:
    """Compute per-epoch sample covariances, symmetrized and ridged
    to guarantee SPD-ness. Returns `(n_epochs, n_channels, n_channels)`."""
    n_epochs, n_channels, _ = epochs.shape
    covs = np.zeros((n_epochs, n_channels, n_channels))
    for i in range(n_epochs):
        x = epochs[i]
        c = (x @ x.T) / (x.shape[1] - 1)
        c = 0.5 * (c + c.T)
        c += ridge * np.eye(n_channels) * np.trace(c) / n_channels
        covs[i] = c
    return covs


def build_prototype_library(
    covs: np.ndarray, k: int = 6, seed: int = 0, max_iter: int = 10
) -> tuple[np.ndarray, np.ndarray]:
    """K-medoids-like prototype library on the AIRM manifold.

    Returns `(prototypes, labels)` where `prototypes` is `(k, C, C)`
    and `labels[i]` is the prototype index nearest to `covs[i]`.
    Prototypes are AIRM Frechet means of their assigned members.
    """
    n, C, _ = covs.shape
    rng = np.random.default_rng(seed)
    idx = rng.choice(n, k, replace=False)
    prototypes = covs[idx].copy()
    labels = np.zeros(n, dtype=int)
    for _ in range(max_iter):
        new_labels = np.zeros(n, dtype=int)
        for i in range(n):
            dists = [airm_distance(covs[i], p) for p in prototypes]
            new_labels[i] = int(np.argmin(dists))
        if np.array_equal(new_labels, labels):
            break
        labels = new_labels
        for j in range(k):
            members = covs[labels == j]
            if len(members) > 0:
                prototypes[j] = airm_frechet_mean(list(members), max_iter=30)
    return prototypes, labels


def quality_control(epochs: np.ndarray, covs: np.ndarray) -> dict:
    """Recording-quality checks that must pass before a trajectory
    result is interpretable as cognition rather than artifact.

    A nearly-reducible transition matrix (tiny spectral gap, effective
    dimension near 1) can arise from a genuinely trapped cognitive
    trajectory OR from a degenerate recording: a flat channel, a
    saturated amplifier, or a covariance that barely moves. These
    checks separate the two.

    Flags:
    - `flat_channel`: any channel whose variance is below 1e-3 of the
      median channel variance.
    - `low_covariance_variability`: the median AIRM distance between
      consecutive epoch covariances is below 0.05, meaning the state
      barely moves epoch to epoch.
    - `extreme_condition_number`: any epoch covariance with condition
      number above 1e6, meaning the SPD matrix is near-singular and
      AIRM quantities become numerically unreliable.
    - `amplitude_saturation`: more than 1 percent of samples at or
      beyond 3 standard deviations of a channel's own distribution in
      a way consistent with clipping (identical extreme values).
    """
    n_epochs, n_channels, n_samples = epochs.shape

    chan_var = epochs.reshape(n_channels * n_epochs, -1).var(axis=1)
    chan_var = epochs.transpose(1, 0, 2).reshape(n_channels, -1).var(axis=1)
    median_var = float(np.median(chan_var))
    flat = [
        int(i) for i in range(n_channels)
        if median_var > 0 and chan_var[i] < 1e-3 * median_var
    ]

    consecutive = [
        airm_distance(covs[i], covs[i + 1]) for i in range(len(covs) - 1)
    ]
    median_step = float(np.median(consecutive)) if consecutive else 0.0

    conds = [float(np.linalg.cond(c)) for c in covs]
    max_cond = float(np.max(conds))

    # Clipping heuristic: count exact-duplicate extreme values.
    flat_signal = epochs.transpose(1, 0, 2).reshape(n_channels, -1)
    sat_frac = 0.0
    for ch in range(n_channels):
        x = flat_signal[ch]
        if x.size == 0:
            continue
        hi = np.max(np.abs(x))
        if hi == 0:
            continue
        n_at_extreme = int(np.sum(np.isclose(np.abs(x), hi, rtol=1e-9)))
        sat_frac = max(sat_frac, n_at_extreme / x.size)

    flags = {
        "flat_channels": flat,
        "median_consecutive_airm_step": median_step,
        "max_condition_number": max_cond,
        "max_saturation_fraction": float(sat_frac),
        "flag_flat_channel": bool(flat),
        "flag_low_covariance_variability": bool(median_step < 0.05),
        "flag_extreme_condition_number": bool(max_cond > 1e6),
        "flag_amplitude_saturation": bool(sat_frac > 0.01),
    }
    flags["qc_pass"] = not (
        flags["flag_flat_channel"]
        or flags["flag_low_covariance_variability"]
        or flags["flag_extreme_condition_number"]
        or flags["flag_amplitude_saturation"]
    )
    return flags


def shuffle_null_control(
    labels: np.ndarray, num_states: int, n_shuffles: int = 200, seed: int = 0
) -> dict:
    """Permutation null control for temporal structure.

    Shuffling the state sequence destroys all temporal order while
    preserving the marginal state occupancy exactly. If the real
    entropy rate is indistinguishable from the shuffled distribution,
    the trajectory carries no Markov structure at this granularity and
    the transition matrix is a description of the marginal, not of
    dynamics.

    This is the G4/G5 specificity + confound control for the
    experiment: it separates "there is temporal structure" from
    "some states are simply more common".

    Returns the observed entropy rate, the shuffled null mean/std, a
    z-score, and an empirical one-sided p-value (fraction of shuffles
    with entropy rate at or below the observed value; low entropy rate
    means MORE structure, so the test is one-sided below).
    """
    from neurospine.dynamics import entropy_rate, estimate_transition_matrix

    observed_T = estimate_transition_matrix(
        labels, num_states=num_states, laplace=1.0 / 1024
    )
    observed_h = entropy_rate(observed_T)

    rng = np.random.default_rng(seed)
    null_h = np.empty(n_shuffles)
    perm = np.array(labels, dtype=int)
    for i in range(n_shuffles):
        rng.shuffle(perm)
        T_null = estimate_transition_matrix(
            perm, num_states=num_states, laplace=1.0 / 1024
        )
        null_h[i] = entropy_rate(T_null)

    mu, sd = float(null_h.mean()), float(null_h.std(ddof=1))
    z = (observed_h - mu) / sd if sd > 0 else 0.0
    p_below = float((null_h <= observed_h).sum() + 1) / (n_shuffles + 1)
    return {
        "observed_entropy_rate": float(observed_h),
        "null_mean_entropy_rate": mu,
        "null_std_entropy_rate": sd,
        "z_score": float(z),
        "p_value_one_sided_below": p_below,
        "n_shuffles": int(n_shuffles),
        "max_possible_entropy_rate": float(np.log(num_states)),
        "verdict": (
            "temporal structure present"
            if p_below < 0.05
            else "no temporal structure detected (entropy rate "
                 "indistinguishable from shuffled null)"
        ),
    }


def run(subject: int, num_prototypes: int, out_dir: Path) -> dict:
    print(f"[eegbci] loading subject {subject} runs 4 + 6")
    epochs = load_epochs(subject)
    print(f"[eegbci] {epochs.shape[0]} epochs, {epochs.shape[1]} channels, "
          f"{epochs.shape[2]} samples/epoch")

    print("[eegbci] computing per-epoch SPD covariances")
    covs = epoch_covariances(epochs)
    print(f"[eegbci] covs shape {covs.shape}")

    print("[eegbci] running recording quality control")
    qc = quality_control(epochs, covs)
    print(f"[eegbci] qc_pass={qc['qc_pass']} "
          f"median_step={qc['median_consecutive_airm_step']:.4f} "
          f"max_cond={qc['max_condition_number']:.3e}")

    print(f"[eegbci] building {num_prototypes}-prototype AIRM library")
    prototypes, labels = build_prototype_library(covs, k=num_prototypes)
    print(f"[eegbci] state sequence length {len(labels)}, "
          f"prototypes touched {len(set(labels.tolist()))}")

    print("[eegbci] estimating transition matrix and summary")
    summary = summarize_trajectory(labels, num_states=num_prototypes, k_metastable=2)

    print("[eegbci] running shuffle null control (200 permutations)")
    null_control = shuffle_null_control(labels, num_prototypes, n_shuffles=200)
    print(f"[eegbci] null control verdict: {null_control['verdict']}")

    # Numerical identity checks (real-data G14):
    from neurospine.dynamics import estimate_transition_matrix
    T = estimate_transition_matrix(labels, num_states=num_prototypes, laplace=1.0 / 1024)
    row_sums_ok = bool(np.allclose(T.sum(axis=1), 1.0, atol=1e-9))
    pi = summary.stationary_distribution
    stationarity_ok = bool(np.allclose(pi @ T, pi, atol=1e-6))

    out_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "subject": int(subject),
        "n_epochs": int(epochs.shape[0]),
        "n_channels": int(epochs.shape[1]),
        "num_prototypes": int(num_prototypes),
        "stationary_distribution": pi.tolist(),
        "stationary_entropy_nats": float(summary.stationary_entropy),
        "entropy_rate_nats_per_step": float(summary.entropy_rate),
        "spectral_gap": float(summary.spectral_gap),
        "effective_dimension": float(summary.effective_dimension),
        "metastable_labels": summary.metastable_labels.tolist(),
        "row_stochasticity_check": row_sums_ok,
        "stationarity_check": stationarity_ok,
        "shuffle_null_control": null_control,
        "quality_control": qc,
    }

    out_path = out_dir / f"summary_subject-{subject:03d}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"[eegbci] wrote {out_path}")
    print(json.dumps(
        {k: v for k, v in result.items() if k not in
         ("stationary_distribution", "metastable_labels")},
        indent=2,
    ))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--subject", type=int, default=1,
                        help="PhysioNet EEG-BCI subject id (1..109)")
    parser.add_argument("--prototypes", type=int, default=6,
                        help="number of AIRM prototypes for discretization")
    parser.add_argument("--out-dir", type=Path,
                        default=Path(__file__).parent / "results")
    args = parser.parse_args()
    run(args.subject, args.prototypes, args.out_dir)


if __name__ == "__main__":
    main()
