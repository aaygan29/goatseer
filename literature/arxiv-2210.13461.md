---
slug: arxiv-2210.13461
authors: [Rao, Gklezakos, Sathish]
venue: arXiv, 2022
identifier: arXiv 2210.13461
year: 2022
projects: [cortex-of-anyone, decision-phenotype, memoryprint]
gates: [G6]
verdict: adjacent
aim: [A1]
---

# Active Predictive Coding: A Unified Neural Framework for Learning Hierarchical World Models for Perception and Planning

## Mechanism (from abstract)

The authors propose "active predictive coding," a framework that learns hierarchical world models to jointly solve compositional representation learning (equivariant vision, part-whole hierarchies) and large-scale planning (composing action sequences from primitive policies). The architecture combines hypernetworks, self-supervised learning, and reinforcement learning to build task-invariant state-transition networks and task-dependent policy networks at multiple levels of abstraction. Tested on vision benchmarks (MNIST, FashionMNIST, Omniglot) and a hierarchical planning task, the authors claim it is the first unified solution addressing part-whole learning (Hinton), nested reference frames (Hawkins), and integrated state-action hierarchy learning in reinforcement learning, all framed as instantiations of predictive coding, a biologically motivated theory of cortical computation.

## Provisional relevance

Provisional: touches cortex-of-anyone and decision-phenotype because a hierarchical, predictive-coding world model is a candidate generative backbone for a personal digital-brain model that must represent both perception and planning/decision structure at multiple abstraction levels, matching the DecisionDecoder's need for a hierarchical action-value representation.
Provisional: touches memoryprint because task-invariant state-transition networks are structurally similar to what an idiographic memory model needs: representations that are stable across specific episodes but generalize the underlying task/environment structure.
Provisional: informs gate G6 (mechanism and necessity) only weakly, since the paper's predictive-coding claims are motivated by biological plausibility but validated purely on synthetic vision/planning benchmarks with no biological data or intervention; a necessity test against real neural data is entirely absent.
Provisional: supports NEUROSPINE aim A1 only as an architectural inspiration, not as empirical evidence, since no human subject data, individual-scale replicability, or neural recordings are used in this paper.

## Action items

- [ ] Do not cite this paper as neuroscience evidence for predictive coding; flag it explicitly as an architecture reference only, pending a biologically validated instantiation.
- [ ] Evaluate whether the hypernetwork-based task-invariant/task-dependent split is a useful design pattern for cortex-of-anyone's Layer 2 (brain) vs Layer 3 (experiment) separation.
