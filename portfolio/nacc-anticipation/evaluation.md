# nacc-anticipation: evaluation

- External home: recorded as github.com/aaygan29/NAcc_benchmark in `ORGANIZATION.md`, but this repo
  does **not** resolve via `gh repo view` this pass (checked directly). The real, active work is the
  PR against `harbor-framework/terminal-bench-science` (#721) from fork
  `aaygan29/terminal-bench-science`, branch `add-nacc-anticipation-decoding`. Local clone confirmed at
  `~/Desktop/Research/submissions/neuroscience/tb-science/tbsci-fork/` (task-template.toml, ci_checks/,
  tasks/, rubrics/ all present). Treat `NAcc_benchmark` as a stale record-repo reference and prefer
  the fork/PR as the source of truth.
- Status: active (PR open, under review)
- Last scored: 2026-09-03
- Next re-score due: 2026-09-17

## One-line claim

This is a benchmark task, not a scientific claim about the brain: a Terminal-Bench-Science
task that makes a standard first-level NAcc reward-anticipation analysis produce a
clean-but-wrong answer under three synthetic confounds, scored by recovery of the true
ranking (nacc>wm>mpfc>insula) once confounds are removed.

## Gate scores

Most gates below apply awkwardly because the deliverable is a verifier/task, not an
empirical finding under test. Scored where meaningful; `n/a` where the gate targets a
scientific claim this project does not make.

| Gate | Status | Note |
| --- | --- | --- |
| G1 provenance/leakage        | pass | Data baked into `environment/data` (no build/trial network); source OpenNeuro ds005479 documented with an explicit disclosed scope switch (PE decoding to reward-anticipation) when the promised outcome data turned out not to exist; oracle purity independently checked (`solution/solve.py` verified via grep to never read `/tests/reference/*`). |
| G2 seed variance (n>=5)      | n/a | Task authoring, not a stochastic scientific estimate. |
| G3 specification robustness  | n/a | |
| G4 specificity ablation      | pass | The entire v2 design is a specificity ablation: the naive analysis makes insula look most gain-selective and white matter look reward-responsive; only removing the three synthetic confounds recovers the true ranking. This is the ladder's G4 test built directly into the task. |
| G5 confound control          | pass | Motion (FD, verified against the dataset's published Mean FD to 0.02mm) and a FLIRT-space registration convention (explicitly spelled out after reviewer feedback, with a documented sign-error catch-and-fix) are both handled; TR/scanner not separately itemized but FD/registration are the two the reviewer actually pressed on. |
| G6 mechanism/necessity       | n/a | Not a mechanism claim; the task tests whether an agent's pipeline recovers ground truth, not why the brain does something. |
| G7 calibration                | n/a | |
| G8 external validity          | n/a | |
| G9 measurement reliability    | n/a | |
| G10 reproducibility            | pass | Oracle reward 1.0 (14/14 verifier tests), 18/18 Harbor static checks pass, all baked and network-free; independently reproducible via `bash ci_checks/check-*.sh <task-dir>` without Docker. |
| G11 ethics/safety              | pass | Public OpenNeuro data (ds005479), no PHI. |
| G12 analytic integrity         | partial | Two gates are deliberately left `unscored` inside the task itself "for fairness" (nullness of the white-matter control, and the two middle ranking positions): an intentional, disclosed scoring-design choice, not an oversight, but it means the task's own internal ladder is not fully scored either. |

### fMRI addendum

| Gate | Status | Note |
| --- | --- | --- |
| G-fMRI.1 per-participant CV        | n/a | Task scoring is per-subject oracle comparison, not a cross-validated predictive claim. |
| G-fMRI.2 sign-concordance binomial | n/a | |
| G-fMRI.3 group-level significance  | n/a | |

### LLM addendum

| Gate | Status | Note |
| --- | --- | --- |
| H1 refusal path                | n/a | |
| H2 calibrated confidence       | n/a | |
| H3 loyalty vector disclosure   | n/a | |

## Contribution to NEUROSPINE

Tuple field(s) this project could feed: none directly (this is a benchmark task, not a
decision instrument). Indirect value: its confound-recovery design is a usable reference
for G5 methodology on any other fMRI-grounded project in this portfolio.

## Open action items

- [ ] Reconcile the `ORGANIZATION.md` external-home entry (`aaygan29/NAcc_benchmark`,
  unresolvable via `gh`) with the actual active location (the fork/PR); this file now
  points at the fork, but the top-level map should match.
- [ ] Track PR #721 to merge or address any remaining reviewer feedback beyond the
  2026-09-02 round (FLIRT convention, unsigned statistic, schema hardening) already closed.
- [ ] Confirm the human-authorship attestation checkboxes and get a Docker-based `harbor
  run` evidence pass (frontier-agent run + failure analysis): the two author-only items
  the memory flags as still outstanding.
