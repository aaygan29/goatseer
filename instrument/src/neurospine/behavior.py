"""Behavior prediction from connectome-state trajectories.

This module fits a class-conditional Markov model over discrete neural
state sequences. It is intended for pipelines where neural recordings are
mapped to connectome states first, then behavior is predicted from the
trajectory dynamics.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


def _pairwise(seq):
    """Consecutive (a, b) pairs. Local helper because itertools.pairwise
    is Python 3.10+, and this repo runs on 3.9."""
    return zip(seq[:-1], seq[1:])


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
    """Fit class-conditional start/transition probabilities.

    Parameters
    ----------
    state_sequences:
        List of 1D integer arrays. Each array is one trial-level
        connectome-state trajectory with values in [0, n_states-1].
    labels:
        Behavior label per sequence. Must have same length as
        ``state_sequences``.
    n_states:
        Size of the shared discrete neural-state alphabet.
    laplace:
        Additive smoothing pseudo-count applied to start and transition
        counts in each class.

    Returns
    -------
    BehaviorMarkovModel
        ``classes`` sorted unique labels, ``start_prob`` with shape
        (n_classes, n_states), ``trans_prob`` with shape
        (n_classes, n_states, n_states), and ``n_states``.
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
        for a, b in _pairwise(seq):
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
        for a, b in _pairwise(seq):
            ll += log_trans[ci, a, b]
        out[ci] = ll
    return out


def predict_behavior(model: BehaviorMarkovModel, seq: np.ndarray) -> str:
    """Predict behavior class from one connectome-state sequence."""
    ll = class_log_likelihood(model, seq)
    return model.classes[int(np.argmax(ll))]


# --- Occupancy (0th-order) ablation -----------------------------------------
# A trajectory model earns the word "trajectory" only if its TRANSITION
# structure adds predictive power over the marginal state OCCUPANCY. This is
# the dynamics-vs-static control (the confound settled in ADR-011/012). The
# occupancy model below destroys temporal order: it scores each timepoint by
# its state's marginal class-conditional probability, ignoring transitions.
# The full Markov model must beat it on held-out data to justify a
# trajectory claim.

@dataclass(frozen=True)
class OccupancyModel:
    """Class-conditional marginal state-occupancy model (order-invariant)."""

    classes: tuple[str, ...]
    occupancy_prob: np.ndarray  # (n_classes, n_states)
    n_states: int


def fit_occupancy_model(
    state_sequences: list[np.ndarray],
    labels: list[str],
    n_states: int,
    laplace: float = 1.0,
) -> OccupancyModel:
    """Fit class-conditional marginal state distributions (bag of states)."""
    _validate_sequences(state_sequences, labels, n_states)
    if laplace <= 0.0:
        raise ValueError(f"laplace must be > 0; got {laplace}")
    classes = tuple(sorted(set(labels)))
    idx = {c: i for i, c in enumerate(classes)}
    occ = np.full((len(classes), n_states), laplace, dtype=float)
    for seq, label in zip(state_sequences, labels):
        ci = idx[label]
        for s in seq:
            occ[ci, int(s)] += 1.0
    occ /= occ.sum(axis=1, keepdims=True)
    return OccupancyModel(classes=classes, occupancy_prob=occ, n_states=n_states)


def occupancy_log_likelihood(model: OccupancyModel, seq: np.ndarray) -> np.ndarray:
    """Log-likelihood of a sequence under each class using only marginal
    state occupancy (order is irrelevant)."""
    if seq.ndim != 1 or len(seq) < 1:
        raise ValueError("seq must be a non-empty 1D array")
    if np.any(seq < 0) or np.any(seq >= model.n_states):
        raise ValueError(f"seq has states outside [0, {model.n_states - 1}]")
    log_occ = np.log(model.occupancy_prob)
    return np.array([sum(log_occ[ci, int(s)] for s in seq)
                     for ci in range(len(model.classes))])


def predict_occupancy(model: OccupancyModel, seq: np.ndarray) -> str:
    return model.classes[int(np.argmax(occupancy_log_likelihood(model, seq)))]


