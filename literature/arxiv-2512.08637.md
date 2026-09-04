---
slug: arxiv-2512.08637
authors: [Ayhan, Nash, Vincis, Bauer, Bertram, Needham]
venue: arXiv, 2025
identifier: arXiv 2512.08637
year: 2025
projects: [tribe-neuroprint, decision-phenotype, bio-toolkit, behavioral-decoding]
gates: [G4, G9]
verdict: adjacent
aim: [A1]
---

# A Persistent Homology Pipeline for the Analysis of Neural Spike Train Data

## Mechanism (from abstract)

The authors build a topological data analysis (TDA) pipeline for spike train ensembles, using the Victor-Purpura distance metric to compute persistent homology over populations of neurons recorded in mouse insular cortex during thermal stimulation. The central finding is that population-level topological signatures discriminate oral thermal stimuli even when individual neurons carry little or no discriminative information on their own, i.e. the coding is a coordinated ensemble property rather than a single-unit property. The paper adds two theoretical supports: a stability theorem showing the topological signature is robust to the Victor-Purpura metric's timing-precision parameter, and a probabilistic stability result bounding signature reliability under trial-to-trial noise. Code and pipeline are built around mouse gustatory/thermal spike data, not fMRI or human behavior.

## Provisional relevance

Provisional: touches tribe-neuroprint and decision-phenotype because both rely on population-level neural codes for decision-relevant variables where single-unit or single-voxel signal is weak; a stability-proven TDA pipeline is a candidate replicability layer for ensemble decoding claims.
Provisional: touches bio-toolkit because the Victor-Purpura + persistent homology pipeline is a reusable method component that could sit in a shared toolkit rather than be reimplemented per project.
Provisional: informs gate G4 (specificity ablation) because the stability theorem gives a formal bound to test whether an ensemble-level topological signal survives a matched control that scrambles neuron identity while preserving marginal statistics.
Provisional: informs gate G9 (measurement reliability) because the probabilistic stability result is directly a test-retest / trial-resampling reliability bound for topological features, which NEUROSPINE decoders currently lack.
Provisional: supports NEUROSPINE aim A1 by offering an individual-scale, single-species, single-subject-type method for extracting a replicable ensemble code, the same shape of claim A1 requires but for human multimodal recordings.

## Action items

- [ ] Evaluate whether the Victor-Purpura + persistent-homology pipeline (or its stability theorem) transfers from spike trains to the continuous, denoised fMRI/EEG feature spaces used by PerceptionDecoder.
- [ ] Re-score G9 in decision-phenotype's evaluation using this paper's probabilistic stability bound as a candidate reliability metric.
