# ADR-007: Add `brain_state` field to the `Thought` tuple

## Status

Proposed, 2026-09-04. Adoption gated on the first EEG-fMRI concurrent
recording entering the study (Phase 1 of `study/TIMELINE.md`).

## Context

Two literature anchors indexed this week (2026-09-04) argue that the
current `Thought` tuple is missing a first-class field:

- `pubmed-42618509` Miller, Brincat, Roy 2026 J. Neuroscience "Analog
  Cognition and Consciousness". Cognition and consciousness arise
  from bidirectional interactions between neuronal spiking and
  rhythmic electric field activity (brain waves). Brain waves exert
  mesoscale influence over neural excitability, support analog
  computation, and route multifunctional neurons into
  context-dependent roles. Consequence: the same spiking read means
  different things under different mesoscale wave states.
- `pubmed-42149756` Sung et al. 2026 IEEE TNSRE "EffortNet". Alpha
  power (8-13 Hz) is a validated objective biomarker of listening
  effort; the same speech input at different alpha levels produces
  different downstream decoding.

Together these argue that NEUROSPINE's prediction dimensions
(perceived stimulus, affect, decision, memory, reward) should be
conditioned on the concurrent brain state, and that the state itself
should be a reported output alongside the predictions. Not doing so
lets a decoder pool across states, which is exactly the failure mode
Miller/Brincat/Roy warn against.

## Decision

Add a `brain_state` field to the `Thought` tuple with the following
shape:

```python
brain_state: dict[str, float] | None = None
```

where the dict may carry any subset of:

- `alpha_power` (8 to 13 Hz band power, normalized).
- `beta_power` (13 to 30 Hz).
- `theta_power` (4 to 8 Hz).
- `gamma_power` (30 to 90 Hz).
- `phase` (dominant oscillation instantaneous phase, in `[0, 2*pi)`).
- `cross_frequency_coupling` (theta-gamma PAC or similar scalar).
- `pupil_diameter` (as a fMRI-adjacent arousal proxy when EEG is
  absent).

`brain_state` is populated when:

- The `recordings` dict contains an `eeg` key with concurrent EEG, OR
- The `recordings` dict contains a `physio` key with pupil / heart
  rate that can be mapped to an arousal-band scalar, OR
- The instrument runs a wave-state estimator on the fMRI itself
  (deferred; see Consequences NOT accepted).

`brain_state` is `None` otherwise, and the `AbstentionProvider` then
falls back to pooled-state evaluation.

Gate binding:

```python
FIELD_GATES["brain_state"] = ["G9"]
```

Rationale: `brain_state` is a measurement, so it needs measurement
reliability (G9) but does not need mechanism gates itself. Downstream
predictions that condition on `brain_state` still need their own
gates.

## Consequences

- `contract.py` gets a new field; `Thought.__post_init__` gains a
  validation for the state dict keys.
- `harness.py` gets a `BrainStateEstimator` provider (new abstract
  Protocol in `providers.py`) that the harness calls before each
  prediction dimension.
- `GoltermannHuthAbstention` gains a per-state-bin evaluation path:
  when `brain_state` is populated, the triad is evaluated on the
  subset of calibration data matching the state bin.
- The instrument spec v0 is not broken; adding a new field with
  `None` default is backward-compatible for existing tests.
- The Cognitive Dark Matter declaration in `unmeasured_domains`
  remains unchanged; `brain_state` is a mesoscale measurement, not
  a cognitive-content prediction.

## Consequences NOT accepted

- We do not attempt to estimate wave state from fMRI alone in this
  ADR. That is a future ADR pending literature (there is preliminary
  work on inferring EEG bands from BOLD via HRF deconvolution;
  needs its own pubmed round).
- We do not add `brain_state` as a required input; `None` is a valid
  state and the harness falls back to pooled evaluation.
- We do not open Aim 4 for wave-state prediction as a target. That
  is out of scope for the current study; wave state is an input
  covariate, not an outcome.

## Adoption trigger

This ADR is proposed but not yet accepted. It becomes accepted when
the first EEG-fMRI concurrent recording (from NATVIEW or an
equivalent dataset per `study/DATA_SOURCES.md`) is wired into
`experiments/`. At that point:

- Move ADR-007 status to "Accepted (YYYY-MM-DD)".
- Bump the contract to v1 or add a v0.1 addendum spec.
- Regenerate the test suite to cover the new field.

## Follow-ups

- Track the fMRI-to-wave-state estimation literature in a future
  pubmed round; if a robust anchor exists, open ADR-008.
- Add a note to `study/METHODS.md` that predictions on the same
  subject at different brain states should not be pooled without
  documenting the pooling.
