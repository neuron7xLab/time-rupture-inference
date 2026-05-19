#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# One command an external reviewer runs to attack the artifact. Every
# gate below is HARD: a skipped hard gate is a failure. Writes machine-
# and human-readable results. Offline, deterministic.
set -uo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=src

RES="evidence/REVIEWER_ATTACK_RESULT.json"
REP="docs/reports/REVIEWER_ATTACK_REPORT.md"
mkdir -p evidence docs/reports

names=() ; codes=()
gate() {
  local name="$1"; shift
  echo "=== $name ==="
  if "$@"; then c=0; else c=$?; fi
  names+=("$name"); codes+=("$c")
  echo "--- $name exit=$c ---"
}

gate "claims_lint"        python scripts/claims_lint.py
gate "ruff"               ruff check .
gate "pytest"             python -m pytest tests -q
gate "falsifier_stress"   python -m ctios.falsifier_stress --mode full
gate "change_detection_arc" python -m ctios.change_detection_arc
gate "external_adversarial" bash scripts/external_adversarial_demo.sh
gate "indi_demo"          bash scripts/indi_demo.sh

ok=true
{
  echo "{"
  echo "  \"commit\": \"$(git rev-parse HEAD 2>/dev/null || echo unknown)\","
  echo "  \"gates\": {"
  for i in "${!names[@]}"; do
    sep=","; [ "$i" -eq $(( ${#names[@]} - 1 )) ] && sep=""
    pass=$([ "${codes[$i]}" -eq 0 ] && echo true || echo false)
    [ "${codes[$i]}" -eq 0 ] || ok=false
    echo "    \"${names[$i]}\": {\"exit\": ${codes[$i]}, \"pass\": $pass}$sep"
  done
  echo "  },"
  echo "  \"all_hard_gates_pass\": $ok"
  echo "}"
} > "$RES"

{
  echo "# Reviewer Attack Report"
  echo
  echo "commit: \`$(git rev-parse --short HEAD 2>/dev/null || echo unknown)\`"
  echo
  echo "| gate | exit | result |"
  echo "|---|---:|---|"
  for i in "${!names[@]}"; do
    r=$([ "${codes[$i]}" -eq 0 ] && echo PASS || echo FAIL)
    echo "| ${names[$i]} | ${codes[$i]} | $r |"
  done
  echo
  echo "all_hard_gates_pass: **$ok**"
  echo
  echo "A skipped hard gate is treated as FAIL. Status remains"
  echo "CONDITIONALLY_READY until a real external collaborator run is"
  echo "recorded (evidence/external_validation_status.json)."
} > "$REP"

echo
if [ "$ok" = true ]; then
  echo "REVIEWER-ATTACK :: ALL HARD GATES PASSED -> $RES $REP"
  exit 0
fi
echo "REVIEWER-ATTACK :: FAILURE (see $RES)"
exit 1
