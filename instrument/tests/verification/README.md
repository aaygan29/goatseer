# tests/verification/

External re-verification tests per ADR-003.

Each file here proves that a bit extracted from a prior Aayush project
still matches its external anchor (a public dataset, a reference
implementation, or a specific published claim). Until an extraction has a
passing verification test here, the gates it feeds in
`portfolio/<slug>/evaluation.md` cannot move above `unscored`.

Naming convention: `test_<portfolio-slug>_<extracted-bit>.py`.

Every test's docstring must name:
- The seed-literature entry that provides the anchor.
- The exact claim being verified.
- The tolerance and why it is justified.
