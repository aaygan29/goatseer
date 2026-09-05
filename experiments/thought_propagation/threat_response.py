"""Threat-response circuit (ADR-014): the scary-stimulus cascade set up
the way a research scientist would, given that imaging cannot capture
the whole response.

The response is a parallel multi-system cascade. This model:
1. Uses an AUGMENTED cortico-subcortical connectome (adds amygdala,
   thalamus, brainstem, the actual threat hubs).
2. Overlays the LeDoux dual-route threat circuit as DIRECTED anatomical
   priors (imaging FC is symmetric and cannot provide direction):
   fast subcortical route Vis -> Thalamus -> Amygdala, slow cortical
   route Vis -> ventral/temporal -> Amygdala, then amygdala outputs.
3. Adds EXOGENOUS effector nodes that are NOT imaged (autonomic,
   endocrine, peripheral motor), representing the un-imageable output
   systems explicitly instead of faking them into the FC.

It then reports where a visual threat terminates (absorption across
effectors), the expected processing depth before output, and two
ablations that test the circuit logic:
- Removing the fast subcortical shortcut should SLOW amygdala arrival.
- Removing PFC regulation should INCREASE autonomic/endocrine drive.

All directed priors are anatomical literature edges (LeDoux 1996, 2000;
Pessoa + Adolphs 2010 on the subcortical route), clearly separated from
the measured FC.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "instrument" / "src"))

from neurospine.circuit import (  # noqa: E402
    DirectedEdge,
    ExogenousEffector,
    build_directed_circuit,
)

# LeDoux dual-route threat circuit as directed anatomical priors.
# Region labels are matched by substring against the augmented atlas.
def threat_priors(regulation: bool = True, fast_route: bool = True) -> list:
    edges = [
        # Slow "high road": visual cortex -> ventral/temporal -> amygdala.
        DirectedEdge("Vis", "Default", 1.0),      # ventral/temporal proxy
        DirectedEdge("Default", "Amygdala", 1.0),
        DirectedEdge("Vis", "Amygdala", 0.5),     # direct cortico-amygdalar
        # Amygdala outputs (parallel):
        DirectedEdge("Amygdala", "Brain-Stem", 1.0),   # PAG defensive motor
        DirectedEdge("Amygdala", "Cont", 1.0),         # PFC appraisal
        DirectedEdge("Amygdala", "Hippocampus", 0.5),  # context encoding
        DirectedEdge("Brain-Stem", "SomMot", 1.0),     # motor staging
    ]
    if fast_route:
        # Fast "low road": visual -> thalamus (pulvinar) -> amygdala.
        edges += [
            DirectedEdge("Vis", "Thalamus", 1.0),
            DirectedEdge("Thalamus", "Amygdala", 1.5),  # privileged shortcut
        ]
    if regulation:
        # PFC downregulation of the amygdala (top-down control).
        edges += [DirectedEdge("Cont", "Amygdala", 1.0)]
    return edges


def threat_effectors() -> list:
    return [
        # Autonomic: heart rate, skin conductance. Driven by amygdala +
        # brainstem. NOT imaged.
        ExogenousEffector("Autonomic",
                          [("Amygdala", 1.0), ("Brain-Stem", 1.0)], imaged=False),
        # Endocrine: HPA / cortisol, via hypothalamus (un-imaged relay,
        # proxied by direct amygdala drive). NOT imaged.
        ExogenousEffector("Endocrine",
                          [("Amygdala", 1.0)], imaged=False),
        # Peripheral motor output: the behavioral reaction. NOT imaged.
        ExogenousEffector("MotorOutput",
                          [("SomMot", 1.0), ("Brain-Stem", 0.5)], imaged=False),
    ]


def build(fc, networks, labels, regulation=True, fast_route=True,
          with_effectors=True):
    return build_directed_circuit(
        fc=fc, node_labels=list(labels), networks=networks,
        directed_priors=threat_priors(regulation, fast_route),
        effectors=threat_effectors() if with_effectors else [],
        prior_weight=3.0,
    )


def main() -> None:
    d = np.load(
        Path(__file__).parent / "results" / "connectome_augmented.npz",
        allow_pickle=True,
    )
    fc, networks, labels = d["fc"], d["networks"], np.array([str(x) for x in d["labels"]])
    n_cortex, n_sub = int(d["n_cortex"]), int(d["n_subcortex"])

    circuit = build(fc, networks, labels)
    seed = circuit.network_indices("Vis")
    print(f"Augmented atlas: {n_cortex} cortical + {n_sub} subcortical regions "
          f"+ {len(circuit.effector_names)} exogenous effectors")
    print(f"Visual seed regions: {len(seed)}")

    ob = circuit.observability_boundary()
    print(f"\nOBSERVABILITY BOUNDARY:")
    print(f"  imaged regions: {ob['n_imaged_regions']}")
    print(f"  un-imaged effectors: {ob['n_exogenous_effectors']} {ob['effectors']}")

    resp = circuit.response_distribution(seed)
    print(f"\nWHERE A VISUAL THREAT TERMINATES (absorption from Vis seed):")
    for eff, p in sorted(resp["absorption"].items(), key=lambda kv: -kv[1]):
        print(f"  {eff:>12}: {p:.3f}")
    print(f"  expected processing steps (imaged) before output: "
          f"{resp['expected_processing_steps']:.2f}")

    # Ablation 1: fast subcortical shortcut speeds amygdala arrival.
    circuit_fast_nofx = build(fc, networks, labels, fast_route=True, with_effectors=False)
    circuit_slow_nofx = build(fc, networks, labels, fast_route=False, with_effectors=False)
    mfpt_with = circuit_fast_nofx.mfpt_between(seed, "Amygdala")
    mfpt_without = circuit_slow_nofx.mfpt_between(seed, "Amygdala")
    print(f"\nABLATION 1: fast subcortical route (Vis->Thalamus->Amygdala)")
    print(f"  MFPT Vis->Amygdala WITH shortcut:    {mfpt_with:.2f}")
    print(f"  MFPT Vis->Amygdala WITHOUT shortcut: {mfpt_without:.2f}")
    faster = mfpt_with < mfpt_without
    print(f"  {'PASS' if faster else 'FAIL'}: shortcut "
          f"{'speeds' if faster else 'does NOT speed'} amygdala arrival")

    # Ablation 2: PFC regulation reduces autonomic+endocrine drive.
    resp_reg = circuit.response_distribution(seed)
    circuit_noreg = build(fc, networks, labels, regulation=False)
    resp_noreg = circuit_noreg.response_distribution(seed)
    auto_endo_reg = resp_reg["absorption"]["Autonomic"] + resp_reg["absorption"]["Endocrine"]
    auto_endo_noreg = resp_noreg["absorption"]["Autonomic"] + resp_noreg["absorption"]["Endocrine"]
    print(f"\nLIMITATION PROBE: PFC (Cont->Amygdala) regulation")
    print(f"  autonomic+endocrine absorption WITH the edge:    {auto_endo_reg:.3f}")
    print(f"  autonomic+endocrine absorption WITHOUT the edge: {auto_endo_noreg:.3f}")
    print(f"  A non-negative random walk is EXCITATORY-ONLY: adding a")
    print(f"  Cont->Amygdala edge increases amygdala inflow and therefore")
    print(f"  INCREASES effector drive ({auto_endo_reg:.3f} > {auto_endo_noreg:.3f}),")
    print(f"  the opposite of real inhibitory PFC downregulation. This is a")
    print(f"  documented model limitation: representing top-down inhibition")
    print(f"  requires SIGNED dynamics (a linear dynamical system with")
    print(f"  negative weights), not a probability-flow random walk. Next step.")

    result = {
        "observability": ob,
        "response_distribution": resp,
        "ablation_fast_route": {
            "mfpt_with": mfpt_with, "mfpt_without": mfpt_without,
            "shortcut_speeds_arrival": bool(faster),
        },
        "limitation_regulation": {
            "auto_endo_with_edge": auto_endo_reg,
            "auto_endo_without_edge": auto_endo_noreg,
            "note": ("excitatory-only random walk cannot represent "
                     "inhibitory PFC regulation; adding the edge increases "
                     "rather than decreases effector drive; requires signed "
                     "dynamics"),
        },
    }
    out = Path(__file__).parent / "results" / "threat_response.json"
    with open(out, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
