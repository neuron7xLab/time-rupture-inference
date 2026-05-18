<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/neuron7xLab/time-rupture-inference/main/.github/assets/banner-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/neuron7xLab/time-rupture-inference/main/.github/assets/banner-light.svg">
  <img alt="time rupture inference" src="https://raw.githubusercontent.com/neuron7xLab/time-rupture-inference/main/.github/assets/banner-dark.svg" width="100%">
</picture>

<br><br>

<img src="https://readme-typing-svg.demolab.com/?lines=error+updates+the+model+%C2%B7+the+model+survives+the+rupture;every+RED+preserved+%C2%B7+no+threshold+tuned+to+green;30+seeds+%C3%97+3+shifts+%C2%B7+win-rate+1.000+vs+injected+%26+naive;falsifier+pinned+before+the+run+or+it+does+not+count;prediction-error+temporal+adaptation+%E2%80%94+proven%2C+scoped%2C+frozen&font=JetBrains+Mono&size=18&pause=1800&color=00FF66&center=true&vCenter=true&width=820&height=46" alt="tagline" />

<br>

# `t i m e   r u p t u r e   i n f e r e n c e`

***A learned temporal model that survives a hidden regime change — or fails loudly.***
***Falsification-first. Every negative result is kept, not erased.***

<br>

[![version](https://img.shields.io/badge/version-0.1.1-0000FF?style=for-the-badge&labelColor=000000)](CHANGELOG.md)
[![gate](https://img.shields.io/badge/gate-19%2F19_green-00FF00?style=for-the-badge&labelColor=000000)](evidence/release_gate.md)
[![tests](https://img.shields.io/badge/tests-91_passing-00FF00?style=for-the-badge&labelColor=000000)](tests/)
[![mypy](https://img.shields.io/badge/mypy-strict-00FF00?style=for-the-badge&labelColor=000000)](pyproject.toml)
[![grid](https://img.shields.io/badge/grid-30_seeds_%C3%97_3_shifts-0000FF?style=for-the-badge&labelColor=000000)](configs/experiment.yaml)
[![lineage](https://img.shields.io/badge/lineage-3_RED_preserved-FF0033?style=for-the-badge&labelColor=000000)](evidence/)
[![license](https://img.shields.io/badge/license-MIT-0000FF?style=for-the-badge&labelColor=000000)](LICENSE)

<br>

[![Python 3.12](https://img.shields.io/badge/Python_3.11--3.13-0000FF?style=flat&logo=python&logoColor=white&labelColor=000000)](https://www.python.org/)
[![NumPy](https://img.shields.io/badge/NumPy-FF0033?style=flat&logo=numpy&logoColor=white&labelColor=000000)](https://numpy.org/)
[![pytest](https://img.shields.io/badge/pytest-00FF00?style=flat&logo=pytest&logoColor=white&labelColor=000000)](https://docs.pytest.org/)
[![Ruff](https://img.shields.io/badge/Ruff-0000FF?style=flat&logo=ruff&logoColor=black&labelColor=000000)](https://docs.astral.sh/ruff/)
[![CI](https://img.shields.io/badge/CI-fail--closed_gate-FF0033?style=flat&logo=githubactions&logoColor=white&labelColor=000000)](.github/workflows/ci.yml)
[![Ukraine](https://img.shields.io/badge/%F0%9F%87%BA%F0%9F%87%A6-Poltava-0000FF?style=flat&labelColor=000000)](#)

</div>

<p align="center">
  <code>error → update → prediction → action → causal change of the future</code>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/neuron7xLab/time-rupture-inference/main/.github/assets/divider.svg" width="100%">
</p>

## The one mechanism

A hidden inter-event interval `τ₀` ruptures to `τ₁` at an unseen step `T*`.
The agent never sees `τ₀`, `τ₁`, `T*`, or the noise — only the realised
interval. It must infer the change from **its own prediction error** and
re-adapt. Nothing is handed to the learner.

```
S(t) → O(t) → B(t) → P(S(t+Δ)) → E(t) → U(t) → S(t+1)
state   obs    belief  prediction  error   update
```

## What is proven — and what is not

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

`git checkout cti-os-v1-RED` reproduces the failure. Scientific
thresholds are byte-identical v2→v4. No threshold was ever tuned to
green; every RED (v1, v3, v6) is a preserved artifact.

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
tests/       91 tests incl. no-leakage, shuffle kill-control, contract
invariants.yaml  machine-readable invariant register (enforced refs)
```

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


<p align="center">
  <img src="https://raw.githubusercontent.com/neuron7xLab/time-rupture-inference/main/.github/assets/divider.svg" width="100%">
</p>

<div align="center">
<sub>Build the smallest environment where language cannot fake adaptation;
then make the model adapt under hidden temporal rupture, or fail loudly.</sub>
</div>
