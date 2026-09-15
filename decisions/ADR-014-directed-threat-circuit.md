# ADR-014: Directed threat circuit with subcortical hubs and exogenous effectors

## Status

Accepted, 2026-09-04.

## Context

ADR-013 built a propagation model on a cortical connectome. Aayush's
critique on 2026-09-04 exposed that this is scientifically insufficient
for a real stimulus response:

> There's so many other potential activations that would occur due to
> the scary stimulus and not all of them can be captured via brain
> imagery, so how would you actually set this kind of response up in the
> first place? Do not do the exact thing I ask right away: analyze it,
> figure out the most scientifically rigorous way, using the mind of a
> research scientist.

A threat response is a parallel, multi-system cascade, and most of it is
not in a cortical fMRI parcellation. Four flaws in the ADR-013 model:

1. **Cortex-only atlas omits the threat circuit.** The amygdala,
   thalamus (pulvinar relay), and brainstem, the actual threat hubs,
   are subcortical and absent from Schaefer-100.
2. **Resting-state FC is symmetric and correlational.** It cannot
   provide the directed feedforward-then-feedback routing a threat
   drives.
3. **A single absorbing random walk is the wrong dynamics.** The real
   response has a fast subcortical shortcut plus a slow cortical route
   converging on the amygdala, then parallel branching to effectors.
4. **Not everything is imageable.** Autonomic (heart rate, skin
   conductance), endocrine (cortisol), and peripheral motor output are
   not on any fMRI graph. Faking them into the FC would be the
   construct-not-measured error the failure archaeology warns against.

## Decision

Add `instrument/src/neurospine/circuit.py`: a `DirectedCircuit` that
combines three sources while keeping their epistemic status distinct.

1. **Measured FC** (symmetric, from imaging), now over an AUGMENTED
   cortico-subcortical atlas (Schaefer-100 cortex + Harvard-Oxford
   subcortical: amygdala, thalamus, brainstem, hippocampus, striatum).
2. **Directed anatomical priors** (`DirectedEdge`): the LeDoux dual-route
   threat circuit as directed edges imaging cannot provide. Fast route
   Vis -> Thalamus -> Amygdala; slow route Vis -> ventral/temporal ->
   Amygdala; amygdala outputs to brainstem (PAG motor), control cortex
   (appraisal), hippocampus (context).
3. **Exogenous effectors** (`ExogenousEffector`): autonomic, endocrine,
   peripheral-motor output nodes that receive from the brain but are NOT
   imaged, marked `imaged=False`, represented explicitly instead of
   faked into the FC.

New absorbing-chain primitives in `dynamics.py`:
`absorption_probabilities` (where the response terminates) and
`expected_steps_to_absorption` (processing depth before output). Both
verified against analytically-known chains.

The observability boundary is a first-class structural property: the
model reports how many nodes are imaged regions versus un-imaged
effectors, and where a stimulus terminates across the effectors. That
accounting IS the answer to "how do you set this up when imaging cannot
capture it all": you enumerate the full system, draw the boundary
explicitly, and quantify what falls outside it.

## Result (2026-09-04)

Augmented atlas: 100 cortical + 15 subcortical regions + 3 exogenous
effectors. Visual threat seeded at the Vis network (17 parcels).

**Where a visual threat terminates (absorption from the Vis seed):**

| effector (all un-imaged) | probability |
| --- | --- |
| MotorOutput (behavioral reaction) | 0.527 |
| Autonomic (heart rate, skin conductance) | 0.245 |
| Endocrine (cortisol) | 0.228 |

The entire terminal readout of the modeled threat response is in
un-imaged effector systems. Expected processing depth before output:
37 steps through imaged regions. This is the quantitative form of the
user's point: the response is real and its endpoint is measurable
(behavior, autonomic, endocrine), but none of the endpoints are in the
brain image.

**Ablation 1 (fast subcortical route), PASS:** removing the
Vis -> Thalamus -> Amygdala shortcut slows amygdala arrival (MFPT
15.08 with the shortcut vs 15.73 without). The subcortical low road
speeds threat detection, as LeDoux's model predicts. The effect is
small because the random walk explores many paths; the direction is
correct.

**Limitation probe (PFC regulation):** adding a Cont -> Amygdala edge
INCREASES rather than decreases effector drive (0.473 vs 0.369). A
non-negative random walk is excitatory-only and structurally cannot
represent inhibitory top-down regulation. Modeling PFC downregulation
requires SIGNED dynamics (a linear dynamical system with negative
weights), which is the documented next step. This is reported as a real
model boundary, not forced to pass.

## Consequences

- The dynamics primitives are reused; only absorption math is added.
- The model is anatomically grounded, directed, and honest about the
  observability boundary.
- It stays group-level (no individuation) and has no calibrated
  abstention (per the standing decision).

## Consequences NOT accepted

- The directed priors are anatomical literature edges, not estimated
  effective connectivity. A DCM or Granger estimate on a real threat
  task would upgrade them; that is a data-collection step.
- The excitatory-only limitation is real: inhibitory regulation is not
  representable here. Signed linear dynamics is the next model.
- No claim that this reads a specific person's fear. It is a group-level
  probabilistic propagation model of how a stimulus CLASS drives a
  response across imaged and un-imaged systems.

## External anchors

- LeDoux, "The Emotional Brain" (1996) and "Emotion circuits in the
  brain" (Annu. Rev. Neurosci. 2000): the dual-route threat circuit.
- Pessoa and Adolphs, "Emotion processing and the amygdala: from a low
  road to many roads" (Nat. Rev. Neurosci. 2010): the subcortical route.
- Makris et al. 2006 / Frazier et al. 2005 / Desikan et al. 2006:
  Harvard-Oxford subcortical atlas.
- Abdelnour, Voss, Raj 2014; Goni et al. 2014: network-diffusion
  propagation.

## Follow-ups

- Signed linear-dynamical-system variant to represent inhibitory
  regulation (the ablation-2 limitation).
- Effective-connectivity priors from a real threat-task dataset.
- More stimulus classes (auditory -> temporal, pain -> insula) and their
  effector profiles.
