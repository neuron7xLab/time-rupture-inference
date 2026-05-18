#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Non-destructive GCP plan. NEVER creates resources. Refuses GPU.
set -u
mkdir -p artifacts/gcp
OUT=artifacts/gcp/dry_run_plan.txt
PROJECT_ID="${PROJECT_ID:-<unset>}"
ZONE="${ZONE:-europe-west4-a}"
MACHINE="${MACHINE:-e2-standard-4}"
DISK_GB="${DISK_GB:-50}"

{
  echo "CTI-OS v7 — GCP DRY-RUN PLAN (no resources created)"
  echo "generated_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "project_id:    $PROJECT_ID"
  echo "zone:          $ZONE"
  echo "machine_type:  $MACHINE   (CPU-only)"
  echo "disk:          ${DISK_GB}GB balanced persistent disk"
  echo "gpu:           REFUSED (phase-1 policy)"
  echo "external_ip:   none unless ALLOW_EXTERNAL_IP=1"
  echo "labels:        project=cti-os-v7 owner=neuron7xlab phase=cpu cost_guard=enabled"
  echo "resource cost: qualitative — small CPU VM, minutes, deleted post-run ≈ \$0"
  echo "next:          review, then 'APPLY=1 PROJECT_ID=.. make gcp-cpu-run'"
} | tee "$OUT"

if [ "${GPU:-0}" = "1" ]; then
  echo "GPU requested -> REFUSED (phase-1). Exit 1." | tee -a "$OUT"
  exit 1
fi
if [ "${APPLY:-0}" = "1" ]; then
  echo "NOTE: dry_run_plan never creates resources even with APPLY=1." | tee -a "$OUT"
fi
echo "DRY-RUN: PASS (plan written to $OUT, nothing created)"
exit 0
