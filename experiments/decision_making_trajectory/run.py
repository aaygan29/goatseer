"""Within-trial state-trajectory decoding of perceptual choice (ds002739).

ADR-018 pivoted the trajectory apparatus (neurospine.behavior,
neurospine.discretize) away from motor imagery (a static contrast, null
result) toward tasks whose discriminative signal is temporal. Sleep staging
(experiments/sleep_transition_decoding) confirmed the apparatus works when
the physiology is temporal (McNemar p=1.18e-13). Decision-making with
evidence accumulation is the other canonical temporal case named in ADR-018:
Rungratsameetaweemana et al. show that within-trial neural dynamics track the
accumulation-to-threshold process, so the WITHIN-TRIAL sequence of brain
states should carry information about the eventual choice beyond a
memoryless summary of the same trial.

Data: OpenNeuro ds002739 (simultaneous EEG-fMRI random-dot-motion perceptual
decision task; originally ds001512, reuploaded for privacy). This experiment
uses EEG only. Each subject has ~160 trials/run with dot direction, choice,
accuracy, confidence, RT and event onsets in EEG_events_sub-XX_run-YY.mat;
raw preprocessed EEG in EEG_data_sub-XX_run-YY.mat (fs=1000 Hz after the
dataset's own gradient/BCG/EOG cleaning, see data/raw/ds002739/README).

Pipeline (per subject):
  1. Load preprocessed EEG + events for one run.
  2. Drop excluded trials (dataset-provided excludedtrials index).
  3. Epoch stimulus-locked: [tstim, tstim + WIN_S] (fixed window; RT varies
     but a fixed post-stimulus window keeps sub-window features comparable
     across trials, matching the sleep experiment's fixed-epoch design).
  4. Split each trial window into N_SUBWIN equal sub-windows; compute a
     per-sub-window feature (theta/alpha/beta band power per channel,
     robust-scaled).
  5. K-MEANS discretize sub-window features into a shared, per-subject,
     UNSUPERVISED state alphabet (no labels used) -> one within-trial state
     sequence per trial.
  6. Label = choice (left/right). neurospine.behavior.analyze_within_subject
     does the rest: per-subject train/test split, class-conditional Markov
     model vs occupancy (0th-order) ablation, per-subject shuffle null,
     group verdict. trajectory_gain = markov_accuracy - occupancy_accuracy
     is the key readout; a positive, null-clearing gain is the claim.

No cross-subject fingerprinting. No leakage: the K-means state alphabet is
unsupervised (no label use), and the Markov/occupancy models and their nulls
are fit on each subject's TRAIN trials only (neurospine.behavior).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "instrument" / "src"))

from neurospine.behavior import analyze_within_subject  # noqa: E402

FS = 1000.0
WIN_S = 1.0            # stimulus-locked analysis window
N_SUBWIN = 5           # sub-windows per trial -> sequence length 5
BANDS = [("theta", 4, 8), ("alpha", 8, 13), ("beta", 13, 30)]
N_STATES = 4


def band_power(x, fs, lo, hi):
    """Welch relative band power for a 1D window."""
    from scipy.signal import welch
    nper = min(len(x), int(fs))
    if nper < 8:
        return 0.0
    f, p = welch(x, fs=fs, nperseg=nper)
    total = np.trapz(p, f) + 1e-12
    band = np.trapz(p[(f >= lo) & (f < hi)], f[(f >= lo) & (f < hi)])
    return float(band / total)


def load_events(events_path):
    import scipy.io as sio
    e = sio.loadmat(events_path)
    tstim = e["tstim"].flatten().astype(int)
    choice = e["choice"].flatten().astype(int)
    accuracy = e["accuracy"].flatten().astype(int)
    excluded = set(e["excludedtrials"].flatten().astype(int).tolist())
    return tstim, choice, accuracy, excluded


def load_eeg(data_path):
    """Return (data: n_channels x n_samples, fs).

    The struct's ``Y`` field is the EEG matrix; ``fd`` is the sampling rate
    IT is actually stored at (the dataset's own downsampled rate, matching
    the event onsets in EEG_events_*.mat), while ``fs`` is the original
    pre-downsampling acquisition rate and ``fsr`` = fs/fd the decimation
    factor. Verified against event onsets: max(tstim) is on the same scale
    as Y.shape[1] only when using fd, not fs (fd=1000 Hz here).
    """
    import scipy.io as sio
    d = sio.loadmat(data_path, simplify_cells=True)
    eeg = d["EEGdata"]
    data = np.asarray(eeg["Y"], dtype=float)
    fd = float(np.asarray(eeg["fd"]).flatten()[0])
    return data, fd


def trial_sequence(data, fs, t0, win_s, n_subwin):
    """(n_subwin, n_channels * n_bands) feature sequence for one trial."""
    win = int(round(win_s * fs))
    sub = win // n_subwin
    end = t0 + win
    if end > data.shape[1] or t0 < 0:
        return None
    seq = []
    for i in range(n_subwin):
        s0, s1 = t0 + i * sub, t0 + (i + 1) * sub
        seg = data[:, s0:s1]
        feats = []
        for ch in range(seg.shape[0]):
            for _, lo, hi in BANDS:
                feats.append(band_power(seg[ch], fs, lo, hi))
        seq.append(feats)
    return np.array(seq)


def load_subject_trials(subj, root, run="01"):
    """Return (list of (n_subwin, n_feat) sequences, list of 'left'/'right')
    for one subject's valid trials in one run."""
    eeg_dir = root / f"sub-{subj}" / "EEG"
    data_path = eeg_dir / f"EEG_data_sub-{subj}_run-{run}.mat"
    events_path = eeg_dir / f"EEG_events_sub-{subj}_run-{run}.mat"
    tstim, choice, accuracy, excluded = load_events(events_path)
    data, fs = load_eeg(data_path)

    seqs, labels = [], []
    for i, t0 in enumerate(tstim):
        trial_no = i + 1  # excludedtrials indices are 1-based (MATLAB)
        if trial_no in excluded:
            continue
        seq = trial_sequence(data, fs, int(t0), WIN_S, N_SUBWIN)
        if seq is None or not np.all(np.isfinite(seq)):
            continue
        seqs.append(seq)
        labels.append("left" if choice[i] == 1 else "right")
    return seqs, labels


