# v5 Minimal Causal-Action — Release Gate

**Verdict: RED / FAIL**

- causal_action_gain: 0.8680 (threshold 0.05)
- action_null_gap: 0.0000 (max 0.02)
- win-rate vs no_action: 1.000
- win-rate vs random_action: 1.000
- interventional effect present: True · action_null inert: True
- v4 tests pass: False · v4 runner green: True

## Claim boundary
Allowed: causal-action gain under hidden temporal rupture, preregistered, replayable.
Forbidden — NOT claimed: intelligence, consciousness, biological neuroplasticity-like fidelity, AGI, cognition, understanding time.

## Checks
- [ ] v4_tests_still_pass
- [x] v4_runner_still_green
- [x] causal_env_deterministic_replay
- [x] no_hidden_variable_leakage
- [x] action_null_shows_no_advantage
- [x] interventional_effect_present
- [x] causal_action_gain_above_threshold
- [x] beats_no_action_post_shift
- [x] beats_random_action_post_shift
- [x] reproduces_over_seed_grid
- [x] evidence_files_written
- [x] claim_boundary_forbids_overclaim

## Failure reasons
- FAILED: v4_tests_still_pass