def evaluate_occupancy_model(
    model: OccupancyModel,
    state_sequences: list[np.ndarray],
    labels: list[str],
) -> dict:
    """Held-out accuracy of the occupancy baseline."""
    if len(state_sequences) != len(labels):
        raise ValueError("state_sequences and labels must have same length")
    preds = [predict_occupancy(model, s) for s in state_sequences]
    acc = float(np.mean([p == y for p, y in zip(preds, labels)])) if labels else 0.0
    return {"accuracy": acc, "n_samples": len(labels), "predictions": preds}


# --- Reusable, data-agnostic analysis engine --------------------------------
# Anyone with their own DISCRETE state sequences (from any modality: EEG,
# fMRI, MEG, pupil, behavior) can call this directly. The only contract is:
# a list of 1D integer arrays with values in [0, n_states-1], one behavior
# label per sequence, and a subject id per sequence so the split is
# subject-disjoint (no subject in both train and test).

def subject_disjoint_split(
    sequences: list,
    labels: list,
    subject_ids: list,
    train_frac: float = 0.7,
    seed: int = 0,
    max_tries: int = 256,
) -> dict:
    """Split by SUBJECT so no subject appears in both train and test, and
    both sides contain at least two classes. Returns index lists."""
    if not (0.0 < train_frac < 1.0):
        raise ValueError(f"train_frac must be in (0, 1); got {train_frac}")
    if not (len(sequences) == len(labels) == len(subject_ids)):
        raise ValueError("sequences, labels, subject_ids must be equal length")
    rng = np.random.default_rng(seed)
    unique = sorted(set(subject_ids))
    if len(unique) < 2:
        raise ValueError("need at least 2 subjects for a subject-disjoint split")
    n_train = min(max(1, int(train_frac * len(unique))), len(unique) - 1)
    for _ in range(max_tries):
        perm = list(unique)
        rng.shuffle(perm)
        train_subj = set(perm[:n_train])
        tr = [i for i, s in enumerate(subject_ids) if s in train_subj]
        te = [i for i, s in enumerate(subject_ids) if s not in train_subj]
        if len({labels[i] for i in tr}) >= 2 and len({labels[i] for i in te}) >= 2:
            return {
                "train_idx": tr, "test_idx": te,
                "train_subjects": sorted(train_subj),
                "test_subjects": sorted(set(unique) - train_subj),
            }
    raise ValueError(
        "could not find a subject-disjoint split with all classes on both "
        "sides; add more subjects or adjust train_frac"
    )


