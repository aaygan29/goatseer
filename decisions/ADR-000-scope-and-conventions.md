# ADR-000-scope-and-conventions

## Status

Accepted, 2026-09-03.

## Context

NEUROSPINE is a new Neuro-AI program consolidating 18 portfolio projects under
a unified evaluation framework. At inception, the program needs a shared
understanding of scope, naming, decision-making process, and writing conventions
to avoid fragmentation and ensure reproducibility.

## Decision

### Program identity

- Program name: NEUROSPINE.
- Repository slug: NEW_REPO (internal, aayushgandhi/NEW_REPO on GitHub).
- Organization: aaygan29.

### In-scope portfolio projects at inception

Active (13): tribe-neuroprint, ism-v1, anesthesia-bridge, memoryprint,
behavioral-decoding, decision-phenotype, jspace-loyalty, mats-jlens, cultist,
wiring-not-weights, cortex-of-anyone, nacc-anticipation, bio-toolkit.

Proposed/earlier (5): warden, affectprint, spikeprint, globalsouthai,
pereverzev-neuro-extension.

Total: 18 projects.

### Instrument contract

The NEUROSPINE decision tuple has seven fields: answer, calibrated_confidence,
abstention_flag, loyalty_vector, sparse_circuit_id, neural_alignment_score,
honesty_verdict. Spec frozen in instrument/specs/contract-v0.md, subject to
ADR revision.

### Gate ladder v0

Twelve core gates (G1-G12) plus fMRI addendum (G-fMRI.1-3) and LLM addendum
(H1-H3). Gate specifications in gates/gate-ladder-v0.md. All changes to gate
definitions require ADRs.

### Rules

**Branch and PR**: All changes to main must go through branches and pull requests.
Force-push to main is prohibited. Code review required before merge.

**README with code**: Every code change must update or extend the relevant
README.md in the same commit or PR. README gaps are treated as definition-of-done
blockers.

**No em dashes**: All written content uses periods, commas, colons, or parens
instead of em dashes. ASCII only.

**Anonymization doctrine**: For double-blind submissions, maintain a separate
anonymized mirror (e.g., anonymous.4open.science) with methods, results, and
code identical but with author names, affiliations, and identifying commits
redacted. Applies only to repositories owned by the user.

**Retirement rule**: Two consecutive same-gate failures across greater than 14
days trigger a retirement ADR. Projects may be archived, redesigned, or moved
to proposed pending further development.

## Consequences

- Shared vocabulary and conventions reduce communication overhead.
- PR-gating ensures no regressions slip to main.
- README-with-code discipline keeps documentation in sync.
- Gate ladder provides a shared, testable evaluation standard.
- Anonymization doctrine prepares for rigorous peer review without compromising
  pre-submission visibility.
- Retirement rule prevents stalled projects from accumulating indefinitely.

The scaffold must be committed before the first real evaluation pass runs.
