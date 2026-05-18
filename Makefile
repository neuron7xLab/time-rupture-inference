PY := python3
export PYTHONPATH := src

.PHONY: setup prereg test run-baselines run-learned run-falsification ledger gate automate all

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

all: test gate
