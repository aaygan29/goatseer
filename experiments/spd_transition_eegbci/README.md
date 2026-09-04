# spd_transition_eegbci

First real-data experiment in NEUROSPINE. Implements the ADR-009
thought-trajectory transition kernel on public EEG.

## Claim under test

A subject's EEG covariance trajectory, discretized on the AIRM
(affine-invariant Riemannian) manifold, induces a Markov transition
matrix whose invariants (stationary distribution, entropy rate,
spectral gap, metastable decomposition) are computable, numerically
well-formed, and non-degenerate on real measured signal.

This is deliberately a weak claim. It establishes that the pipeline
runs end to end on real data and that the numerical identities hold
outside synthetic control. It does NOT claim the transition matrix is
subject-specific, replicable across sessions, or predictive of
behavior. Those are A1 / A2 claims and require the full protocol in
`study/PROTOCOL.md`.

## Data

PhysioNet EEG Motor Movement/Imagery Dataset, runs 4 and 6 (motor
imagery: left vs right fist). Fetched via `mne.datasets.eegbci`.
Public, no data-use agreement, roughly 30 MB for two runs.

Reference: Schalk, McFarland, Hinterberger, Birbaumer, Wolpaw (2004),
"BCI2000: A General-Purpose Brain-Computer Interface (BCI) System",
IEEE TBME 51(6):1034-1043. PhysioNet: Goldberger et al. (2000).

## Pipeline

1. Load runs 4 and 6, standardize channel names, apply the
   standard_1020 montage.
2. Restrict to five sensorimotor channels (C3, C4, Cz, Fz, Pz).
3. Common average reference, bandpass 8-30 Hz (mu + beta).
4. Window into 2-second non-overlapping epochs.
5. Per epoch: sample covariance, symmetrized, ridged to guarantee
   strict positive-definiteness.
6. K-medoids on AIRM distance with AIRM Frechet-mean prototype
   updates, `--prototypes` clusters (default 6).
7. Discretize each epoch to its nearest prototype under AIRM.
8. Estimate the Markov transition matrix with Laplace smoothing.
9. Report stationary distribution, stationary entropy, entropy rate,
   spectral gap, effective dimension, metastable labels.
10. Numerically verify row-stochasticity and `pi @ T == pi`.

## Gates this experiment touches

- **G14 (manifold correctness)**: the AIRM identity tests in
  `instrument/tests/verification/test_manifold.py` must pass, and the
  real-data run must produce a row-stochastic T with a valid
  stationary distribution. Both are asserted in the output JSON as
  `row_stochasticity_check` and `stationarity_check`.
- **G1 (provenance)**: dataset is public and version-pinned by MNE's
  fetcher; the exact runs (4, 6) and channel subset are recorded in
  this README and in the output JSON.
- **G10 (reproducibility)**: `make reproduce` runs the synthetic
  control then three subjects end to end.

## Gates this experiment does NOT touch

G2, G3, G4, G5, G6, G7, G8, G9, G11, G12, G15, and the entire
Goltermann/Huth fMRI triad. This is EEG, single-session,
descriptive. No claim is gated on it.

## Running

```
make synthetic   # dynamics verification tests; required first
make real        # subject 1
make real SUBJECT=7 PROTOTYPES=8
make reproduce   # synthetic + subjects 1, 2, 3
```

Output lands in `results/summary_subject-NNN.json` (gitignored).

## Synthetic-first rule

Per `experiments/README.md`, the synthetic control runs before the
real target. Here the synthetic control is the `test_dynamics.py`
verification suite, which checks every Markov invariant against
analytically-known values (two-state stationary distribution, MFPT
`1/a`, uniform-chain entropy rate `log n`, identity-chain zero
spectral gap). The Makefile enforces the ordering: `real` depends on
`synthetic`.
