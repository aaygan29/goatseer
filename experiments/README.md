# NEUROSPINE Experiments

Each experiment lives in its own subdirectory with the following structure:

```
experiments/<name>/
  Makefile
  README.md
  configs/
    seed_0.yaml
    seed_1.yaml
    ...
  results/
    (gitignored)
```

## Makefile targets

Every experiment must define:

- `make reproduce`: Run the experiment with all seeds, reproducibly.
- `make synthetic`: Run the synthetic-ground-truth version first.
- `make real`: Run on real data (only after synthetic passes).
- `make clean`: Remove results/ and rebuild from scratch.

## Experiment README

Each experiment specifies:

- **Claim**: One-line hypothesis or decision the experiment tests.
- **Hypothesis**: Mechanistic prediction (what we expect to see).
- **Gates**: Which gate(s) from gates/gate-ladder-v0.md are addressed.

## Rules

1. **Synthetic first**: No real-data claim ships without its synthetic counterpart
   passing first. Real-data tests must be marked `@pytest.mark.real`.
2. **Seed sweep**: Configs/ must hold at least n=5 seeds. A single seed failure
   causes the entire experiment to fail and requires root-cause analysis.
3. **Results gitignored**: results/ is never committed to git. A separate
   experiments-tracking/ folder (outside this repo) holds long-term result archives.
