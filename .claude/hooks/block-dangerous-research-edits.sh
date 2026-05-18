#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# PreToolUse guard for TRI-Falsify research integrity.
# Reads the hook JSON on stdin. Exit 2 = block (reason on stderr).
#
# Blocks:
#   1. rm -rf / destructive recursive deletes
#   2. edits/writes to frozen evidence artifacts unless the request
#      carries the literal token PR21_ALLOW_FROZEN_TOUCH
#   3. network download (curl/wget/pip download/requests.get) in a
#      command — CI/tests must stay offline & deterministic
set -euo pipefail

payload="$(cat || true)"
export HOOK_PAYLOAD="$payload"

field() {  # $1 = dotted path into the hook JSON; pure-python, no jq
  HOOK_PATH="$1" python3 -c '
import json, os, sys
try:
    d = json.loads(os.environ.get("HOOK_PAYLOAD", ""))
except Exception:
    sys.exit(0)
cur = d
for k in os.environ.get("HOOK_PATH", "").split("."):
    if isinstance(cur, dict) and k in cur:
        cur = cur[k]
    else:
        cur = ""
        break
print(cur if isinstance(cur, str) else json.dumps(cur))
' 2>/dev/null || true
}

tool="$(field tool_name)"
cmd="$(field tool_input.command)"
fpath="$(field tool_input.file_path)"
blob="$payload"

deny() { echo "BLOCKED by PR21 research-integrity hook: $1" >&2; exit 2; }

# 1. destructive recursive delete
if printf '%s' "$cmd" | grep -Eq 'rm[[:space:]]+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r|-rf|-fr)'; then
  deny "destructive 'rm -rf' is not permitted. Delete specific paths explicitly."
fi

# 2. frozen-evidence protection
allow_frozen=0
if printf '%s' "$blob" | grep -q 'PR21_ALLOW_FROZEN_TOUCH'; then allow_frozen=1; fi
if [ "${PR21_ALLOW_FROZEN_TOUCH:-}" = "1" ]; then allow_frozen=1; fi
frozen_re='evidence/(release_gate\.md|evidence_ledger\.jsonl|metrics_summary\.csv|v5_causal|NEGATIVE_RESULT_|V8_|baseline)|FROZEN|cti-os-v[0-9]'
if [ "$allow_frozen" -eq 0 ]; then
  if printf '%s' "$fpath" | grep -Eq "$frozen_re"; then
    deny "edit to a frozen/preserved evidence artifact ('$fpath'). Add the literal token PR21_ALLOW_FROZEN_TOUCH to the request to override intentionally."
  fi
  if printf '%s' "$cmd" | grep -Eq "(>|>>|tee|sed -i|truncate).*($frozen_re)"; then
    deny "command writes to a frozen/preserved evidence artifact. Override with PR21_ALLOW_FROZEN_TOUCH."
  fi
fi

# 3. network egress inside a command
if printf '%s' "$cmd" | grep -Eq '(^|[^a-zA-Z])(curl|wget)([[:space:]]|$)|pip[[:space:]]+download|pip[[:space:]]+install[[:space:]]+--index-url|requests\.get|urllib\.request|httpx\.|aiohttp'; then
  deny "network egress detected in command. Tests/CI must run offline and deterministic."
fi

exit 0
