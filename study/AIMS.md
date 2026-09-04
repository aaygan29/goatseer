# Aims

Three aims. Each has a primary hypothesis, a preregistered success
criterion, and a preregistered failure criterion. Failing an aim is
publishable; hiding a failure is not.

## Aim 1 (A1): Individual-scale replicable thought prediction

**Hypothesis.** A single subject's neural + behavioral recordings support
prediction of five cognitive-state dimensions (perceived stimulus,
affect, decision, memory state, reward signal), with test-retest
reliability that exceeds the day-to-day drift of the underlying signal
after Goltermann/Huth robustness correction.

**Success criterion (preregistered).**

- On the same subject, same task, across at least two sessions separated
  by at least one week: per-dimension Spearman rank correlation between
  session A predictions and session B predictions greater than 0.6 for
  at least three of the five dimensions, with the two remaining
  dimensions greater than 0.3 or explicitly abstained.
- Predictions must survive the Goltermann/Huth triad
  (G-fMRI.1 per-participant CV, G-fMRI.2 sign-concordance binomial p < 0.05,
  G-fMRI.3 group-level significance across the internal replicate).
- No dimension prediction may be reported without a calibrated
  confidence.

**Failure criterion (preregistered).** If test-retest correlation falls
below 0.3 for three or more dimensions after Goltermann/Huth correction,
A1 fails. The pipeline is retired or its scope narrowed. Report the
failure with the exact within-session performance and the between-session
degradation as the primary result.

**External anchors.** MEIcoder (Sobotka et al., arXiv:2510.20762) for the
subject-conditional decoder architecture; Goltermann/Huth/Buchel (eLife
111743) for the reliability gate; test-retest reliability literature to
be filled from `literature/SYNTHESIS_biomedical.md`.

## Aim 2 (A2): Group-scale generalization with quantified degradation

**Hypothesis.** A per-subject pipeline trained under A1 transfers to a
held-out subject population, with a quantifiable and pre-specified
degradation on each dimension. Transfer is not free; the degradation is
the deliverable.

**Success criterion (preregistered).**

- Train an A1 pipeline on N subjects. Fine-tune on K < 10 minutes of a
  held-out subject's data. Predict on the held-out subject's remaining
  data.
- For at least three of the five dimensions, the held-out performance is
  within a pre-specified fraction (say, 40 percent) of the A1
  within-subject performance on the training subjects.
- Cross-subject alignment step follows the RAVEN weak-to-strong under
  shift protocol (Jeon, Sobotka, Choi, Brbic, arXiv:2510.21332) with the
  RAVEN validation set held out until the final report.

**Failure criterion (preregistered).** If held-out performance falls
below the pre-specified fraction on four or more dimensions, A2 fails.
Report the transfer cost as the deliverable and narrow the group-scale
claim.

## Aim 3 (A3): Declared unmeasured cognitive domains

**Hypothesis.** NEUROSPINE explicitly does not attempt to predict any of
the six Cognitive Dark Matter domains (Mineault, Griffiths, Escola,
arXiv:2603.03414): metacognition, cognitive flexibility, lifelong
learning, reasoning, social reasoning, emotional intelligence. Any
apparent prediction on these domains is a confound to be ruled out.

**Success criterion (preregistered).**

- Every reported prediction is labeled with the Cognitive Dark Matter
  domains it explicitly does not measure.
- A specificity ablation (G4) shows that the pipeline's predictive
  power on the five in-scope dimensions is not reducible to prediction
  of any Cognitive Dark Matter domain.
- The `unmeasured_domains` field of every `Thought` returned by the
  reference harness contains at least the six Cognitive Dark Matter
  labels.

**Failure criterion (preregistered).** If any specificity ablation
reveals that a reported prediction is confounded by a Cognitive Dark
Matter domain, that prediction is either recharacterized (renamed to
what the ablation shows it actually measures) or retracted.

## Non-aims

- NEUROSPINE does not aim to be a general-purpose AI auditing tool.
  That was an earlier misdirection; see ADR-004.
- NEUROSPINE does not aim to reduce mental processes to neural signals
  alone. Behavioral signals are co-equal inputs.
- NEUROSPINE does not aim to predict future decisions further out than
  the temporal window supported by the underlying neural signal (for
  fMRI: seconds; for EEG: hundreds of milliseconds).
- NEUROSPINE does not aim to work on a novel subject with zero
  calibration data. A1 requires per-subject calibration; A2 measures
  the cost of reducing it, not eliminating it.
