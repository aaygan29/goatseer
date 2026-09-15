# spikeprint: evaluation

- External home: local only, `~/Desktop/Research/projects/Neuroscience/Neuro-AI/spikeprint/`
  (confirmed present: CITATION.cff, LICENSE, PREREGISTRATION.md, README.md, REFERENCES.md, data/,
  docs/, results/, scripts/, tests/, pyproject.toml). Confirmed via `gh repo view` that
  `aaygan29/spikeprint` does **not** exist on GitHub yet: consistent with the memory's own
  "NOT pushed, push private repo LAST" sequencing choice.
- Status: proposed (substantial code and real-data results exist, but the project has not been
  greenlit as a finished line and is not yet public)
- Last scored: 2026-09-03
- Next re-score due: 2026-09-10

## One-line claim

Exploratory: on real NARPS ds001734 data, expected-value and prospect-theory logistic
models predict accept/reject choices about as well as a spiking LIF decision model
(held-out AUC 0.882-0.893 across models), with no accuracy or energy superiority claimed
for the spiking substrate (current-coded SNN uses roughly 13x more energy, an honest
null); a separate CSI (vmPFC-dlPFC) validation pipeline is built but not yet run because
it depends on TRIBE v2 compute not exercised in this pass.

## Gate scores

| Gate | Status | Note |
| --- | --- | --- |
| G1 provenance/leakage        | pass | Real NARPS ds001734 (CC0), 27,454 trials, 108 subjects, 433 files checksummed in a manifest; subject-grouped 5-fold CV used, not run-holdout. |
| G2 seed variance (n>=5)      | unscored (no evidence available; models are fit once per fold on real data, not swept over >=5 seeds of a point estimate) | |
| G3 specification robustness  | unscored (no evidence available; no preprocessing/hyperparameter sweep beyond the model-family comparison itself) | |
| G4 specificity ablation      | pass | The H1a text-based manipulation-index test is an honest null (AUC 0.500, sd=0, caused by a real tokenizer bug that discards digits) reported as unvalidated rather than dressed up; the EV positive control (AUC 0.883) confirms the pipeline is sound, isolating the failure to the specific construct rather than the harness. |
| G5 confound control          | partial | A near-tautology confound is flagged and handled (EV is near-tautological for 50/50 gambles); a genre/length confound in an earlier corpus-B-vs-C design was caught by an external critic review and the comparison was demoted to a sanity check rather than a claim. |
| G6 mechanism/necessity       | unscored (no evidence available; no intervention run to show a mechanism is necessary) | |
| G7 calibration                | unscored (no evidence available) | |
| G8 external validity          | fail | The choices13k dataset was deferred because it has no license at the source (author permission needed); NARPS is the only dataset actually run. |
| G9 measurement reliability    | unscored (no evidence available) | |
| G10 reproducibility            | partial | 33+ tests pass, ruff clean, uv-managed environment; no single documented end-to-end `make reproduce` timing found. |
| G11 ethics/safety              | pass | Public NARPS data only; explicit correction discipline when the user caught a construct-naming error (an earlier heuristic was wrongly called "CSI," fixed and marked SUPERSEDED rather than left standing). |
| G12 analytic integrity         | pass | BH-FDR family-wise correction (`decide_family`), a numeric minimum-detectable-effect-size power script, and a documented deviations log (`docs/DEVIATIONS.md`) after each of several external critic review rounds: real preregistration-adjacent discipline, with declared deviations rather than silent ones. |

### fMRI addendum

| Gate | Status | Note |
| --- | --- | --- |
| G-fMRI.1 per-participant CV        | unscored (no evidence available; the CSI-via-TRIBE fMRI pipeline is built but not yet run: it is a "wired slot" pending A100 compute per memory) | |
| G-fMRI.2 sign-concordance binomial | unscored (no evidence available) | |
| G-fMRI.3 group-level significance  | unscored (no evidence available) | |

### LLM addendum

| Gate | Status | Note |
| --- | --- | --- |
| H1 refusal path                | n/a | Not an LLM-decision instrument as currently built. |
| H2 calibrated confidence       | n/a | |
| H3 loyalty vector disclosure   | n/a | |

## Contribution to NEUROSPINE

Tuple field(s) this project could feed: `answer` (choice prediction), `sparse_circuit_id`
(spikes-per-decision as an efficiency handle, if the energy claim ever turns positive).
Currently an honest-null infrastructure project: real methodology, no superiority claim.

## Open action items

- [ ] Run the CSI-via-TRIBE pipeline (already built in `spikeprint/fmri.py`) once A100
  compute is available, to actually test the fMRI-grounded CSI construct rather than
  leaving it as a wired but unexercised slot.
- [ ] Either secure a license from the choices13k authors or drop it from the roadmap;
  currently it is the stated reason G8 fails rather than being merely unscored.
- [ ] Resolve the CSI-name normative tension the external critic flagged (the user's call,
  per memory) before any further paper-facing use of the term.
