# Mechanism Inventory (generated)

Computed by `python -m ctios.mechanism_inventory`. Every CORE_MECHANISM must have a linked test or the build fails.

| file | classification | linked_test |
|---|---|---|
| src/ctios/adversarial_probes.py | ADVERSARIAL_PROBE | test_adversarial_probes.py |
| src/ctios/agent.py | CORE_MECHANISM | test_agent.py |
| src/ctios/agent_cli.py | REVIEWER_SURFACE | — |
| src/ctios/agents.py | CORE_MECHANISM | test_agents.py |
| src/ctios/artifact_assertions.py | REPRODUCIBILITY_GUARD | test_artifact_assertions.py |
| src/ctios/automation.py | CORE_MECHANISM | test_automation_gateway.py |
| src/ctios/benchmark_families.py | CORE_MECHANISM | test_benchmark_families.py |
| src/ctios/calibrated_change_detector.py | CORE_MECHANISM | test_calibrated_change_detector.py |
| src/ctios/carrier_robust_observable.py | CORE_MECHANISM | test_carrier_robust_observable.py |
| src/ctios/causal_agents.py | CORE_MECHANISM | test_causal_agents.py |
| src/ctios/causal_env.py | CORE_MECHANISM | test_causal_env.py |
| src/ctios/causal_gate.py | CORE_MECHANISM | test_causal_runner.py |
| src/ctios/causal_metrics.py | CORE_MECHANISM | test_causal_runner.py |
| src/ctios/causal_runner.py | CORE_MECHANISM | test_causal_runner.py |
| src/ctios/change_detection.py | CORE_MECHANISM | test_change_detection.py |
| src/ctios/change_detection_arc.py | EVIDENCE_PRODUCER | test_change_detection_arc.py |
| src/ctios/code_quality_audit.py | REPRODUCIBILITY_GUARD | test_code_quality_audit.py |
| src/ctios/contract.py | CLAIM_BOUNDARY | test_agents.py |
| src/ctios/deep_adversarial_probes.py | ADVERSARIAL_PROBE | test_deep_adversarial_probes.py |
| src/ctios/drift.py | CORE_MECHANISM | test_core_contract_audit.py |
| src/ctios/env.py | CORE_MECHANISM | test_agents.py |
| src/ctios/external_validation.py | FALSIFIER | test_external_validation_tamper.py |
| src/ctios/falsifier_battery.py | FALSIFIER | test_falsifier_battery_v2.py |
| src/ctios/falsifier_stress.py | FALSIFIER | test_adversarial_probes.py |
| src/ctios/falsify.py | FALSIFIER | test_falsify_engine.py |
| src/ctios/falsify_cli.py | REVIEWER_SURFACE | test_falsify_engine.py |
| src/ctios/gates.py | CORE_MECHANISM | test_core_contract_audit.py |
| src/ctios/human_gate.py | CORE_MECHANISM | test_human_gate.py |
| src/ctios/ledger.py | CORE_MECHANISM | test_core_contract_audit.py |
| src/ctios/mechanism_inventory.py | REPRODUCIBILITY_GUARD | test_mechanism_inventory.py |
| src/ctios/metrics.py | CORE_MECHANISM | test_contract_invariant.py |
| src/ctios/opaque_probe.py | CORE_MECHANISM | test_falsifier_battery_v2.py |
| src/ctios/platform_demo.py | REVIEWER_SURFACE | — |
| src/ctios/portfolio_falsifier.py | FALSIFIER | test_portfolio_falsifier.py |
| src/ctios/predictive_simulation.py | CORE_MECHANISM | test_change_detection.py |
| src/ctios/readiness_score.py | FALSIFIER | test_external_validation_status.py |
| src/ctios/redacted.py | CORE_MECHANISM | test_adversarial_probes.py |
| src/ctios/redacted_io.py | CORE_MECHANISM | test_adversarial_probes.py |
| src/ctios/report.py | EVIDENCE_PRODUCER | test_report.py |
| src/ctios/review_cli.py | REVIEWER_SURFACE | — |
| src/ctios/runner.py | CORE_MECHANISM | test_contract_invariant.py |
| src/ctios/series.py | CORE_MECHANISM | test_series.py |
| src/ctios/spec_cli.py | REVIEWER_SURFACE | test_spec_compiler.py |
| src/ctios/spec_compiler.py | CORE_MECHANISM | test_report.py |
| src/ctios/test_value_audit.py | CORE_MECHANISM | test_test_value_audit.py |
| src/ctios/utils.py | CORE_MECHANISM | test_core_contract_audit.py |
| src/ctios/v6_precision.py | FALSIFIER | test_core_contract_audit.py |
| src/ctios/windowed_change_detector.py | CORE_MECHANISM | test_change_detection.py |
| src/ctios/windowed_detector_ood.py | CORE_MECHANISM | test_windowed_detector_ood.py |
| scripts/conference_smoke.sh | REVIEWER_SURFACE | scripts/*.sh artifact-asserted via reviewer_attack |
| scripts/deep_mechanism_audit.sh | REVIEWER_SURFACE | scripts/*.sh artifact-asserted via reviewer_attack |
| scripts/external_adversarial_demo.sh | REVIEWER_SURFACE | scripts/*.sh artifact-asserted via reviewer_attack |
| scripts/indi_demo.sh | REVIEWER_SURFACE | scripts/*.sh artifact-asserted via reviewer_attack |
| scripts/platform_demo.sh | REVIEWER_SURFACE | scripts/*.sh artifact-asserted via reviewer_attack |
| scripts/prepare_external_reviewer_packet.sh | REVIEWER_SURFACE | scripts/*.sh artifact-asserted via reviewer_attack |
| scripts/reviewer_attack.sh | REVIEWER_SURFACE | scripts/*.sh artifact-asserted via reviewer_attack |

core_without_test: (none)
