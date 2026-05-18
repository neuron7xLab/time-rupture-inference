# Architecture

The pipeline and its mapping to real modules. Boxes labeled
*(conceptual)* are a discipline contract, not a separate module; every
other box names code that exists in this repository.

## Pipeline

```
            ┌──────────────────────────────┐
            │  RedactedHypothesisSpec       │  author input
            │  claim · null · assumptions   │  (conceptual: a redacted
            │  · variables · checks         │   YAML skeleton)
            └───────────────┬──────────────┘
                            │
                            ▼
            ┌──────────────────────────────┐
            │  Spec pinning / sha256        │  HypothesisSpec.sha()
            │  (claim+thresholds+checks+    │  src/ctios/falsify.py
            │   assumptions+variables)      │
            └───────────────┬──────────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
   ┌────────────────────┐     ┌────────────────────────┐
   │  Probe (opaque)     │     │  Negative-control probe │
   │  probe(thr)->metrics│     │  must fail the checks   │
   │  (conceptual: local,│     │  src/ctios/falsify.py   │
   │   never committed)  │     └───────────┬────────────┘
   └─────────┬──────────┘                 │
             └───────────────┬────────────┘
                             ▼
            ┌──────────────────────────────┐
            │  FalsifierBattery             │  run_battery()
            │  deterministic · finite ·     │  src/ctios/falsify.py
            │  load-bearing · neg-ctrl-fails│
            └───────────────┬──────────────┘
                            │
                            ▼
            ┌──────────────────────────────┐
            │  Metrics → checks evaluated   │  _eval_checks()
            │  metric op threshold_key      │  src/ctios/falsify.py
            └───────────────┬──────────────┘
                            │
                            ▼
            ┌──────────────────────────────┐
            │  SealedVerdict                │  Verdict +
            │  status·battery·metrics·sha   │  FALSIFY_<hid>.json
            └───────────────┬──────────────┘
                            │
                            ▼
            ┌──────────────────────────────┐
            │  EvidenceLedger               │  evidence/ NEGATIVE_* ,
            │  preserved RED/GREEN, SPDX+sha│  ledger.py,
            │                               │  provenance_attest.py
            └───────────────┬──────────────┘
                            │ non-GREEN
                            ▼
            ┌──────────────────────────────┐
            │  NextExperimentProposal       │  next_experiment() →
            │  tighten survivors ×0.9 ·     │  NEXT_<hid>.yaml
            │  failed boundary = focus      │
            └───────────────┬──────────────┘
                            │
                            ▼
            ┌──────────────────────────────┐
            │  HumanApprovalGate            │  (conceptual + enforced:
            │  auto_run:false · human_review│   skeleton field;
            │  _required:true — never runs  │   engine never executes
            │  the proposal                 │   the proposal)
            └──────────────────────────────┘
```

## Module map

| Pipeline box | Code |
|---|---|
| RedactedHypothesisSpec | `ctios.falsify.HypothesisSpec`; redacted skeleton `examples/indi_redacted_cognitive_time.yaml` (conceptual layer) |
| Spec pinning / sha256 | `HypothesisSpec.sha()`, `falsify.py` |
| Probe / Negative-control | callable arguments to `falsify(...)`; local, not a repo module (conceptual) |
| FalsifierBattery | `ctios.falsify.run_battery` |
| Metrics → checks | `ctios.falsify._eval_checks` |
| SealedVerdict | `ctios.falsify.Verdict`, `falsify(...)` writes `FALSIFY_<hid>.json` |
| EvidenceLedger | `ctios.ledger`, `evidence/`, `scripts/provenance_attest.py`, `provenance_manifest.json` |
| NextExperimentProposal | `ctios.falsify.next_experiment` → `NEXT_<hid>.yaml` |
| HumanApprovalGate | enforced contract: `human_review_required`, `auto_run:false`; engine has no auto-run path |

## Benchmark substrate (the instance the discipline runs on)

| Concern | Code |
|---|---|
| Hidden-rupture environment | `ctios.env`, `ctios.causal_env` |
| Agents / learners | `ctios.agents`, `ctios.agent`, `ctios.causal_agents`, `ctios.v6_precision` |
| Drift trigger | `ctios.drift` |
| Metrics / gates | `ctios.metrics`, `ctios.causal_metrics`, `ctios.gates`, `ctios.causal_gate`, `ctios.contract` |
| Frozen runners | `ctios.runner`, `ctios.causal_runner` |
| Streaming agent CLI | `ctios.agent_cli` (`tri-agent`) |
| Engine CLI | `ctios.falsify_cli` (`tri-falsify`) |

No module above is invented; every name resolves under `src/ctios/`.

## IP-safe platform layer (typed realization)

The same pipeline, as concrete strongly-typed modules for redacted
private hypotheses:

| Pipeline box | Platform module |
|---|---|
| RedactedHypothesisSpec | `ctios.redacted` (dataclasses + structural invariants) |
| Spec pinning / sha256 | `ctios.redacted_io.spec_sha256` (fail-closed on forbidden keys) |
| Probe (opaque) | `ctios.opaque_probe.OpaqueProbe` Protocol + `ProbeResult` |
| FalsifierBattery | `ctios.falsifier_battery.run_falsifier_battery_v2` (10 checks) |
| SealedVerdict | `ctios.spec_compiler` (`BLOCKED_UNTIL_PROBED`) + `sealed_verdict.json` |
| EvidenceLedger | `runs/<demo>/evidence_ledger.jsonl`, `ctios.report` |
| NextExperimentProposal | `next_experiment.yaml` (proposed only, never run) |
| HumanApprovalGate | `ctios.human_gate` + `ctios.review_cli` (append-only audit) |

Drivers: `python -m ctios.spec_cli compile`,
`python -m ctios.platform_demo`, `python -m ctios.review_cli`,
`bash scripts/platform_demo.sh`.
