"""Anatomical thought-propagation on a region-level connectome (ADR-013).

The transition kernel lives on brain regions, not abstract states. Given
a connectivity matrix over atlas parcels, `connectome_to_markov` builds
a random-walk Markov chain (the network-diffusion model of Abdelnour,
Voss, Raj 2014; Goni et al. 2014). The dynamics machinery in
`dynamics.py` then acquires a direct anatomical meaning:

- committor(sensory, motor)[r] = probability that activation seeded at
  the sensory region set reaches the motor region set before returning
  to the sensory set, evaluated at region r. The high-committor ridge
  is the stimulus-to-behavior thought path.
- MFPT to the motor set = expected propagation steps to the behavioral
  terminus, a latency proxy.
- PCCA(k) = metastable communities of the propagation, expected to
  recover the known functional networks.

This module is a thin anatomical wrapper over the audited dynamics
primitives; it adds no new probability math, only the region semantics.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .dynamics import committor, mean_first_passage_time, perron_cluster_analysis


def connectome_to_markov(
    connectivity: np.ndarray, threshold: float = 0.0
) -> np.ndarray:
    """Row-stochastic region transition matrix from a connectivity matrix.

    Keeps positive weights at or above `threshold`, zeros the diagonal
    (no self-loops in the propagation), and row-normalizes. A region with
    no surviving outgoing edge becomes an absorbing self-loop so the
    matrix stays row-stochastic.

    Negative functional-connectivity weights are dropped: the random-walk
    propagation models excitatory spread, and a signed random walk is not
    a probability kernel.
    """
    C = np.array(connectivity, dtype=float)
    if C.ndim != 2 or C.shape[0] != C.shape[1]:
        raise ValueError(f"connectivity must be square 2D; got {C.shape}")
    n = C.shape[0]
    W = np.where(C >= threshold, C, 0.0)
    W = np.maximum(W, 0.0)
    np.fill_diagonal(W, 0.0)
    row = W.sum(axis=1, keepdims=True)
    empty = (row.squeeze() == 0)
    if np.ndim(empty) == 0:
        empty = np.array([empty])
    if empty.any():
        for idx in np.where(empty)[0]:
            W[idx, idx] = 1.0
        row = W.sum(axis=1, keepdims=True)
    return W / row


@dataclass
class ActivationChain:
    """Result of propagating a stimulus from a sensory seed to a
    behavioral terminus on the region chain."""

    committor: np.ndarray            # (n_regions,) P(reach motor before sensory)
    mfpt_to_target: np.ndarray       # (n_regions,) expected steps to motor
    path_region_order: np.ndarray    # region indices ranked along the path
    source: list                     # sensory seed region indices
    target: list                     # motor terminus region indices


def activation_chain(
    T: np.ndarray, source: list[int], target: list[int]
) -> ActivationChain:
    """Compute the stimulus-to-behavior propagation chain.

    `source` = sensory seed regions (stimulus entry, e.g. visual).
    `target` = behavioral terminus regions (e.g. motor).

    Returns the committor (probability of reaching the target before
    returning to the source), the MFPT from every region to the target,
    and the region order along the sensory-to-motor path (sorted by
    committor ascending, so the sequence runs from source toward
    target).
    """
    q = committor(T, source_set=source, target_set=target)
    # MFPT to the target set: collapse the target set to a single
    # absorbing meta-state by taking the minimum MFPT to any target
    # region (expected steps to hit the set).
    mfpts = np.array([mean_first_passage_time(T, t) for t in target])
    mfpt_to_target = mfpts.min(axis=0)
    order = np.argsort(q)
    return ActivationChain(
        committor=q,
        mfpt_to_target=mfpt_to_target,
        path_region_order=order,
        source=list(source),
        target=list(target),
    )


@dataclass
class AtlasPropagation:
    """A region-level propagation model on a brain atlas.

    `transition` is the row-stochastic region Markov chain, `networks`
    the per-region functional-network label, `labels` the region names.
    """

    transition: np.ndarray
    networks: np.ndarray
    labels: np.ndarray

    def regions_in_network(self, network: str) -> list[int]:
        """Indices of regions whose functional-network label contains
        `network` (case-insensitive substring, so 'Vis' matches
        'Vis', 'SomMot' matches 'SomMot', etc.)."""
        net = network.lower()
        return [
            i for i, n in enumerate(self.networks)
            if net in str(n).lower()
        ]

    def stimulus_to_behavior(
        self, stimulus_network: str, behavior_network: str
    ) -> ActivationChain:
        """Propagate a stimulus class (seeded in its sensory network) to
        a behavior class (a motor / decision network) and return the
        chain."""
        src = self.regions_in_network(stimulus_network)
        tgt = self.regions_in_network(behavior_network)
        if not src:
            raise ValueError(f"no regions found for stimulus network "
                             f"{stimulus_network!r}")
        if not tgt:
            raise ValueError(f"no regions found for behavior network "
                             f"{behavior_network!r}")
        return activation_chain(self.transition, src, tgt)

    def metastable_communities(self, k: int) -> np.ndarray:
        """PCCA metastable communities of the propagation. Expected to
        recover the functional networks when k matches their count."""
        return perron_cluster_analysis(self.transition, k)
