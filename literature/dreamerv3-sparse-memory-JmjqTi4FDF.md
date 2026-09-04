# dreamerv3-sparse-memory-JmjqTi4FDF

- slug: dreamerv3-sparse-memory-JmjqTi4FDF
- authors: TBD
- venue: OpenReview
- year: TBD
- identifier: OpenReview JmjqTi4FDF
- projects: [ism-v1, memoryprint, wiring-not-weights]
- gates: [G5, G6, G7]
- verdict: sharpens

## Mechanism

TBD (unindexed; queued for WebFetch).

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
