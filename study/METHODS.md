# Methods

Concrete methods for the NEUROSPINE study. Referenced from
`PROTOCOL.md`.

## Inputs

### Neural

- **fMRI**: BOLD signal, TR 1.0 to 2.0 s, 3T or 7T, whole-brain. NSD is
  the primary A1 dataset; BMD supplements; HCP-YA and ds003171 (propofol
  grading) for reliability characterization; ds005479 for reward.
- **EEG**: 32 to 128 channel, event-locked or continuous. DEAP for
  affect; NATVIEW for naturalistic viewing.
- **Spikes**: not required for A1 or A2; noted here so the pipeline can
  accept them later without a rewrite.

### Behavioral

- **Choice**: two-alternative or n-alternative decisions with recorded
  outcome.
- **Response time**: milliseconds from stimulus onset to response.
- **Facial expression**: FACS action units where available (DEAP, NSD
  scans do not have this).
- **Physiology**: heart rate, skin conductance, respiration where
  available.
- **Stimulus history**: what the subject has been shown in the current
  session, in order, with onset times.

## Preprocessing

- fMRIPrep v25.x for BOLD preprocessing. Fixed version pinned in
  `experiments/*/configs/`.
- ICA-AROMA for motion denoising, followed by regression of the
  standard six motion regressors and their derivatives.
- HRF deconvolution via GLMsingle for trial-level beta estimation.
- EEG: MNE-Python fixed pipeline: bandpass 0.5 to 40 Hz, ICA for eye
  and muscle removal, epoch to event window per task.
- Behavioral: cleaned response times (0.15 s < RT < 10 s), choice
  encoding standardized across tasks.

## Decoders

One decoder per predicted dimension. Each decoder is a plugin behind the
matching Protocol in `instrument/src/neurospine/providers.py`. Concrete
implementations live under `experiments/<decoder>/`.

- `PerceptionDecoder`: subject-conditional linear or MEIcoder-style
  small model, trained per subject on stimulus embeddings. Input:
  region-of-interest beta maps. Output: MEI or CLIP-space embedding of
  the presumed perceived stimulus.
- `AffectDecoder`: multimodal regressor on valence, arousal, and
  discrete emotion classes. Input: fMRI + EEG + face + physio. Output:
  a dict of continuous and categorical predictions.
- `DecisionDecoder`: fits a hierarchical drift-diffusion model whose
  drift and threshold parameters are functions of neural state. Input:
  behavioral RT + choice + concurrent neural signal. Output: DDM
  parameters and choice probability.
- `MemoryDecoder`: predicts recall probability and the temporal shift
  of encoded reward information, anchored on the Yaghoubi hippocampal
  backward-shift finding.
- `RewardDecoder`: predicts anticipation strength from NAcc BOLD and
  behavioral cues.

## Calibration and abstention

- **Calibration**: split-conformal prediction on a per-subject
  calibration split, with a 20-percent holdout for the coverage check.
  Report ECE per dimension.
- **Abstention**: fire when any of the following holds:
  - Goltermann/Huth triad fails on the fitted decoder for that
    dimension.
  - Conformal prediction interval width exceeds a preregistered
    threshold.
  - Motion or artifact rejection removes more than 20 percent of the
    trials from the input session.

## Statistical framework

- Primary tests are Spearman rank correlation (test-retest) and
  paired-subject t-tests (transfer degradation).
- Multiple-comparison correction across the five prediction dimensions:
  Benjamini and Hochberg with false discovery rate 0.05.
- Effect sizes and 95 percent CIs reported alongside every p-value.
- Bayes factors as a supplement for null results per aim.
- Seed variance: every headline number is reported across at least
  five seeds; mean and standard deviation shown.

## Robustness checks

Beyond the gate ladder:

- **Physiological confound sweep**: refit each decoder with heart rate
  and respiration regressed out; report the delta in test-retest.
- **Scanner site sweep**: for NSD (single-site) this is limited; for
  HCP-YA (multi-site) report the site random effect.
- **Time-of-day sweep**: for the two subjects in NSD and BMD with the
  most sessions, split by AM vs PM sessions and report per-slot
  performance.
- **Attention confound**: use a proxy attention measure (physiology or
  behavioral vigilance) as a covariate and check that decoders do not
  collapse to attention prediction.

## Topological analysis layer

For the individual-scale replicability side, layer a topological
analysis of the neural time series on top of the linear decoders.
Persistent homology of the point cloud in latent-decoder space provides
a signature of the subject's dynamical trajectory. Anchors from
`literature/SYNTHESIS_computational.md` topological section fill in
concrete methods (persistent homology of ROI time series, Betti curves
of latent manifolds, Reeb graphs).

The purpose of this layer is not to replace the linear decoders. It is
to provide a per-subject invariant that quantifies replicability at a
level above per-timepoint prediction: two sessions from the same
subject should have topologically similar latent trajectories even
where instantaneous predictions diverge.

## Physics anchor

Frame the individual-scale pipeline as a statistical-mechanics problem:
the subject's neural state is a point in a high-dimensional configuration
space; the decoders are order parameters. Anchors from
`literature/SYNTHESIS_computational.md` physics section fill in the
concrete framing (spin-glass-style neural population models, energy
landscapes of decision variables).

The purpose is to provide a principled reason why per-subject
calibration is necessary: different subjects live at different
locations on the same energy landscape, and a group model averages
across those locations to zero.
