# ADR-017: Geometry-preserving discretization

## Status

Accepted, 2026-09-05.

## Context

The within-subject decoding experiment localized a real limitation. A
Riemannian minimum-distance-to-mean (MDM) decoder read left-vs-right motor
imagery off the raw covariances, but the connectome-state Markov model
(ADR-009), fed by an AIRM-prototype discretization, could not. The
diagnosis: reducing each window covariance to its nearest of a few global
prototypes collapses exactly the covariance-geometry lateralization (C3 vs
C4) that separates the classes. The discretization, not the data, was the
limit.

## Decision

Add `instrument/src/neurospine/discretize.py`: discretize in the TANGENT
SPACE at the AIRM Frechet mean (a norm-preserving Euclidean embedding of
the SPD manifold; Barachant et al. 2012), along the class-discriminant
axis, so the resulting states encode the discriminative geometry instead of
averaging it away. The state sequence is preserved, so the trajectory model
still applies.

`SupervisedTangentDiscretizer.fit(matrices, labels, n_states)` computes the
Frechet-mean reference, the discriminant axis (leading between-class-scatter
eigenvector, which is the class-mean difference for two classes), and
quantile bin edges of the training projections. `transform` maps any SPD
matrix to a state along that axis. Helpers `discriminant_axis`,
`quantile_edges`, `assign_states` are exposed so the reference and tangent
vectors (label-independent, expensive) can be computed once and only the
axis and bins refit per shuffle.

Rigor note on supervision: the discriminant axis uses training labels, so a
shuffle null MUST refit the axis on shuffled labels, or the null is unfairly
easy. `experiments/geometry_preserving_discretization/` does exactly this.

## External anchor

- Barachant et al. 2012 (tangent-space projection of covariance matrices
  for BCI). Bins along a discriminant direction are the supervised analogue
  of their tangent-space LDA.

## Result

Same subjects and splits as the within-subject experiment, three arms:

| Arm | Mean held-out accuracy |
|---|---|
| AIRM-prototype -> Markov (baseline) | 0.542 |
| **Supervised-tangent OCCUPANCY (this tier)** | **0.635** |
| Supervised-tangent -> Markov | 0.531 |
| Raw-covariance MDM (ceiling) | 0.604 |

The geometry-preserving discretization RECOVERS the decoding signal that the
prototype discretization discarded (+0.094 over baseline), and it tracks the
MDM ceiling per subject (subj 2: tangent-occupancy 0.833 = MDM 0.833,
p = 0.045; subj 7: 0.917 vs MDM 1.000, p = 0.055). Two conclusions:

1. **The discretization was the limit, and this fixes it.** States built to
   preserve the discriminative geometry carry the signal; global AIRM
   prototypes do not.
2. **The signal lives in OCCUPANCY, not the trajectory.** The Markov
   transition model (0.531) does not beat its own occupancy baseline
   (0.635): for this task the discriminative feature is a static covariance
   property, not a temporal transition structure. The transition parameters
   only dilute it on small data.

## Honest limitations

- **Not cohort-significant.** Only 1 of 8 subjects individually clears the
  shuffle null (group binomial p = 0.34). This is the same power ceiling
  the MDM control hits: ~9 test trials per subject in 5 channels. The
  recovery is descriptively clear (mean tracks MDM, per-subject tracks MDM)
  but a population claim needs more trials and channels.
- The discriminant axis is the between-class direction, not full LDA
  (no within-class whitening), chosen for stability in the high-dimensional
  tangent space with few samples. Full LDA is a possible refinement.
- This does not resurrect the trajectory model for this task. It shows the
  state REPRESENTATION can retain the signal; where the signal is temporal
  (not the case here), the trajectory kernel would then have something to
  work with.

## Post-hoc corrections (2026-09-05, multi-agent literature review)

A two-agent literature sweep (computational-neuroscience/benchmarks and
mathematics/neuropsychology) surfaced three corrections that a reviewer
would raise, recorded here rather than buried:

1. **The n=8 recovery was small-sample optimism.** Rerun at n=20 with the
   same 5-channel method, the MDM ceiling falls 0.604 -> 0.571 and the
   tangent-occupancy recovery falls +0.09 -> +0.04 (3/20 subjects, group
   p = 0.075). The effect is real but weak and only marginally significant,
   not the strong effect 8 subjects implied.
2. **The "tightened" run (15 channels + Ledoit-Wolf) BACKFIRED to chance
   (0.50).** Shrinkage pulls the covariance toward the isotropic identity,
   which blurs the exact C3-vs-C4 variance lateralization the decoder needs.
   More channels plus shrinkage was worse, not better. The lesson: pipeline
   choices must be grounded in the benchmark protocol, not assumed.
3. **A binning confound favors occupancy over transitions.** Because states
   are binned ALONG the class-discriminant axis (chosen to separate the
   marginal distribution), transitions are structurally disadvantaged
   relative to occupancy. So "occupancy > transitions" is partly an
   artifact of the discretization design, not a fully independent finding.
   An unsupervised (Riemannian k-means) discretization would be the fair
   comparison.

Context corrections:

- **The method is established, not novel.** Tangent-space discretization of
  covariance trajectories is "Riemannian covariance-microstate analysis"
  (see the SPD-manifold clustering review arXiv:2504.18882, and PMC11763639
  on tangent-space k-means microstate clustering). The only increment here
  is discriminant-axis binning plus a Markov chain on the symbol sequence.
- **The finding is expected physiology, not a discovery.** Motor-imagery
  discriminability is a sustained ERD/ERS mu/beta lateralization at C3/C4
  (a static within-trial feature), which is exactly why single-covariance
  Riemannian classifiers are state of the art and why a temporal model adds
  nothing. Our Markov-null is consistent with decades of literature.
- **eegbci is a known-weak dataset** (~0.60-0.65 population ceiling, high
  per-subject variance; MOABB benchmarks arXiv:2607.22778, arXiv:2606.24394),
  so near-chance per-subject is within the expected range independent of the
  representation question.

Net: ADR-017's demonstration that a geometry-preserving discretization
retains more than the prototype one still holds directionally, but the
effect is weak, partly confounded, and on a task where a trajectory model is
not expected to help. The correct response is not to tune this harder but to
move the trajectory apparatus to a task with genuine temporal structure
(ADR-018).
