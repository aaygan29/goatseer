# Analysis plan

Preregistered statistical analysis plan for NEUROSPINE. Locks before any
Phase 2 or later analysis runs on real data. Deviations are declared
explicitly per the analytic-integrity gate (G12).

## Primary analyses

### Aim 1: within-subject test-retest

- Unit of analysis: subject-dimension pair.
- Test: Spearman rank correlation between session A predictions and
  session B predictions, per subject per dimension.
- Success threshold: rho > 0.6 for at least three of five dimensions
  after Goltermann/Huth correction; the remaining dimensions rho >
  0.3 or explicitly abstained.
- Multiple comparisons: Benjamini and Hochberg across five dimensions
  per subject, FDR 0.05.
- Effect size: rho with 95 percent CI via bootstrap (10 000 samples,
  seed pinned).
- Bayes factor: reported for null-result dimensions using default JZS
  prior; BF10 < 1/3 supports null, > 3 supports effect.

### Aim 2: group-scale transfer

- Unit of analysis: held-out subject.
- Test: paired t-test (within held-out subject) comparing full A1
  performance to fine-tuned transfer performance across dimensions.
- Success threshold: held-out performance within 40 percent of A1
  within-subject on at least three dimensions.
- Cross-subject alignment: RAVEN protocol with a validation set held
  out until final report.
- Robustness: leave-N-out sweeps for N in {1, 2, 5, 10} to bound the
  transfer stability.

### Aim 3: specificity + Cognitive Dark Matter check

- For each in-scope dimension x each Cognitive Dark Matter domain: run
  the G4 specificity ablation (matched control that removes the
  in-scope dimension prediction; check whether apparent Cognitive
  Dark Matter prediction also disappears).
- Report the ablation matrix as a heatmap. Off-diagonal high values
  are recharacterization triggers.

## Secondary and exploratory analyses

- Topological analysis layer: persistent homology of session-level
  latent trajectories per subject. Compare Betti curves between
  sessions; report bottleneck distance as an ancillary replicability
  metric.
- Physics framing: fit a spin-glass-style order parameter per subject
  on the trained decoder's latent state distribution; check that
  cross-subject differences in the order parameter predict transfer
  cost in Aim 2.

## Seed variance (G2)

- Every headline number is reported across at least five seeds when
  the pipeline includes stochastic components.
- For deterministic pipelines (fixed dataset, fixed preprocessing,
  linear or convex fit) that do not admit multiple seeds: report
  cross-validation fold variance and cross-dataset replication as the
  G2-equivalent metric per gate ladder v1 addendum.

## Multiple-comparison discipline

- Every headline number is reported with its Benjamini-Hochberg
  FDR-corrected q-value.
- Uncorrected p-values are shown alongside only when the
  gate-relevant comparison is a single primary contrast.

## Robustness sweeps

- Physiological covariate sweep: refit with heart rate + respiration
  regressed out; report delta in test-retest.
- Site random effect (HCP-YA): report the estimated site variance.
- Time-of-day sweep (NSD, BMD): report AM vs PM performance.
- Attention proxy sweep: covariate-adjust for vigilance; check that
  decoders do not collapse to attention prediction.

## Trajectory-dynamics analyses (ADR-009)

### Primary: does the trajectory carry temporal structure?

- Unit of analysis: subject-session.
- Test: 200-permutation shuffle null on the Kolmogorov-Sinai entropy
  rate of the discretized state sequence. One-sided (below), because
  lower entropy rate means more structure.
- Statistic: empirical p-value plus a z-score against the null
  distribution.
- Multiple comparisons across subjects: Benjamini-Hochberg FDR 0.05.
- Sign concordance across subjects: two-sided binomial on the count
  of subjects whose observed entropy rate falls below the null mean.
  This is the EEG analogue of the G-fMRI.2 sign-concordance leg.

### Required Markov-assumption validation (currently NOT run)

No trajectory result is reportable as a scientific claim until all
four pass:

1. Implied-timescale plateau across a lag-time sweep.
2. Chapman-Kolmogorov agreement between `T(k * lag)` and `T(lag)^k`.
3. State-count stability: the structure verdict does not flip across
   a sweep of prototype counts.
4. Epoch-length stability: same, across epoch durations.

Failing any of these downgrades the trajectory result to a
descriptive pipeline demonstration, which is how the 2026-09-04
EEG-BCI run is currently classified.

### Reporting gate on trajectory outputs

Because the first real-data run showed temporal structure WITHOUT
first-order Markov validity, the trajectory outputs are split into
two tiers:

**Tier 1, reportable as descriptive statistics of the observed
sequence** (no Markov assumption required): stationary distribution
of observed occupancy, entropy rate, spectral gap, effective
dimension, and the shuffle-null verdict.

**Tier 2, reportable ONLY when implied-timescale plateau AND
Chapman-Kolmogorov both pass for that subject**: mean first passage
time, committor functions, and any statement phrased as a property
of an underlying Markov process rather than of the observed
sequence.

A subject failing validation contributes to Tier 1 results and is
explicitly excluded from Tier 2 results, with the exclusion count
reported.

## Handling of missing data

- Trials with more than 20 percent motion or artifact rejection are
  excluded before analysis, per the abstention rule.
- Subjects with fewer than the preregistered minimum number of usable
  trials per session are excluded from that session, not from the
  study. Exclusion counts are reported.

## Reporting

- Every primary analysis reports: point estimate, 95 percent CI,
  seed-variance range or CV-fold variance, corrected q-value, Bayes
  factor when null, effect size interpretation in one sentence.
- Every fMRI-grounded primary analysis carries the Goltermann/Huth
  triad numbers.
- Every failed aim carries the exact within-subject or within-session
  numbers as the primary result.
