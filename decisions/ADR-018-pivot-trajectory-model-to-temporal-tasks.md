# ADR-018: Pivot the trajectory model to temporally-structured tasks

## Status

Accepted, 2026-09-05.

## Context

The behavior-decoding arc (cross-subject null -> within-subject null with an
MDM positive control -> geometry-preserving discretization, ADR-013 dynamics
through ADR-017) was run on PhysioNet EEG-BCI left-vs-right motor imagery. A
two-agent literature sweep (computational-neuroscience/benchmarks and
mathematics/neuropsychology) established that this task is the wrong
substrate for a state-TRAJECTORY model, for three independent reasons:

1. **The discriminative signal is static, by established physiology.** Motor
   imagery is decoded from sustained ERD/ERS mu/beta lateralization at C3/C4,
   a within-trial stationary feature. Single-covariance Riemannian
   classifiers are state of the art precisely because no temporal model is
   needed. A Markov/HMM transition model is not expected to add anything, and
   ours did not.
2. **The dataset is weak.** eegbci tops out around 0.60-0.65 population mean
   with high per-subject variance (MOABB benchmarks arXiv:2607.22778,
   arXiv:2606.24394), so per-subject near-chance is expected regardless of
   the representation.
3. **The one positive we found (ADR-017) is confounded.** Binning along the
   class-discriminant axis structurally favors occupancy over transitions.

Continuing to tune this (more channels, stronger MI datasets like Cho2017 or
Lee2019 via MOABB) would validate a decoder, not the trajectory thesis.

## Decision

Move the trajectory apparatus (`dynamics.py` Markov invariants, `hmm.py`,
`behavior.analyze_*`, `discretize.py`) to a task whose discriminative signal
is genuinely in the temporal SEQUENCE of brain states, where a
Markov/HMM transition model can beat a static/occupancy decoder. The
literature sweep named concrete, sourced candidates:

- **Sleep staging (transition structure).** Sleep-stage sequences have
  canonical transition regularities (W -> N1 -> N2 -> N3 -> REM cycling); the
  transition/dwell-time structure is diagnostic beyond marginal stage
  proportions. Sleep-EDF is already fetched and adaptered in the sibling
  cessation_manifold project, so this is the lowest-friction first target.
- **Decision-making / evidence accumulation.** HMM latent-state sequences and
  their transition timing predict performance fluctuations (Taghia et al.,
  Nat. Commun. 2018, doi:10.1038/s41467-018-04723-6).
- **Auditory attention decoding.** HMM state-sequence learning beats
  isolated-window classification for sustained-but-switching attention
  (arXiv:2607.18614).
- **Hippocampal replay.** Sequence order/compression is the entire signal
  (PMC5097117, PMC6013258); spike-train, not EEG, but the canonical example.

The decisive experiment for each: does the state-TRANSITION model beat the
OCCUPANCY baseline (the same `trajectory_gain` gate used throughout), on a
task the physiology says is temporal? A positive there validates the
trajectory apparatus in its intended regime; the MI arc showed the apparatus
is correct but was pointed at a static contrast.

## Method guardrails carried from the sweep

- **Use an unsupervised (Riemannian k-means) discretization for the
  transition test**, not the discriminant-axis binning, to avoid the
  ADR-017 occupancy confound. The discriminant-axis binning is for
  classification, not for asking where the signal lives.
- **Ground the covariance/classifier protocol in MOABB/pyRiemann**
  (`Covariances('oas')` for conditioning, tangent-space + logistic
  regression as the accuracy baseline) rather than ad-hoc choices; but note
  OAS/Ledoit-Wolf shrinkage is for conditioning, and can blur a spatial
  contrast, so validate it does not suppress the effect.
- **Cite the microstate prior art** (arXiv:2504.18882; PMC11763639) in any
  writeup: the discretization step is established, the Markov-on-symbols +
  occupancy-vs-transition dissociation is the increment.

## Consequences

- The MI behavior-decoding line is closed as an honest, bounded negative:
  the apparatus works, the task was static, the effect was weak and
  confounded. ADR-013 through ADR-017 stand as recorded, with ADR-017's
  post-hoc corrections.
- The next build targets sleep-stage transition decoding first (data on
  hand), with the occupancy-vs-transition gate as the primary readout.
- No further tuning of eegbci motor-imagery decoding.
