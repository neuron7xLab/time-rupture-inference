#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Assemble a self-contained packet an external collaborator can take
# away to run the private redacted layer locally. Copies only PUBLIC
# scaffolding; never touches private content (there is none here).
set -euo pipefail
cd "$(dirname "$0")/.."

OUT="${1:-external_reviewer_packet}"
rm -rf "$OUT"
mkdir -p "$OUT"

cp examples/external_reviewer_packet_template.yaml "$OUT/skeleton.yaml"
cp docs/EXTERNAL_VALIDATION_PROTOCOL.md "$OUT/PROTOCOL.md"
cp release/tri-falsify-review-pack-v0.2.0/EXTERNAL_REVIEW_FORM.md "$OUT/REVIEW_FORM.md"
cp release/tri-falsify-review-pack-v0.2.0/CLAIM_BOUNDARY.md "$OUT/CLAIM_BOUNDARY.md"

cat > "$OUT/HOW_TO_RUN.md" <<'EOF'
# How to run (no author needed)

1. Fill skeleton.yaml — REDACTED structure only. No mechanism/data.
2. Implement a local opaque probe (ctios.opaque_probe.OpaqueProbe);
   keep it on YOUR machine, do not commit it.
3. Compile + run + battery:
     PYTHONPATH=src python -m ctios.spec_cli compile skeleton.yaml --out run/
     # wire your probe -> ctios.falsifier_battery.run_falsifier_battery_v2
4. Inspect every emitted file; confirm NO never-share field leaked.
5. Return only: sanitized verdict JSON + spec sha256 + filled
   REVIEW_FORM.md. Nothing private leaves your machine.
EOF

echo "external reviewer packet -> $OUT/"
ls -1 "$OUT"
echo "PREPARE-EXTERNAL-REVIEWER-PACKET :: OK"
