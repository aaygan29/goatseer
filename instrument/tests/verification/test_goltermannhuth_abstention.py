"""ADR-003 external re-verification for `GoltermannHuthAbstention`.

External anchor: Goltermann, Huth, Buchel (eLife 111743) BOLD-CMRO2
reanalysis. The paper reports two headline facts we use here as an
external check on the abstention logic:

1. Under a common BOLD-CMRO2 coupling assumption, 77.2 percent of
   voxels are unrobustly classified. Consequence: a decoder whose
   reliability is dominated by the unrobust majority of voxels
   should have `all_pass = False` on the triad in a realistic
   simulation.
2. CMRO2 variability is 127.8 percent higher than BOLD variability.
   Consequence: a synthetic CMRO2-scaled version of a BOLD signal
   with matched effect direction should produce a wider abstention
   interval than the BOLD version.

Tolerance justification: these are qualitative reproduction checks,
not point-estimate matches. The exact 77.2 percent number depends on
Goltermann's specific voxel definitions and cohort; we test the
weaker property that "a decoder built on unrobust voxels abstains"
and "wider variability implies wider interval." Full point-estimate
reproduction is queued in `issues_to_open.md` as a real-data
verification.
"""

from __future__ import annotations

import pytest

from neurospine.abstention import (
    GoltermannHuthAbstention,
    TriadResult,
    evaluate_triad,
    sign_concordance_binomial_p,
)


class TestSignConcordanceBinomial:
    def test_all_positive_significant(self) -> None:
        # 20 of 20 positive -> extremely unlikely under p=0.5
        p = sign_concordance_binomial_p(20, 20)
        assert p < 1e-5

    def test_half_positive_null(self) -> None:
        # 10 of 20 positive is exactly the null
        p = sign_concordance_binomial_p(10, 20)
        assert p == pytest.approx(1.0)

    def test_16_of_20_matches_known_value(self) -> None:
        # Known: two-sided binomial p for 16/20 vs p=0.5 is about 0.01182
        p = sign_concordance_binomial_p(16, 20)
        assert p == pytest.approx(0.01182, abs=1e-4)

    def test_edge_case_all_negative(self) -> None:
        p = sign_concordance_binomial_p(0, 20)
        assert p < 1e-5

    def test_invalid_inputs_raise(self) -> None:
        with pytest.raises(ValueError):
            sign_concordance_binomial_p(-1, 10)
        with pytest.raises(ValueError):
            sign_concordance_binomial_p(11, 10)
        with pytest.raises(ValueError):
            sign_concordance_binomial_p(0, 0)


class TestEvaluateTriad:
    def test_all_pass_case(self) -> None:
        # cortex-of-anyone example: 8 of 8 subjects positive, p=0.0039
        result = evaluate_triad(
            per_participant_cv_scores=[0.4] * 8,
            per_participant_directional_signs=[1] * 8,
            group_level_p=0.0039,
        )
        assert result.all_pass
        assert result.sign_concordance_p < 0.01
        assert result.g_fmri_1
        assert result.g_fmri_2
        assert result.g_fmri_3

    def test_null_concordance_fails_g2(self) -> None:
        # 4 positive of 8; not significant
        result = evaluate_triad(
            per_participant_cv_scores=[0.2] * 8,
            per_participant_directional_signs=[1, 1, 1, 1, -1, -1, -1, -1],
            group_level_p=0.5,
        )
        assert not result.g_fmri_2
        assert not result.all_pass

    def test_negative_cv_fails_g1(self) -> None:
        result = evaluate_triad(
            per_participant_cv_scores=[-0.1] * 10,
            per_participant_directional_signs=[1] * 10,
            group_level_p=0.01,
        )
        assert not result.g_fmri_1
        assert not result.all_pass

    def test_high_group_p_fails_g3(self) -> None:
        result = evaluate_triad(
            per_participant_cv_scores=[0.3] * 12,
            per_participant_directional_signs=[1] * 12,
            group_level_p=0.11,
        )
        assert not result.g_fmri_3
        assert not result.all_pass

    def test_empty_scores_raises(self) -> None:
        with pytest.raises(ValueError):
            evaluate_triad([], [1, 1], 0.01)
        with pytest.raises(ValueError):
            evaluate_triad([0.3], [], 0.01)


