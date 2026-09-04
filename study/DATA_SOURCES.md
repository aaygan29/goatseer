# Data sources

Public datasets NEUROSPINE uses. Every dataset carries its access route,
size, and the aim and prediction dimension it feeds.

## Primary (Aim 1, individual scale)

### Natural Scenes Dataset (NSD)

- Modality: 7T fMRI, natural image viewing.
- Subjects: 8. Sessions: 30 to 40 per subject.
- Per-subject data volume: highest of any public fMRI dataset. This is
  why NSD is the A1 anchor.
- Access: naturalscenesdataset.org, registered use.
- Feeds: `PerceptionDecoder`, `MemoryDecoder`, per-subject calibration
  for `SubjectAdapter`.

### BOLD Moments Dataset (BMD)

- Modality: 3T fMRI, natural video viewing.
- Subjects: 10. Sessions: 5 per subject.
- Access: openneuro ds005165.
- Feeds: `PerceptionDecoder` (temporal), `MemoryDecoder`.

## Supplementary (Aim 2, group scale)

### HCP Young Adult (HCP-YA)

- Modality: 3T fMRI task battery + rest.
- Subjects: ~1200. Sessions: 2 per subject.
- Access: humanconnectome.org, registered use.
- Feeds: cross-subject transfer via `SubjectAdapter`; site random
  effect for the robustness sweep.

### DEAP

- Modality: 32-channel EEG + facial video + physiology.
- Subjects: 32. Sessions: 1 per subject (40 trials each).
- Access: eecs.qmul.ac.uk/mmv/datasets/deap/, registered use.
- Feeds: `AffectDecoder` (primary A1 anchor for affect).

### NATVIEW

- Modality: EEG + fMRI simultaneous, naturalistic viewing.
- Subjects: ~30.
- Access: openneuro ds004186.
- Feeds: `AffectDecoder`, multimodal fusion validation.

## Reward and decision (Aim 1 and 2, decision + reward dimensions)

### ds005479 (MID task, current fork)

- Modality: 3T fMRI, monetary incentive delay task.
- Subjects: ~120.
- Access: openneuro ds005479 (verify DOI).
- Feeds: `RewardDecoder`, `DecisionDecoder`, `nacc-anticipation`
  benchmark task in the portfolio.

## Reliability characterization (gates G7, G9, G-fMRI.1/2/3)

### ds003171 (propofol grading)

- Modality: 3T fMRI, graded propofol anesthesia.
- Subjects: 26.
- Access: openneuro ds003171.
- Feeds: `AbstentionProvider` calibration. Propofol grading provides a
  ground-truth axis of "brain state reliability" against which the
  Goltermann/Huth triad and the conformal abstention rule can be
  tuned. This is where the anesthesia-bridge project's engineering
  lifts in via ADR-003.

## Data source discipline

- Every dataset in this list has been checked as accessible (either
  registered or open) as of 2026-09-03. Access status is re-verified
  in each Monday report.
- No dataset that requires industry-partnership access is included.
  NEUROSPINE is reproducible against public data.
- No PHI is present in any dataset used.
- License terms of each dataset are documented in the corresponding
  `experiments/<name>/README.md` before any data is downloaded.
