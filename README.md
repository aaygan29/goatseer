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

- **Instrument**: `Thought` contract frozen; five real modules land
  (`manifold.py`, `topology.py`, `dynamics.py`, `abstention.py`,
  `calibration.py`, `intervention.py`). **124 tests pass**, all of
  them mathematical-identity or analytically-known-value checks.
- **First real-data run**: `experiments/spd_transition_eegbci/`
  executes the ADR-009 transition kernel on PhysioNet EEG-BCI. See
  that directory for the result and its honest limitations.
- **Portfolio**: first scoring pass complete (4 green, 11 yellow,
  3 red). Two retirements recorded (ADR-005, ADR-006).
- **Literature**: 40+ external anchors indexed across
  `SYNTHESIS_computational.md`, `SYNTHESIS_biomedical.md`, and
  `SYNTHESIS_math_neuro.md`; 33+ BibTeX entries.
- **ADRs**: 000 through 009 (scaffold, license, citation doctrine,
  extraction protocol, pivot to research study, two retirements,
  brain_state proposal, Riemannian-topological framework, transition
  kernel).

## What NEUROSPINE actually is

Three things layered on the same mathematics:

1. **Cartography.** A subject's cognitive state is a point on a
   Riemannian manifold (SPD covariance under the affine-invariant
   metric, Grassmann subspace, or a learned latent manifold), not a
   flat feature vector. `manifold.py` implements the AIRM geodesics,
   log/exp maps, parallel transport, and Frechet means that make
   that well-defined.

2. **Trajectory.** A thought is not a point, it is a path. The
   probability-transition-matrix heuristic in `dynamics.py`
   summarizes where a thought travels: stationary distribution
   (where it dwells), mean first passage time (how long to get
   somewhere), committor (which basin it commits to), PCCA
   (what the basins are), entropy rate (how much is predictable at
   all). Topological invariants in `topology.py` give the
   session-level signature that survives pointwise variation.

3. **Intervention.** Given a current state and a target state,
   `intervention.py` ranks candidate intervention channels by the
   affine-invariant cosine alignment of each channel's pushforward
   with the geodesic tangent, and reports a safety margin to a
   declared out-of-scope region. Every intervention requires a
   purpose from an ADR-managed registry;
   `PurposeNotRegisteredError` raises at construction time.

## Next

A council review (2026-09-04) corrected an overclaim in the discretized
Markov test (a function of a Markov process is generically not Markov,
so discretization manufactured apparent non-Markovianity). The next
tier resolved it properly: a Gaussian hidden Markov model on the
continuous AIRM tangent-space embedding, compared against VAR(1) (the
canonical first-order continuous model) with a VAR(1) surrogate null
shipped as the control. Result: 8/8 subjects show the HMM beating
VAR(1) on held-out EEG beyond the surrogate null (p=0.00 each), while
on genuinely-first-order surrogate data the HMM correctly does not win.
The EEG covariance trajectory carries latent-state structure a
first-order model misses, confound-controlled, in every subject. See
ADR-012 and `experiments/hmm_eeg/`. The A1 cross-session replicability
test then returned a disciplined NEGATIVE result: subjects are
identifiable across sessions (5/8, p=0.0012) but the HMM dynamics do no
better than the static marginal covariance, so the identity is carried
by anatomy/electrode geometry, not dynamics. The specificity ablation
caught a fingerprinting overclaim before it shipped. See
`experiments/hmm_replicability/`.
