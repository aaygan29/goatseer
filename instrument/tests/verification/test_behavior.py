"""Verification tests for behavior prediction from connectome-state sequences."""

from __future__ import annotations

import numpy as np
import pytest
from neurospine.behavior import (
    class_log_likelihood,
    evaluate_behavior_markov_model,
    evaluate_occupancy_model,
    fit_behavior_markov_model,
    fit_occupancy_model,
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

    def test_rejects_empty_evaluation_sequences(self) -> None:
        seqs, labels = _make_separable_sequences(n=10)
        model = fit_behavior_markov_model(seqs, labels, n_states=4)
        with pytest.raises(ValueError):
            evaluate_behavior_markov_model(model, [], [])


class TestOccupancyAblation:
    """The occupancy (0th-order) baseline and the trajectory-vs-static
    discrimination it enables (correction to the 'trajectories predict
    behavior' claim; dynamics-vs-static confound, ADR-011/012)."""

    def _order_dependent_sequences(self, n=120, seed=0):
        # Two classes with IDENTICAL state occupancy but OPPOSITE order:
        # T1 goes 0->1->0->1..., T2 goes 1->0->1->0.... A bag-of-states
        # model cannot separate them; a Markov model can.
        rng = np.random.default_rng(seed)
        seqs, labels = [], []
        for _ in range(n):
            seqs.append(np.array([0, 1, 0, 1, 0, 1], dtype=int)); labels.append("T1")
            seqs.append(np.array([1, 0, 1, 0, 1, 0], dtype=int)); labels.append("T2")
        return seqs, labels

    def test_occupancy_cannot_separate_order_only_classes(self) -> None:
        seqs, labels = self._order_dependent_sequences()
        occ = fit_occupancy_model(seqs, labels, n_states=2)
        acc = evaluate_occupancy_model(occ, seqs, labels)["accuracy"]
        # Identical occupancy -> occupancy model is at chance.
        assert abs(acc - 0.5) < 0.1

    def test_markov_beats_occupancy_when_order_matters(self) -> None:
        seqs, labels = self._order_dependent_sequences()
        mk = fit_behavior_markov_model(seqs, labels, n_states=2)
        occ = fit_occupancy_model(seqs, labels, n_states=2)
        mk_acc = evaluate_behavior_markov_model(mk, seqs, labels)["accuracy"]
        occ_acc = evaluate_occupancy_model(occ, seqs, labels)["accuracy"]
        assert mk_acc > occ_acc + 0.3  # transitions carry the signal

    def test_occupancy_separates_occupancy_only_classes(self) -> None:
        # When classes DIFFER in occupancy, the occupancy model works, and
        # the Markov model should not claim extra credit.
        seqs, labels = _make_separable_sequences(n=80)
        occ = fit_occupancy_model(seqs, labels, n_states=4)
        assert evaluate_occupancy_model(occ, seqs, labels)["accuracy"] > 0.9


class TestReusableEngine:
    """analyze_state_sequences on generic data: the bring-your-own-data
    entry point. Verdict gated on BOTH the null and the occupancy baseline."""

    def _sticky_or_switch(self, sticky, rng, length=24):
        """A stochastic length-`length` binary chain. `sticky` classes stay
        in state (p=0.85); switch classes flip (p=0.85). Both have ~50/50
        state occupancy, so ONLY the transition structure separates them."""
        x = [int(rng.random() < 0.5)]
        for _ in range(length - 1):
            stay = rng.random() < (0.85 if sticky else 0.15)
            x.append(x[-1] if stay else 1 - x[-1])
        return np.array(x, dtype=int)

    def _many_subjects(self, order_matters, n_subj=12, per=14, seed=0):
        rng = np.random.default_rng(seed)
        seqs, labels, subjects = [], [], []
        for s in range(n_subj):
            for _ in range(per):
                if order_matters:
                    a = self._sticky_or_switch(True, rng)
                    b = self._sticky_or_switch(False, rng)
                else:
                    # differ in occupancy, not order (order is i.i.d.)
                    a = (rng.random(18) < 0.2).astype(int)
                    b = (rng.random(18) < 0.8).astype(int)
                seqs.append(a); labels.append("A"); subjects.append(s)
                seqs.append(b); labels.append("B"); subjects.append(s)
        return seqs, labels, subjects

    def test_transitions_beat_occupancy_when_order_carries_signal(self) -> None:
        # When only the transition structure separates the classes, the
        # Markov model must beat the occupancy baseline on held-out data.
        from neurospine.behavior import analyze_state_sequences
        seqs, labels, subj = self._many_subjects(order_matters=True)
        r = analyze_state_sequences(seqs, labels, subj, n_states=2,
                                    n_permutations=50, seed=0)
        assert r["occupancy_ablation"]["trajectory_gain"] > 0.1
        assert r["heldout_accuracy"] > r["occupancy_ablation"]["occupancy_accuracy"]

    def test_no_false_trajectory_claim_when_only_occupancy_matters(self) -> None:
        # Guardrail: when classes differ only in occupancy (order is i.i.d.),
        # the engine must NOT claim trajectories. Either it says occupancy,
        # or the transition gain is not positive.
        from neurospine.behavior import analyze_state_sequences
        seqs, labels, subj = self._many_subjects(order_matters=False)
        r = analyze_state_sequences(seqs, labels, subj, n_states=2,
                                    n_permutations=50, seed=0)
        assert r["occupancy_ablation"]["occupancy_accuracy"] > 0.8
        assert "TRAJECTOR" not in r["permutation_null"]["verdict"]

    def test_subject_disjoint_split_excludes_shared_subjects(self) -> None:
        from neurospine.behavior import subject_disjoint_split
        seqs = [np.array([0, 1]) for _ in range(8)]
        labels = ["A", "B"] * 4
        subj = [0, 0, 1, 1, 2, 2, 3, 3]
        sp = subject_disjoint_split(seqs, labels, subj, train_frac=0.5, seed=1)
        assert set(sp["train_subjects"]).isdisjoint(sp["test_subjects"])
