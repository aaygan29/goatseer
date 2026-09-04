# Queued GitHub actions and human-in-the-loop items

Everything here becomes a live issue, a PR, or an ADR retiring it.

## Immediate (do next tick)

- [ ] Retry the pubmed literature crawl (failed at rate limit
      2026-09-03). Target ~30 additional biomedical notes plus
      `literature/SYNTHESIS_biomedical.md`.
- [ ] Enable Issues and Projects on `aaygan29/NEW_REPO`:
      `gh repo edit --enable-issues --enable-projects`.
- [ ] After scaffold PR merges, create labels: `lit-review`,
      `gate-fail`, `instrument`, `retirement`, `blocked-on-auth`,
      `synthetic-first`, `verification`, `pubmed-pending`.
- [ ] Open per-project tracking issues (18 total), titled
      "[<slug>] first evaluation follow-through" linked to
      `portfolio/<slug>/evaluation.md`.
- [ ] Compute the missing G-fMRI.2 sign-concordance binomial for
      `anesthesia-bridge` (Pillar A LZc across 26 subjects) and for
      `decision-phenotype` (NAcc/insula loss channel at n=40). Both
      are cheap statistical add-ons; both are the single missing leg.

## Requires user action (Aayush)

- [ ] Confirm the tribe-neuroprint external home path (recorded as
      `~/Desktop/Research/neuroprint-api/` but does not resolve). If
      the code moved, name the new path.
- [ ] Confirm `aaygan29/NAcc_benchmark` status; the fork with PR #721
      to `terminal-bench-science` is what NEUROSPINE tracks; the
      original repo does not resolve via `gh`.
- [ ] Grant access to private repos NEUROSPINE will PR against:
      `aaygan29/behavioral_decoding`, `aaygan29/decision-phenotype`,
      `aaygan29/jspace-loyalty`. Confirm each reachable via `gh`.
- [ ] Confirm the anonymous.4open.science mirror for `jspace-loyalty`
      is up before the next NewInML resubmission window.
- [ ] Authorize `plugin:engineering:github` in an interactive
      session if the MCP-mediated flow is preferred over `gh` CLI.
- [ ] Authorize `plugin:productivity:linear` or
      `plugin:productivity:notion` if issue mirroring or roadmap
      sync is desired. Not required.
- [x] License decided: AGPL-3.0 (2026-09-03). See
      `decisions/ADR-001-license.md`.

## Committed-out (already done or covered by ADR)

- [x] Program name pinned as NEUROSPINE; repo slug NEW_REPO.
- [x] Auditor -> mind-reading pivot recorded in ADR-004.
- [x] Two retirements recorded in ADR-005 (tribe-neuroprint Paper 1)
      and ADR-006 (Hopf dynamical twin).
- [x] Extractable-bit and external-re-verification protocol recorded
      in ADR-003.
- [x] Citation doctrine recorded in ADR-002.

## Nice-to-have

- [ ] Wire a GitHub Action to render the weekly report from
      `portfolio/*/evaluation.md` deltas.
- [ ] Add a CODEOWNERS file once the instrument has real code
      landing across the extractions.
- [ ] Backfill BibTeX entries for the seminal external theorists
      (Vovk et al. 2005; Angelopoulos and Bates 2021; El-Yaniv and
      Wiener 2010; Ratcliff 1978) into `literature/references.bib`.
