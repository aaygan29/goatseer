"""Persistent-homology primitives on small point clouds.

The topological invariants of a subject's cognitive-state trajectory
(persistent homology, Betti curves, bottleneck distance between
persistence diagrams) are the primary substrate of A1 replicability
per ADR-008. Two sessions can differ pointwise and still be
topologically equivalent; that is the point.

This module implements Vietoris-Rips persistent homology in dimensions
0 and 1 from scratch, with a union-find for H0 and a boundary-matrix
reduction for H1. It handles the small point clouds (up to a few
hundred points) that NEUROSPINE's per-session trajectories produce
after temporal downsampling. Larger scans should delegate to `gudhi`
or `ripser`; the interface is stable enough to swap.

For dimensions >= 2 use a dedicated library. The Vietoris-Rips
complex grows combinatorially and pure Python is not the right tool
above H1.

References (external anchors):

- Edelsbrunner and Harer, "Computational Topology" (AMS, 2010).
- Chazal, de Silva, Glisse, Oudot, "The Structure and Stability of
  Persistence Modules" (Springer, 2016).
- arxiv-2512.08637 (Persistent homology pipeline for neural spike
  trains) and arxiv-2210.09092 (Dynamic TDA of functional brain
  networks) for NEUROSPINE-adjacent applications.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

import numpy as np


@dataclass(frozen=True)
class PersistencePair:
    """One (birth, death) pair from a persistence diagram.

    `birth` and `death` are filtration scales; `dimension` is the
    homology dimension (0 or 1 for this module).
    `float("inf")` in `death` marks an essential class.
    """

    dimension: int
    birth: float
    death: float

    @property
    def persistence(self) -> float:
        return self.death - self.birth


class _UnionFind:
    """Union-find with path compression + union-by-rank."""

    def __init__(self, n: int) -> None:
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def pairwise_distances(points: np.ndarray) -> np.ndarray:
    """Euclidean pairwise distance matrix. Shape `(n, n)`, symmetric,
    zero on the diagonal."""
    if points.ndim != 2:
        raise ValueError(
            f"points must be 2D (n, d); got shape {points.shape}"
        )
    diffs = points[:, None, :] - points[None, :, :]
    return np.linalg.norm(diffs, axis=-1)


def vietoris_rips_h0(distance_matrix: np.ndarray) -> list[PersistencePair]:
    """Persistent H0 (connected components) via union-find on the
    edge-sorted 1-skeleton. Returns one `PersistencePair` per finite-
    death component (born at 0, killed when merged) plus one essential
    class born at 0 and dying at infinity.
    """
    n = distance_matrix.shape[0]
    if distance_matrix.shape != (n, n):
        raise ValueError("distance_matrix must be square")

    # Sort edges by distance
    edges: list[tuple[float, int, int]] = []
    for i, j in combinations(range(n), 2):
        edges.append((float(distance_matrix[i, j]), i, j))
    edges.sort(key=lambda e: e[0])

    uf = _UnionFind(n)
    pairs: list[PersistencePair] = []
    for w, i, j in edges:
        if uf.union(i, j):
            # Two components merged at filtration w; younger dies.
            pairs.append(PersistencePair(dimension=0, birth=0.0, death=w))
    # One essential H0 class remains
    pairs.append(PersistencePair(dimension=0, birth=0.0, death=float("inf")))
    return pairs


def vietoris_rips_h1(
    distance_matrix: np.ndarray, max_scale: float | None = None
) -> list[PersistencePair]:
    """Persistent H1 (loops) via boundary-matrix reduction over the
    2-skeleton up to filtration `max_scale` (defaults to the diameter).

    This is O(m^3) in the number of simplices m and is intended for
    small clouds. For larger clouds delegate to `ripser` or `gudhi`.
    """
    n = distance_matrix.shape[0]
    if n < 3:
        return []
    if max_scale is None:
        max_scale = float(distance_matrix.max())

    # 1-simplices (edges) with their filtration values
    edges: list[tuple[float, tuple[int, int]]] = []
    for i, j in combinations(range(n), 2):
        d = float(distance_matrix[i, j])
        if d <= max_scale:
            edges.append((d, (i, j)))
    edges.sort(key=lambda e: (e[0], e[1]))

    # 2-simplices (triangles): filtration = max pairwise edge weight
    triangles: list[tuple[float, tuple[int, int, int]]] = []
    for i, j, k in combinations(range(n), 3):
        d = max(
            distance_matrix[i, j],
            distance_matrix[i, k],
            distance_matrix[j, k],
        )
        if d <= max_scale:
            triangles.append((float(d), (i, j, k)))
    triangles.sort(key=lambda t: (t[0], t[1]))

    # Simplex ordering: 0-simplices first, then edges, then triangles
    simplices: list[tuple[int, tuple, float]] = []
    idx_of: dict[tuple, int] = {}
    for v in range(n):
        idx_of[(v,)] = len(simplices)
        simplices.append((0, (v,), 0.0))
    for w, e in edges:
        idx_of[e] = len(simplices)
        simplices.append((1, e, w))
    for w, t in triangles:
        idx_of[t] = len(simplices)
        simplices.append((2, t, w))

    # Sort by (filtration, dimension) to ensure valid filtration order
    order = sorted(
        range(len(simplices)), key=lambda k: (simplices[k][2], simplices[k][0])
    )
    inv_order = [0] * len(order)
    for new, old in enumerate(order):
        inv_order[old] = new
    ordered_simplices = [simplices[i] for i in order]

    # Boundary columns
    columns: list[set[int]] = []
    for dim, verts, _ in ordered_simplices:
        col: set[int] = set()
        if dim == 1:
            i, j = verts
            col.add(inv_order[idx_of[(i,)]])
            col.add(inv_order[idx_of[(j,)]])
        elif dim == 2:
            i, j, k = verts
            col.add(inv_order[idx_of[(i, j)]])
            col.add(inv_order[idx_of[(i, k)]])
            col.add(inv_order[idx_of[(j, k)]])
        columns.append(col)

    # Standard column reduction
    low_to_col: dict[int, int] = {}
    pivots: list[int | None] = [None] * len(columns)
    for j, col in enumerate(columns):
        while col:
            low = max(col)
            if low in low_to_col:
                other = low_to_col[low]
                col ^= columns[other]
            else:
                low_to_col[low] = j
                pivots[j] = low
                break
        columns[j] = col

    # Extract H1 pairs: paired = birth in dim 1, death in dim 2
    pairs: list[PersistencePair] = []
    death_by_birth: dict[int, int] = {}
    for j, low in enumerate(pivots):
        if low is not None:
            death_by_birth[low] = j

    for i, (dim, _, w_birth) in enumerate(ordered_simplices):
        if dim != 1:
            continue
        if i not in death_by_birth:
            # Essential H1 class if no triangle killed it
            if pivots[i] is None:
                pairs.append(
                    PersistencePair(
                        dimension=1, birth=w_birth, death=float("inf")
                    )
                )
        else:
            j = death_by_birth[i]
            w_death = ordered_simplices[j][2]
            if w_death > w_birth:
                pairs.append(
                    PersistencePair(
                        dimension=1, birth=w_birth, death=w_death
                    )
                )
    return pairs


def bottleneck_distance(
    diagram_a: list[PersistencePair],
    diagram_b: list[PersistencePair],
    dimension: int = 1,
) -> float:
    """Approximate bottleneck distance between two persistence diagrams
    in one dimension. Uses a symmetric-difference greedy matching.

    Exact bottleneck distance is a bipartite optimization problem;
    this implementation is a Lipschitz-bounded surrogate suitable for
    within-subject vs across-subject comparison on small diagrams.
    Full-precision bottleneck should be computed via `persim` or
    `gudhi.bottleneck_distance` when available.
    """
    a = sorted(
        [p for p in diagram_a if p.dimension == dimension],
        key=lambda p: -p.persistence,
    )
    b = sorted(
        [p for p in diagram_b if p.dimension == dimension],
        key=lambda p: -p.persistence,
    )
    max_shift = 0.0
    for pa, pb in zip(a, b):
        shift = max(abs(pa.birth - pb.birth), abs(pa.death - pb.death))
        if shift > max_shift:
            max_shift = shift
    unmatched = a[len(b):] + b[len(a):]
    for p in unmatched:
        half_persist = 0.5 * p.persistence
        if half_persist > max_shift:
            max_shift = half_persist
    return float(max_shift)


def betti_curve(
    diagram: list[PersistencePair], scales: np.ndarray, dimension: int
) -> np.ndarray:
    """Betti number at each filtration scale for one homology
    dimension. Betti-k at scale s = number of pairs alive at s
    (birth <= s < death).
    """
    live = np.zeros_like(scales, dtype=int)
    for p in diagram:
        if p.dimension != dimension:
            continue
        alive = (scales >= p.birth) & (scales < p.death)
        live += alive.astype(int)
    return live
