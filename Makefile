PY := python3
export PYTHONPATH := src

.PHONY: setup prereg test run-baselines run-learned run-falsification ledger gate automate all \
        v7-prereg-check v7-cpu-smoke v7-artifact-check v7-verdict v7-diagnostics v8-scalar-inexpr v8-1-derive v8-1-diagnostic v8-2-diagnostic gcp-doctor gcp-dry-run gcp-cpu-run gcp-cleanup

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

v8-scalar-inexpr:
	$(PY) scripts/run_scalar_inexpressibility_diagnostic.py

v8-1-derive:
	$(PY) scripts/derive_v8_1_trigger_frequency.py

v8-1-diagnostic:
	$(PY) scripts/run_v8_1_scalar_inexpressibility_diagnostic.py

v8-2-diagnostic:
	$(PY) scripts/run_v8_2_trigger_scoped_diagnostic.py

v8-3-diagnostic:
	$(PY) scripts/run_v8_3_correct_history_diagnostic.py

v8-4-diagnostic:
	$(PY) scripts/run_v8_4_rederived_diagnostic.py

v9-learned:
	$(PY) scripts/run_v9_learned_diagnostic.py

agent:
	$(PY) -m ctios.agent_cli --demo

falsify:
	$(PY) -m ctios.falsify_cli

.PHONY: noise-audit
NOISE_AUDIT_DATE ?= $(shell date -u +%F)
OUTPUT_DIR := evidence/noise_hygiene

noise-audit:
	@mkdir -p $(OUTPUT_DIR)
	python tools/noise_audit.py \
		--enforce \
		--output $(OUTPUT_DIR)/latest.json \
		--snapshot-tag $(NOISE_AUDIT_DATE) \
		--policy-file .auditignore.json


PYTEST ?= pytest
SEED ?= 1729

.PHONY: ms-sn-prereg-lock ms-sn-runtime-absent-contract ms-sn-runtime-red ms-sn-reproducibility ms-sn-scaffold-seal ms-sn-runtime-seal ms-sn-claim-boundary

ms-sn-prereg-lock:
	$(PY) scripts/ms_sn_evidence.py --config configs/ms_sn_v1_0_0.yaml --expected-config-hash configs/ms_sn_v1_0_0.sha256

ms-sn-runtime-red:
	PYTHONPATH=src $(PYTEST) tests/test_ms_sn_red.py -q

ms-sn-runtime-absent-contract:
	PYTHONPATH=src $(PYTEST) tests/test_ms_sn_runtime_absent_contract.py -q

ms-sn-reproducibility:
	PYTHONPATH=src $(PYTEST) tests/test_ms_sn_reproducibility.py -q

ms-sn-sensitivity-grid:
	PYTHONPATH=src $(PYTEST) tests/test_ms_sn_reproducibility.py -q

ms-sn-scaffold-seal:
	@test -f evidence/ms_sn_v1_0_0/manifest.json
	$(PY) scripts/ms_sn_evidence.py --validate-scaffold evidence/ms_sn_v1_0_0/manifest.json


ms-sn-runtime-seal:
	@if [ ! -f evidence/ms_sn_v1_0_0/runtime_manifest.json ]; then \
		echo "FAILURE: runtime_manifest.json absent; runtime validation is out of scope for PR #74 and must fail closed."; \
		exit 1; \
	fi
	$(PY) scripts/ms_sn_evidence.py --validate-runtime evidence/ms_sn_v1_0_0/runtime_manifest.json


ms-sn-claim-boundary:
	PYTHONPATH=src $(PYTEST) tests/test_ms_sn_claim_boundary.py tests/test_nctp_role_boundary_doc.py -q

.PHONY: ms-sn-audit

ms-sn-audit:
	$(MAKE) ms-sn-prereg-lock
	$(MAKE) ms-sn-runtime-absent-contract
	$(MAKE) ms-sn-runtime-red
	$(MAKE) ms-sn-reproducibility
	$(MAKE) ms-sn-scaffold-seal
	$(MAKE) ms-sn-claim-boundary
	PYTHONPATH=src $(PYTEST) tests/test_ms_sn_*.py -q
	PYTHONPATH=src $(PYTEST) tests/test_nctp_role_*.py -q
