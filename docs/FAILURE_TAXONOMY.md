# Failure Taxonomy

The failure classes this apparatus is built to resist, and — honestly —
the residual risk in each. Practical, not philosophical: each row names
a symptom, the concrete defense, what defense does *not* cover, and the
test or artifact that enforces it.

| Failure class | Symptom | System defense | Residual risk | Test / artifact |
|---|---|---|---|---|
| Self-evaluation laundering | A model's fluent self-assessment treated as evidence | Verdict comes only from a pinned falsifier + battery, not from any narrative | A probe can still encode a flattering metric choice | `run_battery`, `tests/test_falsify_engine.py` |
| Prompt-shaped authority | Confident phrasing read as rigor | Claim admitted only if its kill-test ran and did not trigger; prose cannot grant status | Reviewer may still over-trust the prose | claim → falsifier → evidence chain, `docs/SPEC.md` |
| Post-hoc threshold tuning | Threshold edited after seeing results | `spec_sha256` covers thresholds + assumptions + variables; any edit changes the hash | Author can re-pin and rerun openly (visible, not silent) | `HypothesisSpec.sha()`, `test_spec_sha_stable_and_threshold_mutation_changes_it` |
| Benchmark leakage | Agent sees the answer it should infer | Agent receives only the realized signal; no-leakage introspection test | New probes can leak via their own construction | no-leakage test, `docs/SPEC.md` S1 |
| Pseudo-GREEN negative control | Negative control also passes, so the gate is not discriminative | `negative_control_fails` battery check; GREEN requires the control to fail | Control may be weakly designed by the author | `test_battery_catches_pseudo_green_negative_control` |
| Decorative threshold | A threshold that never changes the verdict | `thresholds_load_bearing` battery check | A threshold can be load-bearing yet poorly chosen | `run_battery`, engine contract tests |
| Non-load-bearing metric | Metric reported but not gating anything | Checks bind metrics to threshold keys; unused metric is visible | A bound metric can still be a poor proxy | `_eval_checks`, spec `checks` |
| Claim-boundary inflation | Text asserts cognition/AGI beyond mechanism | Machine-checked lexicon (`claims.yaml` + `scripts/claims_lint.py`) in CI and pytest | Only scans README + `src/ctios/*.py`; docs rely on review | `claims_lint`, `tests/test_claims_lexicon.py` |
| Frozen-number drift | A proven number silently moves | v4/v5 numbers byte-identical across commits; runner asserts them | Drift in unfrozen lineages is not auto-blocked | `ctios.runner --mode full`, `docs/REPRODUCIBILITY_CONTRACT.md` |
| Private-IP leakage via artifact design | Sealed verdict reveals mechanism/data | Redacted interface; verdict carries scalars + hash only; never-share field list | A badly chosen exposed metric could reveal structure | `docs/PRIVATE_RND_PROTOCOL.md` §4/§5 |
| Reviewer-friction failure | Reviewer cannot understand/run/extend without the author | One-pager + fastest-path + one-command smoke + reproducibility contract | First-time clone environment variance | `scripts/conference_smoke.sh`, `docs/REVIEWER_ONE_PAGER.md` |
| Unverifiable theorem prose | A private claim asserted but never tested | Theorem must become a pinned spec + probe before any belief update; engine refuses narrative-only input | The engine cannot judge whether the redaction is faithful | `docs/PRIVATE_RND_PROTOCOL.md`, `examples/indi_redacted_temporal_hypothesis.yaml` |
| Degenerate deterministic probe | A stable, discriminative probe encoding a hidden trivial solution reaches PASS | Family-sensitivity scan: a data-blind probe (std≈0 across structurally distinct families) is a BLOCKER | A probe co-designed against this exact family set is not proven impossible | `ctios.falsifier_stress`, `tests/test_adversarial_probes.py` |
| Metric-threshold collusion | Probe echoes the threshold so the verdict is knife-edge | `verdict_instability` MAJOR + family-sensitivity BLOCKER | Off-boundary collusion with a wider margin is weaker-signal | `ctios.falsifier_battery`, `tests/test_adversarial_probes.py` |
| Carrier shortcut | Probe passes via a confound, not the rupture signal | `CarrierConfoundedRuptureFamily` + family-sensitivity scan flag data-blindness | A confound correlated with the signal across all families would evade | `ctios.benchmark_families`, `ctios.falsifier_stress` |
| Benchmark family overfit | A claim rides one generative assumption silently | 7-family portfolio with per-family `admissible_claim_boundary`; null family must not go rupture-GREEN | Portfolio is still synthetic; real-world transfer untested | `tests/test_benchmark_families.py` |
| Claim-lint scope gap | Inflation in docs/examples/scripts/workflows outside the old README+src scope | Extended `scan_globs` to `docs/**`, `examples/**`, `scripts/**`, `.github/workflows/**`; disclaimer-or-clean | Exempt limitation/critique docs are trusted by classification, not scanned | `scripts/claims_lint.py`, `tests/test_claims_lint_scope.py` |

## How to read this

A defense is a *mechanism with a test*, not a promise. Where the
residual-risk column is non-empty, that risk is open and stated on
purpose — a conference reviewer should attack exactly those columns.
The adversarial self-review in `docs/OPENAI_STYLE_REVIEW.md` does this
deliberately.
