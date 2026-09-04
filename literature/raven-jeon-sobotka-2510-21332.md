# raven-jeon-sobotka-2510-21332

- slug: raven-jeon-sobotka-2510-21332
- authors: Jeon, Sobotka, Choi, Brbic
- venue: NeurIPS 2025
- year: 2025
- identifier: arXiv:2510.21332
- projects: [jspace-loyalty, decision-phenotype, ism-v1]
- gates: [G2, G3, G8]
- verdict: sharpens

## Mechanism

TBD (unindexed; queued for WebFetch).

## Preliminary relevance mapping

Provisional: RAVEN addresses weak-to-strong generalization under distribution
shift, which directly bears on NEUROSPINE's calibrated confidence and loyalty
vector: both fields require stability across task distributions (G2, G3).

Provisional: The title suggests a method for improving model robustness when
weak supervision is available under shift; this may sharpen G2 (seed variance)
by clarifying how robust our confidence estimates must be across model variants,
and G8 (external validity) by testing generalization to held-out distributions.

## Action items

- [ ] Re-score G2 (seed variance) after understanding RAVEN's shift-robustness
  protocol.
- [ ] Re-score G3 (specification robustness) if the method provides a testable
  specification for multi-seed calibration.
- [ ] Cross-reference ../portfolio/jspace-loyalty/evaluation.md and
  ../portfolio/ism-v1/evaluation.md for distribution-shift effects on loyalty
  and honesty vectors.
