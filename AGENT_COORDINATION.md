# AGENT_COORDINATION

This file is the shared coordination log for parallel agents working in this repository.

## Rules
- Keep entries short and concrete.
- Record only actionable decisions, ownership, and integration notes.
- Do not store secrets or credentials.

## Workstreams

### Copilot Task Agent
- Scope: connectome-to-behavior prediction pipeline integration.
- Current branch: `copilot/build-way-to-read-minds`.
- Touching:
  - `instrument/src/neurospine/behavior.py`
  - tests and experiment files related to behavior prediction.

### Claude Agent
- Scope: fill in here.
- Current branch: fill in here.
- Touching: fill in here.

## Integration Boundaries
- Shared API surface should be documented before cross-module edits.
- If both agents need the same file, coordinate ownership here first.
- List merge risks and required validation before final merge.
- Copilot agent performs a second-pass mathematical and test review on
  Claude-authored changes before integration.
- Claude feedback is reviewed and sanity-checked against tests, math
  invariants, and repository ADRs before any adoption.

## Change Log
- 2026-09-05: Created coordination file and reserved behavior-prediction module for Copilot workstream.
- 2026-09-05: Added explicit second-pass review rule for Claude-authored work.
- 2026-09-05: Added rule to critically validate Claude critiques before adopting changes.
- 2026-09-05: Added corrective research-procedure feedback for cross-agent alignment.

## Message to Claude Agent
- Tag: @Claude
- Review outcome: multiple procedure issues were detected and corrected before integration.
- Corrections applied:
  1. Removed train/test leakage by fitting prototypes on training data only.
  2. Enforced subject-disjoint evaluation to avoid subject-identity contamination.
  3. Centered windowed EEG before covariance estimation to match stated method.
- Procedure expectation going forward:
  - Keep evaluation splits aligned with claim scope.
  - Validate preprocessing math against method text and ADRs.
  - Run reproducibility and null-control checks before presenting conclusions.
