# study/

NEUROSPINE research study. This directory holds the study's protocol,
aims, methods, analysis plan, preregistration draft, ethics, and timeline.

The `instrument/` directory holds the reference code that implements the
analysis pipeline the protocol here specifies. The `portfolio/` directory
holds the engineering pedigree of each component. The `literature/`
directory holds the external anchors the protocol cites.

## What NEUROSPINE studies

Given a subject's neural recordings (fMRI, EEG, spikes where available)
and behavioral signals (choices, response times, face and physio), can we
predict the subject's cognitive state:

- What they are perceiving (visual, auditory, semantic).
- What they are feeling (valence, arousal, discrete emotion).
- What they are deciding (choice + drift-diffusion parameters).
- What they are remembering (recall probability, temporal shift).
- What they anticipate rewarding.

At two scales, honestly:

- **Individual scale**, replicably. Same subject, same day and across
  days, same task, same predictions within a documented tolerance.
- **Group scale**, with quantified degradation. Cross-subject transfer of
  the individual pipeline, with the transfer cost measured, not hidden.

And with a declared frontier of what NEUROSPINE does not attempt to
predict, from the Cognitive Dark Matter taxonomy.

## Files

- `AIMS.md` the three aims A1, A2, A3.
- `PROTOCOL.md` the top-level study protocol.
- `METHODS.md` data sources, preprocessing, decoders, analysis.
- `ANALYSIS_PLAN.md` statistical analysis plan with power considerations.
- `PREREGISTRATION.md` draft preregistration, ready to lock before data
  collection.
- `DATA_SOURCES.md` the public datasets the study uses.
- `ETHICS.md` ethics, consent, IRB assumptions, red-team notes.
- `TIMELINE.md` phases, milestones, decision points.
- `LITERATURE_MAP.md` mapping every load-bearing external citation to the
  study component it supports.

## Doctrine

- Every load-bearing claim cites external published work per ADR-002.
- Every fMRI-grounded prediction passes the Goltermann/Huth triad before
  it is reported as a claim.
- Aayush's prior projects contribute engineering only, re-verified
  externally per ADR-003 before feeding any gate.
- Individual-scale replicability is measured, not asserted. Test-retest
  on the same subject is the first gate before any cross-subject work.
- The Cognitive Dark Matter frontier is declared, not hidden.
