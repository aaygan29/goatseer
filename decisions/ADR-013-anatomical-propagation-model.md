# ADR-013: Anatomical thought-propagation model on a real connectome

## Status

Accepted, 2026-09-04.

## Context

Through ADR-009 to ADR-012 the trajectory dynamics ran on an
ANATOMY-FREE state space: SPD covariance matrices of 5 EEG channels,
discretized into abstract prototype states. Aayush named this a
grievous error on 2026-09-04:

> I want mathematical probabilistic representations of thought patterns
> and neural chains of activation incrementally linked to behavior
> outcomes. Have a predicted EEG and a predicted fMRI and an internal
> representational model of the human brain, pull in all the neuro,
> topology, mathematical, computational, and broader architectural
> works, synthesize their results, and create a working neural
> atlas/model that can track thoughts and patterns of thinking as
> probabilistic determinations across the brain, then assign behavioral
> processing: stimulus scary to visual field -> occipital processing ->
> frontal lobe processing -> motor processing -> reaction.

The transition kernel must live on the BRAIN, not on abstract
covariance prototypes. Regions are the nodes, a real connectome is the
propagation matrix, a stimulus seeds a sensory region, and the chain
flows sensory -> association -> motor as a probabilistic path.

Also decided the same day: NEUROSPINE drops calibrated / conformal
abstention entirely (that is the honesty-layer moat of the OTHER
Neuro-AI works, not this one). See memory
`feedback_neurospine_no_abstention`.

## The synthesis (what published work this stands on)

- **Parcellation**: Schaefer et al., "Local-Global Parcellation of the
  Human Cerebral Cortex", Cerebral Cortex 2018 (100 to 1000 parcels,
  each labeled with its Yeo 7-network affiliation).
- **Functional networks**: Yeo et al., "The organization of the human
  cerebral cortex estimated by intrinsic functional connectivity",
  J. Neurophysiology 2011 (the 7 networks: Visual, Somatomotor, Dorsal
  Attention, Ventral Attention / Salience, Limbic, Frontoparietal /
  Control, Default).
- **Connectome**: functional connectivity from a real resting-state
  dataset (nilearn `development_fmri`), group-averaged.
- **Propagation dynamics**: a random walk / network-diffusion Markov
  chain on the connectome. Anchors: Abdelnour, Voss, Raj, "Network
  diffusion accurately models the relationship between structural and
  functional brain connectivity", NeuroImage 2014; Goni et al.,
  "Resting-brain functional connectivity predicted by analytic measures
  of network communication", PNAS 2014.
- **Dynamics math**: the committor, mean first passage time, and PCCA
  metastable decomposition already implemented and audited in
  `dynamics.py` (ADR-009, verified against analytic values, reviewed by
  the council in ADR-011). On a region-level chain these acquire a
  direct anatomical meaning:
  - committor(sensory, motor)[r] = probability that activation seeded
    at the sensory region reaches the motor region before returning to
    the sensory region, evaluated at region r. The high-committor ridge
    is the thought path.
  - MFPT to motor = expected number of propagation steps from any
    region to the behavioral terminus, a latency proxy.
  - PCCA(k=7) = the metastable communities of the propagation, which
    should recover the Yeo functional networks.

## Decision

Add `instrument/src/neurospine/propagation.py`:

- `connectome_to_markov(connectivity, threshold)`: turn a symmetric
  connectivity matrix into a row-stochastic region transition matrix
  (keep positive weights above threshold, zero diagonal, row-normalize).
- `activation_chain(T, source, target)`: return the committor from the
  source region set to the target region set, the MFPT to the target,
  and the ranked propagation path (regions ordered by committor along
  the sensory-to-motor gradient).
- `AtlasPropagation` dataclass holding the region transition matrix, the
  region-to-network map, and region labels, with methods for the
  stimulus-to-behavior chain.

`experiments/thought_propagation/` builds the connectome from the real
atlas + rest data and runs the analysis, with three preregistered
validation checks:

1. **PCCA communities recover the Yeo networks.** Adjusted Rand index
   or normalized mutual information between the k=7 PCCA labels and the
   Schaefer parcels' Yeo affiliations, well above the label-shuffle
   null. If the propagation communities do NOT align with the known
   functional networks, the model is not capturing real organization.
2. **Within-network MFPT < between-network MFPT.** Activation should
   reach same-network regions faster than cross-network regions.
3. **The visual-to-motor committor path passes through association
   cortex** (attention / frontoparietal), not directly, matching the
   known cortical processing hierarchy.

The stimulus-to-behavior chain (e.g. visual stimulus -> occipital ->
association -> motor -> reaction) is read off as the committor gradient
plus the metastable-community sequence from the sensory seed to the
motor terminus.

## Consequences

- The dynamics machinery is reused unchanged; only the nodes change
  from abstract prototypes to atlas regions. This is the correct home
  for committor / MFPT / PCCA.
- The model is group-level and anatomical, so it sidesteps the settled
  individuation battles (fingerprinting, encoder-as-moat) entirely.
- A predicted-EEG / predicted-fMRI forward model is a later layer: once
  the region propagation is validated, region activation can be
  projected to sensors via a lead-field (EEG) or an HRF (fMRI). Queued.

## Consequences NOT accepted

- No calibrated abstention (per the standing decision).
- We do not claim the model reads a specific person's thoughts. It is a
  group-level anatomical propagation model that tracks how a stimulus
  class propagates to a behavioral class as a probability structure.
- We do not claim the connectome is causal. Functional connectivity is
  correlational; the propagation is a diffusion model on it, which is
  the standard, published framing, not a causal claim.

## Validation result (2026-09-04): all three checks PASS

On a real Schaefer-100 connectome (40-subject group FC from
development_fmri):

1. PCCA communities recover the Yeo networks: adjusted Rand index 0.154
   vs shuffle-null 95th percentile 0.024, p < 0.0001.
2. Within-network MFPT (103.5) < between-network MFPT (105.4),
   Mann-Whitney p = 0.0037.
3. The visual-to-motor committor path interior is 100 percent
   association cortex.

Stimulus-to-behavior sequence (visual to motor): Vis 0.000 -> Limbic
0.455 -> DorsAttn 0.482 -> Default 0.494 -> Control 0.506 -> Salience
0.574 -> SomMot 1.000.

Honest caveats (see experiments/thought_propagation/README.md): ARI is
significant but modest (partial recovery); the association-network
committors cluster near 0.5 so only the three-tier Vis -> association ->
SomMot ordering is robust; it is a diffusion model on correlational FC,
not a causal or temporally-resolved cascade; group-level, not
individuation.

## Follow-ups

- Validated on the real connectome (above).
- Map stimulus classes (visual, auditory, somatosensory) to their
  sensory seed networks, and behavior classes to motor/decision
  targets, from published functional atlases (Neurosynth).
- Predicted-EEG forward model (lead field) and predicted-fMRI forward
  model (HRF) as the next layer.
