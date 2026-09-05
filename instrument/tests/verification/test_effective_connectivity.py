"""ADR-016 verification for `effective_connectivity.py`: recover a known
signed directed VAR(1) from its own simulated data, including the sign of
an inhibitory edge, plus the discrete steady-state and group-aggregation
identities.

External anchors: Frassle et al. 2017 (regression DCM), Seth/Barrett/
Barnett 2015 (Granger/VAR). The tests use synthetic ground truth because
a VAR fit is only trustworthy if it recovers a matrix it generated; the
data-side result lives in the experiment, not here.
"""

from __future__ import annotations

import numpy as np
import pytest

from neurospine.effective_connectivity import (
    directed_influence,
    discrete_steady_state,
    edge_group_stats,
    fit_var1,
    group_effective_connectivity,
    spectral_radius,
)


def simulate_var1(A: np.ndarray, T: int, seed: int, noise: float = 0.1) -> np.ndarray:
    """Simulate x_{t+1} = A x_t + noise from a stable A."""
    rng = np.random.default_rng(seed)
    n = A.shape[0]
    X = np.zeros((T, n))
    for t in range(T - 1):
        X[t + 1] = A @ X[t] + noise * rng.standard_normal(n)
    return X


class TestFitVar1:
    def test_recovers_known_matrix(self) -> None:
        A_true = np.array([[0.5, 0.0, 0.0],
                           [0.4, 0.3, 0.0],
                           [0.0, 0.0, 0.6]])
        X = simulate_var1(A_true, T=8000, seed=0, noise=0.1)
        A_hat = fit_var1(X, ridge=1e-3)
        assert np.allclose(A_hat, A_true, atol=0.05)

    def test_recovers_inhibitory_edge_sign(self) -> None:
        # Region 1 is driven POSITIVELY by region 0 and INHIBITED by
        # region 2. The estimator must recover A[1,0] > 0 and A[1,2] < 0.
        A_true = np.array([[0.5, 0.0, 0.0],
                           [0.5, 0.2, -0.4],
                           [0.0, 0.0, 0.5]])
        X = simulate_var1(A_true, T=8000, seed=1, noise=0.1)
        A_hat = fit_var1(X, ridge=1e-3)
        assert A_hat[1, 0] > 0
        assert A_hat[1, 2] < 0

    def test_convention_effect_of_j_on_i(self) -> None:
        # Only edge: region 0 drives region 2. Then A[2,0] is the large
        # entry, A[0,2] is near zero.
        A_true = np.zeros((3, 3))
        A_true[2, 0] = 0.6
        X = simulate_var1(A_true, T=8000, seed=2, noise=0.1)
        A_hat = fit_var1(X, ridge=1e-3)
        assert A_hat[2, 0] > 0.3
        assert abs(A_hat[0, 2]) < 0.1

    def test_ridge_shrinks_toward_zero(self) -> None:
        A_true = np.array([[0.5, 0.0], [0.4, 0.3]])
        X = simulate_var1(A_true, T=500, seed=3, noise=0.1)
        A_small = fit_var1(X, ridge=1e-3)
        A_big = fit_var1(X, ridge=1e6)
        assert np.linalg.norm(A_big) < np.linalg.norm(A_small)

    def test_rejects_bad_input(self) -> None:
        with pytest.raises(ValueError):
            fit_var1(np.zeros((2, 3)), ridge=1.0)  # too few time points
        with pytest.raises(ValueError):
            fit_var1(np.zeros((10, 3)), ridge=-1.0)  # negative ridge


class TestSpectralRadiusAndSteadyState:
    def test_spectral_radius_of_diagonal(self) -> None:
        A = np.diag([0.2, 0.7, -0.5])
        assert spectral_radius(A) == pytest.approx(0.7, abs=1e-10)

    def test_steady_state_solves_fixed_point(self) -> None:
        A = np.array([[0.3, 0.1], [0.2, 0.4]])
        u = np.array([1.0, 0.5])
        x = discrete_steady_state(A, u)
        assert np.allclose(A @ x + u, x, atol=1e-10)

    def test_steady_state_raises_when_unstable(self) -> None:
        A = np.array([[1.2, 0.0], [0.0, 0.3]])  # spectral radius 1.2
        with pytest.raises(ValueError, match="not stable"):
            discrete_steady_state(A, np.array([1.0, 0.0]))

    def test_inhibition_lowers_downstream_steady_state(self) -> None:
        # Same driver, one excitatory vs one inhibitory edge onto target.
        u = np.array([1.0, 0.0])
        A_exc = np.array([[0.3, 0.0], [0.4, 0.3]])
        A_inh = np.array([[0.3, 0.0], [-0.4, 0.3]])
        x_exc = discrete_steady_state(A_exc, u)
        x_inh = discrete_steady_state(A_inh, u)
        assert x_inh[1] < x_exc[1]


