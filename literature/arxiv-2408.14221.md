---
slug: arxiv-2408.14221
authors: [Moutuou, Benali]
venue: arXiv, 2024 (v3 2025)
identifier: arXiv 2408.14221
year: 2024
projects: [wiring-not-weights, tribe-neuroprint, cortex-of-anyone]
gates: [G6, G8]
verdict: adjacent
aim: [A1]
---

# Brain Functions Emerge as Thermal Equilibrium States of the Connectome

## Mechanism (from abstract)

Using the C. elegans connectome, the authors build an algebraic quantum framework in which neural functions (perception, learning, memory, locomotion) surface as thermal-equilibrium states of a quantum system defined over the structural connectome, applying the Kubo-Martin-Schwinger (KMS) formalism from statistical mechanics. They introduce a functional connectome map and an "Integration Capacity" index that quantifies how effectively neurons coordinate information flow, and argue this connects structural (wiring) architecture to functional predictions of behavior. This is a small, fully-mapped invertebrate connectome (C. elegans), not human neuroimaging.

## Provisional relevance

Provisional: touches wiring-not-weights most directly because the paper's entire thesis, that function emerges as an equilibrium state of the structural connectome, is a formalized version of the "wiring matters" side of the identity-in-weights-vs-connectome debate this project is designed to adjudicate; it is a candidate mechanistic model to falsify or corroborate.
Provisional: touches tribe-neuroprint and cortex-of-anyone because the Integration Capacity index is a candidate structural covariate to add alongside functional-connectivity-based decoders, since it is derived from wiring rather than activity.
Provisional: informs gate G6 (mechanism and necessity) because the KMS thermal-equilibrium framework is explicitly mechanistic and falsifiable at the local level (predicts which structural edges should carry the most "temperature"/integration); an intervention removing a high-Integration-Capacity edge should degrade function, a testable necessity claim.
Provisional: informs gate G8 (external validity) because the model is validated only on C. elegans; applying it to human connectome data (even schematic, e.g. Human Connectome Project parcellations) is the missing external dataset.
Provisional: supports NEUROSPINE aim A1 by proposing a structural (not purely functional) route to individual-scale prediction, relevant if wiring-not-weights concludes connectome idiosyncrasy is load-bearing for identity.

## Action items

- [ ] Assess whether the Integration Capacity index is computable on human structural connectome data (e.g., diffusion MRI tractography) as a candidate covariate for SubjectAdapter.
- [ ] Log this paper as a mechanism candidate in wiring-not-weights's evaluation.md and design the G6 necessity intervention (remove top-Integration-Capacity edges, check functional prediction) before citing it as support.
