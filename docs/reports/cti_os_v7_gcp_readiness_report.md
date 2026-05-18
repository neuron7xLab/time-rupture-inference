# CTI-OS v7 — GCP Readiness Report

Date: 2026-05-18 (UTC) · Branch: `gcp/cti-os-v7-readiness`

## Files changed / created
- `configs/v7_experiment.yaml`
- `docs/prereg/cti_os_v7_preregistration.md`
- `docs/cloud/gcp_readiness_protocol.md`
- `docs/cloud/gcp_cost_guardrails.md`
- `scripts/run_v7_cpu.py`, `scripts/check_artifacts.py`
- `scripts/gcp/doctor.sh`, `dry_run_plan.sh`, `create_cpu_vm.sh`, `cleanup.sh`
- `tests/test_v7_config.py`, `tests/test_v7_artifact_schema.py`
- `Makefile` (v7 + gcp targets), `.github/workflows/v7-readiness.yml`
- `README.md` (v7 GCP-readiness section), this report

## Commands run (local, no cloud, no spend)
`ruff check src tests scripts` · `mypy` (strict) · `pytest tests`
(91) · `run_v7_cpu.py --mode smoke` · `check_artifacts.py` ·
`gcp/doctor.sh` · `gcp/dry_run_plan.sh` · `gcp/create_cpu_vm.sh`
(fail-closed without APPLY).

## Test results
- ruff: PASS · mypy --strict: PASS (18 files) · pytest: 91 passed
- claims-lint / provenance: PASS · frozen v4/v5 unchanged, v6 RED kept
- v7 smoke: 12 rows (4 models × 3 seeds × 1 shift) → artifacts emitted
- artifact schema: PASS · dry-run: non-destructive PASS
- create_cpu_vm without APPLY=1: correctly REFUSED (fail-closed)

## Readiness status
Local repo gates: **GREEN**. The repo is a deterministic, cost-guarded,
reproducible cloud-run artifact. `gcp-doctor` returns an *actionable*
PASS/FAIL: on a host without the Cloud SDK it FAILs the gcloud rows
**by design** — that is the operator's setup checklist, not a repo
defect.

## Remaining manual Google Cloud steps (operator)
1. Install Cloud SDK; `gcloud auth login`; create project `cti-os-v7`.
2. Link billing; keep Free Trial; create budget (alerts 25/50/80/95%).
3. `make gcp-doctor` until repo-controllable rows PASS.
4. `make gcp-dry-run`; review plan (nothing is created).
5. `PROJECT_ID=cti-os-v7 ZONE=europe-west4-a APPLY=1 make gcp-cpu-run`
   (single session), pull artifacts, `APPLY=1 … make gcp-cleanup`.

## Exact next command for the user
```bash
git checkout gcp/cti-os-v7-readiness
make test && make v7-prereg-check && make v7-cpu-smoke && \
  make v7-artifact-check && make gcp-doctor && make gcp-dry-run
```

## RED risks
- Operator upgrades to Paid billing before a CPU verdict (credit burn).
- Budget mistaken for a hard cap (it is not — guardrails doc).
- GPU enabled in Phase 1 (scripts refuse it).
- VM left running overnight (single-shot + mandatory cleanup mitigate).

## GREEN criteria (all met locally)
test ✓ · v7-prereg-check ✓ · v7-cpu-smoke ✓ · v7-artifact-check ✓ ·
gcp-doctor actionable ✓ · gcp-dry-run non-destructive ✓ ·
v7-readiness workflow present ✓ · cost-guardrails doc ✓ · prereg doc ✓ ·
no resource creation without APPLY=1 ✓

## No unsupported claims
This is readiness *infrastructure*. No scientific v7 verdict is claimed;
the GRU/SSM science run is the next pre-registered step. No
intelligence / cognition / AGI claim is made anywhere.
