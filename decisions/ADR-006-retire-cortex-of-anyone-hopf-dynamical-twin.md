# ADR-006: Retire cortex-of-anyone Hopf / Stuart-Landau dynamical-twin submodule

## Status

Accepted, 2026-09-03.

## Context

The first scoring pass flagged `portfolio/cortex-of-anyone/evaluation.md`
green overall (it holds the portfolio's cleanest fMRI-triad pass:
`G-fMRI.1/2/3` all real, 8 of 8 subjects positive, Wilcoxon p = 0.0039),
with one honest G6 fail on a specific submodule: the Hopf / Stuart-Landau
dynamical twin. The submodule is documented in the project itself as
failing to reproduce the validated consciousness signature it was
designed to model, and moving in the wrong direction under its own
arousal knob.

The individuation result (the project's G3 pass, and the reason
cortex-of-anyone is green overall) is unaffected.

## Decision

Retire the Hopf / Stuart-Landau dynamical-twin submodule from the
citable-evidence whitelist for NEUROSPINE. Specifically:

- The `SubjectAdapter` provider MUST NOT lift the Hopf twin as a
  component.
- The `MemoryDecoder` provider MUST NOT rely on the Hopf twin for
  reward-shift dynamics; the anchor is instead the Yaghoubi Nature
  hippocampal backward-shift paper directly.
- The `experiments/` directory does not scaffold a Hopf-based
  simulator.

Replacement path (from the scoring report's proposed next action):
replace the Hopf twin with an anesthesia-parameterized neural-mass
model. Whether that replacement lives in cortex-of-anyone or in
NEUROSPINE's `experiments/` is a future ADR.

## Consequences

- One planned extraction path (Hopf-based individuation of dynamic
  neural signatures) is closed.
- The individuation result itself remains the reference example for
  what "passing fMRI triad" looks like in the portfolio, and the
  `SubjectAdapter` still draws engineering pedigree from
  cortex-of-anyone for the per-subject calibration logic.
- No effect on Aim 1 or Aim 2. The Hopf twin was a stretch component,
  not a load-bearing one.

## Consequences NOT accepted

- We do not retire cortex-of-anyone. The overall project remains green
  and remains the reference exemplar for the fMRI triad in the
  portfolio.
- We do not claim the Hopf framework is wrong in general. This ADR
  only says this specific submodule fails its own validation and is
  not fit for NEUROSPINE use.

## Follow-ups

- Update `portfolio/cortex-of-anyone/evaluation.md` header to point at
  this ADR.
- Log the anesthesia-parameterized neural-mass model as a future ADR
  candidate once the pubmed / arxiv scan surfaces a suitable anchor.
