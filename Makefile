PY := python3
export PYTHONPATH := src

.PHONY: setup prereg test run-baselines run-learned run-falsification ledger gate automate all \
        v7-prereg-check v7-cpu-smoke v7-artifact-check v7-verdict v7-diagnostics gcp-doctor gcp-dry-run gcp-cpu-run gcp-cleanup

setup:
	$(PY) -m pip install -q numpy matplotlib pyyaml pytest

prereg:
	$(PY) scripts_prereg.py

test:
	$(PY) -m pytest tests -q

run-baselines:
	$(PY) -m ctios.runner --mode baselines

run-learned:
	$(PY) -m ctios.runner --mode learned

run-falsification:
	$(PY) -m pytest tests/test_falsification_battery.py -q

ledger:
	@cat evidence/evidence_ledger.jsonl | tail -n 3

gate: test
	$(PY) -m ctios.runner --mode full

automate:
	$(PY) -m ctios.automation

# --- CTI-OS v7 GCP-readiness (CPU-first, no paid run without APPLY=1) ---
v7-prereg-check:
	@test -f docs/prereg/cti_os_v7_preregistration.md || (echo "FAIL: v7 prereg missing" && exit 1)
	$(PY) -m pytest tests/test_v7_config.py tests/test_v7_artifact_schema.py -q

v7-cpu-smoke:
	$(PY) scripts/run_v7_cpu.py --mode smoke

v7-artifact-check:
	$(PY) scripts/check_artifacts.py

v7-verdict:
	$(PY) scripts/v7_verdict.py

gcp-doctor:
	@bash scripts/gcp/doctor.sh

gcp-dry-run:
	@bash scripts/gcp/dry_run_plan.sh

gcp-cpu-run:
	@bash scripts/gcp/create_cpu_vm.sh

gcp-cleanup:
	@bash scripts/gcp/cleanup.sh

all: test gate

v7-diagnostics:
	$(PY) scripts/v7_diagnostics.py
