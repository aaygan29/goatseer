# NEUROSPINE Instrument Tests

Pytest suite for the per-decision contract (specs/contract-v0.md). All tests
are organized by the fields they validate.

## Test layout

```
tests/
  __init__.py
  test_answer.py
  test_calibrated_confidence.py
  test_abstention_flag.py
  test_loyalty_vector.py
  test_sparse_circuit_id.py
  test_neural_alignment_score.py
  test_honesty_verdict.py
  conftest.py              # fixtures, synthetic ground truth
  utils/
    seed_sweep.py          # n>=5 replication helper
    synthetic_ground_truth.py
```

## Rules

1. **Synthetic first**: Every test of a real-data claim must be preceded by a
   synthetic-ground-truth counterpart using the same assertion logic.
2. **Seed sweep**: Use conftest's `seed_sweep_fixture(n=5)` to run each synthetic
   test over n random seeds (default n=5). A single seed failure causes the
   entire suite to fail.
3. **No real data in CI**: Real-data tests (marked `@pytest.mark.real`) are
   skipped in CI by default. They may be run locally with `pytest -m real`.

Each field module exports a `conftest` submodule that defines fixtures (synthetic
test data, oracle functions, baseline models).
