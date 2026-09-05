"""Connectome-state to behavior prediction on public EEG-BCI data.

Pipeline:
1. Load PhysioNet EEG-BCI motor-imagery data (runs 4 and 8 by default).
2. Build short trial-wise covariance trajectories on sensorimotor channels.
3. Learn an AIRM prototype library and discretize each trial into a
   connectome-state sequence.
4. Fit a class-conditional Markov model from state sequences to behavior
   labels (T1/T2).
5. Evaluate held-out accuracy on a subject-disjoint split and compare
   against a label-shuffle null.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "instrument" / "src"))

from neurospine.behavior import (
    evaluate_behavior_markov_model,
    fit_behavior_markov_model,
)
from neurospine.manifold import airm_distance, airm_frechet_mean

SENSORIMOTOR_CHANNELS = ["C3", "C4", "Cz", "Fz", "Pz"]


def _covariance(x: np.ndarray, ridge: float = 1e-3) -> np.ndarray:
    c = (x @ x.T) / (x.shape[1] - 1)
    c = 0.5 * (c + c.T)
    c += ridge * np.eye(c.shape[0]) * np.trace(c) / c.shape[0]
    return c


def load_trial_covariances(
    subject: int,
    runs: tuple[int, ...] = (4, 8),
    trial_seconds: float = 4.0,
    window_seconds: float = 1.0,
) -> tuple[list[np.ndarray], list[str]]:
    """Return trial-level covariance trajectories and T1/T2 labels."""
    import mne
    from mne.datasets import eegbci

    files = eegbci.load_data(subject, runs=list(runs), update_path=True, verbose="ERROR")
    raws = [mne.io.read_raw_edf(f, preload=True, verbose="ERROR") for f in files]
    raw = mne.concatenate_raws(raws)
    eegbci.standardize(raw)
    raw.set_montage("standard_1020", on_missing="ignore")
    raw.pick(SENSORIMOTOR_CHANNELS, verbose="ERROR")
    raw.set_eeg_reference("average", projection=False, verbose="ERROR")
    raw.filter(8.0, 30.0, fir_design="firwin", verbose="ERROR")

    events, event_id = mne.events_from_annotations(raw, verbose="ERROR")
    inv = {v: k for k, v in event_id.items()}

    sfreq = float(raw.info["sfreq"])
    trial_samples = round(trial_seconds * sfreq)
    window_samples = round(window_seconds * sfreq)
    if trial_samples % window_samples != 0:
        raise ValueError("trial_seconds must be an integer multiple of window_seconds")

    data = raw.get_data()
    n_total = data.shape[1]

    trial_covs: list[np.ndarray] = []
    labels: list[str] = []
    for sample, _, code in events:
        label = str(inv.get(int(code), ""))
        if label not in {"T1", "T2"}:
            continue
        end = int(sample) + trial_samples
        if end > n_total:
            continue
        trial = data[:, int(sample):end]
        seq = []
        for i in range(0, trial_samples, window_samples):
            w = trial[:, i:i + window_samples]
            seq.append(_covariance(w))
        trial_covs.append(np.stack(seq, axis=0))
        labels.append(label)

    if not trial_covs:
        raise RuntimeError("no T1/T2 trials extracted from EEG annotations")
    return trial_covs, labels


def discretize_trials(trial_covs: list[np.ndarray], prototypes: np.ndarray) -> list[np.ndarray]:
    """Map each covariance in each trial to its nearest AIRM prototype."""
    out: list[np.ndarray] = []
    for trial in trial_covs:
        states = []
        for cov in trial:
            d = [airm_distance(cov, p) for p in prototypes]
            states.append(int(np.argmin(d)))
        out.append(np.array(states, dtype=int))
    return out


def build_prototype_library(
    covs: np.ndarray, k: int = 6, seed: int = 0, max_iter: int = 10
) -> tuple[np.ndarray, np.ndarray]:
    """K-medoids-like prototype library on the AIRM manifold."""
    n = covs.shape[0]
    if k < 2:
        raise ValueError(f"k must be >= 2; got {k}")
    if k > n:
        raise ValueError(f"k={k} exceeds available covariance windows n={n}")
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


def subject_disjoint_split(
    items: list[np.ndarray],
    labels: list[str],
    subjects: list[int],
    train_frac: float,
    seed: int,
) -> tuple[list[np.ndarray], list[str], list[np.ndarray], list[str], list[int], list[int]]:
    if not (0.0 < train_frac < 1.0):
        raise ValueError(f"train_frac must be in (0, 1); got {train_frac}")
    rng = np.random.default_rng(seed)
    unique_subjects = sorted(set(subjects))
    if len(unique_subjects) < 2:
        raise ValueError("need at least 2 subjects for subject-disjoint train/test split")
    rng.shuffle(unique_subjects)

    n_train_subjects = max(1, round(train_frac * len(unique_subjects)))
    n_train_subjects = min(n_train_subjects, len(unique_subjects) - 1)
    train_subjects = sorted(unique_subjects[:n_train_subjects])
    test_subjects = sorted(unique_subjects[n_train_subjects:])

    train_set = set(train_subjects)
    train_idx = [i for i, s in enumerate(subjects) if s in train_set]
    test_idx = [i for i, s in enumerate(subjects) if s not in train_set]
    train_idx.sort()
    test_idx.sort()

    x_tr = [items[i] for i in train_idx]
    y_tr = [labels[i] for i in train_idx]
    x_te = [items[i] for i in test_idx]
    y_te = [labels[i] for i in test_idx]
    if len(set(y_tr)) < 2 or len(set(y_te)) < 2:
        raise ValueError(
            "subject split removed one behavior class from train or test; "
            "add more subjects or change split seed"
        )
    return x_tr, y_tr, x_te, y_te, train_subjects, test_subjects


def run(
    subjects: list[int],
    n_states: int,
    n_permutations: int,
    train_frac: float,
    seed: int,
) -> dict:
    if n_permutations < 1:
        raise ValueError(f"n_permutations must be >= 1; got {n_permutations}")
    trial_covs_all: list[np.ndarray] = []
    labels_all: list[str] = []
    subject_ids: list[int] = []

    for subject in subjects:
        tc, ys = load_trial_covariances(subject)
        trial_covs_all.extend(tc)
        labels_all.extend(ys)
        subject_ids.extend([subject] * len(ys))

    (
        trial_covs_tr,
        y_tr,
        trial_covs_te,
        y_te,
        train_subjects,
        test_subjects,
    ) = subject_disjoint_split(
        trial_covs_all, labels_all, subject_ids, train_frac, seed
    )

    # Learn shared connectome-state library from training trial windows only.
    windows = np.concatenate(trial_covs_tr, axis=0)
    prototypes, _ = build_prototype_library(windows, k=n_states, seed=seed)

    x_tr = discretize_trials(trial_covs_tr, prototypes)
    x_te = discretize_trials(trial_covs_te, prototypes)

    model = fit_behavior_markov_model(x_tr, y_tr, n_states=n_states)
    observed = evaluate_behavior_markov_model(model, x_te, y_te)

    # Shuffle-label null: keep neural sequences fixed, randomize training labels.
    rng = np.random.default_rng(seed)
    null_acc = []
    y_perm = np.array(y_tr, dtype=object)
    for _ in range(n_permutations):
        rng.shuffle(y_perm)
        m = fit_behavior_markov_model(x_tr, y_perm.tolist(), n_states=n_states)
        null_acc.append(evaluate_behavior_markov_model(m, x_te, y_te)["accuracy"])
    null_acc_arr = np.array(null_acc, dtype=float)
    p = float((np.sum(null_acc_arr >= observed["accuracy"]) + 1) / (len(null_acc_arr) + 1))

    return {
        "subjects": subjects,
        "n_trials": len(labels_all),
        "n_train": len(y_tr),
        "n_test": len(y_te),
        "labels": sorted(set(labels_all)),
        "train_subjects": train_subjects,
        "test_subjects": test_subjects,
        "n_states": n_states,
        "train_fraction": train_frac,
        "heldout_accuracy": float(observed["accuracy"]),
        "heldout_confusion": observed["confusion"],
        "permutation_null": {
            "n_permutations": n_permutations,
            "mean_accuracy": float(null_acc_arr.mean()),
            "std_accuracy": float(null_acc_arr.std(ddof=1)) if len(null_acc_arr) > 1 else 0.0,
            "p_value_right_tail": p,
            "verdict": (
                "connectome-state trajectories predict behavior above shuffled-label null"
                if p < 0.05
                else "no evidence above shuffled-label null"
            ),
        },
        "subject_trial_counts": {
            str(s): int(sum(1 for t in subject_ids if t == s)) for s in sorted(set(subject_ids))
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--subjects", nargs="+", type=int, default=[1, 2, 3, 4, 5])
    ap.add_argument("--states", type=int, default=6)
    ap.add_argument("--train-frac", type=float, default=0.7)
    ap.add_argument("--n-permutations", type=int, default=200)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).parent / "results" / "connectome_behavior.json",
    )
    args = ap.parse_args()

    try:
        result = run(
            subjects=args.subjects,
            n_states=args.states,
            n_permutations=args.n_permutations,
            train_frac=args.train_frac,
            seed=args.seed,
        )
    except Exception as exc:
        raise RuntimeError(
            "Failed to run public EEG pipeline. If dataset download is blocked, "
            "upload dataset files into this workspace and rerun."
        ) from exc

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
