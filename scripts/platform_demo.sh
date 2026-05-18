#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# IP-safe falsification platform — end-to-end interface demo.
# Compile a redacted hypothesis, run a deterministic mock opaque probe,
# run the adversarial battery v2, seal a verdict, write the report.
# The mock probe makes NO scientific claim; it exercises the loop.

set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=src

SPEC="examples/indi_redacted_cognitive_time.yaml"
OUT="runs/platform_demo"

g() { printf '\n=== %s ===\n' "$1"; }

g "compile redacted hypothesis (no probe, no verdict)"
python -m ctios.spec_cli compile "$SPEC" --out runs/spec_demo

g "run platform loop (compile -> mock probe -> battery v2 -> sealed)"
python -m ctios.platform_demo --spec "$SPEC" --out "$OUT"

g "human gate — next experiment is NOT runnable until approved"
python -m ctios.review_cli status "$OUT" || true
python -m ctios.review_cli approve "$OUT" --reviewer local \
  --reason "interface demo: battery reviewed"
python -m ctios.review_cli seal "$OUT" --reviewer local \
  --reason "verdict sealed for demo"

cat <<EOF

TRI-FALSIFY PLATFORM DEMO PASSED

Artifacts in $OUT:
  compiled_spec.json  probe_result.json  falsifier_battery.json
  sealed_verdict.json  evidence_ledger.jsonl  next_experiment.yaml
  human_gate_audit.jsonl  REVIEW_REPORT.md

The mock probe is interface-only — no scientific claim. A real
collaborator swaps it for a local opaque probe; the mechanism and
data never enter this repository.
EOF
