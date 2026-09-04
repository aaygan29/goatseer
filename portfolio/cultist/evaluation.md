# cultist: evaluation

- External home: `~/Desktop/Research/submissions/ai-safety/cultist` (deliverable) with code at
  `~/Desktop/Research/projects/Neuroscience/Neuro-AI/cultist` (confirmed present: DATA_MANIFEST.json,
  LICENSE, PREREGISTRATION.md, README.md, data/, docs/, paper/, results/, src/, tests/). Targeting
  IEEE TPS 2026 (#2159) per the current `ORGANIZATION.md`; not yet under `submissions/` as an
  accepted work.
- Status: active
- Last scored: 2026-09-03
- Next re-score due: 2026-09-17

## One-line claim

Exploratory: a frozen brain-encoder-predicted belief-formation signature
B(s)=E+V-R (engagement + value - resistance) carries belief-imparting information beyond
a content-only baseline, validated so far only on synthetic ground truth; the real-data
run (public corpus + learned encoder) is described as a small, not-yet-made change.

## Gate scores

| Gate | Status | Note |
| --- | --- | --- |
| G1 provenance/leakage        | partial | `DATA_MANIFEST.json` documents intended real sources (ChangeMyView/Tan2016, Persuasion-for-Good/Wang2019, MIST/Maertens2023, Neurosynth, TRIBE v2), but the current committed result set is synthetic, not the real corpus. |
| G2 seed variance (n>=5)      | pass (on synthetic data) | 12-seed stability reported: H-incremental detects 12/12, H-load noisier at 9/12 seeds. This is a genuine >=5-seed variance report, but only for the synthetic apparatus. |
| G3 specification robustness  | unscored (no evidence available; no preprocessing/hyperparameter sweep reported) | |
| G4 specificity ablation      | pass (on synthetic data) | Content-only and scrambled controls are exactly the ladder's specificity ablation: positive detects (dAUC +0.067), content-only is null, scrambled is at chance. |
| G5 confound control          | unscored (no evidence available; not yet run against real text/content confounds) | |
| G6 mechanism/necessity       | unscored (no evidence available) | |
| G7 calibration                | unscored (no evidence available) | |
| G8 external validity          | fail | No real public corpus has been run through the pipeline yet; the apparatus is validated on synthetic ground truth only. |
| G9 measurement reliability    | unscored (no evidence available) | |
| G10 reproducibility            | partial | 5 tests pass (positive/content-only/scrambled controls) and the repo is committed (bfe8bb4); no single documented `make reproduce` target for the headline synthetic result. |
| G11 ethics/safety              | pass | Explicit bright line carried from genesis: population/public-data modeling only, never targeting a named individual; framed as proof-of-risk, not an operational persuasion weapon; no human-subjects collection (explicitly ruled out as infeasible for the author to run responsibly). |
| G12 analytic integrity         | partial | `PREREGISTRATION.md` exists and the manuscript was council-reviewed to a MAJOR REVISION-fixed state (apparatus + preregistration framing, humanized); some of that revision happened after initial synthetic results were seen, which is a declared deviation rather than a clean before-data preregistration. |

### fMRI addendum

| Gate | Status | Note |
| --- | --- | --- |
| G-fMRI.1 per-participant CV        | unscored (no evidence available; the encoder is a frozen predictor used as a feature extractor, not fit per-participant here) | |
| G-fMRI.2 sign-concordance binomial | unscored (no evidence available) | |
| G-fMRI.3 group-level significance  | unscored (no evidence available) | |

### LLM addendum

| Gate | Status | Note |
| --- | --- | --- |
| H1 refusal path                | unscored (no evidence available) | |
| H2 calibrated confidence       | unscored (no evidence available) | |
| H3 loyalty vector disclosure   | n/a | Not a loyalty-audit instrument. |

## Program-audit note (not a retirement flag for this project)

`cultist` is the survivor of an earlier program audit that fenced out several sibling
threads (LLM LZc transfer perm_p=1.0, an N=4 fingerprint result, and the spikeprint CSI
line); it absorbed the belief/persuasion strand rather than being retired itself. No
retirement ADR is warranted for `cultist` here.

## Contribution to NEUROSPINE

Tuple field(s) this project could feed: `honesty_verdict`, `calibrated_confidence` (the
specificity-gate design generalizes well to the tuple's abstention concept). Currently
synthetic-only, so nothing feeds the tuple with real evidence yet.

## Open action items

- [ ] Make the "2-line change" swap to a real public corpus loader + learned encoder that
  the memory describes as the remaining step: this is the single highest-leverage action
  for this project (directly advances G1, G8, and unblocks G5/G6/G7 scoring).
- [ ] Once real data runs, re-score G2/G4 against it; the current synthetic-only pass
  scores must not be read as evidence about the real claim.
- [ ] Run the content-only/scrambled specificity ablation (G4) against the real corpus,
  not just synthetic stimuli, before any real-data claim ships.
