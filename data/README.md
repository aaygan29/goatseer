# Data

NEUROSPINE commits no raw data. Every dataset is fetched on demand, and
this file is the single provenance record: what each dataset is, what it is
used for, its license, and how to get it. The same registry lives in code
at `neurospine.io.DATASETS` (`instrument/src/neurospine/io/datasets.py`);
keep the two in sync.

Two ways data enters the repo:

- **auto**: fetched on first use by MNE or nilearn (no manual step). The
  fetchers in `neurospine.io` wrap these so a fetch is one documented call.
- **script**: a `scripts/fetch_*.sh` downloader (for datasets not served by
  a Python package), then loaded through `neurospine.io.load_bids_eeg`.

## Registry

| Dataset | Modality | Role | Fetch | License |
|---|---|---|---|---|
| `eegmmidb` (PhysioNet EEG-BCI) | EEG | Motor-imagery covariance-trajectory + behavior experiments | `neurospine.io.fetch_eegbci(subjects, runs)` (auto) | Open Data Commons Attribution; Schalk et al. 2004, Goldberger et al. 2000 |
| `development_fmri` (Partly Cloudy) | fMRI | Connectome + effective-connectivity experiments | `neurospine.io.fetch_development_fmri(n_subjects)` (auto) | Open access; Richardson et al. 2018 |
| `schaefer_2018` | atlas | Cortical parcellation (100 parcels, 7 networks) | `nilearn.datasets.fetch_atlas_schaefer_2018` (auto) | MIT; Schaefer et al. 2018 |
| `harvard_oxford` | atlas | Subcortical ROIs (amygdala, thalamus, brainstem, ...) | `nilearn.datasets.fetch_atlas_harvard_oxford` (auto) | FSL; Makris et al. 2006 |
| `ds000221` (MPI Leipzig LEMON) | EEG | Eyes-open vs eyes-closed WITHIN-subject contrast (Berger effect); substrate for within-subject decoding | `bash scripts/fetch_lemon_subset.sh` then `neurospine.io.load_bids_eeg` (script) | CC0-like MPI-CBS DUA; Babayan et al. 2019 |

## How to fetch

Auto datasets need no manual step. Run an experiment and MNE / nilearn
download on first use, or call the fetcher directly:

```python
from neurospine.io import fetch_eegbci, fetch_development_fmri, describe_datasets
print(describe_datasets())
paths = fetch_eegbci(subjects=[1, 2, 3], runs=(4, 8))   # PhysioNet EEG
dev = fetch_development_fmri(n_subjects=5)               # movie-watching fMRI
```

Script datasets download to `data/raw/<name>/` (gitignored):

```bash
bash scripts/fetch_lemon_subset.sh          # LEMON, ~600 MB for 2 subjects, ~2 min
```

```python
from neurospine.io import load_bids_eeg
eeg = load_bids_eeg("data/raw/lemon", subject="010002", task="RSEEG",
                    dataset_id="ds000221")
# eeg.data: (n_epochs, n_channels, n_samples); eeg.sfreq; eeg.ch_names
```

`load_bids_eeg` raises a clear `FileNotFoundError` if the data has not been
fetched, so a missing download never silently degrades an experiment.

Note on LEMON BIDS-readiness: the GWDG mirror serves raw BrainVision files,
not a full BIDS tree. To use the `mne-bids` path in `load_bids_eeg`, fetch
the OpenNeuro BIDS release of `ds000221`, or point a lighter loader at the
BrainVision files with `mne.io.read_raw_brainvision`.

## Storage

Fetched data lives under `data/raw/` and `~/mne_data` / `~/nilearn_data`,
all gitignored. Nothing here is committed.
