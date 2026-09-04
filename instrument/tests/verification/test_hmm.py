"""ADR-012 verification for `hmm.py`: recovery of known HMM parameters.

An HMM implementation is only trustworthy if it recovers the
generating parameters from data it sampled itself. These tests
generate synthetic data from a known Gaussian HMM and confirm the fit
recovers the transition matrix, the emission means, and the latent
state sequence (up to the unavoidable label permutation), plus the EM
monotonicity invariant and BIC model selection.
"""

from __future__ import annotations

import numpy as np
import pytest

from neurospine.hmm import GaussianHMM


def _make_true_hmm() -> GaussianHMM:
    """Two well-separated states, sticky transitions."""
    h = GaussianHMM(n_states=2)
    h.start_prob = np.array([0.5, 0.5])
    h.trans = np.array([[0.9, 0.1], [0.15, 0.85]])
    h.means = np.array([[0.0, 0.0], [6.0, 6.0]])
    h.covs = np.array([np.eye(2), np.eye(2)])
    return h


def _best_permutation(true_means, est_means):
    """Match estimated states to true states by nearest mean."""
    K = len(true_means)
    perm = []
    used = set()
    for k in range(K):
        dists = [
            np.inf if j in used else np.linalg.norm(est_means[j] - true_means[k])
            for j in range(K)
        ]
        j = int(np.argmin(dists))
        used.add(j)
        perm.append(j)
    return perm


class TestParameterRecovery:
    def test_recovers_means(self) -> None:
        true = _make_true_hmm()
        rng = np.random.default_rng(0)
        X, _ = true.sample(2000, rng)
        fit = GaussianHMM(n_states=2, n_restarts=4, random_state=1).fit(X)
        perm = _best_permutation(true.means, fit.means)
        for k in range(2):
            assert np.linalg.norm(fit.means[perm[k]] - true.means[k]) < 0.5, (
                f"state {k} mean off: {fit.means[perm[k]]} vs {true.means[k]}"
            )

    def test_recovers_transition_matrix(self) -> None:
        true = _make_true_hmm()
        rng = np.random.default_rng(2)
        X, _ = true.sample(4000, rng)
        fit = GaussianHMM(n_states=2, n_restarts=4, random_state=3).fit(X)
        perm = _best_permutation(true.means, fit.means)
        T_est = fit.trans[np.ix_(perm, perm)]
        assert np.allclose(T_est, true.trans, atol=0.06), (
            f"transition matrix off:\n{T_est}\nvs\n{true.trans}"
        )

    def test_viterbi_recovers_states(self) -> None:
        true = _make_true_hmm()
        rng = np.random.default_rng(4)
        X, states = true.sample(2000, rng)
        fit = GaussianHMM(n_states=2, n_restarts=4, random_state=5).fit(X)
        path = fit.viterbi(X)
        perm = _best_permutation(true.means, fit.means)
        inv = {perm[k]: k for k in range(2)}
        mapped = np.array([inv[p] for p in path])
        acc = (mapped == states).mean()
        # Well-separated states: Viterbi should be near-perfect.
        assert acc > 0.95, f"Viterbi accuracy {acc:.3f} too low"


class TestEMInvariants:
    def test_loglik_monotonic(self) -> None:
        true = _make_true_hmm()
        rng = np.random.default_rng(6)
        X, _ = true.sample(1000, rng)
        # fit() raises AssertionError internally if EM ever decreases;
        # reaching here means monotonicity held across all restarts.
        fit = GaussianHMM(n_states=2, n_restarts=3, random_state=7).fit(X)
        h = fit.loglik_history
        assert all(b >= a - 1e-6 for a, b in zip(h[:-1], h[1:]))

    def test_score_is_finite(self) -> None:
        true = _make_true_hmm()
        rng = np.random.default_rng(8)
        X, _ = true.sample(500, rng)
        fit = GaussianHMM(n_states=2, n_restarts=2, random_state=9).fit(X)
        assert np.isfinite(fit.score(X))


class TestModelSelection:
    def test_bic_prefers_true_state_count(self) -> None:
        """Data from a 2-state HMM: BIC should not prefer 1 state over
        2 (a single Gaussian cannot capture the bimodality)."""
        true = _make_true_hmm()
        rng = np.random.default_rng(10)
        X, _ = true.sample(2000, rng)
        bic1 = GaussianHMM(n_states=1, n_restarts=2, random_state=11).fit(X).bic(X)
        bic2 = GaussianHMM(n_states=2, n_restarts=4, random_state=12).fit(X).bic(X)
        assert bic2 < bic1, f"BIC failed to prefer 2 states: {bic2} vs {bic1}"


class TestInputValidation:
    def test_rejects_1d_input(self) -> None:
        with pytest.raises(ValueError):
            GaussianHMM(n_states=2).fit(np.array([1.0, 2.0, 3.0]))

    def test_n_parameters_positive(self) -> None:
        true = _make_true_hmm()
        rng = np.random.default_rng(13)
        X, _ = true.sample(300, rng)
        fit = GaussianHMM(n_states=2, n_restarts=1, random_state=14).fit(X)
        assert fit.n_parameters() > 0
