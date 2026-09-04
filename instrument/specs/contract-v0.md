# NEUROSPINE Per-Prediction Contract (v0)

The NEUROSPINE harness returns a `Thought` tuple: a structured
prediction of a subject's cognitive state at one moment, from neural
recordings and behavioral signals.

Version 0 is frozen for the Phase 0 scaffold (see `study/TIMELINE.md`).
Changes are recorded as ADRs. The previous v0 auditor-tuple was
retired per ADR-004.

## Fields

| Field | Type | Definition | Gates | Failure mode if emitted without its gate |
| --- | --- | --- | --- | --- |
| subject | str | Subject identifier the prediction is about | (no gate; identity metadata) | Provenance loss |
| perceived_stimulus | Any \| None | What the subject saw / heard / attended to | G1, G6, G-fMRI.1, G-fMRI.2, G-fMRI.3 | Unverified provenance, unfalsifiable mechanism, or fMRI reliability triad failure would let a stimulus artifact masquerade as decoding |
| predicted_affect | dict[str, float] \| None | Valence, arousal, discrete emotion probabilities | G7, G9 | Uncalibrated affect or unreliable test-retest would let noise pass as affect prediction |
| predicted_decision | dict[str, Any] \| None | Choice and drift-diffusion parameters | G7, G8 | Uncalibrated or single-dataset only would leave the DDM prediction not externally valid |
| predicted_memory_state | dict[str, float] \| None | Recall probability and temporal-shift-of-encoding | G6, G-fMRI.1, G-fMRI.2, G-fMRI.3 | Mechanism unproven or reliability triad failure would let a memory-adjacent artifact pass |
| predicted_reward_signal | float \| None | Anticipation strength / valuation magnitude | G6, G-fMRI.1, G-fMRI.2, G-fMRI.3 | Same failure mode as memory: mechanism or reliability |
| confidence | dict[str, float in 0..1] | Per-dimension calibrated confidence | G7 | Uncalibrated confidence is worse than no confidence; the field must ship with G7 or not at all |
| abstention_flag | bool | True if the harness abstained on every attempted prediction this call | G7, G9, G-fMRI.1, G-fMRI.2, G-fMRI.3 | Wrong abstention rule silently ships bad predictions or hides good ones |
| unmeasured_domains | list[str] | Cognitive Dark Matter domains explicitly not attempted | G12 | Without analytic integrity, unmeasured domains become hidden claims |
| is_subject_specific | bool | True iff a subject-specific decoder was used vs group model fallback | G8 | Without external validity, subject-specific claim overstates transfer |

## Invariants enforced at construction

- `confidence[dim]` is in `[0.0, 1.0]` for every reported dimension.
  Values outside range raise `ValueError`.
- `unmeasured_domains` contains only labels from
  `COGNITIVE_DARK_MATTER_DOMAINS`. Foreign labels raise `ValueError`.
- If `abstention_flag=True`, no prediction field may be populated.
  Populated prediction with abstention raises `ValueError`.

## Cognitive Dark Matter taxonomy

Fixed tuple (Mineault, Griffiths, Escola, arXiv:2603.03414):

- `metacognition`
- `cognitive_flexibility`
- `lifelong_learning`
- `reasoning`
- `social_reasoning`
- `emotional_intelligence`

The harness populates `unmeasured_domains` with all six by default.
Adding a domain to the "measured" side requires an ADR revising Aim 3.

## Harness contract

`Neurospine.predict(subject: str, recordings: dict, context: dict) -> Thought`

Given a subject id, a `recordings` dict (fMRI, EEG, behavioral,
physiological data), and a `context` dict (task, stimulus history,
timing), assemble and return a `Thought`. The harness:

1. Consults the caller-provided `ProviderGates` to short-circuit any
   provider whose gates have not fully passed.
2. Calls each active provider in a fixed order.
3. Consults the abstention provider per dimension; a positive returns
   sets the whole `Thought` to abstain and clears every prediction.
4. Populates `confidence` for every dimension where a real prediction
   was emitted AND the calibration gate has passed.
5. Always populates `unmeasured_domains` with the full Cognitive Dark
   Matter taxonomy.

## v0 -> v1 revision triggers

- Any Cognitive Dark Matter domain is moved to the measured side
  (would require rewriting Aim 3).
- The abstention rule changes (would require an ADR after Phase 2
  first-experience data).
- Multi-timepoint prediction is added (currently one prediction per
  call; a session-level prediction would extend to a `ThoughtStream`
  type).
