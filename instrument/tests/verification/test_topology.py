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


class TestH1HardCases:
    """Regression tests for the H1 boundary-matrix reduction against
    spaces with analytically-known first Betti numbers. Added
    2026-09-04 after ADR-010 flagged the H1 reduction as unaudited.

    Each test pins the scale explicitly, because Vietoris-Rips
    persistence depends on the filtration scale: a loop that needs
    edges of length L to be filled will read as an essential
    (infinite-persistence) class at any max_scale < L. That is
    correct behavior, not a bug, so the tests choose scales where
    the expected homology is actually resolved.
    """

    @staticmethod
    def _circle(n, cx, cy, r, seed):
        rng = np.random.default_rng(seed)
        th = np.sort(rng.uniform(0.0, 2 * math.pi, n))
        return np.c_[cx + r * np.cos(th), cy + r * np.sin(th)]

    def test_single_circle_loop_has_finite_death_at_full_scale(self) -> None:
        """The canonical check the earlier suite missed: at a max_scale
        large enough to fill the loop, the H1 class must DIE (finite
        persistence), not persist to infinity. A reduction that fails
        to pair the loop with its filling 2-simplex would report
        infinite persistence here."""
        pts = self._circle(20, 0, 0, 1, seed=42)
        D = pairwise_distances(pts)
        h1 = vietoris_rips_h1(D, max_scale=float(D.max()))
        finite = [p for p in h1 if p.death != float("inf")]
        assert len(finite) >= 1, "loop must have a finite-death pair at full scale"
        top = max(finite, key=lambda p: p.persistence)
        # Born near the nearest-neighbour spacing, dies near the diameter.
        assert 0.0 < top.birth < top.death <= float(D.max()) + 1e-9

    def test_figure_eight_has_two_loops(self) -> None:
        """Two unit circles sharing a neighbourhood: b1 = 2."""
        c1 = self._circle(30, 0, 0, 1, seed=3)
        c2 = self._circle(30, 2.0, 0, 1, seed=4)
        pts = np.vstack([c1, c2])
        D = pairwise_distances(pts)
        h1 = vietoris_rips_h1(D, max_scale=float(D.max()))
        finite = sorted(
            [p for p in h1 if np.isfinite(p.persistence)],
            key=lambda p: -p.persistence,
        )
        assert len(finite) >= 2
        # The two dominant loops should both be substantial and the
        # third (if any) much smaller.
        assert finite[1].persistence > 0.5
        if len(finite) > 2:
            assert finite[1].persistence > 2 * finite[2].persistence
        # Betti-1 at a scale where both loops are alive.
        b1 = betti_curve(h1, np.array([0.9]), dimension=1)
        assert b1[0] == 2

    def test_two_disjoint_circles_betti_one_is_two(self) -> None:
        """Two well-separated circles with different samplings. The
        loops are born at different scales, so Betti-1 climbs to 2 only
        once both are born. This pins the scale where both are alive."""
        pts = np.vstack([
            self._circle(25, 0, 0, 1, seed=1),
            self._circle(25, 10, 0, 1, seed=2),
        ])
        D = pairwise_distances(pts)
        # Cap below the inter-circle gap so we do not build spurious
        # triangles spanning the two components.
        h1 = vietoris_rips_h1(D, max_scale=3.0)
        b1 = betti_curve(h1, np.array([1.3]), dimension=1)
        assert b1[0] == 2

    def test_filled_disk_has_no_dominant_loop(self) -> None:
        """A filled disk is contractible: no persistent H1. Any loops
        found are small sampling artifacts, none dominant."""
        rng = np.random.default_rng(9)
        pts = rng.uniform(-1, 1, (80, 2))
        pts = pts[np.linalg.norm(pts, axis=1) <= 1.0]
        D = pairwise_distances(pts)
        h1 = vietoris_rips_h1(D, max_scale=float(D.max()))
        if h1:
            top = max(p.persistence for p in h1 if np.isfinite(p.persistence))
            # No loop should persist more than a fraction of the diameter.
            assert top < 0.35 * float(D.max())
