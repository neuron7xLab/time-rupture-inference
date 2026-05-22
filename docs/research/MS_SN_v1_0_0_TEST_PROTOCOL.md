# MS-SN v1.0.0 — Deterministic test protocol

## Boundary

This protocol validates only scaffold-level deterministic checks for PR #74.

It does not validate:
- runtime behavior;
- production readiness;
- biological claims;
- intelligence claims;
- subjective-experience claims;
- empirical MS-SN claims.

## Allowed verdicts
- GREEN
- RED_EXPECTED
- RED_UNEXPECTED
- INVALID_RUN

## Canonical gate
`make ms-sn-prereg-lock && make ms-sn-runtime-red && make ms-sn-runtime-absent-contract && make ms-sn-reproducibility && make ms-sn-scaffold-seal`
