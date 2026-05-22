<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/neuron7xLab/time-rupture-inference/main/.github/assets/banner-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/neuron7xLab/time-rupture-inference/main/.github/assets/banner-light.svg">
  <img alt="time rupture inference" src="https://raw.githubusercontent.com/neuron7xLab/time-rupture-inference/main/.github/assets/banner-dark.svg" width="100%">
</picture>

<br>

<p>
  <code>prediction-error temporal adaptation · hidden rupture · fail-closed evidence</code>
</p>

<p>
  <a href="CHANGELOG.md"><img alt="version" src="https://img.shields.io/badge/version-0.1.1-0A66FF?style=flat-square&labelColor=0A0A0A"></a>
  <a href="evidence/release_gate.md"><img alt="gate" src="https://img.shields.io/badge/gate-19/19_GREEN-00FF66?style=flat-square&labelColor=0A0A0A"></a>
  <a href="tests/"><img alt="tests" src="https://img.shields.io/badge/tests-493_PASSING-00FF66?style=flat-square&labelColor=0A0A0A"></a>
  <a href="pyproject.toml"><img alt="mypy" src="https://img.shields.io/badge/mypy-strict-0A66FF?style=flat-square&labelColor=0A0A0A"></a>
  <a href="docs/reports/LINEAGE_STATE.md"><img alt="lineage" src="https://img.shields.io/badge/lineage-RED_preserved-FF0033?style=flat-square&labelColor=0A0A0A"></a>
</p>

<p>
  <sub>
    <code>error → update → prediction → action → next-state estimate</code>
  </sub>
</p>

</div>

## The one mechanism

A hidden inter-event interval `τ₀` ruptures to `τ₁` at an unseen step `T*`.
The agent never sees `τ₀`, `τ₁`, `T*`, or the noise — only the realised
interval. It must infer the change from **its own prediction error** and
re-adapt. Nothing is handed to the learner.

```
S(t) → O(t) → B(t) → P(S(t+Δ)) → E(t) → U(t) → S(t+1)
state   obs    belief  prediction  error   update
```

## What is established — and what is not

<!-- claims:disclaimer -->
> **Allowed claim.** The learned agent adapts to hidden temporal regime
> shifts better than fixed and naive baselines under preregistered
> metrics, deterministic replay, no-leakage constraints, and ablation
> controls.

> **Forbidden claim.** The agent has intelligence, consciousness,
> biological neuroplasticity, or understanding of time.
<!-- claims:end -->

This release is `prediction-error temporal adaptation` — frozen and
scoped. Causal action (`do(A) → S(t+Δ)`) is the **next** pre-registered
lineage, deliberately not begun here.

## What this is / is not  (model taxonomy card)

<!-- claims:disclaimer -->
| dimension | this system | explicitly NOT |
|---|---|---|
| learner | one scalar estimate `m += gain·error` + Page-Hinkley drift trigger | a neural network / backprop / gradients |
| representation | a single inter-event interval scalar | a representational hierarchy or world model |
| "adaptation" | online error-driven parameter + gain update | cognition, understanding, or sentience |
| "neuroplastic-like" markers | 4 measured operational quantities, ablation-gated | biological neuroplasticity or brain fidelity |
| scope | one hidden-regime temporal-rupture benchmark | general intelligence / AGI |
| claim status | narrow, gate-enforced, falsifiable | an ontological claim about mind |
<!-- claims:end -->

A machine-checkable lexicon (`claims.yaml`) plus `scripts/claims_lint.py`
<!-- claims:disclaimer -->
is enforced in CI and pytest: external-facing text cannot assert
cognition / neural-equivalence / AGI outside an explicit disclaimer
block (all such terms are forbidden unless negated).
<!-- claims:end -->
The risk this kills is interpretation-layer inflation, not a code
defect.

## Result · 30 seeds × 3 shift magnitudes (incl. a decrease)

| agent | post-shift MAE | role |
|---|---:|---|
| oracle (knows the schedule) | 0.793 | irreducible noise floor |
| **learned** | **0.883** | the claim |
| exp_smoothing / moving_avg / last | 0.94 – 1.14 | naive baselines |
| injected (τ₀ hard-wired) | 8.003 | strawman, must fail |

