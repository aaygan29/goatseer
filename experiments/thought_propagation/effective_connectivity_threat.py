"""Data-derived effective connectivity for the threat circuit (ADR-016).

ADR-015 assumed the sign of the prefrontal -> amygdala edge (inhibitory).
This experiment ESTIMATES the signed directed edges from real fMRI
(nilearn development_fmri, the Pixar "Partly Cloudy" naturalistic
paradigm, which carries affective/social content) over the same augmented
cortico-subcortical atlas as ADR-014, using ridge-VAR(1) effective
connectivity.

The headline question is empirical, not assumed: what sign does the data
assign to prefrontal (control network) -> amygdala influence, and how
consistent is it across subjects? The regulation prediction from ADR-015
is only data-supported if that edge is estimated inhibitory.

Honest scope: naturalistic movie-watching is NOT a fear-conditioning or
emotion-regulation task, VAR(1) on fMRI is confounded by hemodynamics and
TR (Seth/Barrett/Barnett 2015), and the group is small. The deliverable
is the METHOD (data replaces literature priors) plus whatever the data
actually says, reported without massaging.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "instrument" / "src"))

from neurospine.effective_connectivity import (  # noqa: E402
    directed_influence,
    discrete_steady_state,
    edge_group_stats,
    fit_var1,
    group_effective_connectivity,
    spectral_radius,
)

SUBCORTICAL_KEEP = [
    "Thalamus", "Caudate", "Putamen", "Pallidum",
    "Brain-Stem", "Hippocampus", "Amygdala", "Accumbens",
]


def yeo_network_of(label: str) -> str:
    s = label.decode() if isinstance(label, bytes) else str(label)
    m = re.search(r"(?:LH|RH)_([A-Za-z]+)", s)
    return m.group(1) if m else "Unknown"


def extract_augmented_timeseries(n_subjects: int, n_rois: int):
    """Return (list of per-subject (T, n_regions) arrays, labels, networks)
    over the Schaefer cortex + Harvard-Oxford subcortex augmented atlas."""
    from nilearn.datasets import (
        fetch_atlas_harvard_oxford,
        fetch_atlas_schaefer_2018,
        fetch_development_fmri,
    )
    from nilearn.maskers import NiftiLabelsMasker

    cortex = fetch_atlas_schaefer_2018(n_rois=n_rois, yeo_networks=7, resolution_mm=2)
    subcort = fetch_atlas_harvard_oxford("sub-maxprob-thr25-2mm")

    cortex_labels = [str(l) for l in cortex.labels]
    cortex_networks = [yeo_network_of(l) for l in cortex.labels]
    if cortex_labels and "Background" in cortex_labels[0]:
        cortex_labels = cortex_labels[1:]
        cortex_networks = cortex_networks[1:]

    sub_labels_all = [str(l) for l in subcort.labels]
    keep_idx = [i for i, l in enumerate(sub_labels_all)
                if any(k.lower() in l.lower() for k in SUBCORTICAL_KEEP)]
    sub_labels = [sub_labels_all[i] for i in keep_idx]
    sub_networks = ["Subcortex"] * len(sub_labels)

    dev = fetch_development_fmri(n_subjects=n_subjects)
    m_cortex = NiftiLabelsMasker(labels_img=cortex.maps, standardize="zscore_sample", verbose=0)
    m_sub = NiftiLabelsMasker(labels_img=subcort.maps, standardize="zscore_sample", verbose=0)

    series = []
    for i, (func, conf) in enumerate(zip(dev.func, dev.confounds)):
        ts_c = m_cortex.fit_transform(func, confounds=conf)
        ts_s_all = m_sub.fit_transform(func, confounds=conf)
        cols = [k - 1 for k in keep_idx if 0 < k <= ts_s_all.shape[1]]
        ts = np.hstack([ts_c, ts_s_all[:, cols]])
        series.append(ts)
        print(f"[ec]   subject {i + 1}/{n_subjects}: T={ts.shape[0]}, n={ts.shape[1]}")

    labels = np.array(cortex_labels + sub_labels)
    networks = np.array(cortex_networks + sub_networks)
    return series, labels, networks


def network_indices(networks, name):
    s = name.lower()
    return [i for i in range(len(networks)) if s in str(networks[i]).lower()]


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-subjects", type=int, default=5)
    ap.add_argument("--n-rois", type=int, default=100)
    ap.add_argument("--ridge", type=float, default=5.0)
    args = ap.parse_args()

    print(f"[ec] extracting augmented ROI time series (n={args.n_subjects})")
    series, labels, networks = extract_augmented_timeseries(args.n_subjects, args.n_rois)

    A_mean, sign_cons = group_effective_connectivity(series, ridge=args.ridge)
    sr = spectral_radius(A_mean)
    print(f"\n[ec] group effective connectivity: {A_mean.shape}, "
          f"spectral radius {sr:.3f} (stable: {sr < 1.0})")

    # THE EMPIRICAL QUESTION: estimated sign of the key threat edges.
    edges = {
        "Cont -> Amygdala (regulation)": ("Cont", "Amygdala"),
        "Vis -> Amygdala": ("Vis", "Amygdala"),
        "SalVentAttn -> Amygdala": ("SalVentAttn", "Amygdala"),
        "Default -> Amygdala": ("Default", "Amygdala"),
        "Amygdala -> Cont": ("Amygdala", "Cont"),
    }
    print("\nESTIMATED SIGNED EFFECTIVE CONNECTIVITY (data, not assumed):")
    print(f"  {'edge':<32} {'weight':>9} {'sign':>5} {'consist':>8} {'pairs':>6}")
    edge_report = {}
    for name, (src, tgt) in edges.items():
        try:
            info = directed_influence(A_mean, list(labels), src, tgt, sign_cons)
        except ValueError as exc:
            print(f"  {name:<32} (skipped: {exc})")
            continue
        edge_report[name] = info
        print(f"  {name:<32} {info['mean_weight']:>9.4f} {info['sign']:>5d} "
              f"{info.get('mean_sign_consistency', float('nan')):>8.2f} "
              f"{info['n_pairs']:>6d}")

    # Group-level significance + time-reversed control on the key edges
    # (Vinck et al. 2015; Chvostekova et al. 2021). Sign alone is not
    # enough: the edge must be non-zero at the group level and survive the
    # time-reversal comparison.
    print("\nGROUP STATS + TIME-REVERSED CONTROL (methodology-hardened):")
    print(f"  {'edge':<24} {'mean':>9} {'t':>7} {'p':>7} {'rev_mean':>9} {'net_dir':>9}")
    stats_report = {}
    for name, (src, tgt) in edges.items():
        try:
            gs = edge_group_stats(series, list(labels), src, tgt, ridge=args.ridge)
        except ValueError:
            continue
        stats_report[name] = gs
        print(f"  {name[:24]:<24} {gs['mean']:>9.4f} {gs['t_stat']:>7.2f} "
              f"{gs['p_value']:>7.3f} {gs['reversed_mean']:>9.4f} "
              f"{gs['net_directionality']:>9.4f}")

    reg_gs = stats_report.get("Cont -> Amygdala (regulation)")
    if reg_gs is not None:
        significant = reg_gs["p_value"] < 0.05
        neg = reg_gs["mean"] < 0
        rev_ok = reg_gs["net_directionality"] < 0  # forward more negative
        if significant and neg and rev_ok:
            verdict = ("INHIBITORY and statistically supported (negative at "
                       "the group level, p<0.05, survives time reversal): "
                       "data corroborates the ADR-015 assumption")
        elif neg and not significant:
            verdict = ("group MEAN is inhibitory but NOT statistically "
                       "reliable across subjects (p>=0.05); the sign is not "
                       "corroborated. A real emotion-regulation task is "
                       "needed to test it on-task")
        else:
            verdict = ("not inhibitory / not supported in this naturalistic "
                       "dataset")
        print(f"\n  VERDICT on prefrontal -> amygdala: {verdict}")
        print(f"  mean {reg_gs['mean']:.4f}, t={reg_gs['t_stat']:.2f}, "
              f"p={reg_gs['p_value']:.3f}, net directionality "
              f"{reg_gs['net_directionality']:.4f} over {reg_gs['n_subjects']} subjects")

    # Data-derived steady-state response to a sustained visual input,
    # using the ESTIMATED system directly (discrete VAR steady state).
    u = np.zeros(A_mean.shape[0])
    for i in network_indices(networks, "Vis"):
        u[i] = 1.0
    resp = None
    if sr < 1.0:
        x_ss = discrete_steady_state(A_mean, u)
        amyg = [i for i, l in enumerate(labels) if "amygdala" in str(l).lower()]
        resp = {
            "amygdala_activation": float(np.mean([x_ss[i] for i in amyg])),
            "max_abs_region": float(np.max(np.abs(x_ss))),
        }
        print(f"\nDATA-DERIVED steady state to sustained visual drive:")
        print(f"  mean amygdala activation: {resp['amygdala_activation']:.4f}")

    result = {
        "dataset": "nilearn development_fmri (Partly Cloudy, naturalistic)",
        "n_subjects": args.n_subjects,
        "n_regions": int(A_mean.shape[0]),
        "ridge": args.ridge,
        "spectral_radius": sr,
        "estimated_edges": edge_report,
        "group_stats_time_reversed": stats_report,
        "data_derived_steady_state": resp,
        "caveats": (
            "naturalistic movie, not a threat/regulation task; VAR(1) on "
            "fMRI is hemodynamically confounded and TR-limited; small group. "
            "The method (data-estimated signed edges replacing literature "
            "priors) is the contribution; the edge signs are reported as "
            "estimated, not curated."
        ),
    }
    out = Path(__file__).parent / "results" / "effective_connectivity_threat.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
