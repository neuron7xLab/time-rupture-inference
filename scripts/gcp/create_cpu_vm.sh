#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Create a single-shot CPU VM. Fail-closed: requires APPLY=1 + PROJECT_ID
# + ZONE. No GPU. No external IP unless ALLOW_EXTERNAL_IP=1. Idempotent
# guard: refuses if a VM with the same name already exists.
set -eu
APPLY="${APPLY:-0}"
PROJECT_ID="${PROJECT_ID:-}"
ZONE="${ZONE:-}"
MACHINE="${MACHINE:-e2-standard-4}"
DISK_GB="${DISK_GB:-50}"
NAME="${NAME:-cti-os-v7-cpu}"
ALLOW_EXTERNAL_IP="${ALLOW_EXTERNAL_IP:-0}"

die() { echo "FAIL: $1" >&2; exit 1; }
[ "$APPLY" = "1" ]      || die "refusing: pass APPLY=1 to create resources"
[ -n "$PROJECT_ID" ]    || die "PROJECT_ID required"
[ -n "$ZONE" ]          || die "ZONE required"
command -v gcloud >/dev/null 2>&1 || die "gcloud not installed"

echo "CLEANUP COMMAND (run this after the job):"
echo "  APPLY=1 PROJECT_ID=$PROJECT_ID ZONE=$ZONE NAME=$NAME make gcp-cleanup"

if gcloud compute instances describe "$NAME" --project "$PROJECT_ID" --zone "$ZONE" >/dev/null 2>&1; then
  die "instance $NAME already exists (idempotent guard) — cleanup first"
fi

EXTRA="--no-address"
[ "$ALLOW_EXTERNAL_IP" = "1" ] && EXTRA=""

gcloud compute instances create "$NAME" \
  --project "$PROJECT_ID" --zone "$ZONE" \
  --machine-type "$MACHINE" \
  --boot-disk-size "${DISK_GB}GB" --boot-disk-type pd-balanced \
  --no-restart-on-failure --maintenance-policy TERMINATE \
  --labels project=cti-os-v7,owner=neuron7xlab,phase=cpu,cost_guard=enabled \
  $EXTRA
echo "CREATED $NAME (CPU-only, no GPU). Remember the cleanup command above."
