# decision_making_trajectory

Does the WITHIN-TRIAL sequence of brain states predict perceptual choice
better than a memoryless (occupancy) summary of the same trial? ADR-018
named decision-making as the second temporal target for the trajectory
apparatus after sleep staging (`experiments/sleep_transition_decoding/`,
McNemar p=1.18e-13). Decision-making has within-trial evidence accumulation
(Rungratsameetaweemana et al.; Taghia et al., Nat. Commun. 2018), so the
trajectory should matter at the single-trial timescale, not just across
epochs minutes apart.

## Data

OpenNeuro `ds002739` (simultaneous EEG-fMRI random-dot-motion perceptual
decision task, originally `ds001512`, reuploaded for privacy). EEG only,
4 subjects, run 1. Each `EEG_events_sub-XX_run-YY.mat` has, per trial:
`dotdirection`, `choice` (1=left, 2=right), `accuracy`, `confidence`, `RT`
(ms), `tstim`/`tresp`/`tconf` onsets (samples, fs=1000 Hz after the
dataset's own preprocessing), and an `excludedtrials` index. See
`data/raw/ds002739/README` for the full field description.

## What it runs

```bash
python3 experiments/decision_making_trajectory/run.py \
    --subjects 01 02 03 04 --run 01
```

Per subject: stimulus-locked 1.0s window per valid trial, split into 5
sub-windows, per-sub-window per-channel theta/alpha/beta relative band
power (robust-scaled). An UNSUPERVISED k-means (k=4, no labels used) builds
that subject's discrete state alphabet, giving one length-5 within-trial
state sequence per trial. Label = choice (left/right).
`neurospine.behavior.analyze_within_subject` does the rest: per-subject
stratified train/test split, class-conditional Markov model vs. occupancy
(0th-order) ablation, per-subject label-shuffle null (200 permutations),
and the group-level verdict.

## Result: null, on this window/feature choice

4 subjects, run 1, 141-156 valid trials each (excluded trials dropped per
the dataset's own `excludedtrials` index). Label balance: left/right splits
were 93/63, 77/64, 43/111, 86/70 across sub-01..sub-04 (sub-03 is the most
skewed at 28%/72%).

| Subject | Markov accuracy | Occupancy accuracy | Trajectory gain | Shuffle-null p |
|---|---|---|---|---|
| sub-01 | 0.516 | 0.468 | +0.048 | 0.498 |
| sub-02 | 0.456 | 0.456 | +0.000 | 0.811 |
| sub-03 | 0.525 | 0.574 | -0.049 | 0.612 |
| sub-04 | 0.468 | 0.597 | -0.129 | 0.726 |
| **mean** | **0.491** | n/a | **-0.032** | n/a |

**0/4 subjects significant (group binomial p=1.00). Mean trajectory gain is
slightly NEGATIVE (-0.032): the within-trial state-transition structure does
not beat the memoryless occupancy baseline, and neither beats its own
per-subject shuffle null.** Held-out accuracy hovers at chance (0.46-0.53
for a roughly-balanced two-class problem) for every subject.

**VERDICT: within-subject: no evidence above per-subject nulls.**

This is an honest null, not a confound: two subjects (03, 04) show occupancy
actually beating the trajectory model, which is the ablation doing its job
(if anything, the fixed 5-bin discretization is throwing away information
that a purely marginal state-count summary partially retains), and no
subject clears its own shuffle null in either direction. Read together with
the sleep-staging positive control, the honest interpretation is that a
1.0s post-stimulus window, 5 fixed sub-windows, k-means(k=4) on
theta/alpha/beta band power does not capture whatever within-trial
accumulation dynamics are present in this dataset's EEG at the group level
tested here, not that no such trajectory exists. Candidate follow-ups (not
run here): response-locked or RT-normalized windows, a supervised
discretization in the manner of `discretize.py` (with the correspondingly
label-aware shuffle null it requires), more sub-windows, or fitting an HMM
directly on continuous features as in Taghia et al. rather than
discretizing first.

## Honest caveats

- Fixed 1.0s post-stimulus window regardless of RT: some trials' responses
  land inside the window, some after it. This is a deliberate simplification
  (comparable sub-window features across trials) at the cost of not
  isolating pure pre-decision evidence accumulation; a response-locked or
  RT-normalized window is the natural follow-up if this window shows signal.
- k=4 states, k-means on 3-band x n-channel features is a simple, standard
  discretization, not a state-of-the-art latent-state model (e.g. an HMM
  fit directly on continuous features, as in Taghia et al.). The point here
  is the transition-vs-occupancy contrast under the same discipline used for
  sleep and motor imagery, not a best-possible decoder.
- Label balance and per-subject trial counts are reported by `run.py` before
  the analysis; a null result under balanced labels is a different claim
  than a null under a skewed occupancy confound (which `analyze_within_
  subject`'s occupancy ablation is designed to catch).

## Files

- `run.py`: data loading (`.mat` events + preprocessed EEG), feature
  extraction, unsupervised discretization, and the call into
  `neurospine.behavior.analyze_within_subject`.
- Verified in `instrument/tests/verification/test_decision_making_trajectory.py`
  (band power, trial windowing, discretization correctness on synthetic
  well-separated clusters). `analyze_within_subject` itself is verified in
  `instrument/tests/verification/test_behavior.py` (motor-imagery arc).
- `decisions/ADR-021-decision-making-trajectory.md`.
