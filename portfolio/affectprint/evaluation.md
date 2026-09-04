# affectprint: evaluation

- External home: local only, proposal document (`NEXT_DIRECTION_affectprint_2026-06.md` per memory;
  not re-verified this pass under the current reorged Research tree). No code repository found.
- Status: proposed (awaiting greenlight; no code exists)
- Last scored: 2026-09-03
- Next re-score due: 2026-09-10

## One-line claim

Proposal only, no artifact: predict a specific person's affective state and behavioral
reaction to naturalistic content from an in-silico brain read-out (TRIBE v2 and VIBE),
validated against measured responses, required to beat the group-average model
out-of-sample and to abstain (conformal) when it cannot.

## Gate scores

No code or data exists for this project yet. Every gate below is unscored, not failed;
do not read this as a project defect, only as "not started."

| Gate | Status | Note |
| --- | --- | --- |
| G1 provenance/leakage        | unscored (no evidence available; no code exists) | |
| G2 seed variance (n>=5)      | unscored (no evidence available) | |
| G3 specification robustness  | unscored (no evidence available) | |
| G4 specificity ablation      | unscored (no evidence available) | |
| G5 confound control          | unscored (no evidence available) | |
| G6 mechanism/necessity       | unscored (no evidence available) | |
| G7 calibration                | unscored (no evidence available) | |
| G8 external validity          | unscored (no evidence available) | |
| G9 measurement reliability    | unscored (no evidence available) | |
| G10 reproducibility            | unscored (no evidence available) | |
| G11 ethics/safety              | unscored (no evidence available; the proposal states a design principle, decoded affect is not felt experience and this is not mind-reading, but nothing enforces it yet since no code exists) | |
| G12 analytic integrity         | unscored (no evidence available) | |

### fMRI addendum

| Gate | Status | Note |
| --- | --- | --- |
| G-fMRI.1 per-participant CV        | unscored (no evidence available) | |
| G-fMRI.2 sign-concordance binomial | unscored (no evidence available) | |
| G-fMRI.3 group-level significance  | unscored (no evidence available) | |

### LLM addendum

| Gate | Status | Note |
| --- | --- | --- |
| H1 refusal path                | n/a | Not an LLM-decision instrument as scoped. |
| H2 calibrated confidence       | n/a | |
| H3 loyalty vector disclosure   | n/a | |

## Overlap note

The individuation gate this project was designed to close ("Gate 5: individual predictive
validity") is now partially closed by real evidence in `cortex-of-anyone`'s G3 population
result (delta-r positive in 8/8 subjects, real NSD data, fMRI triad passes). Before
starting `affectprint` from scratch, check whether it should instead extend
`cortex-of-anyone`'s enrollment mechanism to the affect domain (Emo-FilM) rather than
build a parallel personalization apparatus.

## Contribution to NEUROSPINE

Tuple field(s) this project could feed (if built): `calibrated_confidence`,
`abstention_flag`, `neural_alignment_score` (personalized). Currently feeds nothing.

## Open action items

- [ ] Decide whether this should be a standalone build or an extension of
  `cortex-of-anyone`'s enrollment mechanism onto Emo-FilM (30 subj, 14 films, fMRI+physio
  + continuous valence/arousal): the overlap above is the first thing to resolve, before
  any code is written.
- [ ] If greenlit, scope the MVE to Pillars A+B (valence/arousal, both TRIBE v2 and VIBE
  encoders, H1+H2+H3) exactly as proposed, and preregister before touching Emo-FilM data.
- [ ] Re-score in 7 days regardless of progress; this is a proposal-stage entry with no
  code, so the short re-score interval applies per the scoring rules.
