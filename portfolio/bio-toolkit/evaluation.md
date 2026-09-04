# bio-toolkit: evaluation

- External home: github.com/aaygan29/bio-toolkit (confirmed via `gh repo view`: public, default
  branch `main`, pushed 2026-09-03). No local checkout inspected this pass; scored from metadata
  and memory only. Contents not independently verified beyond `gh`'s repo-level metadata.
- Status: active
- Last scored: 2026-09-03
- Next re-score due: 2026-09-17

## One-line claim

Not a scientific claim: a consolidation of three prior biology repos (genoprot, protein
reconstruction from partial genomic sequence; bioplausibility_scoring, a protein-variant
plausibility-vs-function scorer; harbor-bio-tasks, cancer/drug-target/MRI capability
tasks) into one monorepo via `git subtree`, with the three originals archived read-only.

## Gate scores

This project is infrastructure consolidation, not an empirical finding, and it sits
outside NEUROSPINE's neuro-behavioral instrument scope (see the cross-cutting report for
a note on this). Most gates are unscored for lack of inspected contents, not because the
work is bad.

| Gate | Status | Note |
| --- | --- | --- |
| G1 provenance/leakage        | partial | `git subtree` is documented as preserving full history for each subdirectory, which is real provenance discipline at the repo-merge level; individual datasets/models inside each subproject were not inspected this pass. |
| G2 seed variance (n>=5)      | unscored (no evidence available; contents not inspected) | |
| G3 specification robustness  | unscored (no evidence available) | |
| G4 specificity ablation      | unscored (no evidence available) | |
| G5 confound control          | unscored (no evidence available) | |
| G6 mechanism/necessity       | unscored (no evidence available) | |
| G7 calibration                | unscored (no evidence available) | |
| G8 external validity          | unscored (no evidence available) | |
| G9 measurement reliability    | unscored (no evidence available) | |
| G10 reproducibility            | unscored (no evidence available; not inspected for tests/CI this pass) | |
| G11 ethics/safety              | pass | Explicitly excludes `BoNT_break` (kept separate as biosecurity/dual-use) and all safety repos from consolidation: a real, deliberate dual-use boundary decision, not an oversight. |
| G12 analytic integrity         | unscored (no evidence available) | |

### fMRI addendum

| Gate | Status | Note |
| --- | --- | --- |
| G-fMRI.1 per-participant CV        | n/a | Not an fMRI-grounded project. |
| G-fMRI.2 sign-concordance binomial | n/a | |
| G-fMRI.3 group-level significance  | n/a | |

### LLM addendum

| Gate | Status | Note |
| --- | --- | --- |
| H1 refusal path                | n/a | |
| H2 calibrated confidence       | n/a | |
| H3 loyalty vector disclosure   | n/a | |

## Contribution to NEUROSPINE

Tuple field(s) this project could feed: none. This is biology tooling (protein
reconstruction, variant scoring, cancer/drug-target tasks), not a neuro-behavioral
decision instrument, and does not obviously map onto any of the seven tuple fields. Its
inclusion in the NEUROSPINE portfolio is a scope question: see the cross-cutting report.

## Open action items

- [ ] Inspect the three subproject directories (`genoprot/`, `bioplausibility_scoring/`,
  `harbor-bio-tasks/`) directly for tests, data provenance, and reproducibility before any
  further gate scoring beyond G1/G11.
- [ ] Decide, at the program level, whether `bio-toolkit` belongs in the NEUROSPINE
  portfolio at all, given it does not feed any tuple field (flagged in the cross-cutting
  report as a scope-definition gap, not a project defect).
- [ ] If it stays in-portfolio, rebuild the affected resume PDFs (Bio, Tech, Academic CV
  tracks) per the standing README-update rule, since `build_resumes.py` already points at
  the new paths.
