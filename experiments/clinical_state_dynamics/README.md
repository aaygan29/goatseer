# clinical_state_dynamics

**Claim**: ADHD alters the DYNAMICS of resting-state brain-state trajectories
relative to typically-developing controls, tested as a group comparison on
dynamics summaries with mandatory confound control for site and motion. This
is a group-level dynamics comparison, NOT a cross-subject ADHD classifier.

**Hypothesis**: If ADHD involves altered large-scale network switching
(consistent with the broader resting-state ADHD literature on default-mode
and executive-network instability), the ADHD group should show a detectable
shift in entropy rate, spectral gap, mean dwell time, or metastable-community
count of the discretized state trajectory, beyond what site and motion alone
predict.

**Gates**: G1 (provenance: public ADHD-200 data via nilearn), G8/G6
(confound control: site + motion are mandatory covariates, not optional),
G4 (permutation null on every group comparison).

## Data

ADHD-200 Consortium resting-state fMRI (ADHD-200 Consortium, 2012),
`neurospine.io.fetch_adhd`, `n_subjects=40`. Phenotypic table carries
diagnosis (`DX`), acquisition site (`Site`), and motion is computed directly
from each subject's confound file as mean framewise displacement (Power et
al. 2012 convention: sum of absolute frame-to-frame translation/rotation,
rotations converted to arc length at a 50mm head radius).

## Pipeline

1. Schaefer-100 regional time series (`NiftiLabelsMasker`, 7 Yeo networks),
   confound regression using the subject's own confound file, same masker
   pattern as `experiments/thought_propagation/build_augmented_connectome.py`.
2. Per-region z-score standardization across time, k-means (k=5 states by
   default) into a discrete state sequence.
3. `neurospine.dynamics`: `estimate_transition_matrix`, `entropy_rate`,
   `spectral_gap`, mean dwell time (`1 / (1 - mean diagonal)`), metastable
   -community count via `perron_cluster_analysis`.
4. Group comparison (ADHD vs control) per summary, permutation null (label
   shuffled within site, 5000 permutations), Cohen's d effect size.

## Confound control (mandatory, not optional)

ADHD-200 is strongly confounded by acquisition site (different scanners,
protocols, populations) and in-scanner motion (higher in ADHD by
construction of the disorder). Two controls are implemented; the default
run uses `residualize`:

- `--confound-control residualize` (default): each dynamics summary is
  OLS-residualized on site dummies + mean FD across the full analyzed
  sample, and the group comparison + permutation null are run on the
  RESIDUAL. The permutation shuffles diagnosis WITHIN site so the null
  preserves the site/group correlation structure.
- `--confound-control single-site`: restrict to the single largest site,
  removing the site confound by construction (motion is still reported,
  not adjusted, since within-site N is small).

Which control was used for the reported run, group Ns, site distribution,
and motion-by-group are always printed BEFORE the dynamics comparison and
written into `results/clinical_state_dynamics.json`.

## Run

```
cd instrument && python3 -m pytest -q   # verification suite first
python3 experiments/clinical_state_dynamics/run.py \
    --n-subjects 40 --n-states 5 --confound-control residualize
```

Outputs: `results/subject_summaries.csv` (per-subject raw summaries +
covariates) and `results/clinical_state_dynamics.json` (group Ns, site
distribution, motion by group, confound control used, per-metric effect
size and permutation p-value).

## External anchors

- ADHD-200 Consortium, "The ADHD-200 Consortium: A Model to Advance the
  Translational Potential of Neuroimaging in Clinical Neuroscience" (2012).
- Power et al., "Spurious but systematic correlations in functional
  connectivity MRI networks arise from subject motion" (NeuroImage, 2012),
  for the framewise-displacement motion convention and the site/motion
  confound concern that makes control mandatory here.
- Deuflhard and Weber (2005) for PCCA, Prinz et al. (2011) for the MSM
  discipline behind `neurospine.dynamics` (already anchors of ADR-009).

## Honest result

See `decisions/ADR-022-clinical-state-dynamics.md` for the reported group
Ns, site distribution, motion-by-group, and the permutation result on each
dynamics summary, including nulls. A weak or null group difference AFTER
confound control is the correct, informative outcome on this dataset; it is
not evidence for an ADHD classifier and none is claimed here.
