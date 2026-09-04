# Synthesis: computational + physics + topology anchors

Cross-cutting synthesis of the arxiv and bioRxiv crawl (34 notes). Each
row cites the slug of the corresponding literature note. Abstracts are
in the note itself; this file is the reader map from NEUROSPINE
components to their external anchors.

## Table 1: NEUROSPINE aim to supporting papers

| Aim | Slug | What it supplies |
| --- | --- | --- |
| A1 (individual scale replicable) | biorxiv-2025-08-26-672402 | Sample size and covariate influence on normative neuroanatomical models. Bounds the sample-per-subject required for replicable individual decoders. |
| A1 | arxiv-2506.21155 | Amortized personalization in virtual brain twins. Provides an efficient per-subject calibration protocol. |
| A1 | biorxiv-2025-03-27-645646 | Trial-level RSA. Method for per-trial similarity structures that support replicable single-subject reads. |
| A1 | arxiv-2110.09006 | Survey of natural image reconstruction from fMRI. Baseline landscape for PerceptionDecoder. |
| A1 | arxiv-2509.26301 | NeuroTTT test-time training for EEG foundation models. Adaptive per-subject calibration path. |
| A2 (group scale) | arxiv-2602.02511 | Training-data governance for brain foundation models. Cross-cohort transfer discipline. |
| A2 | arxiv-2602.23410 | Brain-OF omnifunctional foundation model for fMRI/EEG/MEG. Backbone for cross-modality group transfer. |
| A2 | biorxiv-2026-04-28-721294 | Neurotransmission grounding of functional connectivity. Cross-subject invariant for transfer. |
| A3 (declared unmeasured) | biorxiv-2026-01-01-697272 | Meta-learning via altered PFC dynamics. Names a cognitive process NEUROSPINE does not attempt (adaptation is not prediction). |
| A3 | biorxiv-2024-05-06-592749 | Episodic memory supports acquiring structured task representations. Boundary between memory decoding and task-structure learning. |

## Table 2: NEUROSPINE gate to supporting papers

| Gate | Slug | What it supplies |
| --- | --- | --- |
| G4 specificity ablation | biorxiv-2025-03-27-645774 | Reward positivity does NOT encode current reward value. Prime example of the confound NEUROSPINE reward decoder must ablate. |
| G5 confound control | biorxiv-2025-08-26-672402 | Covariate distributions in normative models. |
| G6 mechanism / necessity | arxiv-2210.13461 | Active predictive coding. Falsifiable mechanistic frame for perception + planning. |
| G6 | biorxiv-2024-05-15-593712 | Synaptic pruning facilitates Bayesian model selection. Mechanism for sparsification-as-selection. |
| G7 calibration | biorxiv-2025-08-27-672728 | Learning local geometry + nonlinear topology of neural manifolds via STDP. Geometry-informed calibration. |
| G8 external validity | biorxiv-2025-08-27-672292 | Direction of motion decoding in mouse V1. Neuron-level predictive power tied to functional connectivity. Small-N cross-species validation. |
| G9 measurement reliability | biorxiv-2024-05-29-596499 | Cortex deviates from criticality during action + deep sleep. Reliability regimes for brain-state estimation. |
| G-fMRI.3 group significance | arxiv-2201.02340 | Control theory of dynamic FC reconfiguration. Energy landscape framing for group-level significance. |

## Table 3: Instrument component to external anchor

