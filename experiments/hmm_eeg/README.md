# hmm_eeg

ADR-012 experiment: does a hidden Markov model beat a first-order model
on the EEG covariance trajectory, beyond a first-order-null control?

## Why this exists

The council review (ADR-011) showed the discretized Markov test was
confounded: projecting a continuous SPD process onto prototype states
manufactures apparent non-Markovianity. This experiment avoids
discretization entirely and ships its confound control with the test.

## Method

1. Load EEG (PhysioNet eegmmidb, runs 4+6), per-epoch SPD covariance.
2. Embed each covariance into the AIRM tangent space at the group
   Frechet mean (`spd_tangent_embedding`), a norm-preserving Euclidean
   coordinate. No discretization.
3. Temporal train/test split (70/30).
4. Compare per-step held-out log-likelihood: a K-state Gaussian HMM vs
   VAR(1), the canonical first-order continuous Markov model.
5. CONTROL: fit VAR(1) to the full series, generate surrogates from it
   (first-order by construction), run the identical HMM-vs-VAR(1)
   comparison on each. A subject is called genuinely higher-order only
   when its EEG gain exceeds the 95th percentile of the surrogate null.

## Result (2026-09-04)

8/8 subjects: the HMM beats VAR(1) on held-out EEG (gains 2.9 to 5.2
nats/step) far beyond the surrogate null (95th percentiles 0.23 to
1.27, all p=0.00). On the VAR(1) surrogates the HMM gain is negative on
average, confirming the test does not spuriously favor the HMM: it wins
only when there is real higher-order structure to find.

## What this does and does not show

- SHOWS: the EEG covariance trajectory has latent-state structure a
  first-order model misses, confound-controlled, in every subject.
- DOES NOT SHOW: that the HMM states are cognitive states, that they
  replicate across sessions, or that K=3 is the right count. Those are
  the next experiments (session-to-session replicability, BIC state
  selection).

## Running

    python experiments/hmm_eeg/run.py --subjects 1 2 3 4 5 6 7 8 \
        --n-surrogates 12 --hmm-states 3

Requires the neurospine package (numpy, scipy) and mne for the data.
