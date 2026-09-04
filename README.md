# NEUROSPINE (repo slug: NEW_REPO)

Individual and group scale thought / behavior prediction from neural
recordings and behavioral signals. Owner: Aayush Gandhi (aaygan29).

NEUROSPINE is a new research study synthesized from three inputs:

1. Aayush's prior Neuro-AI portfolio (13 active + 5 proposed projects),
   contributing engineering only (never authority) per ADR-002.
2. A seed literature set (MEIcoder, RAVEN, DreamerV3 sparse memory,
   hippocampal backward-shifted reward, Goltermann/Huth/Buchel BOLD-CMRO2
   reanalysis, Cognitive Dark Matter).
3. An expanded literature scan across brain mechanics, network topology,
   physics of neural systems, computational neuroscience, and data
   analytics for neural time series (~34 additional external anchors
   as of 2026-09-04; biomedical side pending pubmed retry).

## What NEUROSPINE studies

Given a subject's neural recordings and behavioral signals, predict:

- What they are perceiving (`perceived_stimulus`).
- What they are feeling (`predicted_affect`: valence, arousal, discrete).
- What they are deciding (`predicted_decision`: choice + DDM parameters).
- What they are remembering (`predicted_memory_state`: recall probability,
  temporal shift).
- What they anticipate rewarding (`predicted_reward_signal`).

Each with calibrated `confidence`, an `abstention_flag`, a declared
`unmeasured_domains` list from the Cognitive Dark Matter taxonomy, and
an `is_subject_specific` flag telling whether the harness used a
per-subject decoder or a group fallback.

At two scales, honestly:

- **Individual scale** (Aim 1), replicably: same subject same task
  same prediction within a documented tolerance across sessions.
- **Group scale** (Aim 2), with the transfer cost quantified, not
  hidden.

And with the Cognitive Dark Matter frontier declared, not smuggled
(Aim 3).

## Layout

- `study/` research study protocol, aims, methods, analysis plan,
  preregistration, ethics, timeline, data sources, literature map.
- `instrument/` reference analysis code (`neurospine` package) + tests.
- `portfolio/` per-project evaluation dossier scored against the gate
  ladder.
- `literature/` per-paper structured notes + `references.bib` +
  synthesis docs.
- `gates/` versioned gate ladder.
- `experiments/` runnable experiments, one Makefile target each.
- `reports/weekly/` Monday scorecard.
- `reports/first-scoring-pass-2026-09-03.md` first cross-cutting
  portfolio scoring report (4 green, 11 yellow, 3 red).
- `decisions/` ADRs (000 through 006 as of 2026-09-03).
- `issues_to_open.md` queued GitHub actions and human-in-the-loop
  items.

## Running the instrument

```
make install-dev
make test           # full suite
make test-synthetic # synthetic-first tests only
make lint
```

`Neurospine.predict(subject, recordings, context)` is the public entry
point. Every field in the returned `Thought` is gated per
`FIELD_GATES` in `instrument/src/neurospine/contract.py`. Reference
providers fail every gate by construction, so a stubbed harness
cannot ship a prediction as a claim.

## Hard rules

- No em dashes in any writing produced by or for this repo.
- Never push or force-push to `main`; branch and PR only.
- README updates ship in the same commit as the code they document.
- Any fMRI-grounded prediction must pass the Goltermann/Huth
  robustness triad before it enters a paper draft or a portfolio
  README as a claim, not a hypothesis.
- For any double-blind submission, ship the `anonymous.4open.science`
  mirror.

## Citation doctrine (ADR-002)

Every load-bearing design choice, method, gate, or metric in
NEUROSPINE is anchored to already-published external work. The
literature index under `literature/` is the citation source of first
resort.

Aayush's prior projects are treated as engineering provenance, not
authority. Code lifted from a prior project is named in git history
and in the source project's `portfolio/<slug>/evaluation.md`, but
never cited as the reason a method is correct. Before an extracted
method can raise any gate in NEUROSPINE, it must pass a fresh
external check per ADR-003.

This rules out the circular-error risk where an undetected bug in a
prior project silently props up a NEUROSPINE claim.

## Status (2026-09-04)

- Phase 0 (instrument freeze): in progress. `Thought` contract frozen;
  reference harness passes 30 synthetic-first tests.
- First portfolio scoring pass complete: 4 green, 11 yellow, 3 red.
- 34 external literature anchors indexed; biomedical side pending
  pubmed retry after rate-limit reset.
- ADRs 000 through 006 accepted (scaffold, license, citation doctrine,
  extraction protocol, pivot from auditor to study, two retirements).
- Next: complete pubmed synthesis, then advance the highest-leverage
  gate gaps flagged by the first scoring pass
  (`G-fMRI.2` sign-concordance binomial for `anesthesia-bridge` and
  `decision-phenotype`).
