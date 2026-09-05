"""Build an AUGMENTED cortico-subcortical connectome (ADR-014).

The cortex-only connectome omits the threat circuit. This adds the
subcortical hubs (amygdala, thalamus, brainstem, hippocampus, striatum)
from the Harvard-Oxford subcortical atlas to the Schaefer cortical
parcels, computing functional connectivity over the combined set from
the same resting-state data.

Public data: Schaefer 2018 (cortex, 7-network labels), Harvard-Oxford
subcortical maxprob (Makris 2006 / Frazier 2005 / Desikan 2006), nilearn
development_fmri.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import numpy as np

# Subcortical grey-matter ROIs to keep (skip WM, ventricles, cortex, bg).
SUBCORTICAL_KEEP = [
    "Thalamus", "Caudate", "Putamen", "Pallidum",
    "Brain-Stem", "Hippocampus", "Amygdala", "Accumbens",
]


def yeo_network_of(label: str) -> str:
    s = label.decode() if isinstance(label, bytes) else str(label)
    m = re.search(r"(?:LH|RH)_([A-Za-z]+)", s)
    return m.group(1) if m else "Unknown"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-subjects", type=int, default=40)
    ap.add_argument("--n-rois", type=int, default=100)
    ap.add_argument("--out", type=Path,
                    default=Path(__file__).parent / "results" / "connectome_augmented.npz")
    args = ap.parse_args()

    from nilearn.connectome import ConnectivityMeasure
    from nilearn.datasets import (
        fetch_atlas_harvard_oxford,
        fetch_atlas_schaefer_2018,
        fetch_development_fmri,
    )
    from nilearn.maskers import NiftiLabelsMasker

    print(f"[aug] fetching Schaefer-{args.n_rois} (cortex) + Harvard-Oxford (subcortex)")
    cortex = fetch_atlas_schaefer_2018(n_rois=args.n_rois, yeo_networks=7, resolution_mm=2)
    subcort = fetch_atlas_harvard_oxford("sub-maxprob-thr25-2mm")

    cortex_labels = [str(l) for l in cortex.labels]
    cortex_networks = [yeo_network_of(l) for l in cortex.labels]
    # Drop the Schaefer background label if present.
    if cortex_labels and "Background" in cortex_labels[0]:
        cortex_labels = cortex_labels[1:]
        cortex_networks = cortex_networks[1:]

    sub_labels_all = [str(l) for l in subcort.labels]
    keep_idx = [
        i for i, l in enumerate(sub_labels_all)
        if any(k.lower() in l.lower() for k in SUBCORTICAL_KEEP)
    ]
    sub_labels = [sub_labels_all[i] for i in keep_idx]
    sub_networks = ["Subcortex"] * len(sub_labels)
    print(f"[aug] cortex parcels: {len(cortex_labels)}, subcortical ROIs kept: "
          f"{len(sub_labels)} -> {sub_labels}")

    print(f"[aug] fetching development_fmri (n={args.n_subjects})")
    dev = fetch_development_fmri(n_subjects=args.n_subjects)

    m_cortex = NiftiLabelsMasker(labels_img=cortex.maps, standardize="zscore_sample", verbose=0)
    # For the subcortical maxprob atlas, mask all labels then select kept columns.
    m_sub = NiftiLabelsMasker(labels_img=subcort.maps, standardize="zscore_sample", verbose=0)
    conn = ConnectivityMeasure(kind="correlation")

    fcs = []
    for i, (func, conf) in enumerate(zip(dev.func, dev.confounds)):
        ts_c = m_cortex.fit_transform(func, confounds=conf)
        ts_s_all = m_sub.fit_transform(func, confounds=conf)
        # Columns of ts_s_all correspond to m_sub.labels_ (the integer
        # region labels present, in column order). In the Harvard-Oxford
        # maxprob atlas the labels-list position equals the voxel integer
        # label, so keep_idx ARE the integer labels to keep. Select the
        # columns whose integer label is in keep_idx.
        # Column c corresponds to voxel integer label (c+1); keep_idx are
        # the label-list positions == voxel integer labels, so the column
        # is keep_idx minus one. Background (0) is never in keep_idx.
        cols = [i - 1 for i in keep_idx if 0 < i <= ts_s_all.shape[1]]
        ts_s = ts_s_all[:, cols]
        ts = np.hstack([ts_c, ts_s])
        fcs.append(conn.fit_transform([ts])[0])
        if (i + 1) % 10 == 0:
            print(f"[aug]   {i + 1}/{args.n_subjects} subjects")

    group_fc = np.mean(fcs, axis=0)
    np.fill_diagonal(group_fc, 0.0)
    networks = np.array(cortex_networks + sub_networks)
    labels = np.array(cortex_labels + sub_labels)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(args.out, fc=group_fc, networks=networks, labels=labels,
             n_cortex=len(cortex_labels), n_subcortex=len(sub_labels))
    print(f"[aug] wrote {args.out}  (FC {group_fc.shape}, "
          f"{len(cortex_labels)} cortical + {len(sub_labels)} subcortical)")


if __name__ == "__main__":
    main()
