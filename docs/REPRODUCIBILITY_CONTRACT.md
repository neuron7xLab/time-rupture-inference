# Reproducibility Contract

A contract for an external reviewer. If a step here does not behave as
written on a clean clone, that is a defect to report — not a quirk to
work around.

## Clean clone path

```bash
git clone https://github.com/neuron7xLab/time-rupture-inference
cd time-rupture-inference
pip install -e ".[dev]"
export PYTHONPATH=src
```

CPU-only, no network, no GPU. Python 3.11–3.13.

## Exact commands

```bash
ruff check src tests scripts
python scripts/claims_lint.py
python scripts/provenance_attest.py
pytest tests -q
python -m ctios.runner --mode full
python -m ctios.causal_runner --mode full
python -m ctios.agent_cli --demo --backend echo_state
# or, one command for all of the above, reviewer-oriented:
bash scripts/conference_smoke.sh
```

## Expected frozen outputs

Byte-identical on any machine:

```
learned post_mae=0.8830 injected=8.0028 oracle=0.7933
gain=0.8680 null_gap=0.0000
tri-agent[echo_state] steps=600 ... regime_shifts=1 first_shift_step=301
```

(The agent's MAE prints alongside; the load-bearing frozen quantities
are the two lines above it and the detected first-shift step.)

## What must not change

The v4 numbers (`0.8830 / 8.0028 / 0.7933`), the v5 numbers
(`0.8680 / 0.0000`), the pinned scientific thresholds, the claim
boundaries, and any preserved RED/GREEN lineage verdict. These are the
invariant register; moving them silently is the primary failure this
apparatus exists to prevent.

## What drift means

If a frozen number differs, the result is not "an update" — it is a
broken invariant or an environment defect. The runner fails closed on
drift. A changed `spec_sha256` for an unchanged claim means a threshold
or assumption was edited; that is detectable by design and must be
explained, not absorbed.

## What counts as evidence

A sealed `FALSIFY_<hid>.json`, a preserved `NEGATIVE_*` artifact with a
reproduction command, a passing `provenance_attest` (sha256 + SPDX),
and the byte-identical frozen runner outputs. Evidence is an artifact,
not a sentence.

## What does not count as evidence

A fluent argument that the claim is true; a benchmark score with no
falsifier; a model's self-evaluation; a green CI run whose gate is not
discriminative; any number that cannot be regenerated from a clean
clone.

## How to extend with a new hypothesis

1. Write a pinned spec (claim / null / assumptions / variables /
   falsifier checks) — see `examples/indi_redacted_cognitive_time.yaml`.
2. Implement a local `probe(thresholds) -> {metric: value}` (kept
   local; never committed if private).
3. Add a discriminative negative-control probe.
4. Call `ctios.falsify.falsify(spec, probe, negative_control=...)`.
5. Inspect the sealed verdict and the proposed `NEXT_<hid>.yaml`;
   decide whether to run it. The engine never runs it for you.

## How to report a failed reproduction

Open an issue with: OS, Python version, the exact command, the full
output, and the diff from the expected frozen lines above. A failed
reproduction is a first-class signal, treated like a sealed negative —
not dismissed.