def analyze_state_sequences(
    sequences: list,
    labels: list,
    subject_ids: list,
    n_states: int,
    n_permutations: int = 200,
    train_frac: float = 0.7,
    seed: int = 0,
) -> dict:
    """Full behavior-from-state-sequence analysis on ANY discretized data.

    Runs a subject-disjoint split, fits the class-conditional Markov model
    and the occupancy (0th-order) baseline, evaluates held-out accuracy,
    computes a label-shuffle null, and returns a verdict that is gated on
    BOTH the null AND the occupancy baseline: a "trajectory" claim requires
    the transition structure to beat marginal state occupancy, not just the
    shuffle null (the dynamics-vs-static confound, ADR-011/012).

    Parameters
    ----------
    sequences : list of 1D int arrays, values in [0, n_states-1].
    labels : behavior label per sequence.
    subject_ids : subject id per sequence (drives the disjoint split).
    n_states : size of the shared discrete state alphabet.

    Returns a JSON-serializable dict of results.
    """
    if n_permutations < 1:
        raise ValueError(f"n_permutations must be >= 1; got {n_permutations}")
    seqs = [np.asarray(s, dtype=int) for s in sequences]
    split = subject_disjoint_split(seqs, labels, subject_ids, train_frac, seed)
    tr, te = split["train_idx"], split["test_idx"]
    x_tr, y_tr = [seqs[i] for i in tr], [labels[i] for i in tr]
    x_te, y_te = [seqs[i] for i in te], [labels[i] for i in te]

    model = fit_behavior_markov_model(x_tr, y_tr, n_states=n_states)
    observed = evaluate_behavior_markov_model(model, x_te, y_te)
    occ = fit_occupancy_model(x_tr, y_tr, n_states=n_states)
    occ_observed = evaluate_occupancy_model(occ, x_te, y_te)
    gain = observed["accuracy"] - occ_observed["accuracy"]

    rng = np.random.default_rng(seed)
    null = []
    y_perm = np.array(y_tr, dtype=object)
    for _ in range(n_permutations):
        rng.shuffle(y_perm)
        m = fit_behavior_markov_model(x_tr, y_perm.tolist(), n_states=n_states)
        null.append(evaluate_behavior_markov_model(m, x_te, y_te)["accuracy"])
    null = np.array(null, dtype=float)
    p = float((np.sum(null >= observed["accuracy"]) + 1) / (len(null) + 1))

    if p < 0.05 and gain > 0:
        verdict = ("state TRAJECTORIES predict behavior: above the shuffle "
                   "null AND above the occupancy baseline")
    elif p < 0.05:
        verdict = ("state OCCUPANCY predicts behavior (above null, but "
                   "transitions add nothing over occupancy)")
    else:
        verdict = "no evidence above shuffled-label null"

    return {
        "n_sequences": len(seqs),
        "n_states": n_states,
        "labels": sorted(set(labels)),
        "train_subjects": split["train_subjects"],
        "test_subjects": split["test_subjects"],
        "n_train": len(y_tr),
        "n_test": len(y_te),
        "heldout_accuracy": float(observed["accuracy"]),
        "heldout_confusion": observed["confusion"],
        "occupancy_ablation": {
            "occupancy_accuracy": float(occ_observed["accuracy"]),
            "markov_accuracy": float(observed["accuracy"]),
            "trajectory_gain": float(gain),
        },
        "permutation_null": {
            "n_permutations": n_permutations,
            "mean_accuracy": float(null.mean()),
            "std_accuracy": float(null.std(ddof=1)) if len(null) > 1 else 0.0,
            "p_value_right_tail": p,
            "verdict": verdict,
        },
    }


def evaluate_behavior_markov_model(
    model: BehaviorMarkovModel,
    state_sequences: list[np.ndarray],
    labels: list[str],
) -> dict:
    """Evaluate accuracy and confusion table on labeled sequences."""
    _validate_sequences(state_sequences, labels, model.n_states)

    unknown = sorted({y for y in labels if y not in model.classes})
    if unknown:
        raise ValueError(f"evaluation labels not in model classes: {unknown}")

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


# --- Within-subject decoding engine -----------------------------------------
# The cross-subject engine (analyze_state_sequences) returned an honest null:
# connectome-state trajectories did not predict motor imagery ACROSS subjects.
# The natural question is whether the signal is there WITHIN a subject, where
# the model does not have to generalize across anatomy. This engine trains and
# tests on the same subject (split across that subject's trials), per subject,
# then aggregates. It keeps the same discipline: an occupancy ablation and a
# per-subject label-shuffle null, and a group test over subjects.

def _stratified_trial_split(labels_idx, train_frac, rng):
    """Split trial indices into train/test, stratified by label, ensuring at
    least one train and one test trial per class. Returns (train, test) index
    lists, or None if a class has fewer than 2 trials."""
    by_class = {}
    for i, y in labels_idx:
        by_class.setdefault(y, []).append(i)
    train, test = [], []
    for y, idxs in by_class.items():
        if len(idxs) < 2:
            return None
        idxs = list(idxs)
        rng.shuffle(idxs)
        n_tr = max(1, min(len(idxs) - 1, int(round(train_frac * len(idxs)))))
        train.extend(idxs[:n_tr])
        test.extend(idxs[n_tr:])
    return train, test


