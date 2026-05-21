<!-- claims:disclaimer -->
# NCTP-1 Runtime Status (Deterministic Scaffold Boundary)

## One-line problem
Establish a fail-closed, deterministic runtime that emits validator-safe NCTP packets while preventing overclaim beyond implemented task logic.

## Implemented vs placeholder scope

- **Implemented prototypes:** TASK-01, TASK-02, TASK-03, TASK-04.
- **Packet-compatible placeholders only:** TASK-05, TASK-06, TASK-07.

No causal, episodic-memory retrieval, or regime-extrapolation validity claim is made for TASK-05..07 in the current runtime.

## Contract invariants (enforced)

1. Top-level packet sections must match schema exactly.
2. Unknown top-level/section keys are rejected.
3. `forecast.horizons` must be non-empty positive integers.
4. `drift.drift_score` must be finite numeric.
5. `causal_delay.delay_distribution` rows must be finite and normalized.

## Evidence commands

```bash
PYTHONPATH=src pytest tests/test_nctp_packet.py tests/test_nctp_runtime.py -q
PYTHONPATH=src pytest tests -q
```

## Falsifiable guardrails

- If malformed packet keys pass validation, boundary is broken.
- If NaN/inf passes drift score checks, numeric guard is broken.
- If non-normalized delay distribution passes, causal-delay contract is broken.

## Current interpretation boundary

This runtime is a deterministic baseline scaffold for integration and auditing.
It is not a claim of complete NCTP-1 functional realization.

<!-- claims:end -->
