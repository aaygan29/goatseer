"""ADR-017 verification for `discretize.py`: geometry-preserving tangent
discretization recovers a class difference that lives in covariance geometry.

The synthetic data has a known discriminative axis: class A covariances have
extra variance in channel 0, class B in channel 1. A discretization that
preserves the covariance geometry must produce states whose occupancy
separates the classes; the AIRM-prototype baseline (tested elsewhere) does
not.
"""

from __future__ import annotations

import numpy as np
import pytest

from neurospine.discretize import (
    SupervisedTangentDiscretizer,
    assign_states,
    discriminant_axis,
    quantile_edges,
)


def spd_for_class(cls: str, seed: int, n_ch: int = 4, n_samp: int = 200):
    rng = np.random.default_rng(seed)
    X = rng.standard_normal((n_ch, n_samp))
    if cls == "A":
        X[0] *= 3.0   # extra variance in channel 0
    else:
        X[1] *= 3.0   # extra variance in channel 1
    C = (X @ X.T) / (n_samp - 1)
    return C + 0.1 * np.eye(n_ch)


def make_dataset(n_per=40, seed=0):
    mats, labels = [], []
    for i in range(n_per):
        mats.append(spd_for_class("A", seed + i)); labels.append("A")
        mats.append(spd_for_class("B", seed + 1000 + i)); labels.append("B")
    return mats, labels


class TestHelpers:
    def test_discriminant_axis_is_unit(self) -> None:
        v = np.array([[0.0, 0.0], [2.0, 0.0], [0.0, 0.0], [-2.0, 0.0]])
        axis = discriminant_axis(v, ["A", "A", "B", "B"])
        assert np.isclose(np.linalg.norm(axis), 1.0)

    def test_discriminant_axis_points_along_mean_difference(self) -> None:
        # class A near +x, class B near -x -> axis along x.
        v = np.array([[3.0, 0.1], [2.5, -0.1], [-3.0, 0.0], [-2.6, 0.2]])
        axis = discriminant_axis(v, ["A", "A", "B", "B"])
        assert abs(axis[0]) > abs(axis[1])

    def test_quantile_edges_count_and_monotonic(self) -> None:
        edges = quantile_edges(np.arange(100.0), n_states=5)
        assert len(edges) == 4
        assert np.all(np.diff(edges) > 0)

    def test_assign_states_in_range(self) -> None:
        edges = quantile_edges(np.arange(100.0), n_states=4)
        states = assign_states(np.arange(100.0), edges)
        assert states.min() >= 0 and states.max() <= 3

    def test_discriminant_axis_requires_two_classes(self) -> None:
        with pytest.raises(ValueError):
            discriminant_axis(np.zeros((3, 2)), ["A", "A", "A"])


class TestSupervisedTangentDiscretizer:
    def test_states_separate_classes(self) -> None:
        mats, labels = make_dataset(n_per=40, seed=0)
        disc = SupervisedTangentDiscretizer.fit(mats, labels, n_states=5)
        states = disc.transform(mats)
        a = states[[i for i, y in enumerate(labels) if y == "A"]]
        b = states[[i for i, y in enumerate(labels) if y == "B"]]
        # The two classes occupy clearly different parts of the state axis.
        assert abs(a.mean() - b.mean()) > 1.0

    def test_occupancy_classifier_beats_chance(self) -> None:
        from neurospine.behavior import (
            evaluate_occupancy_model,
            fit_occupancy_model,
        )
        mats, labels = make_dataset(n_per=40, seed=1)
        disc = SupervisedTangentDiscretizer.fit(mats, labels, n_states=6)
        # Each matrix is a length-1 "sequence"; occupancy = which bin.
        seqs = [np.array([s]) for s in disc.transform(mats)]
        model = fit_occupancy_model(seqs, labels, n_states=6)
        acc = evaluate_occupancy_model(model, seqs, labels)["accuracy"]
        assert acc > 0.8

    def test_states_within_range(self) -> None:
        mats, labels = make_dataset(n_per=20, seed=2)
        disc = SupervisedTangentDiscretizer.fit(mats, labels, n_states=4)
        states = disc.transform(mats)
        assert states.min() >= 0 and states.max() <= 3

    def test_project_matches_transform_ordering(self) -> None:
        mats, labels = make_dataset(n_per=20, seed=3)
        disc = SupervisedTangentDiscretizer.fit(mats, labels, n_states=5)
        proj = disc.project(mats)
        states = disc.transform(mats)
        # Higher projection -> higher-or-equal state bin (monotone mapping).
        order = np.argsort(proj)
        assert np.all(np.diff(states[order]) >= 0)
