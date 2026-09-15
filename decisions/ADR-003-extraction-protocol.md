# ADR-003: Extraction and re-verification protocol

## Status

Accepted, 2026-09-03.

## Context

ADR-002 established that NEUROSPINE leans on external citations and does not
cite Aayush's prior projects as authority. It also said extracted code must
get a fresh external check before it contributes to any gate scoring. This
ADR spells out how.

The failure mode we are ruling out: an undetected bug in a prior project
props up a NEUROSPINE claim. A reviewer finds the prior bug; the
NEUROSPINE claim falls with it. This is the "circular error" risk Aayush
named on 2026-09-03.

## Decision

Every extraction from a prior Aayush project follows this protocol before it
can raise any gate in `portfolio/<slug>/evaluation.md` above `unscored`.

### Step 1: name the bit

In the source project's `portfolio/<slug>/evaluation.md`, fill in the
`Extractable strongest bit` section with:

- What is being lifted (function, class, config, data pipeline step).
- The file path in the source project.
- One sentence on what it does.

### Step 2: name the external anchor

In the same section, fill in the `External re-verification anchor`:

- The seed-literature entry (or a forward cite) that gives the anchor.
- The specific claim in that paper the extracted bit is supposed to
  implement or approximate.
- The public dataset or reference implementation the anchor was validated
  against.

If no external anchor exists, the extraction stops here. The bit stays in
the source project as engineering, and NEUROSPINE does not lift it. Open an
issue tagged `needs-anchor` to search for one.

### Step 3: re-implement or import into NEUROSPINE

Either:

- **Copy** the code into `instrument/src/neurospine/` (or a plugin under
  `experiments/`) with only the minimal changes needed to fit the harness
  interface. Preserve the source-project header comment naming the file
  path it came from.
- **Re-implement** from scratch, referring only to the external anchor's
  description. Do not read the source project's code during the
  re-implementation. This is the stronger option and is required when the
  bit is small enough that re-implementation costs less than an hour.

### Step 4: run the external check

Write a test at `instrument/tests/verification/test_<slug>_extraction.py`
that:

- Runs the extracted code against a public dataset or reference
  implementation.
- Compares the output to the anchor's published result (or to the
  reference implementation's output on the same input).
- Passes only if the extracted code matches within a documented tolerance.

The tolerance must be justified in the test's docstring. "Numerically
identical" is preferred. "Within the paper's reported standard error" is
acceptable when identity is impossible. "Same sign" is a red flag; document
why it is the best available.

### Step 5: update the evaluation

Fill in the extraction's row in the `Extraction ledger` table (added to
`portfolio/README.md` in the same PR as this ADR). Only then can the
gates the extraction touches move above `unscored`.

## Consequences

- Extraction is now slower than "just copy the file over." This is the
  point. The cost buys immunity from circular errors in prior work.
- Some prior work will have no viable external anchor. That is a signal to
  either find the anchor (best) or keep the bit purely archival (fine).
- The `instrument/tests/verification/` directory becomes the trust boundary
  between "engineering from Aayush's prior work" and "gate-relevant
  behavior in NEUROSPINE."

## Consequences NOT accepted

- We do not forbid reuse. Reuse aggressively; verify externally.
- We do not require that the source project be retired. A source project
  can keep running as its own thing while a bit of it is extracted and
  re-verified here.
