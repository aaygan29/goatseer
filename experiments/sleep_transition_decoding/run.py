"""Sleep-stage transition decoding: the trajectory model in its right regime.

ADR-018 pivoted the trajectory apparatus off motor imagery (a static ERD/ERS
contrast where transitions carry nothing) toward tasks whose signal IS
temporal. Sleep staging is the canonical such task: stage sequences are
strongly constrained (W -> N1 -> N2 -> N3 -> REM cycling; you rarely jump
W -> N3), so a decoder that uses the stage-TRANSITION structure should beat a
memoryless per-epoch classifier. That is the mirror image of the motor-
imagery result, and the positive control that validates the apparatus.

Per recording, each 30s epoch becomes a per-band relative-power feature
vector (two EEG channels). A `SupervisedSequenceDecoder` (per-stage Gaussian
emissions + a stage-transition matrix) is fit leave-one-recording-out and the
held-out night is decoded WITH transitions (Viterbi) versus WITHOUT
(per-epoch argmax). If accuracy-with > accuracy-without across recordings, the
transition structure carries signal.

Data: PhysioNet Sleep-EDF Expanded (scripts/fetch_sleep_edfx_subset.sh).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "instrument" / "src"))

from neurospine.sequence_decode import (  # noqa: E402
    SupervisedSequenceDecoder,
    transition_gain,
)

EPOCH_S = 30.0
BANDS = [("delta", 0.5, 4), ("theta", 4, 8), ("alpha", 8, 13),
         ("sigma", 11, 16), ("beta", 16, 30)]
STAGE_MAP = {"Sleep stage W": "W", "Sleep stage 1": "N1", "Sleep stage 2": "N2",
             "Sleep stage 3": "N3", "Sleep stage 4": "N3", "Sleep stage R": "REM"}
EEG_HINTS = ["Fpz-Cz", "Pz-Oz"]


def band_features(x, sfreq):
    from scipy.signal import welch
    f, p = welch(x, fs=sfreq, nperseg=min(len(x), int(sfreq * 4)))
    total = np.trapz(p, f) + 1e-12
    return [np.trapz(p[(f >= lo) & (f < hi)], f[(f >= lo) & (f < hi)]) / total
            for _, lo, hi in BANDS]


def load_recording(psg_path, hyp_path):
    """Return (X, y): ordered per-epoch features and stage labels."""
    import mne
    raw = mne.io.read_raw_edf(psg_path, preload=True, verbose="ERROR")
    ann = mne.read_annotations(hyp_path)
    raw.set_annotations(ann, verbose="ERROR")
    picks = [c for c in raw.ch_names if any(h.lower() in c.lower() for h in EEG_HINTS)]
    if not picks:
        picks = raw.ch_names[:2]
    raw.pick(picks, verbose="ERROR")
    raw.filter(0.3, 30.0, verbose="ERROR")
    sfreq = float(raw.info["sfreq"])
    step = int(EPOCH_S * sfreq)
    data = raw.get_data()

    X, y = [], []
    for a in raw.annotations:
        stage = STAGE_MAP.get(a["description"])
        if stage is None:
            continue
        t0 = int(a["onset"] * sfreq)
        t1 = int((a["onset"] + a["duration"]) * sfreq)
        for s in range(t0, t1 - step + 1, step):
            seg = data[:, s:s + step]
            if seg.shape[1] < step or np.any(np.isnan(seg)):
                continue
            feats = []
            for ch in range(seg.shape[0]):
                feats += band_features(seg[ch], sfreq)
            X.append(feats)
            y.append(stage)
    X = np.array(X)
    if len(X) == 0:
        return None
    # Within-recording z-score (leakage-free: each night by its own stats).
    X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-9)
    return X, np.array(y)


def find_pairs(root: Path):
    pairs = []
    for psg in sorted(root.glob("*-PSG.edf")):
        stem = psg.stem[:6]
        hyps = sorted(root.glob(f"{stem}*-Hypnogram.edf"))
        if hyps:
            pairs.append((psg, hyps[0]))
    return pairs


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", type=Path,
                    default=REPO_ROOT / "data" / "raw" / "sleep_edfx")
    ap.add_argument("--out", type=Path,
                    default=Path(__file__).parent / "results" / "sleep_transition.json")
    args = ap.parse_args()

    pairs = find_pairs(args.data_root)
    if len(pairs) < 2:
        raise SystemExit(f"need >=2 recordings under {args.data_root}; run "
                         "scripts/fetch_sleep_edfx_subset.sh")

    recs = []
    for psg, hyp in pairs:
        r = load_recording(psg, hyp)
        if r is not None and len(set(r[1])) >= 2:
            recs.append((psg.stem[:6], r[0], r[1]))
            print(f"[{psg.stem[:6]}] {len(r[1])} epochs, stages {sorted(set(r[1]))}")
    if len(recs) < 2:
        raise SystemExit("fewer than 2 usable recordings")

    # Leave-one-recording-out. Also accumulate paired per-epoch outcomes for
    # a McNemar test: b = transitions fixed it, c = transitions broke it.
    fold = {}
    b = c = 0
    for i in range(len(recs)):
        name, Xte, yte = recs[i]
        Xtr = [recs[j][1] for j in range(len(recs)) if j != i]
        ytr = [recs[j][2] for j in range(len(recs)) if j != i]
        dec = SupervisedSequenceDecoder.fit(Xtr, ytr)
        g = transition_gain(dec, [Xte], [yte])
        fold[name] = g
        pw = dec.decode(Xte, use_transitions=True)
        pn = dec.decode(Xte, use_transitions=False)
        for yi, w, n in zip(yte, pw, pn):
            cw, cn = (w == yi), (n == yi)
            b += int(cw and not cn)
            c += int(cn and not cw)
        print(f"  fold {name}: with-transitions {g['accuracy_with_transitions']:.3f}  "
              f"without {g['accuracy_without_transitions']:.3f}  "
              f"gain {g['transition_gain']:+.3f}")

    from scipy.stats import binomtest
    mcnemar_p = float(binomtest(b, b + c, 0.5).pvalue) if (b + c) > 0 else 1.0

    gains = [g["transition_gain"] for g in fold.values()]
    n_pos = sum(1 for x in gains if x > 0)
    n = len(gains)
    from math import comb
    sign_p = float(sum(comb(n, k) * 0.5**n for k in range(n_pos, n + 1)))
    summary = {
        "n_recordings": n,
        "mean_accuracy_with_transitions":
            float(np.mean([g["accuracy_with_transitions"] for g in fold.values()])),
        "mean_accuracy_without_transitions":
            float(np.mean([g["accuracy_without_transitions"] for g in fold.values()])),
        "mean_transition_gain": float(np.mean(gains)),
        "folds_with_positive_gain": n_pos,
        "sign_test_p": sign_p,
        "mcnemar": {"transitions_fixed": b, "transitions_broke": c,
                    "p_value": mcnemar_p},
        "per_fold": fold,
    }
    print("\nSLEEP-STAGE TRANSITION DECODING (leave-one-recording-out):")
    print(f"  accuracy WITH transitions:    {summary['mean_accuracy_with_transitions']:.3f}")
    print(f"  accuracy WITHOUT transitions: {summary['mean_accuracy_without_transitions']:.3f}")
    print(f"  mean transition gain:         {summary['mean_transition_gain']:+.3f}")
    print(f"  folds with positive gain:     {n_pos}/{n} (sign-test p={sign_p:.4f})")
    print(f"  McNemar (paired epochs):      transitions fixed {b}, broke {c}, "
          f"p={mcnemar_p:.2e}")
    if summary["mean_transition_gain"] > 0:
        print("  VERDICT: temporal transition structure carries decodable signal.")
        print("  The trajectory model earns its keep here, unlike motor imagery.")
    else:
        print("  VERDICT: transitions did not help even on sleep (unexpected; investigate).")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
