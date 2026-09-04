"""ADR-003 verification for `intervention.py`.

Tests the intervention-scoring semantics: purpose enforcement,
geodesic-tangent alignment, and channel ranking.
"""

from __future__ import annotations

import numpy as np
import pytest

from neurospine.intervention import (
    ChannelScore,
    Intervention,
    InterventionChannel,
    PURPOSE_REGISTRY,
    PurposeNotRegisteredError,
    score_intervention_channels,
)
from neurospine.manifold import (
    LatentState,
    airm_log_map,
)


def random_spd(n: int, seed: int = 0, ridge: float = 0.5) -> np.ndarray:
    rng = np.random.default_rng(seed)
    A = rng.standard_normal((n, n))
    return A @ A.T + ridge * np.eye(n)


def state(matrix: np.ndarray, subject: str = "sub-01") -> LatentState:
    return LatentState(family="spd", matrix=matrix, subject=subject)


class TestPurposeEnforcement:
    def test_unregistered_purpose_raises(self) -> None:
        P = random_spd(3, seed=0)
        Q = random_spd(3, seed=1)
        with pytest.raises(PurposeNotRegisteredError):
            score_intervention_channels(
                state(P), state(Q), [], purpose="not_a_real_purpose"
            )

    def test_registered_purpose_accepted(self) -> None:
        P = random_spd(3, seed=2)
        Q = random_spd(3, seed=3)
        result = score_intervention_channels(
            state(P), state(Q), [], purpose="sustained_attention"
        )
        assert isinstance(result, Intervention)
        assert result.purpose == "sustained_attention"

    def test_intervention_construction_rejects_bad_purpose(self) -> None:
        P = random_spd(3, seed=4)
        Q = random_spd(3, seed=5)
        with pytest.raises(PurposeNotRegisteredError):
            Intervention(
                purpose="fictional_purpose",
                current_state=state(P),
                target_state=state(Q),
                channels_by_efficacy=(),
                geodesic_length=1.0,
                safety_margin=1.0,
            )


class TestChannelScoring:
    def test_geodesic_direction_wins(self) -> None:
        P = random_spd(3, seed=6)
        Q = random_spd(3, seed=7)
        geo_tangent = airm_log_map(P, Q)

        # Channel 1: exactly aligned with the geodesic tangent.
        ch_geo = InterventionChannel(
            name="aligned",
            pushforward=lambda x, geo=geo_tangent: geo.copy(),
            modality="synthetic",
        )
        # Channel 2: orthogonal direction (negated log map)
        ch_orth = InterventionChannel(
            name="anti",
            pushforward=lambda x, geo=geo_tangent: -geo.copy(),
            modality="synthetic",
        )

        result = score_intervention_channels(
            state(P), state(Q), [ch_geo, ch_orth],
            purpose="sustained_attention",
        )
        top = result.channels_by_efficacy[0]
        assert top.name == "aligned"
        assert top.airm_cosine_alignment == pytest.approx(1.0, abs=1e-6)

        bottom = result.channels_by_efficacy[-1]
        assert bottom.name == "anti"
        assert bottom.airm_cosine_alignment == pytest.approx(-1.0, abs=1e-6)

    def test_channels_sorted_descending(self) -> None:
        P = random_spd(3, seed=8)
        Q = random_spd(3, seed=9)
        rng = np.random.default_rng(10)
        channels = []
        for i in range(5):
            V = rng.standard_normal((3, 3))
            V = 0.5 * (V + V.T)
            channels.append(
                InterventionChannel(
                    name=f"c{i}",
                    pushforward=lambda x, v=V: v.copy(),
                    modality="synthetic",
                )
            )
        result = score_intervention_channels(
            state(P), state(Q), channels, purpose="sustained_attention"
        )
        aligns = [c.airm_cosine_alignment for c in result.channels_by_efficacy]
        assert aligns == sorted(aligns, reverse=True)


class TestGeodesicLength:
    def test_matches_manifold_distance(self) -> None:
        from neurospine.manifold import airm_distance

        P = random_spd(3, seed=11)
        Q = random_spd(3, seed=12)
        result = score_intervention_channels(
            state(P), state(Q), [], purpose="sustained_attention"
        )
        assert result.geodesic_length == pytest.approx(
            airm_distance(P, Q), abs=1e-8
        )


class TestSafetyMargin:
    def test_infinite_when_no_out_of_scope(self) -> None:
        P = random_spd(3, seed=13)
        Q = random_spd(3, seed=14)
        result = score_intervention_channels(
            state(P), state(Q), [], purpose="sustained_attention"
        )
        import math

        assert math.isinf(result.safety_margin)

    def test_finite_when_out_of_scope_declared(self) -> None:
        P = random_spd(3, seed=15)
        Q = random_spd(3, seed=16)
        R = random_spd(3, seed=17)
        result = score_intervention_channels(
            state(P), state(Q), [],
            purpose="sustained_attention",
            out_of_scope_region=state(R),
        )
        assert 0.0 <= result.safety_margin < float("inf")


