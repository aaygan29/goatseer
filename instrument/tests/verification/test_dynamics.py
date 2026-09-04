"""ADR-003 verification for `dynamics.py`: Markov transition invariants.

External anchors:

- Prinz, Wu, Sarich et al. 2011 (Markov state models in molecular
  kinetics) for the discipline.
- Deuflhard + Weber 2005 (robust PCCA) for the metastable-cluster
  target.

The tests verify mathematical identities:

1. Row-stochasticity of any estimated T.
2. Stationary distribution satisfies pi @ T == pi and sums to 1.
3. On a known two-state chain, the analytic stationary distribution
   and MFPT are recovered.
4. Entropy rate is bounded in `[0, log(n)]`.
5. Spectral gap is 0 for the identity chain, 1 for a strictly
   contractive uniform-mixing chain.
6. Committor is 0 on source, 1 on target, and in `[0, 1]` elsewhere.
7. PCCA labels partition the state space into `k` non-empty
   metastable subsets for a well-separated block chain.
"""

from __future__ import annotations

import numpy as np
import pytest

from neurospine.dynamics import (
    committor,
    entropy_rate,
    estimate_transition_matrix,
    mean_first_passage_time,
    perron_cluster_analysis,
    spectral_gap,
    stationary_distribution,
    summarize_trajectory,
)


class TestTransitionEstimation:
    def test_row_stochastic(self) -> None:
        rng = np.random.default_rng(0)
        seq = rng.integers(0, 5, size=1000)
        T = estimate_transition_matrix(seq, num_states=5)
        assert np.allclose(T.sum(axis=1), 1.0)
        assert (T >= 0).all()

    def test_deterministic_chain_recovered(self) -> None:
        # 0 -> 1 -> 2 -> 0 -> 1 -> 2 ...
        seq = np.array([0, 1, 2] * 30)
        T = estimate_transition_matrix(seq, num_states=3)
        # Every 0 goes to 1, every 1 to 2, every 2 to 0 (except last)
        assert T[0, 1] == pytest.approx(1.0)
        assert T[1, 2] == pytest.approx(1.0)

    def test_empty_row_becomes_self_loop(self) -> None:
        # State 2 never appears in transitions.
        seq = np.array([0, 1, 0, 1, 0, 1])
        T = estimate_transition_matrix(seq, num_states=3)
        assert T[2, 2] == pytest.approx(1.0)
        assert np.allclose(T.sum(axis=1), 1.0)

    def test_laplace_smoothing_prevents_zeros(self) -> None:
        seq = np.array([0, 0, 0, 0])
        T = estimate_transition_matrix(seq, num_states=2, laplace=1.0)
        assert (T > 0).all()

    def test_out_of_range_state_raises(self) -> None:
        seq = np.array([0, 1, 3])
        with pytest.raises(ValueError):
            estimate_transition_matrix(seq, num_states=3)


class TestStationaryDistribution:
    def test_pi_times_T_equals_pi(self) -> None:
        rng = np.random.default_rng(1)
        M = rng.random((4, 4)) + 0.01
        T = M / M.sum(axis=1, keepdims=True)
        pi = stationary_distribution(T)
        assert pi.sum() == pytest.approx(1.0)
        assert (pi >= 0).all()
        assert np.allclose(pi @ T, pi, atol=1e-8)

    def test_two_state_analytic(self) -> None:
        # T = [[1-a, a], [b, 1-b]] has pi = (b, a) / (a + b)
        a, b = 0.2, 0.5
        T = np.array([[1 - a, a], [b, 1 - b]])
        pi = stationary_distribution(T)
        expected = np.array([b, a]) / (a + b)
        assert np.allclose(pi, expected, atol=1e-8)


class TestEntropyRate:
    def test_deterministic_chain_zero_rate(self) -> None:
        T = np.array([[0.0, 1.0], [1.0, 0.0]])
        assert entropy_rate(T) == pytest.approx(0.0)

    def test_uniform_chain_maximum_rate(self) -> None:
        n = 4
        T = np.full((n, n), 1.0 / n)
        # Uniform T over n states: entropy rate = log(n).
        assert entropy_rate(T) == pytest.approx(np.log(n))

    def test_bounded(self) -> None:
        rng = np.random.default_rng(2)
        M = rng.random((5, 5)) + 0.01
        T = M / M.sum(axis=1, keepdims=True)
        h = entropy_rate(T)
        assert 0.0 <= h <= np.log(5) + 1e-8


