"""Within-subject behavior decoding from connectome-state trajectories.

The cross-subject experiment (experiments/connectome_behavior_prediction)
returned an honest NULL: connectome-state trajectories did not predict motor
imagery ACROSS subjects, and the transitions added nothing over occupancy.
The obvious follow-up: is the signal there WITHIN a subject, where the model
does not have to generalize across anatomy and electrode geometry?

This runs the same covariance -> AIRM-prototype -> state pipeline on PhysioNet
EEG-BCI, but decodes per subject: for each subject, a subject-specific state
library is learned and their trials are split train/test, then the Markov
model + occupancy baseline + a per-subject shuffle null are computed. Results
are aggregated over the cohort (how many subjects individually beat their own
null, a group binomial p, mean accuracy, mean trajectory gain).

Data is fetched through the shared neurospine.io layer.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "instrument" / "src"))

from neurospine.behavior import analyze_within_subject  # noqa: E402
from neurospine.io import fetch_eegbci  # noqa: E402
from neurospine.manifold import airm_distance, airm_frechet_mean  # noqa: E402

SENSORIMOTOR = ["C3", "C4", "Cz", "Fz", "Pz"]


def _cov(x, ridge=1e-3):
    c = (x @ x.T) / (x.shape[1] - 1)
    c = 0.5 * (c + c.T)
    return c + ridge * np.eye(c.shape[0]) * np.trace(c) / c.shape[0]


def load_trials(subject, runs=(4, 8), trial_s=4.0, window_s=1.0):
    """Return (list of (n_windows, ch, ch) covariance trajectories, labels)
    for one subject's T1/T2 trials."""
    import mne
    from mne.datasets import eegbci

    files = fetch_eegbci([subject], runs=runs)[subject]
    raws = [mne.io.read_raw_edf(f, preload=True, verbose="ERROR") for f in files]
    raw = mne.concatenate_raws(raws)
    eegbci.standardize(raw)
    raw.set_montage("standard_1020", on_missing="ignore")
    raw.pick(SENSORIMOTOR, verbose="ERROR")
    raw.set_eeg_reference("average", projection=False, verbose="ERROR")
    raw.filter(8.0, 30.0, fir_design="firwin", verbose="ERROR")

    events, event_id = mne.events_from_annotations(raw, verbose="ERROR")
    inv = {v: k for k, v in event_id.items()}
    sfreq = float(raw.info["sfreq"])
    ts, ws = int(round(trial_s * sfreq)), int(round(window_s * sfreq))
    data = raw.get_data()
    n = data.shape[1]

    covs, labels = [], []
    for sample, _, code in events:
        lab = str(inv.get(int(code), ""))
        if lab not in {"T1", "T2"}:
            continue
        end = int(sample) + ts
        if end > n:
            continue
        trial = data[:, int(sample):end]
        seq = [_cov(trial[:, i:i + ws]) for i in range(0, ts, ws)]
        covs.append(np.stack(seq))
        labels.append(lab)
    return covs, labels


def build_prototypes(windows, k, seed=0, iters=10):
    """k-medoids-like AIRM prototype library with Frechet-mean updates."""
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(windows), size=min(k, len(windows)), replace=False)
    protos = [windows[i] for i in idx]
    for _ in range(iters):
        assign = [int(np.argmin([airm_distance(w, p) for p in protos]))
                  for w in windows]
        for j in range(len(protos)):
            members = [windows[i] for i in range(len(windows)) if assign[i] == j]
            if members:
                protos[j] = airm_frechet_mean(members, max_iter=20)
    return protos


def discretize(covs, protos):
    return [np.array([int(np.argmin([airm_distance(c, p) for p in protos]))
                      for c in trial], dtype=int) for trial in covs]


def trial_mean_cov(trial):
    """Represent a trial by the AIRM Frechet mean of its window covariances."""
    return airm_frechet_mean(list(trial), max_iter=20)


