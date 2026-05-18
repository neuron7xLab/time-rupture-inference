"""Fail-closed gate for the v5 minimal causal-action line. No soft pass."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CausalGate:
    green: bool
    reasons: list[str]
    checks: dict[str, bool]


def evaluate(
    *,
    v4_tests_pass: bool,
    v4_runner_green: bool,
    replay_ok: bool,
    no_leakage_ok: bool,
    action_null_gap: float,
    interventional_effect_present: bool,
    causal_gain: float,
    win_rate_vs_no_action: float,
    win_rate_vs_random: float,
    grid_reproduced: bool,
    evidence_written: bool,
    claim_boundary_ok: bool,
    thr: dict[str, float],
) -> CausalGate:
    c: dict[str, bool] = {}
    c["v4_tests_still_pass"] = v4_tests_pass
    c["v4_runner_still_green"] = v4_runner_green
    c["causal_env_deterministic_replay"] = replay_ok
    c["no_hidden_variable_leakage"] = no_leakage_ok
    c["action_null_shows_no_advantage"] = action_null_gap <= thr["max_allowed_action_null_gap"]
    c["interventional_effect_present"] = interventional_effect_present
    c["causal_action_gain_above_threshold"] = causal_gain > thr["min_causal_action_gain"]
    c["beats_no_action_post_shift"] = win_rate_vs_no_action >= thr["min_win_rate_vs_no_action"]
    c["beats_random_action_post_shift"] = (
        win_rate_vs_random >= thr["min_win_rate_vs_random_action"]
    )
    c["reproduces_over_seed_grid"] = grid_reproduced
    c["evidence_files_written"] = evidence_written
    c["claim_boundary_forbids_overclaim"] = claim_boundary_ok

    reasons = [f"FAILED: {k}" for k, ok in c.items() if not ok]
    return CausalGate(green=all(c.values()), reasons=reasons, checks=c)
