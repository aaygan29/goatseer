# Literature map

Maps every load-bearing external citation in the study to the
NEUROSPINE component it supports. Detail per paper is in
`literature/<slug>.md`; cross-cutting synthesis is in
`literature/SYNTHESIS_computational.md` (biomedical synthesis pending
after pubmed scan retry).

## By study component

| Component | Primary external anchor | Slug |
| --- | --- | --- |
| Instrument contract shape | ADR-004 (repo-internal) | decisions/ADR-004 |
| Gate ladder v0 | Council-review skill (repo-internal) | gates/gate-ladder-v0.md |
| fMRI reliability triad | Goltermann, Huth, Buchel 2025 eLife | goltermann-huth-buchel-elife-111743 |
| PerceptionDecoder | Sobotka et al. 2025 arXiv 2510.20762 | meicoder-sobotka-2510-20762 |
| PerceptionDecoder baseline landscape | Deep learning fMRI reconstruction survey | arxiv-2110.09006 |
| AffectDecoder taxonomy | Mineault, Griffiths, Escola 2026 (Cognitive Dark Matter) | cognitive-dark-matter-mineault-2603-03414 |
| DecisionDecoder confound anchor | Reward positivity does not encode current reward value | biorxiv-2025-03-27-645774 |
| MemoryDecoder temporal anchor | Yaghoubi et al. 2026 Nature (backward-shifted reward) | hippocampal-backward-shifted-reward-nature-09958 |
| RewardDecoder temporal anchor | Same as MemoryDecoder | hippocampal-backward-shifted-reward-nature-09958 |
| SubjectAdapter cross-subject shift | Jeon, Sobotka, Choi, Brbic (RAVEN) | raven-jeon-sobotka-2510-21332 |
| SubjectAdapter amortization | Amortizing personalization in virtual brain twins | arxiv-2506.21155 |
| CalibrationProvider theory | Vovk et al. 2005; Angelopoulos and Bates 2021 | (to be added to references.bib) |
| AbstentionProvider theory | El-Yaniv and Wiener 2010 | (to be added to references.bib) |
| Sparse-circuit mechanism | DreamerV3 sparse memory circuits | dreamerv3-sparse-memory-JmjqTi4FDF |
| Topological analysis layer | Persistent homology pipeline for neural spike train data | arxiv-2512.08637 |
| Topological anchor (dynamic fMRI) | Dynamic TDA of functional human brain networks | arxiv-2210.09092 |
| Physics anchor (statistical mechanics) | Neural networks as spin models | arxiv-2408.06421 |
| Physics anchor (equilibrium thermodynamics) | Brain functions as thermal equilibrium states | arxiv-2408.14221 |

## By NEUROSPINE aim

| Aim | Load-bearing anchors |
| --- | --- |
| A1 individual scale replicability | MEIcoder, virtual brain twin amortization, trial-level RSA, NSD + BMD data, Goltermann/Huth triad |
| A2 group scale transfer | RAVEN, Brain-OF, neurotransmission-grounded FC, HCP-YA data |
| A3 declared unmeasured | Cognitive Dark Matter taxonomy, meta-learning via PFC dynamics (boundary example) |

## By hard rule

| Rule | Anchor | Slug |
| --- | --- | --- |
| Goltermann/Huth triad required for fMRI | Goltermann/Huth/Buchel 2025 | goltermann-huth-buchel-elife-111743 |
| External-citation doctrine | ADR-002 (repo-internal) | decisions/ADR-002 |
| Extraction re-verification | ADR-003 (repo-internal) | decisions/ADR-003 |

## Biomedical anchors added tick 2 (partial pubmed pass, 2026-09-04)

See `../literature/SYNTHESIS_biomedical.md` for the full table.

| Component | Biomedical anchor | Slug |
| --- | --- | --- |
| CalibrationProvider (hierarchical trial-level) | Freund et al. 2025 | pubmed-39957839 |
| RewardDecoder (validated cross-task) | Speer et al. Brain Reward Signature 2023 | pubmed-36878456 |
| AffectDecoder (MVPA categorical) | Putkinen et al. 2021 | pubmed-33367590 |
| PerceptionDecoder (RNN dynamic) | Misra et al. 2021 | pubmed-34478442 |
| DecisionDecoder (DDM parameterization) | Saulin et al. 2024 | pubmed-38970361 |
| DecisionDecoder (IS-RSA individual differences) | Jiang et al. 2024 | pubmed-39126347 |

## Textbook / seminal entries added to references.bib (tick 2, 2026-09-04)

- Vovk, Gammerman, Shafer 2005 (conformal prediction textbook).
- Angelopoulos and Bates 2021 (conformal prediction tutorial).
- El-Yaniv and Wiener 2010 (selective classification foundations).
- Ratcliff 1978 (DDM foundational).

## Mathematical / computational-neuroscience anchors (tick 3, 2026-09-04)

Directly added by Aayush's request for strongly math-based computational
neuroscience literature. Full notes under `../literature/`.

| Component / concern | Anchor | Slug |
| --- | --- | --- |
| Analog wave computation (top-down control, mesoscale modulation) | Miller, Brincat, Roy 2026 | pubmed-42618509 |
| Low-dim latents from high-dim activity (solvable RNN model, NCE) | Schmutz et al. 2025 | pubmed-40502061 |
| Embedding-theorem bounds on internal manifold dimension | O'Reilly-Shah + Selvitella 2026 | pubmed-42599379 |
| Unbounded dimensionality scaling with neuron count | Manley et al. 2024 | pubmed-38452763 |

These sit on the physics + math side and inform gates G6 (mechanism),
G8 (external validity across recording scales), G12 (dimensionality
claims paired with recording scale).

## Gaps still open

- Working memory decoding anchor.
- BCI / intent decoding (thought / speech).
- Sample size and reproducibility in neuroimaging (Marek 2022 style).
- Semantic / language decoding from fMRI (Huth-style).
- Cross-subject transfer beyond RAVEN.
- EEG-based decoder test-retest.
- Multimodal neural + behavioral fusion.
- Biomechanics of neural systems: explicitly deferred until any
  NEUROSPINE dimension touches motor prediction.
