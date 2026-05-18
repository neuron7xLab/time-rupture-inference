# SPDX-License-Identifier: MIT
"""v8.2 trigger-scoped + carrier-controlled diagnostic. No learned model.
Verdict (GREEN / PARTIAL_RED / RED) lives here, never in CI."""

from __future__ import annotations

import csv
import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from ctios.diagnostics.carrier_decomposition import channel_masks  # noqa: E402
from ctios.diagnostics.oracle_channel_analysis import analyse  # noqa: E402
from ctios.envs.latent_context_temporal_rupture_v8_1 import generate  # noqa: E402

CFG = yaml.safe_load((ROOT / "configs" / "v8_2_trigger_scoped_env.yaml").read_text())


def _git() -> str:
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                        capture_output=True, text=True, check=False)
    return r.stdout.strip() or "UNINITIALIZED"


def main() -> int:
    m = analyse(CFG)
    period = int(CFG["period"])
    structural = (
        m["trigger_count"] >= CFG["trigger_count_min"]
        and m["aliasing_rate"] >= CFG["aliasing_rate_min"]
        and m["same_observation_different_future_rate"] >= CFG["same_obs_diff_future_rate_min"]
        and m["total_mae_regime"] <= m["total_mae_history"] + 1e-9
        and m["total_mae_history"] <= m["total_mae_scalar"] + 1e-9
        and m["no_learned_model_run"]
    )
    tc_ok = m["trigger_context_gap_ratio"] >= CFG["trigger_context_gap_ratio_min"]
    cc_ok = m["carrier_controlled_gap_ratio"] >= CFG["carrier_controlled_gap_ratio_min"]
    h2r_ok = m["history_to_regime_distance"] <= CFG["history_to_regime_distance_max"]

    r0 = hashlib.sha256(np.round(generate(0, CFG).obs, 9).tobytes()).hexdigest()
    r1 = hashlib.sha256(np.round(generate(0, CFG).obs, 9).tobytes()).hexdigest()
    replay_ok = r0 == r1

    if not (structural and replay_ok):
        verdict = "RED"
    elif tc_ok and cc_ok and h2r_ok:
        verdict = "GREEN"
    elif tc_ok and (not cc_ok or not h2r_ok):
        verdict = "PARTIAL_RED"
    else:
        verdict = "RED"

    askable = verdict == "GREEN"
    art = ROOT / "artifacts" / "v8_2"
    art.mkdir(parents=True, exist_ok=True)
    payload = {**m, "verdict": verdict, "deterministic_replay_hash": r0,
               "structural_ok": structural, "replay_ok": replay_ok}
    (art / "metrics.json").write_text(json.dumps(payload, indent=2))
    with (art / "metrics.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["metric", "value"])
        for k, v in payload.items():
            w.writerow([k, v])
    run0 = generate(0, CFG)
    masks = channel_masks(run0.obs, run0.is_trigger, period)
    for name in ("trigger", "carrier", "background"):
        with (art / f"{name}_mask.csv").open("w", newline="") as f:
            csv.writer(f).writerows([[int(b)] for b in masks[name]])
    with (art / "oracle_predictions.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["step", "obs", "true_mean", "is_trigger"])
        for k in range(len(run0.obs)):
            w.writerow([k, float(run0.obs[k]), float(run0.true_mean[k]),
                        int(run0.is_trigger[k])])
    (art / "run_config_resolved.yaml").write_text(yaml.safe_dump(CFG))
    (art / "environment_fingerprint.json").write_text(json.dumps({
        "python": platform.python_version(), "numpy": np.__version__,
        "config_sha256": hashlib.sha256(
            (ROOT / "configs" / "v8_2_trigger_scoped_env.yaml").read_bytes()
        ).hexdigest(),
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }, indent=2))
    (art / "git_commit.txt").write_text(_git() + "\n")
    (art / "deterministic_replay_hash.txt").write_text(r0 + "\n")

    body = (
        f"# v8.2 Trigger-Scoped / Carrier-Controlled Diagnostic\n\n"
        f"**VERDICT: {verdict}**\n\n"
        f"## Channel MAE (scalar / history / regime)\n"
        f"- total:   {m['total_mae_scalar']:.4f} / {m['total_mae_history']:.4f}"
        f" / {m['total_mae_regime']:.4f}\n"
        f"- trigger: {m['trigger_context_mae_scalar']:.4f} /"
        f" {m['trigger_context_mae_history']:.4f} /"
        f" {m['trigger_context_mae_regime']:.4f}\n"
        f"- carrier: {m['carrier_mae_scalar']:.4f} /"
        f" {m['carrier_mae_history']:.4f} / {m['carrier_mae_regime']:.4f}\n"
        f"- background: {m['background_mae_scalar']:.4f} /"
        f" {m['background_mae_history']:.4f} /"
        f" {m['background_mae_regime']:.4f}\n\n"
        f"## Gap hierarchy\n"
        f"- trigger_context_gap_ratio = {m['trigger_context_gap_ratio']:.4f}"
        f" (min {CFG['trigger_context_gap_ratio_min']}) -> {tc_ok}\n"
        f"- carrier_controlled_gap_ratio = "
        f"{m['carrier_controlled_gap_ratio']:.4f}"
        f" (min {CFG['carrier_controlled_gap_ratio_min']}) -> {cc_ok}\n"
        f"- whole_stream_gap_ratio = {m['whole_stream_gap_ratio']:.4f}"
        f" (min {CFG['whole_stream_gap_ratio_min']})\n"
        f"- history_to_regime_distance = "
        f"{m['history_to_regime_distance']:.4f}"
        f" (max {CFG['history_to_regime_distance_max']}) -> {h2r_ok}\n"
        f"- structural_ok={structural} replay_ok={replay_ok}\n\n"
        f"Stronger-model testing askable: {'yes' if askable else 'no'}.\n\n"
        "Claim boundary: a validated task-evaluation property only. No "
        "intelligence / cognition / AGI / model-advantage claim. No "
        "learned model was run.\n```json\n"
        + json.dumps(payload, indent=2) + "\n```\n"
    )
    (ROOT / "evidence" / "SCALAR_INEXPRESSIBILITY_DIAGNOSTIC_v8_2.md").write_text(body)
    (ROOT / "docs" / "reports" / "cti_os_v8_2_task_design_verdict.md").write_text(
        "# CTI-OS v8.2 — Task-Design Verdict\n\n"
        "## 1. Parent v8.1 RED\nPreserved (evidence/V8_1_PARENT_RED.md): "
        "real but carrier-masked scalar-inexpressibility, gap 0.1525.\n\n"
        "## 2. Why whole-stream MAE masked the signal\nThe deterministic "
        "carrier inflated both stationary-oracle MAEs, diluting the "
        "trigger-specific gap below 0.25.\n\n"
        "## 3. Trigger-scoped metric\nMAE restricted to the aliased "
        "z-dependent trigger windows.\n\n"
        "## 4. Carrier-controlled metric\nObservation-derived phase mean "
        "(no z / future / schedule) removed from both oracles; residual "
        "z-channel compared.\n\n"
        "## 5. Oracle hierarchy\nscalar < history < regime by access; "
        "regime = floor.\n\n## 6. Metrics\n```json\n"
        + json.dumps(payload, indent=2) + "\n```\n\n"
        f"## 7. Verdict\n**{verdict}**\n\n## 8. Stronger-model testing\n"
        + ("askable.\n" if askable else "NOT askable.\n")
        + "\n## 9. Claim boundary\nValidated task-evaluation property "
        "only; no capability/cognition/AGI claim.\n\n## 10. Next PR\n"
        + (
            "GREEN -> a future PR may test learned sequence models against "
            "this carrier-controlled benchmark.\n"
            if verdict == "GREEN"
            else "Not GREEN -> preserve; diagnose before any further "
            "lineage. No model.\n"
        )
    )
    if verdict != "GREEN":
        (ROOT / "evidence" / f"NEGATIVE_RESULT_v8_2_{verdict}.md").write_text(
            f"# {verdict} — v8.2 (pinned, not erased)\n\n"
            f"trigger_context_gap_ratio={m['trigger_context_gap_ratio']:.4f}, "
            f"carrier_controlled_gap_ratio={m['carrier_controlled_gap_ratio']:.4f}"
            f", history_to_regime_distance={m['history_to_regime_distance']:.4f}"
            f". No threshold tuned. Stronger-model testing stays not "
            "askable. Preserve; next is a NEW pre-registration.\n"
        )

    print(f"\nCTI-OS v8.2 TASK-DESIGN STATUS: {verdict}")
    print("parent RED preserved: yes")
    print("learned model run: no")
    print(f"trigger-scoped signal: {'yes' if tc_ok else 'no'}")
    print(f"carrier-controlled validity: {'yes' if cc_ok else 'no'}")
    print(f"stronger-model testing askable: {'yes' if askable else 'no'}")
    print("next permitted PR: "
          + ("learned-model vs validated benchmark" if askable
             else "preserve RED; new pre-registration only"))
    return 0 if verdict in ("GREEN", "PARTIAL_RED") else 1


if __name__ == "__main__":
    raise SystemExit(main())
