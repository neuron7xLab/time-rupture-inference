# SPDX-License-Identifier: MIT
"""Orchestrate the oracle hierarchy over the v8.1 env and assemble the
v8.2 channel-decomposed metrics. No learned model is constructed."""

from __future__ import annotations

from typing import Any

import numpy as np

from ctios.diagnostics.carrier_decomposition import (
    carrier_aware_predictions,
    channel_masks,
)
from ctios.diagnostics.trigger_scoped_metrics import (
    channel_mae,
    gap_ratio,
    history_to_regime_distance,
)
from ctios.envs.latent_context_temporal_rupture_v8_1 import generate
from ctios.oracles import history_oracle, regime_oracle, scalar_oracle


def analyse(cfg: dict[str, Any]) -> dict[str, Any]:
    mu, delta = float(cfg["mu"]), float(cfg["delta"])
    st, lt = float(cfg["short_thresh"]), float(cfg["long_thresh"])
    period = int(cfg["period"])
    seeds = list(range(int(cfg["seed_count"])))

    acc: dict[str, list[float]] = {}
    trig_total = n_total = pos = neg = 0

    def add(key: str, val: float) -> None:
        acc.setdefault(key, []).append(val)

    for sd in seeds:
        run = generate(sd, cfg)
        masks = channel_masks(run.obs, run.is_trigger, period)
        sp = scalar_oracle.predict_series(run.obs, st, lt, mu)
        hp, _ = history_oracle.predict_series(run.obs, st, lt, mu, delta)
        rp = regime_oracle.predict_series(run.true_mean)
        scp, hcp = carrier_aware_predictions(run.obs, st, lt, mu, delta)

        sm = channel_mae(sp, run.obs, masks)
        hm = channel_mae(hp, run.obs, masks)
        rm = channel_mae(rp, run.obs, masks)
        scm = channel_mae(scp, run.obs, masks)
        hcm = channel_mae(hcp, run.obs, masks)

        for ch in ("total", "trigger", "carrier", "background"):
            add(f"scalar_{ch}", sm[ch])
            add(f"history_{ch}", hm[ch])
            add(f"regime_{ch}", rm[ch])
            add(f"scalar_carrier_{ch}", scm[ch])
            add(f"history_carrier_{ch}", hcm[ch])

        tm = run.is_trigger
        trig_total += int(tm.sum())
        n_total += len(run.obs)
        dev = np.sign(run.obs[tm] - mu).astype(int)
        pos += int((dev > 0).sum())
        neg += int((dev < 0).sum())

    m = {k: float(np.nanmean(v)) for k, v in acc.items()}

    tc_gap, tc_ratio = gap_ratio(m["scalar_trigger"], m["history_trigger"])
    cc_gap, cc_ratio = gap_ratio(
        m["scalar_carrier_trigger"], m["history_carrier_trigger"]
    )
    ws_gap, ws_ratio = gap_ratio(m["scalar_total"], m["history_total"])
    h2r = history_to_regime_distance(m["history_trigger"], m["regime_trigger"])

    return {
        "total_mae_scalar": m["scalar_total"],
        "total_mae_history": m["history_total"],
        "total_mae_regime": m["regime_total"],
        "trigger_context_mae_scalar": m["scalar_trigger"],
        "trigger_context_mae_history": m["history_trigger"],
        "trigger_context_mae_regime": m["regime_trigger"],
        "carrier_mae_scalar": m["scalar_carrier"],
        "carrier_mae_history": m["history_carrier"],
        "carrier_mae_regime": m["regime_carrier"],
        "background_mae_scalar": m["scalar_background"],
        "background_mae_history": m["history_background"],
        "background_mae_regime": m["regime_background"],
        "trigger_context_gap": tc_gap,
        "trigger_context_gap_ratio": tc_ratio,
        "carrier_controlled_gap": cc_gap,
        "carrier_controlled_gap_ratio": cc_ratio,
        "whole_stream_gap": ws_gap,
        "whole_stream_gap_ratio": ws_ratio,
        "history_to_regime_distance": h2r,
        "trigger_count": trig_total,
        "aliasing_rate": trig_total / n_total if n_total else 0.0,
        "same_observation_different_future_rate": 1.0 if (pos > 0 and neg > 0) else 0.0,
        "history_disambiguation_gain": m["scalar_trigger"] - m["history_trigger"],
        "no_learned_model_run": True,
    }
