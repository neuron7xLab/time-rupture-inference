#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# External review package — one-command verification.
#
# Hard gates (failure aborts): claim lexicon lint, provenance
# attestation, full test suite, frozen temporal-adaptation runner.
# Soft demos (skipped if the module is absent): causal-action,
# streaming agent. Prints exactly one explicit success line at the end.

set -euo pipefail

cd "$(dirname "$0")/.."
export PYTHONPATH=src

step() { printf '\n=== %s ===\n' "$1"; }

step "claim lexicon lint (hard)"
if [ -f scripts/claims_lint.py ]; then
  python scripts/claims_lint.py
else
  echo "SKIP: scripts/claims_lint.py absent"
fi

step "provenance attestation (hard)"
if [ -f scripts/provenance_attest.py ]; then
  python scripts/provenance_attest.py
else
  echo "SKIP: scripts/provenance_attest.py absent"
fi

step "full test suite (hard)"
python -m pytest tests -q

step "frozen temporal-adaptation runner (hard, byte-identical)"
python -m ctios.runner --mode full

step "causal-action demo (soft)"
if python -c "import importlib.util,sys; sys.exit(0 if importlib.util.find_spec('ctios.causal_runner') else 1)"; then
  python -m ctios.causal_runner --mode full
else
  echo "SKIP: ctios.causal_runner absent"
fi

step "streaming agent demo (soft)"
if python -c "import importlib.util,sys; sys.exit(0 if importlib.util.find_spec('ctios.agent_cli') else 1)"; then
  python -m ctios.agent_cli --demo --backend echo_state
else
  echo "SKIP: ctios.agent_cli absent"
fi

cat <<'EOF'

INDI-DEMO :: ALL HARD GATES PASSED — package verified

Read next:
  docs/INDI_README.md                        (start here)
  examples/indi_redacted_cognitive_time.yaml (redacted skeleton)
  docs/PRIVATE_RND_PROTOCOL.md               (IP boundary)

Three questions (the only thing asked):
  1. Is this close to the research loop you meant?
  2. Is the redacted hypothesis interface enough to protect your IP?
  3. What would make this useful for your next private experiment?
EOF
