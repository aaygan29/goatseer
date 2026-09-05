"""Effective connectivity from real BOLD via regularized VAR(1) (ADR-016).

ADR-015's signed linear system needed SIGNED directed weights, and those
were supplied as anatomical-literature priors (excitatory threat cascade,
an assumed-inhibitory prefrontal -> amygdala edge). This module estimates
those weights from data instead, so the sign of an edge becomes an
empirical result rather than an assumption.

The estimator is a ridge-regularized first-order vector autoregression:

    x_{t+1} = A x_t + e_t

fit per region by least squares. The off-diagonal `A[i, j]` is the signed
directed influence of region `j` on region `i` (Granger sense: how much
`j`'s activation at `t` predicts `i`'s at `t+1` beyond `i`'s own past).
This is the linearized / regression-DCM regime: a linear DCM with fixed
hemodynamics reduces to exactly this regression (Frassle et al. 2017,
"Regression DCM for fMRI", NeuroImage).

External anchors:

- Frassle et al. 2017, "Regression dynamic causal modeling for fMRI"
  (NeuroImage): the linearized, regression-form effective-connectivity
  estimator this module implements a ridge analogue of.
- Friston, Harrison, Penny 2003, "Dynamic causal modelling"
  (NeuroImage): the effective-connectivity framework (directed, signed
  influence) these estimates target.
- Seth, Barrett, Barnett 2015, "Granger causality analysis in
  neuroscience and neuroimaging" (J. Neurosci.): the VAR / Granger basis
  and its fMRI caveats (hemodynamic confounds, TR, downsampling).

Convention throughout: `A[i, j]` is the effect of `j` on `i`, matching
the signed-connectivity convention in `signed_dynamics.py` (`W[i, j]` is
the effect of `j` on `i`), so an estimated `A` drops straight into that
model.
"""

from __future__ import annotations

import numpy as np
from scipy import stats


def fit_var1(X: np.ndarray, ridge: float = 1.0) -> np.ndarray:
    """Ridge-regularized VAR(1) effective connectivity.

    - `X`: BOLD time series, shape `(T, n_regions)` (rows are time).
    - `ridge`: L2 penalty on `A`. `ridge > 0` is required on short fMRI
      runs where `T` is comparable to `n_regions`.

    Returns `A` of shape `(n_regions, n_regions)`, where `A[i, j]` is the
    signed directed influence of region `j` on region `i`. Solves, per
    target region `i`, the ridge regression of `X[t+1, i]` on `X[t, :]`:

        A^T = (P^T P + ridge I)^{-1} P^T F

    with `P = X[:-1]` (past) and `F = X[1:]` (future).
    """
    X = np.asarray(X, dtype=float)
    if X.ndim != 2:
        raise ValueError(f"X must be 2D (T, n); got shape {X.shape}")
    if X.shape[0] < 3:
        raise ValueError("need at least 3 time points")
    if ridge < 0:
        raise ValueError(f"ridge must be >= 0; got {ridge}")
    P = X[:-1]
    F = X[1:]
    n = X.shape[1]
    G = P.T @ P + ridge * np.eye(n)
    # A^T has shape (n, n); A^T[j, i] = coefficient of past region j for
    # target i, so A[i, j] = (that) = effect of j on i.
    A_T = np.linalg.solve(G, P.T @ F)
    return A_T.T


def spectral_radius(A: np.ndarray) -> float:
    """Largest eigenvalue modulus of `A`. A discrete VAR is stable (its
    steady state exists) iff this is strictly less than 1."""
    return float(np.max(np.abs(np.linalg.eigvals(A))))


def discrete_steady_state(A: np.ndarray, u: np.ndarray) -> np.ndarray:
    """Equilibrium `x = A x + u`, i.e. `x = (I - A)^{-1} u`, the sustained
    response of the estimated VAR system to a constant input `u`. Requires
    spectral radius < 1."""
    A = np.asarray(A, dtype=float)
    u = np.asarray(u, dtype=float)
    sr = spectral_radius(A)
    if sr >= 1.0:
        raise ValueError(
            f"estimated system is not stable (spectral radius {sr:.3f} "
            ">= 1); steady state is not defined"
        )
    return np.linalg.solve(np.eye(A.shape[0]) - A, u)


