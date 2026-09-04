# ADR-009: Thought trajectory as a Markov process on the cognitive manifold, with a probability-transition-matrix heuristic

## Status

Accepted, 2026-09-04.

## Context

ADR-008 built the Riemannian-topological cartography and the
purpose-constrained intervention scorer. A thought was still a
per-timepoint read: given `(subject, recordings, context_t)`, return
a `Thought`. Aayush pushed the framing on 2026-09-04:

> My theory here is that you can use this kind of mathematical
> computation to derive the process of where a thought travels
> throughout the brain and basically represent the complexities of
> human thought via some kind of probability matrix heuristic. Can
> you integrate this in.

And:

> Also find and use real data.

A thought is not a point on M. It is a trajectory `M(t)` on M, and
the object that summarizes its complexity is the transition kernel
`K(x, y) = P(state_{t+1} = y | state_t = x)`, together with the
invariants of the induced Markov process: stationary distribution
`pi`, entropy rate `H(pi | K)`, spectral gap `1 - lambda_2`, mean
first passage times, and Perron-cluster decomposition into
metastable "thought basins."

This is the natural probability-matrix heuristic: complexity =
non-triviality of `K`, and "where a thought travels" = the
committor and MFPT structure of the process.

## Decision

Add a fifth mathematical pillar to NEUROSPINE: **Markov transition
dynamics on the cognitive-state manifold**, with a probability-
transition-matrix heuristic as the summary output.

Concretely:

### 1. `dynamics.py` module

New module implementing transition-matrix estimation and Markov-state
invariants:

- `estimate_transition_matrix(state_indices, num_states, laplace)`:
  count-based Markov transition matrix from a sequence of discretized
  state indices, with Laplace smoothing.
- `stationary_distribution(T)`: left-Perron eigenvector, normalized.
- `entropy_rate(T, pi)`: `sum_i pi_i sum_j T_ij log(1/T_ij)` in
  nats, the Kolmogorov-Sinai entropy of the Markov chain.
- `spectral_gap(T)`: `1 - |lambda_2|`, where the second-largest
  eigenvalue modulus of `T` controls mixing time.
- `mean_first_passage_time(T, target)`: MFPT from every state to a
  designated target, solved as a linear system.
- `committor(T, source_set, target_set)`: harmonic function that
  gives P(reach target before source | start at x); the classical
  transition-path-theory object.
- `perron_cluster_analysis(T, k)`: PCCA-like sign-structure
  clustering into `k` metastable sets from the top-k eigenvectors.

Manifold binding: state discretization uses AIRM distance to a set
of prototype SPD matrices computed via `airm_frechet_mean` on
subclouds; the transition kernel therefore respects the manifold
geometry, not a Euclidean flattening.

### 2. `Thought` contract extension

Add a `trajectory_summary: dict[str, float] | None = None` field
carrying:

- `stationary_entropy`: `H(pi)`, the entropy of the stationary
  distribution (higher = more uniformly explored state space).
- `entropy_rate`: KS entropy in nats per step.
- `spectral_gap`: `1 - |lambda_2|`.
- `effective_dimension`: `exp(H(pi))`, the participation ratio.
- `mfpt_to_current_state`: mean first passage time from the
  stationary distribution to the currently-observed state.
- `metastable_basin_id`: index of the metastable set the current
  state belongs to (per PCCA).

Populated by a new provider `TrajectorySummaryProvider` (Protocol in
`providers.py`); gated by `FIELD_GATES["trajectory_summary"] =
["G7", "G9", "G14"]`.

### 3. `Intervention` contract extension

Interventions now consider the transition kernel: `Intervention`
carries a new field
`predicted_stationary_shift: float | None = None`
giving the total-variation distance between the pre-intervention and
post-intervention stationary distributions under the linearized
channel effect on `K`. A high-alignment channel that would not
actually shift `pi` toward `Q` is downgraded in the ranking.

### 4. Real-data experiment

