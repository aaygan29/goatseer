"""Reproducible dataset access for NEUROSPINE.

Every experiment in this repo needs real public data, and until now each
one fetched its own inline (MNE `eegbci` here, nilearn `development_fmri`
there), with no single place recording where the data comes from, what its
license is, or how to swap in a new dataset. This module centralizes that.

Three things live here:

1. `DATASETS`: a provenance registry (id, role, license, fetch method,
   status) so every dataset the repo touches is documented in one place.
   Mirrors `data/README.md`.
2. Fetchers for the datasets the experiments already use, wrapping the
   MNE / nilearn auto-download so the fetch is one call with provenance,
   not copy-pasted boilerplate: `fetch_eegbci`, `fetch_development_fmri`.
3. `load_bids_eeg`: a generic BIDS-EEG adapter (ported from the
   cessation_manifold project) so ANY BIDS EEG dataset (LEMON, a future
   task dataset) can be loaded into the uniform `LoadedEEG` contract and
   fed to the pipeline. It raises loudly if the data has not been fetched,
   rather than silently falling back to nothing.

Heavy optional dependencies (mne, mne_bids, nilearn) are imported lazily
inside the functions that need them, so `import neurospine.io` is cheap
and dependency-light.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class DatasetInfo:
    """One row of dataset provenance."""

    dataset_id: str
    modality: str          # "eeg" | "fmri" | "atlas"
    role: str              # what the repo uses it for
    license: str
    fetch: str             # how to obtain it (function name or script)
    status: str            # "auto" (fetched on demand) | "script" | "not-public"
    url: str = ""


# The single source of truth for what data the repo touches. Kept in sync
# with data/README.md.
DATASETS = {
    "eegmmidb": DatasetInfo(
        dataset_id="eegmmidb",
        modality="eeg",
        role="EEG-BCI motor imagery; the covariance-trajectory and behavior "
             "experiments run on this.",
        license="Open Data Commons Attribution (PhysioNet); cite Schalk et "
                "al. 2004 and Goldberger et al. 2000.",
        fetch="fetch_eegbci()",
        status="auto",
        url="https://physionet.org/content/eegmmidb/1.0.0/",
    ),
    "development_fmri": DatasetInfo(
        dataset_id="development_fmri",
        modality="fmri",
        role="Naturalistic movie-watching fMRI (Pixar 'Partly Cloudy'); the "
             "connectome and effective-connectivity experiments run on this.",
        license="Open access via nilearn / OpenNeuro; cite Richardson et al. "
                "2018.",
        fetch="fetch_development_fmri()",
        status="auto",
        url="https://osf.io/5hju4/",
    ),
    "ds000221": DatasetInfo(
        dataset_id="ds000221",
        modality="eeg",
        role="MPI Leipzig LEMON resting EEG. Eyes-open vs eyes-closed is a "
             "real WITHIN-subject contrast (Berger effect), the substrate "
             "for the within-subject decoding line of work.",
        license="CC0-like MPI-CBS data use agreement; cite Babayan et al. 2019.",
        fetch="scripts/fetch_lemon_subset.sh, then load_bids_eeg()",
        status="script",
        url="https://openneuro.org/datasets/ds000221",
    ),
    "sleep_edfx": DatasetInfo(
        dataset_id="sleep_edfx",
        modality="eeg",
        role="PhysioNet Sleep-EDF Expanded: PSG + 30s hypnogram stages. A "
             "task with genuine temporal transition structure (W/N1/N2/N3/"
             "REM cycling), for the trajectory-model pivot (ADR-018/019).",
        license="Open Data Commons Attribution v1.0; cite Kemp et al. 2000 "
                "and Goldberger et al. 2000 (PhysioNet).",
        fetch="scripts/fetch_sleep_edfx_subset.sh, then read PSG+Hypnogram EDFs",
        status="script",
        url="https://physionet.org/content/sleep-edfx/1.0.0/",
    ),
    "schaefer_2018": DatasetInfo(
        dataset_id="schaefer_2018",
        modality="atlas",
        role="Cortical parcellation (100 parcels, 7 Yeo networks) for the "
             "connectome experiments.",
        license="MIT (nilearn atlas); cite Schaefer et al. 2018.",
        fetch="nilearn.datasets.fetch_atlas_schaefer_2018",
        status="auto",
        url="https://github.com/ThomasYeoLab/CBIG",
    ),
    "harvard_oxford": DatasetInfo(
        dataset_id="harvard_oxford",
        modality="atlas",
        role="Subcortical atlas (amygdala, thalamus, brainstem, hippocampus, "
             "striatum) augmenting the cortical parcellation.",
        license="FSL license (nilearn atlas); cite Makris et al. 2006.",
        fetch="nilearn.datasets.fetch_atlas_harvard_oxford",
        status="auto",
        url="https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/Atlases",
    ),
}


def describe_datasets() -> str:
    """One-line-per-dataset provenance summary."""
    lines = []
    for d in DATASETS.values():
        lines.append(f"{d.dataset_id} [{d.modality}, {d.status}] {d.role} "
                     f"({d.license})")
    return "\n".join(lines)


@dataclass
class LoadedEEG:
    """Uniform contract for loaded EEG, whatever the source dataset.

    `data` is (n_epochs, n_channels, n_samples) when epoched, or
    (n_channels, n_samples) for continuous. `labels`, when present, is one
    label per epoch.
    """

    data: "object"          # np.ndarray
    sfreq: float
    ch_names: list
    subject_id: str
    source: str
    session_id: str = "n/a"
    labels: list = field(default_factory=list)


def fetch_eegbci(subjects, runs=(4, 8)) -> dict:
    """Download PhysioNet EEG-BCI runs for the given subjects and return
    `{subject: [edf_path, ...]}`. Wraps `mne.datasets.eegbci.load_data`
    with `update_path=True`, the fetch the experiments already do inline.
    """
    from mne.datasets import eegbci

    out = {}
    for s in subjects:
        out[s] = list(
            eegbci.load_data(s, runs=list(runs), update_path=True, verbose="ERROR")
        )
    return out


def fetch_development_fmri(n_subjects: int = 5):
    """Fetch the nilearn development_fmri movie-watching dataset. Returns
    the nilearn Bunch (`.func`, `.confounds`)."""
    from nilearn.datasets import fetch_development_fmri

    return fetch_development_fmri(n_subjects=n_subjects)


def load_bids_eeg(
    bids_root: str,
    subject: str,
    task: str,
    session: str | None = None,
    epoch_length_s: float = 5.0,
    l_freq: float = 1.0,
    h_freq: float = 45.0,
    dataset_id: str = "unknown",
) -> LoadedEEG:
    """Load one subject/task from a local BIDS EEG dataset and epoch it.

    Raises `FileNotFoundError` with a clear message if the local data has
    not been fetched, rather than silently returning nothing. Ported from
    the cessation_manifold project's adapter so a new real EEG dataset is a
    config change, not a rewrite.
    """
    root = Path(bids_root)
    if not root.exists():
        raise FileNotFoundError(
            f"BIDS root {bids_root!r} does not exist. Run the fetch script "
            f"for dataset {dataset_id!r} (see data/README.md) before loading "
            "real data."
        )

    import mne
    from mne_bids import BIDSPath, read_raw_bids

    bids_path = BIDSPath(
        subject=subject, task=task, session=session, root=root, datatype="eeg"
    )
    raw = read_raw_bids(bids_path, verbose=False)
    raw.load_data()
    raw.filter(l_freq, h_freq, verbose=False)

    epochs = mne.make_fixed_length_epochs(
        raw, duration=epoch_length_s, preload=True, verbose=False
    )
    return LoadedEEG(
        data=epochs.get_data(),
        sfreq=float(raw.info["sfreq"]),
        ch_names=list(raw.ch_names),
        subject_id=subject,
        session_id=session or "n/a",
        source=dataset_id,
    )