def group_effective_connectivity(
    time_series: list, ridge: float = 1.0
) -> tuple:
    """Fit VAR(1) per subject and aggregate.

    Returns `(A_mean, sign_consistency)`:

    - `A_mean`: element-wise mean of the per-subject `A` matrices.
    - `sign_consistency`: for each edge, the fraction of subjects whose
      estimate has the same sign as `A_mean` (in `[0.5, 1.0]`). An edge is
      trustworthy as a directed, signed claim only where this is high;
      it is the reliability filter that keeps a group mean from asserting
      a sign no individual subject supports.
    """
    if len(time_series) == 0:
        raise ValueError("time_series cannot be empty")
    As = np.array([fit_var1(X, ridge=ridge) for X in time_series])
    A_mean = As.mean(axis=0)
    mean_sign = np.sign(A_mean)
    agree = (np.sign(As) == mean_sign[None, :, :]).mean(axis=0)
    # Where the mean is exactly zero, sign is undefined; report 0.5.
    agree = np.where(mean_sign == 0, 0.5, agree)
    return A_mean, agree


def _edge_indices(labels: list, source_substr: str, target_substr: str):
    s, t = source_substr.lower(), target_substr.lower()
    src = [i for i, l in enumerate(labels) if s in str(l).lower()]
    tgt = [i for i, l in enumerate(labels) if t in str(l).lower()]
    if not src or not tgt:
        raise ValueError(
            f"no regions match source={source_substr!r} or "
            f"target={target_substr!r}"
        )
    return src, tgt


def edge_group_stats(
    time_series: list,
    labels: list,
    source_substr: str,
    target_substr: str,
    ridge: float = 1.0,
) -> dict:
    """Group-level statistics for one directed edge, with a time-reversed
    control.

    For each subject, the edge weight is the mean of `A[t, s]` over the
    matching source `s` and target `t` regions (the effect of source on
    target). Returns:

    - `per_subject`: the per-subject forward edge weights.
    - `mean`, `t_stat`, `p_value`: one-sample t-test of the forward
      weights against zero (is the directed influence non-zero at the
      group level?).
    - `reversed_mean`: the same edge estimated on TIME-REVERSED series.
      A genuine directed influence changes under time reversal, whereas
      spurious directionality from linearly-mixed noise does not (Vinck
      et al. 2015; Chvostekova et al. 2021). `net_directionality =
      mean - reversed_mean` is the reversal-controlled estimate.

    Time reversal is a control, not an oracle: Vinck et al. show it can
    misjudge some bidirectionally-coupled pairs even without noise, so it
    is reported alongside the raw estimate, not as a replacement.
    """
    src, tgt = _edge_indices(labels, source_substr, target_substr)

    def edge_of(A):
        return float(np.mean([A[i, j] for i in tgt for j in src]))

    fwd = np.array([edge_of(fit_var1(X, ridge=ridge)) for X in time_series])
    rev = np.array(
        [edge_of(fit_var1(np.asarray(X)[::-1], ridge=ridge)) for X in time_series]
    )
    if len(fwd) >= 2:
        t_stat, p_value = stats.ttest_1samp(fwd, 0.0)
    else:
        t_stat, p_value = float("nan"), float("nan")
    return {
        "per_subject": fwd.tolist(),
        "mean": float(fwd.mean()),
        "t_stat": float(t_stat),
        "p_value": float(p_value),
        "reversed_mean": float(rev.mean()),
        "net_directionality": float(fwd.mean() - rev.mean()),
        "n_subjects": len(fwd),
    }


def directed_influence(
    A: np.ndarray,
    labels: list,
    source_substr: str,
    target_substr: str,
    sign_consistency: np.ndarray | None = None,
) -> dict:
    """Summarize the estimated `source -> target` effective connectivity,
    averaged over all region pairs matching the two label substrings.

    Returns the mean signed weight, its sign, the number of pairs, and (if
    `sign_consistency` is given) the mean cross-subject sign agreement for
    those pairs. `A[i, j]` is the effect of `j` (source) on `i` (target).
    """
    src, tgt = _edge_indices(labels, source_substr, target_substr)
    vals = [A[i, j] for i in tgt for j in src]
    out = {
        "mean_weight": float(np.mean(vals)),
        "sign": int(np.sign(np.mean(vals))),
        "n_pairs": len(vals),
    }
    if sign_consistency is not None:
        cons = [sign_consistency[i, j] for i in tgt for j in src]
        out["mean_sign_consistency"] = float(np.mean(cons))
    return out
