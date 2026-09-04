# decision-phenotype: evaluation

- External home: github.com/aaygan29/decision-phenotype (confirmed via `gh repo view`: public,
  default branch `main`, pushed 2026-08-21). Local checkout confirmed at
  `~/Desktop/Research/projects/Neuroscience/decision_phenotype/` (reproduce.py, tests/, results/,
  figures/, submission/ all present).
- Status: active
- Last scored: 2026-09-03
- Next re-score due: 2026-09-17

## One-line claim

Exploratory (submission not yet accepted at a venue; treat as exploratory per the citation
rule even though the artifact is under `projects/Neuroscience/decision_phenotype`, not the
`submissions/` or `MLCB_2026_submission/` paths the rule names): an honesty-gated
neuroeconomic decision-phenotype estimator, real-data validated on NARPS behavioral
choices (n=108, AUC 0.958) with directionally consistent but underpowered NAcc/insula
fMRI grounding, replicated cross-lab (ds000005, AUC 0.86-0.89 transfer) and cross-modality
(EEG reward positivity, ds003458).

## Gate scores

| Gate | Status | Note |
| --- | --- | --- |
| G1 provenance/leakage        | pass | NARPS (Botvinik-Nezer 2019), ds000005 (Tom 2007), ds003458 (Cavanagh 2015) all cited with DOIs; subject-grouped 5-fold CV used, not run-holdout; a real brainmask-alignment bug was caught and fixed rather than silently producing zeros. |
| G2 seed variance (n>=5)      | unscored (no evidence available; the estimator is fit deterministically on real data rather than swept over seeds) | |
| G3 specification robustness  | partial | Cross-dataset replication (NARPS-trained model predicts ds000005 out-of-dataset, AUC 0.86, and reverse 0.89) is a real robustness signal but is a dataset swap, not the ladder's narrower "vary one non-load-bearing preprocessing choice." |
| G4 specificity ablation      | pass | E3's negative control is explicitly null (p=0.90) against the positive control's real effect (brain>behavior dR2=+0.114, p=0.003); the naive "predict a leader's actions from their neuroprofile" framing was rejected and inverted into an abstention claim (C5) rather than forced through. |
| G5 confound control          | partial | The MNI-vs-native brainmask mismatch (a real confound) was caught and fixed for both FirstLevelModel and NiftiSpheresMasker; motion/TR/scanner/physio are not separately enumerated and checked as a set. |
| G6 mechanism/necessity       | partial | AIM-consistent directions are shown (NAcc down to loss, insula up to loss, both significant at n=40) but no single intervention is run that would break the proposed mechanism and show the effect disappear. |
| G7 calibration                | partial | Conformal coverage and ECE are reported on real NARPS data (coverage 1.00 >= 0.90 target, ECE 0.034) for the behavioral honesty layer. This calibration evidence stands on its own; it does not license upgrading the fMRI-grounded NAcc/insula claim specifically, since the fMRI triad below is not fully established. |
| G8 external validity          | partial | Real second-dataset replication exists for the behavioral/phenotype-transfer claim (ds000005, cross-lab AUC 0.86-0.89) and a second modality (EEG L7, ds003458); the direct fMRI NAcc/insula finding itself was only cross-checked against NeuroVault group maps (gain channel only), not a second full fMRI cohort. |
| G9 measurement reliability    | unscored (no evidence available; no test-retest or split-half reported for the fMRI betas) | |
| G10 reproducibility            | pass | `python reproduce.py` runs in about 100 seconds and all 6 headline synthetic-data gates pass; this is the cleanest literal G10 pass found across the portfolio. |
| G11 ethics/safety              | pass | All datasets public (NARPS, ds000005, ds003458 all OpenNeuro CC0/public); explicit honesty stance that no individual is scanned and neural grounding is a population property, never measured firing or psychodiagnosis. |
| G12 analytic integrity         | partial | STATUS.md/ROADMAP.md carry a living log with kill-criteria discipline, and grounding-chain honesty labels (established/external/literature/abstained/pending) are used throughout; several real-data runs (e.g. re-anchoring after the n=8 NSD-style null in the L6 link) were exploratory/iterative rather than strictly preregistered before the data were looked at. |

### fMRI addendum

| Gate | Status | Note |
| --- | --- | --- |
| G-fMRI.1 per-participant CV        | partial | Per-subject GLM with subject-level betas feeding a group test at n=12 then n=40 is close to but not a strict subject-held-out cross-validation of a predictive claim. |
| G-fMRI.2 sign-concordance binomial | unscored (no evidence available) | "AIM directions all consistent" at n=12 and n=40 is reported qualitatively; no formal binomial sign-concordance test across participants is reported. |
| G-fMRI.3 group-level significance  | pass | NAcc decreases to loss t=-2.12, p=0.040; anterior insula increases to loss t=+2.32, p=0.025, both at n=40 with the direction matching AIM theory. |

The fMRI triad is not fully established (G-fMRI.2 unscored), so the direct neural-behavior
mapping stays at the abstained/hypothesis level the memory itself reports: "the r=-0.40
neural-lambda-ratio is wrong-sign + ratio artifact, gate abstains." This matches the
project's own honesty stance and should not be upgraded past that here.

### LLM addendum

| Gate | Status | Note |
| --- | --- | --- |
| H1 refusal path                | n/a | Not an LLM-decision instrument. |
| H2 calibrated confidence       | n/a | |
| H3 loyalty vector disclosure   | n/a | |

## Contribution to NEUROSPINE

Tuple field(s) this project could feed: `answer` (choice prediction), `calibrated_confidence`
and `abstention_flag` (the honesty layer is close to a working reference implementation of
these two fields), `neural_alignment_score` (directionally consistent, underpowered).

## Open action items

- [ ] Run and report the per-participant sign-concordance binomial test (G-fMRI.2) for the
  NAcc/insula loss channel at n=40: the single missing leg of the fMRI triad, and the
  direct blocker on upgrading the neural-behavior link past "abstained."
- [ ] Find or acquire a large MID reward-anticipation fMRI dataset with fmriprep
  derivatives and individual data (the memory's own stated gap for the direct
  neural<->behavioral link, L6, still abstained).
- [ ] Submit to NBDT (diamond open access, no fee) per the plan in `submission/`; complete
  the outstanding author-metadata TODOs (affiliation, ORCID, Gowthaam co-authorship call)
  before submitting.
