"""Aggregate per-subject summaries from the EEG-BCI transition-kernel run.

Reads every `results/summary_subject-*.json` and reports the
across-subject distribution of the Markov invariants plus the
shuffle-null verdict tally. This is the group-level view of a
per-subject analysis: it does NOT pool subjects into one model,
it reports how many subjects individually show structure.

Run:

    python experiments/spd_transition_eegbci/aggregate.py
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path(__file__).parent / "results",
    )
    parser.add_argument("--alpha", type=float, default=0.05)
    args = parser.parse_args()

    files = sorted(args.results_dir.glob("summary_subject-*.json"))
    if not files:
        raise SystemExit(f"no results found under {args.results_dir}")

    rows = []
    for f in files:
        with open(f) as fh:
            rows.append(json.load(fh))

    n = len(rows)
    h = np.array([r["entropy_rate_nats_per_step"] for r in rows])
    gap = np.array([r["spectral_gap"] for r in rows])
    eff = np.array([r["effective_dimension"] for r in rows])
    z = np.array([r["shuffle_null_control"]["z_score"] for r in rows])
    p = np.array([r["shuffle_null_control"]["p_value_one_sided_below"] for r in rows])
    max_h = rows[0]["shuffle_null_control"]["max_possible_entropy_rate"]

    structured = p < args.alpha
    n_struct = int(structured.sum())

    # Benjamini-Hochberg FDR correction across subjects.
    order = np.argsort(p)
    ranks = np.empty(n, dtype=int)
    ranks[order] = np.arange(1, n + 1)
    q = p * n / ranks
    q = np.minimum.accumulate(q[order][::-1])[::-1]
    q_full = np.empty(n)
    q_full[order] = np.minimum(q, 1.0)
    n_struct_fdr = int((q_full < args.alpha).sum())

    print(f"subjects analyzed: {n}")
    print(f"max possible entropy rate (log k): {max_h:.4f}")
    print()
    print(f"entropy rate       mean {h.mean():.4f}  sd {h.std(ddof=1):.4f}  "
          f"range [{h.min():.4f}, {h.max():.4f}]")
    print(f"spectral gap       mean {gap.mean():.4f}  sd {gap.std(ddof=1):.4f}  "
          f"range [{gap.min():.4f}, {gap.max():.4f}]")
    print(f"effective dim      mean {eff.mean():.4f}  sd {eff.std(ddof=1):.4f}  "
          f"range [{eff.min():.4f}, {eff.max():.4f}]")
    print(f"null z-score       mean {z.mean():.4f}  sd {z.std(ddof=1):.4f}  "
          f"range [{z.min():.4f}, {z.max():.4f}]")
    print()
    print(f"subjects with temporal structure (uncorrected p < {args.alpha}): "
          f"{n_struct}/{n} = {100.0 * n_struct / n:.1f}%")
    print(f"subjects with temporal structure (BH-FDR q < {args.alpha}):      "
          f"{n_struct_fdr}/{n} = {100.0 * n_struct_fdr / n:.1f}%")
    print()

    # Sign-concordance binomial (G-fMRI.2 analogue for this EEG run):
    # how many subjects have z < 0 (entropy rate BELOW the null, i.e.
    # more structure than chance)?
    n_neg = int((z < 0).sum())
    from math import comb
    k = min(n_neg, n - n_neg)
    tail = sum(comb(n, i) for i in range(k + 1)) * (0.5 ** n)
    binom_p = min(1.0, 2.0 * tail)
    print(f"sign concordance: {n_neg}/{n} subjects have z < 0 "
          f"(more structure than shuffled), two-sided binomial p = {binom_p:.3e}")
    print()

    print("per-subject detail:")
    print(f"{'subj':>5} {'h_rate':>8} {'gap':>7} {'eff_dim':>8} {'z':>9} "
          f"{'p':>8} {'q(BH)':>8}  verdict")
    for i, r in enumerate(rows):
        print(f"{r['subject']:>5} {h[i]:>8.4f} {gap[i]:>7.4f} {eff[i]:>8.4f} "
              f"{z[i]:>9.3f} {p[i]:>8.4f} {q_full[i]:>8.4f}  "
              f"{'STRUCTURE' if q_full[i] < args.alpha else 'none'}")


if __name__ == "__main__":
    main()
