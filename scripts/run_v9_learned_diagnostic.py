# SPDX-License-Identifier: MIT
"""v9 — learned recurrent model vs the validated v8.4 benchmark.

Anchored to the v8.4 oracles + analytic causal floor (emitted for
reference). Warm-scored trigger channel. Verdict (GREEN/RED) lives here,
never in CI. No threshold/env edited after results.
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

from ctios.diagnostics.causal_bound import derive  # noqa: E402
from ctios.diagnostics.trigger_scoped_metrics import (  # noqa: E402
    gap_ratio,
    history_to_regime_distance,
)
from ctios.envs.latent_context_temporal_rupture_v8_4 import generate  # noqa: E402
from ctios.learners.echo_state_learner import EchoStateLearner  # noqa: E402
from ctios.oracles import regime_oracle, scalar_oracle  # noqa: E402

CFG = yaml.safe_load((ROOT / "configs" / "v8_4_rederived_env.yaml").read_text())
ART = ROOT / "artifacts" / "v9"


def _warm(idx: np.ndarray) -> np.ndarray:
    return idx[1:] if idx.size else idx


def _learned_predictions(obs: np.ndarray, seed: int) -> np.ndarray:
    m = EchoStateLearner(dim=64, seed=seed, leak=0.3, ridge=1e-2)
    out = np.empty(len(obs))
    for k in range(len(obs)):
        out[k] = m.predict()
        m.update(float(obs[k]))
    return out


def main() -> int:
    bound = derive(CFG)
    ART.mkdir(parents=True, exist_ok=True)
    (ART / "causal_bound.json").write_text(json.dumps(bound.as_dict(), indent=2))

    mu = float(CFG["mu"])
    st, lt = float(CFG["short_thresh"]), float(CFG["long_thresh"])
    seeds = list(range(int(CFG["seed_count"])))
    L_t, S_t, R_t, L_all, S_all, R_all = [], [], [], [], [], []
    trig = ntot = pos = neg = 0

    for sd in seeds:
        run = generate(sd, CFG)
        o = run.obs
        wt = _warm(np.flatnonzero(run.is_trigger))
        lp = _learned_predictions(o, sd)
        sp = scalar_oracle.predict_series(o, st, lt, mu)
        rp = regime_oracle.predict_series(run.true_mean)
        L_t.append(float(np.mean(np.abs(lp[wt] - o[wt]))))
        S_t.append(float(np.mean(np.abs(sp[wt] - o[wt]))))
        R_t.append(float(np.mean(np.abs(rp[wt] - o[wt]))))
        L_all.append(float(np.mean(np.abs(lp - o))))
        S_all.append(float(np.mean(np.abs(sp - o))))
        R_all.append(float(np.mean(np.abs(rp - o))))
        tm = run.is_trigger
        trig += int(tm.sum())
        ntot += len(o)
        dev = np.sign(o[tm] - mu).astype(int)
        pos += int((dev > 0).sum())
        neg += int((dev < 0).sum())

    L, S, R = float(np.mean(L_t)), float(np.mean(S_t)), float(np.mean(R_t))
    h2r_learned = history_to_regime_distance(L, R)
    _, learned_vs_scalar = gap_ratio(S, L)            # >0 ⇒ learned beats scalar
    sodf = 1.0 if (pos > 0 and neg > 0) else 0.0
    structural = (
        trig >= CFG["trigger_count_min"]
        and trig / ntot >= CFG["aliasing_rate_min"]
        and sodf >= CFG["same_obs_diff_future_rate_min"]
        and float(np.mean(R_all)) <= float(np.mean(S_all)) + 1e-9
    )
    def _rhash() -> str:
        p = _learned_predictions(generate(0, CFG).obs, 0)
        return hashlib.sha256(np.round(p, 6).tobytes()).hexdigest()

    r0 = _rhash()
    replay_ok = r0 == _rhash()

    h2r_ok = h2r_learned <= CFG["history_to_regime_distance_max"]
    beats_scalar = learned_vs_scalar > 0.0
    not_below_floor = h2r_learned >= bound.h2r_causal_min - 1e-6
    green = (
        structural and replay_ok and h2r_ok and beats_scalar and not_below_floor
    )
    verdict = "GREEN" if green else "RED"

    payload = {
        "verdict": verdict,
        "learned_trigger_mae_warm": L,
        "scalar_trigger_mae_warm": S,
        "regime_trigger_mae_warm": R,
        "learned_to_regime_distance": h2r_learned,
        "learned_vs_scalar_gap_ratio": learned_vs_scalar,
        "analytic_h2r_causal_min": bound.h2r_causal_min,
        "beats_scalar": beats_scalar,
        "h2r_within_gate": h2r_ok,
        "not_below_information_floor": not_below_floor,
        "trigger_count": trig,
        "structural_ok": structural,
        "deterministic_replay_hash": r0,
        "learned_model_run": True,
    }
    (ART / "metrics.json").write_text(json.dumps(payload, indent=2))

    finding = (
        "GREEN — a small online-learned recurrent model recovers the "
        "latent-context scalar-inexpressible structure from observations "
        f"alone: warm-trigger h2r={h2r_learned:.4f} ≤ 0.35, beating the "
        f"scalar oracle (gap_ratio={learned_vs_scalar:.4f}) and staying "
        f"≥ the analytic causal floor ({bound.h2r_causal_min:.4f})."
        if green
        else (
            "RED — the learned model does NOT recover the structure on a "
            f"PROVABLY solvable task: h2r={h2r_learned:.4f} (gate 0.35), "
            f"learned_vs_scalar={learned_vs_scalar:.4f}, "
            f"learned_trig={L:.3f} scalar_trig={S:.3f} regime_trig={R:.3f}. "
            "A precise negative: discoverable ≠ discovered by this model. "
            "Preserved, not tuned."
        )
    )
    (ROOT / "evidence" / "LEARNED_VS_VALIDATED_v9.md").write_text(
        f"# v9 — Learned model vs validated v8.4 benchmark\n\n"
        f"**VERDICT: {verdict}**\n\n"
        f"- warm-trigger MAE: learned={L:.4f} scalar={S:.4f} regime={R:.4f}\n"
        f"- learned_to_regime_distance = {h2r_learned:.4f} (gate ≤0.35) -> {h2r_ok}\n"
        f"- learned_vs_scalar_gap_ratio = {learned_vs_scalar:.4f} (>0) -> {beats_scalar}\n"
        f"- analytic causal floor = {bound.h2r_causal_min:.4f} "
        f"(not-below = {not_below_floor})\n"
        f"- triggers={trig} structural={structural} replay={replay_ok}\n\n"
        f"## Finding\n{finding}\n\n"
        "Claim boundary: a preregistered, oracle-anchored recovery result "
        "only. No intelligence / cognition / AGI / general-capability "
        "claim.\n```json\n" + json.dumps(payload, indent=2) + "\n```\n"
    )
    (ROOT / "docs" / "reports" / "cti_os_v9_learned_verdict.md").write_text(
        "# CTI-OS v9 — Learned-model Verdict\n\n## Parent\n"
        "v8.4 GREEN preserved (validated benchmark, causal floor reachable).\n\n"
        f"## Verdict\n**{verdict}**\n\n{finding}\n\n"
        "## Next\n"
        + (
            "GREEN -> the line's terminal scientific question is answered "
            "positively under strict preregistration; future work = "
            "generality / external data (separate pre-registrations).\n"
            if green
            else "RED -> preserved; the structure is discoverable (v8.4) "
            "but not recovered by this learner. New pre-registration only.\n"
        )
        + "\n## Claim boundary\nNo capability / cognition / AGI claim.\n"
    )
    if not green:
        (ROOT / "evidence" / "NEGATIVE_RESULT_v9_RED.md").write_text(
            f"# RED — v9 (pinned, not erased)\n\nlearned h2r={h2r_learned:.4f} "
            f"(gate 0.35), vs_scalar={learned_vs_scalar:.4f}, analytic floor "
            f"{bound.h2r_causal_min:.4f}. Discoverable (v8.4) but not "
            "recovered by this learned model. No threshold tuned.\n"
        )

    print(f"\nCTI-OS v9 STATUS: {verdict}")
    print(f"learned_trig={L:.4f} scalar_trig={S:.4f} regime_trig={R:.4f}")
    print(f"h2r_learned={h2r_learned:.4f} (gate 0.35) "
          f"vs_scalar={learned_vs_scalar:.4f} floor={bound.h2r_causal_min:.4f}")
    return 0 if green else 1


if __name__ == "__main__":
    raise SystemExit(main())
