# time-rupture-inference — Demonstration Script

A linear, reproducible walk-through. Every step prints a verifiable
number; nothing requires trusting the presenter. ~3 minutes on a laptop,
CPU-only, no network.

## 0. Setup
```
git clone https://github.com/neuron7xLab/time-rupture-inference
cd time-rupture-inference && pip install -e ".[dev]"
export PYTHONPATH=src
```

## 1. The whole contract is green
```
ruff check src tests scripts        # style
mypy                                # --strict, 38 files
python scripts/claims_lint.py       # no claim inflation
python scripts/provenance_attest.py # sha256 + SPDX; external scan OPEN
pytest tests -q                     # 150 tests
```
Expected: every line PASS / 150 passed.

## 2. The surviving positive (S1) — frozen, byte-identical
```
python -m ctios.runner --mode full
```
Expected (must be exactly this, on any machine):
`learned post_mae=0.8830 injected=8.0028 oracle=0.7933`,
`win-rate vs injected=1.000 vs best-naive=1.000`, verdict GREEN.

## 3. Causal-action (S2)
```
python -m ctios.causal_runner --mode full
```
Expected: `gain=0.8680 null_gap=0.0000 win_no=1.000 win_rnd=1.000`.

## 4. The instrument (S4) and the honest negative (S5)
```
python scripts/run_v8_4_rederived_diagnostic.py   # GREEN: h2r 0.185 <= 0.35
python scripts/run_v9_learned_diagnostic.py        # RED: learned 5.92, h2r 6.47
```
Point: S4 proves the task is solvable (causal floor reachable); S5
shows a generic learner does NOT solve it — a preserved, quantified
negative, not a failure to hide.

## 5. The runnable agent (S6)
```
python -m ctios.agent_cli --demo --backend echo_state
# stderr: steps=600 mae~0.93 regime_shifts=1 first_shift_step=301
python -m ctios.agent_cli --file YOUR.csv --backend adaptive
```
The agent runs on any numeric stream, adapts online, flags the regime
shift (demo: detects it at step 301; true shift at 300).

## 6. The point of the demo

Not "look how strong the model is". The demonstrable claim is the
**discipline**: a chain of preserved negatives + one frozen positive +
one validated instrument + one honest learner-negative, every number
reproducible from a clean clone, no threshold ever tuned to green.
Full state: `docs/SPEC.md`, `docs/reports/LINEAGE_STATE.md`.
