---
slug: dreamerv3-sparse-memory-JmjqTi4FDF
authors: Sobotka, Ijspeert, Bellegarda
venue: Interpretability Workshop
year: 2025
identifier: OpenReview JmjqTi4FDF
projects: [ism-v1, memoryprint, wiring-not-weights]
gates: [G5, G6, G7]
verdict: sharpens
---

# Reverse-Engineering Memory in DreamerV3: From Sparse Representations to Functional Circuits

## Mechanism (from abstract)

DreamerV3 relies on sparse memory representations and small internal subnetworks (circuits) to store and act on memory. The paper applies mechanistic interpretability analysis to reverse-engineer the functional components that enable DreamerV3's memory operations. This work bridges the gap between learned representations and identifiable circuit-level mechanisms, demonstrating that complex decision-making behavior emerges from structured but minimal computational motifs.

## Preliminary relevance mapping

Provisional: Sparse memory circuits in DreamerV3 are directly relevant to
NEUROSPINE's sparse_circuit_id field (field 5), which requires identifying the
minimal causal circuit that produces a decision.

Provisional: The approach may sharpen G5 (confound control) by showing how to
isolate memory circuits from unrelated model computations, and G6
(mechanism/necessity) by testing whether sparse subsets are indeed sufficient
and necessary for decision output.

## Action items

- [ ] Re-score G5 (confound control) after understanding sparse-circuit isolation
  in DreamerV3.
- [ ] Re-score G6 (mechanism/necessity) if the paper provides empirical evidence
  that sparse circuits are causally sufficient for downstream behavior.
- [ ] Cross-reference ../portfolio/wiring-not-weights/evaluation.md for
  connections to circuit-weight dissociation.
