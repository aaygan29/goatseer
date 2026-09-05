"""Geometry-preserving discretization of SPD trajectories (ADR-017).

The within-subject experiment showed that discretizing each covariance to
its nearest of a few global AIRM prototypes DISCARDS the class-discriminative
covariance geometry (a Riemannian MDM decoded left-vs-right motor imagery
that the prototype-state Markov model could not). The prototypes cluster on
dominant variance, not on the axis that separates the classes.

This module discretizes in the TANGENT SPACE at the AIRM Frechet mean, which
is a norm-preserving Euclidean embedding of the SPD manifold (Barachant et
al. 2012), and along the class-discriminative axis, so the resulting states
encode the discriminative geometry instead of averaging it away. The state
sequence is preserved, so the trajectory model still applies; it just sees
states that carry the signal.

Rigor note on supervision: the discriminative axis is fit on TRAINING labels
only. Because a supervised discretization encodes class information, any
shuffle null MUST refit the axis on shuffled labels too, or the null is
unfairly easy. The Frechet-mean reference and the tangent vectors are
label-independent, so the expensive step is computed once and only the axis
and bin edges are refit per permutation. `discriminant_axis`, `quantile_edges`
and `assign_states` are exposed for exactly that fast, correct null.

External anchor: Barachant et al. 2012 (tangent-space projection of
covariance matrices for BCI). Bins along a discriminant direction are the
supervised analogue of their tangent-space LDA.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .manifold import spd_tangent_embedding, spd_tangent_vector


def discriminant_axis(vectors: np.ndarray, labels: list) -> np.ndarray:
    """Unit discriminant direction in a Euclidean feature space: the leading
    eigenvector of the between-class scatter of `vectors` (N, d) under
    `labels`. For two classes this is the (normalized) class-mean difference.
    """
    vectors = np.asarray(vectors, dtype=float)
    classes = sorted(set(labels))
    if len(classes) < 2:
        raise ValueError("need at least two classes for a discriminant axis")
    grand = vectors.mean(axis=0)
    d = vectors.shape[1]
    Sb = np.zeros((d, d))
    for c in classes:
        idx = [i for i, y in enumerate(labels) if y == c]
        mu = vectors[idx].mean(axis=0) - grand
        Sb += len(idx) * np.outer(mu, mu)
    w, V = np.linalg.eigh(Sb)
    axis = V[:, -1]
    n = np.linalg.norm(axis)
    return axis / n if n > 0 else axis


def quantile_edges(values: np.ndarray, n_states: int) -> np.ndarray:
    """Interior bin edges splitting `values` into `n_states` quantile bins."""
    if n_states < 2:
        raise ValueError(f"n_states must be >= 2; got {n_states}")
    qs = np.linspace(0.0, 1.0, n_states + 1)[1:-1]
    return np.quantile(np.asarray(values, dtype=float), qs)


def assign_states(values: np.ndarray, edges: np.ndarray) -> np.ndarray:
    """Assign each value to a bin index in [0, len(edges)] via `edges`."""
    return np.digitize(np.asarray(values, dtype=float), edges).astype(int)


@dataclass
class SupervisedTangentDiscretizer:
    """Fit a tangent-space discriminant discretizer on labeled SPD matrices,
    then map any SPD matrix to a state index along the discriminant axis.

    `reference` is the AIRM Frechet mean of the fit matrices; `axis` is the
    unit discriminant direction in the tangent space at `reference`; `edges`
    are the quantile bin edges of the fit projections. `n_states` bins.
    """

    reference: np.ndarray
    axis: np.ndarray
    edges: np.ndarray
    n_states: int

    @classmethod
    def fit(cls, matrices: list, labels: list, n_states: int
            ) -> "SupervisedTangentDiscretizer":
        vecs, ref = spd_tangent_embedding(list(matrices))
        axis = discriminant_axis(vecs, labels)
        proj = vecs @ axis
        edges = quantile_edges(proj, n_states)
        return cls(reference=ref, axis=axis, edges=edges, n_states=n_states)

    def transform(self, matrices: list) -> np.ndarray:
        """Map SPD matrices to state indices in [0, n_states-1]."""
        proj = np.array([spd_tangent_vector(self.reference, M) @ self.axis
                         for M in matrices])
        states = assign_states(proj, self.edges)
        return np.clip(states, 0, self.n_states - 1)

    def project(self, matrices: list) -> np.ndarray:
        """Scalar projections onto the discriminant axis (for the fast null:
        embed once, then refit axis/edges on shuffled labels off the cached
        tangent vectors instead of re-embedding)."""
        return np.array([spd_tangent_vector(self.reference, M) @ self.axis
                         for M in matrices])
