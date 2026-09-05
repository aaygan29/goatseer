"""ADR-019 verification for `sequence_decode.py`: transitions help when the
label sequence is temporally structured, and do not when labels are i.i.d.

The decisive property: on data where emissions overlap but the label
transitions are constrained (sticky), Viterbi (with transitions) must beat
the memoryless per-timestep argmax; on i.i.d. labels it must not.
"""

from __future__ import annotations

import numpy as np
import pytest

from neurospine.sequence_decode import (
    SupervisedSequenceDecoder,
    transition_gain,
)


def sticky_sequences(n_seq, T, sticky_p, overlap, seed):
    """Two classes with overlapping Gaussian emissions (mean +-1, std=overlap).
    `sticky_p` controls label autocorrelation: high = strong temporal
    structure the transition matrix can exploit."""
    rng = np.random.default_rng(seed)
    X_list, y_list = [], []
    for _ in range(n_seq):
        y = [int(rng.random() < 0.5)]
        for _ in range(T - 1):
            stay = rng.random() < sticky_p
            y.append(y[-1] if stay else 1 - y[-1])
        X = np.array([[rng.normal(1.0 if yi == 1 else -1.0, overlap)] for yi in y])
        X_list.append(X)
        y_list.append(np.array(y))
    return X_list, y_list


class TestFit:
    def test_requires_two_classes(self) -> None:
        with pytest.raises(ValueError):
            SupervisedSequenceDecoder.fit([np.zeros((3, 2))], [np.array([0, 0, 0])])

    def test_shapes(self) -> None:
        X, y = sticky_sequences(5, 20, 0.9, 0.8, seed=0)
        dec = SupervisedSequenceDecoder.fit(X, y)
        K = len(dec.classes)
        assert dec.means.shape[0] == K
        assert dec.log_trans.shape == (K, K)


class TestTransitionsHelpWhenTemporal:
    def test_viterbi_beats_memoryless_on_sticky_labels(self) -> None:
        # Emissions overlap heavily (std 1.2 vs mean-gap 2), so per-timestep
        # classification is weak; the sticky label structure rescues it.
        Xtr, ytr = sticky_sequences(30, 40, sticky_p=0.92, overlap=1.2, seed=1)
        Xte, yte = sticky_sequences(15, 40, sticky_p=0.92, overlap=1.2, seed=2)
        dec = SupervisedSequenceDecoder.fit(Xtr, ytr)
        g = transition_gain(dec, Xte, yte)
        assert g["transition_gain"] > 0.05
        assert g["accuracy_with_transitions"] > g["accuracy_without_transitions"]

    def test_no_gain_when_labels_iid(self) -> None:
        # sticky_p = 0.5 -> labels are i.i.d., transitions carry nothing.
        Xtr, ytr = sticky_sequences(30, 40, sticky_p=0.5, overlap=1.2, seed=3)
        Xte, yte = sticky_sequences(15, 40, sticky_p=0.5, overlap=1.2, seed=4)
        dec = SupervisedSequenceDecoder.fit(Xtr, ytr)
        g = transition_gain(dec, Xte, yte)
        assert g["transition_gain"] < 0.05


class TestDecodeContract:
    def test_decode_returns_labels(self) -> None:
        X, y = sticky_sequences(4, 10, 0.9, 0.6, seed=5)
        dec = SupervisedSequenceDecoder.fit(X, y)
        pred = dec.decode(X[0], use_transitions=True)
        assert len(pred) == len(y[0])
        assert set(pred).issubset(set(dec.classes))

    def test_perfectly_separable_scores_high_both_ways(self) -> None:
        # Non-overlapping emissions -> both decoders near perfect.
        X, y = sticky_sequences(10, 30, sticky_p=0.8, overlap=0.05, seed=6)
        dec = SupervisedSequenceDecoder.fit(X, y)
        assert dec.score(X, y, use_transitions=True) > 0.95
        assert dec.score(X, y, use_transitions=False) > 0.95