class TestFamilyMismatch:
    def test_mismatched_families_raise(self) -> None:
        P = random_spd(3, seed=18)
        rng = np.random.default_rng(19)
        subspace = rng.standard_normal((5, 2))
        p_state = LatentState(family="spd", matrix=P, subject="s")
        g_state = LatentState(family="grassmann", matrix=subspace, subject="s")
        with pytest.raises(NotImplementedError):
            score_intervention_channels(
                p_state, g_state, [], purpose="sustained_attention"
            )


class TestPurposeRegistry:
    def test_registry_populated(self) -> None:
        assert len(PURPOSE_REGISTRY) >= 4
        assert "sustained_attention" in PURPOSE_REGISTRY
        assert "reduce_anxiety_preserve_cognition" in PURPOSE_REGISTRY

    def test_all_registry_values_are_descriptions(self) -> None:
        for k, v in PURPOSE_REGISTRY.items():
            assert isinstance(k, str) and k
            assert isinstance(v, str) and len(v) > 10


class TestSafetyMarginRegression:
    """Regression tests for the critical safety-margin defect found by
    adversarial audit on 2026-09-04.

    The original implementation evaluated the clearance to the
    out-of-scope region at the geodesic MIDPOINT gamma(0.5) only. That
    certifies nothing about the rest of the path: the reported margin
    was comfortably positive in cases where the trajectory terminates
    in, or passes exactly through, the forbidden state. The margin must
    be the minimum over t in [0, 1].

    Each test below is one of the counterexamples the verifier
    constructed, with the numbers it reported.
    """

    def test_target_is_forbidden_gives_zero_margin(self) -> None:
        """If the DECLARED TARGET is itself the out-of-scope state, the
        trajectory terminates in the forbidden region, so the true
        margin is 0. The old midpoint implementation reported L/2."""
        P = random_spd(3, seed=15)
        Q = random_spd(3, seed=16)
        result = score_intervention_channels(
            state(P), state(Q), [],
            purpose="sustained_attention",
            out_of_scope_region=state(Q),
        )
        assert result.safety_margin == pytest.approx(0.0, abs=1e-9), (
            f"target is the forbidden state, margin must be 0; got "
            f"{result.safety_margin}"
        )
        assert result.closest_approach_t == pytest.approx(1.0, abs=1e-6)

    def test_forbidden_state_on_the_path_gives_zero_margin(self) -> None:
        """If the out-of-scope state lies exactly ON the geodesic, the
        margin is 0 regardless of where on the path it sits. The old
        implementation reported 0.8575 for the t=0.15 case."""
        from neurospine.manifold import airm_geodesic

        P = random_spd(3, seed=15)
        Q = random_spd(3, seed=16)
        for t_forbidden in (0.15, 0.35, 0.75, 0.9):
            R = airm_geodesic(P, Q, t_forbidden)
            result = score_intervention_channels(
                state(P), state(Q), [],
                purpose="sustained_attention",
                out_of_scope_region=state(R),
            )
            assert result.safety_margin < 1e-2, (
                f"forbidden state on path at t={t_forbidden}, margin must "
                f"be ~0; got {result.safety_margin}"
            )
            assert abs(result.closest_approach_t - t_forbidden) < 0.02

    def test_margin_never_exceeds_midpoint_distance(self) -> None:
        """The minimum over the path is by definition at most the
        distance at any single point, including the midpoint. This is
        the invariant the old implementation violated."""
        from neurospine.manifold import airm_distance, airm_geodesic

        for seed in range(20, 30):
            P = random_spd(3, seed=seed)
            Q = random_spd(3, seed=seed + 100)
            R = random_spd(3, seed=seed + 200)
            result = score_intervention_channels(
                state(P), state(Q), [],
                purpose="sustained_attention",
                out_of_scope_region=state(R),
            )
            midpoint_d = airm_distance(airm_geodesic(P, Q, 0.5), R)
            assert result.safety_margin <= midpoint_d + 1e-9, (
                f"seed {seed}: min-over-path {result.safety_margin} "
                f"exceeded midpoint distance {midpoint_d}"
            )

    def test_argmin_is_not_always_the_midpoint(self) -> None:
        """The verifier's benign case: generic R has its closest
        approach at t=0.666, not 0.5. If argmin were always 0.5 the
        old implementation would have been accidentally correct."""
        P = random_spd(3, seed=15)
        Q = random_spd(3, seed=16)
        R = random_spd(3, seed=17)
        result = score_intervention_channels(
            state(P), state(Q), [],
            purpose="sustained_attention",
            out_of_scope_region=state(R),
        )
        assert abs(result.closest_approach_t - 0.5) > 0.05, (
            f"expected argmin away from the midpoint; got "
            f"t={result.closest_approach_t}"
        )

    def test_far_forbidden_region_keeps_large_margin(self) -> None:
        """Sanity: the fix must not collapse every margin to zero. A
        forbidden region far from the path keeps a healthy margin."""
        P = np.eye(3)
        Q = np.diag([1.2, 1.0, 0.9])
        R = np.diag([1000.0, 1000.0, 1000.0])
        result = score_intervention_channels(
            state(P), state(Q), [],
            purpose="sustained_attention",
            out_of_scope_region=state(R),
        )
        assert result.safety_margin > 5.0

    def test_no_out_of_scope_region_has_none_argmin(self) -> None:
        P = random_spd(3, seed=15)
        Q = random_spd(3, seed=16)
        result = score_intervention_channels(
            state(P), state(Q), [], purpose="sustained_attention"
        )
        import math
        assert math.isinf(result.safety_margin)
        assert result.closest_approach_t is None


