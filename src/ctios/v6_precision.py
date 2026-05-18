# SPDX-License-Identifier: MIT
"""v6 precision-weighting lineage gate.

Falsifier: a precision-weighted (scalar-Kalman) update must NOT be worse
than the frozen v4 fixed-gain+drift-boost learner on aggregate
regret-vs-oracle across the 30x3 grid, and must win on a pre-registered
fraction of cells. Default v4 path is precision_weighted=OFF, so the
frozen baseline is untouched. RED is reported as RED and preserved.
"""

from __future__ import annotations

import hashlib
import json

import numpy as np
import yaml

from ctios.agents import LearnedAgent, OracleAgent
from ctios.contract import EVAL_HORIZON, N_STEPS, RECOVERY_BAND_MULT, SIGMA, T_STAR, TAU0
from ctios.env import Environment
from ctios.metrics import compute_metrics
from ctios.utils import ROOT


def _post_mae(agent: LearnedAgent | OracleAgent, env: Environment) -> tuple[float, str]:
    env.reset()
    errs = np.empty(N_STEPS, dtype=float)
    for k in range(N_STEPS):
        p = agent.predict()
        o = env.step()
        errs[k] = o.observed_interval - p
        agent.update(o.observed_interval)
    m = compute_metrics(errs, T_STAR, EVAL_HORIZON, None, RECOVERY_BAND_MULT)
    h = hashlib.sha256(np.round(errs, 9).tobytes()).hexdigest()
    return m.post_shift_mae, h


def main() -> int:
    pre = yaml.safe_load(
        (ROOT / "prereg" / "v6_precision_weighting_preregistration.yaml").read_text()
    )
    thr = pre["thresholds"]
    seeds = list(range(pre["grid"]["seeds"]))
    deltas = [float(d) for d in pre["grid"]["shift_deltas"]]

    reg_fixed: list[float] = []
    reg_prec: list[float] = []
    cells_win = 0
    cells = 0
    replay_ok = True
    rows: list[dict[str, object]] = []

    for delta in deltas:
        tau1 = TAU0 + delta
        for s in seeds:
            env = Environment(TAU0, tau1, T_STAR, SIGMA, N_STEPS, s)
            orc, _ = _post_mae(OracleAgent(env.oracle_view()), env)
            fx, _ = _post_mae(LearnedAgent(prior=1.0), env)
            pr, hpr = _post_mae(LearnedAgent(prior=1.0, precision_weighted=True), env)
            if s == 0 and delta == deltas[0]:
                _, hpr2 = _post_mae(
                    LearnedAgent(prior=1.0, precision_weighted=True), env
                )
                replay_ok = hpr == hpr2
            rf, rp = fx - orc, pr - orc
            reg_fixed.append(rf)
            reg_prec.append(rp)
            cells += 1
            cells_win += int(rp < rf)
            rows.append(
                {"delta": delta, "seed": s, "oracle": orc, "fixed": fx,
                 "precision": pr, "regret_fixed": rf, "regret_precision": rp}
            )

    agg_rf = float(np.mean(reg_fixed))
    agg_rp = float(np.mean(reg_prec))
    ratio = agg_rp / agg_rf if agg_rf > 0 else float("inf")
    win_rate = cells_win / cells
    ablation_regresses = agg_rf >= agg_rp  # precision_off (fixed) not better

    checks = {
        "precision_not_worse_aggregate": ratio <= thr["max_regret_ratio_vs_fixed"],
        "win_rate_vs_fixed": win_rate >= thr["min_win_rate_vs_fixed"],
        "ablation_must_regress": ablation_regresses or not thr["ablation_must_regress"],
        "deterministic_replay": replay_ok,
    }
    green = all(checks.values())

    ev = ROOT / "evidence"
    (ev / "v6_precision_ledger.jsonl").write_text(
        "\n".join(json.dumps(r, default=float) for r in rows) + "\n"
    )
    lines = [
        "# v6 Precision-Weighting — Release Gate",
        "",
        f"**Verdict: {'GREEN / PASS' if green else 'RED / FAIL'}**",
        "",
        f"- aggregate regret  fixed={agg_rf:.4f}  precision={agg_rp:.4f}  "
        f"ratio={ratio:.4f} (max {thr['max_regret_ratio_vs_fixed']})",
        f"- win-rate precision<fixed: {win_rate:.3f} (min {thr['min_win_rate_vs_fixed']})",
        "",
        "## Checks",
        *[f"- [{'x' if v else ' '}] {k}" for k, v in checks.items()],
        "",
        "Operational analogy only (scalar Kalman / predictive-coding "
        "precision weighting); NOT a biological claim.",
    ]
    (ev / "v6_precision_release_gate.md").write_text("\n".join(lines))

    if not green:
        (ev / "NEGATIVE_RESULT_v6.md").write_text(
            "# NEGATIVE RESULT — v6 precision-weighting (pinned, not erased)\n\n"
            "**Verdict: RED / FAIL.** Reported as-is. No threshold tuned.\n\n"
            f"- aggregate regret fixed={agg_rf:.4f} precision={agg_rp:.4f} "
            f"ratio={ratio:.4f}\n- win-rate={win_rate:.3f}\n\n"
            "## Failing checks\n"
            + "\n".join(f"- {k}" for k, v in checks.items() if not v)
            + "\n\n## Disposition\nFrozen v4 untouched. The principled "
            "Kalman gain did not beat the heuristic drift-boost on this "
            "benchmark — a preserved negative, not a defeat. "
            "Intelligence / cognition is explicitly NOT claimed.\n"
        )

    print(f"\n=== v6 precision-weighting :: {'PASS (GREEN)' if green else 'FAIL (RED)'} ===")
    for k, v in checks.items():
        print(f"  [{'OK' if v else 'XX'}] {k}")
    print(f"regret fixed={agg_rf:.4f} precision={agg_rp:.4f} win={win_rate:.3f}")
    return 0 if green else 1


if __name__ == "__main__":
    raise SystemExit(main())