def analyze_within_subject(
    sequences: list,
    labels: list,
    subject_ids: list,
    n_states: int,
    n_permutations: int = 200,
    train_frac: float = 0.6,
    seed: int = 0,
    min_trials_per_subject: int = 8,
) -> dict:
    """Within-subject behavior decoding from discrete state sequences.

    For each subject with enough trials and at least two classes, splits that
    subject's trials (stratified), fits the class-conditional Markov model and
    the occupancy baseline on the subject's train trials, evaluates held-out
    accuracy, and runs a per-subject label-shuffle null. Aggregates across
    subjects: how many individually beat their own null, the group binomial p
    for that count under a 5% per-subject false-positive rate, mean held-out
    accuracy, and mean trajectory gain (Markov minus occupancy).

    The verdict is gated the same way as the cross-subject engine: a
    "trajectory" claim needs the transitions to beat occupancy, not just the
    shuffle null (ADR-011/012).
    """
    if n_permutations < 1:
        raise ValueError(f"n_permutations must be >= 1; got {n_permutations}")
    seqs = [np.asarray(s, dtype=int) for s in sequences]
    subjects = sorted(set(subject_ids))

    per_subject = {}
    for subj in subjects:
        rng = np.random.default_rng(hash((seed, str(subj))) % (2**32))
        idx = [i for i in range(len(seqs)) if subject_ids[i] == subj]
        if len(idx) < min_trials_per_subject:
            continue
        if len({labels[i] for i in idx}) < 2:
            continue
        split = _stratified_trial_split([(i, labels[i]) for i in idx],
                                        train_frac, rng)
        if split is None:
            continue
        tr, te = split
        if len({labels[i] for i in tr}) < 2 or len({labels[i] for i in te}) < 2:
            continue
        x_tr, y_tr = [seqs[i] for i in tr], [labels[i] for i in tr]
        x_te, y_te = [seqs[i] for i in te], [labels[i] for i in te]

        model = fit_behavior_markov_model(x_tr, y_tr, n_states=n_states)
        acc = evaluate_behavior_markov_model(model, x_te, y_te)["accuracy"]
        occ = fit_occupancy_model(x_tr, y_tr, n_states=n_states)
        occ_acc = evaluate_occupancy_model(occ, x_te, y_te)["accuracy"]

        null = []
        y_perm = np.array(y_tr, dtype=object)
        for _ in range(n_permutations):
            rng.shuffle(y_perm)
            m = fit_behavior_markov_model(x_tr, y_perm.tolist(), n_states=n_states)
            null.append(evaluate_behavior_markov_model(m, x_te, y_te)["accuracy"])
        null = np.array(null, dtype=float)
        p = float((np.sum(null >= acc) + 1) / (len(null) + 1))
        per_subject[str(subj)] = {
            "heldout_accuracy": float(acc),
            "occupancy_accuracy": float(occ_acc),
            "trajectory_gain": float(acc - occ_acc),
            "p_value": p,
            "n_train": len(y_tr),
            "n_test": len(y_te),
        }

    n = len(per_subject)
    if n == 0:
        raise ValueError(
            "no subject had enough trials / both classes on each split; "
            "lower min_trials_per_subject or supply more trials"
        )
    accs = [r["heldout_accuracy"] for r in per_subject.values()]
    gains = [r["trajectory_gain"] for r in per_subject.values()]
    n_sig = sum(1 for r in per_subject.values() if r["p_value"] < 0.05)
    # Group binomial: P(>= n_sig of n subjects significant) under a 5%
    # per-subject false-positive rate. Small p means the hit rate exceeds
    # chance across the cohort.
    from math import comb
    group_p = float(sum(comb(n, k) * 0.05**k * 0.95**(n - k)
                        for k in range(n_sig, n + 1)))
    mean_gain = float(np.mean(gains))

    if group_p < 0.05 and mean_gain > 0:
        verdict = ("within-subject: state TRAJECTORIES predict behavior "
                   "(cohort hit-rate above chance AND transitions beat "
                   "occupancy)")
    elif group_p < 0.05:
        verdict = ("within-subject: state OCCUPANCY predicts behavior "
                   "(cohort above chance, but transitions add nothing over "
                   "occupancy)")
    else:
        verdict = "within-subject: no evidence above per-subject nulls"

    return {
        "n_subjects": n,
        "mean_heldout_accuracy": float(np.mean(accs)),
        "n_subjects_significant": n_sig,
        "group_binomial_p": group_p,
        "mean_trajectory_gain": mean_gain,
        "per_subject": per_subject,
        "verdict": verdict,
    }
