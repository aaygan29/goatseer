"""Build a region-level brain connectome from a real public atlas and
real resting-state fMRI, for the anatomical thought-propagation model
(ADR-013).

This is the correction to the anatomy-free error: the transition kernel
must live on brain regions, not on abstract EEG covariance prototypes.

Pipeline:
1. Fetch the Schaefer 2018 atlas (100 parcels, 7-network Yeo labels).
   Public, published (Schaefer et al., Cerebral Cortex 2018).
2. Fetch nilearn development_fmri resting-state data (public).
3. Extract per-parcel timeseries, compute per-subject correlation FC,
   average to a group connectome.
4. Save the connectome, the parcel-to-Yeo-network map, and parcel names.

Output: results/connectome.npz with {fc, networks, labels}.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import numpy as np


def yeo_network_of(label: str) -> str:
    """Extract the 7-network Yeo affiliation from a Schaefer parcel name
    like '7Networks_LH_Vis_1' -> 'Vis'."""
    s = label.decode() if isinstance(label, bytes) else str(label)
    m = re.search(r"(?:LH|RH)_([A-Za-z]+)", s)
    return m.group(1) if m else "Unknown"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-subjects", type=int, default=40)
    ap.add_argument("--n-rois", type=int, default=100)
    ap.add_argument("--out", type=Path,
                    default=Path(__file__).parent / "results" / "connectome.npz")
    args = ap.parse_args()

    from nilearn.connectome import ConnectivityMeasure
    from nilearn.datasets import fetch_atlas_schaefer_2018, fetch_development_fmri
    from nilearn.maskers import NiftiLabelsMasker

    print(f"[connectome] fetching Schaefer-{args.n_rois} atlas (7 networks)")
    atlas = fetch_atlas_schaefer_2018(
        n_rois=args.n_rois, yeo_networks=7, resolution_mm=2
    )
    labels = atlas.labels
    networks = np.array([yeo_network_of(l) for l in labels])
    print(f"[connectome] networks present: {sorted(set(networks))}")

    print(f"[connectome] fetching development_fmri (n={args.n_subjects})")
    dev = fetch_development_fmri(n_subjects=args.n_subjects)

    masker = NiftiLabelsMasker(
        labels_img=atlas.maps, standardize="zscore_sample", verbose=0
    )
    conn = ConnectivityMeasure(kind="correlation")

    fcs = []
    for i, (func, conf) in enumerate(zip(dev.func, dev.confounds)):
        ts = masker.fit_transform(func, confounds=conf)
        fc = conn.fit_transform([ts])[0]
        fcs.append(fc)
        if (i + 1) % 10 == 0:
            print(f"[connectome]   {i + 1}/{args.n_subjects} subjects")

    group_fc = np.mean(fcs, axis=0)
    np.fill_diagonal(group_fc, 0.0)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        args.out,
        fc=group_fc,
        networks=networks,
        labels=np.array([str(l) for l in labels]),
        n_subjects=args.n_subjects,
    )
    print(f"[connectome] wrote {args.out}  (FC shape {group_fc.shape})")


if __name__ == "__main__":
    main()
