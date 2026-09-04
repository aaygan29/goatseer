"""ADR-003 verification for `manifold.py`: AIRM identities on Sym++(n).

External anchors: Bhatia (2007), Barachant et al. (2012). The
verification here checks the identities the AIRM is built on rather
than reproducing a published numerical result, because AIRM identities
are exact under the algebra and any implementation that respects them
is correct up to floating-point tolerance.

Identities tested:

1. `airm_distance(P, P) == 0` for any SPD P.
2. `airm_distance(P, Q) == airm_distance(Q, P)`.
3. `airm_distance(A P A.T, A Q A.T) == airm_distance(P, Q)` for
   invertible A (affine invariance).
4. `airm_exp_map(P, airm_log_map(P, Q)) == Q` on the manifold.
5. `airm_geodesic(P, Q, 0) == P` and `airm_geodesic(P, Q, 1) == Q`.
6. `airm_geodesic(P, Q, 0.5)` has AIRM distance `d/2` from both P
   and Q, where `d = airm_distance(P, Q)`.
7. `airm_parallel_transport(P, P, X) == X`.
8. `airm_parallel_transport(P, Q, X)` preserves the AIRM inner
   product: `<X, X>_P == <PT(X), PT(X)>_Q`.
9. `airm_frechet_mean` of a single matrix is that matrix.
10. `spd_sqrtm(A) @ spd_sqrtm(A) == A` for SPD A.
"""

from __future__ import annotations

import numpy as np
import pytest
from scipy.linalg import eigh

from neurospine.manifold import (
    LatentState,
    airm_distance,
    airm_exp_map,
    airm_frechet_mean,
    airm_geodesic,
    airm_inner,
    airm_log_map,
    airm_parallel_transport,
    grassmann_distance,
    grassmann_principal_angles,
    spd_expm,
    spd_invsqrtm,
    spd_logm,
    spd_sqrtm,
)


def random_spd(n: int, seed: int = 0, ridge: float = 0.5) -> np.ndarray:
    rng = np.random.default_rng(seed)
    A = rng.standard_normal((n, n))
    return A @ A.T + ridge * np.eye(n)


def random_invertible(n: int, seed: int = 1) -> np.ndarray:
    rng = np.random.default_rng(seed)
    A = rng.standard_normal((n, n))
    # Ensure invertibility by rejecting near-singular
    while abs(np.linalg.det(A)) < 1e-3:
        A = rng.standard_normal((n, n))
    return A


class TestSPDPrimitives:
    def test_sqrtm_roundtrip(self) -> None:
        P = random_spd(5, seed=0)
        S = spd_sqrtm(P)
        assert np.allclose(S @ S, P, atol=1e-10)

    def test_invsqrtm_matches_inverse_of_sqrtm(self) -> None:
        P = random_spd(5, seed=0)
        assert np.allclose(spd_invsqrtm(P), np.linalg.inv(spd_sqrtm(P)), atol=1e-10)

    def test_logm_expm_are_inverse(self) -> None:
        P = random_spd(5, seed=2)
        assert np.allclose(spd_expm(spd_logm(P)), P, atol=1e-10)

    def test_logm_nonspd_raises(self) -> None:
        A = np.array([[-1.0, 0.0], [0.0, 1.0]])
        with pytest.raises(ValueError):
            spd_logm(A)


class TestAIRMDistanceIdentities:
    def test_zero_on_diagonal(self) -> None:
        P = random_spd(4, seed=3)
        assert abs(airm_distance(P, P)) < 1e-8

    def test_symmetric(self) -> None:
        P = random_spd(4, seed=4)
        Q = random_spd(4, seed=5)
        d1 = airm_distance(P, Q)
        d2 = airm_distance(Q, P)
        assert abs(d1 - d2) < 1e-8

    def test_positive_when_different(self) -> None:
        P = random_spd(4, seed=6)
        Q = random_spd(4, seed=7)
        assert airm_distance(P, Q) > 1e-4

    def test_affine_invariance(self) -> None:
        P = random_spd(4, seed=8)
        Q = random_spd(4, seed=9)
        A = random_invertible(4, seed=10)
        d = airm_distance(P, Q)
        d_transformed = airm_distance(A @ P @ A.T, A @ Q @ A.T)
        assert abs(d - d_transformed) < 1e-6


class TestGeodesic:
    def test_endpoints(self) -> None:
        P = random_spd(3, seed=11)
        Q = random_spd(3, seed=12)
        assert np.allclose(airm_geodesic(P, Q, 0.0), P, atol=1e-8)
        assert np.allclose(airm_geodesic(P, Q, 1.0), Q, atol=1e-8)

    def test_midpoint_equidistant(self) -> None:
        P = random_spd(3, seed=13)
        Q = random_spd(3, seed=14)
        d = airm_distance(P, Q)
        M = airm_geodesic(P, Q, 0.5)
        dp = airm_distance(P, M)
        dq = airm_distance(M, Q)
        assert abs(dp - d / 2.0) < 1e-6
        assert abs(dq - d / 2.0) < 1e-6

    def test_out_of_range_t_raises(self) -> None:
        P = random_spd(3, seed=15)
        Q = random_spd(3, seed=16)
        with pytest.raises(ValueError):
            airm_geodesic(P, Q, -0.1)
        with pytest.raises(ValueError):
            airm_geodesic(P, Q, 1.1)


