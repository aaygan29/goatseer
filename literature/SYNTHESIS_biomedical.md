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

## Tick 4 additions (2026-09-04, round-2 pubmed)

Five more biomedical anchors covering the highest-leverage previously-
open topics.

| Slug | Anchor | Contribution |
| --- | --- | --- |
| pubmed-37127759 | Tang, LeBel, Jain, Huth 2023 Nature Neuroscience | Non-invasive continuous-language semantic decoder that transfers across perceived, imagined, and silent-video inputs. Reference PerceptionDecoder for a language-head option. Mental-privacy result: subject cooperation required to train + apply. |
| pubmed-36944488 | Deutsch et al. 2023 J. Neuroscience | Working memory contents in auditory cortex are NOT distractor-resistant. G4 specificity template for MemoryDecoder: distraction-vs-no-distraction contrast. |
| pubmed-35296861 | Marek et al. 2022 Nature | Reproducible BWAS require thousands of subjects. Draws the boundary: within-subject decoding is fine at small N; across-subject association is not. Caps A2 to within-subject-plus-fine-tuning rather than BWAS. |
| pubmed-41979953 | Cao et al. 2026 IEEE TNSRE | Hybrid covert-attention-augmented motor imagery + transformer EEG fusion. Intra-subject 89%, inter-subject 81%: concrete reference for A2 transfer-cost expectations on BCI-style paradigms. |
| pubmed-42149756 | Sung et al. 2026 IEEE TNSRE (EffortNet) | Self-supervised + incremental + transfer three-part learning stack for per-subject EEG decoders with reduced calibration data. Engineering blueprint for SubjectAdapter's low-data path. |

## Table 3 update: NEUROSPINE component to biomedical external anchor

Additions from tick 4:

| Component | Anchor | Slug |
| --- | --- | --- |
| PerceptionDecoder (language head option) | Tang et al. 2023 | pubmed-37127759 |
| MemoryDecoder (G4 specificity via distraction) | Deutsch et al. 2023 | pubmed-36944488 |
| SubjectAdapter (low-data per-subject blueprint) | Sung et al. 2026 EffortNet | pubmed-42149756 |
| SubjectAdapter (BCI-style transfer cost reference) | Cao et al. 2026 CAA-MI | pubmed-41979953 |
| Study-wide sample-size discipline | Marek et al. 2022 | pubmed-35296861 |

## Gaps still open (after tick 4)

- Multimodal EEG-fMRI fusion for decoding cognition (pubmed search
  returned zero hits with the exact query; needs a broader search
  term next tick).
- Memory recall decoding + hippocampal reactivation on the
  biomedical side (Yaghoubi Nature paper covers the temporal-shift
  physics side already).
- Cross-subject generalization beyond RAVEN + BCI-style (nothing
  strong from fMRI side yet).
- Semantic language decoding beyond Tang et al. 2023 (may not need
  more).
- Naturalistic movie / video decoding at scale.

## Attribution

According to PubMed. Notes cite DOI links per the pubmed tool's
attribution policy. See individual `pubmed-<pmid>.md` files.
