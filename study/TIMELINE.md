# Timeline

Total: ~28 weeks from instrument freeze to writeup, with decision
points at the end of Phase 2 and Phase 3 that can shorten or narrow
the remaining phases.

## Phase 0: instrument freeze (weeks 1 to 2)

- Freeze `Thought` contract, gate ladder v0, ADRs 001 to 006.
- Reference harness passes synthetic-first tests.
- Extraction protocol documented (ADR-003) and adopted.
- Literature index at ~34 external anchors after tick 3; pubmed scan
  queued to close the biomedical side to ~60 to 80.

Milestone: PR chore/scaffold-neurospine merged. Weekly report cadence
starts.

## Phase 1: individual-scale pipeline (weeks 3 to 8)

- ADR-003 extraction and re-verification for each of the five
  decoders.
- fMRIPrep + GLMsingle pipeline pinned in `experiments/preproc/`.
- Per-subject decoder fits on NSD and BMD training sessions.
- Goltermann/Huth triad computed per subject per decoder.

Milestone: Each decoder has a passing synthetic-first test and a
first real-data fit on at least one subject.

## Phase 2: replicability test (weeks 9 to 12)

- Test-retest analysis per subject per dimension on NSD and BMD.
- Preregistration locked at the start of the phase; no changes to
  the analysis plan after this point.
- Aim 1 outcome reported.

**Decision point.** If A1 fails on more than three subjects, narrow
scope to the surviving dimensions and rewrite the paper before
proceeding to Phase 3.

## Phase 3: group-scale transfer (weeks 13 to 20)

- Train A1 pipeline on HCP-YA training pool.
- Fine-tune on held-out subjects using the RAVEN protocol.
- Aim 2 outcome reported.

**Decision point.** If A2 fails on four or more dimensions, publish as
"individual scale only" and open a separate roadmap for group-scale
future work.

## Phase 4: specificity + Cognitive Dark Matter check (weeks 21 to 24)

- G4 ablation for each in-scope dimension x each Cognitive Dark Matter
  domain.
- Aim 3 outcome reported.

**Decision point.** If A3 reveals a confound on the headline
dimension, retract that dimension and re-run Phase 5 on the surviving
four.

## Phase 5: reporting (weeks 25 to 28)

- Draft manuscript per aim results.
- Release code, configs, derived datasets under AGPL-3.0.
- Submit; ship anonymized mirror for any double-blind venue.

## Weekly rhythm inside every phase

- Monday: publish `reports/weekly/YYYY-MM-DD.md` with portfolio
  scorecard deltas, top new papers, PRs opened/merged/blocked, and
  the single next experiment that would change any aim's verdict.
- Any tick that lands a PR, opens an ADR, or retires a project posts
  a one-paragraph status.
