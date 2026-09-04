---
slug: meicoder-sobotka-2510-20762
authors: [Sobotka, Baroni, Antolík]
venue: NeurIPS 2025
year: 2025
identifier: arXiv:2510.20762
projects: [tribe-neuroprint, wiring-not-weights, behavioral-decoding, decision-phenotype]
gates: [G6, G8, G9]
verdict: adjacent
---

# MEIcoder: Decoding Visual Stimuli from Neural Activity

## Mechanism (from abstract)

MEIcoder decodes visual stimuli from neural population activity using neuron-specific most exciting inputs (MEIs), structural similarity index measure loss, and adversarial training. The method achieves state-of-the-art performance reconstructing visual stimuli from single-cell activity in primary visual cortex (V1), particularly excelling on small datasets with few recorded neurons. Ablation studies demonstrate that MEIs are the main performance drivers. Scaling experiments show reliable reconstruction of high-fidelity natural images from as few as 1000-2500 neurons and fewer than 1000 training data points. A unified benchmark with over 160,000 samples supports future research.

## Preliminary relevance mapping

Provisional: MEIcoder touches tribe-neuroprint because neural fingerprinting via decoding may leverage MEI extraction to identify individual-specific neural codes from sparse recordings.

Provisional: It sharpens wiring-not-weights by demonstrating that sparse, interpretable neural features (MEIs) suffice for stimulus reconstruction, suggesting identity lives in selective weight patterns rather than full connectome.

Provisional: It informs behavioral-decoding's decoder architecture; MEI-based adversarial training could improve fidelity of neural-to-observable mappings.

Provisional: MEIcoder informs G6 (mechanism/necessity) by showing MEIs are causal to performance via ablation. It informs G8 (external validity) if results generalize to other visual areas beyond V1 and to non-human primates. G9 (measurement reliability) is strengthened by ablation studies demonstrating robustness of the method.

## Action items

- [ ] Cross-reference MEI methodology with ../portfolio/tribe-neuroprint/evaluation.md for fingerprinting circuits.
- [ ] Evaluate whether MEI extraction could replace or augment current decoding schemes in behavioral-decoding.
- [ ] Check whether V1-centric results transfer to downstream visual areas (V2, IT).
