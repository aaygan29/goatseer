# ADR-020: Multi-source data integration hub

## Status

Accepted, 2026-09-05.

## Context

New data cannot be collected for this program, so robustness has to come from
integrating as many public sources as possible through one adapter layer.
`neurospine.io` already fetched EEG-BCI, development_fmri, LEMON, and the
Schaefer/Harvard-Oxford atlases; ADR-019 added Sleep-EDF. A dataset-scouting
agent then verified fetch paths for a decision-making dataset and several
clinical (disordered-population) datasets, to serve two program directions:
the decision-making trajectory experiment (ADR-018) and validity-hardening on
clinical populations.

## Decision

Grow `neurospine.io` into the single provenance-and-fetch hub for every data
source the program uses, and register the verified new sources with their
exact fetch recipes:

- **`adhd200`** (clinical resting fMRI, ADHD vs controls) via
  `neurospine.io.fetch_adhd` (nilearn, verified working). Phenotypic labels
  plus the site/motion covariates a group analysis must control for.
- **`ds002739`** (perceptual-decision EEG+fMRI, trial choice/RT/confidence)
  via `openneuro-py`, the target for the decision-making trajectory
  experiment: within-trial evidence accumulation is a genuinely temporal
  contrast, unlike motor imagery.
- **`ds003478`** (clinical resting EEG, depressed vs control) via
  `openneuro-py` + the existing `load_bids_eeg` adapter.

All sit in `DATASETS` (mirrored in `data/README.md`) with modality, role,
license, fetch method, and status, so a new source is a registry entry plus a
fetcher, not a rewrite.

## Guardrails (carried from the failure-archaeology culture)

- **Clinical datasets are confounded.** ADHD-200 is driven by site and
  motion; any ADHD-vs-control claim must control for both (single-site
  subsets, motion regression, matched age), or it is a site/motion classifier
  wearing a clinical label. Register the data now; do not ship a clinical
  claim without those controls.
- **Verify before building.** The scout flagged that some OpenNeuro pages did
  not render for a direct read and that `ds000115` event files are unreliable;
  inspect `events.tsv` / `participants.tsv` and confirm the live accession
  before committing compute to any OpenNeuro set.
- **Match the analysis to the modality.** Decision-making (temporal) is the
  right next target for the `sequence_decode` trajectory apparatus; clinical
  resting data is a different question (does a disorder alter state
  dynamics), and should be posed as a group comparison with a permutation
  null and confound control, not a cross-subject classifier.

## Next builds (gated on heavy downloads + rigor, not started here)

1. **Decision-making trajectory experiment** on `ds002739`: does the
   within-trial state SEQUENCE predict the choice better than a memoryless
   decoder (the ADR-019 transition-gain test)? This is the direct
   continuation of the validated sleep result.
2. **Clinical state-dynamics comparison** on `adhd200` (and later `ds003478`):
   do brain-state transition dynamics (entropy rate, dwell time,
   metastability) differ by group, controlling for site and motion? This is
   the novel clinical question the trajectory apparatus is suited to, and the
   validity-hardening the multi-source hub enables.

## Consequences

- The io hub now spans EEG-BCI, movie fMRI, resting EEG, sleep EEG, clinical
  fMRI, clinical EEG, decision EEG+fMRI, and atlases: eight sources across two
  modalities and healthy plus clinical populations.
- Both next builds are unblocked and scoped; each needs a large download and
  careful confound control, so they are separate tiers, not rushed here.
