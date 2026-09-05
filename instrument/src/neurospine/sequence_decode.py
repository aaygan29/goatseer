"""Supervised sequence decoding: does temporal structure carry signal? (ADR-019)

The motor-imagery arc closed with a lesson (ADR-018): a state-TRAJECTORY
model only earns its keep on a task whose discriminative signal is in the
temporal SEQUENCE, not a static per-epoch feature. This module is the
decisive test for that, reusable across tasks (sleep staging first, then
decision-making).

A `SupervisedSequenceDecoder` fits per-class Gaussian emissions plus a
class-transition matrix from labeled sequences, then decodes a held-out
sequence two ways:

- WITH transitions: Viterbi over emissions AND the transition matrix.
- WITHOUT transitions: independent per-timestep argmax of the emission
  likelihood (a memoryless classifier; equivalent to a uniform transition
  matrix).

If `accuracy(with) > accuracy(without)`, the temporal transition structure
carries decodable signal beyond the per-timestep features. That is exactly
the property motor imagery lacked and sleep staging is expected to have
(sleep-stage sequences are strongly constrained: you rarely jump W -> N3).

This is a supervised complement to the unsupervised Baum-Welch `GaussianHMM`
in `hmm.py`: here the states ARE the labels, emissions and transitions are
estimated directly from labeled data, and the transitions-on-vs-off contrast
is the readout.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def _gaussian_loglik(X: np.ndarray, mean: np.ndarray, cov: np.ndarray) -> np.ndarray:
    """Log N(x; mean, cov) for each row of X (T, d). Returns (T,)."""
    d = X.shape[1]
    sign, logdet = np.linalg.slogdet(cov)
    inv = np.linalg.inv(cov)
    diff = X - mean
    maha = np.einsum("ti,ij,tj->t", diff, inv, diff)
    return -0.5 * (d * np.log(2 * np.pi) + logdet + maha)


@dataclass
class SupervisedSequenceDecoder:
    """Per-class Gaussian emissions + a class-transition matrix, decoded with
    or without the transitions to test whether temporal structure helps."""

    classes: tuple
    means: np.ndarray          # (K, d)
    covs: np.ndarray           # (K, d, d)
    log_trans: np.ndarray      # (K, K), log P(next=j | cur=i)
    log_init: np.ndarray       # (K,)

    @classmethod
    def fit(cls, X_list: list, y_list: list, reg: float = 1e-2
            ) -> "SupervisedSequenceDecoder":
        """Fit from labeled sequences. `X_list[i]` is (T_i, d); `y_list[i]`
        is (T_i,) labels. Covariances are ridge-regularized for stability."""
        if len(X_list) != len(y_list):
            raise ValueError("X_list and y_list must have equal length")
        classes = tuple(sorted({y for ys in y_list for y in ys}))
        if len(classes) < 2:
            raise ValueError("need at least two classes")
        idx = {c: i for i, c in enumerate(classes)}
        K = len(classes)
        Xall = np.concatenate([np.asarray(X, float) for X in X_list], axis=0)
        yall = np.concatenate([np.asarray([idx[y] for y in ys]) for ys in y_list])
        d = Xall.shape[1]

        means = np.zeros((K, d))
        covs = np.zeros((K, d, d))
        for k in range(K):
            rows = Xall[yall == k]
            means[k] = rows.mean(axis=0)
            if len(rows) > 1:
                c = np.atleast_2d(np.cov(rows, rowvar=False))
            else:
                c = np.eye(d)
            covs[k] = c + reg * np.eye(d) * (np.trace(c) / d + 1e-9)

        trans = np.ones((K, K))  # Laplace
        init = np.ones(K)
        for ys in y_list:
            seq = [idx[y] for y in ys]
            init[seq[0]] += 1.0
            for a, b in zip(seq[:-1], seq[1:]):
                trans[a, b] += 1.0
        trans /= trans.sum(axis=1, keepdims=True)
        init /= init.sum()
        return cls(classes=classes, means=means, covs=covs,
                   log_trans=np.log(trans), log_init=np.log(init))

    def _emission_loglik(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, float)
        return np.stack([_gaussian_loglik(X, self.means[k], self.covs[k])
                         for k in range(len(self.classes))], axis=1)  # (T, K)

    def decode(self, X: np.ndarray, use_transitions: bool = True) -> list:
        """Return predicted labels for sequence X. With transitions: Viterbi.
        Without: per-timestep argmax of the emission likelihood."""
        E = self._emission_loglik(X)
        T, K = E.shape
        if not use_transitions:
            return [self.classes[int(k)] for k in E.argmax(axis=1)]
        delta = self.log_init + E[0]
        back = np.zeros((T, K), dtype=int)
        for t in range(1, T):
            scores = delta[:, None] + self.log_trans  # (K_prev, K_next)
            back[t] = scores.argmax(axis=0)
            delta = scores.max(axis=0) + E[t]
        path = [int(delta.argmax())]
        for t in range(T - 1, 0, -1):
            path.append(int(back[t][path[-1]]))
        path.reverse()
        return [self.classes[k] for k in path]

    def score(self, X_list: list, y_list: list, use_transitions: bool = True
              ) -> float:
        """Mean per-timestep accuracy over sequences."""
        correct = total = 0
        for X, ys in zip(X_list, y_list):
            pred = self.decode(X, use_transitions=use_transitions)
            correct += sum(p == y for p, y in zip(pred, ys))
            total += len(ys)
        return correct / total if total else 0.0


def transition_gain(decoder: "SupervisedSequenceDecoder", X_list, y_list) -> dict:
    """Accuracy with vs without transitions, and their difference. A positive
    gain means the temporal transition structure carries decodable signal."""
    with_t = decoder.score(X_list, y_list, use_transitions=True)
    without_t = decoder.score(X_list, y_list, use_transitions=False)
    return {"accuracy_with_transitions": with_t,
            "accuracy_without_transitions": without_t,
            "transition_gain": with_t - without_t}
