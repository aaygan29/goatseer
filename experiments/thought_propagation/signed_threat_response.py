"""Signed-dynamics threat response (ADR-015): the inhibitory-regulation
prediction the excitatory-only random walk could not make.

ADR-014's ablation 2 was a documented limitation: in a row-stochastic
random walk, adding a PFC -> amygdala edge INCREASED effector drive,
because a probability-conserving walk cannot subtract. This experiment
rebuilds the same threat circuit as a SIGNED linear rate model
(`signed_dynamics.py`), where the PFC -> amygdala edge is INHIBITORY
(negative weight), and shows the correct-direction prediction:

  increasing prefrontal regulatory gain monotonically LOWERS amygdala
  steady-state activation and the autonomic / endocrine / motor drive
  read out from it.

It also quantifies the control cost: the minimum control energy for the
prefrontal control set to hold the amygdala at a downregulated target,
using the controllability Gramian (Gu et al. 2015).

Same augmented cortico-subcortical connectome as ADR-014. Effectors are
LINEAR READOUTS of the neural steady state, not absorbing nodes, which is
the honest representation for a linear system: an effector's drive is a
weighted sum of the activation it receives.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "instrument" / "src"))

from neurospine.circuit import DirectedEdge  # noqa: E402
from neurospine.signed_dynamics import build_signed_system  # noqa: E402


def excitatory_edges(fast_route: bool = True) -> list:
    """LeDoux threat cascade, excitatory branches (matches ADR-014 minus
    the regulation edge, which is now inhibitory)."""
    edges = [
        DirectedEdge("Vis", "Default", 1.0),       # slow high road proxy
        DirectedEdge("Default", "Amygdala", 1.0),
        DirectedEdge("Vis", "Amygdala", 0.5),      # direct cortico-amygdalar
        DirectedEdge("Amygdala", "Brain-Stem", 1.0),
        DirectedEdge("Amygdala", "Cont", 1.0),     # amygdala recruits PFC
        DirectedEdge("Amygdala", "Hippocampus", 0.5),
        DirectedEdge("Brain-Stem", "SomMot", 1.0),
    ]
    if fast_route:
        edges += [
            DirectedEdge("Vis", "Thalamus", 1.0),
            DirectedEdge("Thalamus", "Amygdala", 1.5),
        ]
    return edges


def inhibitory_edges() -> list:
    """Prefrontal top-down downregulation of the amygdala (SIGNED)."""
    return [DirectedEdge("Cont", "Amygdala", 1.0)]


def effector_readouts(sys) -> dict:
    """Linear readout weights for the un-imaged effectors, as index->weight
    maps over the neural nodes."""
    def w(pairs):
        v = np.zeros(sys.n)
        for substr, weight in pairs:
            for i in sys.index_of(substr):
                v[i] = weight
        return v
    return {
        "Autonomic": w([("Amygdala", 1.0), ("Brain-Stem", 1.0)]),
        "Endocrine": w([("Amygdala", 1.0)]),
        "MotorOutput": w([("SomMot", 1.0), ("Brain-Stem", 0.5)]),
    }


def build(fc, networks, labels, inh_weight=1.0, fast_route=True, gamma=None):
    return build_signed_system(
        fc, list(labels), networks,
        excitatory_edges=excitatory_edges(fast_route),
        inhibitory_edges=inhibitory_edges(),
        exc_weight=1.0, inh_weight=inh_weight,
        fc_scale=0.5, leak_margin=1.0, gamma=gamma,
    )


def stimulus(sys, networks, tonic_pfc=0.3):
    """Sustained visual-threat input on the Vis network plus a tonic
    prefrontal drive so regulatory gain has something to carry."""
    u = np.zeros(sys.n)
    for i in range(sys.n):
        if "vis" in str(networks[i]).lower():
            u[i] = 1.0
        if "cont" in str(networks[i]).lower():
            u[i] = tonic_pfc
    return u


def main() -> None:
    d = np.load(
        Path(__file__).parent / "results" / "connectome_augmented.npz",
        allow_pickle=True,
    )
    fc = d["fc"]
    networks = d["networks"]
    labels = np.array([str(x) for x in d["labels"]])
    n_cortex, n_sub = int(d["n_cortex"]), int(d["n_subcortex"])

    sys_ = build(fc, networks, labels, inh_weight=1.0)
    u = stimulus(sys_, networks)
    amyg = sys_.index_of("Amygdala")
    readouts = effector_readouts(sys_)

    print(f"Augmented atlas: {n_cortex} cortical + {n_sub} subcortical regions")
    print(f"Signed linear system: n={sys_.n}, gamma={sys_.gamma:.3f}, "
          f"stable={sys_.is_stable()} (spectral abscissa "
          f"{sys_.spectral_abscissa():.3f})")
    print(f"Amygdala regions: {len(amyg)}; visual/PFC drive applied.")

    # PREDICTION: increasing prefrontal regulatory gain lowers amygdala and
    # effector drive. This is the ablation-2 direction FLIPPED, now correct.
    print("\nPREDICTION: prefrontal regulatory gain vs threat drive")
    print(f"  {'inh gain':>9} {'amygdala':>10} {'Autonomic':>10} "
          f"{'Endocrine':>10} {'MotorOut':>10}")
    # Hold the leak fixed at the baseline value across the sweep so the
    # only thing varying is the inhibitory gain, not the relaxation rate.
    gamma_fixed = sys_.gamma
    sweep = []
    for g in [0.0, 0.5, 1.0, 1.5, 2.0]:
        s = build(fc, networks, labels, inh_weight=g, gamma=gamma_fixed)
        x = s.steady_state(u)
        amyg_act = float(np.mean([x[i] for i in amyg]))
        drives = {k: float(v @ x) for k, v in effector_readouts(s).items()}
        sweep.append({"inh_gain": g, "amygdala": amyg_act, **drives})
        print(f"  {g:>9.1f} {amyg_act:>10.4f} {drives['Autonomic']:>10.4f} "
              f"{drives['Endocrine']:>10.4f} {drives['MotorOutput']:>10.4f}")

    amyg_series = [row["amygdala"] for row in sweep]
    auto_series = [row["Autonomic"] for row in sweep]
    monotone = all(b < a for a, b in zip(amyg_series, amyg_series[1:]))
    auto_monotone = all(b < a for a, b in zip(auto_series, auto_series[1:]))
    print(f"\n  amygdala activation strictly decreasing in inh gain: "
          f"{'PASS' if monotone else 'FAIL'}")
    print(f"  autonomic drive strictly decreasing in inh gain:      "
          f"{'PASS' if auto_monotone else 'FAIL'}")
    print("  This is the ADR-014 limitation resolved: inhibition now")
    print("  SUBTRACTS, so prefrontal regulation reduces the threat")
    print("  response instead of amplifying it.")

    # CONTROL COST: minimum energy for the prefrontal control set to hold
    # the amygdala at a downregulated target (Gu et al. 2015 Gramian).
    cont_nodes = sys_.index_of("Cont")
    target = np.zeros(sys_.n)
    x_free = sys_.steady_state(u)
    for i in amyg:
        target[i] = 0.5 * x_free[i]   # halve amygdala activation
    energy = sys_.minimum_control_energy(cont_nodes, target)
    print(f"\nCONTROL COST (prefrontal control set, {len(cont_nodes)} nodes):")
    print(f"  min control energy to halve amygdala activation: {energy:.4g}")

    result = {
        "system": {
            "n_nodes": int(sys_.n),
            "gamma": float(sys_.gamma),
            "stable": bool(sys_.is_stable()),
            "spectral_abscissa": sys_.spectral_abscissa(),
        },
        "regulation_sweep": sweep,
        "amygdala_monotone_decreasing": bool(monotone),
        "autonomic_monotone_decreasing": bool(auto_monotone),
        "min_control_energy_halve_amygdala": float(energy),
        "note": ("signed linear rate model; PFC->amygdala edge is "
                 "inhibitory (negative); increasing regulatory gain "
                 "monotonically lowers amygdala and effector drive, "
                 "resolving the ADR-014 ablation-2 limitation"),
    }
    out = Path(__file__).parent / "results" / "signed_threat_response.json"
    with open(out, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
