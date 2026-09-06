"""Verification tests for the pure helper functions in
experiments/decision_making_trajectory/run.py (band power, trial windowing,
unsupervised discretization). These are experiment-local helpers, not shared
package code, so tests live alongside the other verification tests but
import the experiment script directly.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "instrument" / "src"))


import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    "decision_trajectory_run",
    str(REPO_ROOT / "experiments" / "decision_making_trajectory" / "run.py"))
run = _ilu.module_from_spec(_spec)
try:
    _spec.loader.exec_module(run)
except Exception as _e:  # missing optional deps -> skip like importorskip did
    pytest.skip(f"cannot import decision run.py: {_e}", allow_module_level=True)


class TestBandPower:
    def test_pure_tone_concentrates_in_its_band(self) -> None:
        fs = 1000.0
        t = np.arange(int(fs)) / fs
        x = np.sin(2 * np.pi * 10.0 * t)  # 10 Hz -> alpha band (8-13 Hz)
        alpha = run.band_power(x, fs, 8, 13)
        theta = run.band_power(x, fs, 4, 8)
        assert alpha > 0.8
        assert theta < 0.1

    def test_short_window_returns_zero_not_nan(self) -> None:
        assert run.band_power(np.zeros(3), 1000.0, 4, 8) == 0.0


class TestTrialSequence:
    def test_shape_and_none_on_out_of_range(self) -> None:
        rng = np.random.default_rng(0)
        data = rng.normal(size=(3, 5000))
        seq = run.trial_sequence(data, 1000.0, 100, run.WIN_S, run.N_SUBWIN)
        assert seq.shape == (run.N_SUBWIN, 3 * len(run.BANDS))
        assert run.trial_sequence(data, 1000.0, 4900, run.WIN_S, run.N_SUBWIN) is None
        assert run.trial_sequence(data, 1000.0, -5, run.WIN_S, run.N_SUBWIN) is None


class TestDiscretizeSubject:
    def test_two_well_separated_clusters_recovered(self) -> None:
        rng = np.random.default_rng(1)
        # Two trials, each 5 sub-windows, feature dim 2; sub-windows alternate
        # between two well-separated feature clouds.
        seqs = []
        for _ in range(6):
            lo = rng.normal(loc=[-5, -5], scale=0.1, size=(3, 2))
            hi = rng.normal(loc=[5, 5], scale=0.1, size=(2, 2))
            seqs.append(np.vstack([lo, hi]))
        states = run.discretize_subject(seqs, n_states=2, seed=0)
        assert len(states) == 6
        for s in states:
            assert s.shape == (5,)
            assert set(np.unique(s)).issubset({0, 1})
            # first 3 sub-windows (lo cluster) share a state, distinct from
            # the last 2 (hi cluster).
            assert len(set(s[:3].tolist())) == 1
            assert len(set(s[3:].tolist())) == 1
            assert s[0] != s[3]

    def test_returns_one_sequence_per_trial_preserving_length(self) -> None:
        rng = np.random.default_rng(2)
        seqs = [rng.normal(size=(4, 3)) for _ in range(5)]
        states = run.discretize_subject(seqs, n_states=3, seed=0)
        assert len(states) == 5
        assert all(s.shape == (4,) for s in states)
