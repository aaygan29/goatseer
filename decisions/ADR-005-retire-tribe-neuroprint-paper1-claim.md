# ADR-005: Retire tribe-neuroprint Paper 1 zero-shot manipulation-detection claim

## Status

Accepted, 2026-09-03.

## Context

The first scoring pass (`reports/first-scoring-pass-2026-09-03.md`)
flagged `portfolio/tribe-neuroprint/evaluation.md` red on G4 (specificity
ablation), G5 (confound control), and G12 (analytic integrity). The
project's own auto-memory explicitly documents the retraction:

- The Paper 1 zero-shot dlPFC / PBI manipulation-detection claim is
  driven by an uncontrolled stimulus-length confound.
- Longer prompts drive the claimed signature independent of any
  manipulation content.
- No specificity ablation in the current codebase separates length from
  manipulation.

Per the retirement rule (`gates/gate-ladder-v0.md`): a project failing
the same gate twice across two evaluations more than 14 days apart with
no viable fix in the tree becomes a retirement candidate. This is only
the first scoring pass, so the two-strikes rule has not fired. This
retirement fires on a stronger ground: the memory itself already
documents the failure as settled.

## Decision

Retire the Paper 1 claim from the citable-evidence whitelist for
NEUROSPINE. Specifically:

- The `PerceptionDecoder` provider MUST NOT lift the zero-shot
  manipulation signature from tribe-neuroprint as a component.
- The `AbstentionProvider` MUST NOT use the retracted signature as a
  reliability input.
- The `literature/` index does not cite Paper 1 as evidence for any
  claim in NEUROSPINE.

The Corpus A/B/C pipeline design and Paper 2 (unrelated to the
retracted zero-shot claim) are unaffected. The API's current
calibration numbers, insofar as they descend from the retracted claim,
are marked unreliable and must be recomputed with stimulus length as a
covariate before any downstream reuse.

## Consequences

- One provider anchor removed from the planned extraction list.
  Replacement: MEIcoder (Sobotka et al., arXiv:2510.20762) becomes the
  sole external anchor for `PerceptionDecoder`. The engineering
  pedigree still names tribe-neuroprint for the encoder scaffolding
  under ADR-002 rules, but the correctness argument no longer touches
  the retracted claim.
- `portfolio/tribe-neuroprint/evaluation.md` status remains `active`
  because Paper 2 and the Corpus A/B/C design continue. The evaluation
  notes this ADR in the header.
- No effect on the study's Aim 1 or Aim 2 timeline; the extraction
  simply drops one candidate.

## Consequences NOT accepted

- We do not retire the entire tribe-neuroprint project. Only the
  specific Paper 1 zero-shot claim.
- We do not accuse the project of misconduct. The retraction is
  documented in the project's own memory; this ADR only propagates the
  retraction into NEUROSPINE's citation surface.

## Follow-ups

- Update `portfolio/tribe-neuroprint/evaluation.md` header to point at
  this ADR.
- Ensure the pubmed / arxiv literature scan does not add tribe-neuroprint
  Paper 1 as an anchor. Any accidental inclusion in
  `literature/SYNTHESIS_biomedical.md` or
  `literature/SYNTHESIS_computational.md` must be removed on merge.
