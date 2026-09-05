"""Smoke tests for the data-io layer (no network).

These verify the provenance registry, the LoadedEEG contract, and that the
BIDS loader fails loudly (not silently) when local data is missing. Actual
downloads are exercised by the experiments, not here.
"""

from __future__ import annotations

import numpy as np
import pytest

from neurospine.io import (
    DATASETS,
    DatasetInfo,
    LoadedEEG,
    describe_datasets,
    load_bids_eeg,
)


class TestRegistry:
    def test_registry_nonempty_and_typed(self) -> None:
        assert DATASETS
        for k, v in DATASETS.items():
            assert isinstance(v, DatasetInfo)
            assert v.dataset_id == k

    def test_every_dataset_has_required_provenance(self) -> None:
        for v in DATASETS.values():
            assert v.modality in {"eeg", "fmri", "atlas"}
            assert v.role and v.license and v.fetch
            assert v.status in {"auto", "script", "not-public"}

    def test_core_datasets_present(self) -> None:
        for did in ("eegmmidb", "development_fmri", "ds000221"):
            assert did in DATASETS

    def test_describe_is_one_line_per_dataset(self) -> None:
        text = describe_datasets()
        assert len(text.splitlines()) == len(DATASETS)


class TestLoadedEEGContract:
    def test_holds_fields(self) -> None:
        eeg = LoadedEEG(
            data=np.zeros((3, 4, 10)), sfreq=100.0,
            ch_names=["C3", "C4", "Cz", "Fz"], subject_id="01",
            source="unit-test", labels=["a", "b", "c"],
        )
        assert eeg.data.shape == (3, 4, 10)
        assert eeg.sfreq == 100.0
        assert eeg.session_id == "n/a"
        assert len(eeg.labels) == 3


class TestBidsLoaderFailsLoudly:
    def test_missing_root_raises_clear_error(self, tmp_path) -> None:
        missing = tmp_path / "does_not_exist"
        with pytest.raises(FileNotFoundError, match="fetch script"):
            load_bids_eeg(str(missing), subject="01", task="rest",
                          dataset_id="unit-test")
