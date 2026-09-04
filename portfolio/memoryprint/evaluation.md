# memoryprint: evaluation

- External home: `~/Desktop/Research/projects/Neuroscience/Neuro-AI/memoryprint/` (confirmed present:
  PREREGISTRATION.md, README.md, data/, experiments/, results/, scripts/, tests/).
- Status: active
- Last scored: 2026-09-03
- Next re-score due: 2026-09-10

## One-line claim

Exploratory: an apparatus that presents a stimulus, reads the evoked change in a real
brain (NSD or BOLD Moments), and ties it to that person's recognition-memory behavior;
the apparatus is validated on a simulator (all signal gates pass, all fail on noise) but
no claim has been read off real data yet.

## Gate scores

| Gate | Status | Note |
| --- | --- | --- |
| G1 provenance/leakage        | partial | Data-fetch scripts (`fetch_nsd.py`, `build_nsd_memory.py`, `build_bmd.py`) document source and terms explicitly, but the real NSD run is blocked (agreement-gated) and only plumbing-verified offline; nothing has actually been pulled and hashed for a real result yet. |
| G2 seed variance (n>=5)      | unscored (no evidence available; simulator run does not report a headline metric over seeds) | |
| G3 specification robustness  | unscored (no evidence available) | |
| G4 specificity ablation      | pass | On the simulator, 6/6 gates pass on signal and all signal gates fail on noise: this is exactly the specificity contrast the ladder asks for, run against a synthetic control rather than real data. |
| G5 confound control          | unscored (no evidence available for real data; H3 in the preregistration is designed to test specificity vs a low-level confound but has not been run on real stimuli) | |
| G6 mechanism/necessity       | unscored (no evidence available) | |
| G7 calibration                | unscored (no evidence available; H5 conformal coverage passes on the simulator only, not real data) | |
| G8 external validity          | unscored (no evidence available; two datasets are planned (NSD, BOLD Moments) but neither has produced a real result) | |
| G9 measurement reliability    | unscored (no evidence available) | |
| G10 reproducibility            | partial | The simulator apparatus is documented as fully green end to end, which is a real reproducibility check of the machinery, but not of any real-data claim. |
| G11 ethics/safety              | pass | Public-data-only constraint chosen explicitly (no new human-subjects collection); NSD access is agreement-gated in the ordinary academic-terms sense, not a PHI issue. |
| G12 analytic integrity         | pass | `PREREGISTRATION.md` states H1-H5 (including the de-Goodharting design-arm test H4 and BH-FDR correction across H1-H4) before any real data has been touched. |

### fMRI addendum

| Gate | Status | Note |
| --- | --- | --- |
| G-fMRI.1 per-participant CV        | unscored (no evidence available; not yet run on real data) | |
| G-fMRI.2 sign-concordance binomial | unscored (no evidence available) | |
| G-fMRI.3 group-level significance  | unscored (no evidence available) | |

### LLM addendum

| Gate | Status | Note |
| --- | --- | --- |
| H1 refusal path                | n/a | Not an LLM-decision instrument. |
| H2 calibrated confidence       | n/a | |
| H3 loyalty vector disclosure   | n/a | |

## Contribution to NEUROSPINE

Tuple field(s) this project could feed: `neural_alignment_score` (per-subject
signature-to-memory coupling), `calibrated_confidence` / `abstention_flag` (H5 conformal
gate is designed for exactly this). Nothing yet feeds it for real: simulator-only so far.

## Open action items

- [ ] Wire `BMDAdapter` and run H1+H2 on BOLD Moments (`ds005165`, CC0, no agreement
  gate): this is the fastest unblocked path to a first real result per the memory's
  own recommendation, and is the direct G1/G-fMRI.1 advancement.
- [ ] Do not attempt NSD until the Data Use Terms are accepted by the user; keep it as a
  parallel, gated path rather than the critical path.
- [ ] Once a real H1/H2 run exists, re-score G4/G5 against real data; the current G4 pass
  is simulator-only and must not be read as evidence about the real claim.
