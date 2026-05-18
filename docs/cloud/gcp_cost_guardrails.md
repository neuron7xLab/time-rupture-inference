# GCP Cost Guardrails — CTI-OS v7

Budgets in Google Cloud are **alerts, not hard caps**. They do not stop
spend. The hard stop is operator discipline + these rules.

## $300 credit preservation policy
The Free-Trial credit is treated as a finite research asset. Phase 1
must cost ≈ $0 (small CPU VM, minutes, deleted immediately). No paid
upgrade until a CPU verdict (GREEN or honest RED) exists.

## Hard stop
**At 80% credit usage: STOP all runs.** No new VM, investigate, do not
"just finish one more". 95% = account-level freeze + manual review.

## Default budget thresholds (alerts)
25% · 50% · 80% · 95%. Configure before any run. Alerts ≠ enforcement.

## Resource rules (fail-closed defaults)
- No persistent GPU VM. No GPU in Phase 1 at all.
- No overnight VM, no notebook-only / always-on workflow.
- No large disk by default (≤ 50GB balanced PD).
- No external IP unless explicitly justified (`ALLOW_EXTERNAL_IP=1`).
- Delete the VM immediately after the run (`gcp-cleanup`).
- Store only compressed artifacts; pull then purge remote.
- Manual human verification before any paid-billing upgrade.

## Why kill-switch must be manual/automated, not "the budget"
A budget alert can fire after spend already happened. Containment =
single-shot VM + mandatory `cleanup.sh` + the 80% hard-stop rule, owned
by the operator, encoded in scripts that fail closed without `APPLY=1`.