def mdm_control(trial_covs, labels, train_frac=0.6, seed=0):
    """Riemannian minimum-distance-to-mean POSITIVE CONTROL, per subject.

    Classifies each trial's mean covariance by the nearest per-class AIRM
    Frechet mean (Barachant et al. 2012). This is the canonical decoder for
    left-vs-right motor imagery and tells us whether the discriminative signal
    is present in the covariance geometry at all, independent of the
    state-trajectory representation. Returns held-out accuracy or None.
    """
    rng = np.random.default_rng(seed)
    classes = sorted(set(labels))
    by_c = {c: [i for i, y in enumerate(labels) if y == c] for c in classes}
    if any(len(v) < 2 for v in by_c.values()):
        return None
    tr, te = [], []
    for c, idxs in by_c.items():
        idxs = list(idxs); rng.shuffle(idxs)
        k = max(1, min(len(idxs) - 1, int(round(train_frac * len(idxs)))))
        tr += idxs[:k]; te += idxs[k:]
    means = {c: airm_frechet_mean([trial_covs[i] for i in tr if labels[i] == c],
                                  max_iter=20) for c in classes}
    correct = 0
    for i in te:
        d = {c: airm_distance(trial_covs[i], means[c]) for c in classes}
        pred = min(d, key=d.get)
        correct += int(pred == labels[i])
    return correct / len(te)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--subjects", nargs="+", type=int, default=[1, 2, 3, 4, 5, 6, 7, 8])
    ap.add_argument("--states", type=int, default=5)
    ap.add_argument("--n-permutations", type=int, default=200)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", type=Path,
                    default=Path(__file__).parent / "results" / "within_subject.json")
    args = ap.parse_args()

    all_seq, all_lab, all_subj = [], [], []
    mdm_accs = {}
    for s in args.subjects:
        covs, labels = load_trials(s)
        if len({l for l in labels}) < 2:
            print(f"[subj {s}] skipped: <2 classes")
            continue
        # Subject-specific state library (unsupervised, on this subject's
        # windows; the LABELED train/test split happens inside the engine).
        windows = np.concatenate(covs, axis=0)
        protos = build_prototypes(list(windows), k=args.states, seed=args.seed)
        seqs = discretize(covs, protos)
        all_seq.extend(seqs)
        all_lab.extend(labels)
        all_subj.extend([s] * len(labels))
        # Positive control on the same trials, same split fraction.
        tmeans = [trial_mean_cov(t) for t in covs]
        acc = mdm_control(tmeans, labels, seed=args.seed)
        if acc is not None:
            mdm_accs[str(s)] = float(acc)
        print(f"[subj {s}] {len(labels)} T1/T2 trials -> states; "
              f"MDM control acc {acc:.3f}")

    result = analyze_within_subject(
        all_seq, all_lab, all_subj, n_states=args.states,
        n_permutations=args.n_permutations, seed=args.seed,
    )
    mdm_mean = float(np.mean(list(mdm_accs.values()))) if mdm_accs else float("nan")
    result["mdm_positive_control"] = {
        "per_subject_accuracy": mdm_accs,
        "mean_accuracy": mdm_mean,
        "note": ("Riemannian minimum-distance-to-mean on the raw covariances "
                 "(Barachant et al. 2012). If MDM decodes but the "
                 "state-trajectory model does not, the discriminative signal "
                 "is in the covariance geometry and the discretization "
                 "discards it."),
    }

    print("\nWITHIN-SUBJECT DECODING (PhysioNet EEG-BCI, T1 vs T2):")
    print(f"  subjects analyzed:            {result['n_subjects']}")
    print(f"  mean held-out accuracy:       {result['mean_heldout_accuracy']:.3f}")
    print(f"  subjects beating own null:    {result['n_subjects_significant']}/{result['n_subjects']}")
    print(f"  group binomial p:             {result['group_binomial_p']:.4f}")
    print(f"  mean trajectory gain:         {result['mean_trajectory_gain']:.3f}")
    print(f"  MDM positive-control acc:     {mdm_mean:.3f} (raw covariance decoder)")
    print(f"  VERDICT: {result['verdict']}")
    if mdm_mean > 0.6 and result["mean_heldout_accuracy"] < 0.6:
        print("  INTERPRETATION: the signal IS present within subject (MDM "
              "decodes it), but the connectome-state-trajectory representation "
              "discards it. The discretization, not the data, is the limit.")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