Ship `experiments/spd_transition_eegbci/` that:

- Downloads ~30 MB of PhysioNet EEG-BCI (motor imagery) via
  `mne.datasets.eegbci.load_data`. This is a real public dataset;
  no gate.
- For one subject, windows the raw EEG (Fz/Cz/Pz/C3/C4 subset)
  into 2-second epochs.
- Computes SPD covariance per epoch and projects to a common
  Frechet-mean-centered SPD family.
- Discretizes states via k-medoids on AIRM distance to a small
  prototype library.
- Estimates the transition matrix on the discretized state space.
- Reports stationary distribution, entropy rate, spectral gap, and
  the metastable clustering.
- Verifies row sums = 1, stationary distribution eigenvalue = 1
  numerically.

This is the first real-data run in the repo and the first test that
the manifold + dynamics pipeline actually clears numerical identities
against measured signal, not only synthetic ground truth.

## Consequences

- One new module (`dynamics.py`), one new provider Protocol
  (`TrajectorySummaryProvider`), one new field on `Thought`, one new
  optional field on `Intervention`.
- One new experiment directory with a Makefile target and a runnable
  Python script; adds `mne` and `scikit-learn` as optional
  dependencies via `[project.optional-dependencies]`.
- Verification tests for `dynamics.py` cover: row-stochasticity,
  stationary-distribution eigenvalue, entropy-rate bounds, spectral
  gap on known-mixing chains, MFPT solving a linear system that
  matches an analytical two-state expectation.
- Gate ladder: no new gate; existing G14 (manifold correctness)
  covers manifold-side identities of `dynamics.py`, G7 + G9 cover
  the calibration and reliability side of the trajectory summary
  itself.
- The intervention scorer now has a second-order check (kernel-shift
  under channel) alongside the first-order geodesic-tangent check.

## Consequences NOT accepted

- We do not commit to a specific discretization method. K-medoids on
  AIRM distance is the reference in `dynamics.py`; VAMP / diffusion
  maps / SFA remain candidates for future ADRs.
- We do not require the Markov assumption to hold. `entropy_rate` on
  a non-Markov trajectory is a lower bound; the analysis plan will
  test the Markov assumption via block-shuffling on real data.
- We do not extend to hidden Markov models this ADR. HMMs and their
  variational Bayesian variants (e.g. VBHMM) queue for ADR-011.

## External anchors

- Coifman + Lafon 2006 (Diffusion maps) as the alternative
  discretization / graph-Laplacian approach; textbook cite queued.
- Deuflhard + Weber (PCCA / PCCA+), Prinz, Wu, Sarich 2011 (Markov
  state models in molecular dynamics; the math transfers directly).
  Queued for pubmed round-4.
- `pubmed-22010143` Barachant et al. 2012: SPD manifold operations
  the transition kernel discretization depends on.
- `pubmed-31320220` Sohn et al. 2019: cortical curved manifold and
  RNN dynamics as the biological substrate for the assumption that
  cognition lives on a low-dim manifold with meaningful transitions.
- `pubmed-42618509` Miller, Brincat, Roy 2026: wave-mediated
  routing is exactly what modulates the transition kernel entries
  `T_ij` in a biologically-grounded way.

## Purpose registry entries added

- `explore_cognitive_state_space` (analytic-only, no action taken;
  produce a trajectory summary + persistence diagram + transition
  matrix on a single-subject session).
- `identify_metastable_basin` (analytic-only; return the PCCA
  clustering and each state's assignment).

Both are analytic; they emit no side effects and require no ethics
review beyond the standard NEUROSPINE ethics section.

## Follow-ups

- Pubmed round-4: Markov state models in neuroscience, VAMP,
  Coifman-Lafon diffusion maps, transition-path theory in the brain.
- ADR-010: hidden Markov / VBHMM extension.
- ADR-011: expected-free-energy scoring in the intervention module
  (Friston et al. 2021 anchor already indexed as pubmed-33626312).
