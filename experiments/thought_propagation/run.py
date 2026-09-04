"""Anatomical thought-propagation analysis (ADR-013).

Loads the real region connectome, builds the propagation Markov chain,
runs the stimulus-to-behavior chain, and executes the three
preregistered validation checks.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "instrument" / "src"))

from neurospine.propagation import AtlasPropagation, connectome_to_markov  # noqa: E402


def label_agreement(labels_a, labels_b) -> float:
    """Adjusted Rand index between two labelings."""
    from sklearn.metrics import adjusted_rand_score
    return float(adjusted_rand_score(labels_a, labels_b))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--connectome", type=Path,
                    default=Path(__file__).parent / "results" / "connectome.npz")
    ap.add_argument("--threshold", type=float, default=0.0)
    ap.add_argument("--n-shuffles", type=int, default=500)
    ap.add_argument("--out", type=Path,
                    default=Path(__file__).parent / "results" / "propagation.json")
    args = ap.parse_args()

    d = np.load(args.connectome, allow_pickle=True)
    fc, networks, labels = d["fc"], d["networks"], d["labels"]
    # The Schaefer atlas ships a Background label at index 0; the masker
    # extracts only the real parcels, so align networks/labels to FC.
    if len(networks) == fc.shape[0] + 1:
        networks, labels = networks[1:], labels[1:]
    T = connectome_to_markov(fc, threshold=args.threshold)
    atlas = AtlasPropagation(transition=T, networks=networks, labels=labels)

    # Encode networks as integers for clustering comparison.
    net_names = sorted(set(networks.tolist()))
    net_id = {n: i for i, n in enumerate(net_names)}
    yeo = np.array([net_id[n] for n in networks])
    k = len(net_names)

    # ---- Validation 1: PCCA communities recover the Yeo networks ----
    pcca = atlas.metastable_communities(k)
    ari = label_agreement(yeo, pcca)
    rng = np.random.default_rng(0)
    null_ari = []
    for _ in range(args.n_shuffles):
        perm = rng.permutation(pcca)
        null_ari.append(label_agreement(yeo, perm))
    null_ari = np.array(null_ari)
    ari_p = float((null_ari >= ari).mean())
    ari_p95 = float(np.percentile(null_ari, 95))

    # ---- Validation 2: within-network MFPT < between-network MFPT ----
    from neurospine.dynamics import mean_first_passage_time
    within, between = [], []
    for tgt in range(len(networks)):
        m = mean_first_passage_time(T, tgt)
        for src in range(len(networks)):
            if src == tgt:
                continue
            if networks[src] == networks[tgt]:
                within.append(m[src])
            else:
                between.append(m[src])
    within, between = np.array(within), np.array(between)
    from scipy.stats import mannwhitneyu
    u_stat, u_p = mannwhitneyu(within, between, alternative="less")

    # ---- Validation 3: visual -> motor path through association cortex ----
    chain = atlas.stimulus_to_behavior("Vis", "SomMot")
    q = chain.committor
    # Association networks (not primary sensory/motor).
    assoc = {"DorsAttn", "SalVentAttn", "Cont", "Default", "Limbic"}
    # Rank regions by committor; the "path interior" is the mid-committor
    # band (excluding source ~0 and target ~1). Check which networks
    # dominate the interior.
    interior_mask = (q > 0.2) & (q < 0.8)
    interior_nets = Counter(networks[interior_mask].tolist())
    interior_assoc_frac = (
        sum(v for kk, v in interior_nets.items() if kk in assoc)
        / max(1, sum(interior_nets.values()))
    )

    # The stimulus-to-behavior network sequence: mean committor per
    # network, ordered from source (low) to target (high).
    net_committor = {n: float(q[networks == n].mean()) for n in net_names}
    seq = sorted(net_committor.items(), key=lambda kv: kv[1])

    print("=" * 60)
    print("ANATOMICAL THOUGHT-PROPAGATION VALIDATION")
    print("=" * 60)
    print(f"\n[1] PCCA communities vs Yeo networks (k={k}):")
    print(f"    adjusted Rand index = {ari:.3f}")
    print(f"    shuffle null 95th pct = {ari_p95:.3f}, p = {ari_p:.4f}")
    print(f"    {'PASS' if ari_p < 0.05 else 'FAIL'}: propagation communities "
          f"{'recover' if ari_p < 0.05 else 'do NOT recover'} functional networks")
    print(f"\n[2] within-network vs between-network MFPT:")
    print(f"    within mean {within.mean():.2f}, between mean {between.mean():.2f}")
    print(f"    Mann-Whitney U p (within < between) = {u_p:.2e}")
    print(f"    {'PASS' if u_p < 0.05 else 'FAIL'}: activation reaches same-network "
          f"regions {'faster' if u_p < 0.05 else 'NOT faster'}")
    print(f"\n[3] visual->motor committor path interior:")
    print(f"    association-cortex fraction of path interior = "
          f"{interior_assoc_frac:.2f}")
    print(f"    interior network composition: {dict(interior_nets)}")
    print(f"    {'PASS' if interior_assoc_frac > 0.5 else 'FAIL'}: path "
          f"{'passes through' if interior_assoc_frac > 0.5 else 'does NOT pass through'} "
          f"association cortex")
    print(f"\nSTIMULUS -> BEHAVIOR network sequence (visual stimulus to motor):")
    for n, c in seq:
        print(f"    {n:>14}  committor {c:.3f}")

    result = {
        "n_regions": int(len(networks)),
        "n_networks": k,
        "validation_1_pcca_vs_yeo": {
            "adjusted_rand_index": ari,
            "shuffle_p": ari_p,
            "shuffle_p95": ari_p95,
            "pass": bool(ari_p < 0.05),
        },
        "validation_2_within_vs_between_mfpt": {
            "within_mean": float(within.mean()),
            "between_mean": float(between.mean()),
            "mannwhitney_p": float(u_p),
            "pass": bool(u_p < 0.05),
        },
        "validation_3_path_through_association": {
            "association_fraction": float(interior_assoc_frac),
            "interior_composition": {k2: int(v) for k2, v in interior_nets.items()},
            "pass": bool(interior_assoc_frac > 0.5),
        },
        "stimulus_to_behavior_sequence": [
            {"network": n, "mean_committor": c} for n, c in seq
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
