"""Riemannian primitives on the SPD and Grassmann manifolds.

The affine-invariant Riemannian metric (AIRM) on the manifold of
symmetric positive-definite matrices `Sym++(n)` is the workhorse for
NEUROSPINE's neural-state cartography. EEG / MEG cross-spectral
densities, fMRI connectivity matrices, and many latent-covariance
representations are SPD by construction, and Euclidean averaging
swells eigenvalues (well-documented in the pyRiemann literature).
AIRM preserves positive-definiteness and admits closed-form geodesics,
log/exp maps, and parallel transport.

For a subspace-valued state (e.g. shared response models), the
Grassmann manifold `Gr(k, n)` is the correct object; a minimal set of
Grassmann primitives lives at the bottom of this module.

References (external anchors, per ADR-002):

- Bhatia, "Positive Definite Matrices" (Princeton, 2007) for AIRM.
- Barachant, Bonnet, Congedo, Jutten, "Multiclass Brain-Computer
  Interface Classification by Riemannian Geometry", IEEE TBME 2012.
- Edelman, Arias, Smith, "The Geometry of Algorithms with
  Orthogonality Constraints", SIAM J. Matrix Anal. Appl. 1998, for
  Grassmann geometry.

Numerical safety:

- Every SPD input is symmetrized as `0.5 * (A + A.T)` before use.
- Every eigendecomposition uses `scipy.linalg.eigh` on the
  symmetrized matrix, which is numerically stable and returns real
  eigenvalues.
- Log/exp maps use eigen-basis evaluation, not power series.
- Tolerances are documented per function and returned in any
  identity-check test that consumes them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from scipy.linalg import eigh


Family = Literal["spd", "grassmann", "learned_latent", "euclidean"]


def _sym(A: np.ndarray) -> np.ndarray:
    """Force symmetry: `0.5 * (A + A.T)`. Idempotent, closed-form."""
    return 0.5 * (A + A.T)


def _is_spd(A: np.ndarray, tol: float = 1e-8) -> bool:
    """Return True iff A is symmetric and its smallest eigenvalue > tol.

    Uses `eigh` on the symmetrized matrix to avoid a Cholesky failure
    on marginally indefinite inputs from numerical drift.
    """
    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        return False
    S = _sym(A)
    if not np.allclose(A, S, atol=1e-6):
        return False
    w = eigh(S, eigvals_only=True)
    return bool(w.min() > tol)


def spd_sqrtm(A: np.ndarray) -> np.ndarray:
    """Principal SPD square root via eigendecomposition. `A = V diag(w) V.T`
    with `w > 0`; return `V diag(sqrt(w)) V.T`."""
    S = _sym(A)
    w, V = eigh(S)
    if w.min() <= 0:
        raise ValueError(
            f"spd_sqrtm requires strictly positive eigenvalues; got min "
            f"{w.min():.3e}. Regularize with a small ridge before calling."
        )
    return V @ np.diag(np.sqrt(w)) @ V.T


def spd_invsqrtm(A: np.ndarray) -> np.ndarray:
    """Principal SPD inverse square root via eigendecomposition."""
    S = _sym(A)
    w, V = eigh(S)
    if w.min() <= 0:
        raise ValueError(
            f"spd_invsqrtm requires strictly positive eigenvalues; got min "
            f"{w.min():.3e}."
        )
    return V @ np.diag(1.0 / np.sqrt(w)) @ V.T


def spd_logm(A: np.ndarray) -> np.ndarray:
    """Matrix logarithm on SPD via eigendecomposition. Real, symmetric."""
    S = _sym(A)
    w, V = eigh(S)
    if w.min() <= 0:
        raise ValueError(
            f"spd_logm requires strictly positive eigenvalues; got min "
            f"{w.min():.3e}."
        )
    return V @ np.diag(np.log(w)) @ V.T


def spd_expm(A: np.ndarray) -> np.ndarray:
    """Matrix exponential of a symmetric matrix via eigendecomposition.
    Returns an SPD matrix."""
    S = _sym(A)
    w, V = eigh(S)
    return V @ np.diag(np.exp(w)) @ V.T


def airm_distance(P: np.ndarray, Q: np.ndarray) -> float:
    """Affine-invariant Riemannian distance between two SPD matrices:

        d(P, Q) = || log(P^{-1/2} Q P^{-1/2}) ||_F

    Properties: symmetry `d(P, Q) = d(Q, P)`, non-negativity, `d(P, P)
    = 0`, invariance under `X -> A X A.T` for any invertible A.
    """
    P_inv_sqrt = spd_invsqrtm(P)
    M = _sym(P_inv_sqrt @ Q @ P_inv_sqrt)
    return float(np.linalg.norm(spd_logm(M), ord="fro"))


def airm_geodesic(P: np.ndarray, Q: np.ndarray, t: float) -> np.ndarray:
    """AIRM geodesic from P to Q evaluated at t in [0, 1]:

        gamma(t) = P^{1/2} (P^{-1/2} Q P^{-1/2})^t P^{1/2}

    where the fractional matrix power uses the eigen-basis. At t=0
    returns P; at t=1 returns Q.
    """
    if not (0.0 <= t <= 1.0):
        raise ValueError(f"t must be in [0, 1]; got {t}")
    P_sqrt = spd_sqrtm(P)
    P_inv_sqrt = spd_invsqrtm(P)
    M = _sym(P_inv_sqrt @ Q @ P_inv_sqrt)
    w, V = eigh(M)
    if w.min() <= 0:
        raise ValueError(
            "airm_geodesic requires the middle matrix to be SPD; got "
            f"min eigenvalue {w.min():.3e}."
        )
    M_t = V @ np.diag(np.power(w, t)) @ V.T
    return _sym(P_sqrt @ M_t @ P_sqrt)


def airm_log_map(P: np.ndarray, Q: np.ndarray) -> np.ndarray:
    """Riemannian log at P applied to Q: a tangent vector `X` in the
    tangent space `T_P M` such that `airm_exp_map(P, X) = Q`.

    Formula: `X = P^{1/2} log(P^{-1/2} Q P^{-1/2}) P^{1/2}`.
    """
    P_sqrt = spd_sqrtm(P)
    P_inv_sqrt = spd_invsqrtm(P)
    M = _sym(P_inv_sqrt @ Q @ P_inv_sqrt)
    return _sym(P_sqrt @ spd_logm(M) @ P_sqrt)


def airm_exp_map(P: np.ndarray, X: np.ndarray) -> np.ndarray:
    """Riemannian exp at P applied to tangent `X`: returns the SPD
    point reached by traveling along `X` from `P` for unit time.

    Formula: `Q = P^{1/2} exp(P^{-1/2} X P^{-1/2}) P^{1/2}`.
    """
    P_sqrt = spd_sqrtm(P)
    P_inv_sqrt = spd_invsqrtm(P)
    return _sym(P_sqrt @ spd_expm(_sym(P_inv_sqrt @ X @ P_inv_sqrt)) @ P_sqrt)


def airm_inner(P: np.ndarray, X: np.ndarray, Y: np.ndarray) -> float:
    """Affine-invariant inner product of tangent vectors X, Y at P:

        <X, Y>_P = tr(P^{-1} X P^{-1} Y)

    Symmetric in X, Y; positive-definite for `X = Y != 0`.
    """
    P_inv = np.linalg.inv(_sym(P))
    return float(np.trace(P_inv @ _sym(X) @ P_inv @ _sym(Y)))


def airm_parallel_transport(
    P: np.ndarray, Q: np.ndarray, X: np.ndarray
) -> np.ndarray:
    """Parallel-transport a tangent vector X from T_P M to T_Q M along
    the AIRM geodesic from P to Q.

    Formula: `X' = E X E.T` where `E = (Q P^{-1})^{1/2}`. E is
    computed via the standard SPD-based construction:

        E = P^{1/2} (P^{-1/2} Q P^{-1/2})^{1/2} P^{-1/2}
    """
    P_sqrt = spd_sqrtm(P)
    P_inv_sqrt = spd_invsqrtm(P)
    M = _sym(P_inv_sqrt @ Q @ P_inv_sqrt)
    M_sqrt = spd_sqrtm(M)
    E = P_sqrt @ M_sqrt @ P_inv_sqrt
    return _sym(E @ _sym(X) @ E.T)


def airm_frechet_mean(
    matrices: list[np.ndarray],
    max_iter: int = 100,
    tol: float = 1e-8,
) -> np.ndarray:
    """Frechet (Karcher) mean of a set of SPD matrices under AIRM.

    Iterative log-Euclidean initialization plus gradient descent:
    initialize as the log-Euclidean mean, then take Riemannian
    gradient steps until the mean tangent is below tolerance in
    Frobenius norm.
    """
    if not matrices:
        raise ValueError("frechet_mean requires at least one matrix")
    n = matrices[0].shape[0]
    for i, M in enumerate(matrices):
        if M.shape != (n, n):
            raise ValueError(
                f"matrices[{i}] has shape {M.shape}, expected ({n}, {n})"
            )

    # Log-Euclidean init
    mean_log = np.mean([spd_logm(M) for M in matrices], axis=0)
    P = spd_expm(mean_log)

    for _ in range(max_iter):
        tangent_sum = sum(airm_log_map(P, M) for M in matrices)
        step = tangent_sum / len(matrices)
        if np.linalg.norm(step, ord="fro") < tol:
            return P
        P = airm_exp_map(P, step)
    return P



def airm_geodesic_min_distance(
    P: np.ndarray, Q: np.ndarray, R: np.ndarray, n_samples: int = 201
) -> tuple[float, float]:
    """Minimum AIRM distance from the geodesic `P -> Q` to the point `R`.

    Returns `(min_distance, argmin_t)`.

    There is no closed form for the closest approach of an AIRM
    geodesic to an arbitrary third SPD point, so this samples the
    geodesic uniformly in the parameter `t` on `[0, 1]` and takes the
    minimum. Sampling density is the accuracy knob: the returned
    minimum is an UPPER bound on the true minimum, and the bound
    tightens as `n_samples` grows.

    This exists because evaluating a clearance at a single interior
    point (for example the midpoint `t = 0.5`) certifies nothing about
    the rest of the path. A forbidden region can sit exactly on the
    trajectory while the midpoint distance is comfortably large.
    """
    if n_samples < 2:
        raise ValueError(f"n_samples must be >= 2; got {n_samples}")
    best_d = float("inf")
    best_t = 0.0
    for t in np.linspace(0.0, 1.0, n_samples):
        d = airm_distance(airm_geodesic(P, Q, float(t)), R)
        if d < best_d:
            best_d = d
            best_t = float(t)
    return float(best_d), best_t


def spd_tangent_vector(reference: np.ndarray, X: np.ndarray) -> np.ndarray:
    """Vectorize the AIRM tangent vector of `X` at `reference` into a
    Euclidean coordinate whose L2 norm equals the AIRM Riemannian norm
    of the tangent.

    Steps (the standard pyRiemann tangent-space map):
    1. `S = log(reference^{-1/2} X reference^{-1/2})`, symmetric.
    2. Vectorize the upper triangle of `S`, weighting off-diagonal
       entries by `sqrt(2)` so that `||vec||_2 == ||S||_F`.

    The result is a `D = n(n+1)/2` vector for `n x n` SPD input. A set
    of such vectors, taken at the group Frechet mean, is the correct
    Euclidean embedding for feeding SPD trajectories to a Gaussian
    model without discretizing them.
    """
    R_inv_sqrt = spd_invsqrtm(reference)
    S = spd_logm(_sym(R_inv_sqrt @ X @ R_inv_sqrt))
    n = S.shape[0]
    iu = np.triu_indices(n)
    vec = S[iu].astype(float)
    # sqrt(2) weight on off-diagonal entries (they appear twice in ||.||_F)
    weights = np.where(iu[0] == iu[1], 1.0, np.sqrt(2.0))
    return vec * weights


def spd_tangent_embedding(
    matrices: list[np.ndarray], reference: np.ndarray | None = None
) -> tuple[np.ndarray, np.ndarray]:
    """Embed a list of SPD matrices into the tangent space at their
    AIRM Frechet mean (or at a supplied `reference`).

    Returns `(vectors, reference)` where `vectors` is `(N, n(n+1)/2)`.
    Norm-preserving per `spd_tangent_vector`.
    """
    if reference is None:
        reference = airm_frechet_mean(list(matrices))
    vecs = np.array([spd_tangent_vector(reference, M) for M in matrices])
    return vecs, reference

# --------------------------------------------------------------------
# Grassmann primitives
# --------------------------------------------------------------------


def grassmann_principal_angles(U: np.ndarray, V: np.ndarray) -> np.ndarray:
    """Principal angles between the column spans of U (n x k) and V (n x k').

    Returns the array of `min(k, k')` principal angles in `[0, pi/2]`,
    in ascending order. Uses SVD of `U.T @ V` and clips singular
    values to `[0, 1]` before `arccos` to handle numerical drift.
    """
    if U.ndim != 2 or V.ndim != 2 or U.shape[0] != V.shape[0]:
        raise ValueError(
            "grassmann_principal_angles requires two matrices with the "
            "same number of rows"
        )
    Qu, _ = np.linalg.qr(U)
    Qv, _ = np.linalg.qr(V)
    s = np.linalg.svd(Qu.T @ Qv, compute_uv=False)
    return np.arccos(np.clip(s, -1.0, 1.0))


def grassmann_distance(U: np.ndarray, V: np.ndarray) -> float:
    """Geodesic (arc-length) Grassmann distance: `sqrt(sum theta_i^2)`,
    i.e. the 2-norm of the vector of principal angles.

    This is the distance induced by the canonical metric on `Gr(k, n)`
    (Edelman, Arias, Smith 1998). It is NOT the chordal distance; see
    `grassmann_chordal_distance` for that, and note the two differ by
    a non-constant factor (they agree only in the small-angle limit).

    Bound: `0 <= d_geo <= sqrt(k) * pi / 2`.

    Important: the geodesic distance is not of negative type, so a
    Gram matrix built from it is generally indefinite. Do not use it
    to construct a PSD kernel or a classical-MDS embedding. Use
    `grassmann_chordal_distance` for those.
    """
    theta = grassmann_principal_angles(U, V)
    return float(np.sqrt(np.sum(theta ** 2)))


def grassmann_chordal_distance(U: np.ndarray, V: np.ndarray) -> float:
    """Chordal (projection Frobenius) Grassmann distance:
    `sqrt(sum sin^2 theta_i)`.

    Equivalently `(1 / sqrt(2)) * || U U^T - V V^T ||_F` for
    orthonormal-column U, V: it is the Euclidean distance between the
    orthogonal projectors onto the two subspaces, which is why it
    embeds isometrically in a Hilbert space and yields a PSD kernel.

    Bound: `0 <= d_chord <= sqrt(k)`.

    Use this, not `grassmann_distance`, whenever downstream code needs
    negative type: kernel construction, classical MDS, or anything
    assuming a Euclidean embedding of subspaces.
    """
    theta = grassmann_principal_angles(U, V)
    return float(np.sqrt(np.sum(np.sin(theta) ** 2)))


# --------------------------------------------------------------------
# High-level state container
# --------------------------------------------------------------------


@dataclass(frozen=True)
class LatentState:
    """A point on NEUROSPINE's cognitive-state manifold.

    `family` disambiguates the geometry:
    - `"spd"`: `matrix` is an SPD matrix; use AIRM.
    - `"grassmann"`: `matrix` is a tall-thin orthonormal-column
      matrix representing a subspace.
    - `"learned_latent"`: `matrix` is a coordinate vector in a
      learned latent manifold; treat metrically per the caller's
      pullback metric.
    - `"euclidean"`: baseline flat-vector case, for comparison.
    """

    family: Family
    matrix: np.ndarray
    subject: str
    timestamp: float | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.matrix, np.ndarray):
            raise TypeError(
                f"matrix must be numpy.ndarray; got {type(self.matrix)!r}"
            )
        if self.family == "spd":
            if not _is_spd(self.matrix):
                raise ValueError(
                    "family='spd' requires a symmetric positive-definite "
                    "matrix; symmetrize + ridge before construction if "
                    "your source is only positive-semidefinite."
                )
        if self.family == "grassmann":
            k = self.matrix.shape[1]
            if k > self.matrix.shape[0]:
                raise ValueError(
                    "family='grassmann' requires n >= k (tall-thin matrix)"
                )
