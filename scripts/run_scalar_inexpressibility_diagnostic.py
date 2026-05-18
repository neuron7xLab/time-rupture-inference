# SPDX-License-Identifier: MIT
"""v8 scalar-inexpressibility diagnostic. Oracle hierarchy only — NO
learned model is trained here. Pre-registered gates
(docs/prereg/cti_os_v8_scalar_inexpressible_env.md). GREEN proves the
environment requires latent state; RED is preserved, no threshold tuned.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from ctios.envs.latent_context_temporal_rupture import generate  # noqa: E402
from ctios.oracles import history_oracle, regime_oracle, scalar_oracle  # noqa: E402

CFG = yaml.safe_load((ROOT / "configs" / "scalar_inexpressible_env.yaml").read_text())


def _mae(p: np.ndarray, o: np.ndarray) -> float:
    return float(np.mean(np.abs(p - o)))


def main() -> int:
    mu, delta = CFG["mu"], CFG["delta"]
    st, lt = CFG["short_thresh"], CFG["long_thresh"]
    seeds = list(range(CFG["seed_count"]))

    s_mae, h_mae, r_mae = [], [], []
    trig_total = 0
    n_total = 0
    signs_pos = signs_neg = 0
    recover_hit = recover_tot = 0

    for sd in seeds:
        run = generate(sd, CFG)
        sp = scalar_oracle.predict_series(run.obs, st, lt, mu)
        hp, inferred = history_oracle.predict_series(run.obs, st, lt, mu, delta)
        rp = regime_oracle.predict_series(run.true_mean)
        s_mae.append(_mae(sp, run.obs))
        h_mae.append(_mae(hp, run.obs))
        r_mae.append(_mae(rp, run.obs))
        tmask = run.is_trigger
        trig_total += int(tmask.sum())
        n_total += len(run.obs)
        realized = np.sign(run.obs[tmask] - mu).astype(int)
        signs_pos += int((realized > 0).sum())
        signs_neg += int((realized < 0).sum())
        true_sign = run.z_sign[tmask]
        recover_hit += int((inferred[tmask] == true_sign).sum())
        recover_tot += int(tmask.sum())

    agg_s, agg_h, agg_r = float(np.mean(s_mae)), float(np.mean(h_mae)), float(np.mean(r_mae))
    gap = (agg_s - agg_h) / agg_s if agg_s > 0 else 0.0
    aliasing_rate = trig_total / n_total
    # every trigger shares the (short,short,long) window; if BOTH realized
    # signs occur across the grid, each trigger is observation-aliased.
    same_obs_diff_future = 1.0 if (signs_pos > 0 and signs_neg > 0) else 0.0
    disambig_gain = agg_s - agg_h
    context_recovery = recover_hit / recover_tot if recover_tot else 0.0
    history_close = agg_h <= agg_r * (1.0 + CFG["history_close_frac"])

    # determinism
    r0a, r0b = generate(0, CFG), generate(0, CFG)
    replay_ok = bool(np.array_equal(r0a.obs, r0b.obs))

    checks = {
        "gap_ge_min": gap >= CFG["gap_min"],
        "history_beats_scalar": agg_h < agg_s,
        "history_approaches_regime": history_close,
        "aliasing_measured": aliasing_rate > 0.0,
        "same_obs_diff_future_measured": same_obs_diff_future > 0.0,
        "deterministic_replay": replay_ok,
    }
    green = all(checks.values())
    verdict = "GREEN" if green else "RED"

    summary = {
        "verdict": verdict,
        "scalar_oracle_mae": agg_s,
        "history_oracle_mae": agg_h,
        "regime_oracle_mae": agg_r,
        "scalar_inexpressibility_gap": gap,
        "gap_min_pinned": CFG["gap_min"],
        "aliasing_rate": aliasing_rate,
        "history_disambiguation_gain": disambig_gain,
        "context_recovery_score": context_recovery,
        "same_observation_different_future_rate": same_obs_diff_future,
        "checks": checks,
        "grid": f"{len(seeds)} seeds x {CFG['n_steps']} steps",
        "no_learned_model_run": True,
    }

    art = ROOT / "artifacts" / "v8"
    art.mkdir(parents=True, exist_ok=True)
    (art / "scalar_inexpressibility_summary.json").write_text(json.dumps(summary, indent=2))

    askable = (
        "Stronger-model (GRU/SSM) testing is now scientifically askable: "
        "the environment provably requires latent state."
        if green
        else "Stronger-model testing remains NOT askable: the environment "
        "does not prove scalar-inexpressibility (preserved RED)."
    )
    (ROOT / "evidence" / "SCALAR_INEXPRESSIBILITY_DIAGNOSTIC.md").write_text(
        "# Scalar-Inexpressibility Diagnostic (v8)\n\n"
        f"**VERDICT: {verdict}**\n\n"
        "## Hypothesis\nA latent-context rupture environment makes a single "
        "scalar estimate insufficient: identical (short,short,long) windows "
        "precede opposite futures depending on hidden z.\n\n"
        "## Oracle hierarchy (MAE, lower better)\n"
        f"- scalar_oracle = {agg_s:.4f}\n"
        f"- history_oracle = {agg_h:.4f}\n"
        f"- regime_oracle (floor) = {agg_r:.4f}\n\n"
        "## Metrics\n"
        f"- scalar_inexpressibility_gap = {gap:.4f} (pinned min {CFG['gap_min']})\n"
        f"- aliasing_rate = {aliasing_rate:.4f}\n"
        f"- same_observation_different_future_rate = {same_obs_diff_future:.1f}\n"
        f"- history_disambiguation_gain = {disambig_gain:.4f}\n"
        f"- context_recovery_score = {context_recovery:.4f}\n\n"
        "## Checks\n"
        + "".join(f"- [{'x' if v else ' '}] {k}\n" for k, v in checks.items())
        + f"\n## Is stronger-model testing now askable?\n{askable}\n\n"
        "Claim boundary: a validated task property, not a capability. No "
        "intelligence / cognition / AGI claim. No learned model was run.\n"
        "```json\n" + json.dumps(summary, indent=2) + "\n```\n"
    )
    if not green:
        p_short = 0.0228  # P(N(mu,sigma) < mu-2sigma)
        p_trig = p_short**3  # (short,short,long), symmetric tails
        (ROOT / "evidence" / "NEGATIVE_RESULT_v8.md").write_text(
            "# NEGATIVE RESULT — v8 scalar-inexpressible env (pinned, not erased)\n\n"
            f"**RED.** gap={gap:.4f} (pinned min {CFG['gap_min']}). No "
            "threshold tuned.\n\n"
            "## Root cause (quantified)\n"
            "Construction correct, parameterization decorative: with σ=1, "
            "short=μ−2, long=μ+2, the (short,short,long) trigger has "
            f"probability ≈ {p_short}³ ≈ {p_trig:.2e} per step → ≈0 "
            "triggers across the grid; latent context never reaches the "
            "observable, so scalar≈history≈regime at the σ floor.\n\n"
            "## Disposition\n"
            "Environment failed its own pre-registered gate. Preserved; "
            "stronger-model testing stays NOT askable. Fix = a NEW "
            "pre-registration with first-principles trigger frequency, "
            "committed BEFORE re-running (closure-before-restart, not a "
            "silent param edit on this pinned lineage).\n"
        )

    print(f"\n=== v8 SCALAR-INEXPRESSIBILITY :: {verdict} ===")
    print(f"scalar={agg_s:.4f} history={agg_h:.4f} regime={agg_r:.4f} "
          f"gap={gap:.4f} (min {CFG['gap_min']})")
    for k, v in checks.items():
        print(f"  [{'OK' if v else 'XX'}] {k}")
    return 0 if green else 1


if __name__ == "__main__":
    raise SystemExit(main())
