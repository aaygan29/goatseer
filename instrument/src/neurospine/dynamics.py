"""Markov transition dynamics on the cognitive-state manifold.

Given a subject's trajectory of discretized state indices, this
module computes the probability-transition-matrix heuristic that
summarizes "where a thought travels": stationary distribution,
entropy rate, spectral gap, mean first passage times, committor
functions, and PCCA-like metastable decomposition.

The transition matrix itself is estimated from a discretized
sequence; discretization is the caller's responsibility (typical
choice: k-medoids on AIRM distance to a set of prototype SPD
matrices, so the discretization respects Riemannian geometry).
Manifold-aware helpers to build such a discretization live in
`manifold_discretization.py` when they land (queued).

External anchors (see `decisions/ADR-009-thought-trajectory-transition-kernel.md`):

- Deuflhard + Weber, "Robust Perron cluster analysis in conformation
  dynamics" (Linear Algebra Appl., 2005) for PCCA.
- Prinz, Wu, Sarich et al., "Markov models of molecular kinetics:
  generation and validation" (J. Chem. Phys., 2011) for the MSM
  discipline this module borrows.
- Coifman + Lafon 2006 for diffusion-map framing.
- `pubmed-31320220` Sohn et al. 2019 for the cortical low-dim
  curved-manifold justification of the discretization approach.

Numerical notes:

- Every transition matrix is checked for row-stochasticity within
  `1e-10` before an invariant is computed.
- Stationary distribution is the left-Perron eigenvector,
  normalized to sum to 1.
- Entropy rate is reported in nats per step (natural log).
- Spectral gap uses the second-largest eigenvalue MODULUS, not the
  algebraic second-largest, to correctly handle complex eigenvalues
  of non-reversible chains.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def _check_row_stochastic(T: np.ndarray, tol: float = 1e-9) -> None:
    if T.ndim != 2 or T.shape[0] != T.shape[1]:
        raise ValueError(
            f"transition matrix must be square 2D; got shape {T.shape}"
        )
    if (T < -tol).any():
        raise ValueError("transition matrix has negative entries")
    row_sums = T.sum(axis=1)
    if not np.allclose(row_sums, 1.0, atol=tol):
        raise ValueError(
            f"transition matrix rows must sum to 1; got max deviation "
            f"{np.abs(row_sums - 1.0).max():.3e}"
        )


def estimate_transition_matrix(
    state_indices: np.ndarray,
    num_states: int,
    laplace: float = 0.0,
) -> np.ndarray:
    """Count-based Markov transition matrix from a state sequence.

    `state_indices` is a 1D integer array with values in
    `[0, num_states)`. `laplace` is a smoothing prior added to every
    count (default 0.0, i.e. maximum-likelihood; use small positive
    for regularization when some states are rare).

    Returns a row-stochastic matrix `T` where `T[i, j] = P(next = j
    | current = i)`.
    """
    state_indices = np.asarray(state_indices)
    if state_indices.ndim != 1:
        raise ValueError(
            f"state_indices must be 1D; got shape {state_indices.shape}"
        )
    if state_indices.size < 2:
        raise ValueError("state_indices must have at least 2 samples")
    if (state_indices < 0).any() or (state_indices >= num_states).any():
        raise ValueError(
            "state_indices must be in [0, num_states); got min "
            f"{state_indices.min()} max {state_indices.max()}"
        )
    if laplace < 0:
        raise ValueError(f"laplace prior must be non-negative; got {laplace}")

    counts = np.full((num_states, num_states), float(laplace))
    for a, b in zip(state_indices[:-1], state_indices[1:]):
        counts[int(a), int(b)] += 1.0

    row_sums = counts.sum(axis=1, keepdims=True)
    empty_rows = (row_sums.squeeze() == 0)
    # For states never visited, place self-loop 1.0 so T stays
    # row-stochastic; those rows will not affect anything reachable
    # from the observed subgraph.
    if empty_rows.any():
        counts[empty_rows] = 0.0
        for idx in np.where(empty_rows)[0]:
            counts[idx, idx] = 1.0
        row_sums = counts.sum(axis=1, keepdims=True)
    return counts / row_sums


def stationary_distribution(T: np.ndarray, tol: float = 1e-10) -> np.ndarray:
    """Stationary distribution: the left-Perron eigenvector of T,
    normalized to sum to 1.

    Uses eigendecomposition. For irreducible aperiodic chains this
    returns the unique stationary distribution; for reducible chains
    it returns one valid stationary distribution.
    """
    _check_row_stochastic(T)
    eigvals, eigvecs = np.linalg.eig(T.T)
    # Find the eigenvalue closest to 1.
    idx = int(np.argmin(np.abs(eigvals - 1.0)))
    v = np.real(eigvecs[:, idx])
    # Sign convention: dominant component positive.
    if v.sum() < 0:
        v = -v
    v = np.maximum(v, 0.0)  # numerical clipping
    s = v.sum()
    if s < tol:
        raise ValueError(
            "stationary_distribution: Perron eigenvector normalization "
            f"failed; sum={s:.3e}. Chain may be pathological."
        )
    return v / s


def entropy_rate(T: np.ndarray, pi: np.ndarray | None = None) -> float:
    """Kolmogorov-Sinai entropy rate of the Markov chain in nats/step:

        h = sum_i pi_i sum_j T_ij log(1 / T_ij)

    with 0 log 0 = 0. If `pi` is not provided, it is computed from `T`.
    """
    _check_row_stochastic(T)
    if pi is None:
        pi = stationary_distribution(T)
    else:
        pi = np.asarray(pi, dtype=float)
        if pi.shape != (T.shape[0],):
            raise ValueError(
                f"pi shape {pi.shape} does not match T size {T.shape[0]}"
            )
    with np.errstate(divide="ignore", invalid="ignore"):
        logT = np.where(T > 0, np.log(T), 0.0)
    row_entropy = -np.sum(T * logT, axis=1)
    return float(np.sum(pi * row_entropy))


def spectral_gap(T: np.ndarray) -> float:
    """`1 - |lambda_2|` where `|lambda_2|` is the second-largest
    eigenvalue modulus of T. Larger gap = faster mixing.
    """
    _check_row_stochastic(T)
    eigvals = np.linalg.eigvals(T)
    moduli = np.sort(np.abs(eigvals))[::-1]
    if len(moduli) < 2:
        return 1.0
    lambda_1, lambda_2 = moduli[0], moduli[1]
    # For a row-stochastic T the largest modulus is 1 up to tolerance.
    return float(max(0.0, lambda_1 - lambda_2))


def mean_first_passage_time(
    T: np.ndarray, target: int
) -> np.ndarray:
    """MFPT from every state to `target`, solved as a linear system.

    For a chain with transition matrix T, let m_i = E[first hit of
    target | start i]. Then `m_target = 0` and for `i != target`:

        m_i = 1 + sum_j T_ij m_j.

    In matrix form, restricting to non-target states: `(I - T') m' =
    1`, where T' is the T with target row and column removed.
    """
    _check_row_stochastic(T)
    n = T.shape[0]
    if not (0 <= target < n):
        raise ValueError(f"target must be in [0, {n}); got {target}")
    if n == 1:
        return np.zeros(1)
    keep = [i for i in range(n) if i != target]
    A = np.eye(n - 1) - T[np.ix_(keep, keep)]
    b = np.ones(n - 1)
    m_sub = np.linalg.solve(A, b)
    m = np.zeros(n)
    m[keep] = m_sub
    return m


def committor(
    T: np.ndarray, source_set: list[int], target_set: list[int]
) -> np.ndarray:
    """Committor function q_i = P(reach target before source | start i).

    Harmonic on the transient states: `q_i = sum_j T_ij q_j`, with
    boundary q_i = 0 on source, q_i = 1 on target.
    """
    _check_row_stochastic(T)
    n = T.shape[0]
    source_set = list(source_set)
    target_set = list(target_set)
    if not source_set or not target_set:
        raise ValueError("source_set and target_set must both be non-empty")
    if set(source_set) & set(target_set):
        raise ValueError("source_set and target_set must be disjoint")
    boundary = set(source_set) | set(target_set)
    transient = [i for i in range(n) if i not in boundary]
    q = np.zeros(n)
    for t in target_set:
        q[t] = 1.0
    if not transient:
        return q
    # (I - T') q' = T_bt @ q_target
    T_tt = T[np.ix_(transient, transient)]
    T_tb = T[np.ix_(transient, target_set)]
    A = np.eye(len(transient)) - T_tt
    b = T_tb.sum(axis=1)
    q_trans = np.linalg.solve(A, b)
    for idx, val in zip(transient, q_trans):
        q[idx] = val
    return q


def perron_cluster_analysis(T: np.ndarray, k: int) -> np.ndarray:
    """PCCA-style metastable clustering: label each state with the
    dominant sign pattern of the top-`k` right eigenvectors of T.

    This is a compact, dependency-free approximation to the full
    PCCA / PCCA+ algorithm of Deuflhard and Weber; it captures the
    qualitative metastable decomposition for well-separated chains
    without matching PCCA+'s optimal rotation.

    Returns an integer label in `[0, k)` per state.
    """
    _check_row_stochastic(T)
    n = T.shape[0]
    if not (1 <= k <= n):
        raise ValueError(f"k must be in [1, {n}]; got {k}")
    if k == 1:
        return np.zeros(n, dtype=int)

    eigvals, eigvecs = np.linalg.eig(T)
    order = np.argsort(-np.abs(eigvals))
    top = eigvecs[:, order[:k]].real
    if k == 2:
        # Classical PCCA sign-structure clustering on the second
        # eigenvector: states with positive component go to one
        # basin, negative to the other. This is deterministic and
        # correct for two well-separated basins.
        return (top[:, 1] < 0).astype(int)
    # For k >= 3, use k-means++ initialization to avoid collapsed
    # centers on the top-k eigenvector rows.
    rng = np.random.default_rng(0)
    first = int(rng.integers(0, n))
    center_indices = [first]
    for _ in range(1, k):
        d = np.min(
            ((top[:, None, :] - top[center_indices][None, :, :]) ** 2).sum(axis=2),
            axis=1,
        )
        probs = d / d.sum() if d.sum() > 0 else np.full(n, 1.0 / n)
        center_indices.append(int(rng.choice(n, p=probs)))
    centers = top[center_indices].copy()
    labels = np.zeros(n, dtype=int)
    for _ in range(100):
        d = ((top[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
        new_labels = d.argmin(axis=1)
        if np.array_equal(new_labels, labels):
            break
        labels = new_labels
        for j in range(k):
            mask = labels == j
            if mask.any():
                centers[j] = top[mask].mean(axis=0)
    return labels


@dataclass(frozen=True)
class TrajectorySummary:
    """Summary of the Markov process induced by a discretized
    trajectory on the cognitive-state manifold.
    """

    stationary_distribution: np.ndarray
    stationary_entropy: float
    entropy_rate: float
    spectral_gap: float
    effective_dimension: float
    metastable_labels: np.ndarray

    def as_dict(self) -> dict[str, float]:
        """Return the scalar-valued fields as a plain dict, for
        embedding in `Thought.trajectory_summary`."""
        return {
            "stationary_entropy": float(self.stationary_entropy),
            "entropy_rate": float(self.entropy_rate),
            "spectral_gap": float(self.spectral_gap),
            "effective_dimension": float(self.effective_dimension),
        }


def summarize_trajectory(
    state_indices: np.ndarray,
    num_states: int,
    k_metastable: int = 2,
    laplace: float = 1.0 / 1024,
) -> TrajectorySummary:
    """Convenience: estimate the transition matrix and compute the
    full trajectory summary in one call.
    """
    T = estimate_transition_matrix(state_indices, num_states, laplace=laplace)
    pi = stationary_distribution(T)
    with np.errstate(divide="ignore", invalid="ignore"):
        log_pi = np.where(pi > 0, np.log(pi), 0.0)
    stationary_H = float(-np.sum(pi * log_pi))
    h_rate = entropy_rate(T, pi)
    gap = spectral_gap(T)
    eff_dim = float(np.exp(stationary_H))
    labels = perron_cluster_analysis(T, k_metastable)
    return TrajectorySummary(
        stationary_distribution=pi,
        stationary_entropy=stationary_H,
        entropy_rate=h_rate,
        spectral_gap=gap,
        effective_dimension=eff_dim,
        metastable_labels=labels,
    )


# --------------------------------------------------------------------
# Markov-assumption validation (ADR-009 required checks)
# --------------------------------------------------------------------


def estimate_transition_matrix_at_lag(
    state_indices: np.ndarray,
    num_states: int,
    lag: int,
    laplace: float = 0.0,
) -> np.ndarray:
    """Transition matrix at a given lag time.

    `T(lag)[i, j] = P(state_{t+lag} = j | state_t = i)`, estimated by
    counting `(x_t, x_{t+lag})` pairs. Lag-time selection is the
    central methodological choice in Markov state modeling: too short
    and the process is not yet Markov, too long and statistics are
    wasted.
    """
    state_indices = np.asarray(state_indices)
    if lag < 1:
        raise ValueError(f"lag must be >= 1; got {lag}")
    if state_indices.size <= lag:
        raise ValueError(
            f"need more than {lag} samples to estimate at lag {lag}; "
            f"got {state_indices.size}"
        )
    counts = np.full((num_states, num_states), float(laplace))
    for a, b in zip(state_indices[:-lag], state_indices[lag:]):
        counts[int(a), int(b)] += 1.0
    row_sums = counts.sum(axis=1, keepdims=True)
    empty = (row_sums.squeeze() == 0)
    if np.ndim(empty) == 0:
        empty = np.array([empty])
    if empty.any():
        counts[empty] = 0.0
        for idx in np.where(empty)[0]:
            counts[idx, idx] = 1.0
        row_sums = counts.sum(axis=1, keepdims=True)
    return counts / row_sums


def implied_timescales(
    state_indices: np.ndarray,
    num_states: int,
    lags: list[int],
    n_timescales: int = 3,
    laplace: float = 1.0 / 1024,
) -> dict:
    """Implied timescales across a lag sweep.

    For each lag, `t_i(lag) = -lag / log(|lambda_i(lag)|)` for the
    subdominant eigenvalues. If the process is Markov at lag `L`, the
    implied timescales become independent of lag for `lag >= L`: they
    plateau. A plateau is the standard justification for the Markov
    assumption; monotonic drift without plateau falsifies it.

    Returns the timescale curves plus a plateau diagnostic: the
    coefficient of variation of each timescale over the upper half of
    the lag range. A CV below `plateau_cv_threshold` (default 0.1)
    for the slowest timescale is the conventional plateau criterion.
    """
    if not lags:
        raise ValueError("lags must be non-empty")
    if n_timescales < 1:
        raise ValueError(f"n_timescales must be >= 1; got {n_timescales}")

    curves = np.full((len(lags), n_timescales), np.nan)
    for li, lag in enumerate(sorted(lags)):
        T = estimate_transition_matrix_at_lag(
            state_indices, num_states, lag, laplace=laplace
        )
        eigvals = np.linalg.eigvals(T)
        moduli = np.sort(np.abs(eigvals))[::-1]
        # Skip the stationary eigenvalue (modulus 1) and take the next ones.
        sub = moduli[1 : 1 + n_timescales]
        for ti, lam in enumerate(sub):
            if 0.0 < lam < 1.0:
                curves[li, ti] = -lag / np.log(lam)
            else:
                curves[li, ti] = np.nan

    sorted_lags = sorted(lags)
    upper_half = curves[len(sorted_lags) // 2 :, :]
    cvs = []
    for ti in range(n_timescales):
        col = upper_half[:, ti]
        col = col[np.isfinite(col)]
        if col.size < 2 or col.mean() == 0:
            cvs.append(float("nan"))
        else:
            cvs.append(float(col.std(ddof=1) / abs(col.mean())))

    slowest_cv = cvs[0] if cvs else float("nan")
    return {
        "lags": sorted_lags,
        "timescales": curves.tolist(),
        "upper_half_cv": cvs,
        "slowest_timescale_cv": slowest_cv,
        "plateau_detected": bool(
            np.isfinite(slowest_cv) and slowest_cv < 0.1
        ),
    }


def chapman_kolmogorov_test(
    state_indices: np.ndarray,
    num_states: int,
    lag: int,
    k_values: list[int] | None = None,
    laplace: float = 1.0 / 1024,
) -> dict:
    """Chapman-Kolmogorov test of the Markov assumption.

    If the process is Markov at lag `L`, then
    `T(k * L) == T(L)^k` for all integer `k >= 1`. This function
    estimates both sides directly from data and reports their
    discrepancy.

    Metric: the mean and max absolute row-wise total-variation
    distance between the estimated `T(k*L)` and the propagated
    `T(L)^k`. TV distance between two probability rows p and q is
    `0.5 * sum |p_i - q_i|`, so it lives in `[0, 1]` and is directly
    interpretable.

    A common acceptance criterion is max row TV below 0.1; that
    threshold is a convention, not a theorem, and is reported
    alongside the raw numbers so the reader can judge.
    """
    if k_values is None:
        k_values = [2, 3, 4]
    T_lag = estimate_transition_matrix_at_lag(
        state_indices, num_states, lag, laplace=laplace
    )
    results = []
    for k in k_values:
        if state_indices.size <= k * lag:
            results.append({
                "k": int(k),
                "skipped": True,
                "reason": f"sequence too short for lag {k * lag}",
            })
            continue
        T_direct = estimate_transition_matrix_at_lag(
            state_indices, num_states, k * lag, laplace=laplace
        )
        T_propagated = np.linalg.matrix_power(T_lag, k)
        row_tv = 0.5 * np.abs(T_direct - T_propagated).sum(axis=1)
        results.append({
            "k": int(k),
            "skipped": False,
            "mean_row_tv": float(row_tv.mean()),
            "max_row_tv": float(row_tv.max()),
        })

    live = [r for r in results if not r["skipped"]]
    worst = max((r["max_row_tv"] for r in live), default=float("nan"))
    return {
        "lag": int(lag),
        "per_k": results,
        "worst_max_row_tv": worst,
        "passes_conventional_threshold": bool(
            np.isfinite(worst) and worst < 0.1
        ),
    }


def absorption_probabilities(
    T: np.ndarray, absorbing: list[int]
) -> np.ndarray:
    """Absorption probabilities of an absorbing Markov chain.

    For a chain with absorbing states `absorbing` (each an absorbing
    self-loop, `T[a, a] = 1`), returns a matrix `B` of shape
    `(n_transient, n_absorbing)` where `B[s, e]` is the probability of
    being absorbed in absorbing state `e` starting from transient state
    `s`. Rows sum to 1 (every path is eventually absorbed, assuming the
    absorbing set is reachable from every transient state).

    Standard construction: with the chain reordered as `[[Q, R], [0, I]]`,
    `B = (I - Q)^{-1} R`. The returned array is indexed by the ORIGINAL
    transient-state order (a list `transient` is returned alongside so
    the caller can map rows back).
    """
    _check_row_stochastic(T)
    n = T.shape[0]
    absorbing = list(absorbing)
    aset = set(absorbing)
    for a in absorbing:
        if not np.isclose(T[a, a], 1.0):
            raise ValueError(
                f"state {a} is not absorbing (T[{a},{a}] = {T[a, a]:.3f})"
            )
    transient = [i for i in range(n) if i not in aset]
    if not transient:
        raise ValueError("no transient states")
    Q = T[np.ix_(transient, transient)]
    R = T[np.ix_(transient, absorbing)]
    N = np.linalg.inv(np.eye(len(transient)) - Q)
    B = N @ R
    full = np.zeros((n, len(absorbing)))
    for r, s in enumerate(transient):
        full[s] = B[r]
    for c, a in enumerate(absorbing):
        full[a, c] = 1.0
    return full


def expected_steps_to_absorption(
    T: np.ndarray, absorbing: list[int]
) -> np.ndarray:
    """Expected number of steps before absorption, per starting state.

    `t = (I - Q)^{-1} 1` for the transient block; absorbing states are 0.
    This is the expected processing depth before the chain reaches an
    absorbing (e.g. effector) node.
    """
    _check_row_stochastic(T)
    n = T.shape[0]
    aset = set(absorbing)
    transient = [i for i in range(n) if i not in aset]
    Q = T[np.ix_(transient, transient)]
    N = np.linalg.inv(np.eye(len(transient)) - Q)
    t = N @ np.ones(len(transient))
    full = np.zeros(n)
    for r, s in enumerate(transient):
        full[s] = t[r]
    return full
