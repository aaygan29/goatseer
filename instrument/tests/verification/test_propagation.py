"""ADR-013 verification for propagation.py on synthetic connectomes
with known structure. The anatomical meaning is only trustworthy if the
committor/MFPT/community math behaves correctly on graphs whose answer
is obvious by construction."""

from __future__ import annotations

import numpy as np
import pytest

from neurospine.propagation import (
    AtlasPropagation,
    activation_chain,
    connectome_to_markov,
)


class TestConnectomeToMarkov:
    def test_row_stochastic(self) -> None:
        rng = np.random.default_rng(0)
        C = np.abs(rng.standard_normal((10, 10)))
        C = 0.5 * (C + C.T)
        T = connectome_to_markov(C)
        assert np.allclose(T.sum(axis=1), 1.0)

    def test_drops_negative_weights(self) -> None:
        C = np.array([[0.0, 0.8, -0.9], [0.8, 0.0, 0.5], [-0.9, 0.5, 0.0]])
        T = connectome_to_markov(C)
        # Region 0 -> region 2 edge was negative, so no probability there.
        assert T[0, 2] == 0.0
        assert np.allclose(T.sum(axis=1), 1.0)

    def test_zero_diagonal_no_self_loops(self) -> None:
        C = np.abs(np.random.default_rng(1).standard_normal((6, 6)))
        C = 0.5 * (C + C.T)
        T = connectome_to_markov(C)
        # Diagonal is only nonzero for isolated nodes; here all connected.
        assert np.all(np.diag(T) < 1.0)

    def test_isolated_region_becomes_absorbing(self) -> None:
        C = np.zeros((3, 3))
        C[0, 1] = C[1, 0] = 1.0  # region 2 isolated
        T = connectome_to_markov(C)
        assert T[2, 2] == 1.0
        assert np.allclose(T.sum(axis=1), 1.0)


class TestActivationChain:
    def test_chain_graph_committor_monotone(self) -> None:
        """On a path graph 0-1-2-3-4, the committor from {0} to {4}
        must increase monotonically along the path."""
        n = 5
        C = np.zeros((n, n))
        for i in range(n - 1):
            C[i, i + 1] = C[i + 1, i] = 1.0
        T = connectome_to_markov(C)
        chain = activation_chain(T, source=[0], target=[4])
        q = chain.committor
        assert q[0] == pytest.approx(0.0)
        assert q[4] == pytest.approx(1.0)
        # Strictly increasing along the path.
        assert all(q[i] < q[i + 1] for i in range(n - 1))

    def test_committor_symmetric_midpoint(self) -> None:
        """On a symmetric path 0-1-2-3-4 the midpoint committor is 0.5."""
        n = 5
        C = np.zeros((n, n))
        for i in range(n - 1):
            C[i, i + 1] = C[i + 1, i] = 1.0
        T = connectome_to_markov(C)
        q = activation_chain(T, source=[0], target=[4]).committor
        assert q[2] == pytest.approx(0.5, abs=1e-6)

    def test_mfpt_decreases_toward_target(self) -> None:
        n = 5
        C = np.zeros((n, n))
        for i in range(n - 1):
            C[i, i + 1] = C[i + 1, i] = 1.0
        T = connectome_to_markov(C)
        chain = activation_chain(T, source=[0], target=[4])
        m = chain.mfpt_to_target
        assert m[4] == 0.0
        # Closer regions reach the target in fewer steps.
        assert m[3] < m[0]


class TestAtlasPropagation:
    def _two_community(self):
        """Two 3-node communities weakly linked; networks labeled A/B."""
        C = np.zeros((6, 6))
        for block in ([0, 1, 2], [3, 4, 5]):
            for i in block:
                for j in block:
                    if i != j:
                        C[i, j] = 1.0
        C[2, 3] = C[3, 2] = 0.05  # weak inter-community bridge
        networks = np.array(["A", "A", "A", "B", "B", "B"])
        labels = np.array([f"r{i}" for i in range(6)])
        return AtlasPropagation(
            transition=connectome_to_markov(C),
            networks=networks,
            labels=labels,
        )

    def test_regions_in_network(self) -> None:
        atlas = self._two_community()
        assert atlas.regions_in_network("A") == [0, 1, 2]
        assert atlas.regions_in_network("B") == [3, 4, 5]

    def test_metastable_communities_recover_blocks(self) -> None:
        atlas = self._two_community()
        labels = atlas.metastable_communities(2)
        assert set(labels[:3]) == {labels[0]}
        assert set(labels[3:]) == {labels[3]}
        assert labels[0] != labels[3]

    def test_stimulus_to_behavior_runs(self) -> None:
        atlas = self._two_community()
        chain = atlas.stimulus_to_behavior("A", "B")
        # Source regions have low committor, target high.
        assert chain.committor[0] < chain.committor[5]

    def test_missing_network_raises(self) -> None:
        atlas = self._two_community()
        with pytest.raises(ValueError):
            atlas.stimulus_to_behavior("A", "Z")
