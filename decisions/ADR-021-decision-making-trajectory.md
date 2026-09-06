# ADR-021: Within-trial state trajectories for perceptual decision-making

## Status

Accepted, 2026-09-05. Result: null (see below).

## Context

ADR-018 named decision-making / evidence accumulation as the second temporal
target for the trajectory apparatus, after sleep staging (ADR-019) confirmed
the apparatus works when the physiology is genuinely temporal (McNemar
p=1.18e-13 on Sleep-EDF; see `experiments/sleep_transition_decoding/`). Sleep
staging tests transitions ACROSS epochs (30s stages, minutes apart).
Decision-making offers a different, arguably sharper test: transitions
WITHIN a single trial, on the timescale of evidence accumulation to a
threshold (Rungratsameetaweemana et al.; Taghia et al., Nat. Commun. 2018,
doi:10.1038/s41467-018-04723-6, show HMM latent-state sequences and their
transition timing track accumulation dynamics and predict performance).

If evidence accumulation is real in the EEG signal, the trial's internal
STATE SEQUENCE (e.g. low-evidence -> building -> committed) should carry
information about the eventual choice beyond a trial's memoryless (bag-of-
sub-windows) summary. That is exactly the trajectory-vs-occupancy contrast
`neurospine.behavior.analyze_within_subject` already implements.

## Data

OpenNeuro `ds002739`: simultaneous EEG-fMRI random-dot-motion perceptual
decision task (originally `ds001512`, reuploaded for privacy; 24 subjects).
Each subject/run has ~160 trials with `dotdirection`, `choice` (1=left,
2=right), `accuracy`, `confidence`, `RT`, and `tstim`/`tresp`/`tconf` onsets
(samples at 1000 Hz) in `EEG_events_sub-XX_run-YY.mat`; band-pass filtered,
gradient/BCG/EOG-corrected EEG in `EEG_data_sub-XX_run-YY.mat`. This
experiment uses EEG only, 4 subjects, run 1.

## Decision

Reuse the existing apparatus with no new inference code:

1. Stimulus-locked epoch per trial: `[tstim, tstim + 1.0s]`.
2. Split into 5 sub-windows; per sub-window, per-channel theta/alpha/beta
   relative band power (Welch), robust-scaled.
3. **Unsupervised** k-means (k=4) over all of a subject's sub-window feature
   vectors builds that subject's discrete state alphabet -> a length-5
   within-trial state sequence per trial. No labels are used in this step,
   so the state alphabet cannot leak choice information; only the
   Markov/occupancy models fit on it can use labels, and they only see the
   subject's own TRAIN trials (`neurospine.behavior.analyze_within_subject`).
4. Label = choice (left/right). `analyze_within_subject` runs the
   per-subject stratified split, class-conditional Markov model vs.
   occupancy (0th-order) ablation, a per-subject label-shuffle null, and the
   group-level verdict. `trajectory_gain = markov_accuracy -
   occupancy_accuracy` is the key readout, exactly as in the sleep and
   motor-imagery arcs.

Excluded trials use the dataset's own `excludedtrials` index. No new
inference module: `neurospine.behavior.analyze_within_subject` (reused
unmodified from the motor-imagery arc, ADR-011/012) and `sklearn.cluster.
KMeans` for the unsupervised discretization are sufficient; a new
`discretize_subject` helper lives in `experiments/decision_making_trajectory/
run.py`, not in the shared package, since it is a thin, task-specific
feature/clustering step rather than a reusable inference primitive.

## Guardrails

- Unsupervised state discretization: no label leakage into the state
  alphabet itself.
- Subject-disjoint is not required here (within-subject design by
  construction); train/test is trial-disjoint per subject, stratified by
  class (`_stratified_trial_split`).
- Every claim is gated on BOTH a per-subject shuffle null AND the occupancy
  ablation (ADR-011/012 discipline), not just one or the other.
- Label balance (left vs. right) is inspected per subject before running the
  analysis; see the experiment README for the actual counts.

## External anchors

- Rungratsameetaweemana et al. (cited per task brief): within-trial neural
  dynamics track evidence accumulation in perceptual decisions.
- Taghia et al., Nat. Commun. 2018 (doi:10.1038/s41467-018-04723-6): HMM
  latent-state sequences and transition timing predict decision performance.
- ds002739 / ds001512: simultaneous EEG-fMRI random-dot-motion dataset
  (OpenNeuro).

## Result

4 subjects, run 1, 141-156 valid trials each. Mean held-out accuracy 0.491
(chance), mean trajectory gain -0.032 (occupancy baseline slightly beats the
Markov model on average), 0/4 subjects clear their own shuffle null (group
binomial p=1.00). **VERDICT: within-subject: no evidence above per-subject
nulls.** Full per-subject numbers in
`experiments/decision_making_trajectory/README.md`.

This is an honest null, not a confound: the occupancy ablation and shuffle
null both fired as designed (two subjects even show occupancy beating the
Markov model, i.e. no spurious "trajectory" claim survives the gate). It
means this specific representation (1.0s post-stimulus window, 5 fixed
sub-windows, unsupervised k-means on theta/alpha/beta band power, k=4
states) does not capture decodable within-trial accumulation dynamics in
this dataset at this sample size, not that no such trajectory exists. The
sleep-staging positive control (ADR-019) already shows the apparatus
correctly detects a real transition signal when one is present at
sufficient strength; this result narrows where in the decision-making
representation space (window locking, discretization, feature choice) the
signal would need to be sought next, rather than indicting the apparatus.

## Consequences

- Either outcome sharpens the map of where the trajectory apparatus earns
  its keep: sleep staging (across-epoch) is now a settled positive; this ADR
  settles the within-trial evidence-accumulation case with the same
  discipline (null and occupancy baseline required for any claim).
