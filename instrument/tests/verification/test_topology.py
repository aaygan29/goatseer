"""ADR-003 verification for `topology.py`: Vietoris-Rips persistent
homology on point clouds with known Betti numbers.

The topology of the underlying manifold is known analytically for the
synthetic clouds below; a correct persistent-homology implementation
must recover it up to sampling artifacts. Tolerances are documented
per test.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from neurospine.topology import (
    PersistencePair,
    betti_curve,
    bottleneck_distance,
    pairwise_distances,
    vietoris_rips_h0,
    vietoris_rips_h1,
)


def unit_circle(n: int, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    theta = np.sort(rng.uniform(0.0, 2 * math.pi, n))
    return np.stack([np.cos(theta), np.sin(theta)], axis=1)


def two_circles(n_per: int = 20, sep: float = 5.0, seed: int = 1) -> np.ndarray:
    a = unit_circle(n_per, seed=seed)
    b = unit_circle(n_per, seed=seed + 1)
    b = b + np.array([sep, 0.0])
    return np.concatenate([a, b], axis=0)


class TestH0:
    def test_connected_cloud_has_one_essential_class(self) -> None:
        pts = unit_circle(30)
        D = pairwise_distances(pts)
        pairs = vietoris_rips_h0(D)
        essential = [p for p in pairs if p.death == float("inf")]
        assert len(essential) == 1
        finite = [p for p in pairs if p.death != float("inf")]
        # 30 points, one essential component, 29 finite deaths.
        assert len(finite) == 29

    def test_two_clusters_gives_two_long_bars(self) -> None:
        pts = two_circles(n_per=15, sep=10.0)
        D = pairwise_distances(pts)
        pairs = vietoris_rips_h0(D)
        # Sort by persistence descending.
        sorted_by_p = sorted(pairs, key=lambda p: -p.persistence)
        # Longest is the essential class (infinite); next-longest bar
        # corresponds to the merge of the two clusters and should be
        # much larger than the tiny within-cluster merges.
        finite_sorted = sorted(
            [p for p in pairs if p.death != float("inf")],
            key=lambda p: -p.persistence,
        )
        # The top finite persistence should exceed the mean of the rest
        # by a large multiple; conservative check:
        top = finite_sorted[0].persistence
        rest_max = finite_sorted[1].persistence
        assert top > 3 * rest_max


class TestH1:
    def test_circle_has_one_persistent_H1_class(self) -> None:
        pts = unit_circle(30, seed=42)
        D = pairwise_distances(pts)
        pairs_h0 = vietoris_rips_h0(D)
        pairs_h1 = vietoris_rips_h1(D, max_scale=float(D.max()))
        # The most persistent H1 class corresponds to the loop.
        persistent = sorted(pairs_h1, key=lambda p: -p.persistence)
        # There MAY be short-lived noise loops; we require the
        # dominant loop to be much longer than the others.
        assert persistent, "expected at least one H1 class"
        top = persistent[0]
        assert top.persistence > 0.5, (
            f"top H1 persistence too small: {top.persistence}"
        )
        # Optional shape check: shorter-than-top loops are noise
        if len(persistent) > 1:
            assert top.persistence > 3 * persistent[1].persistence, (
                f"top loop should dominate; got persistences "
                f"{[p.persistence for p in persistent[:5]]}"
            )

    def test_scattered_cloud_has_no_persistent_H1(self) -> None:
        rng = np.random.default_rng(43)
        pts = rng.standard_normal((20, 2))
        D = pairwise_distances(pts)
        pairs = vietoris_rips_h1(D, max_scale=float(D.max()))
        # There may be short-lived loops from sampling; none should
        # dominate.
        if pairs:
            max_persistence = max(p.persistence for p in pairs)
            # A scattered cloud has no true 1-cycle; the diameter of
            # random Gaussian samples is order 2-3 so require any
            # detected loop is small vs the diameter.
            assert max_persistence < 0.5 * float(D.max())


class TestBettiCurve:
    def test_betti_zero_at_zero_scale(self) -> None:
        pts = unit_circle(30)
        D = pairwise_distances(pts)
        pairs = vietoris_rips_h1(D, max_scale=float(D.max()))
        scales = np.array([0.0])
        b1 = betti_curve(pairs, scales, dimension=1)
        assert b1[0] == 0

    def test_betti_one_at_intermediate_scale_for_circle(self) -> None:
        pts = unit_circle(30)
        D = pairwise_distances(pts)
        pairs = vietoris_rips_h1(D, max_scale=float(D.max()))
        # Find a scale within the top persistent bar
        top = max(pairs, key=lambda p: p.persistence)
        mid = 0.5 * (top.birth + top.death)
        b1 = betti_curve(pairs, np.array([mid]), dimension=1)
        assert b1[0] >= 1


class TestBottleneckDistance:
    def test_identical_diagrams_zero_distance(self) -> None:
        pts = unit_circle(20)
        D = pairwise_distances(pts)
        p = vietoris_rips_h1(D)
        assert bottleneck_distance(p, p, dimension=1) == 0.0

    def test_symmetry(self) -> None:
        pts_a = unit_circle(20, seed=100)
        pts_b = unit_circle(20, seed=200)
        pa = vietoris_rips_h1(pairwise_distances(pts_a))
        pb = vietoris_rips_h1(pairwise_distances(pts_b))
        assert bottleneck_distance(pa, pb, dimension=1) == pytest.approx(
            bottleneck_distance(pb, pa, dimension=1)
        )

    def test_disjoint_shapes_nonzero(self) -> None:
        pts_a = unit_circle(20)
        pts_b = 5.0 * unit_circle(20, seed=999)  # scaled circle
        pa = vietoris_rips_h1(pairwise_distances(pts_a))
        pb = vietoris_rips_h1(pairwise_distances(pts_b))
        assert bottleneck_distance(pa, pb, dimension=1) > 0.5


class TestPersistencePair:
    def test_persistence_property(self) -> None:
        p = PersistencePair(dimension=1, birth=0.5, death=1.5)
        assert p.persistence == 1.0

    def test_infinite_death(self) -> None:
        p = PersistencePair(dimension=0, birth=0.0, death=float("inf"))
        assert math.isinf(p.persistence)
