# ADR-001-license-unlicense-vs-mit

## Status

Proposed, awaiting confirmation. See issues_to_open.md.

## Context

The NEUROSPINE repository is initialized with the Unlicense, which is the most
permissive open-source license (public domain, no attribution required, no
warranty disclaimers). The brief specified MIT, which requires attribution and
includes explicit disclaimer of warranties and limitations of liability. A
deliberate choice is needed.

## Decision

Recommend adopting option A: **keep the Unlicense**.

The Unlicense strictly dominates MIT on permissiveness:
- Unlicense: anyone can do anything with the code, no obligations.
- MIT: anyone can do anything, but must include a copy of the license and
  copyright notice.

For a research and benchmark program where the goal is maximum adoption and
remix without friction, Unlicense is the stronger choice. Academic users often
prefer MIT for its explicitness, but Unlicense grants strictly more freedom.

This decision is proposed pending Aayush confirmation.

## Consequences

- Researchers and practitioners can use, fork, and build on NEUROSPINE code
  with zero legal friction.
- No copyright attribution required (unlike MIT).
- Academic citations to papers using NEUROSPINE are the primary attribution
  mechanism.
- Practitioners are free to commercialize derivative work.
- The license is already in the repo; switching to MIT is a one-line change if
  the recommendation is overruled.

See issues_to_open.md for follow-up tracking.
