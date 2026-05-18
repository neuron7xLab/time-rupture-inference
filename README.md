# CTI-OS · Proof of Life

Minimal falsifiable proof that a temporal-causal agent is *intelligent*
in the operational sense: it learns a hidden inter-event interval from
its own prediction error, and **re-adapts after an unseen regime shift**
— without ever being told the interval, the shift, or its timing.

This kills category 12 of the PFC-CI audit (intelligence injected vs.
intelligence learned): here the solution is *not* handed to the learner.

## The contest

| agent | knows interval? | adapts after T*? | role |
|---|---|---|---|
| `injected` | yes (τ0 hard-wired) | no | strawman, must fail post-shift |
| `last_interval` / `moving_average` / `exp_smoothing` | no | slowly | naive baselines |
| `oracle` | yes (full schedule) | yes | achievable upper bound (regret 0) |
| **`learned_full`** | **no** | **yes, from error** | **the claim** |
| `learned_no_update` / `no_drift` / `no_memory` / `frozen` | no | partially | ablations → necessity |

## Falsifier (pinned before any run)

`prereg/preregistration.yaml` + `prereg/falsifier_contract.yaml`, hashed
into `prereg/sha_pin.txt` and git-committed **before** the experiment.
The gate goes GREEN only if learned beats injected **and** the best
naive baseline on post-shift error, across ≥85% of 16 seeds, with the
error-update mechanism shown necessary by ablation, no hidden-variable
leakage, and stable deterministic replay. Any RED check fails the whole
run and is reported as RED — no tuning, no cherry-picking.

## Run

```bash
make setup
make prereg          # then: git add -A && git commit (pins the falsifier)
make test
make gate            # full multi-seed run + fail-closed verdict
```

Evidence: `evidence/evidence_ledger.jsonl`, `evidence/release_gate.md`,
`evidence/honest_failures.md`, `evidence/metrics_summary.csv`,
`plots/*.png`.

## Scope

PASS ⇒ a learned temporal causal model survives a regime shift in this
synthetic family. It does **not** claim biological fidelity or
cross-environment generality — those are separate falsification
lineages.
