# Architecture Scorecard — the contract as mechanism

`ctios.architecture_scorecard` turns the canonical architecture-output
contract from prose into a deterministic, fail-closed audit function, and
`tri-architect` runs it. It exists so that "score the artifact, calibrate
confidence, expose failure" is *executed*, not merely asserted.

## What it computes

| stage | mechanism | guarantee |
| ----- | --------- | --------- |
| STAGE 11 scoring | nine-dimension weighted rubric | weights are a frozen partition of unity (`weights_sum() == 1.0`) |
| STAGE 13 confidence | five sub-factors minus penalties | hard-capped by the evidence tier |
| anti-pseudo firewall | line-level regex detectors | a CRITICAL hit is a blocking fact |

## Evidence tiers and their hard ceilings

| tier | meaning | confidence ceiling |
| ---- | ------- | ------------------ |
| `NONE` | no verification harness | 0.60 |
| `SYNTHETIC_ONLY` | only synthetic / self tests | 0.75 |
| `LOCAL_REGRESSION` | a real regression suite passes locally | 0.90 |
| `REPEATED_REGRESSION` | regression passes repeatedly | 0.95 |
| `INDEPENDENT_VALIDATION` | external validation recorded | 0.99 |

`ELITE_VALIDATED_PRODUCTION` is **unreachable** below
`REPEATED_REGRESSION`, regardless of the raw score. This mirrors
`ctios.readiness_score`: the number never overrides a blocking fact.

## Claim → falsifier → evidence → boundary

- **Claim.** The harness scores an artifact against a fixed rubric and
  bounds confidence to the supplied evidence tier.
- **Falsifier.** `tests/test_architecture_scorecard.py` pins every band,
  every ceiling, the production gate, the unbacked-dimension floor, and
  each firewall rule. If any guarantee drifts, a test goes red.
- **Evidence.** 18 scorecard tests + 6 CLI tests, all offline and
  deterministic; `mypy --strict` and `ruff` clean.
- **Boundary.** This is an audit instrument over *artifacts*. It makes no
  claim about real-world validity, and self-mode is capped at
  `REPEATED_REGRESSION` until a real external collaborator run is
  recorded in `evidence/external_validation_status.json`.

<!-- claims:disclaimer -->
The dimension label `cognitive_neural_validity` is a rubric field name
only — NOT a claim that the apparatus has cognition or is a neural
network. The firewall stores the forbidden lexicon ("neural",
"cognitive", "proves", …) as enforcement data; it is the mechanism that
*detects* that vocabulary, not an assertion of it. No biological or
intelligence claim is made anywhere in this module.
<!-- claims:end -->

## Usage

```bash
tri-architect --self                 # score this apparatus, human output
tri-architect --self --json          # machine-readable contract
tri-architect --firewall FILE.md     # anti-pseudo scan only (exit 1 on CRITICAL)
```

Self-mode on the current tree reports `VALIDATED` (≈4.63) at tier
`REPEATED_REGRESSION` with confidence ≤ 0.95 — deliberately short of the
production class, because no real external run exists yet.
