"""Verification tests for behavior prediction from connectome-state sequences."""

from __future__ import annotations

import numpy as np
import pytest
from neurospine.behavior import (
    class_log_likelihood,
    evaluate_behavior_markov_model,
    fit_behavior_markov_model,
    predict_behavior,
)


def _make_separable_sequences(n: int = 80, seed: int = 0):
    rng = np.random.default_rng(seed)
    seqs: list[np.ndarray] = []
    labels: list[str] = []

    # Class "T1" stays mostly in low-index states 0/1.
    for _ in range(n):
        x = [0]
        for _ in range(5):
            nxt = 0 if rng.random() < 0.7 else 1
            x.append(nxt)
        seqs.append(np.array(x, dtype=int))
        labels.append("T1")

    # Class "T2" stays mostly in high-index states 2/3.
    for _ in range(n):
        x = [3]
        for _ in range(5):
            nxt = 3 if rng.random() < 0.7 else 2
            x.append(nxt)
        seqs.append(np.array(x, dtype=int))
        labels.append("T2")

    return seqs, labels


class TestBehaviorMarkovModel:
    def test_row_stochastic_parameters(self) -> None:
        seqs, labels = _make_separable_sequences(n=20)
        model = fit_behavior_markov_model(seqs, labels, n_states=4)
        assert np.allclose(model.start_prob.sum(axis=1), 1.0, atol=1e-10)
        assert np.allclose(model.trans_prob.sum(axis=2), 1.0, atol=1e-10)

    def test_predicts_behavior_from_state_trajectory(self) -> None:
        seqs, labels = _make_separable_sequences(n=80)
        model = fit_behavior_markov_model(seqs, labels, n_states=4)
        metrics = evaluate_behavior_markov_model(model, seqs, labels)
        assert metrics["accuracy"] > 0.9

    def test_loglik_prefers_matching_class(self) -> None:
        seqs, labels = _make_separable_sequences(n=30)
        model = fit_behavior_markov_model(seqs, labels, n_states=4)
        ll = class_log_likelihood(model, np.array([0, 0, 1, 0, 1], dtype=int))
        pred = model.classes[int(np.argmax(ll))]
        assert pred == "T1"

    def test_rejects_out_of_range_state(self) -> None:
        seqs, labels = _make_separable_sequences(n=10)
        model = fit_behavior_markov_model(seqs, labels, n_states=4)
        with pytest.raises(ValueError):
            predict_behavior(model, np.array([0, 1, 4], dtype=int))

    def test_rejects_mismatched_input_lengths(self) -> None:
        with pytest.raises(ValueError):
            fit_behavior_markov_model([np.array([0, 1], dtype=int)], [], n_states=3)

    def test_rejects_unknown_evaluation_label(self) -> None:
        seqs, labels = _make_separable_sequences(n=10)
        model = fit_behavior_markov_model(seqs, labels, n_states=4)
        with pytest.raises(ValueError):
            evaluate_behavior_markov_model(model, [np.array([0, 1, 0], dtype=int)], ["X"])