| Component | Primary anchor | Slug |
| --- | --- | --- |
| PerceptionDecoder | MEIcoder | meicoder-sobotka-2510-20762 |
| PerceptionDecoder (baseline landscape) | Deep learning fMRI reconstruction survey | arxiv-2110.09006 |
| AffectDecoder | Cognitive Dark Matter (taxonomy) | cognitive-dark-matter-mineault-2603-03414 |
| AffectDecoder (data fusion pattern) | Artists' brain multimodal fusion | biorxiv-2025-01-01-630982 |
| DecisionDecoder | Reward positivity confound paper | biorxiv-2025-03-27-645774 |
| MemoryDecoder | Hippocampal backward-shifted reward | hippocampal-backward-shifted-reward-nature-09958 |
| MemoryDecoder (subspace anchor) | Hippocampal-retrosplenial subspace communication | biorxiv-2025-12-31-697203 |
| RewardDecoder | Hippocampal backward-shifted reward | hippocampal-backward-shifted-reward-nature-09958 |
| SubjectAdapter | RAVEN weak-to-strong under shift | raven-jeon-sobotka-2510-21332 |
| SubjectAdapter (efficient per-subject) | Virtual brain twin amortization | arxiv-2506.21155 |
| CalibrationProvider | Neural manifold geometry via STDP | biorxiv-2025-08-27-672728 |
| AbstentionProvider | Goltermann/Huth/Buchel triad | goltermann-huth-buchel-elife-111743 |
| AbstentionProvider (reliability regimes) | Cortex deviates from criticality | biorxiv-2024-05-29-596499 |

## Topological analysis layer (contribution to A1 replicability)

Persistent homology of subject latent trajectories is the intended
individual-scale invariant that quantifies replicability at a level
above per-timepoint prediction. Anchors:

- `arxiv-2210.09092` Dynamic TDA of functional human brain networks.
  Baseline for dynamic persistent-homology pipelines applied to fMRI.
- `arxiv-2512.08637` Persistent homology pipeline for neural spike
  train data. Direct method for spike-train TDA if MEA data enter the
  study.
- `arxiv-2509.14634` Interpretable higher-order topological features
  across scales. Multi-scale Betti signatures for classification tasks.
- `arxiv-2406.15505` Integral Betti signature confirming hyperbolic
  geometry of brain networks. Global geometry anchor.
- `biorxiv-2025-08-27-672728` STDP as a local mechanism for learning
  the geometry of neural manifolds. Ties TDA back to biology.

## Physics anchor (contribution to individual-scale principled framing)

The framing "subjects live at different locations on the same energy
landscape" is grounded in:

- `arxiv-2408.06421` Neural networks as spin models. Statistical
  mechanics view of training dynamics.
- `arxiv-2408.14221` Brain functions as thermal equilibrium states of
  the connectome. Equilibrium-thermodynamic framing of brain-state
  prediction.
- `arxiv-2201.02340` Control theory of FC energy efficiency.
- `biorxiv-2024-05-29-596499` Cortex deviates from criticality.
  Constrains when the equilibrium framing holds and when it breaks.

## Mechanism / world-model bridge

- `arxiv-2210.13461` Active predictive coding as a unified world-model
  frame for perception and planning. Bridge between DreamerV3-style
  world models and neuroscience predictive coding.
- `dreamerv3-sparse-memory-JmjqTi4FDF` Sparse memory circuits in
  DreamerV3. Mechanism for sparse-circuit identification behind a
  prediction.
- `biorxiv-2024-05-15-593712` Synaptic pruning as Bayesian model
  selection. Complementary biological mechanism for sparsification.

## Wave-dynamics and analog computation (tick 3, 2026-09-04)

Miller, Brincat, Roy (J. Neuroscience 2026, pubmed-42618509) argue that
cognition and consciousness arise from bidirectional interactions
between neuronal spiking and rhythmic electric field activity (brain
waves). Top-down control coordinates neural populations into
low-dimensional, task-oriented dynamics; brain waves are the
mesoscale substrate for that coordination, and support analog
computation, and route multifunctional neurons into context-dependent
roles.

Concrete consequences for NEUROSPINE:

- Every fMRI-grounded predictor should be conditioned on the
  concurrent mesoscale wave state; the Goltermann/Huth triad becomes
  more informative when evaluated per wave-state bin rather than
  pooled across states.
- The `PerceptionDecoder`, `MemoryDecoder`, and `RewardDecoder`
  should treat multifunctional-neuron context switching as a first-
  class confound (G4).
- A future `brain_state` field on the `Thought` tuple is warranted
  once EEG-fMRI concurrent recordings enter the study (see
  `issues_to_open.md`).

## Neural-manifold math (tick 3, 2026-09-04)

Three math-heavy anchors that together set the theoretical bounds
NEUROSPINE decoders must respect:

