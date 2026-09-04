# Synthesis: biomedical anchors (partial, tick 2)

Initial pubmed sweep after the first crawl attempt failed at rate
limit. Six papers indexed inline this tick, covering test-retest
reliability, reward, affect, dynamic decoding, and drift-diffusion
individual differences. Full pubmed synthesis (target ~30 to 60
notes covering working memory, BCI, cross-subject transfer, sample
size, and mind-reading proper) is queued in `issues_to_open.md`.

## Table 1: NEUROSPINE aim to supporting papers

| Aim | Slug | What it supplies |
| --- | --- | --- |
| A1 (individual scale replicable) | pubmed-39957839 | Freund et al. Hierarchical Bayesian + multivariate decoding hits near-maximal test-retest in PFC + parietal cortex on Stroop across months. Reference recipe for the A1 per-subject decoder wrapper. |
| A1 | pubmed-33367590 | Putkinen et al. MVPA decoding of music-evoked emotion in auditory + motor + interoceptive cortex; enables per-subject affect decoding. |
| A1 | pubmed-38970361 | Saulin et al. DDM initial-bias-plus-drift parameterization from fMRI in a social decision task. |
| A1 + A2 | pubmed-36878456 | Speer et al. Brain Reward Signature; 92 percent MID accuracy in-sample, 92 percent same-task new sample, 73 percent gambling task. |
| A1 + A2 | pubmed-34478442 | Misra et al. RNN latent-trajectory decoding of movie-watching fMRI with individual-difference IQ prediction. |
| A1 + A2 | pubmed-39126347 | Jiang et al. Hierarchical Bayesian DDM plus IS-RSA for cross-subject transfer diagnostic. |

## Table 2: NEUROSPINE gate to supporting papers

| Gate | Slug | What it supplies |
| --- | --- | --- |
| G4 specificity ablation | pubmed-33367590 | Music-vs-film stimulus contrast as a natural G4 control for AffectDecoder. |
| G4 | pubmed-36878456 | Disgust-Delay Task as the G4 specificity control for RewardDecoder. |
| G6 mechanism / necessity | pubmed-34478442 | Saliency and lesion analysis as a G6 template for PerceptionDecoder. |
| G6 | pubmed-38970361 | Reciprocity-driven condition as the G6 mechanism check for DecisionDecoder. |
| G6 | pubmed-39126347 | Drift-rate mediation as a formal G6 mechanism test. |
| G7 calibration | pubmed-39957839 | Hierarchical Bayesian trial-level fMRI as the calibration front-end. |
| G7 | pubmed-39126347 | Hierarchical Bayesian DDM as the calibration front-end for decision predictions. |
| G8 external validity | pubmed-36878456 | MID to gambling task generalization as the G8 template for RewardDecoder. |
| G8 | pubmed-34478442 | IQ prediction across subjects as the G8 template. |
| G9 measurement reliability | pubmed-39957839 | Near-maximal test-retest across months as the G9 exemplar. |
| G-fMRI.1 per-participant CV | pubmed-39957839 | Hierarchical framework is designed exactly for this. |
| G-fMRI.2 sign concordance | pubmed-36878456 | 92 percent decoding across a second sample implies strong per-subject concordance. |

## Table 3: NEUROSPINE component to biomedical external anchor

| Component | Primary biomedical anchor | Slug |
| --- | --- | --- |
| PerceptionDecoder (dynamic movie/EEG) | Learning brain dynamics via RNN | pubmed-34478442 |
| AffectDecoder (categorical emotion, MVPA) | Music-evoked emotions in auditory + motor cortex | pubmed-33367590 |
| DecisionDecoder (DDM parameterization) | Empathy prosocial DDM bias | pubmed-38970361 |
| DecisionDecoder (individual differences) | Impulsivity DDM + IS-RSA | pubmed-39126347 |
| RewardDecoder (validated across tasks) | Brain Reward Signature | pubmed-36878456 |
| CalibrationProvider (hierarchical trial-level) | Freund et al. hierarchical + multivariate | pubmed-39957839 |

## Gaps still open

The pubmed crawl this tick covered 4 of the 12 planned topic axes.
Still to run in the next tick:

- Working memory decoding (multivariate pattern analysis).
- BCI / intent decoding for thought / speech.
- Sample size and reproducibility in neuroimaging (Marek 2022 style).
- Cross-subject generalization of neural decoders (beyond RAVEN).
- Semantic / language decoding from fMRI (Huth-style).
- Memory recall decoding and hippocampal reactivation (biomedical
  side; the Nature backward-shift paper is the physics side).
- Test-retest of EEG-based decoders.
- Multimodal fusion of neural + behavioral signals.

## Attribution

According to PubMed. Notes cite DOI links per the pubmed tool's
attribution policy. See individual `pubmed-<pmid>.md` files.
