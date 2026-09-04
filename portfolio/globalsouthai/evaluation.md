# globalsouthai: evaluation

- External home: `~/Desktop/Research/submissions/neuro-ai/submissions/globalsouthai/` (confirmed
  present: CITATIONS.md, METHODS.md, OVERVIEW.md, README.md, code/, data/, figures/, latex/,
  paper.pdf). This is under `submissions/`, so findings drawn from this specific artifact satisfy
  the citation rule for "Aayush's own work as an established finding," subject to the venue's
  actual acceptance status below.
- Status: submitted (regular deadline Sep 5 2026 AoE for GlobalSouthAI @ NeurIPS 2026; non-archival,
  double-blind affinity workshop). Scoring here is retrospective on the submitted artifact, not on
  an acceptance decision, which is not yet known.
- Last scored: 2026-09-03
- Next re-score due: 2026-09-17

## One-line claim

A position paper ("The Steepest Derivative") arguing AI neuro-persuasion is a compounding
cognitive-security risk for the Global South, combined with one real secondary-analysis
result reused from a third party's published work (Dai et al., arXiv:2510.01255: deployed
DeepSeek refuses China-sensitive prompts 6-78x more than comparable US models, Cohen's h
0.74-1.06, with a Western-topic specificity control from that source). The paper's own
auditing instrument is validated on synthetic controls only and explicitly does not claim
measured electoral influence.

## Gate scores

| Gate | Status | Note |
| --- | --- | --- |
| G1 provenance/leakage        | pass | The refusal-asymmetry finding is a real, independently published external result (Dai et al.) with a DOI/arXiv id, reused under citation, not re-derived by Aayush; own-instrument components (forecaster, WARDEN-style check) are clearly separated from the borrowed result. |
| G2 seed variance (n>=5)      | n/a | The headline quantitative result is a third-party published statistic, not this project's own model output to sweep over seeds. |
| G3 specification robustness  | n/a | |
| G4 specificity ablation      | pass | The source paper's own Western-topic specificity control is explicitly carried into this paper's use of the finding, rather than the refusal-asymmetry number being used context-free. |
| G5 confound control          | unscored (no evidence available for the paper's own auditing instrument beyond the borrowed result) | |
| G6 mechanism/necessity       | unscored (no evidence available) | |
| G7 calibration                | unscored (no evidence available; the auditing instrument is explicitly validated on synthetic controls only, not real held-out data) | |
| G8 external validity          | fail (honestly scoped) | The auditing instrument (forecaster + WARDEN-style check + conformal gate) has not been run on real data; the paper does not claim it has, which is the correct honest framing but still leaves G8 unmet for the instrument itself. |
| G9 measurement reliability    | unscored (no evidence available) | |
| G10 reproducibility            | partial | `latex/` recompiles to the submitted PDF and `code/loyalty_analysis.py` is present; no end-to-end reproduce script for the borrowed statistic (which is not this project's to reproduce; it belongs to the source paper). |
| G11 ethics/safety              | partial | Double-blind anonymization is the doctrine for this venue class (`feedback_submission_anonymization.md`); this evaluation did not independently verify an `anonymous.4open.science` mirror exists for this specific submission, only that the anonymization doctrine applies. Do not assume compliance without checking. |
| G12 analytic integrity         | partial | Passed an inline council-review (ACCEPT, non-archival) after a real catch-and-fix: a fabricated meta-analysis authorship was found and corrected (to Holbling/Maier/Feuerriegel), and the persuasion claim was recalibrated to the meta-analysis's actual null-leaning finding. The catch-and-fix is good discipline; the fact that a fabrication reached a near-final draft at all is a genuine integrity near-miss worth tracking. |

### fMRI addendum

| Gate | Status | Note |
| --- | --- | --- |
| G-fMRI.1 per-participant CV        | n/a | Not an fMRI-grounded claim. |
| G-fMRI.2 sign-concordance binomial | n/a | |
| G-fMRI.3 group-level significance  | n/a | |

### LLM addendum

| Gate | Status | Note |
| --- | --- | --- |
| H1 refusal path                | n/a | The refusal-asymmetry finding is about a third-party model's refusal behavior as the object of study, not this paper's own instrument refusing to answer. |
| H2 calibrated confidence       | unscored (no evidence available; instrument validated on synthetic controls only) | |
| H3 loyalty vector disclosure   | pass | The paper reuses jspace-loyalty's loyalty/cognitive-security framing directly, per its own description. |

## Contribution to NEUROSPINE

Tuple field(s) this project could feed: `loyalty_vector`, `honesty_verdict` (reused from
jspace-loyalty and behavioral-decoding respectively). This project is primarily a
synthesis/position paper, not a new instrument component.

## Open action items

- [ ] Confirm the `anonymous.4open.science` mirror actually exists and is linked for this
  specific submission before the Sep 5 2026 AoE deadline (do not assume from the general
  doctrine memory; verify the artifact directly).
- [ ] Complete the two remaining camera-ready nits (complete author lists on two arXiv bib
  entries; rename the `angwin2022bias` bibkey to the correct Stark & Hoey 2021 citation).
- [ ] If accepted, track the decision in `SUBMISSIONS.md` and re-score G8/G11 once known.
