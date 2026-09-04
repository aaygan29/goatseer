# NEUROSPINE (working name: NEW_REPO)

Unified Neuro-AI program repository. Owner: Aayush Gandhi (aaygan29).

This repository consolidates the strongest surviving pieces of the Neuro-AI
portfolio into one instrument, tracks every project against a versioned gate
ladder, and maintains a living literature index that continuously re-scores
what should be built, sharpened, or retired.

## Layout

- `portfolio/` one folder per in-scope project, each with an `evaluation.md`
  scored against the current gate ladder in `gates/`.
- `literature/` one structured note per paper, plus `references.bib`.
- `gates/` the versioned gate ladder used to accept or retire work.
- `instrument/` the NEUROSPINE instrument itself: spec, source, tests.
- `experiments/` runnable, reproducible experiments. Every real-data claim is
  preceded by a synthetic ground-truth control.
- `reports/weekly/` Monday auto-report of portfolio deltas and new literature.
- `decisions/` ADRs for every scope change or project retirement.
- `issues_to_open.md` queue of GitHub actions that need auth or human review
  before they can fire.

## Contract of the instrument

Given `(model, subject, task)`, NEUROSPINE returns a per-decision tuple:

```
{
  answer,                    # the model's decision
  calibrated_confidence,     # conformal, subject-conditional
  abstention_flag,           # honesty gate; refuse when unsupported
  loyalty_vector,            # per-source alignment (jspace-loyalty)
  sparse_circuit_id,         # DreamerV3-style handle on the mechanism
  neural_alignment_score,    # per-subject encoder pass/fail
  honesty_verdict            # WARDEN-style H1/H2/H3
}
```

Every field must have a passing gate before it ships. See
`instrument/specs/contract-v0.md`.

## Cadence

Each tick runs one of, in priority order: (1) index a new paper, (2) refresh a
stale `evaluation.md`, (3) implement a small unambiguous change on a portfolio
repo, (4) close an instrument spec gap test-first, (5) crawl new literature.
Weekly report every Monday under `reports/weekly/`.

## Hard rules

- No em dashes in any writing produced by or for this repo.
- Never push or force-push to `main`; branch and PR only.
- README updates ship in the same commit as the code they document.
- Any fMRI-grounded claim must pass the Goltermann/Huth robustness triad
  before it enters a paper draft or a portfolio README as a claim, not a
  hypothesis.
- Aayush's own prior work is exploratory unless it lives under
  `Neuro-AI/submissions/` or `MLCB_2026_submission/`.
- For double-blind submissions, ship the `anonymous.4open.science` mirror.

## Status

Scaffold only. See `reports/weekly/2026-09-07.md` for the first placeholder
report. Instrument code is unwritten; portfolio evaluations are stubs pending
their first real scoring pass.
