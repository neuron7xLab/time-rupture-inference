"""Per-run causal metrics + aggregate causal-action gain."""

from __future__ import annotations

from collections import Counter

import numpy as np

from ctios.contract import validate_window


def run_metrics(
    errors: np.ndarray, actions: list[str], t_star: int, eval_horizon: int
) -> dict[str, float | dict]:
    validate_window(t_star, eval_horizon, errors.size)
    ae = np.abs(errors)
    pre = ae[:t_star]
    post = ae[t_star : t_star + eval_horizon]
    pre_mae = float(np.mean(pre)) if pre.size else float("nan")
    post_mae = float(np.mean(post)) if post.size else float("nan")
    aue = float(np.sum(post))

    band = 1.5 * pre_mae
    roll = _rolling(post, 20)
    rec = np.where(roll <= band)[0]
    adapt = float(rec[0]) if rec.size else float("inf")

    post_actions = actions[t_star : t_star + eval_horizon]
    counts = dict(Counter(actions))
    stab_frac = (
        sum(a == "stabilize" for a in post_actions) / len(post_actions)
        if post_actions
        else 0.0
    )
    return {
        "pre_shift_mae": pre_mae,
        "post_shift_mae": post_mae,
        "post_shift_aue": aue,
        "adaptation_time": adapt,
        "action_counts": counts,
        "stabilize_fraction_post_shift": stab_frac,
    }


def causal_action_gain(post_mae_action_null: float, post_mae_interventional: float) -> float:
    """Positive => acting (in interventional mode) helped vs the same agent
    when its actions were inert (action_null)."""
    return post_mae_action_null - post_mae_interventional


def _rolling(x: np.ndarray, w: int) -> np.ndarray:
    if x.size == 0:
        return x
    w = min(w, x.size)
    c = np.cumsum(np.insert(x, 0, 0.0))
    out = (c[w:] - c[:-w]) / w
    head = np.array([np.mean(x[: i + 1]) for i in range(w - 1)])
    return np.concatenate([head, out])
