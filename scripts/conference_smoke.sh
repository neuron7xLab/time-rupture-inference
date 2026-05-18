#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Conference / reviewer smoke: one command, hostile-reviewer oriented.
# Hard gates fail loud. Frozen numbers are printed for direct check
# against docs/REPRODUCIBILITY_CONTRACT.md.

set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=src

g() { printf '\n=== %s ===\n' "$1"; }

g "claim-boundary lexicon (hard)"
python scripts/claims_lint.py

g "provenance attestation — sha256 + SPDX (hard)"
python scripts/provenance_attest.py

g "test suite (hard)"
python -m pytest tests -q

g "frozen positive — v4 temporal adaptation (hard, byte-identical)"
python -m ctios.runner --mode full

g "frozen positive — v5 minimal causal-action (soft)"
if python -c "import importlib.util,sys;sys.exit(0 if importlib.util.find_spec('ctios.causal_runner') else 1)"; then
  python -m ctios.causal_runner --mode full
else
  echo "SKIP: ctios.causal_runner absent"
fi

g "streaming agent — hidden-shift detection (soft)"
if python -c "import importlib.util,sys;sys.exit(0 if importlib.util.find_spec('ctios.agent_cli') else 1)"; then
  python -m ctios.agent_cli --demo --backend echo_state
else
  echo "SKIP: ctios.agent_cli absent"
fi

cat <<'EOF'

TRI-FALSIFY CONFERENCE SMOKE PASSED

Expected frozen numbers (must match exactly, any machine):
  learned post_mae=0.8830 injected=8.0028 oracle=0.7933
  gain=0.8680 null_gap=0.0000
  tri-agent[echo_state] regime_shifts=1 first_shift_step=301

Read next:
  docs/REVIEWER_ONE_PAGER.md   (60-second system identity)
  docs/SYSTEM_CARD.md          (abstraction + boundaries)
  docs/CONTRIBUTION_CLAIMS.md  (original vs prior art)
  docs/OPENAI_STYLE_REVIEW.md  (strongest objections)
EOF
