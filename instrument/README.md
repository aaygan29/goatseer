# instrument/

Reference analysis code for the NEUROSPINE study. `study/` holds the
protocol this code implements. `portfolio/` holds engineering pedigree
of the components. `literature/` holds the external anchors.

## What is here

- `src/neurospine/` the importable package.
  - `contract.py` the `Thought` dataclass, `FIELD_GATES`,
    `COGNITIVE_DARK_MATTER_DOMAINS`, `NotYetGatedError`.
  - `providers.py` runtime-checkable `Protocol`s for each provider
    (`PerceptionDecoder`, `AffectDecoder`, `DecisionDecoder`,
    `MemoryDecoder`, `RewardDecoder`, `SubjectAdapter`,
    `CalibrationProvider`, `AbstentionProvider`).
  - `reference.py` Null and Fixed reference providers used by the
    smoke tests. All fail their acceptance gates by construction.
  - `harness.py` `Neurospine.predict(subject, recordings, context)`.
- `tests/` pytest suite. `test_contract.py` covers the `Thought`
  contract; `test_harness.py` end-to-end smoke tests with reference
  providers; `tests/verification/` holds ADR-003 external
  re-verification tests per extraction.
- `specs/contract-v0.md` the frozen v0 spec of the `Thought` tuple.

## Status

- Contract: **frozen at v0** (Thought tuple, superseded the earlier
  Decision tuple per ADR-004).
- Harness: **wired end-to-end**, 30 tests pass.
- Providers: **stubs only** in `reference.py`. Real providers land
  as they clear their gates and pass ADR-003 external re-verification.
- Extraction protocol: see ADR-003.

## Order of assembly (planned)

1. Contract v0 frozen. Done.
2. Reference providers + failing tests for every prediction dimension.
   Done.
3. First real `AbstentionProvider`: implements the Goltermann/Huth
   triad check on any fMRI-grounded input. Requires the anesthesia
   bridge extraction per ADR-003.
4. First real `CalibrationProvider`: conformal wrapper on a held-out
   split. External anchor Vovk et al. 2005; Angelopoulos and Bates
   2021.
5. First real `PerceptionDecoder`: subject-conditional decoder on NSD,
   anchor MEIcoder.
6. First real `MemoryDecoder` and `RewardDecoder`: temporal-shift
   readouts anchored on the Yaghoubi hippocampal backward-shift paper.
7. First real `DecisionDecoder`: hierarchical DDM with neural
   parameter link functions.
8. First real `AffectDecoder`: multimodal fusion on DEAP.
9. First real `SubjectAdapter`: RAVEN weak-to-strong under shift.
10. Full contract on one held-out subject in NSD and one in HCP-YA.

## External anchors

Every provider's docstring names the seed-literature or expanded-scan
entry it implements. See `../decisions/ADR-002-citation-doctrine.md`
for the rule and `../literature/SYNTHESIS_computational.md` for the
component-to-anchor table.

## How to add a real provider

1. Implement a class that satisfies the Protocol in `providers.py`.
2. Write an ADR-003 verification test at
   `tests/verification/test_<slug>_<bit>.py` that proves the
   extraction matches its external anchor.
3. Update the `Extractable strongest bit` and `External
   re-verification` sections of the relevant
   `portfolio/<slug>/evaluation.md`.
4. Only after verification test passes may the gates that provider
   feeds move above `unscored` in the evaluation.
