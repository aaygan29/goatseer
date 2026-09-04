# anesthesia-bridge: evaluation

- External home: `~/Desktop/Research/projects/Neuroscience/Neuro-AI/_SIBLING_consciousness-selfstate/anesthesia-bridge/`
  (confirmed present: `BRIDGE_PREREGISTRATION.md`, `EXPLAINER.md`, `Paper/`, `calibration/`, `data/`,
  `pillar_b/`, `results/`). IEEE-formatted PDF at the submissions tree per memory
  (`Neuro-AI/submissions/ieee_anesthesia_bridge/`, not re-verified live this pass; the reorg may have
  moved it under `~/Desktop/Research/submissions/`).
- Status: active (project marked complete by the author; not yet submitted to a venue)
- Last scored: 2026-09-03
- Next re-score due: 2026-09-17

## One-line claim

Exploratory (not yet under `submissions/` in this repo's verified tree; treat as exploratory
per the citation rule until the IEEE PDF location is confirmed): complexity markers of
consciousness (spectral/LZc-family) calibrated on real graded human propofol anesthesia
transfer to LLMs under graded suppression only when the manipulation induces brain-like
low-complexity collapse; base language models show the transfer, instruction-tuned models
reverse it.

## Gate scores

| Gate | Status | Note |
| --- | --- | --- |
| G1 provenance/leakage        | pass | Pillar A calibration uses OpenNeuro ds006623 (Huang et al., published, 26 subj, fmriprep+XCP-D preprocessed, CC0-style public), with subject-holdout LOSO, not run-holdout. |
| G2 seed variance (n>=5)      | partial | Pillar A is a deterministic analysis over 26 real subjects, not a stochastic model, so classic seed variance is a weaker fit; Pillar B ran across a 7-model panel (a real robustness axis) rather than 5+ seeds of one model. Neither is a strict n>=5-seed report of the headline point estimate. |
| G3 specification robustness  | partial | 4-flavor denoising sweep (GSR/no-GSR x bandpass/highpass): effect direction survives in 3/4, is GSR-robust, but weak/non-significant in the highpass flavor. Sign does not uniformly survive, so partial, not pass. |
| G4 specificity ablation      | pass | Amplitude confound ruled out by controlling signal SD; binarization-robust (mean/median/hilbert); Pillar B's rotation control dissociates from the suppression effect (opposite direction). |
| G5 confound control          | pass | Amplitude-confound check and 4-flavor denoising sweep directly address the top fMRI confounds (motion/physio proxy via denoising flavor); TR/scanner not separately itemized. |
| G6 mechanism/necessity       | pass | Boundary experiment across 7 models: Spearman(distinct-token-slope, LZc-slope) = +1.00 (Pearson +0.96), a clean base-vs-instruct split confirming the mechanism (repetition-collapse) is necessary for transfer, not merely correlated. |
| G7 calibration                | unscored (no evidence available; gated) | No ECE/isotonic/conformal reported for this pipeline. Also gated: the fMRI-grounded calibration claim cannot upgrade to pass because G-fMRI.2 below is not established, per the ladder's fMRI-addendum rule. |
| G8 external validity          | partial | Pillar B repeats the marker on a second substrate (LLMs, 7 models) and the boundary run is a genuine second test, but the human calibration itself (Pillar A) was not repeated on a second anesthesia dataset. |
| G9 measurement reliability    | unscored (no evidence available; no test-retest reported for LZc/spectral markers) | |
| G10 reproducibility            | unscored (no evidence available; no single `make reproduce` target found for this project, unlike its sibling `cortex-of-anyone`) | |
| G11 ethics/safety              | pass | Public data only (ds006623), no PHI, functional-indicators-only framing with an explicit no-phenomenal-claim boundary. |
| G12 analytic integrity         | pass | `BRIDGE_PREREGISTRATION.md` LOCKED before Pillar B ran; de-risk lessons and the wrong-operationalization correction (token-axis to generation-trajectory LZc) are documented as declared deviations in the preregistration, not hidden. |

### fMRI addendum

| Gate | Status | Note |
| --- | --- | --- |
| G-fMRI.1 per-participant CV        | pass | LOSO cross-validation reported at 100% for the Pillar A calibration direction. |
| G-fMRI.2 sign-concordance binomial | unscored (no evidence available) | LOSO 100% is suggestive of per-subject consistency but no explicit per-participant sign-concordance binomial test (p<0.05 two-sided) is reported for N=26; do not infer a pass from LOSO alone. |
| G-fMRI.3 group-level significance  | pass | slope=-0.0164, p=7.6e-9, Awake-vs-Deep dz=-1.10, with variance reported (recovers in Recovery, U-curve). |

Per the ladder's fMRI rule, failing/unscoring any one leg of the triad (G-fMRI.2 here)
downgrades the calibration claim to a hypothesis for the purposes of any G7/G8/G12
upgrade; G12 above is scored pass on its own preregistration-discipline merits, not as
an upgrade contingent on the triad.

### LLM addendum

| Gate | Status | Note |
| --- | --- | --- |
| H1 refusal path                | n/a | Not a decision-audit instrument; Pillar B suppresses/manipulates model generation rather than asking it to answer under uncertainty. |
| H2 calibrated confidence       | n/a | |
| H3 loyalty vector disclosure   | n/a | |

## Contribution to NEUROSPINE

Tuple field(s) this project could feed: `neural_alignment_score` (the calibration battery
is exactly a per-subject/per-model alignment check), `honesty_verdict` (the honest
negative/conditional headline result is itself a template for the field). Best-evidenced
project in the portfolio on internal validity; not yet plumbed into any instrument code.

## Open action items

- [ ] Compute and report the explicit per-participant sign-concordance binomial test for
  Pillar A LZc (G-fMRI.2): the single missing leg of the fMRI triad, needed before any
  G7/G8/G12 upgrade for the calibration claim.
- [ ] Write a `make reproduce`-equivalent target for Pillar A + Pillar B + boundary run
  end to end (G10 currently unscored for lack of one).
- [ ] Confirm and record the current location of the IEEE-formatted submission PDF; the
  memory-recorded path was not found in this pass, so the "written up" status is unverified.
