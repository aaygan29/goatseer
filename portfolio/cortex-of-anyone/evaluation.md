# cortex-of-anyone: evaluation

- External home: `~/Desktop/Research/projects/Neuroscience/Neuro-AI/_SIBLING_consciousness-selfstate/cortex-of-anyone/`
  (confirmed present: README.md, data/, enrollment/, experiments/, neuro_ai_core/, results/, tests/,
  validate_all.py). That folder's own README flags **13 uncommitted local changes** as of the last
  reorg pass: a real hygiene risk, not resolved by this evaluation. `aaygan29/cortex-of-anyone`
  does not resolve via `gh repo view`; per memory the real integration lives on branches
  (`cortex-of-anyone-integration`, `cortex-of-anyone-live-brain`) pushed to the
  `The-Sapient-Company/sapient` org repo, not a personal repo of this name.
- Status: active
- Last scored: 2026-09-03
- Next re-score due: 2026-09-17

## One-line claim

Exploratory: a per-subject additive read-out head, enrolled from real NSD data, beats a
leave-one-subject-out average-brain encoder out of sample in every one of 8 available
subjects (mean delta-r +0.0211, Wilcoxon p=0.0039); a separate consciousness-proxy gate
(aperiodic spectral exponent) is validated on real propofol EEG (n=20); a dynamical-twin
mechanistic model built to explain the consciousness gate does not reproduce it.

## Gate scores

| Gate | Status | Note |
| --- | --- | --- |
| G1 provenance/leakage        | pass | `.cortex` files carry SHA-256 hashes of stored weights; NSD test-split source and the fcp-indi-style targeted EEG cohort fetch are both documented; subject-holdout (leave-one-subject-out) used for the population claim, not run-holdout. |
| G2 seed variance (n>=5)      | partial | 5-fold CV is used for the population result; this is real resampling variance but not a >=5-seed sweep of a stochastic point estimate on fixed real data. |
| G3 specification robustness  | pass | The individuation result is shown at n=3 (unique-image, large within-subject delta-r +0.13 to +0.19) and again at n=8 (population, smaller but consistent delta-r), two independently-built analyses that agree in sign and are documented as reconciling each other. |
| G4 specificity ablation      | pass | Shuffle-null controls are near zero in every real run reported (population shuffle-null mean +0.0012 vs real +0.0211); the L5 consciousness gate's shuffled-label negative control (rho +0.075 to +0.17) is explicitly reported as failing to pass, confirming specificity. |
| G5 confound control          | partial | A real MNI-vs-native-space brainmask misalignment bug was caught and fixed for the consciousness-gate EEG pipeline; motion/TR/scanner are not separately enumerated for the fMRI individuation claim. |
| G6 mechanism/necessity       | fail (honestly reported) | The Hopf/Stuart-Landau dynamical-twin model built to explain the one validated consciousness signature (spectral exponent) moves in the wrong direction under its own arousal knob; the memory states this plainly as the twin failing the gate, not as a hidden negative. |
| G7 calibration                | unscored (no evidence available on real data; H5 conformal coverage of .90 was reported on the simulator MVE, not the real NSD/EEG runs) | |
| G8 external validity          | partial | The consciousness-proxy axis is validated on a real, independent second dataset (ds005620 propofol EEG, n=20, a genuinely different modality from the fMRI individuation claim); the individuation claim itself has only been tested within one dataset (NSD, at n=3 and n=8 slices of the same cohort). |
| G9 measurement reliability    | unscored (no evidence available; no test-retest across sessions for individual .cortex fingerprints) | |
| G10 reproducibility            | pass | `python3 validate_all.py` runs signal and negative-control worlds in one process and writes a signed report; real-data variants are explicit flags (`--real-l5`, `--real-l5-spec`). |
| G11 ethics/safety              | pass | Public data only (NSD, ds005620); no PHI; functional framing with governance for `brain_file`s explicitly named as unfinished future work rather than glossed over. |
| G12 analytic integrity         | partial | H1/H3/H5 were preregistered for the simulator MVE; the real NSD runs were iterative and re-anchored after an earlier null (260-shared-image RSA), which the project documents as a declared reconciliation rather than a hidden re-analysis, matching the ladder's "or the deviation is declared explicitly" clause. |

### fMRI addendum

| Gate | Status | Note |
| --- | --- | --- |
| G-fMRI.1 per-participant CV        | pass | G3-population uses 5-fold CV of a per-subject encoder against a leave-one-subject-out group encoder: a genuine subject-held-out design. |
| G-fMRI.2 sign-concordance binomial | pass | delta-r positive in 8/8 available subjects (binomial p=1/256 ~ 0.004, consistent with the reported Wilcoxon p=0.0039); this is the cleanest fMRI-triad pass found in the whole portfolio. |
| G-fMRI.3 group-level significance  | pass | Wilcoxon p=0.0039 with 95% CI [+0.0105, +0.0330] reported. |

The fMRI triad is established for the individuation claim specifically. That licenses the
partial G7/G8 scores above to be read as real, not aspirational, for this one claim; it
does **not** extend to the separate, and honestly failing, dynamical-twin mechanism claim
or to the consciousness-proxy axis's own calibration.

### LLM addendum

| Gate | Status | Note |
| --- | --- | --- |
| H1 refusal path                | n/a | Not an LLM-decision instrument. |
| H2 calibrated confidence       | n/a | |
| H3 loyalty vector disclosure   | n/a | |

## Retirement candidate (partial scope)

The Hopf/Stuart-Landau dynamical-twin submodule (`dynamical_twin.py`) fails to reproduce
the project's own validated consciousness signature and is explicitly flagged in memory
as needing "a realistic anesthesia-parameterized neural-mass model, not a bifurcation-
sweep Hopf." This is a fundamental-failure note for that submodule specifically, not for
the individuation result, which is real and robust.

Proposed ADR (not created here): `decisions/ADR-005-retire-cortex-of-anyone-hopf-dynamical-twin.md`.

## Contribution to NEUROSPINE

Tuple field(s) this project could feed: `neural_alignment_score` (direct: the strongest
real per-subject-vs-average result in the portfolio), `answer` (personalized read-out).
Best real fMRI-triad evidence in the portfolio; commit the 13 pending local changes before
relying on this further.

## Open action items

- [ ] Commit or explicitly review the 13 uncommitted local changes flagged by the
  project's own README before any further work builds on this codebase.
- [ ] Replace the Hopf dynamical-twin with an anesthesia-parameterized neural-mass model,
  or open the retirement ADR above and redesign the mechanism axis from scratch.
- [ ] Run the individuation result on a second, independent fMRI dataset (not another
  slice of NSD) to advance G8 for the individuation claim specifically.
