---
slug: arxiv-2406.15505
authors: [Caputi, Pidnebesna, Hlinka]
venue: arXiv, 2024
identifier: arXiv 2406.15505
year: 2024
projects: [tribe-neuroprint, cortex-of-anyone, wiring-not-weights]
gates: [G3, G8]
verdict: adjacent
aim: [A1, A2]
---

# Integral Betti Signature Confirms the Hyperbolic Geometry of Brain, Climate, and Financial Networks

## Mechanism (from abstract)

The authors extend persistent-homology-based TDA with "integral Betti signatures," a summary of Betti curves, and show these signatures distinguish Euclidean, spherical, and hyperbolic geometries in distance matrices from points on manifolds with constant sectional curvature. A key methodological warning: standard network-construction approaches (thresholding, correlation-to-distance conversions) introduce spurious spherical geometry that is an artifact of the construction pipeline, not the underlying data geometry. Applied to real brain, climate, and financial network data, the integral Betti signature places brain functional networks between Euclidean and hyperbolic geometry, closer to mild hyperbolicity, and the authors separately test whether low-rank modular network structure alone could fake a hyperbolic signature.

## Provisional relevance

Provisional: touches tribe-neuroprint and cortex-of-anyone because both build functional connectivity networks from fMRI and would inherit the exact spurious-sphericity artifact this paper warns about if the standard correlation-thresholding pipeline is used unexamined.
Provisional: touches wiring-not-weights because a network's intrinsic curvature (hyperbolic vs. Euclidean) is a structural, connectome-level property distinct from weights, directly relevant to the identity-is-in-the-weights-not-the-connectome debate this project runs.
Provisional: informs gate G3 (specification robustness) because the paper demonstrates that a seemingly minor preprocessing choice (network-construction method) flips the geometric conclusion; any NEUROSPINE topology claim needs this exact robustness check.
Provisional: informs gate G8 (external validity) because integral Betti signatures were validated across three unrelated domains (brain, climate, finance), which is a template for demonstrating a topology metric's cross-domain and cross-dataset stability.
Provisional: supports NEUROSPINE aim A1 and A2 by supplying a geometry-aware sanity check that individual- and group-scale connectivity topology claims are not artifacts of the network-construction pipeline, a confound A1/A2 replicability claims must rule out.

## Action items

- [ ] Re-run whatever network-construction step NEUROSPINE's topology layer currently uses and check for the spurious-sphericity artifact this paper documents, before trusting any curvature/topology claim.
- [ ] Add "network-construction method" as a required arm of the G3 specification-robustness sweep for any project computing brain-network topology.
