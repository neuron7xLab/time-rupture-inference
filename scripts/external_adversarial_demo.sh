#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# WP6 — external adversarial portability demo. Offline, deterministic.
# Hard gates fail loud; the exact success line is asserted by CI.

set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=src

g() { printf '\n=== %s ===\n' "$1"; }

g "1. ruff"
ruff check src tests scripts

g "2. claims lint (extended scope)"
python scripts/claims_lint.py

g "3. adversarial / family / lint-scope tests"
python -m pytest tests/test_adversarial_probes.py \
  tests/test_benchmark_families.py tests/test_claims_lint_scope.py -q

g "4. falsifier stress (fail-closed)"
python -m ctios.falsifier_stress --mode full

g "5. evidence artifact exists"
ls evidence/ADVERSARIAL_PORTABILITY_*.json >/dev/null

g "6. report exists"
test -f docs/ADVERSARIAL_PORTABILITY_REPORT.md

# soft gates — never fatal
g "soft: indi_demo"
[ -f scripts/indi_demo.sh ] && bash scripts/indi_demo.sh >/dev/null 2>&1 \
  && echo "indi_demo OK" || echo "indi_demo SKIP/soft-fail"
g "soft: conference_smoke"
[ -f scripts/conference_smoke.sh ] && \
  bash scripts/conference_smoke.sh >/dev/null 2>&1 \
  && echo "conference_smoke OK" || echo "conference_smoke SKIP/soft-fail"

echo
echo "EXTERNAL-ADVERSARIAL-DEMO :: ALL HARD GATES PASSED — portability stress verified"
