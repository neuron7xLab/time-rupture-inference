# Review Path

Four tracks, increasing cost. Each states the exact files, exact
commands, expected artifacts, expected failure modes, and the **only**
conclusion that is admissible. A stranger must be able to execute
these from a clean clone with no author present.

## Track A — 3-minute trust scan

Goal: decide whether the repo has serious boundaries or only narrative
polish.

Read: [`README.md`](../README.md) ·
[`docs/TRUST_LAYER.md`](TRUST_LAYER.md) ·
[`docs/OPEN_STRUCTURAL_GAPS.md`](OPEN_STRUCTURAL_GAPS.md) ·
[`docs/CLAIM_SOURCE_MATRIX.md`](CLAIM_SOURCE_MATRIX.md).

Admissible conclusion: *"The repository has explicit claim boundaries
and declared open gaps."*
Forbidden conclusion: *"The repository proves real-world validity."*

## Track B — 15-minute evidence scan

Goal: check whether claims resolve to artifacts.

Read: [`evidence/release_gate.md`](../evidence/release_gate.md) ·
[`docs/reports/LINEAGE_STATE.md`](reports/LINEAGE_STATE.md) ·
[`docs/REPRODUCIBILITY_CONTRACT.md`](REPRODUCIBILITY_CONTRACT.md) ·
[`evidence/DOC_TRUST_AUDIT.json`](../evidence/DOC_TRUST_AUDIT.json).

Admissible conclusion: *"The repo preserves reproducible evidence
artifacts and a sealed negative lineage."*
Forbidden conclusion: *"The method generalizes beyond the tested
families."*

## Track C — 45-minute clean-clone reproduction

Goal: run the public reproducibility path. Use the commands already in
[`docs/REPRODUCIBILITY_CONTRACT.md`](REPRODUCIBILITY_CONTRACT.md); do
not invent new ones unless one fails.

```bash
git clone https://github.com/neuron7xLab/time-rupture-inference
cd time-rupture-inference
pip install -e ".[dev]"
export PYTHONPATH=src
ruff check src tests scripts
python scripts/claims_lint.py
python scripts/check_doc_trust.py
python scripts/provenance_attest.py
pytest tests -q
bash scripts/conference_smoke.sh
PYTHONPATH=src python -m ctios.runner --mode full
PYTHONPATH=src python -m ctios.causal_runner --mode full
```

Expected frozen, byte-identical: `learned post_mae=0.8830
injected=8.0028 oracle=0.7933` and `gain=0.8680 null_gap=0.0000`;
claims lint, doc-trust, provenance pass; pytest passes or the failure
is documented with the environment.
Expected failure mode: first-clone environment variance (Python/OS) —
report it as a sealed negative, do not work around it.

Admissible conclusion: *"The public artifact is locally reproducible
on this machine."*
Forbidden conclusion: *"The underlying hypothesis is true."*

## Track D — 2-hour adversarial review

Goal: try to break the apparatus. Each task must fail closed.

Deliberate mutation tests (each must fail closed):

1. **Change a forbidden claim.** Edit a README line to assert a
   forbidden position (e.g. an unsupported general-intelligence claim)
   outside a disclaimer block → `python scripts/claims_lint.py` →
   expect non-zero exit.
2. **Corrupt a `source_id`.** Rename a `source_id` in
   `docs/CLAIM_SOURCE_MATRIX.md` to one absent from
   `evidence/SOURCE_REGISTRY.yaml` (or delete that source) →
   `python scripts/check_doc_trust.py` → expect fail-closed.
3. **Remove an external gap.** Set `GAP_1`/`GAP_2` to CLOSED without
   an evidence bundle, or add a readiness wording that must not pass
   (`README`/docs) while a gap is OPEN →
   `tests/test_structural_gaps.py` and `scripts/check_doc_trust.py`
   must keep readiness/product language blocked (non-zero exit).
4. **Drift a frozen number.** Change a frozen v4/v5 expected value →
   `PYTHONPATH=src python -m ctios.runner --mode full` → expect drift
   failure.
- Also run `bash scripts/external_adversarial_demo.sh` (if present).

Admissible conclusion: *"The apparatus resists selected classes of
interpretive and documentation inflation."*
Forbidden conclusion: *"The apparatus is complete or secure against
all attacks."*
