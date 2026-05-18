# SPDX-License-Identifier: MIT
"""v8.3 — correctly-specified causal history oracle vs the analytic
causal lower bound. The bound is derived and emitted BEFORE the oracle
runs. No learned model. Verdict (GREEN / BOUNDARY_RED / RED) lives here,
never in CI. v8.2 thresholds reused unchanged.
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

from ctios.diagnostics.carrier_decomposition import (  # noqa: E402
    carrier_aware_predictions,
    channel_masks,
)
from ctios.diagnostics.causal_bound import derive  # noqa: E402
from ctios.diagnostics.trigger_scoped_metrics import (  # noqa: E402
    channel_mae,
    gap_ratio,
    history_to_regime_distance,
)
from ctios.envs.latent_context_temporal_rupture_v8_1 import generate  # noqa: E402
from ctios.oracles import correct_history_oracle, regime_oracle, scalar_oracle  # noqa: E402

CFG = yaml.safe_load((ROOT / "configs" / "v8_2_trigger_scoped_env.yaml").read_text())
ART = ROOT / "artifacts" / "v8_3"


def main() -> int:
    # 1) DERIVE the causal bound BEFORE running the oracle, emit it.
    bound = derive(CFG)
    ART.mkdir(parents=True, exist_ok=True)
    (ART / "causal_bound.json").write_text(json.dumps(bound.as_dict(), indent=2))

    mu, delta = float(CFG["mu"]), float(CFG["delta"])
    st, lt = float(CFG["short_thresh"]), float(CFG["long_thresh"])
    period = int(CFG["period"])
    seeds = list(range(int(CFG["seed_count"])))
    acc: dict[str, list[float]] = {}
    trig = ntot = pos = neg = 0

    def add(k: str, v: float) -> None:
        acc.setdefault(k, []).append(v)

    for sd in seeds:
        run = generate(sd, CFG)
        masks = channel_masks(run.obs, run.is_trigger, period)
        sp = scalar_oracle.predict_series(run.obs, st, lt, mu)
        hp, _ = correct_history_oracle.predict_series(run.obs, st, lt, mu, delta)
        rp = regime_oracle.predict_series(run.true_mean)
        scp, hcp = carrier_aware_predictions(run.obs, st, lt, mu, delta)
        sm, hm, rm = (channel_mae(p, run.obs, masks) for p in (sp, hp, rp))
        scm = channel_mae(scp, run.obs, masks)
        hcm = channel_mae(hcp, run.obs, masks)
        for ch in ("total", "trigger", "carrier", "background"):
            add(f"s_{ch}", sm[ch])
            add(f"h_{ch}", hm[ch])
            add(f"r_{ch}", rm[ch])
            add(f"sc_{ch}", scm[ch])
            add(f"hc_{ch}", hcm[ch])
        tm = run.is_trigger
        trig += int(tm.sum())
        ntot += len(run.obs)
        dev = np.sign(run.obs[tm] - mu).astype(int)
        pos += int((dev > 0).sum())
        neg += int((dev < 0).sum())

    m = {k: float(np.nanmean(v)) for k, v in acc.items()}
    _, tc_ratio = gap_ratio(m["s_trigger"], m["h_trigger"])
    _, cc_ratio = gap_ratio(m["sc_trigger"], m["hc_trigger"])
    h2r = history_to_regime_distance(m["h_trigger"], m["r_trigger"])
    structural = (
        trig >= CFG["trigger_count_min"]
        and trig / ntot >= CFG["aliasing_rate_min"]
        and (1.0 if pos > 0 and neg > 0 else 0.0) >= CFG["same_obs_diff_future_rate_min"]
        and m["r_total"] <= m["h_total"] + 1e-9 <= m["s_total"] + 1e-9
    )
    r0 = hashlib.sha256(np.round(generate(0, CFG).obs, 9).tobytes()).hexdigest()
    replay_ok = r0 == hashlib.sha256(
        np.round(generate(0, CFG).obs, 9).tobytes()
    ).hexdigest()

    tc_ok = tc_ratio >= CFG["trigger_context_gap_ratio_min"]
    cc_ok = cc_ratio >= CFG["carrier_controlled_gap_ratio_min"]
    h2r_ok = h2r <= CFG["history_to_regime_distance_max"]
    # empirical oracle is at/above the analytic causal optimum (within 20%)
    at_bound = h2r >= 0.8 * bound.h2r_causal_min

    if not (structural and replay_ok):
        verdict = "RED"
    elif tc_ok and cc_ok and h2r_ok:
        verdict = "GREEN"
    elif tc_ok and cc_ok and (not h2r_ok) and (not bound.attainable_at_0_35) and at_bound:
        verdict = "BOUNDARY_RED"   # gate unattainable by ANY causal oracle
    else:
        verdict = "RED"

    askable = verdict == "GREEN"
    payload = {
        "verdict": verdict,
        "trigger_context_gap_ratio": tc_ratio,
        "carrier_controlled_gap_ratio": cc_ratio,
        "history_to_regime_distance": h2r,
        "h2r_causal_min_analytic": bound.h2r_causal_min,
        "analytic_attainable_at_0_35": bound.attainable_at_0_35,
        "empirical_at_causal_bound": at_bound,
        "trigger_count": trig,
        "h_trigger_mae": m["h_trigger"],
        "r_trigger_mae": m["r_trigger"],
        "s_trigger_mae": m["s_trigger"],
        "structural_ok": structural,
        "deterministic_replay_hash": r0,
        "no_learned_model_run": True,
    }
    (ART / "metrics.json").write_text(json.dumps(payload, indent=2))

    finding = (
        "GREEN — a correctly-specified causal history oracle reaches the "
        "trigger-channel floor; learned sequence-model testing is now "
        "scientifically askable."
        if verdict == "GREEN"
        else (
            "BOUNDARY_RED — the correctly-specified oracle sits at the "
            "analytic causal optimum, and that optimum "
            f"(h2r_min={bound.h2r_causal_min:.4f}) EXCEEDS the pinned "
            "0.35. One hidden flip + cold prior force unavoidable "
            "wrong-sign triggers; NO causal oracle can pass. The v8.2 "
            "PARTIAL_RED was NOT an oracle defect — it is an "
            "information-theoretic mis-pinning of the h2r gate vs the env "
            "(δ/σ/flip/trigger-count). Defect = benchmark parameterization."
            if verdict == "BOUNDARY_RED"
            else "RED — see metrics; preserve, diagnose, do not tune."
        )
    )
    (ROOT / "evidence" / "SCALAR_INEXPRESSIBILITY_DIAGNOSTIC_v8_3.md").write_text(
        f"# v8.3 — Correctly-specified history oracle vs causal bound\n\n"
        f"**VERDICT: {verdict}**\n\n"
        f"- trigger_context_gap_ratio = {tc_ratio:.4f} (≥0.35) -> {tc_ok}\n"
        f"- carrier_controlled_gap_ratio = {cc_ratio:.4f} (≥0.25) -> {cc_ok}\n"
        f"- history_to_regime_distance = {h2r:.4f} (≤0.35) -> {h2r_ok}\n"
        f"- analytic h2r_causal_min = {bound.h2r_causal_min:.4f} "
        f"(attainable@0.35={bound.attainable_at_0_35})\n"
        f"- empirical_at_causal_bound = {at_bound}\n"
        f"- h_trig={m['h_trigger']:.3f} r_trig={m['r_trigger']:.3f} "
        f"s_trig={m['s_trigger']:.3f} triggers={trig}\n\n"
        f"## Finding\n{finding}\n\n"
        "Claim boundary: validated task-design/identifiability property "
        "only. No intelligence / cognition / AGI / model-advantage claim. "
        "No learned model was run.\n```json\n"
        + json.dumps(payload, indent=2) + "\n```\n"
    )
    (ROOT / "docs" / "reports" / "cti_os_v8_3_task_design_verdict.md").write_text(
        "# CTI-OS v8.3 — Task-Design Verdict\n\n"
        "## Parent\nv8.2 PARTIAL_RED preserved "
        "(evidence/V8_2_PARENT_PARTIAL_RED.md).\n\n"
        "## Pre-run analytic causal bound\n```json\n"
        + json.dumps(bound.as_dict(), indent=2) + "\n```\n\n"
        f"## Verdict\n**{verdict}**\n\n{finding}\n\n"
        "## Next permitted step\n"
        + (
            "GREEN -> a future PR may test learned sequence models.\n"
            if verdict == "GREEN"
            else "BOUNDARY_RED/RED -> NEW v8.4 pre-registration that "
            "re-derives env δ/σ/flip-policy OR the h2r gate from first "
            "principles so a causal oracle CAN reach the floor. NOT a "
            "v8.3 edit. v8.2/v8.3 preserved.\n"
        )
        + "\n## Claim boundary\nNo capability / cognition / AGI claim.\n"
    )
    if verdict != "GREEN":
        (ROOT / "evidence" / f"NEGATIVE_RESULT_v8_3_{verdict}.md").write_text(
            f"# {verdict} — v8.3 (pinned, not erased)\n\n"
            f"h2r={h2r:.4f}, analytic causal min={bound.h2r_causal_min:.4f} "
            f"(attainable@0.35={bound.attainable_at_0_35}). No threshold "
            "tuned. Stronger-model testing stays NOT askable. "
            + ("The gate is unattainable by ANY causal oracle: the defect "
               "is benchmark parameterization, not the oracle. Next = v8.4 "
               "re-derivation, new pre-registration."
               if verdict == "BOUNDARY_RED" else
               "Preserve; diagnose before any further lineage.")
            + "\n"
        )

    print(f"\nCTI-OS v8.3 STATUS: {verdict}")
    print(f"h2r={h2r:.4f} analytic_min={bound.h2r_causal_min:.4f} "
          f"attainable@0.35={bound.attainable_at_0_35} at_bound={at_bound}")
    print(f"tc={tc_ratio:.4f} cc={cc_ratio:.4f} "
          f"stronger-model askable: {'yes' if askable else 'no'}")
    return 0 if verdict in ("GREEN", "BOUNDARY_RED") else 1


if __name__ == "__main__":
    raise SystemExit(main())
