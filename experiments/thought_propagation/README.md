# thought_propagation

ADR-013: an anatomical probabilistic thought-propagation model. The
transition kernel lives on brain regions, not abstract EEG covariance
prototypes. This is the correction to the anatomy-free error.

## What it is

A stimulus-to-behavior chain rendered as a probability structure on a
real brain connectome. A stimulus seeds its sensory network (visual ->
Vis), activation propagates as a random walk on the connectome, and the
committor / mean-first-passage-time structure gives the path to the
behavioral terminus (motor -> SomMot). The dynamics math is the audited
committor / MFPT / PCCA from `dynamics.py`; only the nodes change from
prototypes to atlas regions.

## Data (all public, published)

- Schaefer 2018 atlas, 100 parcels, 7-network Yeo labels (Schaefer et
  al., Cerebral Cortex 2018; Yeo et al., J. Neurophysiol. 2011).
- Functional connectome from nilearn `development_fmri` resting-state
  (40 subjects), group-averaged correlation FC.
- Random-walk / network-diffusion propagation (Abdelnour/Voss/Raj 2014;
  Goni et al. 2014).

## Pipeline

    python experiments/thought_propagation/build_connectome.py \
        --n-subjects 40 --n-rois 100        # -> results/connectome.npz
    python experiments/thought_propagation/run.py               # analysis

## Result (2026-09-04), all three preregistered checks PASS

1. PCCA communities recover the Yeo networks: adjusted Rand index 0.154
   vs shuffle-null 95th percentile 0.024, p < 0.0001. The propagation's
   metastable communities reflect known functional organization.
2. Within-network MFPT (103.5) < between-network MFPT (105.4),
   Mann-Whitney p = 0.0037. Activation reaches same-network regions
   faster.
3. The visual-to-motor committor path interior is 100 percent
   association cortex (DorsAttn, Salience, Control, Default, Limbic):
   the path runs through the association hierarchy, not directly, as the
   known cortical processing chain does.

Stimulus-to-behavior network sequence (visual stimulus to motor), by
mean committor:

    Vis 0.000 -> Limbic 0.455 -> DorsAttn 0.482 -> Default 0.494
    -> Control 0.506 -> Salience 0.574 -> SomMot 1.000

This is "stimulus in visual field -> occipital -> association -> motor
-> reaction" as a committor gradient on the real connectome.

## Honest caveats

- ARI 0.154 is highly significant against the null but modest in
  absolute terms: the propagation communities PARTIALLY recover the Yeo
  networks, they do not reproduce them exactly.
- The committor values for the five association networks cluster near
  0.5 (0.455 to 0.574). The strong, robust claim is the three-tier
  ordering Vis (0) -> association (~0.5) -> SomMot (1). The fine
  ordering AMONG association networks is weak and should not be
  over-interpreted.
- This is a diffusion model on FUNCTIONAL connectivity, which is
  correlational. The "sequence" is a committor ordering on that graph,
  not a measured temporal cascade and not a causal claim.
- Group-level model. It says how a stimulus CLASS propagates to a
  behavior CLASS across a population connectome, not what one person is
  thinking. Individuation is a separate, settled-hard problem and is
  deliberately out of scope.

## Next

- Map more stimulus classes (auditory -> temporal, somatosensory) and
  behavior classes to their networks from Neurosynth.
- Predicted-EEG forward model (lead field) and predicted-fMRI forward
  model (HRF) projecting region activation to sensors.

## Threat-response circuit (ADR-014)

`threat_response.py` corrects the four flaws of the cortex-only v1 by
building the scary-stimulus cascade the way a research scientist would.

- Augmented atlas: Schaefer-100 cortex + Harvard-Oxford subcortex
  (amygdala, thalamus, brainstem, hippocampus, striatum). Build it with
  `build_augmented_connectome.py`.
- Directed LeDoux dual-route priors (fast Vis->Thalamus->Amygdala, slow
  Vis->ventral->Amygdala, then amygdala outputs). Imaging FC is
  symmetric and cannot provide direction.
- Exogenous effectors (autonomic, endocrine, peripheral motor) that
  receive from the brain but are NOT imaged, represented explicitly.

Result: a visual threat terminates 0.527 in behavioral motor output,
0.245 autonomic, 0.228 endocrine, ALL of which are un-imaged effectors.
Expected processing depth before output is 37 steps through imaged
regions. The fast subcortical route speeds amygdala arrival (MFPT 15.08
vs 15.73, ablation PASS). A limitation probe shows the excitatory-only
random walk cannot represent inhibitory PFC regulation (documented, next
step is signed dynamics).

This directly answers "how do you set up the response when imaging
cannot capture it all": enumerate the full system, draw the
observability boundary explicitly (115 imaged regions vs 3 un-imaged
effectors), and quantify where the response goes across it.
