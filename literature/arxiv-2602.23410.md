---
slug: arxiv-2602.23410
authors: [Guo, Bi, Abdellatif, Galbenus, Shah, Morrison, Dammers]
venue: arXiv, 2026
identifier: arXiv 2602.23410
year: 2026
projects: [tribe-neuroprint, cortex-of-anyone, bio-toolkit]
gates: [G1, G8]
verdict: sharpens
aim: [A2]
---

# Brain-OF: An Omnifunctional Foundation Model for fMRI, EEG and MEG

## Mechanism (from abstract)

Brain-OF is a unified foundation model trained jointly across fMRI, EEG, and MEG, addressing the core obstacle that these modalities differ in spatiotemporal resolution and semantic content. The architecture introduces an "Any-Resolution Neural Signal Sampler" that projects heterogeneous brain signals into a shared semantic space, plus a mixture-of-experts-style routing mechanism with shared experts for universal cross-modality patterns and routed experts for modality-specific characteristics. Pretraining uses "Masked Temporal-Frequency Modeling," reconstructing signals jointly in time and frequency domains, across roughly 40 datasets. The paper reports improved performance on multiple downstream neuroscience tasks attributed to the joint multimodal, dual-domain pretraining.

## Provisional relevance

Provisional: touches tribe-neuroprint and cortex-of-anyone directly because a pretrained, multi-modality (fMRI+EEG+MEG) encoder is a candidate shared backbone underneath PerceptionDecoder, AffectDecoder, and MemoryDecoder, potentially replacing bespoke per-modality encoders.
Provisional: touches bio-toolkit as a candidate pretrained-model dependency, since adopting Brain-OF (if weights are released) would change the toolkit's build vs. buy calculus for encoders.
Provisional: informs gate G1 (provenance and leakage) because pretraining across ~40 datasets creates substantial risk that any NEUROSPINE evaluation dataset overlaps with Brain-OF's pretraining corpus; this must be checked before using Brain-OF features on any held-out NEUROSPINE test set.
Provisional: informs gate G8 (external validity) because the model's own claim rests on cross-dataset, cross-modality generalization, which is the same evidence class A2 requires, but the paper's downstream task list and datasets need to be checked against NEUROSPINE's own held-out sets for independence.
Provisional: supports NEUROSPINE aim A2 by being architecturally aimed at exactly the cross-subject, cross-modality generalization problem A2 is trying to quantify, making it either a strong baseline to beat or a component to adopt.

## Action items

- [ ] Check whether Brain-OF's ~40 pretraining datasets overlap with any dataset NEUROSPINE plans to use for evaluation (G1 leakage check) before adopting it as a backbone.
- [ ] If weights/code become available, benchmark Brain-OF features against NEUROSPINE's current per-modality encoders on a shared held-out task, re-scoring G8.