Win-rate vs injected **1.000** · vs best naive **1.000** · on every shift.
Ablation proves the drift mechanism necessary. Four neuroplasticity-like
markers (synaptic / homeostatic / neuromodulation / extinction) are
**measured**, never asserted.

## Falsification lineage — every RED kept

| tag | verdict | what it records |
|---|---|---|
| `cti-os-v1-RED` | 🔴 | drift detector poisoned by cold-start |
| `cti-os-v2-GREEN` | 🟢 | base proof of life |
| `cti-os-v3-RED` | 🔴 | two new controls mis-specified |
| `cti-os-v4-GREEN` | 🟢 | doctoral critique closed → `v0.1.0` |
| v5 (PR #1) | 🟢 | minimal causal-action: gain 0.868, action_null 0.000 |
| v6 | 🔴 | precision-weighting (Kalman) RED — principled ≠ better, kept |
| v7 | 🔴 | learned reservoir/SSM ≤ heuristic — NO_HEADROOM (boundary = task) |
| v8 | 🔴 | scalar-inexpressible env: trigger too rare, decorative |
| v8.1 | 🔴 | frequency fixed; inexpressibility real but carrier-masked |
| v8.2 | 🟠 | trigger-scoped+carrier-controlled: signal confirmed & carrier-robust; history-oracle under-specified (PARTIAL_RED) |

`git checkout cti-os-v1-RED` reproduces the failure. Scientific
thresholds are byte-identical v2→v4. No threshold was ever tuned to
green; every RED (v1, v3, v6, v7, v8, v8.1) and PARTIAL_RED (v8.2) is a
preserved artifact. Full state: [`docs/reports/LINEAGE_STATE.md`](docs/reports/LINEAGE_STATE.md).

## Run

```bash
pip install -e ".[dev]"
python scripts_prereg.py        # pin the falsifier, then commit it
PYTHONPATH=src pytest tests -q
PYTHONPATH=src python -m ctios.runner --mode full   # fail-closed gate
PYTHONPATH=src python -m ctios.automation            # full chain → runs/ UTC ledger
```

Exit `0` ⇔ GREEN. Evidence regenerated every run:
`evidence/release_gate.md`, `evidence_ledger.jsonl`,
`NEGATIVE_RESULT_*.md`, `metrics_summary.csv`, `plots/`.

## Structure

```
src/ctios/   env · agents · drift · metrics · gates · ledger · runner · automation
prereg/      preregistration.yaml · falsifier_contract.yaml · sha_pin.txt
configs/     env · agents · metrics · experiment (the 30×3 grid)
evidence/    ledger · negatives · v4 baseline lock · release gate
tests/       493 tests incl. no-leakage, shuffle kill-control, contract
invariants.yaml  machine-readable invariant register (enforced refs)
```

Formal specification (claim → falsifier → evidence → boundary):
[`docs/SPEC.md`](docs/SPEC.md). Reproducible demonstration:
[`docs/DEMO.md`](docs/DEMO.md).

## Reviewer map

- Trust architecture: [`docs/TRUST_LAYER.md`](docs/TRUST_LAYER.md)
- Reproduction contract: [`docs/REPRODUCIBILITY_CONTRACT.md`](docs/REPRODUCIBILITY_CONTRACT.md)
- Claim/source matrix: [`docs/CLAIM_SOURCE_MATRIX.md`](docs/CLAIM_SOURCE_MATRIX.md)
- References (claim-mapped): [`docs/REFERENCES.md`](docs/REFERENCES.md)
- Prior-art boundary map: [`docs/PRIOR_ART_BOUNDARY_MAP.md`](docs/PRIOR_ART_BOUNDARY_MAP.md)
- Review paths: [`docs/REVIEW_PATH.md`](docs/REVIEW_PATH.md)
- Value positioning: [`docs/VALUE_POSITIONING.md`](docs/VALUE_POSITIONING.md)
- Open structural gaps: [`docs/OPEN_STRUCTURAL_GAPS.md`](docs/OPEN_STRUCTURAL_GAPS.md)

Citations do not expand scientific claims; they only map boundaries,
prior art, and reviewer context.

## System identity

TRI-Falsify is a falsification-first temporal inference and
hypothesis-auditing apparatus. A pinned, hashed hypothesis runs
through an adversarial battery into a sealed, reproducible verdict;
on failure it auto-proposes a human-gated next experiment and never
runs anything itself. Reviewer entry points:

- [`docs/REVIEWER_ONE_PAGER.md`](docs/REVIEWER_ONE_PAGER.md) — 60-second system identity.
- [`docs/SYSTEM_CARD.md`](docs/SYSTEM_CARD.md) — abstraction, inputs/outputs, boundaries.
- [`docs/CONFERENCE_ABSTRACT.md`](docs/CONFERENCE_ABSTRACT.md) — workshop abstract.
- [`docs/CONTRIBUTION_CLAIMS.md`](docs/CONTRIBUTION_CLAIMS.md) — original vs prior art.
- [`docs/REPRODUCIBILITY_CONTRACT.md`](docs/REPRODUCIBILITY_CONTRACT.md) — clean-clone contract + frozen outputs.
- [`docs/FAILURE_TAXONOMY.md`](docs/FAILURE_TAXONOMY.md) — defenses + residual risk.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — pipeline + module map.

PR21 adds adversarial portability stress tests: eight deterministic
degenerate probes run fail-closed against the battery over a
seven-family synthetic portfolio plus a data-sensitivity scan, with a
sealed evidence artifact and a CI gate. It improves battery coverage
against degenerate probes; it does not assert real-world validity, and
an external collaborator run of the private layer remains open.

One command for a reviewer: `bash scripts/conference_smoke.sh`.
One command for the adversarial gate: `bash scripts/external_adversarial_demo.sh`.

## External review package

**Start here if you are reviewing the private-safe redacted-hypothesis
R&D package:** [`docs/INDI_README.md`](docs/INDI_README.md). One-command
check: `bash scripts/indi_demo.sh`. A redacted private hypothesis runs
through the apparatus with no proprietary mechanism, dataset, or
theorem content entering this repository.

- [`docs/INDI_README.md`](docs/INDI_README.md) — read this first.
- [`docs/INDI_EXECUTIVE_SUMMARY.md`](docs/INDI_EXECUTIVE_SUMMARY.md) — 3-minute summary.
- [`docs/PRIVATE_RND_PROTOCOL.md`](docs/PRIVATE_RND_PROTOCOL.md) — redacted hypothesis interface + IP boundary table.
- [`docs/INDI_REVIEWER_CHECKLIST.md`](docs/INDI_REVIEWER_CHECKLIST.md) — fastest useful path, then graded tiers.

## CTI-OS v7 · GCP readiness (CPU-first, no GPU default)

v7 tests whether a learned sequence model (small GRU / linear
state-space) beats the frozen v4 heuristic **and** a from-scratch
conventional baseline on a harder multi-regime, partially-observable
environment. The repo is prepared as a deterministic, cost-guarded,
reproducible cloud-run artifact — Google is only an execution surface.

```bash
# local readiness gates (no cloud, no spend)
make test
make v7-prereg-check
make v7-cpu-smoke
make v7-artifact-check
make gcp-doctor          # actionable PASS/FAIL (install gcloud + auth)
make gcp-dry-run         # non-destructive plan, creates nothing
# only if all green AND operator-reviewed cost guardrails:
PROJECT_ID=cti-os-v7 ZONE=europe-west4-a APPLY=1 make gcp-cpu-run
APPLY=1 PROJECT_ID=cti-os-v7 make gcp-cleanup
```

Phase 1 is CPU-only; GPU is a documented, manually-unlocked future
phase. No command creates cloud resources unless `APPLY=1` is explicit.
Budgets are alerts, not hard caps — see
[`docs/cloud/gcp_cost_guardrails.md`](docs/cloud/gcp_cost_guardrails.md).
Pre-registration: [`docs/prereg/cti_os_v7_preregistration.md`](docs/prereg/cti_os_v7_preregistration.md).

<!-- claims:disclaimer -->
Claim boundary: a learned sequence model with a representational
advantage on a harder task — NOT intelligence, NOT AGI, NOT cognition.
<!-- claims:end -->

<div align="center">
<sub>Build the smallest environment where language cannot fake adaptation; then make the model adapt under hidden temporal rupture, or fail loudly.</sub>
</div>
