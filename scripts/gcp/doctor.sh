#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# GCP readiness doctor. Read-only by default. Never enables APIs unless
# APPLY=1. Prints a PASS/FAIL table; exit 1 if any hard check FAILs.
set -u
APPLY="${APPLY:-0}"
ALLOW_DIRTY="${ALLOW_DIRTY:-0}"
fail=0
row() { printf '%-34s %s\n' "$1" "$2"; }
chk() { if eval "$2" >/dev/null 2>&1; then row "$1" "PASS"; else row "$1" "FAIL"; fail=1; fi; }

echo "=== CTI-OS v7 GCP doctor (read-only unless APPLY=1) ==="
chk "gcloud installed"            "command -v gcloud"
chk "python3 >= 3.11"             "python3 -c 'import sys;raise SystemExit(0 if sys.version_info[:2]>=(3,11) else 1)'"
chk "git repo"                    "git rev-parse --is-inside-work-tree"
if [ "$ALLOW_DIRTY" = "1" ]; then
  row "git clean tree" "SKIP (ALLOW_DIRTY=1)"
else
  chk "git clean tree"            "test -z \"\$(git status --porcelain)\""
fi
chk "disk free > 2GB"             "test \$(df -Pk . | awk 'NR==2{print \$4}') -gt 2000000"

if command -v gcloud >/dev/null 2>&1; then
  acct=$(gcloud auth list --filter=status:ACTIVE --format='value(account)' 2>/dev/null || true)
  proj=$(gcloud config get-value project 2>/dev/null || true)
  [ -n "$acct" ] && row "gcloud active account" "PASS ($acct)" || { row "gcloud active account" "FAIL (run: gcloud auth login)"; fail=1; }
  [ -n "$proj" ] && [ "$proj" != "(unset)" ] && row "gcloud active project" "PASS ($proj)" || { row "gcloud active project" "FAIL (gcloud config set project)"; fail=1; }
  row "billing status" "MANUAL (verify Free Trial in console; budgets are alerts not caps)"
  if [ "$APPLY" = "1" ]; then
    row "compute API" "$(gcloud services enable compute.googleapis.com >/dev/null 2>&1 && echo ENABLED || echo FAIL)"
  else
    row "compute API" "NOT ENABLED (pass APPLY=1 to enable compute.googleapis.com)"
  fi
else
  row "gcloud account/project/api" "SKIP (gcloud absent — install Cloud SDK)"
fi

echo "=== phase-1 policy: CPU-only, no GPU, no paid run without APPLY=1 ==="
[ "$fail" -eq 0 ] && echo "DOCTOR: PASS" || echo "DOCTOR: FAIL (resolve rows above)"
exit "$fail"
