# Organization

Path map for NEW_REPO / NEUROSPINE. This file is the source of truth when
directory names change or projects are retired.

## Top-level

| Path | Purpose |
| --- | --- |
| `README.md` | Program overview, instrument contract, hard rules. |
| `ORGANIZATION.md` | This file. Path map. |
| `MEMORY_LINKS.md` | Cross-references to Aayush's auto-memory entries. |
| `issues_to_open.md` | Queued GitHub actions blocked on auth or human review. |
| `LICENSE` | AGPL-3.0 (see `decisions/ADR-001-license.md`). |
| `gates/` | Versioned gate ladder. Current: `gate-ladder-v0.md`. |
| `instrument/` | NEUROSPINE source, tests, and spec. |
| `experiments/` | Runnable experiments, one Makefile target each. |
| `portfolio/` | Per-project evaluation dossier. |
| `literature/` | Per-paper structured notes, plus `references.bib`. |
| `reports/weekly/` | Monday scorecard. |
| `decisions/` | ADRs. |

## In-scope projects and their canonical external homes

Active:

| Slug | External home | Notes |
| --- | --- | --- |
| `tribe-neuroprint` | `~/Desktop/Research/neuroprint-api/` | TRIBE v2 pipeline + FastAPI. |
| `ism-v1` | Modal pipeline, local | Interoceptive Self-Model v1. |
| `anesthesia-bridge` | `ds003171` + LLM battery | Propofol grading. |
| `memoryprint` | NSD / BMD local | Idiographic memory to behavior. |
| `behavioral-decoding` | `aaygan29/behavioral_decoding` | AIxBio Africa, private. |
| `decision-phenotype` | `aaygan29/decision-phenotype` | AIM-DDM + C1 to C5. |
| `jspace-loyalty` | `aaygan29/jspace-loyalty` | NewInML NeurIPS 2026. |
| `mats-jlens` | Local | Qwen3-4B multi-hop, J-space vs unembedding. |
| `cultist` | `~/Desktop/Research/cultist` | B(s) = E + V - R, latent-fusion. |
| `wiring-not-weights` | Local | Identity in weights, ablation ladder. |
| `cortex-of-anyone` | Blueprint doc | Deployment envelope; T1 feasible. |
| `nacc-anticipation` | `aaygan29/NAcc_benchmark` fork | TB-Science PR pending. |
| `bio-toolkit` | `aaygan29/bio-toolkit` | Consolidated bio infra. |

Proposed / earlier:

| Slug | Status |
| --- | --- |
| `warden` | Proposal, unifies deceptkit/cultist/neurobridge/CHORUS/PRISM. |
| `affectprint` | Proposal, affect validation arm of Cortex of Anyone. |
| `spikeprint` | Proposal, neuromorphic extension of neurosignal. |
| `globalsouthai` | Submitted 2026-08-23, GlobalSouthAI at NeurIPS 2026. |
| `pereverzev-neuro-extension` | Early stage, port to real neurodata. |

## Retirement

A project moves out of `portfolio/` and into an ADR under `decisions/` when it
fails the same gate twice across two evaluations more than 14 days apart with
no viable fix in the tree. See ADR template in `decisions/README.md`.
