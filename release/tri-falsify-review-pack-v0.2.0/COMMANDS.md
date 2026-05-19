# COMMANDS — exact reviewer path

Clean clone, then:

```bash
pip install -e ".[dev]"
export PYTHONPATH=src
```

## One-command attack (recommended)

```bash
bash scripts/reviewer_attack.sh
```

Runs every hard gate and writes `evidence/REVIEWER_ATTACK_RESULT.json`
+ `docs/reports/REVIEWER_ATTACK_REPORT.md`.

## Individual gates

```bash
python scripts/claims_lint.py                       # claim-boundary scan
ruff check .                                        # style
mypy                                                # types (strict)
PYTHONPATH=src pytest tests -q                      # full suite
PYTHONPATH=src python -m ctios.falsifier_stress --mode full
PYTHONPATH=src python -m ctios.change_detection_arc
bash scripts/external_adversarial_demo.sh
bash scripts/indi_demo.sh
```

## Frozen invariant (must be byte-identical)

```bash
PYTHONPATH=src python -m ctios.runner --mode full
# learned post_mae=0.8830 injected=8.0028 oracle=0.7933
PYTHONPATH=src python -m ctios.causal_runner --mode full
# gain=0.8680 null_gap=0.0000
```

## Readiness (self-honest, not a score to chase)

```bash
PYTHONPATH=src python -m ctios.readiness_score
```

Prints blocking facts FIRST, status SECOND, number LAST. Status cannot
exceed `CONDITIONALLY_READY` until a real external collaborator run is
recorded.
