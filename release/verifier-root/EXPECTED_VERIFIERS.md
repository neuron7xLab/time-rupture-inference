# Expected Verifiers (the pinned trust set)

These 13 files are pinned in `verifier_manifest.lock`. Each can
silently weaken protection if mutated unnoticed, so each requires a
manifest update + `docs/reports/VERIFIER_CHANGE_REPORT.md` rationale.

| file | what it protects |
|---|---|
| `scripts/claims_lint.py` | claim-boundary scan |
| `scripts/provenance_attest.py` | sha256 + SPDX provenance |
| `scripts/reviewer_attack.sh` | one-command reviewer hard gates |
| `scripts/deep_mechanism_audit.sh` | 13-gate deep integrity audit |
| `src/ctios/readiness_score.py` | self-honest status (no candy score) |
| `src/ctios/external_validation.py` | real-external-run proof bundle |
| `src/ctios/artifact_assertions.py` | exit-code ≠ evidence |
| `src/ctios/code_quality_audit.py` | executable code-quality audit |
| `src/ctios/mechanism_inventory.py` | every CORE has a test |
| `src/ctios/test_value_audit.py` | no weak/decorative test as proof |
| `src/ctios/deep_adversarial_probes.py` | 8 pseudo-mechanism probes |
| `tools/check_verifier_manifest_static.py` | the independent root itself |
| `.github/workflows/ci.yml` | the PR-blocking gate definition |

The static checker pins *itself* so a reviewer running it from outside
detects tampering of the checker too. The generator
(`tools/verifier_manifest.py`) is convenience; the static checker is
the root and is independently tested.
