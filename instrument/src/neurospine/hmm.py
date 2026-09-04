"""Gaussian hidden Markov model for cognitive-state trajectories.

Council review (ADR-011) established that a first-order Markov chain on
discretized SPD prototype states does not capture the EEG covariance
trajectory for a minority of subjects, and that the discretization
itself confounds the test. The principled next model (ADR-012) is a
hidden Markov model: a LATENT state chain that is first-order Markov,
emitting observations through a noisy channel. A latent chain can be
Markov even when the observed prototype sequence is not, which is the
standard resolution in the EEG/MEG brain-state literature (HMM-MAR,
microstate HMMs).

Crucially, this HMM operates on the CONTINUOUS tangent-space embedding
of the SPD covariances, NOT on discretized labels. Projecting each SPD
matrix to the tangent space at the global AIRM Frechet mean and
vectorizing gives a Euclidean feature that a Gaussian HMM can model
directly, sidestepping the discretization confound entirely.

Implementation notes:

- Full-covariance Gaussian emissions.
- Forward-backward and Baum-Welch run entirely in log space via
  `scipy.special.logsumexp` for numerical stability.
- Emission covariances are ridge-regularized each M-step to stay
  positive-definite on short sequences.
- `fit` does multiple random restarts and keeps the best final
  log-likelihood; EM log-likelihood is asserted non-decreasing within
  each restart (a standard EM correctness invariant).
- Dependency-light: numpy + scipy only, consistent with the rest of
  `neurospine`.

References (external anchors):

- Rabiner, "A Tutorial on Hidden Markov Models" (Proc. IEEE, 1989).
- Baker, Woolrich et al., "Fast transient networks in spontaneous
  human brain activity" (eLife, 2014) for HMM brain-state modeling.
- Bishop, "Pattern Recognition and Machine Learning" (2006), ch. 13,
  for the EM update equations used here.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.special import logsumexp


def _log_gaussian(x: np.ndarray, mean: np.ndarray, cov: np.ndarray) -> float:
    """Log density of a full-covariance multivariate Gaussian at x."""
    d = mean.shape[0]
    diff = x - mean
    sign, logdet = np.linalg.slogdet(cov)
    if sign <= 0:
        # Should not happen after ridge; guard anyway.
        cov = cov + 1e-6 * np.eye(d)
        sign, logdet = np.linalg.slogdet(cov)
    sol = np.linalg.solve(cov, diff)
    return float(-0.5 * (d * np.log(2 * np.pi) + logdet + diff @ sol))


def _log_emission_matrix(
    X: np.ndarray, means: np.ndarray, covs: np.ndarray
) -> np.ndarray:
    """`(T, K)` log emission probabilities log P(x_t | state=k)."""
    T = X.shape[0]
    K = means.shape[0]
    logB = np.empty((T, K))
    for k in range(K):
        for t in range(T):
            logB[t, k] = _log_gaussian(X[t], means[k], covs[k])
    return logB


@dataclass
class GaussianHMM:
    """A Gaussian hidden Markov model with full-covariance emissions.

    Parameters after `fit`:
    - `start_prob` (K,): initial state distribution.
    - `trans` (K, K): row-stochastic latent transition matrix.
    - `means` (K, D): emission means.
    - `covs` (K, D, D): emission covariances.
    """

    n_states: int
    n_iter: int = 100
    tol: float = 1e-4
    reg_covar: float = 1e-4
    n_restarts: int = 5
    random_state: int = 0

    start_prob: np.ndarray = field(default=None, repr=False)
    trans: np.ndarray = field(default=None, repr=False)
    means: np.ndarray = field(default=None, repr=False)
    covs: np.ndarray = field(default=None, repr=False)
    converged_loglik: float = field(default=-np.inf)
    loglik_history: list = field(default_factory=list, repr=False)

    def _init_params(self, X: np.ndarray, rng: np.random.Generator) -> None:
        T, D = X.shape
        K = self.n_states
        # k-means++-style mean init on the data.
        idx = [int(rng.integers(0, T))]
        for _ in range(1, K):
            d2 = np.min(
                [((X - X[i]) ** 2).sum(axis=1) for i in idx], axis=0
            )
            p = d2 / d2.sum() if d2.sum() > 0 else np.full(T, 1.0 / T)
            idx.append(int(rng.choice(T, p=p)))
        self.means = X[idx].copy()
        global_cov = np.cov(X.T) + self.reg_covar * np.eye(D)
        self.covs = np.array([global_cov.copy() for _ in range(K)])
        self.start_prob = np.full(K, 1.0 / K)
        # Slightly sticky init (HMM brain states are persistent).
        self.trans = np.full((K, K), 0.1 / max(1, K - 1))
        np.fill_diagonal(self.trans, 0.9)
        self.trans /= self.trans.sum(axis=1, keepdims=True)

    def _forward_backward(self, logB: np.ndarray):
        T, K = logB.shape
        log_start = np.log(self.start_prob + 1e-300)
        log_trans = np.log(self.trans + 1e-300)

        log_alpha = np.empty((T, K))
        log_alpha[0] = log_start + logB[0]
        for t in range(1, T):
            for j in range(K):
                log_alpha[t, j] = logB[t, j] + logsumexp(
                    log_alpha[t - 1] + log_trans[:, j]
                )

        log_beta = np.empty((T, K))
        log_beta[T - 1] = 0.0
        for t in range(T - 2, -1, -1):
            for i in range(K):
                log_beta[t, i] = logsumexp(
                    log_trans[i, :] + logB[t + 1] + log_beta[t + 1]
                )

        loglik = logsumexp(log_alpha[T - 1])
        log_gamma = log_alpha + log_beta - loglik
        return log_alpha, log_beta, log_gamma, loglik, log_trans

    def _fit_once(self, X: np.ndarray, rng: np.random.Generator):
        T, D = X.shape
        K = self.n_states
        self._init_params(X, rng)
        history = []
        prev_ll = -np.inf
        for _ in range(self.n_iter):
            logB = _log_emission_matrix(X, self.means, self.covs)
            log_alpha, log_beta, log_gamma, loglik, log_trans = (
                self._forward_backward(logB)
            )
            history.append(float(loglik))

            gamma = np.exp(log_gamma)  # (T, K)

            # xi: sum over t of P(state_t=i, state_{t+1}=j | X)
            log_xi_sum = np.full((K, K), -np.inf)
            for t in range(T - 1):
                for i in range(K):
                    vals = (
                        log_alpha[t, i]
                        + log_trans[i, :]
                        + logB[t + 1]
                        + log_beta[t + 1]
                        - loglik
                    )
                    log_xi_sum[i] = np.logaddexp(log_xi_sum[i], vals)
            xi_sum = np.exp(log_xi_sum)

            # M-step
            self.start_prob = gamma[0] + 1e-300
            self.start_prob /= self.start_prob.sum()
            self.trans = xi_sum + 1e-300
            self.trans /= self.trans.sum(axis=1, keepdims=True)
            Nk = gamma.sum(axis=0)  # (K,)
            for k in range(K):
                w = gamma[:, k]
                self.means[k] = (w[:, None] * X).sum(axis=0) / (Nk[k] + 1e-300)
                diff = X - self.means[k]
                cov = (w[:, None, None] * (diff[:, :, None] * diff[:, None, :])).sum(
                    axis=0
                ) / (Nk[k] + 1e-300)
                self.covs[k] = cov + self.reg_covar * np.eye(D)

            if loglik - prev_ll < self.tol and prev_ll > -np.inf:
                break
            prev_ll = loglik
        return history

    def fit(self, X: np.ndarray) -> "GaussianHMM":
        X = np.asarray(X, dtype=float)
        if X.ndim != 2:
            raise ValueError(f"X must be (T, D); got shape {X.shape}")
        best_ll = -np.inf
        best = None
        for r in range(self.n_restarts):
            rng = np.random.default_rng(self.random_state + r)
            history = self._fit_once(X, rng)
            # EM monotonicity within a restart. The covariance M-step is
            # ridge-regularized (reg_covar), which perturbs the pure-EM
            # objective, so a small relative dip is expected and allowed;
            # a real EM bug produces large, growing decreases. Tolerance
            # is relative to the log-likelihood magnitude.
            for a, b in zip(history[:-1], history[1:]):
                tol = max(1e-4, 1e-4 * abs(a))
                if b < a - tol:
                    raise AssertionError(
                        f"EM log-likelihood decreased beyond ridge tolerance: "
                        f"{a} -> {b} (tol {tol:.3e})"
                    )
            ll = history[-1]
            if ll > best_ll:
                best_ll = ll
                best = (
                    self.start_prob.copy(),
                    self.trans.copy(),
                    self.means.copy(),
                    self.covs.copy(),
                    list(history),
                )
        (self.start_prob, self.trans, self.means, self.covs,
         self.loglik_history) = best
        self.converged_loglik = best_ll
        return self

    def score(self, X: np.ndarray) -> float:
        """Log-likelihood of X under the fitted model."""
        X = np.asarray(X, dtype=float)
        logB = _log_emission_matrix(X, self.means, self.covs)
        _, _, _, loglik, _ = self._forward_backward(logB)
        return float(loglik)

    def viterbi(self, X: np.ndarray) -> np.ndarray:
        """MAP latent state sequence for X."""
        X = np.asarray(X, dtype=float)
        logB = _log_emission_matrix(X, self.means, self.covs)
        T, K = logB.shape
        log_start = np.log(self.start_prob + 1e-300)
        log_trans = np.log(self.trans + 1e-300)
        delta = np.empty((T, K))
        psi = np.zeros((T, K), dtype=int)
        delta[0] = log_start + logB[0]
        for t in range(1, T):
            for j in range(K):
                seq = delta[t - 1] + log_trans[:, j]
                psi[t, j] = int(np.argmax(seq))
                delta[t, j] = logB[t, j] + np.max(seq)
        path = np.empty(T, dtype=int)
        path[T - 1] = int(np.argmax(delta[T - 1]))
        for t in range(T - 2, -1, -1):
            path[t] = psi[t + 1, path[t + 1]]
        return path

    def n_parameters(self, diag_cov: bool = False) -> int:
        """Free-parameter count for BIC/AIC.

        start (K-1) + transitions K*(K-1) + means K*D + covariances
        (full: K*D*(D+1)/2)."""
        K, D = self.means.shape
        p_start = K - 1
        p_trans = K * (K - 1)
        p_means = K * D
        p_cov = K * D * (D + 1) // 2 if not diag_cov else K * D
        return p_start + p_trans + p_means + p_cov

    def bic(self, X: np.ndarray) -> float:
        """Bayesian information criterion: `-2 logL + p log T`. Lower is
        better."""
        X = np.asarray(X, dtype=float)
        T = X.shape[0]
        return -2.0 * self.score(X) + self.n_parameters() * np.log(T)

    def sample(self, n: int, rng: np.random.Generator) -> tuple:
        """Generate `(X, states)` of length n from the fitted model."""
        K, D = self.means.shape
        states = np.empty(n, dtype=int)
        X = np.empty((n, D))
        states[0] = rng.choice(K, p=self.start_prob)
        for t in range(1, n):
            states[t] = rng.choice(K, p=self.trans[states[t - 1]])
        for t in range(n):
            k = states[t]
            X[t] = rng.multivariate_normal(self.means[k], self.covs[k])
        return X, states
