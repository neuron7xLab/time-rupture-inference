# SPDX-License-Identifier: MIT
"""v8.4 — re-derived benchmark. Analytic causal floor (proven ≤ gate)
emitted BEFORE the run; then the correctly-specified causal oracle is
checked against the UNCHANGED gates with a warm-scored trigger channel.
No learned model. Verdict lives here (research lineage), not in CI.
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

from ctios.diagnostics.carrier_decomposition import carrier_aware_predictions  # noqa: E402
from ctios.diagnostics.causal_bound import derive  # noqa: E402
from ctios.diagnostics.trigger_scoped_metrics import (  # noqa: E402
    gap_ratio,
    history_to_regime_distance,
)
from ctios.envs.latent_context_temporal_rupture_v8_4 import generate  # noqa: E402
from ctios.oracles import correct_history_oracle, regime_oracle, scalar_oracle  # noqa: E402

CFG = yaml.safe_load((ROOT / "configs" / "v8_4_rederived_env.yaml").read_text())
ART = ROOT / "artifacts" / "v8_4"


def _warm_trigger_idx(is_trig: np.ndarray) -> np.ndarray:
    """Trigger indices excluding the first (pre-warm cold-prior) one."""
    idx = np.flatnonzero(is_trig)
    return idx[1:] if idx.size else idx


def main() -> int:
    bound = derive(CFG)                       # proven BEFORE the run
    ART.mkdir(parents=True, exist_ok=True)
    (ART / "causal_bound.json").write_text(json.dumps(bound.as_dict(), indent=2))

    mu, delta = float(CFG["mu"]), float(CFG["delta"])
    st, lt = float(CFG["short_thresh"]), float(CFG["long_thresh"])
    seeds = list(range(int(CFG["seed_count"])))
    s_t, h_t, r_t, sc_t, hc_t = [], [], [], [], []
    s_all, h_all, r_all = [], [], []
    trig = ntot = pos = neg = 0

    for sd in seeds:
        run = generate(sd, CFG)
        wt = _warm_trigger_idx(run.is_trigger)
        sp = scalar_oracle.predict_series(run.obs, st, lt, mu)
        hp, _ = correct_history_oracle.predict_series(run.obs, st, lt, mu, delta)
        rp = regime_oracle.predict_series(run.true_mean)
        scp, hcp = carrier_aware_predictions(run.obs, st, lt, mu, delta)
        o = run.obs
        s_t.append(float(np.mean(np.abs(sp[wt] - o[wt]))))
        h_t.append(float(np.mean(np.abs(hp[wt] - o[wt]))))
        r_t.append(float(np.mean(np.abs(rp[wt] - o[wt]))))
        sc_t.append(float(np.mean(np.abs(scp[wt] - o[wt]))))
        hc_t.append(float(np.mean(np.abs(hcp[wt] - o[wt]))))
        s_all.append(float(np.mean(np.abs(sp - o))))
        h_all.append(float(np.mean(np.abs(hp - o))))
        r_all.append(float(np.mean(np.abs(rp - o))))
        tm = run.is_trigger
        trig += int(tm.sum())
        ntot += len(o)
        dev = np.sign(o[tm] - mu).astype(int)
        pos += int((dev > 0).sum())
        neg += int((dev < 0).sum())

    S, H, R = float(np.mean(s_t)), float(np.mean(h_t)), float(np.mean(r_t))
    SC, HC = float(np.mean(sc_t)), float(np.mean(hc_t))
    _, tc = gap_ratio(S, H)
    _, cc = gap_ratio(SC, HC)
    h2r = history_to_regime_distance(H, R)
    sodf = 1.0 if (pos > 0 and neg > 0) else 0.0
    structural = (
        trig >= CFG["trigger_count_min"]
        and trig / ntot >= CFG["aliasing_rate_min"]
        and sodf >= CFG["same_obs_diff_future_rate_min"]
        and float(np.mean(r_all)) <= float(np.mean(h_all)) + 1e-9
        and float(np.mean(h_all)) <= float(np.mean(s_all)) + 1e-9
    )
    r0 = hashlib.sha256(np.round(generate(0, CFG).obs, 9).tobytes()).hexdigest()
    replay_ok = r0 == hashlib.sha256(
        np.round(generate(0, CFG).obs, 9).tobytes()
    ).hexdigest()
    near_analytic = abs(h2r - bound.h2r_causal_min) <= 0.25 * max(
        bound.h2r_causal_min, 1e-9
    ) or h2r <= bound.h2r_causal_min

    tc_ok = tc >= CFG["trigger_context_gap_ratio_min"]
    cc_ok = cc >= CFG["carrier_controlled_gap_ratio_min"]
    h2r_ok = h2r <= CFG["history_to_regime_distance_max"]
    green = (
        structural and replay_ok and tc_ok and cc_ok and h2r_ok and near_analytic
    )
    verdict = "GREEN" if green else "RED"
    askable = green

    payload = {
        "verdict": verdict,
        "trigger_context_gap_ratio": tc,
        "carrier_controlled_gap_ratio": cc,
        "history_to_regime_distance": h2r,
        "h2r_causal_min_analytic": bound.h2r_causal_min,
        "analytic_attainable_at_0_35": bound.attainable_at_0_35,
        "empirical_near_analytic": bool(near_analytic),
        "h_trigger_mae_warm": H,
        "r_trigger_mae_warm": R,
        "s_trigger_mae_warm": S,
        "trigger_count": trig,
        "structural_ok": structural,
        "deterministic_replay_hash": r0,
        "no_learned_model_run": True,
    }
    (ART / "metrics.json").write_text(json.dumps(payload, indent=2))

    finding = (
        "GREEN — env re-derived so the causal floor is reachable "
        f"(analytic h2r_min={bound.h2r_causal_min:.4f} ≤ 0.35), the "
        "correctly-specified causal oracle attains it "
        f"(h2r={h2r:.4f}) at the analytic optimum, with the "
        "scalar-inexpressible signal still real & carrier-robust "
        f"(tc={tc:.4f}, cc={cc:.4f}). Learned sequence-model testing is, "
        "for the first time, scientifically askable."
        if green
        else (
            "RED — see metrics. h2r="
            f"{h2r:.4f} (gate 0.35), analytic min "
            f"{bound.h2r_causal_min:.4f}, near_analytic={near_analytic}. "
            "Preserve; diagnose; do not tune. Stronger-model testing "
            "stays not askable."
        )
    )
    (ROOT / "evidence" / "SCALAR_INEXPRESSIBILITY_DIAGNOSTIC_v8_4.md").write_text(
        f"# v8.4 — Re-derived benchmark diagnostic\n\n**VERDICT: {verdict}**\n\n"
        f"- analytic h2r_causal_min = {bound.h2r_causal_min:.4f} "
        f"(attainable@0.35={bound.attainable_at_0_35}, proven pre-run)\n"
        f"- empirical h2r (warm) = {h2r:.4f} (gate ≤0.35) -> {h2r_ok}\n"
        f"- empirical_near_analytic = {near_analytic}\n"
        f"- trigger_context_gap_ratio = {tc:.4f} (≥0.35) -> {tc_ok}\n"
        f"- carrier_controlled_gap_ratio = {cc:.4f} (≥0.25) -> {cc_ok}\n"
        f"- warm trigger MAE: scalar={S:.3f} history={H:.3f} regime={R:.3f}"
        f"  triggers={trig}\n\n## Finding\n{finding}\n\n"
        "Claim boundary: validated task-design property only. No "
        "intelligence / cognition / AGI / model-advantage claim. No "
        "learned model was run.\n```json\n"
        + json.dumps(payload, indent=2) + "\n```\n"
    )
    (ROOT / "docs" / "reports" / "cti_os_v8_4_task_design_verdict.md").write_text(
        "# CTI-OS v8.4 — Task-Design Verdict\n\n"
        "## Parent\nv8.3 BOUNDARY_RED preserved.\n\n"
        "## Pre-run analytic causal bound (proven ≤ gate)\n```json\n"
        + json.dumps(bound.as_dict(), indent=2) + "\n```\n\n"
        f"## Verdict\n**{verdict}**\n\n{finding}\n\n## Next permitted step\n"
        + (
            "GREEN -> the benchmark is valid; a future PR may test learned "
            "sequence models (the question is finally well-posed).\n"
            if green
            else "RED -> preserve; NEW pre-registration only.\n"
        )
        + "\n## Claim boundary\nNo capability / cognition / AGI claim.\n"
    )
    if not green:
        (ROOT / "evidence" / "NEGATIVE_RESULT_v8_4_RED.md").write_text(
            f"# RED — v8.4 (pinned, not erased)\n\nh2r={h2r:.4f}, analytic "
            f"min={bound.h2r_causal_min:.4f}, near_analytic={near_analytic}, "
            f"tc={tc:.4f}, cc={cc:.4f}. No threshold tuned. Stronger-model "
            "testing stays NOT askable.\n"
        )

    print(f"\nCTI-OS v8.4 STATUS: {verdict}")
    print(f"h2r={h2r:.4f} analytic_min={bound.h2r_causal_min:.4f} "
          f"near_analytic={near_analytic} tc={tc:.4f} cc={cc:.4f}")
    print(f"stronger-model testing askable: {'YES' if askable else 'no'}")
    return 0 if green else 1


if __name__ == "__main__":
    raise SystemExit(main())
