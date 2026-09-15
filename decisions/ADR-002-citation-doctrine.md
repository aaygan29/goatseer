# ADR-002: Citation doctrine: lean external, do not cite own prior work

## Status

Accepted, 2026-09-03.

## Context

NEUROSPINE draws engineering from Aayush's prior projects (TRIBE pipeline,
NeuroPrint, ISM, jspace-loyalty, decision-phenotype, cultist, memoryprint,
and so on). The default assumption in a research repo is that its own prior
work is the theoretical basis. Aayush pushed back on 2026-09-03:

> I don't want to internally cite my own work because I'll have a hard time
> explaining it and explaining specifically all the things contained within.
> That is why I am trying to rely on other tools that you showed me are
> already cited and published and done with regards to the basis of this
> work. I also want to then take the bits and pieces of the works that I
> did that are the strongest and synthesize them here.

Then, sharpening the concern:

> You need to take whatever is strongest from the tools already made and
> build up a much stronger program right? You don't want to run into this
> whole circular issue where there could be an error in our prior work that
> we didn't notice. Do whatever you can to avoid that situation but still
> proceed with original design.

The concrete risks:

1. **Defensive burden.** Every internal citation is a claim Aayush must
   defend on the spot. External peer-reviewed citations shift the defense to
   the venue.
2. **Circular error.** An undetected bug in a prior project silently props
   up a NEUROSPINE claim; a reviewer catches the prior bug and both fall.
3. **Reviewer skepticism.** A pattern of self-citation in a program-scale
   claim reads as an ecosystem talking to itself.

## Decision

Adopt the following doctrine for all NEUROSPINE code, docs, PRs, ADRs,
literature notes, and paper drafts written from here on.

**1. Lean external.** Every load-bearing design choice, method, gate, or
metric is anchored to an already-published external reference. The
literature index at `literature/` is the citation source of first resort.

**2. Do not cite Aayush's prior projects as authority.** Not in docstrings.
Not in READMEs. Not in ADR bodies. Not in paper drafts. Even for artifacts
that are already peer-reviewed or under formal submission, prefer a stronger
external anchor when one exists.

**3. Extraction is engineering, not evidence.** Code or methods lifted from
a prior project are treated as engineering provenance. They are named in the
git history, in ADRs, and in the `portfolio/<slug>/evaluation.md` sections,
but never as the reason the method is correct.

**4. Every extraction gets a fresh external check.** Before an extracted
method contributes to any gate scoring in NEUROSPINE, it must be re-tested
against an external ground truth (a public dataset, a reference
implementation, or a specific claim in the seed literature). The extraction
does not inherit the prior project's scoring. This closes the circular-error
risk. Protocol is captured in ADR-003.

**5. Weekly reports and PRs describe the external anchor first.** Example:
"Conformal honesty gate (Vovk et al. 2005, Angelopoulos and Bates 2021),
engineered by lifting the abstention scaffold from a prior branch and
re-verified on the CIFAR-10H calibration split" is acceptable. "Extends
jspace-loyalty's abstention scaffold" is not.

## Consequences

- Portfolio evaluations shift from "did this project prove X?" to "which
  bit of this project can be lifted and re-anchored to which external
  paper?" This is reflected in the new `Extractable strongest bit` and
  `External re-verification` sections of the evaluation template.
- Some prior work becomes purely archival: valuable to the person who wrote
  it, not part of the NEUROSPINE argument. That is fine.
- Weekly reports lengthen slightly to accommodate the external anchor per
  design choice. Acceptable cost.
- Reviewers see NEUROSPINE as a program grounded in the peer-reviewed
  literature, with a specific engineering pedigree that they do not need to
  audit to accept the core claims.

## Consequences NOT accepted

- We do not throw away prior work or refuse to reuse code. The doctrine is
  about citation stance, not code hygiene. Reuse aggressively; cite
  externally.
- We do not require independent re-implementation of every extracted
  method. A re-test against external ground truth is sufficient.

## Follow-ups

- ADR-003: extraction and re-verification protocol.
- Update the evaluation template to include the two new sections. Applied
  in the same PR as this ADR.
- Update `README.md` to link this ADR from a new "Citation doctrine" block.
