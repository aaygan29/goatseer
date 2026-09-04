---
slug: arxiv-2408.06421
authors: [Barney, Winer, Galitski]
venue: arXiv, 2024
identifier: arXiv 2408.06421
year: 2024
projects: [wiring-not-weights, warden, jspace-loyalty]
gates: [G6]
verdict: adjacent
aim: [A1]
---

# Neural Networks as Spin Models: From Glass to Hidden Order Through Training

## Mechanism (from abstract)

The authors map an artificial neural network's neurons to Ising spins and its weights to spin-spin couplings, turning training dynamics into a statistical-mechanics problem. At initialization (random weights), the network corresponds to a layered Sherrington-Kirkpatrick spin glass exhibiting replica symmetry breaking, a disordered, frustrated phase. Using the Thouless-Anderson-Palmer (TAP) mean-field equations, they track two network types trained on MNIST and show the spin-glass phase is destroyed during training, replaced by a phase with "hidden order" whose melting (transition) temperature grows as a power law in training time. They interpret training as a process that selects and reinforces symmetry-broken states corresponding to the learned task.

## Provisional relevance

Provisional: touches wiring-not-weights because the spin-model framing gives a formal, physics-grounded language for asking whether "identity" in a trained network is a property of the couplings (weights) or of the emergent order parameter (a state that could in principle be reached by different coupling configurations), directly bearing on the weights-vs-wiring debate applied to artificial (not biological) networks.
Provisional: touches warden and jspace-loyalty at a stretch because a network's "hidden order" phase and its melting temperature could be reinterpreted as a formal measure of how entrenched a learned disposition (e.g. a loyalty vector) is, and how much perturbation is needed to destabilize it; this is speculative and needs validation before use.
Provisional: informs gate G6 (mechanism and necessity) because the TAP-equation analysis is explicitly mechanistic (order parameters, transition temperatures) and offers a falsifiable intervention: perturbing couplings that carry the "hidden order" signature should measurably degrade task performance, a necessity test.
Provisional: supports NEUROSPINE aim A1 only indirectly and provisionally, since the paper is about artificial networks (not biological subjects), and the connection to individual-scale thought prediction from real recordings is currently speculative rather than demonstrated.

## Action items

- [ ] Treat this as a physics-anchor candidate only; do not cite as neuroscience evidence until a biological analogue (e.g. an Ising/spin-glass model fit to real spiking or fMRI data) is identified.
- [ ] Discuss with warden whether "melting temperature of hidden order" is a usable formalization of loyalty-vector entrenchment (H3) or is a false-friend metaphor; log the verdict as an ADR before adopting.
