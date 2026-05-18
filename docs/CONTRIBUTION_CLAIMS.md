# Contribution Claims — Original vs Prior Art

**This repository does not claim to invent falsification, evaluation,
CI, or temporal prediction.** Its contribution is the *integration
discipline*: a claim-boundary-enforced falsification loop with
preserved negatives and reproducible sealed verdicts, runnable on a
redacted private hypothesis without disclosing its mechanism.

Each row states the claim, whether it is original to this repo, the
in-repo evidence, the boundary, and what would falsify it.

| Claim | Status | Evidence | Boundary | Falsifier |
|---|---|---|---|---|
| Hidden temporal rupture benchmark | Constructed instrument (not novel as a concept; specific construction is ours) | `src/ctios/env.py`, v8.4 re-derived env, `docs/SPEC.md` S4 | A synthetic family, not a real-world task | Scalar provably sufficient on it, or causal floor unreachable, or params not pinned before run |
| Prediction-error temporal adaptation result | Narrow surviving positive | Frozen `learned 0.8830 < injected 8.0028`, oracle 0.7933, win-rate 1.000, ablation, no-leakage, `git tag cti-os-v4-GREEN` | A scalar adaptive estimator on a synthetic rupture; not cognition | Loss to injected or best-naive on aggregate or any shift, single-seed-only, leakage, or non-reproducible |
| Preserved negative-lineage discipline | Original integration | `evidence/NEGATIVE_*`, `docs/reports/LINEAGE_STATE.md`, sha-pinned RED tags | Governance, not truth-generation | One RED with no sealed artifact or no reproduction path |
| Generalized falsification engine | Original integration | `ctios.falsify`, 12 engine contract tests, `tri-falsify` demo GREEN with 5 gates | A discipline primitive; does not generate truth | Battery passes a non-deterministic probe, decorative threshold, or pseudo-GREEN control, or tuned threshold not caught by spec sha |
| Redacted hypothesis interface | Original integration | `docs/PRIVATE_RND_PROTOCOL.md`, `examples/indi_redacted_cognitive_time.yaml`, opaque-probe API | Tests shape, never mechanism/data/theorem | A real hypothesis class that cannot be expressed without leaking a never-share field |
| External review package | Original packaging | `docs/INDI_*`, `scripts/indi_demo.sh` | Packaging, not science | A reviewer cannot run/falsify/extend it without the author present |
| Reusable theorem-to-experiment loop | Original integration | redacted spec + local probe + falsifier → sealed verdict → human-gated proposal | Falsification loop with mandatory human gate; not autonomous research | The loop auto-runs a next experiment, or a survived check is narrated beyond what it tested |

## Explicit prior-art disclaimer

Falsification (Popper), preregistration, adversarial evaluation,
held-out negative controls, reproducible CI, and online temporal
prediction are all established. None are claimed here as inventions.
The originality is that they are *fused into one fail-closed apparatus*
where claim-boundary inflation, threshold tuning, pseudo-GREEN
controls, and private-IP leakage are each blocked by a specific,
testable mechanism rather than by reviewer goodwill — and where the
same apparatus audits a private hypothesis through a redacted interface.