def discretize_subject(seqs, n_states, seed=0):
    """Unsupervised k-means over ALL sub-window feature vectors of a
    subject (no labels used), robust-scaled first. Returns one integer state
    sequence per trial."""
    from sklearn.cluster import KMeans
    stacked = np.concatenate(seqs, axis=0)
    med = np.median(stacked, axis=0)
    iqr = np.subtract(*np.percentile(stacked, [75, 25], axis=0))
    iqr[iqr == 0] = 1.0
    scaled = (stacked - med) / iqr

    km = KMeans(n_clusters=n_states, n_init=10, random_state=seed).fit(scaled)
    labels_flat = km.labels_
    out, pos = [], 0
    for seq in seqs:
        n = len(seq)
        out.append(labels_flat[pos:pos + n].astype(int))
        pos += n
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", type=Path,
                    default=REPO_ROOT / "data" / "raw" / "ds002739")
    ap.add_argument("--subjects", nargs="+",
                    default=["01", "02", "03", "04"])
    ap.add_argument("--run", default="01")
    ap.add_argument("--n-states", type=int, default=N_STATES)
    ap.add_argument("--n-permutations", type=int, default=200)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", type=Path,
                    default=Path(__file__).parent / "results" / "decision_trajectory.json")
    args = ap.parse_args()

    sequences, labels, subject_ids = [], [], []
    per_subject_counts = {}
    for subj in args.subjects:
        try:
            seqs, labs = load_subject_trials(subj, args.data_root, args.run)
        except FileNotFoundError as exc:
            print(f"[sub-{subj}] SKIPPED (missing data): {exc}")
            continue
        if len(seqs) < 8 or len(set(labs)) < 2:
            print(f"[sub-{subj}] SKIPPED: {len(seqs)} usable trials, "
                  f"classes={set(labs)}")
            continue
        states = discretize_subject(seqs, args.n_states, seed=args.seed)
        n_left = sum(1 for lb in labs if lb == "left")
        per_subject_counts[subj] = {"n_trials": len(labs), "n_left": n_left,
                                     "n_right": len(labs) - n_left}
        print(f"[sub-{subj}] {len(labs)} trials (left={n_left}, "
              f"right={len(labs) - n_left})")
        sequences.extend(states)
        labels.extend(labs)
        subject_ids.extend([subj] * len(labs))

    if len(set(subject_ids)) < 1:
        raise SystemExit("no usable subjects; check data-root and event files")

    result = analyze_within_subject(
        sequences, labels, subject_ids,
        n_states=args.n_states,
        n_permutations=args.n_permutations,
        seed=args.seed,
    )
    result["per_subject_trial_counts"] = per_subject_counts
    result["config"] = {
        "win_s": WIN_S, "n_subwin": N_SUBWIN, "n_states": args.n_states,
        "bands": [b[0] for b in BANDS], "run": args.run,
        "subjects_requested": args.subjects,
    }

    print("\nDECISION-MAKING WITHIN-TRIAL TRAJECTORY DECODING:")
    print(f"  n_subjects used:            {result['n_subjects']}")
    print(f"  mean heldout accuracy:      {result['mean_heldout_accuracy']:.3f}")
    print(f"  mean trajectory gain:       {result['mean_trajectory_gain']:+.3f}")
    print(f"  subjects significant:       {result['n_subjects_significant']}/"
          f"{result['n_subjects']} (group binomial p={result['group_binomial_p']:.4f})")
    for s, r in result["per_subject"].items():
        print(f"    sub-{s}: acc={r['heldout_accuracy']:.3f} "
              f"occ={r['occupancy_accuracy']:.3f} gain={r['trajectory_gain']:+.3f} "
              f"p={r['p_value']:.4f}")
    print(f"  VERDICT: {result['verdict']}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