class TestGrassmannMetricDistinction:
    """Regression tests for the grassmann_distance docstring defect
    found by adversarial audit on 2026-09-04.

    The docstring called the arc-length distance "chordal". They are
    different functions, and the distinction is load-bearing: the
    geodesic distance matrix is not of negative type, so it cannot
    build a PSD kernel, while the chordal one can.
    """

    def test_geodesic_and_chordal_differ(self) -> None:
        from neurospine.manifold import (
            grassmann_chordal_distance,
            grassmann_distance,
        )

        # Orthogonal complementary 2-planes in R^4: all angles pi/2.
        U = np.eye(4)[:, :2]
        V = np.eye(4)[:, 2:4]
        d_geo = grassmann_distance(U, V)
        d_chord = grassmann_chordal_distance(U, V)
        assert d_geo == pytest.approx(np.sqrt(2) * np.pi / 2, abs=1e-9)
        assert d_chord == pytest.approx(np.sqrt(2), abs=1e-9)

    def test_ratio_is_not_a_constant(self) -> None:
        """If they differed by a fixed scale the naming would be a
        cosmetic issue. They do not."""
        from neurospine.manifold import (
            grassmann_chordal_distance,
            grassmann_distance,
        )

        rng = np.random.default_rng(0)
        subspaces = [np.linalg.qr(rng.standard_normal((8, 3)))[0] for _ in range(12)]
        ratios = []
        for i in range(len(subspaces)):
            for j in range(i + 1, len(subspaces)):
                dg = grassmann_distance(subspaces[i], subspaces[j])
                dc = grassmann_chordal_distance(subspaces[i], subspaces[j])
                if dc > 1e-8:
                    ratios.append(dg / dc)
        assert max(ratios) - min(ratios) > 0.1, (
            f"ratio range {min(ratios):.4f}..{max(ratios):.4f} is too tight; "
            "expected a non-constant factor"
        )

    def test_chordal_respects_sqrt_k_bound(self) -> None:
        from neurospine.manifold import grassmann_chordal_distance

        rng = np.random.default_rng(1)
        k = 3
        for _ in range(20):
            U = np.linalg.qr(rng.standard_normal((8, k)))[0]
            V = np.linalg.qr(rng.standard_normal((8, k)))[0]
            assert grassmann_chordal_distance(U, V) <= np.sqrt(k) + 1e-9

    def test_chordal_is_negative_type_geodesic_is_not(self) -> None:
        """The property that separates the two names. Classical MDS on
        the chordal matrix is valid; on the geodesic matrix it is not."""
        from neurospine.manifold import (
            grassmann_chordal_distance,
            grassmann_distance,
        )

        rng = np.random.default_rng(0)
        subs = [np.linalg.qr(rng.standard_normal((8, 3)))[0] for _ in range(25)]
        n = len(subs)

        def gram_min_eig(metric) -> float:
            D = np.zeros((n, n))
            for i in range(n):
                for j in range(i + 1, n):
                    d = metric(subs[i], subs[j])
                    D[i, j] = D[j, i] = d
            J = np.eye(n) - np.ones((n, n)) / n
            G = -0.5 * J @ (D ** 2) @ J
            return float(np.linalg.eigvalsh(0.5 * (G + G.T)).min())

        assert gram_min_eig(grassmann_chordal_distance) > -1e-8, (
            "chordal distance should be of negative type (PSD Gram)"
        )
        assert gram_min_eig(grassmann_distance) < -1e-3, (
            "geodesic distance should NOT be of negative type"
        )
