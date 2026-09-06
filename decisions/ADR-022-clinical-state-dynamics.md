# ADR-022: Clinical state-dynamics group comparison (ADHD-200)

## Status

Accepted, 2026-09-05.

## Context

The program's trajectory apparatus (`neurospine.dynamics`, ADR-009) has so
far been validated on synthetic ground truth and on healthy-population
temporal tasks (sleep staging, motor imagery). The next question is whether
it says anything about a real clinical population: does a disorder alter
the DYNAMICS of brain-state trajectories, not merely the marginal
connectivity. This must be posed as a GROUP COMPARISON with confound
control, not as a cross-subject classifier; ADHD-200 is well known in the
literature to be strongly confounded by acquisition site (7 independent
sites, different scanners/protocols) and in-scanner motion, so any group
difference that does not survive controlling for both is not
interpretable as a disorder effect.

## Decision

Add `experiments/clinical_state_dynamics/run.py`. Pipeline: Schaefer-100
regional time series (confound-regressed via `NiftiLabelsMasker`, same
pattern as `build_augmented_connectome.py`) -> per-region z-score ->
k-means (k=5) discretization -> `neurospine.dynamics.estimate_transition_matrix`
-> four dynamics summaries (`entropy_rate`, `spectral_gap`, mean dwell time,
metastable-community count via `perron_cluster_analysis`). Group comparison
ADHD vs typically-developing control on each summary, with a permutation
null (5000 permutations, labels shuffled WITHIN site) and Cohen's d.

No new module code was needed beyond the experiment's own helpers
(motion-proxy computation, OLS residualization, the permutation test,
Cohen's d), which are covered by
`instrument/tests/verification/test_clinical_state_dynamics.py`.

## Data and alignment (provenance)

ADHD-200 Consortium resting-state fMRI, `neurospine.io.fetch_adhd(n_subjects=40)`.
The phenotypic table nilearn ships for this reduced download (`site`,
`adhd`/`tdc`, `MeanFD`, ...) does not cover every functional scan returned:
matching the numeric subject id in each functional filename against the
phenotypic table's `Subject` column found phenotypic rows for only 30 of
the 40 scans. The other 10 (subject ids 0010042, 0010064, 0010128, 0021019,
0023008, 0023012, 0027011, 0027018, 0027034, 0027037) have no diagnosis,
site, or motion label in this table and are DROPPED rather than guessed.
This is reported explicitly by the run script, not silently absorbed.

## Confound control (mandatory)

`MeanFD` (mean framewise displacement) ships directly in the ADHD-200
phenotypic table; no derivation from raw confound files was needed. Two
controls are implemented (`--confound-control`):

- `residualize` (default, reported below): every dynamics summary is
  OLS-residualized on site dummies + `MeanFD` across the full analyzed
  sample, and the ADHD-control comparison + permutation null run on the
  residual. The permutation null shuffles diagnosis WITHIN site.
- `single-site`: restrict to the single largest site (KKI, n=8) to remove
  the site confound by construction.

## Result

`python3 experiments/clinical_state_dynamics/run.py --n-subjects 40 --n-states 5 --confound-control residualize --n-perm 5000`

**Sample**: N = 30 analyzed (13 ADHD, 17 control). Site distribution: KKI 8,
OHSU 6, Peking_2 4, NYU 4, NeuroImage 4, Peking_1 3, Peking_3 1 (7 sites,
none dominant). Mean FD by group: ADHD 0.0648, control 0.0756 (ADHD group
is NOT the more-motion group here, contrary to the usual worry direction;
still controlled for).

**Dynamics comparison (site + motion residualized, permutation p from 5000
within-site-shuffled permutations)**:

| summary | ADHD mean (raw) | control mean (raw) | Cohen's d (residualized) | permutation p |
|---|---|---|---|---|
| entropy rate | 1.188 | 1.224 | -0.44 | 0.271 |
| spectral gap | 0.446 | 0.442 | -0.12 | 0.772 |
| mean dwell time | 2.172 | 2.159 | +0.45 | 0.219 |
| metastable communities | 2.15 | 2.47 | -0.05 | 0.818 |

Under the `single-site` control (KKI only, n=8: 4 ADHD, 4 control) the same
four summaries show similarly small, non-significant differences
(|d| <= 0.38, p >= 0.58 for all four; entropy rate d=-0.38 p=0.575, spectral
gap d=-0.04 p=0.915, dwell time d=0.31 p=0.665, communities d=-0.21 p=1.0).

**Honest reading: null.** No dynamics summary shows a group difference that
survives confound control, under either control strategy. Effect sizes are
small to moderate (|d| up to 0.45) but none approaches significance at
N=30 (or N=8 for the single-site check), and the direction is not
consistent enough across summaries to suggest a suppressed real effect
(entropy rate points one way, dwell time the opposite way, as expected
since the two are related but not redundant). This is the correct, honest
outcome for a hard, small, multi-site, confounded dataset: it does not
support a claim that ADHD alters resting-state trajectory dynamics as
captured by this pipeline, and it is NOT evidence against such an effect
either (the study is underpowered at N=30 for an effect of this plausible
size; a d=0.45 effect needs roughly n=80/arm for 80% power at alpha=0.05).

## External anchors

- ADHD-200 Consortium (2012), "The ADHD-200 Consortium: A Model to Advance
  the Translational Potential of Neuroimaging in Clinical Neuroscience."
- Power et al. (2012), NeuroImage, on motion as a systematic confound in
  functional connectivity, the standard justification for mandatory motion
  control on this dataset.
- Deuflhard and Weber (2005) for PCCA, Prinz et al. (2011) for the MSM
  discipline already anchoring `neurospine.dynamics` (ADR-009).

## Honest limitations

- N=30 after the phenotypic-alignment drop is small for a multi-site,
  heterogeneous clinical dataset; the null result here is informative but
  not definitive, and is explicitly reported as underpowered rather than
  as evidence of no effect.
- k=5 discretization states and a single k-means seed were used; a
  state-count sweep and multi-seed stability check were not run for this
  first pass (see Consequences).
- The 10 functional scans with no phenotypic match were dropped, not
  imputed; this shrinks N further and is disclosed rather than patched
  over.
- This is a group comparison of dynamics summaries. It does NOT support,
  and is not framed as, a cross-subject ADHD classifier.

## Consequences

- The trajectory apparatus now has one clinical-population data point:
  under confound control, ADHD-200 resting-state dynamics summaries show
  no detectable group difference at N=30. Future work extending N (all
  ADHD-200 sites, not just the 40-subject reduced download) or sweeping
  the discretization state count would be the natural next step before
  drawing a stronger conclusion either way.
