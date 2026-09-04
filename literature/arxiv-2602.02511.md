---
slug: arxiv-2602.02511
authors: [Hanley, Yeh, Rodriguez, Pilkington, Farahany]
venue: arXiv, 2026
identifier: arXiv 2602.02511
year: 2026
projects: [cortex-of-anyone, warden, tribe-neuroprint]
gates: [G11]
verdict: sharpens
aim: [A3]
---

# Training Data Governance for Brain Foundation Models

## Mechanism (from abstract)

This is a governance/ethics paper, not an empirical or methods paper. The authors argue that neural data (EEG, fMRI) carries stronger privacy and consent expectations than text or image data because of its clinical origins, and that the foundation-model paradigm's core move, large-scale repurposing, cross-context stitching, and open-ended downstream application, is in tension with those expectations, especially as commercial actors gain access under fragmented regulatory frameworks. Drawing on AI ethics, neuroethics, and bioethics, they organize open governance questions around privacy, consent, bias, and benefit-sharing, and propose baseline safeguards and agenda-setting questions rather than a finished framework.

## Provisional relevance

Provisional: touches cortex-of-anyone and warden directly because both projects propose enrolling individuals' neural data into personal or standing models; this paper's concerns about repurposing and cross-context stitching apply exactly to a "digital brain" enrollment pipeline and to WARDEN's persistent cognitive-security framing.
Provisional: touches tribe-neuroprint because any pretrained brain-foundation-model backbone adopted (e.g. Brain-OF, arXiv 2602.23410) inherits these governance concerns about its own training data provenance and consent.
Provisional: informs gate G11 (ethics and safety) directly and is the strongest single anchor found in this scan for that gate; it supplies concrete baseline-safeguard language (consent scope, benefit-sharing, re-identification risk) that NEUROSPINE's ethics notes currently lack detail on.
Provisional: supports NEUROSPINE aim A3 (declared unmeasured cognitive domains) only indirectly, by implying that consent and governance documentation is itself an "unmeasured" dimension that must be declared alongside cognitive dark matter domains, i.e. a governance dark-matter analogue.

## Action items

- [ ] Draft a data-governance addendum to gates/gate-ladder-v0.md's G11 section using this paper's privacy/consent/bias/benefit-sharing framing as the checklist structure.
- [ ] Audit cortex-of-anyone's and warden's current data-sourcing notes against the "cross-context stitching" and "re-purposing" concerns this paper raises, before any real personal-data enrollment.
