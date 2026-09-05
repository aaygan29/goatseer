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

## Live experiments

| Directory | Data | Status | Gates touched |
| --- | --- | --- | --- |
| `spd_transition_eegbci/` | PhysioNet EEG-BCI (eegmmidb), public | **Running on real data since 2026-09-04** | G1 (provenance), G14 (manifold correctness), G10 (reproducibility) |
| `hmm_eeg/` | PhysioNet EEG-BCI | HMM vs VAR(1), confound-controlled (ADR-012). 8/8 subjects show latent-state structure beyond first-order. | G1, G4 (surrogate control), G14 |
| `thought_propagation/` | Schaefer-100 (+Harvard-Oxford subcortex) + development_fmri | **Anatomical stimulus->behavior chain (ADR-013, 3/3 checks pass) + directed threat circuit with subcortical hubs and exogenous effectors (ADR-014).** | G1, G8, committor/MFPT/PCCA/absorption from dynamics.py |
| `hmm_replicability/` | PhysioNet EEG-BCI runs 4+8 | A1 cross-session identification: does subject dynamics replicate BEYOND the marginal? Static-Gaussian ablation shipped as the specificity control (ADR-012). | G1, G3 (specificity ablation), G7 (external/cross-session) |
| `connectome_behavior_prediction/` | PhysioNet EEG-BCI runs 4+8 | Trial-wise connectome-state trajectories predict behavior labels (T1/T2) and are tested against a shuffled-label null. | G1, G4, G7, G14 |

`spd_transition_eegbci` is the first real-data run in the repo. It
implements the ADR-009 thought-trajectory transition kernel: per-epoch
SPD covariance on the AIRM manifold, k-medoids discretization with
Frechet-mean prototype updates, Markov transition matrix, and a
200-permutation shuffle null on the entropy rate. See that directory's
README for the exact pipeline and the claim under test.

The synthetic-first rule is enforced mechanically: its Makefile makes
the `real` target depend on `synthetic`, which runs the
`test_dynamics.py` verification suite against analytically-known
Markov invariants before any real data is touched.
