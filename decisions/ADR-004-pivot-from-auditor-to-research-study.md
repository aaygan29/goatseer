# ADR-004: Pivot from AI auditor to thought-prediction research study

## Status

Accepted, 2026-09-03.

## Context

The initial scaffold framed NEUROSPINE as an AI auditing instrument: given
a `(model, subject, task)` triple, return a `Decision` tuple with answer,
calibrated confidence, abstention, loyalty vector, sparse circuit id,
neural alignment, and honesty verdict. Aayush corrected on 2026-09-03:

> That is not what we needed you to make. I needed you to make a
> synthesized combined new neuro-ai project that allowed you to basically
> predict thought patterns and read minds, in essence, based on neural
> activity recordings and behavioral signals and so on from all the
> papers previously provided.

And shortly after, sharpening scope:

> You need to take whatever is strongest from the tools already made and
> build up a much stronger program right? You don't want to run into
> this whole circular issue where there could be an error in our prior
> work that we didn't notice. Do whatever you can to avoid that
> situation but still proceed with original design.

And again, expanding scope:

> When I actually needed you to pull together the entire neuro-ai works
> along with the papers that I sent along with your overall reviews and
> reading of a lot more arxiv papers and pubmed papers about brain
> mechanics and data analytics and topology and biomechanics and physics
> and neuroscience and so on that would enable you to do these kinds of
> behavioral thought predictions on an individual scale replicably and
> on a larger scale that would also be a new research study.

NEUROSPINE is not an auditor. It is a new research study for individual
and group scale thought / behavior prediction from neural + behavioral
recordings, synthesized from the seed literature, Aayush's prior Neuro-AI
portfolio (engineering only, per ADR-002), and a wider literature scan
across brain mechanics, network topology, biomechanics, physics of
neural systems, computational neuroscience, and data analytics for
neural time series.

## Decision

1. **Rename the primary output.** The per-decision `Decision` tuple is
   retired. NEUROSPINE returns a `Thought` tuple: `perceived_stimulus`,
   `predicted_affect`, `predicted_decision`, `predicted_memory_state`,
   `predicted_reward_signal`, plus `confidence`, `abstention_flag`,
   `unmeasured_domains`, `is_subject_specific`.

2. **Rename the entry point.** `Neurospine.decide(model, subject, task)`
   is retired. Replaced by `Neurospine.predict(subject, recordings,
   context)`.

3. **Add a `study/` directory** housing the research study protocol:
   `AIMS.md`, `PROTOCOL.md`, `METHODS.md`, `ANALYSIS_PLAN.md`,
   `PREREGISTRATION.md`, `DATA_SOURCES.md`, `ETHICS.md`, `TIMELINE.md`,
   `LITERATURE_MAP.md`. The instrument in `instrument/` is the reference
   analysis code that implements the protocol.

4. **Expand the literature scan** to cover brain mechanics, network
   topology (persistent homology of neural time series), physics of
   neural systems (statistical mechanics of neural populations),
   biomechanics of neural signals, and computational neuroscience.
   Target ~50 to 80 external anchors, versus the initial 7 seed
   papers. Delivered via two systematic crawls (pubmed + biorxiv, then
   arxiv) whose outputs land in `literature/SYNTHESIS_biomedical.md`
   and `literature/SYNTHESIS_computational.md`.

5. **Preserve the survivors.** Gate ladder v0, ADR-002 citation
   doctrine, ADR-003 extraction protocol, portfolio evaluation
   structure, `issues_to_open.md`, `MEMORY_LINKS.md` all carry over
   unchanged. The `Thought` contract inherits the gated short-circuit
   design from the retired `Decision` contract: the harness cannot
   emit a prediction whose gates have not passed.

6. **Update the reference harness accordingly.** Providers are now
   `PerceptionDecoder`, `AffectDecoder`, `DecisionDecoder`,
   `MemoryDecoder`, `RewardDecoder`, `SubjectAdapter`,
   `CalibrationProvider`, `AbstentionProvider`. Reference stubs return
   None and fail gates by construction so the harness cannot ship
   claims from a stubbed provider.

7. **The LLM addendum in the gate ladder** (H1, H2, H3) is retained
   but reoriented: H1 becomes the abstention rule applied to
   NEUROSPINE predictions, not to an LLM output. H2 and H3 are folded
   into G7 (calibration) and G12 (analytic integrity) for the
   thought-prediction framing. See ADR-007 (planned) for the v1 gate
   ladder revision.

## Consequences

- All of the prior contract-side auditor code is superseded.
  Compiled bytecode caches removed via `make clean`.
- Portfolio evaluations still score against the same gate ladder v0.
  The `Contribution to NEUROSPINE` line in each `evaluation.md` now
  refers to a `Thought` tuple field, not a `Decision` tuple field.
  The mapping is spelled out in the memory
  `[[project-neurospine-semantics]]`.
- The reference harness passes 30 synthetic-first tests under the new
  contract; previous 25 tests deleted with the auditor semantics.
- The `study/` directory and the expanded literature index are the
  deliverable of the current sprint. The instrument is the companion.
- Timeline (per `study/PROTOCOL.md`) targets ~28 weeks from instrument
  freeze to writeup.

## Consequences NOT accepted

- We do not throw away the earlier scaffold. Gate ladder, ADRs, and
  portfolio structure carry over. Only the semantic layer changed.
- We do not abandon the fMRI-focus. The Goltermann/Huth triad remains
  load-bearing for every fMRI-grounded prediction.
- We do not scope NEUROSPINE to any single modality. Neural and
  behavioral inputs are co-equal.
