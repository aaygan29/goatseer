# Gate ladder v1 addendum

Addendum to `gate-ladder-v0.md` capturing gaps surfaced by the first
scoring pass on 2026-09-03. The base ladder is unchanged; this file
overrides only where it explicitly says so, and is folded into a full
v1 rewrite once a second scoring pass either confirms these overrides
or supplies new ones.

## G2 (seed variance): non-stochastic pipelines

**Problem:** G2 requires `n >= 5` seeds. Several strong portfolio
projects use deterministic pipelines on fixed real datasets where the
"seeds" concept does not apply.

**Override:** For a deterministic pipeline (fixed dataset, fixed
preprocessing, linear / convex fit) that does not admit multiple
seeds:

- G2 passes when either of the following is reported:
  - Cross-validation fold variance across at least 5 folds, with mean
    and standard deviation.
  - Cross-dataset replication on at least one independent public
    dataset, with paired-metric mean and standard deviation.
- G2 is marked `n/a` (not `unscored`) when the claim itself is a
  single-dataset descriptive result that does not admit either
  resampling axis. The claim is then downgraded from `pass` to
  `partial` on G8 (external validity) until an independent dataset
  arrives.

## G-fMRI.2 (sign-concordance binomial): computed vs unscored

**Problem:** Multiple projects have the raw per-participant directional
data required but never computed the binomial test explicitly, leaving
G-fMRI.2 stuck at `unscored` despite ingredients existing.

**Override:** When per-subject directional data are on disk, G-fMRI.2
`unscored` is a bug. The scoring must either compute the binomial and
score it, or explicitly justify why the data are insufficient (e.g.
fewer than 8 subjects, or a design that does not produce a directional
statistic).

**Consequence:** The proposed next actions for `anesthesia-bridge` and
`decision-phenotype` are prioritized because both have the data and
the missing statistic is cheap.

## Naming collision: `warden` project vs H1/H2/H3 addendum

**Problem:** The LLM addendum in `gate-ladder-v0.md` is called the
"WARDEN honesty gate", which shares its name with the `warden`
portfolio project.

**Override:** In this repo, the LLM addendum is henceforth called the
"honesty addendum" (H1/H2/H3). The gate ids H1, H2, H3 are unchanged.
Any reference to a "WARDEN gate" in older files should be updated at
next touch.

**Consequence:** Reads no differently in code (gate ids stable) but
removes the naming ambiguity in docs and PRs.

## Whole-project scope check (new gate G13, proposed)

**Problem:** `bio-toolkit` scored `unscored` on every gate because it
does not map to any `Thought` tuple field. The ladder has no way to
say "this project is out of scope for NEUROSPINE" other than
retirement, which is heavier than warranted.

**Proposed gate G13:** each project's evaluation.md must name at
least one `Thought` tuple field it plausibly feeds. When no field is
plausible, G13 is marked `n/a` and the project is flagged as
"portfolio-adjacent" rather than in-scope. This is not a retirement;
it is a scope-clarification.

**Adoption:** Deferred to gate ladder v1 proper. Applied to
`bio-toolkit` immediately as a `portfolio-adjacent` note.

## Retirement rule sharpening

The base rule fires on "same gate failing twice, more than 14 days
apart, no viable fix in the tree." The first scoring pass added a
second retirement path:

- **Documented-failure retirement.** When the project's own memory or
  README documents a failure as settled, an ADR may retire the
  specific failing component without waiting for the two-strikes
  rule. See ADR-005 (tribe-neuroprint Paper 1) and ADR-006 (Hopf
  dynamical twin).

## fMRI addendum sharpening

The base addendum requires the full triad G-fMRI.1/2/3 for any
fMRI-grounded claim. The first scoring pass showed that G-fMRI.3
(group-level significance) admits an "honest fail" verdict when the
sample is under-powered rather than truly null. This addendum:

- Distinguishes `G-fMRI.3 fail (underpowered)` from `G-fMRI.3 fail
  (null result)` in the note column of every `evaluation.md`.
- Underpowered fail does not disqualify a project from `green` overall
  when the direction and effect size are consistent; the project is
  flagged for additional data instead.

## Effective date

2026-09-03. Applied prospectively to future scoring passes. The
2026-09-03 pass is the first application.
