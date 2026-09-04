# Gate ladder v0

Initial adaptation of the council-review skill's twelve-seat extended ladder
to NEUROSPINE. Each gate is scored per project in
`portfolio/<slug>/evaluation.md`. A project cannot enter the instrument until
all applicable gates pass.

Extend via ADR. Do not silently add or drop gates.

## G1. Provenance and leakage

Every dataset, model, and preprocessed artifact is traceable to a source with
version and hash. No test data touches training. Cross-subject splits are
subject-holdout, not run-holdout, unless the claim is explicitly within-subject.

## G2. Seed variance (n >= 5)

Any headline metric is reported over at least five seeds with mean, standard
deviation, and the seed used for the point estimate. Point estimates without
variance do not pass.

## G3. Specification robustness

Vary one non-load-bearing preprocessing or hyperparameter choice; the sign of
the effect must survive. Report the choice matrix.

## G4. Specificity ablation

Show the result does not appear under a matched control that removes the
proposed mechanism. If it does, the claim is renamed to what the control also
produces.

## G5. Confound control

Enumerate confounds and check at least the top three. For fMRI: motion, TR,
scanner, physio. For LLM: prompt length, formatting, token position.

## G6. Mechanism and necessity

Give a mechanistic story that is falsifiable at the local level. Then run one
intervention that would break the mechanism and show the effect goes away.

## G7. Calibration

Predicted confidences are calibrated on held-out data. ECE reported, isotonic
or conformal fix applied when it fails.

## G8. External validity

Repeat on a second dataset or a second model. If unavailable, name the missing
external and quantify the risk.

## G9. Measurement reliability

Test-retest for neural readouts. For behavioral, inter-rater or split-half.
For model outputs, prompt-perturbation stability.

## G10. Reproducibility

`make reproduce` produces the reported number end to end from raw or its cached
hash, on a fresh venv, in under an hour where feasible. Seed sweep included.

## G11. Ethics and safety

Public or user-consented data only. No PHI in the repo. Deception, coercion,
and belief-imparting instruments include a red-team note and a refusal path.

## G12. Analytic integrity and preregistration

Analysis plan is written before the data are looked at, or the deviation is
declared explicitly. Multiple-comparisons are corrected.

## fMRI addendum: Goltermann/Huth robustness triad

For any fMRI-grounded claim:

- G-fMRI.1 Per-participant cross-validation with the subject held out.
- G-fMRI.2 Sign-concordance binomial across participants passes at p < 0.05
  two-sided against chance direction.
- G-fMRI.3 Group-level effect (for example delta-CMRO2) is significant with
  variance across participants reported.

Failing any of these downgrades the claim to a hypothesis and moves it out of
the paper draft.

## LLM addendum: WARDEN honesty gate

- H1: The model refuses when the answer is not entailed by the assumptions.
- H2: Calibrated confidence and abstention rate are reported.
- H3: The loyalty vector for the tested prompt is disclosed.

## Retirement rule

If a project fails the same gate twice across two evaluations more than 14
days apart with no viable fix in the tree, open an ADR to retire it or invert
its claim.
