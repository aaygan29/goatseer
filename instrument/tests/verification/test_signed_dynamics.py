"""ADR-015 verification for `signed_dynamics.py`: linear-rate-model
identities and the inhibition property the excitatory-only random walk
could not express.

External anchors: Gu et al. 2015 (Nat. Commun.) for the linear-system /
controllability-Gramian machinery; Galan 2008 (PLoS ONE) for the linear
rate model on the connectome. The tests check the linear-algebraic
identities the model rests on, plus the one behavioral property that
motivated the whole tier: an inhibitory edge SUPPRESSES its target.

Analytic two-node case used throughout:

    regions (source s, target t), one directed edge s -> t of weight w,
    leak gamma. Then A = [[-g, 0], [w, -g]], and for input u = [1, 0]:
        x_s = 1 / g
        x_t = w / g^2
    so an excitatory edge (w > 0) lifts x_t above zero and an inhibitory
    edge (w < 0) drives x_t below zero. That sign flip is the point.
"""

from __future__ import annotations

import numpy as np
import pytest

from neurospine.circuit import DirectedEdge
from neurospine.signed_dynamics import (
    SignedLinearSystem,
    build_signed_system,
)


def two_node(w: float, gamma: float = 2.0) -> SignedLinearSystem:
    """Source s -> target t with weight w. W[t, s] = w (effect of s on t)."""
    W = np.array([[0.0, 0.0], [w, 0.0]])
    return SignedLinearSystem(W=W, gamma=gamma, labels=["s", "t"])


class TestConstruction:
    def test_rejects_non_square(self) -> None:
        with pytest.raises(ValueError):
            SignedLinearSystem(W=np.zeros((2, 3)), gamma=1.0, labels=["a", "b"])

    def test_rejects_label_mismatch(self) -> None:
        with pytest.raises(ValueError):
            SignedLinearSystem(W=np.zeros((2, 2)), gamma=1.0, labels=["a"])

    def test_A_has_leak_on_diagonal(self) -> None:
        sys = two_node(0.5, gamma=2.0)
        assert np.allclose(np.diag(sys.A), -2.0)


class TestStability:
    def test_large_leak_is_stable(self) -> None:
        assert two_node(0.5, gamma=2.0).is_stable()

    def test_unstable_when_leak_too_small(self) -> None:
        # A single excitatory self-reinforcing pair: give W a positive
        # eigenvalue larger than gamma.
        W = np.array([[0.0, 3.0], [3.0, 0.0]])  # eigenvalues +/- 3
        sys = SignedLinearSystem(W=W, gamma=1.0, labels=["a", "b"])
        assert not sys.is_stable()
        assert sys.spectral_abscissa() > 0

    def test_steady_state_raises_when_unstable(self) -> None:
        W = np.array([[0.0, 3.0], [3.0, 0.0]])
        sys = SignedLinearSystem(W=W, gamma=1.0, labels=["a", "b"])
        with pytest.raises(ValueError, match="unstable"):
            sys.steady_state(np.array([1.0, 0.0]))


class TestSteadyState:
    def test_matches_two_node_analytic(self) -> None:
        w, g = 0.7, 2.0
        sys = two_node(w, gamma=g)
        x = sys.steady_state(np.array([1.0, 0.0]))
        assert x[0] == pytest.approx(1.0 / g, abs=1e-10)
        assert x[1] == pytest.approx(w / g**2, abs=1e-10)

    def test_solves_fixed_point(self) -> None:
        sys = two_node(0.7, gamma=2.0)
        u = np.array([1.0, 0.3])
        x = sys.steady_state(u)
        # At equilibrium A x + u = 0.
        assert np.allclose(sys.A @ x + u, 0.0, atol=1e-10)

    def test_linearity_superposition(self) -> None:
        sys = two_node(0.7, gamma=2.0)
        u1 = np.array([1.0, 0.0])
        u2 = np.array([0.0, 0.5])
        x_sum = sys.steady_state(u1 + u2)
        x_parts = sys.steady_state(u1) + sys.steady_state(u2)
        assert np.allclose(x_sum, x_parts, atol=1e-10)

    def test_inhibitory_edge_suppresses_target(self) -> None:
        u = np.array([1.0, 0.0])
        x_exc = two_node(+0.7, gamma=2.0).steady_state(u)
        x_inh = two_node(-0.7, gamma=2.0).steady_state(u)
        # Excitatory lifts the target above zero; inhibitory drives it
        # below zero. This is the property the random walk could not
        # express.
        assert x_exc[1] > 0
        assert x_inh[1] < 0
        assert x_inh[1] == pytest.approx(-x_exc[1], abs=1e-10)


