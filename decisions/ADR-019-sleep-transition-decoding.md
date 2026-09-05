# ADR-019: Supervised sequence decoding, and the sleep-transition positive control

## Status

Accepted, 2026-09-05.

## Context

ADR-018 pivoted the trajectory apparatus off motor imagery (a static ERD/ERS
contrast where a transition model cannot help, confirmed by literature and by
our own null) toward tasks whose discriminative signal is genuinely in the
temporal SEQUENCE. It named sleep staging as the first target: sleep-stage
sequences are strongly constrained (W -> N1 -> N2 -> N3 -> REM cycling; abrupt
jumps are rare), so a decoder that uses the stage-TRANSITION structure should
beat a memoryless per-epoch classifier. That contrast is the positive control
the program needed: a regime where the trajectory model must win.

## Decision

Add `instrument/src/neurospine/sequence_decode.py`: a
`SupervisedSequenceDecoder` with per-class Gaussian emissions plus a
class-transition matrix, estimated directly from labeled sequences, decoded
two ways:

- WITH transitions: Viterbi over emissions and the transition matrix.
- WITHOUT transitions: per-timestep argmax of the emission likelihood (a
  memoryless classifier; a uniform transition matrix).

`transition_gain` reports `accuracy(with) - accuracy(without)`. A positive
gain means the temporal transition structure carries decodable signal beyond
the per-epoch features. This is a supervised complement to the unsupervised
Baum-Welch `GaussianHMM`: here the states ARE the labels, so the
transitions-on-vs-off contrast is a clean, interpretable readout, and the
module is reusable for any labeled-sequence task (sleep now, decision-making
next).

`experiments/sleep_transition_decoding/` runs it on PhysioNet Sleep-EDF
Expanded (added to `neurospine.io` and `scripts/fetch_sleep_edfx_subset.sh`).
Each 30s epoch becomes a per-band relative-power feature vector on two EEG
channels; the decoder is fit leave-one-recording-out; each held-out night is
decoded with and without transitions.

## External anchors

- Kemp et al. 2000 (Sleep-EDF); Goldberger et al. 2000 (PhysioNet).
- Temporal-context-helps-staging is the standard result behind sequence
  sleep stagers (e.g. SeqSleepNet and HMM/CRF post-processing); the
  transition matrix encodes the physiological stage-cycling constraint.

## Result

Leave-one-recording-out on Sleep-EDF (initial 3 recordings, 5 stages each):

| | accuracy |
|---|---|
| WITH transitions (Viterbi) | 0.834 |
| WITHOUT transitions (memoryless) | 0.816 |

Positive transition gain (+0.018) in **3/3 recordings**. A paired-epoch
**McNemar test across all held-out epochs is decisive: adding transitions
FIXED 278 epochs and BROKE 129, p = 1.18e-13.** The per-epoch classifier is
already strong (band power is stage-discriminative), so the accuracy gain is
modest, but the transition model corrects more than twice as many epochs as
it harms, and the effect is overwhelmingly significant. This is the mirror
image of the motor-imagery result: there transitions carried nothing (static
contrast), here they help in every recording. The trajectory apparatus works
in the regime the physiology says is temporal.

## Honest limitations

- The accuracy gain is small because per-epoch staging accuracy is already
  high (a ceiling effect); the claim is direction, consistency, and the
  paired-epoch significance, not a large accuracy jump. The recording-level
  sign test is underpowered at N=3 (p = 0.125); the paired-epoch McNemar test
  (p = 1e-13) is the primary significance. The fetch script pulls up to 14
  recordings and the fold-level test should be re-run at that N.
- Two EEG channels and simple band-power features; a full sleep stager uses
  EOG/EMG and richer features. The point here is the transition-vs-no-
  transition contrast, not a state-of-the-art stager.
- Emissions are per-stage Gaussians (not the covariance-manifold pipeline);
  the trajectory question is about the label sequence, so Euclidean
  band-power features are the honest, standard choice for staging.

## Consequences

- The trajectory apparatus is validated in a temporal regime, closing the
  loop the motor-imagery arc opened.
- `SupervisedSequenceDecoder` is the reusable engine for the next target,
  decision-making / evidence-accumulation (ADR-018), where within-trial
  state switching should again make transitions informative.
