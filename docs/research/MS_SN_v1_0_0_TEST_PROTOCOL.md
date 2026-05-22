# MS-SN v1.0.0 — Deterministic test protocol

## Boundary
No high-level intelligence or biological-proof claim is validated by this protocol.

## Allowed verdicts
- GREEN
- RED_EXPECTED
- RED_UNEXPECTED
- INVALID_RUN

## Canonical gate
`make ms-sn-prereg-lock && make ms-sn-runtime-red && make ms-sn-runtime-absent-contract && make ms-sn-reproducibility && make ms-sn-scaffold-seal`
