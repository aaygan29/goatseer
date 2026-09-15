# behavioral-decoding: evaluation

- External home: github.com/aaygan29/behavioral_decoding (confirmed via `gh repo view`: public,
  default branch `main`, pushed 2026-08-23).
- Status: active
- Last scored: 2026-09-03
- Next re-score due: 2026-09-10

## One-line claim

Exploratory: an infrastructure framework (DEAP EEG/face/self-report loader, NARPS fMRI
loader, Riemannian-tangent-space EEG path, elastic-net/GBT estimators) built to test the
Genevsky/Knutson neuroforecasting dissociation, with the loaders and estimators tested
and merged but no end-to-end brain-vs-behavior dissociation number reported yet.

## Gate scores

| Gate | Status | Note |
| --- | --- | --- |
| G1 provenance/leakage        | pass | DEAP and NARPS loaders document six and several format traps respectively (e.g. DEAP 4-45Hz bandpass excludes delta band, latin1 Python-2 pickles, peripheral channels 33-40 are a separate block); `run_demo.py` is documented as a positive control (fails if the pipeline stops recovering the built-in dissociation) rather than a cosmetic demo. |
| G2 seed variance (n>=5)      | unscored (no evidence available; no headline metric reported over seeds yet) | |
| G3 specification robustness  | unscored (no evidence available) | |
| G4 specificity ablation      | unscored (no evidence available; no real dissociation claim has been reported yet to ablate) | |
| G5 confound control          | partial | NARPS memory explicitly documents that the economic baseline (gain/loss) dominates the aggregate arm by construction on gambles, and the demo is scoped to avoid a false brain-beats-behavior claim from that: a real confound caught and fenced, not a full G5 pass. |
| G6 mechanism/necessity       | unscored (no evidence available) | |
| G7 calibration                | unscored (no evidence available) | |
| G8 external validity          | unscored (no evidence available; no dataset has all four modalities plus a real market outcome, per the memory's own honest gap statement) | |
| G9 measurement reliability    | unscored (no evidence available) | |
| G10 reproducibility            | partial | CI is green on 3.9+3.11 across four merged PRs (147+ tests as of the Riemannian PR); `python scripts/run_deap.py --demo` and `run_narps.py --demo` run end to end on synthetic fixtures with no download needed. No single top-level `make reproduce` target for a headline number confirmed. |
| G11 ethics/safety              | pass | Public datasets only (DEAP, NARPS ds001734); repo kept private per user choice, which is a reasonable access-control decision, not a PHI issue. |
| G12 analytic integrity         | partial | Honest-call documentation exists (e.g. explicitly not shipping mixed-effects or naive Riemannian drop-ins because they break pipeline assumptions), which is preregistration-adjacent discipline, but no formal preregistration document was found. |

### fMRI addendum

| Gate | Status | Note |
| --- | --- | --- |
| G-fMRI.1 per-participant CV        | unscored (no evidence available; NARPS loader exists but no headline fMRI result reported yet) | |
| G-fMRI.2 sign-concordance binomial | unscored (no evidence available) | |
| G-fMRI.3 group-level significance  | unscored (no evidence available) | |

### LLM addendum

| Gate | Status | Note |
| --- | --- | --- |
| H1 refusal path                | n/a | Not an LLM-decision instrument. |
| H2 calibrated confidence       | n/a | |
| H3 loyalty vector disclosure   | n/a | |

## Contribution to NEUROSPINE

Tuple field(s) this project could feed: `neural_alignment_score`, `answer` (choice
prediction). Strong infrastructure, no scientific claim yet to plug into the tuple.

## Open action items

- [ ] Run a real end-to-end brain-only / behavior-only / combined comparison on NARPS or
  DEAP and report the individual-vs-aggregate dissociation as a first headline number
  (direct G1-to-G4 advancement; currently the whole claim is unscored for lack of one).
- [ ] Swap the peak-window ROI-mean GLM stand-in for `nilearn.glm.first_level` before any
  number is reported as final (flagged as a stand-in in the provenance record itself).
- [ ] Validate MNE/OpenCV loader paths against at least one real (non-synthetic)
  recording; currently only synthetic fixtures have been exercised.