class TestLogExpDuality:
    def test_exp_log_roundtrip(self) -> None:
        P = random_spd(4, seed=17)
        Q = random_spd(4, seed=18)
        X = airm_log_map(P, Q)
        Q_recovered = airm_exp_map(P, X)
        assert np.allclose(Q, Q_recovered, atol=1e-8)


class TestParallelTransport:
    def test_identity_on_same_point(self) -> None:
        P = random_spd(3, seed=19)
        rng = np.random.default_rng(20)
        X = rng.standard_normal((3, 3))
        X = 0.5 * (X + X.T)
        PT = airm_parallel_transport(P, P, X)
        assert np.allclose(PT, X, atol=1e-10)

    def test_preserves_airm_norm(self) -> None:
        P = random_spd(3, seed=21)
        Q = random_spd(3, seed=22)
        rng = np.random.default_rng(23)
        X = rng.standard_normal((3, 3))
        X = 0.5 * (X + X.T)
        PT = airm_parallel_transport(P, Q, X)
        norm_P = airm_inner(P, X, X)
        norm_Q = airm_inner(Q, PT, PT)
        assert abs(norm_P - norm_Q) < 1e-6


class TestFrechetMean:
    def test_singleton_is_identity(self) -> None:
        P = random_spd(3, seed=24)
        assert np.allclose(airm_frechet_mean([P]), P, atol=1e-8)

    def test_two_matrices_is_geodesic_midpoint(self) -> None:
        P = random_spd(3, seed=25)
        Q = random_spd(3, seed=26)
        mean = airm_frechet_mean([P, Q])
        mid = airm_geodesic(P, Q, 0.5)
        assert np.allclose(mean, mid, atol=1e-6)

    def test_frechet_gradient_vanishes(self) -> None:
        rng = np.random.default_rng(27)
        matrices = [random_spd(3, seed=100 + i) for i in range(5)]
        mean = airm_frechet_mean(matrices, max_iter=200, tol=1e-10)
        tangent_sum = sum(airm_log_map(mean, M) for M in matrices)
        assert np.linalg.norm(tangent_sum, ord="fro") / len(matrices) < 1e-6


class TestGrassmann:
    def test_distance_zero_for_same_subspace(self) -> None:
        rng = np.random.default_rng(28)
        A = rng.standard_normal((5, 2))
        # Same subspace: multiply columns by an invertible 2x2
        B = A @ rng.standard_normal((2, 2))
        # SVD's floating-point noise on a 5x2 matrix is ~O(1e-7);
        # anything under 1e-6 is subspace equality up to noise.
        assert grassmann_distance(A, B) < 1e-6

    def test_distance_positive_for_different_subspaces(self) -> None:
        rng = np.random.default_rng(29)
        A = rng.standard_normal((5, 2))
        B = rng.standard_normal((5, 2))
        assert grassmann_distance(A, B) > 1e-4

    def test_principal_angles_bounded(self) -> None:
        rng = np.random.default_rng(30)
        A = rng.standard_normal((5, 2))
        B = rng.standard_normal((5, 2))
        angles = grassmann_principal_angles(A, B)
        assert (angles >= 0).all()
        assert (angles <= np.pi / 2 + 1e-8).all()


class TestLatentState:
    def test_spd_construction_accepts_spd(self) -> None:
        P = random_spd(3, seed=31)
        state = LatentState(family="spd", matrix=P, subject="sub-01")
        assert state.family == "spd"

    def test_spd_construction_rejects_non_spd(self) -> None:
        A = np.array([[-1.0, 0.0], [0.0, 1.0]])
        with pytest.raises(ValueError):
            LatentState(family="spd", matrix=A, subject="sub-01")

    def test_grassmann_construction_rejects_wide_matrix(self) -> None:
        rng = np.random.default_rng(32)
        wide = rng.standard_normal((2, 5))
        with pytest.raises(ValueError):
            LatentState(family="grassmann", matrix=wide, subject="sub-01")


class TestTangentEmbedding:
    """Verification for spd_tangent_vector / spd_tangent_embedding
    (ADR-012). The tangent embedding must be norm-preserving: the L2
    norm of the embedded vector equals the AIRM Riemannian distance
    from the reference to the point."""

    def test_norm_preserving(self) -> None:
        from neurospine.manifold import airm_distance, spd_tangent_vector

        R = random_spd(5, seed=0)
        for s in range(1, 6):
            X = random_spd(5, seed=s)
            v = spd_tangent_vector(R, X)
            assert np.linalg.norm(v) == pytest.approx(
                airm_distance(R, X), abs=1e-8
            )

    def test_reference_maps_to_zero(self) -> None:
        from neurospine.manifold import spd_tangent_vector

        R = random_spd(4, seed=7)
        v = spd_tangent_vector(R, R)
        assert np.allclose(v, 0.0, atol=1e-8)

    def test_embedding_dimension(self) -> None:
        from neurospine.manifold import spd_tangent_embedding

        mats = [random_spd(5, seed=s) for s in range(10)]
        vecs, ref = spd_tangent_embedding(mats)
        # n(n+1)/2 for n=5 is 15.
        assert vecs.shape == (10, 15)

    def test_embedding_uses_frechet_mean_by_default(self) -> None:
        from neurospine.manifold import (
            airm_frechet_mean,
            spd_tangent_embedding,
        )

        mats = [random_spd(3, seed=s) for s in range(6)]
        _, ref = spd_tangent_embedding(mats)
        fm = airm_frechet_mean(mats)
        assert np.allclose(ref, fm, atol=1e-6)