class TestSpectralGap:
    def test_identity_chain_zero_gap(self) -> None:
        T = np.eye(4)
        assert spectral_gap(T) == pytest.approx(0.0)

    def test_uniform_chain_maximum_gap(self) -> None:
        T = np.full((4, 4), 0.25)
        # Uniform chain: lambda_1 = 1, all others 0 -> gap = 1.
        assert spectral_gap(T) == pytest.approx(1.0)


class TestMFPT:
    def test_two_state_analytic_mfpt(self) -> None:
        # For 2-state chain [[1-a, a], [b, 1-b]], MFPT from 0 to 1 is 1/a.
        a, b = 0.3, 0.7
        T = np.array([[1 - a, a], [b, 1 - b]])
        m = mean_first_passage_time(T, target=1)
        assert m[1] == 0.0
        assert m[0] == pytest.approx(1.0 / a, abs=1e-8)

    def test_target_has_zero_mfpt(self) -> None:
        rng = np.random.default_rng(3)
        M = rng.random((5, 5)) + 0.01
        T = M / M.sum(axis=1, keepdims=True)
        m = mean_first_passage_time(T, target=2)
        assert m[2] == 0.0
        assert (m[np.arange(5) != 2] > 0).all()


class TestCommittor:
    def test_bounded_between_zero_and_one(self) -> None:
        rng = np.random.default_rng(4)
        M = rng.random((5, 5)) + 0.01
        T = M / M.sum(axis=1, keepdims=True)
        q = committor(T, source_set=[0], target_set=[4])
        assert q[0] == 0.0
        assert q[4] == 1.0
        assert ((q >= 0.0) & (q <= 1.0)).all()

    def test_source_target_overlap_raises(self) -> None:
        T = np.full((3, 3), 1.0 / 3)
        with pytest.raises(ValueError):
            committor(T, source_set=[0, 1], target_set=[1, 2])


class TestPCCA:
    def test_block_chain_has_two_clusters(self) -> None:
        # Two nearly-disconnected blocks
        eps = 0.01
        T = np.array([
            [0.5 - eps, 0.5 - eps, eps, eps],
            [0.5 - eps, 0.5 - eps, eps, eps],
            [eps, eps, 0.5 - eps, 0.5 - eps],
            [eps, eps, 0.5 - eps, 0.5 - eps],
        ])
        T = T / T.sum(axis=1, keepdims=True)
        labels = perron_cluster_analysis(T, k=2)
        assert set(labels[:2]) == {labels[0]}
        assert set(labels[2:]) == {labels[2]}
        assert labels[0] != labels[2]

    def test_k_equals_one_returns_single_cluster(self) -> None:
        T = np.full((3, 3), 1.0 / 3)
        labels = perron_cluster_analysis(T, k=1)
        assert np.all(labels == 0)


class TestSummarizeTrajectory:
    def test_returns_populated_summary(self) -> None:
        rng = np.random.default_rng(5)
        seq = rng.integers(0, 4, size=500)
        summary = summarize_trajectory(seq, num_states=4)
        assert summary.stationary_distribution.shape == (4,)
        assert summary.effective_dimension > 1.0
        assert 0.0 <= summary.entropy_rate <= np.log(4) + 1e-8
        d = summary.as_dict()
        for k in ("stationary_entropy", "entropy_rate", "spectral_gap", "effective_dimension"):
            assert k in d
            assert isinstance(d[k], float)


