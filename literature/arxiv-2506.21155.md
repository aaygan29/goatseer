---
slug: arxiv-2506.21155
authors: [Baldy, Woodman, Jirsa]
venue: arXiv, 2025 (ICANN 2025)
identifier: arXiv 2506.21155
year: 2025
projects: [cortex-of-anyone, wiring-not-weights, warden]
gates: [G1, G11]
verdict: sharpens
aim: [A1]
---

# Amortizing Personalization in Virtual Brain Twins

## Mechanism (from abstract)

The paper introduces "anonymized personalization" for constructing personalized virtual/digital brain models (a "virtual brain twin"), addressing two constraints simultaneously: infrastructure cost and privacy. The method allows the expensive training/fitting stage to be performed without exposure to identifiable personal data, while inference remains both tailored to the individual and computationally lightweight, i.e. personalization is amortized across a population-level model and only the final adaptation step touches the individual's private data. Code is released; the paper's stated contribution is feasibility and discussion of implications for experimental and computational neuroscience, not a full clinical validation.

## Provisional relevance

Provisional: touches cortex-of-anyone directly because "amortized personalization" is precisely the enrollment mechanism the project's Layer 1 (few-shot fMRI enrollment) needs: a population-pretrained model that adapts cheaply to a new individual without requiring the individual's raw data to leave a protected pipeline.
Provisional: touches wiring-not-weights because a virtual brain twin is parameterized in terms of personalized structural/dynamical parameters, offering a concrete testbed for the identity-in-weights-vs-wiring ablation ladder: does the personalization live in the twin's connectivity parameters or its dynamic (weight-like) parameters.
Provisional: touches warden because the anonymized-training design pattern is a direct, reusable answer to the privacy concerns raised in the Training Data Governance paper (arXiv 2602.02511), giving WARDEN's cognitive-security framing a concrete privacy-preserving enrollment mechanism to point to.
Provisional: informs gate G1 (provenance/leakage) because the anonymization method's core claim needs auditing: what exactly is anonymized during training, and does any leakage path remain between the population model and identifiable individual data.
Provisional: informs gate G11 (ethics and safety) because this is one of the few papers found that engineers a privacy-preserving personalization pipeline rather than merely discussing the problem, giving NEUROSPINE a concrete mechanism to adopt or benchmark against for its own consented-data individual modeling.
Provisional: supports NEUROSPINE aim A1 by directly targeting individual-scale, replicable modeling from limited per-subject data (few-shot enrollment via amortized personalization), the same evidentiary shape A1 requires.

## Action items

- [ ] Read the released code to verify what "anonymized" means operationally in this pipeline, and check it against G11's PHI/consent requirements before treating it as a solved problem.
- [ ] Prototype amortized personalization as the enrollment mechanism for cortex-of-anyone's Layer 1 and report few-shot sample-size requirements against the current enrollment baseline.
