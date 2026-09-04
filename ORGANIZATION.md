# Organization

Path map for NEW_REPO / NEUROSPINE. Source of truth when directory
names change or projects are retired.

## Top-level

| Path | Purpose |
| --- | --- |
| `README.md` | Program overview, instrument contract, hard rules. |
| `ORGANIZATION.md` | This file. Path map. |
| `MEMORY_LINKS.md` | Cross-references to Aayush's auto-memory entries. |
| `issues_to_open.md` | Queued GitHub actions and human-in-the-loop items. |
| `LICENSE` | AGPL-3.0 (see `decisions/ADR-001-license.md`). |
| `Makefile` | `make test`, `make install-dev`, `make lint`, `make clean`. |
| `pyproject.toml` | `neurospine` package definition (Python >=3.10). |
| `study/` | Research study protocol, aims, methods, preregistration. |
| `instrument/` | Reference analysis code + tests + specs. |
| `gates/` | Versioned gate ladder. Current: `gate-ladder-v0.md`. |
| `experiments/` | Runnable experiments, one Makefile target each. |
| `portfolio/` | Per-project evaluation dossier. |
| `literature/` | Per-paper structured notes, plus `references.bib`. |
| `reports/weekly/` | Monday scorecard. |
| `reports/first-scoring-pass-2026-09-03.md` | First real gate-scoring pass, cross-cutting summary. |
| `decisions/` | ADRs (000 to 006 as of 2026-09-03). |
| `thought_evaluator.py` + `tests/` | Legacy Copilot module merged from main; orthogonal to NEUROSPINE. |

## In-scope projects and their canonical external homes

Verified 2026-09-03. Stale paths corrected per the first scoring pass.

Active:

| Slug | External home | Notes |
| --- | --- | --- |
| `tribe-neuroprint` | Path unresolved as of 2026-09-03 scoring. Confirm with Aayush. | TRIBE v2 pipeline. Paper 1 claim retired via ADR-005. |
| `ism-v1` | Modal pipeline, local | Interoceptive Self-Model v1. |
| `anesthesia-bridge` | `ds003171` + LLM battery | Propofol grading. Green on 2026-09-03 scoring, blocked on G-fMRI.2. |
| `memoryprint` | NSD / BMD local | Idiographic memory to behavior. |
| `behavioral-decoding` | `aaygan29/behavioral_decoding` (private) | AIxBio Africa. |
| `decision-phenotype` | `aaygan29/decision-phenotype` | AIM-DDM + C1 to C5. Green on 2026-09-03 scoring, blocked on G-fMRI.2. |
| `jspace-loyalty` | `aaygan29/jspace-loyalty` | NewInML NeurIPS 2026; second-model replication blocked on hardware. |
| `mats-jlens` | Local | Qwen3-4B multi-hop, J-space vs unembedding. |
| `cultist` | `~/Desktop/Research/cultist` | B(s) = E + V - R, latent-fusion. |
| `wiring-not-weights` | Local | Identity in weights, ablation ladder. Green on 2026-09-03 scoring, gap is data. |
| `cortex-of-anyone` | Blueprint doc + local | Deployment envelope; T1 feasible. Hopf twin retired via ADR-006. |
| `nacc-anticipation` | fork with PR #721 to `terminal-bench-science` | GitHub remote path was `aaygan29/NAcc_benchmark`, unresolved as of 2026-09-03; the active work is the fork PR. |
| `bio-toolkit` | `aaygan29/bio-toolkit` | Consolidated bio infra. Does not map to any NEUROSPINE tuple field. |

Proposed / earlier:

| Slug | Status |
| --- | --- |
| `warden` | Proposal; overlaps with the H1/H2/H3 addendum terminology (see gate ladder). |
| `affectprint` | Proposal; overlaps with cortex-of-anyone G3 result. |
| `spikeprint` | Proposal, neuromorphic extension. |
| `globalsouthai` | Submitted 2026-08-23, GlobalSouthAI at NeurIPS 2026. |
| `pereverzev-neuro-extension` | Early stage; no code exists yet. |

## Retirement

A project moves out of `portfolio/` and into an ADR under `decisions/`
when it fails the same gate twice across two evaluations more than 14
days apart with no viable fix in the tree, OR when the project's own
documented evidence records a failure as settled (as with ADR-005 and
ADR-006). See ADR template in `decisions/README.md`.
