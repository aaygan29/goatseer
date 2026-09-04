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
