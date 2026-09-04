# tribe-neuroprint: evaluation

- External home: github.com/aaygan29/neuroprint-api (recorded path `~/Desktop/Research/neuroprint-api/`
  no longer exists on disk as of this pass; likely moved or folded into the TRIBE v2 / Neuroethics
  submission trees during the 2026-08-23 Research reorg. Not re-verified live; treat path as stale
  until confirmed.)
- Status: active, but core claim retracted
- Last scored: 2026-09-03
- Next re-score due: 2026-09-17

## One-line claim

Exploratory: a FastAPI service scores LLM text for "manipulation" against a TRIBE v2
fMRI-predicted ground truth (Corpus A, 30 stimuli); the API layer is paused pending
data collection, and the founding neural result behind it has been retracted.

## Gate scores

| Gate | Status | Note |
| --- | --- | --- |
| G1 provenance/leakage        | partial | TRIBE v2 predictions (A01-A30.npy) and 8-ROI Destrieux pipeline are documented (`project_tribe_research.md`), but Corpus B statistical-results file is empty and text for Corpus B was never saved: chain is broken past Corpus A. |
| G2 seed variance (n>=5)      | unscored (no evidence available; would need re-running the CSI/PBI pipeline with resampled stimulus sets or bootstrap over subjects to report a variance) | |
| G3 specification robustness  | unscored (no evidence of a preprocessing/hyperparameter sweep) | |
| G4 specificity ablation      | fail | Paper 1's dlPFC/PBI threat-vs-reward-vs-neutral effect (eta^2=0.591, p=0.0003) was retracted by the user: confounded by stimulus-length differences between conditions, not a genuine manipulative-content signature. This is exactly the ablation G4 requires, and it fails. |
| G5 confound control          | fail | Same retraction: the length confound was not controlled before the original claim was made. |
| G6 mechanism/necessity       | unscored (no evidence available) | |
| G7 calibration                | unscored (no evidence available) | |
| G8 external validity          | unscored (no evidence available; Corpus B/C exist as a second-corpus plan but inference is incomplete) | |
| G9 measurement reliability    | unscored (no evidence available) | |
| G10 reproducibility            | unscored (no evidence available; no `make reproduce` target found) | |
| G11 ethics/safety              | partial | Public/synthetic-text data, no PHI; but the API's manipulation-score output is exactly the kind of instrument that could be misused without a documented refusal path: none found. |
| G12 analytic integrity         | fail | The retraction itself is the record of an un-preregistered analysis producing an overclaimed result; no preregistration document found for Paper 1. |

### fMRI addendum

| Gate | Status | Note |
| --- | --- | --- |
| G-fMRI.1 per-participant CV        | unscored (no evidence available; TRIBE v2 is a pretrained zero-shot predictor here, not fit per-participant in this project) | |
| G-fMRI.2 sign-concordance binomial | unscored (no evidence available) | |
| G-fMRI.3 group-level significance  | fail (as originally reported) | The reported group effect (eta^2=0.591) is retracted for confound, so it does not stand as a fMRI-grounded finding regardless of its original p-value. |

### LLM addendum

| Gate | Status | Note |
| --- | --- | --- |
| H1 refusal path                | unscored (no evidence available) | |
| H2 calibrated confidence       | unscored (no evidence available) | |
| H3 loyalty vector disclosure   | n/a | Not a loyalty-audit instrument. |

## Retirement candidate

Paper 1's zero-shot dlPFC/PBI manipulation-detection claim is explicitly retracted per
`project_tribe_research.md` ("RETRACTED 2026-07-06 ... confounded by stimulus length
... not a genuine manipulative-content signature"). This is a fundamental-failure note
in the memory itself. The claim should not be cited as valid evidence anywhere, and the
`neuroprint-api` service's `manipulation_score` output is calibrated against that same
retracted result (Corpus A ground truth), so its current scoring logic inherits the
confound until re-derived from a length-controlled signature.

Proposed ADR (not created here): `decisions/ADR-004-retire-tribe-neuroprint-paper1-claim.md`.
Scope: retire only the Paper 1 zero-shot claim and the API's current calibration; the
Corpus A/B/C convergent-manipulation pipeline design and Paper 2 (neuroethics/governance)
are explicitly unaffected per the same memory entry.

## Contribution to NEUROSPINE

Tuple field(s) this project could feed: `neural_alignment_score` (if re-derived
length-controlled), `honesty_verdict` (the retraction itself is a usable honesty-layer
precedent: a documented confound catch-and-correct). Currently feeds nothing safely.

## Open action items

- [ ] Re-run the manipulation-detection design with stimulus length as a covariate or
  matched control before any G4/G5 re-score (direct fix for the retracted confound).
- [ ] Locate or reconstruct the current `neuroprint-api` checkout; the recorded external
  home path is missing, so provenance (G1) cannot be fully verified until found.
- [ ] Open `decisions/ADR-004-retire-tribe-neuroprint-paper1-claim.md` scoping the
  retraction to Paper 1 / API calibration only, per the retirement rule.
