# CI Baseline Snapshot (Phase 0 — closed late, honestly)

This artifact was a **pre-gate** that should have preceded the `ci.yml`
edit in PR #34. It did not. This is the honest closure: the snapshot
is recorded now, explicitly marked as produced *after* the change it
should have preceded — not back-dated, not pretended.

| field | value |
|---|---|
| commit at PR #34 merge | `d597270` |
| this PR base commit | `d5972700c34f457583e343509faf04850dcea850` |
| Python | 3.12.3 |
| workflows | ci, conference-smoke, indi-demo-gate, platform-demo, v7-readiness |
| `ci.yml` sha256 (pre-this-PR) | `0e48ffec…a882b` |
| loose `pip install` lines | 2 |
| `fetch-depth: 0` occurrences | 2 |
| setup-python cache | disabled |
| mypy in CI | bare `mypy` → **fixed here to `mypy --strict src/ctios`** |
| lock files present | `requirements-lock.txt` (exists — the v2 premise "no lock" was partly wrong; recorded) |
| Node deprecation annotations | not measured; no fake env added |
| verifier pins | 13 |
| external validation | `EXTERNAL_RUN_PENDING` |

Machine copy: `evidence/CI_BASELINE_SNAPSHOT.json`. Remaining CI phases
are tracked, with status, in `docs/DEBT_LEDGER.md`.
