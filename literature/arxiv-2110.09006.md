---
slug: arxiv-2110.09006
authors: [Rakhimberdina, Jodelet, Liu, Murata]
venue: arXiv, 2021
identifier: arXiv 2110.09006
year: 2021
projects: [tribe-neuroprint, bio-toolkit]
gates: [G8]
verdict: adjacent
aim: [A1]
---

# Natural Image Reconstruction from fMRI using Deep Learning: A Survey

## Mechanism (from abstract)

A survey of deep-learning approaches to reconstructing natural images perceived by a subject from their fMRI activity. The authors compare architectural design choices, benchmark datasets, and evaluation metrics used across the field, and assess comparative performance of the surveyed methods, concluding with strengths, limitations, and future directions for the fMRI-to-image reconstruction line of work. As a survey, it contributes no new empirical result but consolidates the field's benchmarks and evaluation practice as of 2021.

## Provisional relevance

Provisional: touches tribe-neuroprint and bio-toolkit because PerceptionDecoder's fMRI-based perception-reconstruction component sits in exactly this literature; the survey's benchmark-dataset and evaluation-metric inventory is directly reusable for choosing what NEUROSPINE should be evaluated against.
Provisional: informs gate G8 (external validity) because the survey's cross-paper performance comparison table is itself evidence of how much fMRI-to-image decoders currently degrade across datasets and subjects, a baseline against which NEUROSPINE's own cross-subject degradation numbers (A2) should be compared.
Provisional: supports NEUROSPINE aim A1 by cataloguing which evaluation metrics and datasets the field treats as evidence of individual-scale replicable perceptual decoding, informing what PerceptionDecoder needs to report to be taken seriously by this literature.

## Action items

- [ ] Extract the survey's benchmark dataset and metric list and cross-check it against what tribe-neuroprint's PerceptionDecoder currently reports, to identify missing standard metrics.
- [ ] Because this survey is from 2021, commission a follow-up scan restricted to 2024-2026 for updated performance numbers before citing any "state of the art" claim from it.
