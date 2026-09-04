"""Directed anatomical circuits with exogenous effectors (ADR-014).

A functional connectome is symmetric and correlational, and a cortical
parcellation omits subcortical hubs and the peripheral effectors a
stimulus actually drives. This module builds a DIRECTED transition
matrix that combines three sources, keeping their epistemic status
distinct:

1. MEASURED functional connectivity (symmetric, from imaging).
2. DIRECTED anatomical priors: known directed edges from the literature
   (e.g. the LeDoux threat circuit), which imaging FC cannot provide.
3. EXOGENOUS effectors: nodes that receive from the brain but are NOT
   measured by imaging (autonomic, endocrine, peripheral motor). They
   are represented explicitly rather than faked into the FC, so the
   model can report what fraction of a response terminates in imaged
   versus un-imaged nodes.

The dynamics primitives in `dynamics.py` (committor, MFPT) then operate
on the combined directed chain. They already accept asymmetric
row-stochastic matrices, so no new probability math is introduced; this
module only assembles the graph and tracks the observability boundary.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .dynamics import (
    absorption_probabilities,
    expected_steps_to_absorption,
    mean_first_passage_time,
)


@dataclass(frozen=True)
class DirectedEdge:
    """A directed anatomical prior edge `source -> target` with weight.
    `source` and `target` are region labels (matched by substring)."""

    source: str
    target: str
    weight: float = 1.0


@dataclass(frozen=True)
class ExogenousEffector:
    """A node that receives from the brain but is not imaged.

    `in_edges` are (brain_region_label, weight) pairs. `imaged=False`
    marks it as outside the observability boundary; the model reports
    imaged-vs-effector terminal mass separately.
    """

    name: str
    in_edges: list  # list of (region_label, weight)
    imaged: bool = False


@dataclass
class DirectedCircuit:
    """A directed circuit over measured regions plus exogenous effectors.

    `transition` is the combined row-stochastic directed matrix over
    `node_labels` (regions first, then effectors). `n_regions` is the
    imaged region count; nodes at index >= n_regions are effectors.
    """

    transition: np.ndarray
    node_labels: list
    networks: np.ndarray
    n_regions: int
    effector_names: list = field(default_factory=list)

    def index_of(self, label_substr: str) -> list:
        """Region indices whose label contains `label_substr`."""
        s = label_substr.lower()
        return [i for i, l in enumerate(self.node_labels)
                if i < self.n_regions and s in str(l).lower()]

    def network_indices(self, network: str) -> list:
        s = network.lower()
        return [i for i in range(self.n_regions)
                if s in str(self.networks[i]).lower()]

    def effector_index(self, name: str) -> int:
        return self.node_labels.index(name)


    def response_distribution(self, seed: list) -> dict:
        """Where a stimulus seeded at `seed` regions terminates.

        All effectors are absorbing, so every path eventually reaches an
        effector. Returns the absorption distribution across effectors
        (the probability the response terminates in autonomic vs
        endocrine vs motor, averaged over the seed regions) plus the
        expected number of processing steps in imaged regions before the
        response reaches any effector.
        """
        eff_idx = [self.effector_index(n) for n in self.effector_names]
        B = absorption_probabilities(self.transition, eff_idx)
        steps = expected_steps_to_absorption(self.transition, eff_idx)
        seed_absorb = np.mean([B[s] for s in seed], axis=0)
        return {
            "absorption": {
                self.effector_names[c]: float(seed_absorb[c])
                for c in range(len(eff_idx))
            },
            "expected_processing_steps": float(np.mean([steps[s] for s in seed])),
        }

    def mfpt_between(self, seed: list, target_substr: str) -> float:
        """Expected steps from `seed` to the first region matching
        `target_substr` (e.g. 'Amygdala'). Used to compare routing
        (fast subcortical vs slow cortical) via ablation."""
        tgts = self.index_of(target_substr)
        if not tgts:
            raise ValueError(f"no region matches {target_substr!r}")
        mfpts = np.array([mean_first_passage_time(self.transition, t) for t in tgts])
        m = mfpts.min(axis=0)
        return float(np.mean([m[s] for s in seed]))

    def observability_boundary(self) -> dict:
        """Report the imaged / un-imaged structure of the circuit: how
        many nodes are measured brain regions vs exogenous effectors."""
        return {
            "n_imaged_regions": int(self.n_regions),
            "n_exogenous_effectors": int(len(self.effector_names)),
            "effectors": list(self.effector_names),
        }


def build_directed_circuit(
    fc: np.ndarray,
    node_labels: list,
    networks: np.ndarray,
    directed_priors: list,
    effectors: list,
    prior_weight: float = 2.0,
    fc_threshold: float = 0.0,
) -> DirectedCircuit:
    """Assemble a directed circuit.

    - `fc`: measured symmetric connectivity over the imaged regions.
    - `directed_priors`: list of `DirectedEdge` anatomical priors,
      matched to regions by label substring. These make the matrix
      asymmetric where imaging cannot.
    - `effectors`: list of `ExogenousEffector`. Each becomes a new node
      with incoming edges from its named regions and a single outgoing
      self-loop (effectors are terminal / absorbing in the propagation).
    - `prior_weight`: weight given to each anatomical prior edge,
      relative to the FC weights (which are correlations in roughly
      [0, 1]). A prior weight > 1 lets the known directed route dominate
      a weak correlational edge, which is the intended behavior.
    """
    n = fc.shape[0]
    labels = list(node_labels)
    eff_names = [e.name for e in effectors]
    total = n + len(effectors)

    # Weighted directed adjacency.
    W = np.where(fc >= fc_threshold, np.maximum(fc, 0.0), 0.0).copy()
    np.fill_diagonal(W, 0.0)
    W = np.pad(W, ((0, len(effectors)), (0, len(effectors))))

    def match(substr):
        s = substr.lower()
        return [i for i in range(n) if s in str(labels[i]).lower()]

    # Directed anatomical priors (asymmetric): add source->target only.
    for e in directed_priors:
        srcs, tgts = match(e.source), match(e.target)
        for si in srcs:
            for ti in tgts:
                W[si, ti] += prior_weight * e.weight

    # Exogenous effectors: incoming edges from named regions, terminal.
    for k, eff in enumerate(effectors):
        eff_i = n + k
        labels.append(eff.name)
        for region_substr, w in eff.in_edges:
            for si in match(region_substr):
                W[si, eff_i] += prior_weight * w
        W[eff_i, eff_i] = 1.0  # absorbing self-loop

    # Row-normalize; regions with no out-edge become self-absorbing.
    row = W.sum(axis=1, keepdims=True)
    empty = (row.squeeze() == 0)
    if np.ndim(empty) == 0:
        empty = np.array([empty])
    if empty.any():
        for idx in np.where(empty)[0]:
            W[idx, idx] = 1.0
        row = W.sum(axis=1, keepdims=True)
    T = W / row

    net_padded = np.array(list(networks) + ["Effector"] * len(effectors))
    return DirectedCircuit(
        transition=T,
        node_labels=labels,
        networks=net_padded,
        n_regions=n,
        effector_names=eff_names,
    )
