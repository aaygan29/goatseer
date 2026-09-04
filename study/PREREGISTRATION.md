# Preregistration (draft)

Ready to lock at OSF or the venue-specific preregistration service
before any Phase 2 or later analysis touches real data. Every field
below has a locked value at lock time; nothing is left ambiguous.

## Study title

NEUROSPINE: individual and group scale thought and behavior prediction
from neural and behavioral recordings.

## Authors

To be finalized before lock. Aayush Gandhi (lead).

## Hypotheses

- **H1 (Aim 1)**: Within-subject test-retest Spearman rho on at least
  three of five predicted dimensions exceeds 0.6 after Goltermann/Huth
  correction, on both NSD and BMD.
- **H2 (Aim 2)**: Held-out-subject fine-tuned performance is within
  40 percent of within-subject A1 performance on at least three
  dimensions, with the RAVEN transfer protocol.
- **H3 (Aim 3)**: Zero of the six Cognitive Dark Matter domains
  survive the G4 specificity ablation as confounds of any in-scope
  dimension.

## Sample and datasets

- Primary A1: NSD subjects 1 to 8, BMD subjects 1 to 10.
- Aim 2: HCP-YA random sample of N = 200 for the training pool;
  20 held-out subjects for fine-tune evaluation.
- Affect A1: DEAP subjects 1 to 32.
- Reward: ds005479 first 60 subjects for training, next 20 held out.
- Reliability: ds003171 all 26 subjects.

## Exclusions

- Sessions with more than 20 percent motion or artifact rejection are
  excluded per-trial from analysis, not per-session.
- Subjects with fewer than the preregistered minimum trials per
  session are excluded from that session.

## Analysis plan

See `ANALYSIS_PLAN.md`. Locked here by reference.

## Multiple comparisons and correction

Benjamini and Hochberg FDR 0.05 across the five prediction dimensions
per subject. See `ANALYSIS_PLAN.md`.

## Success and failure criteria

Per aim, see `AIMS.md`. Both success and failure criteria are
publishable outcomes.

## Deviations

Any deviation from the locked plan is declared explicitly in the
manuscript with a paragraph naming the deviation, when it happened,
and why. No silent deviations.

## Timeline

Phase 0 to Phase 5 per `PROTOCOL.md`. Preregistration lock date is at
the start of Phase 2 (week 9 in the timeline).

## Data availability

All derived datasets, model weights, configs, and analysis code
released under AGPL-3.0 at the NEW_REPO GitHub repository within 60
days of publication.

## Preregistration lock statement (to be added at lock)

We commit to executing the analyses described above on the datasets
described above. Any additional exploratory analyses are labeled as
such and separated from the confirmatory results.
