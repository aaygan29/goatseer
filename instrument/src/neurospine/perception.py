"""Reference `PerceptionDecoder`: per-subject linear projection.

MEIcoder (Sobotka et al., arXiv:2510.20762) is the external anchor for
subject-conditional visual decoding. MEIcoder's own headline is that
small per-subject decoders (1000 to 2500 neurons, fewer than 1000
training points) suffice to reconstruct visual stimuli with high
fidelity. NEUROSPINE does not lift MEIcoder's weights or its
nonlinear head; it lifts only the class of per-subject linear
projections that MEIcoder generalizes. A subsequent
`MEIcoderStylePerceptionDecoder` may add the nonlinear head once the
weights are re-derived from public data (deferred).

Anchor for the language head (deferred): Tang et al. Nature
Neuroscience 2023 ([pubmed-37127759](../../../literature/pubmed-37127759.md))
non-invasive continuous-language semantic decoder.

Anchor for the manifold interpretation of the returned embedding:
Han + Bonner Current Biology 2026 ([pubmed-41570814](../../../literature/pubmed-41570814.md))
naturalistic individual differences on a high-dim visual manifold.

Design: the decoder is a linear projection `y = beta @ W + b`, per
subject. Zero external dependencies. If the caller supplies a
`target_embedding` in `context`, `decode` also computes cosine
nonconformity and returns a dict compatible with
`SplitConformalCalibration`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SubjectConditionalPerceptionDecoder:
    """Per-subject linear decoder from an ROI beta pattern to a
    target embedding space (e.g. CLIP-like semantic vector).

    `subject_weights[subject]` is a V x D matrix (V input features,
    D target embedding dimension) represented as `list[list[float]]`.
    `subject_bias[subject]` is a length-D vector, optional.

    Return contract of `decode(subject, recordings, context)`:

    - If `subject` has no per-subject calibration weights: return
      `None`. The harness will then set the field to `None`.
    - If `recordings` lacks the required `beta_pattern` key: return
      `None`.
    - Otherwise: compute the embedding. If `context` carries a
      `target_embedding` key, also compute the cosine nonconformity
      and return a dict `{"embedding": [...], "nonconformity_score":
      float}`. Otherwise return the raw embedding list.
    """

    subject_weights: dict[str, list[list[float]]] = field(default_factory=dict)
    subject_bias: dict[str, list[float]] = field(default_factory=dict)

    def decode(self, subject: str, recordings: dict, context: dict) -> Any | None:
        if subject not in self.subject_weights:
            return None
        beta = recordings.get("beta_pattern")
        if beta is None:
            return None

        weights = self.subject_weights[subject]
        if not weights:
            raise ValueError(
                f"subject {subject!r} has an empty weight matrix"
            )
        expected_v = len(weights)
        if len(beta) != expected_v:
            raise ValueError(
                f"beta length {len(beta)} does not match subject "
                f"{subject!r} weight rows {expected_v}"
            )

        embedding_dim = len(weights[0])
        bias = self.subject_bias.get(subject, [0.0] * embedding_dim)
        if len(bias) != embedding_dim:
            raise ValueError(
                f"bias length {len(bias)} does not match embedding "
                f"dim {embedding_dim}"
            )

        embedding = list(bias)
        for i, x in enumerate(beta):
            row = weights[i]
            for j in range(embedding_dim):
                embedding[j] += x * row[j]

        target = context.get("target_embedding")
        if target is None:
            return embedding
        nc = embedding_cosine_nonconformity(embedding, target)
        return {"embedding": embedding, "nonconformity_score": nc}


def embedding_cosine_nonconformity(
    predicted: list[float], target: list[float]
) -> float:
    """Cosine nonconformity: `1 - cos(pred, target)`, in `[0, 2]`.

    Zero when predicted and target are exactly aligned; two when
    exactly anti-aligned. A zero-norm vector on either side is
    reported as nonconformity 1.0 (maximally uninformative).
    """
    if len(predicted) != len(target):
        raise ValueError(
            f"embedding dim mismatch: predicted {len(predicted)} vs "
            f"target {len(target)}"
        )
    dot = sum(p * t for p, t in zip(predicted, target))
    norm_p = math.sqrt(sum(p * p for p in predicted))
    norm_t = math.sqrt(sum(t * t for t in target))
    if norm_p == 0.0 or norm_t == 0.0:
        return 1.0
    cos = dot / (norm_p * norm_t)
    cos = max(-1.0, min(1.0, cos))
    return 1.0 - cos


def identity_weights(n: int) -> list[list[float]]:
    """Convenience: an n x n identity matrix in list form. Used by
    tests and by pass-through decoders where the beta pattern is
    already in the target embedding space."""
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
