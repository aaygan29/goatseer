"""Smoke tests for the clinical_state_dynamics experiment helpers.

The experiment (`experiments/clinical_state_dynamics/run.py`) composes
existing, already-tested `neurospine.dynamics` primitives; these tests
cover its own new helper functions on synthetic data: the motion-proxy
computation, OLS residualization, the permutation test, and Cohen's d.
No network access or real ADHD-200 data is needed.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "experiments" / "clinical_state_dynamics"))

from run import cohens_d, mean_fd_from_confounds, permutation_test, residualize  # noqa: E402


def test_mean_fd_from_confounds(tmp_path: Path) -> None:
    # Six-column motion confound file: three translations (mm), three
    # rotations (rad). A single 1mm jump in one translation column at
    # one timepoint should give a known mean FD.
    n = 10
    motion = np.zeros((n, 6))
    motion[5, 0] = 1.0  # step of 1mm at t=5 -> |diff|=1 at that frame
    df = pd.DataFrame(motion, columns=["X", "Y", "Z", "RotX", "RotY", "RotZ"])
    path = tmp_path / "confounds.tsv"
    df.to_csv(path, sep="\t", index=False)

    fd = mean_fd_from_confounds(str(path))
    # 9 frame-to-frame diffs; the single-frame 1mm spike creates two
    # non-zero diffs (rise then fall), each magnitude 1.0; mean = 2/9.
    assert fd == pytest.approx(2.0 / 9, abs=1e-9)


def test_residualize_removes_linear_site_and_motion_effect() -> None:
    rng = np.random.default_rng(0)
    n = 60
    site = rng.choice(["A", "B", "C"], size=n)
    site_effect = {"A": 0.0, "B": 5.0, "C": -3.0}
    mean_fd = rng.uniform(0.05, 0.5, size=n)
    y = (
        np.array([site_effect[s] for s in site])
        + 2.0 * mean_fd
        + rng.normal(scale=0.01, size=n)
    )
    resid = residualize(y, site, mean_fd)
    # After removing the site + motion linear effect, residual variance
    # should collapse to roughly the noise floor.
    assert resid.std() < 0.2
    # And the residual should no longer correlate strongly with motion.
    assert abs(np.corrcoef(resid, mean_fd)[0, 1]) < 0.3


def test_permutation_test_null_true_no_effect() -> None:
    rng = np.random.default_rng(1)
    n = 80
    values = rng.normal(size=n)  # no true group effect
    group = np.array([1] * (n // 2) + [0] * (n // 2))
    obs, p = permutation_test(values, group, site=None, n_perm=2000, rng=rng)
    assert -0.5 < obs < 0.5
    assert p > 0.05  # should not falsely reject under the true null


def test_permutation_test_detects_real_effect() -> None:
    rng = np.random.default_rng(2)
    n = 80
    group = np.array([1] * (n // 2) + [0] * (n // 2))
    values = rng.normal(size=n) + group * 3.0  # large true effect
    obs, p = permutation_test(values, group, site=None, n_perm=2000, rng=rng)
    assert obs > 1.0
    assert p < 0.01


def test_permutation_test_stratified_by_site() -> None:
    rng = np.random.default_rng(3)
    n = 90
    site = np.array(["A"] * 30 + ["B"] * 30 + ["C"] * 30)
    group = rng.integers(0, 2, size=n)
    values = rng.normal(size=n)
    obs, p = permutation_test(values, group, site=site, n_perm=1000, rng=rng)
    assert isinstance(obs, float)
    assert 0.0 <= p <= 1.0


def test_cohens_d_known_effect() -> None:
    group = np.array([1] * 50 + [0] * 50)
    rng = np.random.default_rng(4)
    values = np.concatenate(
        [rng.normal(1.0, 1.0, size=50), rng.normal(0.0, 1.0, size=50)]
    )
    d = cohens_d(values, group)
    assert 0.5 < d < 1.5  # true effect is d=1, allow sampling slack


def test_cohens_d_zero_when_identical_groups() -> None:
    group = np.array([1, 1, 0, 0])
    values = np.array([1.0, 1.0, 1.0, 1.0])
    assert cohens_d(values, group) == pytest.approx(0.0)
