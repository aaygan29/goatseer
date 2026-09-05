# geometry_preserving_discretization

Can a discretization that PRESERVES the covariance geometry retain the
decoding signal that the AIRM-prototype discretization discarded? (ADR-017.)

## The setup

The within-subject experiment showed a Riemannian MDM decoded left-vs-right
motor imagery that the prototype-state Markov model could not: the global
prototypes collapse the C3/C4 lateralization that separates the classes.
This experiment discretizes instead in the tangent space at the AIRM Frechet
mean (norm-preserving; Barachant et al. 2012) ALONG the class-discriminant
axis, so states encode the discriminative geometry.

Per subject, same train/test split, three arms plus the MDM ceiling. The
supervised-tangent null refits the discriminant axis on shuffled labels, so
it tests the whole supervised pipeline, not just the Markov step.

```bash
python experiments/geometry_preserving_discretization/run.py --subjects 1 2 3 4 5 6 7 8 --states 5
```

## Result

| Arm | Mean held-out accuracy |
|---|---|
| AIRM-prototype -> Markov (baseline) | 0.542 |
| **Supervised-tangent OCCUPANCY (this tier)** | **0.635** |
| Supervised-tangent -> Markov | 0.531 |
| Raw-covariance MDM (ceiling) | 0.604 |

The geometry-preserving discretization recovers the signal (+0.094 over the
prototype baseline) and tracks the MDM ceiling per subject (subj 2:
tangent-occupancy 0.833 = MDM 0.833, p = 0.045; subj 7: 0.917 vs MDM 1.000,
p = 0.055). Two takeaways:

1. **The discretization was the limit, and this fixes it.** States that
   preserve the discriminative geometry carry the signal.
2. **The signal lives in OCCUPANCY, not the trajectory.** The Markov
   transition model does not beat its own occupancy baseline: this signal is
   a static covariance feature, not a temporal transition structure.

## Honest caveats

- Not cohort-significant: 1/8 subjects individually clear the null (group
  p = 0.34). Same power ceiling as MDM (~9 test trials/subject, 5 channels).
  The recovery is descriptively clear (tracks MDM), not a population claim.
- Discriminant axis = between-class direction (not full LDA), for stability
  in the high-dim tangent space with few samples.

## Files

- `neurospine.discretize.SupervisedTangentDiscretizer` and the helpers
  `discriminant_axis` / `quantile_edges` / `assign_states`, verified in
  `tests/verification/test_discretize.py`.
- `run.py`: the three arms, the MDM ceiling, and the supervised-pipeline null.
