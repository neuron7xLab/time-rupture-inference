# MS-SN v1.0.0 — Merge checklist for PR #74

Merge is allowed only if all conditions are true:

- [ ] PR remains scaffold-only.
- [ ] `src/ctios/ms_sn_runtime.py` is absent.
- [ ] `configs/ms_sn_v1_0_0.sha256` matches `configs/ms_sn_v1_0_0.yaml`.
- [ ] `evidence/ms_sn_v1_0_0/manifest.json` validates as `SCAFFOLD_ONLY`.
- [ ] No runtime-green terminology exists.
- [ ] No production, biological, intelligence, subjective-experience, or empirical validation claim exists.
- [ ] README contains no hardcoded numeric test-count badge or prose count.
- [ ] NCTP StrEnum change is documented as API normalization only.
- [ ] CI matrix and Makefile targets are synchronized.
- [ ] PR does not modify unrelated generated evidence outputs.
- [ ] MS-SN files are covered by provenance manifest or explicitly excluded with rationale.

Required commands:

```bash
make ms-sn-audit
PYTHONPATH=src pytest tests -q
```
