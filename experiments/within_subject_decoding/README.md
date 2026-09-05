# within_subject_decoding

Does a connectome-state trajectory predict behavior WITHIN a subject, where
the model does not have to generalize across anatomy? And if not, is the
signal absent, or is it the representation that loses it?

## Why this experiment

The cross-subject experiment (`connectome_behavior_prediction/`) returned an
honest null: state trajectories did not predict motor imagery across
subjects. The natural next question is within-subject. This experiment
answers it, and adds a positive control so a null cannot be misread as
"no signal in the data".

## What it runs

PhysioNet EEG-BCI, left-vs-right motor imagery (T1/T2), 8 subjects, fetched
through `neurospine.io.fetch_eegbci`. Per subject:

1. Build trial-wise covariance trajectories on 5 sensorimotor channels.
2. Learn a subject-specific AIRM prototype library and discretize each
   trial into a connectome-state sequence.
3. Split that subject's trials, fit the Markov model + occupancy baseline,
   evaluate held-out, run a per-subject label-shuffle null
   (`neurospine.behavior.analyze_within_subject`).
4. **Positive control:** a Riemannian minimum-distance-to-mean (MDM)
   decoder on the raw covariances (Barachant et al. 2012), the canonical
   left-vs-right decoder, on the same trials.

```bash
python experiments/within_subject_decoding/run.py --subjects 1 2 3 4 5 6 7 8 --states 5
```

## Result: the representation, not the data, is the limit

| Decoder | Mean held-out accuracy | Per-subject high |
|---|---|---|
| Connectome-state Markov (this repo's ADR-009 representation) | 0.573 | no subject above ~0.6 |
| Raw-covariance MDM (positive control) | 0.615 | subj 5 = 0.83, subj 7 = 0.92 |

The state-trajectory model shows **no evidence above per-subject nulls**
(1/8 subjects, group binomial p = 0.34, mean trajectory gain +0.03). But
the MDM control decodes the same trials well in several subjects. So the
discriminative left-vs-right signal IS present within subject, in the
covariance geometry, and the discretization into a small shared state
alphabet discards it before the Markov model ever sees it.

This is a finding about the representation: reducing each window to its
nearest of a few AIRM prototypes collapses exactly the spatial-covariance
lateralization (C3 vs C4) that separates the classes. The
state-trajectory kernel is the right tool for asking where a thought
dwells and travels; it is the wrong tool for a decoding contrast that
lives in the fine covariance structure.

## Honest caveats

- MDM itself is modest and variable here (5 channels, ~9 test trials per
  subject; some subjects sit at chance). The robust claim is the CONTRAST
  (MDM recovers signal the state model does not), not a strong absolute
  MDM number.
- The state model is not "broken": on data whose class difference lives in
  transition structure rather than covariance geometry it would behave
  differently. This experiment shows the mismatch for THIS task.
- Discretization here is unsupervised and per-subject (leakage-free for
  labels). A supervised or finer discretization might retain more; that is
  a separate question.

## Files

- `neurospine.behavior.analyze_within_subject`: the reusable per-subject
  engine (split, Markov + occupancy, per-subject null, cohort aggregation),
  verified in `tests/verification/test_behavior.py`.
- `run.py`: the EEG adapter (via `neurospine.io`) plus the MDM control.
