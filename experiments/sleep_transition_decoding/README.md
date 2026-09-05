# sleep_transition_decoding

Does the temporal TRANSITION structure of brain states carry decodable
signal? Sleep staging is the positive control (ADR-018/019): stage sequences
are strongly constrained, so a transition-aware decoder should beat a
memoryless one, unlike motor imagery where transitions carried nothing.

## What it runs

PhysioNet Sleep-EDF Expanded (`scripts/fetch_sleep_edfx_subset.sh`). Each 30s
epoch becomes a per-band relative-power feature vector (delta/theta/alpha/
sigma/beta on two EEG channels). A `SupervisedSequenceDecoder`
(`neurospine.sequence_decode`: per-stage Gaussian emissions + a stage-
transition matrix) is fit leave-one-recording-out and each held-out night is
decoded two ways:

- WITH transitions: Viterbi over emissions and the transition matrix.
- WITHOUT transitions: per-epoch argmax of the emission likelihood.

```bash
bash scripts/fetch_sleep_edfx_subset.sh        # PhysioNet, up to 14 recordings
python experiments/sleep_transition_decoding/run.py
```

## Result: transitions carry signal here

Leave-one-recording-out (initial 3 recordings, 5 stages):

| Decoder | Mean accuracy |
|---|---|
| WITH transitions (Viterbi) | 0.834 |
| WITHOUT transitions (memoryless) | 0.816 |

- Positive transition gain (+0.018) in **3/3 recordings**.
- **Paired-epoch McNemar test: transitions FIXED 278 epochs, BROKE 129,
  p = 1.18e-13.** The transition model corrects more than twice as many
  epochs as it harms.

This is the mirror image of `within_subject_decoding/` and
`geometry_preserving_discretization/`: there, on motor imagery, the signal
was static and transitions added nothing. Here, on sleep, the transition
structure helps in every recording and overwhelmingly at the epoch level.
The trajectory apparatus works in the regime the physiology says is temporal.

## Honest caveats

- The accuracy gain is small because per-epoch staging is already near
  ceiling; the claim is direction, consistency, and paired-epoch
  significance. The recording-level sign test is underpowered at N=3
  (p = 0.125); McNemar (p = 1e-13) is the primary test. Re-run with more
  recordings (the fetch pulls up to 14) to power the fold-level test.
- Two EEG channels, simple band-power features; not a state-of-the-art
  stager. The point is the transition-vs-no-transition contrast.

## Files

- `neurospine.sequence_decode.SupervisedSequenceDecoder` / `transition_gain`,
  verified in `tests/verification/test_sequence_decode.py`.
- `run.py`: feature extraction, leave-one-recording-out, and the McNemar test.
