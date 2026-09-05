"""Behavior prediction from connectome-state trajectories.

This module fits a class-conditional Markov model over discrete neural
state sequences. It is intended for pipelines where neural recordings are
mapped to connectome states first, then behavior is predicted from the
trajectory dynamics.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import pairwise

import numpy as np


@dataclass(frozen=True)
class BehaviorMarkovModel:
    """Class-conditional Markov predictors over connectome states."""

    classes: tuple[str, ...]
    start_prob: np.ndarray  # (n_classes, n_states)
    trans_prob: np.ndarray  # (n_classes, n_states, n_states)
    n_states: int


def _validate_sequences(
    state_sequences: list[np.ndarray], labels: list[str], n_states: int
) -> None:
    if len(state_sequences) == 0:
        raise ValueError("state_sequences cannot be empty")
    if len(state_sequences) != len(labels):
        raise ValueError("state_sequences and labels must have same length")
    if n_states < 2:
        raise ValueError(f"n_states must be >= 2; got {n_states}")
    for i, seq in enumerate(state_sequences):
        if seq.ndim != 1:
            raise ValueError(f"sequence {i} must be 1D; got {seq.shape}")
        if len(seq) < 1:
            raise ValueError(f"sequence {i} must be non-empty")
        if np.any(seq < 0) or np.any(seq >= n_states):
            raise ValueError(f"sequence {i} has states outside [0, {n_states - 1}]")


def fit_behavior_markov_model(
    state_sequences: list[np.ndarray],
    labels: list[str],
    n_states: int,
    laplace: float = 1.0,
) -> BehaviorMarkovModel:
    """Fit class-conditional start and transition probabilities.

    Each behavior class gets its own Markov chain over the same discrete
    connectome-state alphabet.
    """
    _validate_sequences(state_sequences, labels, n_states)
    if laplace <= 0.0:
        raise ValueError(f"laplace must be > 0; got {laplace}")

    classes = tuple(sorted(set(labels)))
    n_classes = len(classes)
    idx = {c: i for i, c in enumerate(classes)}

    start = np.full((n_classes, n_states), laplace, dtype=float)
    trans = np.full((n_classes, n_states, n_states), laplace, dtype=float)

    for seq, label in zip(state_sequences, labels):
        ci = idx[label]
        start[ci, seq[0]] += 1.0
        for a, b in pairwise(seq):
            trans[ci, a, b] += 1.0

    start /= start.sum(axis=1, keepdims=True)
    trans /= trans.sum(axis=2, keepdims=True)

    return BehaviorMarkovModel(
        classes=classes,
        start_prob=start,
        trans_prob=trans,
        n_states=n_states,
    )


def class_log_likelihood(model: BehaviorMarkovModel, seq: np.ndarray) -> np.ndarray:
    """Log-likelihood of one state sequence under each behavior class."""
    if seq.ndim != 1 or len(seq) < 1:
        raise ValueError("seq must be a non-empty 1D array")
    if np.any(seq < 0) or np.any(seq >= model.n_states):
        raise ValueError(f"seq has states outside [0, {model.n_states - 1}]")

    log_start = np.log(model.start_prob)
    log_trans = np.log(model.trans_prob)

    out = np.zeros(len(model.classes), dtype=float)
    for ci in range(len(model.classes)):
        ll = log_start[ci, seq[0]]
        for a, b in pairwise(seq):
            ll += log_trans[ci, a, b]
        out[ci] = ll
    return out


def predict_behavior(model: BehaviorMarkovModel, seq: np.ndarray) -> str:
    """Predict behavior class from one connectome-state sequence."""
    ll = class_log_likelihood(model, seq)
    return model.classes[int(np.argmax(ll))]


def evaluate_behavior_markov_model(
    model: BehaviorMarkovModel,
    state_sequences: list[np.ndarray],
    labels: list[str],
) -> dict:
    """Evaluate accuracy and confusion table on labeled sequences."""
    if len(state_sequences) != len(labels):
        raise ValueError("state_sequences and labels must have same length")

    preds = [predict_behavior(model, s) for s in state_sequences]
    acc = float(np.mean([p == y for p, y in zip(preds, labels)])) if labels else 0.0

    confusion: dict[str, dict[str, int]] = {
        t: {p: 0 for p in model.classes} for t in model.classes
    }
    for y, p in zip(labels, preds):
        confusion[y][p] += 1

    return {
        "accuracy": acc,
        "n_samples": len(labels),
        "classes": list(model.classes),
        "confusion": confusion,
        "predictions": preds,
    }
