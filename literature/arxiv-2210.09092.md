---
slug: arxiv-2210.09092
authors: [Chung, Das, Ombao]
venue: arXiv, 2022 (v4 2023)
identifier: arXiv 2210.09092
year: 2022
projects: [tribe-neuroprint, cortex-of-anyone]
gates: [G2, G9]
verdict: adjacent
aim: [A2]
---

# Dynamic Topological Data Analysis of Functional Human Brain Networks

## Mechanism (from abstract)

The authors build a "dynamic-TDA" framework that computes persistent homology across a time series of brain functional-connectivity networks (rather than a single static network), and introduce a Wasserstein-distance-based inference method to statistically compare topological patterns over time or between groups. Applied to resting-state fMRI, the method successfully discriminates topological characteristics between male and female brain networks, demonstrating the framework's sensitivity to a known individual/group-level difference. A MATLAB implementation (part of the PH-STAT toolbox family by the same senior author) is released publicly.

## Provisional relevance

Provisional: touches tribe-neuroprint and cortex-of-anyone because both need a time-resolved (not static) topological summary of functional connectivity to track how an individual's brain-network topology changes across task epochs or manipulation states, which is exactly what dynamic-TDA provides.
Provisional: informs gate G2 (seed variance) because a Wasserstein-distance inference procedure gives a principled statistical test for topological differences that could be adapted to seed-variance testing (is the topological signature stable across resampled seeds/subsamples of the same subject's data).
Provisional: informs gate G9 (measurement reliability) because the male/female discrimination result is itself a test-retest-style validity check (a known, replicable group difference); NEUROSPINE's topology layer could use the same sex-difference benchmark as a positive control before trusting novel claims.
Provisional: supports NEUROSPINE aim A2 by giving a demonstrated instance of group-scale generalization of a dynamic topological signature (sex difference) with an associated statistical test, directly the shape of evidence A2 requires, though it is a demographic split rather than a thought-prediction task.

## Action items

- [ ] Prototype the Wasserstein-distance group-comparison test on NEUROSPINE's existing connectivity data using the known sex-difference result as a positive control before applying it to novel claims.
- [ ] Evaluate whether the released MATLAB PH-STAT toolbox can be wrapped into bio-toolkit rather than reimplementing dynamic-TDA from scratch.
