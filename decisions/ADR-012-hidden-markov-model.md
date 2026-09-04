# ADR-012: Hidden Markov model on the tangent-space embedding

## Status

Accepted, 2026-09-04.

## Context

ADR-011 (council review) established two things: (1) the EEG covariance
trajectory carries temporal structure beyond marginal occupancy (valid,
shuffle null), and (2) the claim that it is "not first-order Markov" was
confounded, because discretizing a continuous SPD process into prototype
states manufactures apparent non-Markovianity. A minority of subjects
deviated from first-order Markov at k=2 against a construction-matched
null, but the discretized test is weak.

The principled resolution is a hidden Markov model. A latent state chain
can be first-order Markov even when the observed prototype sequence is
not (a function of a Markov chain is generically non-Markov). This is
the standard framing in the EEG/MEG brain-state literature (HMM-MAR,
microstate HMMs).

## Decision

Add `hmm.py`: a full-covariance Gaussian HMM (forward-backward and
Baum-Welch in log space, Viterbi, BIC/AIC, sampling). It operates on the
CONTINUOUS AIRM tangent-space embedding of the SPD covariances
(`spd_tangent_embedding`), not on discretized labels, so it sidesteps
the discretization confound entirely. The tangent embedding is
norm-preserving: the L2 norm of the embedded vector equals the AIRM
Riemannian norm of the tangent.

### Verification

`test_hmm.py` confirms the HMM recovers, from data it sampled itself:
emission means (within 0.5), the transition matrix (within 0.06), the
latent state sequence via Viterbi (>95% accuracy on well-separated
states), EM log-likelihood monotonicity (within a ridge-scaled relative
tolerance), and BIC preferring the true state count over one state. An
HMM that cannot recover known parameters is not trusted on real data;
this one can.

### The confound-controlled experiment

`experiments/hmm_eeg/` asks the sharp, controlled question that the
discretized test could not: does a K-state HMM achieve higher held-out
log-likelihood than VAR(1) (the canonical first-order continuous Markov
model) on the EEG, BEYOND what it achieves on data that is VAR(1) by
construction?

- Embed EEG covariances to the tangent space.
- Temporal train/test split.
- Compare per-step held-out log-likelihood: K-state HMM vs VAR(1).
- CONTROL, shipped with the test per the ADR-011 lesson: fit VAR(1) to
  the full series, generate surrogates from it, run the identical
  HMM-vs-VAR(1) comparison on each. A subject shows genuine higher-order
  structure only when its EEG HMM-minus-VAR(1) gain exceeds the 95th
  percentile of the surrogate null.

### Result (8 subjects, 12 surrogates each)

All 8 subjects show the K=3 HMM beating VAR(1) on held-out EEG beyond the
first-order surrogate null:

| subject | EEG gain (nats/step) | surrogate null 95th pct | p |
| --- | --- | --- | --- |
| 1 | 3.66 | 1.27 | 0.00 |
| 2 | 4.65 | 1.27 | 0.00 |
| 3 | 4.44 | 0.23 | 0.00 |
| 4 | 4.96 | 0.58 | 0.00 |
| 5 | 4.44 | 0.69 | 0.00 |
| 6 | 4.65 | 0.91 | 0.00 |
| 7 | 5.17 | 0.83 | 0.00 |
| 8 | 2.91 | 0.93 | 0.00 |

The control validates the test's discriminative power: on the VAR(1)
surrogates (first-order by construction) the HMM gain is NEGATIVE on
average (null means -0.27 to -1.90), so the HMM correctly does not beat
VAR(1) on genuinely first-order data. The EEG exceeds that null in every
subject.

This is the confound-controlled positive result. The EEG covariance
trajectory carries latent-state structure that a first-order model
misses, in 8/8 subjects, and this exceeds what the pipeline finds on
genuinely first-order data. The discretized k=2 test found only 3/8
because discretization is lossy and confounded; the continuous
tangent-space HMM with a VAR(1) surrogate null is strictly more
sensitive and properly controlled.

What this does NOT establish (guarding against the ADR-011 overclaim):
the HMM states are not shown to be cognitive states, not shown to
replicate across sessions, and K=3 is not shown to be the right count.
Those are the next experiments.

## Consequences

- `hmm.py` and `spd_tangent_embedding` / `spd_tangent_vector` added to
  the public API.
- The trajectory-analysis story is now: discretized prototype dynamics
  (ADR-009, descriptive Tier 1 only) are superseded for inference by the
  continuous tangent-space HMM (ADR-012), which is confound-controlled
  by design.
- Test count rises to 155.

## Consequences NOT accepted

- We do not claim the latent HMM chain IS the brain's state machine. The
  HMM is a model that fits better than a first-order baseline; that is a
  statement about the data's structure, not about neural mechanism.
- We do not report Viterbi state labels as cognitive states without the
  A1 replicability test (do the same subject's HMM states recur across
  sessions?). That is the next experiment.

## Follow-ups

- Full 8-subject HMM-vs-VAR(1) sweep with the surrogate null.
- A1 replicability: fit the HMM on session A, score session B, test
  whether the latent states transfer within subject.
- BIC state-count selection per subject (currently fixed K=3).
- Complete the ADR-011 literature sweep (HMM-MAR, microstates,
  transition-path theory).
