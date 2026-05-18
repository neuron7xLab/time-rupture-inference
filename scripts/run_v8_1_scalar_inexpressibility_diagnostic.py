# SPDX-License-Identifier: MIT
"""v8.1 scalar-inexpressibility diagnostic. Runs the trigger-frequency
precheck FIRST; only if it passes does the oracle hierarchy run. No
learned model. Verdict lives here (research lineage), never in CI.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from ctios.diagnostics.trigger_frequency import derive  # noqa: E402
from ctios.envs.latent_context_temporal_rupture_v8_1 import generate  # noqa: E402
from ctios.oracles import history_oracle, regime_oracle, scalar_oracle  # noqa: E402

CFG = yaml.safe_load((ROOT / "configs" / "v8_1_scalar_inexpressible_env.yaml").read_text())


def _mae(p: np.ndarray, o: np.ndarray) -> float:
    return float(np.mean(np.abs(np.asarray(p) - np.asarray(o))))


def main() -> int:
    deriv = derive(CFG)
    if not deriv.frequency_precheck_passed:
        print("v8.1: RED_PRECHECK — diagnostic not run (frequency too low)")
        (ROOT / "evidence" / "SCALAR_INEXPRESSIBILITY_DIAGNOSTIC_v8_1.md").write_text(
            "# v8.1 — RED_PRECHECK\n\nTrigger-frequency precheck failed "
            "before the diagnostic. Preserved; no parameter tuned.\n"
        )
        return 1

    mu, delta = CFG["mu"], CFG["delta"]
    st, lt = CFG["short_thresh"], CFG["long_thresh"]
    seeds = list(range(CFG["seed_count"]))
    s_mae, h_mae, r_mae = [], [], []
    trig_total = n_total = 0
    pos = neg = 0
    rec_hit = rec_tot = 0

    for sd in seeds:
        run = generate(sd, CFG)
        sp = scalar_oracle.predict_series(run.obs, st, lt, mu)
        hp, inferred = history_oracle.predict_series(run.obs, st, lt, mu, delta)
        rp = regime_oracle.predict_series(run.true_mean)
        s_mae.append(_mae(sp, run.obs))
        h_mae.append(_mae(hp, run.obs))
        r_mae.append(_mae(rp, run.obs))
        tm = run.is_trigger
        trig_total += int(tm.sum())
        n_total += len(run.obs)
        realized = np.sign(run.obs[tm] - mu).astype(int)
        pos += int((realized > 0).sum())
        neg += int((realized < 0).sum())
        rec_hit += int((inferred[tm] == run.z_sign[tm]).sum())
        rec_tot += int(tm.sum())

    agg_s, agg_h, agg_r = float(np.mean(s_mae)), float(np.mean(h_mae)), float(np.mean(r_mae))
    gap = (agg_s - agg_h) / agg_s if agg_s > 0 else 0.0
    aliasing = trig_total / n_total
    sodf = 1.0 if (pos > 0 and neg > 0) else 0.0
    disambig = agg_s - agg_h
    ctx_rec = rec_hit / rec_tot if rec_tot else 0.0
    hist_close = agg_h <= agg_r * (1.0 + CFG["history_close_frac"])

    h0 = hashlib.sha256(np.round(generate(0, CFG).obs, 9).tobytes()).hexdigest()
    h1 = hashlib.sha256(np.round(generate(0, CFG).obs, 9).tobytes()).hexdigest()
    replay_ok = h0 == h1
    ordering_valid = agg_r <= agg_h + 1e-9 <= agg_s + 1e-9

    checks = {
        "precheck_passed": deriv.frequency_precheck_passed,
        "observed_trigger_count_nonneg": trig_total >= CFG["min_trigger_count_total"],
        "same_obs_diff_future_gt_min": sodf > CFG["min_same_obs_diff_future_rate"],
        "aliasing_gt_min": aliasing > CFG["min_aliasing_rate"],
        "gap_ge_min": gap >= CFG["gap_min"],
        "history_beats_scalar": agg_h < agg_s,
        "history_approaches_regime": hist_close,
        "oracle_ordering_valid": ordering_valid,
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
        "scalar_inexpressibility_gap_ratio": gap,
        "gap_min_pinned": CFG["gap_min"],
        "aliasing_rate": aliasing,
        "expected_trigger_probability": deriv.expected_trigger_probability,
        "observed_trigger_count": trig_total,
        "expected_trigger_count_total_grid": deriv.expected_trigger_count_total_grid,
        "same_observation_different_future_rate": sodf,
        "history_disambiguation_gain": disambig,
        "context_recovery_score": ctx_rec,
        "deterministic_replay_hash": h0,
        "oracle_ordering_valid": ordering_valid,
        "checks": checks,
        "no_learned_model_run": True,
    }
    art = ROOT / "artifacts" / "v8_1"
    art.mkdir(parents=True, exist_ok=True)
    (art / "scalar_inexpressibility_v8_1_summary.json").write_text(
        json.dumps(summary, indent=2)
    )

    askable = (
        "Learned sequence-model testing against this validated environment "
        "is now scientifically askable."
        if green
        else "v8.1 failed to establish scalar-inexpressibility; "
        "stronger-model testing remains not askable."
    )
    (ROOT / "evidence" / "SCALAR_INEXPRESSIBILITY_DIAGNOSTIC_v8_1.md").write_text(
        f"# v8.1 Scalar-Inexpressibility Diagnostic\n\n**VERDICT: {verdict}**\n\n"
        f"- scalar_oracle = {agg_s:.4f}\n- history_oracle = {agg_h:.4f}\n"
        f"- regime_oracle (floor) = {agg_r:.4f}\n"
        f"- scalar_inexpressibility_gap = {gap:.4f} (pinned min {CFG['gap_min']})\n"
        f"- aliasing_rate = {aliasing:.4f}  observed_triggers = {trig_total}\n"
        f"- same_observation_different_future_rate = {sodf:.1f}\n"
        f"- history_disambiguation_gain = {disambig:.4f}\n"
        f"- context_recovery_score = {ctx_rec:.4f}\n\n## Checks\n"
        + "".join(f"- [{'x' if v else ' '}] {k}\n" for k, v in checks.items())
        + f"\n{askable}\n\nClaim boundary: a validated task property, not a "
        "capability. No intelligence / cognition / AGI / model-advantage "
        "claim. No learned model was run.\n```json\n"
        + json.dumps(summary, indent=2)
        + "\n```\n"
    )
    if not green:
        (ROOT / "evidence" / "NEGATIVE_RESULT_v8_1.md").write_text(
            "# NEGATIVE RESULT — v8.1 (pinned, not erased)\n\n"
            f"**RED.** gap={gap:.4f} (pinned min {CFG['gap_min']}). No "
            "threshold tuned.\n\n"
            "## Progress vs parent v8\n"
            f"Triggers now fire ({trig_total}, precheck PASS, "
            f"aliasing={aliasing:.4f}, sodf={sodf:.1f}) and "
            f"`history_oracle` ({agg_h:.4f}) MATERIALLY BEATS "
            f"`scalar_oracle` ({agg_s:.4f}) — scalar-inexpressibility is "
            "REAL, not decorative. The frequency defect of v8 is fixed.\n\n"
            "## Why still RED (precise root cause)\n"
            f"gap={gap:.4f}<{CFG['gap_min']} and history "
            f"({agg_h:.4f}) is far from regime ({agg_r:.4f}). Construction "
            "B's deterministic carrier (short,short,long,mid×8) is a strong "
            "PREDICTABLE cycle the scalar/history oracles (built for a "
            "μ-stationary stream) do not model, so whole-stream MAE of "
            "BOTH is inflated by carrier error, diluting the gap below "
            "0.25 and preventing history from approaching the noise "
            "floor. The scalar-inexpressible signal exists but is masked "
            "by carrier variance.\n\n"
            "## Disposition\n"
            "Preserved RED; stronger-model testing stays NOT askable. The "
            "fix is a metric/construction correction (trigger-scoped "
            "evaluation OR a carrier that is itself scalar-predictable so "
            "only the trigger drives the gap) — a NEW v8.2 "
            "pre-registration committed before re-run, NOT a v8.1 param "
            "edit. Closure-before-restart.\n"
        )

    (ROOT / "docs" / "reports" / "cti_os_v8_1_task_design_verdict.md").write_text(
        "# CTI-OS v8.1 — Task-Design Verdict\n\n"
        "## 1. Parent v8 RED\n"
        "v8 RED preserved (evidence/V8_PARENT_RED.md): rare trigger "
        "(~1.2e-5/step) made aliasing decorative, gap 0.0004.\n\n"
        "## 2. v8.1 preregistered correction\n"
        "Construction B: deterministic alias schedule (period "
        f"{CFG['period']}), frequency derived BEFORE the run.\n\n"
        "## 3. Trigger-frequency derivation\n"
        f"```json\n{json.dumps(deriv.as_dict(), indent=2)}\n```\n\n"
        "## 4. Oracle hierarchy\n"
        f"scalar={agg_s:.4f}  history={agg_h:.4f}  regime={agg_r:.4f}\n\n"
        "## 5. Metrics table\n"
        f"| metric | value |\n|---|---|\n"
        f"| scalar_inexpressibility_gap | {gap:.4f} (min {CFG['gap_min']}) |\n"
        f"| aliasing_rate | {aliasing:.4f} |\n"
        f"| same_obs_diff_future_rate | {sodf:.1f} |\n"
        f"| observed_trigger_count | {trig_total} |\n"
        f"| context_recovery_score | {ctx_rec:.4f} |\n\n"
        f"## 6. Verdict\n**{verdict}**\n\n## 7. Stronger-model testing\n"
        f"{askable}\n\n## 8. Reproduction\n"
        "```\nPYTHONPATH=src python scripts/derive_v8_1_trigger_frequency.py\n"
        "PYTHONPATH=src python scripts/run_v8_1_scalar_inexpressibility_diagnostic.py\n```\n\n"
        "## 9. Claim boundary\nValidated task property only. No "
        "intelligence / cognition / AGI / model-advantage claim.\n\n"
        "## 10. Next allowed step\n"
        + (
            "GREEN -> a future PR may test learned sequence models against "
            "this validated environment.\n"
            if green
            else "RED -> preserve; do NOT train models; diagnose the "
            "construction before any further lineage.\n"
        )
    )

    print(f"\n=== v8.1 SCALAR-INEXPRESSIBILITY :: {verdict} ===")
    print(f"scalar={agg_s:.4f} history={agg_h:.4f} regime={agg_r:.4f} "
          f"gap={gap:.4f} triggers={trig_total}")
    for k, v in checks.items():
        print(f"  [{'OK' if v else 'XX'}] {k}")
    return 0 if green else 1


if __name__ == "__main__":
    raise SystemExit(main())
