#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Deep mechanism integrity gate. Collector: set -uo (allowlisted in
# ctios.code_quality_audit) so every gate runs and is recorded; the
# script still exits non-zero if any hard gate fails. Exit code is NOT
# accepted alone — required artifacts are asserted.
set -uo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=src

names=(); codes=()
g() { local n="$1"; shift; echo "=== $n ==="; if "$@"; then c=0; else c=$?; fi
      names+=("$n"); codes+=("$c"); echo "--- $n exit=$c ---"; }

g claims_lint            python scripts/claims_lint.py
g ruff                   ruff check .
g mypy                   mypy
g pytest                 python -m pytest tests -q
g code_quality_audit     python -m ctios.code_quality_audit
g mechanism_inventory    python -m ctios.mechanism_inventory
g test_value_audit       python -m ctios.test_value_audit
g falsifier_stress       python -m ctios.falsifier_stress --mode full
g change_detection_arc   python -m ctios.change_detection_arc
g reviewer_attack        bash scripts/reviewer_attack.sh

# Hard semantic guards — artifact + status, not just exit codes.
g artifact_assertions    python -m ctios.artifact_assertions
g deep_probes            python -m pytest tests/test_deep_adversarial_probes.py -q
g external_pending       python - <<'PY'
import json, sys
from pathlib import Path
sys.path.insert(0, "src")
from ctios.external_validation import real_external_run_attested
s = json.loads(Path("evidence/external_validation_status.json").read_text())
assert s["status"] == "EXTERNAL_RUN_PENDING", "status must stay PENDING"
assert real_external_run_attested() is False, "no real external run yet"
print("external validation correctly PENDING")
PY

ok=true
for c in "${codes[@]}"; do [ "$c" -eq 0 ] || ok=false; done

{
  echo "{"
  echo "  \"commit\": \"$(git rev-parse HEAD 2>/dev/null || echo unknown)\","
  echo "  \"gates\": {"
  for i in "${!names[@]}"; do
    sep=,; [ "$i" -eq $(( ${#names[@]} - 1 )) ] && sep=
    p=$([ "${codes[$i]}" -eq 0 ] && echo true || echo false)
    echo "    \"${names[$i]}\": {\"exit\": ${codes[$i]}, \"pass\": $p}$sep"
  done
  echo "  },"
  echo "  \"all_hard_gates_pass\": $ok,"
  echo "  \"readiness\": \"CONDITIONALLY_READY_HARDENED\""
  echo "}"
} > evidence/DEEP_MECHANISM_AUDIT_RESULT.json

{
  echo "# Deep Mechanism Audit Report"
  echo
  echo "commit: \`$(git rev-parse --short HEAD 2>/dev/null || echo unknown)\`"
  echo
  echo "| gate | exit | result |"; echo "|---|---:|---|"
  for i in "${!names[@]}"; do
    r=$([ "${codes[$i]}" -eq 0 ] && echo PASS || echo FAIL)
    echo "| ${names[$i]} | ${codes[$i]} | $r |"
  done
  echo
  echo "all_hard_gates_pass: **$ok**"
  echo
  echo "readiness: CONDITIONALLY_READY_HARDENED (READY requires a real"
  echo "external collaborator run with a valid proof bundle)."
} > docs/reports/DEEP_MECHANISM_AUDIT_REPORT.md

echo
if [ "$ok" = true ]; then
  echo "DEEP-MECHANISM-AUDIT :: ALL HARD GATES PASSED"
  exit 0
fi
echo "DEEP-MECHANISM-AUDIT :: FAILURE"
exit 1
