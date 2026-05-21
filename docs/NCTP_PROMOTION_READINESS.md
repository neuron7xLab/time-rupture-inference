# NCTP Promotion Readiness

## Purpose

This document defines the promotion path from the nested prototype package:

```text
src/ctios/nctp_state/**
```

toward a later top-level NCTP runtime surface.

The current package is an executable prototype slice. It is not yet a canonical runtime path and does not replace the CTI-OS release gate.

## Current promoted facts

The following facts are admissible after PR #60:

- TASK-01 prototype computes deterministic multi-horizon projection.
- TASK-02 prototype computes precision-weighted error.
- TASK-03 prototype computes adaptive state update from weighted error, state delta, uncertainty, elapsed time, and memory conflict.
- Packet validation rejects malformed packet sections, including malformed `state`.
- The builder preserves caller-provided elapsed-time variation through horizon alignment.
- A dedicated smoke workflow verifies ruff, mypy strict, packet validation, dt sensitivity, and adaptive-state behavior.

## Current boundary

Not claimed:

- biological fidelity
- causal intervention validity
- canonical CTI-OS replacement
- scientific superiority over v9
- production promotion
- TASK-04 through TASK-07 full implementation

## Promotion stages

### Stage 0: nested prototype

Current state:

```text
src/ctios/nctp_state/**
tools/nctp_state_smoke.py
.github/workflows/nctp-state-smoke.yml
```

Allowed:

- smoke checks
- audit checks
- documentation
- internal API refinement

Forbidden:

- README claim expansion
- canonical runner replacement
- provenance root expansion by implication

### Stage 1: promotion readiness audit

Required command:

```bash
PYTHONPATH=src python tools/nctp_promotion_audit.py
```

Pass condition:

```text
packet contract, adaptive-state behavior, and dt sensitivity all pass.
```

### Stage 2: top-level runtime promotion PR

A future promotion PR may introduce:

```text
src/ctios/nctp_packet.py
src/ctios/nctp_runtime.py
tests/test_nctp_packet.py
tests/test_nctp_runtime.py
docs/NCTP_RUNTIME_STATUS.md
```

That PR must also update:

```text
README.md test count
provenance_manifest.json
```

Only through authorized repository tools:

```bash
python tools/update_readme_test_count.py --write
PYTHONPATH=src python scripts/provenance_attest.py --write
```

### Stage 3: canonical integration decision

Canonical integration requires:

- pytest coverage
- mypy strict pass
- provenance pass
- README count sync
- smoke pass
- promotion audit pass
- no release-gate replacement without explicit claim boundary update

## Audit command

```bash
PYTHONPATH=src python tools/nctp_promotion_audit.py
```

The audit verifies:

- seven task specs are declared
- valid prototype packet passes validation
- malformed `state=None` fails validation
- missing `state.s_prev` fails validation
- changed stream scores above stable stream
- changed stream crosses TASK-03 label threshold
- changed stream increases reset probability
- high elapsed-time packet scores above low elapsed-time packet

## Review rule

Promotion is blocked if any of the following occurs:

- top-level runtime added without provenance update
- pytest count changed without README update
- README claims expanded without evidence
- TASK-03 ignores input `dt`
- packet validator accepts malformed `state`
- canonical runner imports prototype code without promotion PR

## Boundary

This document is a promotion-control artifact. It does not expand scientific claims.
