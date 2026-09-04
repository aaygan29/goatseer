# pereverzev-neuro-extension: evaluation

- External home: none; not the user's own repo. The base result being extended is Igor
  Pereverzev's (not affiliated with Aayush), documented on his Substack/LessWrong. No code, plan
  document, or repo for the extension itself was found this pass.
- Status: proposed (discussed only; not started per memory)
- Last scored: 2026-09-03
- Next re-score due: 2026-09-10

## One-line claim

Not started: a plan to port Pereverzev's validated relocation-vs-collapse and
Stein's-lemma detection-latency result (measured on SpikeGPT's latent space) onto real
neurodata instead of a language model's latent space.

## Gate scores

No code exists for this project. Every gate is unscored because there is nothing yet to
score, not because anything has failed.

| Gate | Status | Note |
| --- | --- | --- |
| G1 provenance/leakage        | unscored (no evidence available; no code or data plan exists yet) | |
| G2 seed variance (n>=5)      | unscored (no evidence available) | |
| G3 specification robustness  | unscored (no evidence available) | |
| G4 specificity ablation      | unscored (no evidence available) | |
| G5 confound control          | unscored (no evidence available) | |
| G6 mechanism/necessity       | unscored (no evidence available) | |
| G7 calibration                | unscored (no evidence available) | |
| G8 external validity          | unscored (no evidence available) | |
| G9 measurement reliability    | unscored (no evidence available) | |
| G10 reproducibility            | unscored (no evidence available) | |
| G11 ethics/safety              | unscored (no evidence available) | |
| G12 analytic integrity         | unscored (no evidence available) | |

### fMRI addendum

| Gate | Status | Note |
| --- | --- | --- |
| G-fMRI.1 per-participant CV        | unscored (no evidence available; not yet decided whether the neuro extension will use fMRI, EEG, or another modality) | |
| G-fMRI.2 sign-concordance binomial | unscored (no evidence available) | |
| G-fMRI.3 group-level significance  | unscored (no evidence available) | |

### LLM addendum

| Gate | Status | Note |
| --- | --- | --- |
| H1 refusal path                | n/a | The base result is about a hidden signal evading a monitor, not an honesty-gated decision instrument as currently scoped. |
| H2 calibrated confidence       | n/a | |
| H3 loyalty vector disclosure   | n/a | |

## Citation note

Pereverzev's own base result (retrain-vs-frozen monitor test; Stein's-lemma detection
bound; Part 1's flawed metric self-retracted in Part 2) is a third party's published,
external work, not Aayush's, so it is citable as an established finding on its own terms
once the extension is planned. Any claim from the extension itself is unscored/exploratory
until built.

## Contribution to NEUROSPINE

Tuple field(s) this project could feed (if built): `sparse_circuit_id` (a relocation-vs-
collapse detection signature is a mechanism-handle candidate). Currently feeds nothing.

## Open action items

- [ ] Decide the target modality (fMRI, EEG, or another real neurodata source) before any
  code is written; this determines whether the fMRI addendum triad will apply.
- [ ] Write a one-page plan naming the specific dataset, the retrain-vs-frozen monitor
  analog in neural terms, and the Stein's-lemma detection-latency analog, before writing
  any code: this is the concrete next step that would move this out of "not started."
- [ ] Keep this project clearly separate from the Terminal-Bench-Science task proposals in
  any outreach material, per the existing memory instruction.
