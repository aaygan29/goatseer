"""ADR-014 verification for circuit.py and the absorption primitives.

Tests the directed-circuit assembly and the absorbing-chain math on
graphs with known answers."""

from __future__ import annotations

import numpy as np
import pytest

from neurospine.circuit import (
    DirectedEdge,
    ExogenousEffector,
    build_directed_circuit,
)
from neurospine.dynamics import (
    absorption_probabilities,
    expected_steps_to_absorption,
)


class TestAbsorptionProbabilities:
    def test_single_absorber_certain(self) -> None:
        T = np.array([[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [0.0, 0.0, 1.0]])
        B = absorption_probabilities(T, [2])
        assert B[0, 0] == pytest.approx(1.0)

    def test_two_absorbers_split(self) -> None:
        T = np.array([[0, 1, 0, 0], [0, 0, 0.5, 0.5], [0, 0, 1, 0], [0, 0, 0, 1]], float)
        B = absorption_probabilities(T, [2, 3])
        assert B[0].tolist() == pytest.approx([0.5, 0.5])

    def test_rows_sum_to_one(self) -> None:
        rng = np.random.default_rng(0)
        M = rng.random((6, 6)) + 0.01
        T = M / M.sum(axis=1, keepdims=True)
        # Make states 4,5 absorbing.
        for a in (4, 5):
            T[a] = 0.0
            T[a, a] = 1.0
        T = T / T.sum(axis=1, keepdims=True)
        B = absorption_probabilities(T, [4, 5])
        assert np.allclose(B[:4].sum(axis=1), 1.0)

    def test_non_absorbing_state_raises(self) -> None:
        T = np.array([[0.5, 0.5], [0.5, 0.5]])
        with pytest.raises(ValueError):
            absorption_probabilities(T, [1])

    def test_expected_steps_two_chain(self) -> None:
        T = np.array([[0, 1, 0, 0], [0, 0, 0.5, 0.5], [0, 0, 1, 0], [0, 0, 0, 1]], float)
        t = expected_steps_to_absorption(T, [2, 3])
        assert t[0] == pytest.approx(2.0)
        assert t[2] == 0.0


class TestDirectedCircuit:
    def _simple(self, **kw):
        # 3 regions A(vis) B(hub) C(motor), FC connects them symmetrically.
        fc = np.array([[0.0, 0.3, 0.1], [0.3, 0.0, 0.3], [0.1, 0.3, 0.0]])
        labels = ["Vis_1", "Hub_1", "SomMot_1"]
        networks = np.array(["Vis", "Hub", "SomMot"])
        priors = [DirectedEdge("Vis", "Hub", 1.0), DirectedEdge("Hub", "SomMot", 1.0)]
        effectors = [
            ExogenousEffector("Motor", [("SomMot", 1.0)]),
            ExogenousEffector("Auto", [("Hub", 1.0)]),
        ]
        return build_directed_circuit(fc, labels, networks, priors, effectors, **kw)

    def test_effectors_are_absorbing(self) -> None:
        c = self._simple()
        for name in c.effector_names:
            i = c.effector_index(name)
            assert c.transition[i, i] == pytest.approx(1.0)

    def test_row_stochastic(self) -> None:
        c = self._simple()
        assert np.allclose(c.transition.sum(axis=1), 1.0)

    def test_directed_prior_is_asymmetric(self) -> None:
        c = self._simple(prior_weight=5.0)
        vis, hub = c.index_of("Vis")[0], c.index_of("Hub")[0]
        # The prior Vis->Hub makes that direction heavier than Hub->Vis.
        assert c.transition[vis, hub] > c.transition[hub, vis]

    def test_response_distribution_sums_to_one(self) -> None:
        c = self._simple()
        seed = c.network_indices("Vis")
        resp = c.response_distribution(seed)
        assert sum(resp["absorption"].values()) == pytest.approx(1.0)

    def test_observability_boundary_counts(self) -> None:
        c = self._simple()
        ob = c.observability_boundary()
        assert ob["n_imaged_regions"] == 3
        assert ob["n_exogenous_effectors"] == 2

    def test_effector_receives_from_named_region(self) -> None:
        c = self._simple(prior_weight=3.0)
        motor_eff = c.effector_index("Motor")
        som = c.index_of("SomMot")[0]
        # SomMot region has an edge to the Motor effector.
        assert c.transition[som, motor_eff] > 0.0
        # Vis region has no direct edge to the Motor effector.
        vis = c.index_of("Vis")[0]
        assert c.transition[vis, motor_eff] == 0.0

    def test_missing_effector_region_ignored(self) -> None:
        # An effector whose source region does not exist just gets no
        # incoming edge; the build should not crash.
        fc = np.array([[0.0, 0.3], [0.3, 0.0]])
        labels = ["Vis_1", "SomMot_1"]
        networks = np.array(["Vis", "SomMot"])
        c = build_directed_circuit(
            fc, labels, networks, [],
            [ExogenousEffector("Ghost", [("Nonexistent", 1.0)])],
        )
        assert np.allclose(c.transition.sum(axis=1), 1.0)