class TestGoltermannHuthAbstention:
    def test_abstains_when_triad_absent_for_fmri_dim(self) -> None:
        p = GoltermannHuthAbstention()
        assert p.should_abstain(
            "sub-01", {}, {}, "perceived_stimulus"
        ) is True

    def test_permits_when_triad_passes(self) -> None:
        triad = TriadResult(True, True, True, 0.4, 0.001, 0.001)
        p = GoltermannHuthAbstention(
            latest_triad={"perceived_stimulus": triad}
        )
        assert p.should_abstain(
            "sub-01", {}, {}, "perceived_stimulus"
        ) is False

    def test_abstains_when_any_triad_leg_fails(self) -> None:
        # G-fMRI.2 fails
        triad = TriadResult(True, False, True, 0.4, 0.3, 0.001)
        p = GoltermannHuthAbstention(
            latest_triad={"perceived_stimulus": triad}
        )
        assert p.should_abstain(
            "sub-01", {}, {}, "perceived_stimulus"
        ) is True

    def test_non_fmri_dim_ignores_triad(self) -> None:
        # No triad for predicted_decision, but it is not in the
        # fMRI-grounded set; the abstention rule falls through.
        p = GoltermannHuthAbstention(interval_width_by_dim={"predicted_decision": 0.1})
        assert p.should_abstain(
            "sub-01", {}, {}, "predicted_decision"
        ) is False

    def test_wide_interval_triggers_abstain(self) -> None:
        p = GoltermannHuthAbstention(
            interval_width_by_dim={"predicted_decision": 0.9},
            interval_width_threshold=0.5,
        )
        assert p.should_abstain(
            "sub-01", {}, {}, "predicted_decision"
        ) is True

    def test_motion_rejection_triggers_abstain(self) -> None:
        p = GoltermannHuthAbstention(
            motion_rejection_by_subject={"sub-01": 0.3},
            motion_rejection_threshold=0.2,
        )
        assert p.should_abstain(
            "sub-01", {}, {}, "predicted_decision"
        ) is True

    def test_goltermann_unrobust_majority_signal(self) -> None:
        """Qualitative reproduction: a decoder whose per-participant
        signs reflect the paper's 77.2 percent unrobust proportion
        (i.e. roughly 22.8 percent robust) will fail G-fMRI.2 unless
        the robust minority is unusually large."""
        n = 40
        robust_positive = round(n * 0.228)
        # Assume the unrobust majority contribute random signs; half positive.
        unrobust = n - robust_positive
        unrobust_positive = unrobust // 2
        positive = robust_positive + unrobust_positive
        signs = [1] * positive + [-1] * (n - positive)
        result = evaluate_triad(
            per_participant_cv_scores=[0.05] * n,
            per_participant_directional_signs=signs,
            group_level_p=0.20,
        )
        assert not result.g_fmri_2

    def test_goltermann_cmro2_wider_than_bold(self) -> None:
        """Qualitative reproduction: with CMRO2 variability 127.8
        percent higher than BOLD, an interval width proportional to
        that variability crosses the abstention threshold sooner
        under the CMRO2 assumption."""
        bold_width = 0.30
        cmro2_width = bold_width * 2.278  # 127.8 percent higher
        threshold = 0.50
        p_bold = GoltermannHuthAbstention(
            interval_width_by_dim={"perceived_stimulus": bold_width},
            interval_width_threshold=threshold,
            latest_triad={
                "perceived_stimulus": TriadResult(True, True, True, 0.4, 0.001, 0.001)
            },
        )
        p_cmro2 = GoltermannHuthAbstention(
            interval_width_by_dim={"perceived_stimulus": cmro2_width},
            interval_width_threshold=threshold,
            latest_triad={
                "perceived_stimulus": TriadResult(True, True, True, 0.4, 0.001, 0.001)
            },
        )
        assert not p_bold.should_abstain("s", {}, {}, "perceived_stimulus")
        assert p_cmro2.should_abstain("s", {}, {}, "perceived_stimulus")