class TestSimulate:
    def test_converges_to_steady_state(self) -> None:
        sys = two_node(0.7, gamma=2.0)
        u = np.array([1.0, 0.0])
        traj = sys.simulate(np.zeros(2), u, steps=5000, dt=0.01)
        assert np.allclose(traj[-1], sys.steady_state(u), atol=1e-3)


class TestControllability:
    def test_gramian_is_spd(self) -> None:
        sys = two_node(0.7, gamma=2.0)
        Wc = sys.controllability_gramian([0])
        assert np.allclose(Wc, Wc.T, atol=1e-10)
        assert np.all(np.linalg.eigvalsh(Wc) > 0)

    def test_gramian_solves_lyapunov(self) -> None:
        sys = two_node(0.7, gamma=2.0)
        Wc = sys.controllability_gramian([0])
        B = np.array([[1.0], [0.0]])
        residual = sys.A @ Wc + Wc @ sys.A.T + B @ B.T
        assert np.allclose(residual, 0.0, atol=1e-9)

    def test_min_control_energy_positive(self) -> None:
        sys = two_node(0.7, gamma=2.0)
        e = sys.minimum_control_energy([0], np.array([0.1, 0.1]))
        assert e > 0

    def test_closer_target_costs_less_energy(self) -> None:
        sys = two_node(0.7, gamma=2.0)
        near = sys.minimum_control_energy([0], np.array([0.1, 0.1]))
        far = sys.minimum_control_energy([0], np.array([1.0, 1.0]))
        assert far > near


class TestBuildSignedSystem:
    def test_builds_stable_system(self) -> None:
        rng = np.random.default_rng(0)
        fc = np.abs(rng.standard_normal((4, 4)))
        fc = (fc + fc.T) / 2
        labels = ["Vis_1", "Cont_1", "Amygdala_L", "SomMot_1"]
        nets = np.array(["Vis", "Cont", "Sub", "SomMot"])
        sys = build_signed_system(
            fc, labels, nets,
            excitatory_edges=[DirectedEdge("Vis", "Amygdala", 1.0)],
            inhibitory_edges=[DirectedEdge("Cont", "Amygdala", 1.0)],
        )
        assert sys.is_stable()

    def test_inhibitory_prior_has_negative_weight(self) -> None:
        rng = np.random.default_rng(1)
        fc = np.zeros((4, 4))
        labels = ["Vis_1", "Cont_1", "Amygdala_L", "SomMot_1"]
        nets = np.array(["Vis", "Cont", "Sub", "SomMot"])
        sys = build_signed_system(
            fc, labels, nets,
            excitatory_edges=[],
            inhibitory_edges=[DirectedEdge("Cont", "Amygdala", 1.0)],
            inh_weight=1.0,
        )
        # W[Amygdala, Cont] should be negative (effect of Cont on Amygdala).
        assert sys.W[2, 1] < 0

    def test_increasing_inhibition_lowers_target_activation(self) -> None:
        # The scientific claim: stronger PFC->amygdala inhibition
        # monotonically reduces amygdala steady-state activation under a
        # fixed visual drive. gamma is held fixed so the effect is the
        # inhibition alone, not a shifting leak.
        labels = ["Vis", "Cont", "Amygdala", "SomMot"]
        u = np.array([1.0, 0.3, 0.0, 0.0])  # visual + tonic PFC drive

        def amyg_activation(inh: float) -> float:
            W = np.zeros((4, 4))
            W[2, 0] = 1.0   # Vis -> Amygdala (exc)
            W[1, 0] = 1.0   # Vis -> Cont (exc)
            W[2, 1] = -inh  # Cont -> Amygdala (inh)
            sys = SignedLinearSystem(W=W, gamma=3.0, labels=labels)
            return sys.steady_state(u)[2]

        a0 = amyg_activation(0.0)
        a1 = amyg_activation(0.5)
        a2 = amyg_activation(1.0)
        assert a1 < a0
        assert a2 < a1
