# Cyber Hygiene Top-7 Audit — Merge Readiness Pack

## Scope
This pack validates the diff for:
- `tools/cyber_hygiene_audit.py`
- `tests/test_cyber_hygiene_audit.py`
- `evidence/cyber_hygiene_top7.json`

## One-line problem statement
Ensure we can deterministically derive exactly 7 critical recurring hygiene classes from Bandit JSON and fail closed when contract or class coverage breaks.

## Falsifiable hypothesis
If input contract is malformed, required classes are missing, or path traversal manipulates hotspots, the audit must produce `FAIL` (or raise contract error) and tests must fail.

## Invariants
1. `exactly_7_classes == 7`.
2. Required classes include: `B607`, `B603`, `B404`, `B101`, `B105`, `SCRIPTS`, `SRC`.
3. `top_files` ordering is deterministic: `count desc`, then `filename asc`.
4. Traversal-like paths (e.g. `../scripts/x.py`) do not count as `SCRIPTS`/`SRC` hotspot entries.

## Validation commands (reproducible)
```bash
python -m pytest -q tests/test_cyber_hygiene_audit.py
python tools/cyber_hygiene_audit.py --bandit-json /tmp/bandit.json --output evidence/cyber_hygiene_top7.json
python -m pytest -q tests/test_noise_audit.py tests/test_code_quality_audit.py tests/test_cyber_hygiene_audit.py
make cyber-hygiene-audit
```

## CI integration
- The gate is wired into `.github/workflows/ci.yml` as:
  - `pip install bandit==1.8.3`
  - `make cyber-hygiene-audit`
- Policy mode defaults to `must_not_exist`, so any detected targeted class blocks merge.

## Risk notes
- Input size guard (`max_bytes`) is intentionally fail-closed to reduce resource exhaustion exposure.
- Field sanitization drops invalid records (`test_id`, `filename`) instead of trusting scanner output blindly.

## Merge decision
**READY FOR MERGE** when all validation commands are green and generated report shows:
- `status: "PASS"`
- `mode: "must_not_exist"`
- `present_disallowed_classes: []`
- `dropped_invalid_rows: 0`

## Rollback
Single-commit rollback via:
```bash
git revert <commit_sha>
```

## Owner
Security / CTI-OS maintainers.
