# GCP Readiness Protocol — CTI-OS v7 (CPU-first)

The repo, not Google, is the source of truth. Google is only an
execution surface. No paid run until every local gate is GREEN.

## Project preparation
1. Create a dedicated project (e.g. `cti-os-v7`). Isolated billing.
2. Keep **Free Trial** ($300 / 90 days) until the CPU phase proves the
   model is worth power. Under Free Trial: no GPU, limited Marketplace
   and quota — this is acceptable for Phase 1.
3. Do **not** upgrade to Paid billing until a GREEN/RED CPU verdict
   exists. Unused credit is preserved to the end of the 90 days.

## Billing budget requirement
A Cloud Billing **budget is required** before any run. Critical:
**budgets are alerts, not hard caps** — they do not stop spend. Hard
stop is enforced manually/automatically per
`docs/cloud/gcp_cost_guardrails.md`.

## CPU-first policy
Phase 1: `e2-standard-4` / `n2-standard-4`, 50GB balanced PD, no GPU,
no external IP unless justified, VM deleted after the run.

## GPU unlock conditions (future phase, manual)
All true: (1) CPU phase produced GREEN or honest RED with artifacts;
(2) explicit cost re-budget; (3) documented separate prereg; (4) manual
operator action. GPU is never the default.

## Required APIs
`compute.googleapis.com` (Phase 1). Listed by `doctor.sh`, enabled only
when the operator passes `APPLY=1` — never blindly.

## Manual console steps (operator)
1. Create project, link billing.
2. Create budget with thresholds 25/50/80/95% (alerts).
3. Run `make gcp-doctor` → resolve every FAIL.
4. `make gcp-dry-run` → review non-destructive plan.
5. Only then `APPLY=1 ... make gcp-cpu-run`.

## Rollback procedure
`APPLY=1 make gcp-cleanup` deletes only CTI-OS-labelled resources after
showing the list. No wildcard deletion.

## Shutdown procedure
VM is single-shot: created → run → artifacts pulled → deleted in the
same operator session. No overnight VM, no persistent notebook.

## Artifact download procedure
`gcloud compute scp` the compressed `artifacts/v7` tarball back, verify
`check_artifacts.py` PASS locally, then delete the VM.

## Operational checklist (exact)
- [ ] local: `make test v7-prereg-check v7-cpu-smoke v7-artifact-check` PASS
- [ ] `make gcp-doctor` actionable PASS/FAIL reviewed
- [ ] budget created (alerts) + guardrails read
- [ ] `make gcp-dry-run` plan reviewed, no resources created
- [ ] operator runs `APPLY=1 make gcp-cpu-run` (single session)
- [ ] artifacts pulled + `check_artifacts.py` PASS
- [ ] `APPLY=1 make gcp-cleanup` — VM deleted, cleanup log written
