#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Delete ONLY resources carrying the exact CTI-OS v7 labels. Requires
# APPLY=1. Shows the list before deleting. No wildcard deletion ever.
set -eu
APPLY="${APPLY:-0}"
PROJECT_ID="${PROJECT_ID:-}"
ZONE="${ZONE:-}"
mkdir -p artifacts/gcp
LOG=artifacts/gcp/cleanup_log.txt
FILTER='labels.project=cti-os-v7 AND labels.owner=neuron7xlab'

die() { echo "FAIL: $1" >&2; exit 1; }
[ -n "$PROJECT_ID" ] || die "PROJECT_ID required"
command -v gcloud >/dev/null 2>&1 || die "gcloud not installed"

echo "Resources matching CTI-OS v7 labels (project=$PROJECT_ID):" | tee "$LOG"
gcloud compute instances list --project "$PROJECT_ID" \
  --filter="$FILTER" --format='table(name,zone,status)' 2>&1 | tee -a "$LOG"

if [ "$APPLY" != "1" ]; then
  echo "DRY: pass APPLY=1 to actually delete the listed (labelled) resources." | tee -a "$LOG"
  exit 0
fi

names=$(gcloud compute instances list --project "$PROJECT_ID" \
  --filter="$FILTER" --format='value(name,zone)' 2>/dev/null || true)
[ -z "$names" ] && { echo "nothing labelled to delete." | tee -a "$LOG"; exit 0; }
echo "$names" | while read -r n z; do
  [ -n "$n" ] || continue
  echo "deleting $n ($z)" | tee -a "$LOG"
  gcloud compute instances delete "$n" --project "$PROJECT_ID" --zone "$z" --quiet 2>&1 | tee -a "$LOG"
done
echo "CLEANUP DONE — log: $LOG" | tee -a "$LOG"
