# connectome_behavior_prediction

Predict a behavior label from a sequence of discrete neural states, with a
subject-disjoint split, a label-shuffle null, and an occupancy ablation
that keeps the model honest about whether it is really using the
trajectory.

## What it does

Each trial is a short trajectory over a shared alphabet of discrete
connectome states. A class-conditional Markov model
(`neurospine.behavior`) learns per-behavior start and transition
probabilities; a trial is classified by likelihood. Held-out accuracy is
tested against a label-shuffle null and against an occupancy baseline.

The demo pipeline discretizes PhysioNet EEG-BCI motor-imagery covariances
into AIRM-prototype states and predicts left-vs-right imagery (T1/T2). But
the analysis engine is data-agnostic: any discrete state sequences work.

## Two ways to run

### 1. The EEG demo (public PhysioNet data, auto-downloaded via MNE)

    python experiments/connectome_behavior_prediction/run.py \
        --subjects 1 2 3 4 5 --states 6 --n-permutations 200

### 2. Bring your own data (any modality)

Provide a `.npz` or `.json` with three arrays and run:

    python experiments/connectome_behavior_prediction/run.py \
        --input my_data.json --states <K> --n-permutations 200

The only contract is:

- `sequences`: a list of 1D integer arrays, each a trial's state
  trajectory, values in `[0, K-1]`. Any modality (EEG, fMRI, MEG, pupil,
  behavior) works once it is discretized into `K` states.
- `labels`: one behavior label per sequence.
- `subject_ids`: one subject id per sequence, so the train/test split is
  subject-disjoint (no subject on both sides).

Equivalently, call the engine directly:

    from neurospine.behavior import analyze_state_sequences
    result = analyze_state_sequences(sequences, labels, subject_ids,
                                     n_states=K, n_permutations=200)

## How the result is gated (read this before believing a number)

Two controls decide the verdict, and both must pass for the strong claim:

1. **Subject-disjoint split.** No subject appears in both train and test.
   Pooling a subject across the split inflates accuracy; this pipeline
   forbids it. (This is why the demo numbers are honest, not high.)
2. **Occupancy ablation.** A 0th-order bag-of-states baseline that ignores
   temporal order. The Markov model earns the word "trajectory" only if
   its transition structure beats marginal state occupancy, not just the
   shuffle null. This is the dynamics-vs-static confound settled in
   ADR-011/012; `trajectory_gain = markov_accuracy - occupancy_accuracy`.

Verdict logic: above the null AND above occupancy -> "trajectories predict
behavior"; above the null but not occupancy -> "occupancy predicts
behavior"; otherwise -> "no evidence above the null".

## Demo result (honest, and negative)

On PhysioNet EEG-BCI, subject-disjoint, 20 subjects (600 trials, 180 held
out): held-out accuracy 0.47, occupancy 0.52, `trajectory_gain` -0.04,
permutation p = 1.0. Verdict: **no evidence above the shuffle null**. The
connectome-state pipeline does not predict left-vs-right motor imagery
across subjects, and the transition structure adds nothing over occupancy.
This is the disciplined outcome once leakage is removed: earlier
within-subject numbers were leakage, not signal. Reported as-is; the value
of the pipeline is that it will not let an occupancy effect or a
within-subject leak masquerade as a trajectory result.

## Files

- `neurospine.behavior`: the model and the reusable `analyze_state_sequences`
  engine (subject-disjoint split, Markov + occupancy fit, shuffle null,
  gated verdict). Verified in `tests/verification/test_behavior.py`.
- `run.py`: the EEG adapter plus the `--input` bring-your-own-data path.
