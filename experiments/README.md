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
| `connectome_behavior_prediction/` | PhysioNet EEG-BCI, or **bring your own** (`--input`) | Behavior from discrete state sequences, subject-disjoint split + occupancy ablation. Honest cross-subject NEGATIVE at n=20 (no trajectory signal beyond occupancy or null). Reusable engine `analyze_state_sequences`. | G1, G3 (occupancy ablation), G4 (shuffle null), G7 (subject-disjoint) |
| `within_subject_decoding/` | PhysioNet EEG-BCI | Within-subject decoding with a Riemannian-MDM positive control. State-trajectory model finds no signal (0.57), but MDM on the raw covariances does (0.62, subjects to 0.92): the discretization discards the signal, the data has it. Engine `analyze_within_subject`. | G1, G3 (occupancy + MDM control), G4 (per-subject null) |
| `geometry_preserving_discretization/` | PhysioNet EEG-BCI | Tangent-space discriminant discretization (ADR-017). At n=8 it recovered signal the prototype discretization lost; at n=20 the effect is weak (recovery +0.04, group p=0.075) and partly confounded (see ADR-017 post-hoc, ADR-018 pivot). MI is a static-signal, weak dataset. `neurospine.discretize`. | G1, G3 (prototype/MDM baselines), G4 (supervised-pipeline null) |
| `sleep_transition_decoding/` | PhysioNet Sleep-EDF Expanded | The trajectory model's POSITIVE control (ADR-018/019): stage-transition structure helps decoding (Viterbi 0.834 vs memoryless 0.816, 3/3 recordings; McNemar fixed 278 / broke 129, p=1e-13). Mirror image of the MI null. Engine `sequence_decode`. | G1, G3 (transitions-off baseline), G4 (McNemar) |
| `clinical_state_dynamics/` | ADHD-200 Consortium resting fMRI (nilearn `fetch_adhd`) | ADHD vs typically-developing GROUP comparison (not a classifier) on dynamics summaries (entropy rate, spectral gap, dwell time, metastable communities), site+motion confound-controlled (ADR-022). N=30 after phenotypic alignment (13 ADHD, 17 control, 7 sites); honest NULL after residualizing on site + mean FD (all perm p > 0.2, \|d\| <= 0.45), consistent under a single-site (KKI, n=8) check. | G1 (provenance), G6/G8 (confound control), G4 (permutation null) |

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