class TestGroupAggregation:
    def test_sign_consistency_one_when_all_agree(self) -> None:
        A_true = np.array([[0.5, 0.0], [0.4, 0.3]])
        Xs = [simulate_var1(A_true, T=4000, seed=s, noise=0.1) for s in range(6)]
        A_mean, cons = group_effective_connectivity(Xs, ridge=1e-3)
        # The A[1,0] edge is strongly positive in every subject.
        assert cons[1, 0] == pytest.approx(1.0, abs=1e-9)
        assert A_mean[1, 0] > 0

    def test_sign_consistency_near_half_for_null_edge(self) -> None:
        # An edge with no true influence has random sign across subjects.
        A_true = np.array([[0.5, 0.0], [0.0, 0.5]])
        Xs = [simulate_var1(A_true, T=300, seed=s, noise=0.5) for s in range(20)]
        _, cons = group_effective_connectivity(Xs, ridge=1e-2)
        assert cons[0, 1] < 0.9  # the null off-diagonal edge is unreliable

    def test_rejects_empty(self) -> None:
        with pytest.raises(ValueError):
            group_effective_connectivity([], ridge=1.0)


class TestEdgeGroupStats:
    def test_significant_and_time_reversal_for_real_edge(self) -> None:
        # Region 0 inhibits region 1 in every subject. The group edge
        # (effect of 0 on 1) should be significantly negative and the
        # forward estimate more negative than the time-reversed one.
        A_true = np.array([[0.5, 0.0], [-0.4, 0.3]])
        Xs = [simulate_var1(A_true, T=4000, seed=s, noise=0.1) for s in range(8)]
        labels = ["Cont", "Amygdala"]
        gs = edge_group_stats(Xs, labels, "Cont", "Amygdala", ridge=1e-2)
        assert gs["mean"] < 0
        assert gs["p_value"] < 0.05
        assert gs["net_directionality"] < 0  # forward more negative than reversed
        assert gs["n_subjects"] == 8

    def test_null_edge_not_significant(self) -> None:
        # No true influence 0 -> 1: group t-test should not reject at 0.05
        # for most seeds. Use a null-generating A with no 0->1 edge.
        A_true = np.array([[0.5, 0.0], [0.0, 0.5]])
        Xs = [simulate_var1(A_true, T=400, seed=s, noise=0.3) for s in range(10)]
        gs = edge_group_stats(Xs, ["a", "b"], "a", "b", ridge=1e-1)
        assert gs["p_value"] > 0.05


class TestDirectedInfluence:
    def test_reads_signed_edge_by_label(self) -> None:
        A = np.zeros((3, 3))
        A[2, 0] = -0.5  # effect of region 0 (Cont) on region 2 (Amygdala)
        labels = ["Cont_1", "Vis_1", "Amygdala_L"]
        out = directed_influence(A, labels, "Cont", "Amygdala")
        assert out["sign"] == -1
        assert out["mean_weight"] == pytest.approx(-0.5, abs=1e-10)
        assert out["n_pairs"] == 1

    def test_averages_over_matching_pairs(self) -> None:
        A = np.zeros((4, 4))
        # Two amygdala targets, one Cont source.
        A[2, 0] = -0.4
        A[3, 0] = -0.6
        labels = ["Cont_1", "Vis_1", "Amygdala_L", "Amygdala_R"]
        out = directed_influence(A, labels, "Cont", "Amygdala")
        assert out["mean_weight"] == pytest.approx(-0.5, abs=1e-10)
        assert out["n_pairs"] == 2

    def test_raises_on_no_match(self) -> None:
        A = np.zeros((2, 2))
        with pytest.raises(ValueError):
            directed_influence(A, ["a", "b"], "Cont", "Amygdala")
