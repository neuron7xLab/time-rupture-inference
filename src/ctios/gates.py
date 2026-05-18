"""Release gate v3. Fail-closed. Never auto-softens a RED verdict.

Adds the doctoral-critique closure checks: statistical-power grid,
shuffled-order leakage kill-control, and the four operational adaptation
markers (neuroplastic-like label only, NOT biological).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class GateResult:
    green: bool
    reasons: list[str]
    checks: dict[str, bool]


def evaluate_gate(
    *,
    agg: dict[str, dict[str, float]],
    prereg: dict[str, float],
    win_rate_learned_vs_injected: float,
    win_rate_learned_vs_baseline: float,
    ablation_ok: bool,
    no_leakage_ok: bool,
    replay_ok: bool,
    prereg_before_run: bool,
    every_delta_pass: bool,
    shuffle_no_gain: bool,
    neuro_markers: dict[str, bool],
    n_seeds: int,
    n_deltas: int,
    min_seeds: int,
    min_deltas: int,
) -> GateResult:
    L = agg["learned_full"]
    inj = agg["injected"]
    best_naive = min(
        v["post_shift_mae"]
        for k, v in agg.items()
        if k.startswith(("moving_average", "last_interval", "exp_smoothing"))
    )
    c: dict[str, bool] = {}
    c["learned_beats_injected_post_mae"] = L["post_shift_mae"] < inj["post_shift_mae"]
    c["learned_beats_best_naive_post_mae"] = L["post_shift_mae"] < best_naive
    c["learned_beats_injected_aue"] = (
        L["area_under_post_shift_error"] < inj["area_under_post_shift_error"]
    )
    c["adaptation_under_threshold"] = L["adaptation_time"] < prereg["adaptation_time_max"]
    c["detection_delay_bounded"] = L["detection_delay"] < prereg["detection_delay_max"]
    c["false_alarm_bounded"] = L["false_alarm_rate"] <= prereg["false_alarm_rate_max"]
    c["win_rate_vs_injected"] = win_rate_learned_vs_injected >= prereg["min_win_rate"]
    c["win_rate_vs_baseline"] = win_rate_learned_vs_baseline >= prereg["min_win_rate"]
    c["ablation_shows_necessity"] = ablation_ok
    c["no_hidden_variable_leakage"] = no_leakage_ok
    c["deterministic_replay"] = replay_ok
    c["prereg_committed_before_run"] = prereg_before_run
    # --- v3 doctoral-critique closures ---
    c["statistical_power_grid"] = n_seeds >= min_seeds and n_deltas >= min_deltas
    c["pass_holds_on_every_shift"] = every_delta_pass
    c["shuffled_order_no_gain"] = shuffle_no_gain
    c["np_marker_synaptic"] = neuro_markers.get("synaptic", False)
    c["np_marker_homeostatic"] = neuro_markers.get("homeostatic", False)
    c["np_marker_neuromodulation"] = neuro_markers.get("neuromodulation", False)
    c["np_marker_extinction"] = neuro_markers.get("extinction", False)

    reasons = [f"FAILED: {k}" for k, ok in c.items() if not ok]
    return GateResult(green=all(c.values()), reasons=reasons, checks=c)
