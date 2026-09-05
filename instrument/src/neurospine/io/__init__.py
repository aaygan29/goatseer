"""Reproducible dataset access: provenance registry, fetchers, and a
generic BIDS-EEG loader. See `datasets.py` and `data/README.md`."""

from .datasets import (
    DATASETS,
    DatasetInfo,
    LoadedEEG,
    describe_datasets,
    fetch_adhd,
    fetch_development_fmri,
    fetch_eegbci,
    load_bids_eeg,
)

__all__ = [
    "DATASETS",
    "DatasetInfo",
    "LoadedEEG",
    "describe_datasets",
    "fetch_adhd",
    "fetch_development_fmri",
    "fetch_eegbci",
    "load_bids_eeg",
]
