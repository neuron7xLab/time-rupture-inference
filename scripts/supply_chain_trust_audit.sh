#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Supply-chain trust driver (PR O). Offline, stdlib-only Python.
# Runs the Scorecard-honesty gate first, then the fail-closed
# aggregate over every independent supply-chain trust root. Exits
# non-zero if any root fails — no PASS unless all pass.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "=== scorecard honesty (no fabricated score) ==="
python scripts/verify_scorecard_prerequisites.py

echo "=== supply-chain aggregate (fail-closed) ==="
PYTHONPATH=src python -m ctios.supply_chain_audit

echo "SUPPLY-CHAIN TRUST DRIVER :: ALL ROOTS CONSISTENT"
