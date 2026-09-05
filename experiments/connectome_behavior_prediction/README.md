# Connectome Behavior Prediction

Claim: discrete connectome-state trajectories from EEG carry predictive
signal for behavioral condition labels (T1/T2) beyond a shuffled-label
null.

## Pipeline

1. Load public PhysioNet EEG-BCI motor-imagery runs (4, 8) with `mne`.
2. Keep sensorimotor EEG channels and bandpass 8 to 30 Hz.
3. For each cue event (T1/T2), build a 4-second trial and split into 1-second windows.
4. Compute one SPD covariance matrix per window.
5. Learn an AIRM prototype library and discretize each window to a state id.
6. Split by subject so train and test subjects are disjoint.
7. Fit a class-conditional Markov model from state-sequence to behavior label.
8. Evaluate held-out accuracy and run a permutation null by shuffling labels.

## Run

```bash
python experiments/connectome_behavior_prediction/run.py --subjects 1 2 3 4 5
```

If public dataset access is blocked in this environment, upload the EEG files
here and rerun.