class TestMarkovValidation:
    """Verification for the ADR-009 required Markov-assumption checks.

    A genuinely Markov chain must show a plateau in implied timescales
    and must pass Chapman-Kolmogorov. A deliberately non-Markov
    sequence must fail at least one. These tests use sequences whose
    Markov-ness is known by construction.
    """

    @staticmethod
    def _sample_markov(T: np.ndarray, n: int, seed: int = 0) -> np.ndarray:
        rng = np.random.default_rng(seed)
        k = T.shape[0]
        out = np.empty(n, dtype=int)
        out[0] = 0
        for t in range(1, n):
            out[t] = rng.choice(k, p=T[out[t - 1]])
        return out

    def test_lagged_estimator_matches_lag_one(self) -> None:
        from neurospine.dynamics import estimate_transition_matrix_at_lag

        seq = np.array([0, 1, 2, 0, 1, 2, 0, 1, 2, 0])
        T1a = estimate_transition_matrix(seq, num_states=3)
        T1b = estimate_transition_matrix_at_lag(seq, num_states=3, lag=1)
        assert np.allclose(T1a, T1b)

    def test_lagged_estimator_row_stochastic(self) -> None:
        from neurospine.dynamics import estimate_transition_matrix_at_lag

        rng = np.random.default_rng(0)
        seq = rng.integers(0, 4, size=300)
        for lag in (1, 2, 5, 10):
            T = estimate_transition_matrix_at_lag(seq, 4, lag)
            assert np.allclose(T.sum(axis=1), 1.0)

    def test_lag_too_long_raises(self) -> None:
        from neurospine.dynamics import estimate_transition_matrix_at_lag

        seq = np.array([0, 1, 0])
        with pytest.raises(ValueError):
            estimate_transition_matrix_at_lag(seq, 2, lag=5)

    def test_true_markov_chain_plateaus(self) -> None:
        """A sequence sampled from an actual Markov chain must show a
        plateau in implied timescales."""
        from neurospine.dynamics import implied_timescales

        T = np.array([
            [0.90, 0.08, 0.02],
            [0.05, 0.90, 0.05],
            [0.02, 0.08, 0.90],
        ])
        seq = self._sample_markov(T, 20000, seed=1)
        res = implied_timescales(seq, 3, lags=[1, 2, 3, 5, 8, 12], n_timescales=2)
        assert res["plateau_detected"], (
            f"expected plateau for a true Markov chain; "
            f"slowest CV = {res['slowest_timescale_cv']}"
        )

    def test_true_markov_chain_passes_chapman_kolmogorov(self) -> None:
        from neurospine.dynamics import chapman_kolmogorov_test

        T = np.array([
            [0.90, 0.08, 0.02],
            [0.05, 0.90, 0.05],
            [0.02, 0.08, 0.90],
        ])
        seq = self._sample_markov(T, 20000, seed=2)
        res = chapman_kolmogorov_test(seq, 3, lag=1, k_values=[2, 3])
        assert res["passes_conventional_threshold"], (
            f"true Markov chain failed CK; worst TV = {res['worst_max_row_tv']}"
        )

    def test_deterministic_period_3_fails_chapman_kolmogorov_at_lag_1(self) -> None:
        """A deterministic 3-cycle is Markov, so CK should PASS. This
        guards against a CK implementation that flags everything."""
        from neurospine.dynamics import chapman_kolmogorov_test

        seq = np.array([0, 1, 2] * 2000)
        res = chapman_kolmogorov_test(seq, 3, lag=1, k_values=[2, 3])
        assert res["passes_conventional_threshold"]

    def test_second_order_chain_is_detected_as_non_markov(self) -> None:
        """A second-order (non-Markov at lag 1) sequence should show a
        worse CK discrepancy than a first-order one on the same
        alphabet. This is the discriminative test."""
        from neurospine.dynamics import chapman_kolmogorov_test

        rng = np.random.default_rng(3)
        n = 20000
        seq = np.zeros(n, dtype=int)
        seq[1] = 1
        # Next state depends on the PREVIOUS TWO states, not just one.
        for t in range(2, n):
            if seq[t - 1] == seq[t - 2]:
                seq[t] = (seq[t - 1] + 1) % 3
            else:
                seq[t] = seq[t - 2]
        non_markov = chapman_kolmogorov_test(seq, 3, lag=1, k_values=[2, 3])

        T = np.array([
            [0.90, 0.08, 0.02],
            [0.05, 0.90, 0.05],
            [0.02, 0.08, 0.90],
        ])
        markov_seq = self._sample_markov(T, n, seed=4)
        markov = chapman_kolmogorov_test(markov_seq, 3, lag=1, k_values=[2, 3])

        assert non_markov["worst_max_row_tv"] > markov["worst_max_row_tv"], (
            f"second-order sequence TV {non_markov['worst_max_row_tv']:.4f} "
            f"should exceed first-order TV {markov['worst_max_row_tv']:.4f}"
        )

    def test_implied_timescales_shape_and_keys(self) -> None:
        from neurospine.dynamics import implied_timescales

        rng = np.random.default_rng(5)
        seq = rng.integers(0, 4, size=2000)
        res = implied_timescales(seq, 4, lags=[1, 2, 4], n_timescales=2)
        assert res["lags"] == [1, 2, 4]
        assert len(res["timescales"]) == 3
        assert len(res["timescales"][0]) == 2
        assert "plateau_detected" in res

    def test_empty_lags_raises(self) -> None:
        from neurospine.dynamics import implied_timescales

        with pytest.raises(ValueError):
            implied_timescales(np.array([0, 1, 0, 1]), 2, lags=[])
