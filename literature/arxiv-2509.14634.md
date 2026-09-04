---
slug: arxiv-2509.14634
authors: [Zhao, Li, Wang, Wang, Zhou, Yan, Qi]
venue: arXiv, 2025
identifier: arXiv 2509.14634
year: 2025
projects: [tribe-neuroprint, anesthesia-bridge, cortex-of-anyone]
gates: [G4, G8]
verdict: adjacent
aim: [A2]
---

# Extracting Interpretable Higher-Order Topological Features Across Multiple Scales for Alzheimer's Disease Classification

## Mechanism (from abstract)

The authors apply persistent homology to fMRI-derived functional connectivity matrices to extract higher-order topological features (cycles, cavities) across multiple scales, then use these as classifier inputs for Alzheimer's disease (AD) diagnosis. Four quantitative techniques are introduced to capture multiscale geometric variation in the functional networks. The headline empirical finding is that the number of topological cycles/cavities significantly decreases in AD patients, and the brain regions implicated by these cycle/cavity changes align with regions already established in the AD literature, which the authors treat as a sanity check on interpretability. The method outperforms baseline classifiers in their reported comparisons, with ablations to confirm each topological feature's contribution.

## Provisional relevance

Provisional: touches tribe-neuroprint and cortex-of-anyone because both need group-level, interpretable topological summaries of fMRI functional connectivity that can be defended against a domain-knowledge sanity check (matching known regions), which is the same bar this paper sets for itself.
Provisional: touches anesthesia-bridge because a topological-cycle metric is a candidate additional dimension for the LZc/sigma/VNE/Phi* battery, since cycle-count is sensitive to network integration/segregation changes analogous to anesthesia-induced connectivity collapse.
Provisional: informs gate G4 (specificity ablation) because the paper's own ablation study of which topological feature contributes to classification is a template for a matched-control ablation in NEUROSPINE's TDA layer.
Provisional: informs gate G8 (external validity) because a disease-classification topological signature is a plausible second dataset/second task to test whether NEUROSPINE's topology layer generalizes beyond its primary cohort.
Provisional: supports NEUROSPINE aim A2 by demonstrating group-scale generalization of a topological biomarker across patients with a quantified degradation-style comparison (AD vs. controls), though this is diagnostic classification, not group-scale thought prediction, so the transfer is partial.

## Action items

- [ ] Assess whether cycle/cavity counts from persistent homology add signal beyond the existing graph-theoretic metrics already planned for the topology layer, before adding a fifth analysis pipeline.
- [ ] Re-score G8 in anesthesia-bridge's evaluation.md once a topological cycle-count metric is prototyped on the propofol dataset (ds003171).