- `pubmed-40502061` (Schmutz et al., bioRxiv 2025): analytically
  solvable RNN whose low-dim latent dynamics generate a high-dim
  activity manifold. Introduces Neural Cross-Encoder (NCE). Warning
  from mouse V1: grating and spontaneous activity reduce to low-dim
  latents, natural-image responses do not. The covariance eigenspectrum
  alone cannot recover latent dimensionality under nonlinearity.
- `pubmed-42599379` (O'Reilly-Shah and Selvitella, J. Comp. Neurosci.
  2026): proves via generalized synchronization plus delay-embedding
  theory (Whitney, Takens) that contracting RNNs develop internal
  manifolds embedding the sensory dynamics driving them. Hidden
  dimension depends on the intrinsic dimension of the sensory
  manifold, not the world. Prediction-separation result: prediction
  error sets the resolution below which distinct-future states are
  guaranteed to be separated in neural state space.
- `pubmed-38452763` (Manley et al., Neuron 2024): light-beads
  microscopy on up to 1 million mouse cortical neurons shows
  unbounded scaling of dimensionality with neuron number; 16 dims
  hold half the variance and correlate with behavior, but higher
  dims are fine-grained cortex-wide ensembles without immediate
  behavioral correlates.

Together these three anchors set the following working assumptions
for NEUROSPINE:

- Per-subject low-dim latents are theoretically well-founded
  (Schmutz, O'Reilly-Shah) but only up to a resolution set by the
  achieved prediction error (O'Reilly-Shah's prediction-separation
  bound).
- Reported latent dimensionality is always paired with the recording
  scale it was derived at (Manley); low-dim claims at small N do
  not automatically transfer to large N.
- Any topological analysis layer in `study/METHODS.md` inherits its
  mathematical grounding from the embedding-theorem framework of
  O'Reilly-Shah + Selvitella and from persistent-homology anchors
  already indexed (arxiv-2210.09092, arxiv-2512.08637).

## Cross-subject transfer bridge

- `raven-jeon-sobotka-2510-21332` RAVEN weak-to-strong under
  distribution shift.
- `arxiv-2602.23410` Brain-OF omnifunctional foundation model.
- `arxiv-2602.02511` Training-data governance for brain foundation
  models.
- `arxiv-2506.21155` Amortized personalization in virtual brain twins.
- `biorxiv-2025-08-26-672402` Sample size + covariate distributions in
  normative neuroanatomical models.

## Novel dataset + method notes

- `biorxiv-2026-04-28-721534` Simultaneous two-photon calcium imaging
  + auditory discrimination. Public dataset for auditory decoding.
- `biorxiv-2026-04-28-721377` Jacobian-informed VAR-LiNGAM for
  synchronous neural oscillation causal discovery. Method for causal
  connectivity that could feed the SubjectAdapter.
- `biorxiv-2026-04-28-721294` FC-to-neurotransmission linking.
  Grounds functional connectivity in receptor biology.

## Cognition-outside-scope (Cognitive Dark Matter borderline)

- `biorxiv-2026-01-01-697272` Meta-learning via PFC dynamics. Explicitly
  in the Cognitive Dark Matter "cognitive_flexibility" domain that
  NEUROSPINE does not attempt to predict.
- `biorxiv-2024-05-06-592749` Episodic memory supports acquiring
  structured task representations. On the boundary between
  MemoryDecoder in-scope and Cognitive Dark Matter
  "cognitive_flexibility".

## Gaps this scan did not close

- The pubmed side crawl failed at rate limit. `SYNTHESIS_biomedical.md`
  will land in a later tick and should cover: test-retest reliability
  of neural decoders, individual differences in brain-behavior
  mapping, decision neuroscience DDM anchors, working memory decoding,
  affect decoding.
- Biomechanics of neural systems: the arxiv scan did not surface a
  strong biomechanics anchor. Explicitly deferred; consult movement /
  proprioception literature separately if any NEUROSPINE dimension
  ever touches motor prediction.
- Direct anchor for AffectDecoder in the affect literature. Placeholder
  is the Cognitive Dark Matter taxonomy plus the data fusion pattern
  from the artists' brain paper; the pubmed scan should replace this
  with a proper affect-decoding anchor.
