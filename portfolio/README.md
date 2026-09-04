# NEUROSPINE Portfolio

Each subfolder holds one project's evaluation file: `<slug>/evaluation.md`.

## Evaluation protocol

Every evaluation is scored against gates/gate-ladder-v0.md. The evaluation.md
template specifies 12 gates (G1-G12), optional fMRI addendum (G-fMRI.1-3), and
optional LLM addendum (H1-H3).

Each gate is marked one of:

- **unscored**: First time scoring, or score is stale (>7 days old).
- **pass**: Gate conditions met.
- **fail**: Gate conditions not met; root cause noted.
- **n/a**: Gate does not apply to this project.
- **blocked**: Cannot score until a dependency gate is resolved.

## Refresh schedule

Evaluations are refreshed on any tick where the score is > 7 days stale. A new
evaluation.md is committed with updated timestamps and re-scored gates.

## Retirement rule

Two consecutive same-gate failures across > 14 days trigger a retirement ADR
(decisions/). The project may be archived, redesigned, or moved to proposed/
pending further development.
