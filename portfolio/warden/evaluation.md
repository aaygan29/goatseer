# warden: evaluation

- External home: github.com/aaygan29/warden (confirmed via `gh repo view`: public, default branch
  `main`, pushed 2026-08-16, described by its own repo metadata as a "simulated-data reference
  skeleton"). Source project docs also live outside `~/Desktop/Research` at
  `~/.claude-science/orgs/.../workspaces/.../` per memory (not re-verified this pass).
- Status: proposed (a runnable v0.1 skeleton exists; the instrument itself is not validated)
- Last scored: 2026-09-03
- Next re-score due: 2026-09-10

## One-line claim

Exploratory: a proposed calibrated, abstaining cognitive-security instrument (three
heads: manipulability-sensitivity, live-engagement detection, countermeasure ordering)
with a runnable simulated-data skeleton verified end-to-end; per the citation rule, its
own pilot results on real ERP/CIT/persuasion data are explicitly not yet in the
reproducible-with-data whitelist and must not be treated as established.

## Gate scores

| Gate | Status | Note |
| --- | --- | --- |
| G1 provenance/leakage        | partial | The skeleton (deceptkit's fusion chain vendored in) runs end to end (exit 0, all three heads plus the C8 scope refusal fire) on simulated data only; real-data pilot results exist (`results/real_*.json`) but are explicitly flagged as not-yet-validated per `feedback_citing_own_unverified_work`. |
| G2 seed variance (n>=5)      | unscored (no evidence available) | |
| G3 specification robustness  | unscored (no evidence available) | |
| G4 specificity ablation      | unscored (no evidence available) | |
| G5 confound control          | unscored (no evidence available) | |
| G6 mechanism/necessity       | unscored (no evidence available) | |
| G7 calibration                | unscored (no evidence available; described as calibrated/abstaining by design, but not yet validated per the citation rule) | |
| G8 external validity          | unscored (no evidence available) | |
| G9 measurement reliability    | unscored (no evidence available) | |
| G10 reproducibility            | partial | The simulated-data skeleton is independently verifiable (documented exit-0 run through a specific conda env); no real-data reproduce target exists. |
| G11 ethics/safety              | pass | Non-goals are enforced at the API boundary, not just stated: no per-individual H1/H2 output in asymmetric-power settings (employment, custody, immigration, clearance, interrogation), refuses to run in adverse contexts, EPPA/admissibility screen refuses employment-context use, never offered as evidence of a mental state. This is a strong, concrete G11 pass. |
| G12 analytic integrity         | partial | A documented 6-persona red-team hardening pass exists (`critiques_warden.md`, `triage_warden.md`, `revision_log_warden.md`), plus a literature review with ~18 DOI-verified sources grounding target effect sizes; the design is preregistered in spirit, but the pilot real-data results are explicitly not held to the same bar yet. |

### fMRI addendum

| Gate | Status | Note |
| --- | --- | --- |
| G-fMRI.1 per-participant CV        | n/a | Instrument targets ERP/CIT/persuasion data, not fMRI, per the current design. |
| G-fMRI.2 sign-concordance binomial | n/a | |
| G-fMRI.3 group-level significance  | n/a | |

### LLM addendum

| Gate | Status | Note |
| --- | --- | --- |
| H1 refusal path                | pass | The enforced non-goals above are literally H1 (refuse when the answer/use is not entailed by what the design permits) implemented as hard refusals, not soft guidance. |
| H2 calibrated confidence       | partial | The three heads are designed to abstain (SPRT-based H2 abstains at low coverage; H1 is assumption-relative, not a trait measurement), but no validated abstention-rate report exists per the citation rule. |
| H3 loyalty vector disclosure   | n/a | Not this project's construct; note the naming collision between the WARDEN project and the gate ladder's own "WARDEN honesty gate" addendum name: flagged in the cross-cutting report as a ladder-sharpening candidate. |

## Contribution to NEUROSPINE

Tuple field(s) this project could feed: `honesty_verdict` (this project is close to the
namesake and reference design for that field), `abstention_flag`. The enforced-refusal
pattern (G11/H1) is a genuinely reusable template for the instrument's honesty layer even
before the instrument itself is validated.

## Open action items

- [ ] Do not promote any `results/real_*.json` finding into a paper, portfolio README
  claim, or the NEUROSPINE instrument until it clears the reproducible-with-data
  whitelist per `feedback_citing_own_unverified_work`: this is the single blocking rule
  for this project.
- [ ] Pick one head (H1 manipulability-sensitivity is the most literature-grounded, per
  Falk 2010 r=0.49) and run it to a validated real-data result with G1-G5 scored for real,
  rather than leaving all three heads at skeleton stage simultaneously.
- [ ] Resolve the naming collision between the WARDEN project and the ladder's WARDEN
  honesty-gate addendum before either is referenced in the same document again.
