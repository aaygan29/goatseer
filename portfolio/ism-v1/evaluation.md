# ism-v1: evaluation

- External home: `~/Desktop/Research/projects/Neuroscience/Neuro-AI/_SIBLING_consciousness-selfstate/interoceptive-self-model/`
  (grouped under the consciousness/self-state sibling program as of 2026-08-16; confirmed present
  with PREREGISTRATION.md, README.md, `ism/`, `modal_app.py`, `scripts/`, `cache_targets/`).
- Status: active
- Last scored: 2026-09-03
- Next re-score due: 2026-09-10

## One-line claim

Exploratory: a closed-loop self-model gives an LLM an encoder-read summary of its own
hidden state and trains self-prediction; the full Modal pipeline runs green on a mock
smoke test, but no real (non-mock) result has been produced yet.

## Gate scores

| Gate | Status | Note |
| --- | --- | --- |
| G1 provenance/leakage        | unscored (no evidence available; only mock-target runs exist so far) | |
| G2 seed variance (n>=5)      | unscored (no evidence available) | |
| G3 specification robustness  | unscored (no evidence available) | |
| G4 specificity ablation      | unscored (no evidence available) | |
| G5 confound control          | unscored (no evidence available) | |
| G6 mechanism/necessity       | unscored (no evidence available) | |
| G7 calibration                | unscored (no evidence available) | |
| G8 external validity          | unscored (no evidence available) | |
| G9 measurement reliability    | unscored (no evidence available) | |
| G10 reproducibility            | partial | `python3 -m modal run modal_app.py --mock --model Qwen/Qwen2.5-0.5B` runs end to end and green on mock (`project_interoceptive_self_model.md`), which is a real reproducibility positive control for the pipeline itself, but not for any scientific claim (mock T1=NaN, T2-T4 are noise by design). |
| G11 ethics/safety              | partial | No PHI; mock/synthetic data only so far. No documented refusal path for what the self-model reports back to the LLM. |
| G12 analytic integrity         | pass | Four falsification tests T1-T4 (faithfulness/causal/functional/integration) are preregistered in `PREREGISTRATION.md` before any real target data is used. |

### fMRI addendum

| Gate | Status | Note |
| --- | --- | --- |
| G-fMRI.1 per-participant CV        | unscored (no evidence available; TRIBE target adapter is ported but not yet validated on Modal) | |
| G-fMRI.2 sign-concordance binomial | unscored (no evidence available) | |
| G-fMRI.3 group-level significance  | unscored (no evidence available) | |

### LLM addendum

| Gate | Status | Note |
| --- | --- | --- |
| H1 refusal path                | unscored (no evidence available) | |
| H2 calibrated confidence       | unscored (no evidence available) | |
| H3 loyalty vector disclosure   | n/a | Not a loyalty-audit instrument. |

## Contribution to NEUROSPINE

Tuple field(s) this project could feed: `honesty_verdict` (self-model faithfulness is
directly an honesty-of-self-report construct), `sparse_circuit_id` (if the encoder
readout is treated as a mechanism handle). Nothing is validated to feed the tuple yet.

## Open action items

- [ ] Run `modal run modal_app.py --corpus 8 --p0-only` to de-risk TRIBE-adapter timing
  before any full-corpus attempt (direct unblock for G1/G10 on real data, per the memory's
  own next step).
- [ ] Swap in an instruct base model (mock T1=NaN is a tiny non-instruct model artifact,
  not a science result) so T1 can actually produce parseable self-reports.
- [ ] Once a real (non-mock) run exists, score G1-G6 against it; do not backfill scores
  from the mock run.
