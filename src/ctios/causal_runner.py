# SPDX-License-Identifier: MIT
"""v5 minimal causal-action runner. CLI: --mode sanity | full.

GREEN exit 0 only if the fail-closed causal gate passes (full mode).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import inspect
import json
import subprocess
import sys
from typing import Any

import numpy as np
import yaml

from ctios.causal_agents import CausalLearnedAgent, NoActionAgent, RandomActionAgent
from ctios.causal_env import CausalEnvironment, CausalObservation
from ctios.causal_gate import evaluate
from ctios.causal_metrics import causal_action_gain, run_metrics
from ctios.contract import EVAL_HORIZON as EVAL_H
from ctios.contract import N_STEPS, SIGMA, T_STAR, TAU0, validate_window
from ctios.utils import ROOT

# v4/v5 share ONE invariant channel (ctios.contract). No magic literals.


def _make_agent(kind: str, seed: int):
    if kind == "no_action":
        return NoActionAgent()
    if kind == "random_action":
        return RandomActionAgent(seed=seed)
    return CausalLearnedAgent()


def _run(env: CausalEnvironment, agent, n: int) -> dict[str, Any]:
    env.reset()
    errs = np.empty(n)
    actions: list[str] = []
    prev_err: float | None = None
    for _k in range(n):
        pred = agent.predict()
        act = agent.select_action(prev_err)
        obs = env.step(act)
        err = obs.observed_interval - pred
        env.record_error(err)
        agent.update(obs.observed_interval, act)
        errs[_k] = err
        actions.append(act)
        prev_err = err
    return {"errors": errs, "actions": actions}


def _hash(e: np.ndarray) -> str:
    return hashlib.sha256(np.round(e, 9).tobytes()).hexdigest()


def _no_leakage_ok() -> bool:
    import dataclasses

    fields = {f.name for f in dataclasses.fields(CausalObservation)}
    if fields != {"step", "observed_interval", "previous_action", "previous_error"}:
        return False
    from ctios import causal_agents as CA

    for cls in (CA.NoActionAgent, CA.RandomActionAgent, CA.CausalLearnedAgent):
        params = set(inspect.signature(cls.__init__).parameters)
        if params & {"tau0", "tau1", "t_star", "sigma", "hidden", "schedule", "regime"}:
            return False
    src = inspect.getsource(CA.CausalLearnedAgent)
    return all(t not in src for t in ("tau0", "tau1", "t_star", "_Hidden", "regime"))


def _interventional_effect_probe(seed: int, delta: float) -> bool:
    """Structural: in interventional mode all-stabilize must change the
    trajectory vs all-observe (same hidden schedule)."""

    def fixed(action: str) -> float:
        env = CausalEnvironment(
            TAU0, TAU0 + delta, T_STAR, SIGMA, N_STEPS, seed, mode="interventional"
        )
        env.reset()
        ae = []
        for k in range(N_STEPS):
            obs = env.step(action)
            ae.append(abs(obs.observed_interval - (TAU0 if k < T_STAR else TAU0 + delta)))
        validate_window(T_STAR, EVAL_H, len(ae))
        return float(np.mean(ae[T_STAR : T_STAR + EVAL_H]))

    return abs(fixed("stabilize") - fixed("observe")) > 1e-6


def _action_null_inertness(seed: int, delta: float) -> bool:
    """In action_null mode all-stabilize must NOT change the trajectory."""

    def series(action: str) -> str:
        env = CausalEnvironment(
            TAU0, TAU0 + delta, T_STAR, SIGMA, N_STEPS, seed, mode="action_null"
        )
        env.reset()
        return _hash(np.array([env.step(action).observed_interval for _ in range(N_STEPS)]))

    return series("stabilize") == series("observe")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["sanity", "full"], default="sanity")
    args = ap.parse_args()

    pre = yaml.safe_load(
        (ROOT / "prereg" / "v5_causal_action_preregistration.yaml").read_text()
    )
    thr = pre["thresholds"]
    if args.mode == "sanity":
        seeds, deltas = list(range(3)), [4.0]
    else:
        seeds = list(range(pre["grid"]["seeds"]))
        deltas = [float(d) for d in pre["grid"]["shift_deltas"]]

    kinds = ["causal_learned", "no_action", "random_action"]
    rows: list[dict[str, Any]] = []
    # post_mae[mode][kind][(delta,seed)] = value
    pm: dict[str, dict[str, dict[tuple, float]]] = {
        m: {k: {} for k in kinds} for m in ("interventional", "action_null")
    }
    replay_ok = True

    for delta in deltas:
        for seed in seeds:
            for mode in ("interventional", "action_null"):
                for kind in kinds:
                    env = CausalEnvironment(
                        TAU0, TAU0 + delta, T_STAR, SIGMA, N_STEPS, seed, mode=mode
                    )
                    ag = _make_agent(kind, seed)
                    r = _run(env, ag, N_STEPS)
                    mt = run_metrics(r["errors"], r["actions"], T_STAR, EVAL_H)
                    pm[mode][kind][(delta, seed)] = mt["post_shift_mae"]
                    if mode == "interventional" and kind == "causal_learned" and seed == 0:
                        env2 = CausalEnvironment(
                            TAU0, TAU0 + delta, T_STAR, SIGMA, N_STEPS, seed, mode=mode
                        )
                        r2 = _run(env2, _make_agent(kind, seed), N_STEPS)
                        replay_ok &= _hash(r["errors"]) == _hash(r2["errors"])
                    rows.append(
                        {
                            "run_id": f"{kind}-{mode}-d{delta}-s{seed}",
                            "seed": seed,
                            "mode": mode,
                            "agent": kind,
                            "shift_delta": delta,
                            "pre_shift_mae": mt["pre_shift_mae"],
                            "post_shift_mae": mt["post_shift_mae"],
                            "post_shift_aue": mt["post_shift_aue"],
                            "adaptation_time": mt["adaptation_time"],
                            "action_counts": json.dumps(mt["action_counts"]),
                            "stabilize_fraction_post_shift": mt[
                                "stabilize_fraction_post_shift"
                            ],
                            "replay_hash": _hash(r["errors"]),
                            "pass_fail": "n/a",
                            "failure_reason": "",
                        }
                    )

    grid = [(d, s) for d in deltas for s in seeds]
    gain = float(
        np.mean(
            [
                causal_action_gain(
                    pm["action_null"]["causal_learned"][g],
                    pm["interventional"]["causal_learned"][g],
                )
                for g in grid
            ]
        )
    )
    action_null_gap = float(
        np.mean(
            [
                abs(
                    pm["action_null"]["causal_learned"][g]
                    - pm["action_null"]["no_action"][g]
                )
                for g in grid
            ]
        )
    )
    win_no = float(
        np.mean(
            [
                pm["interventional"]["causal_learned"][g]
                < pm["interventional"]["no_action"][g]
                for g in grid
            ]
        )
    )
    win_rnd = float(
        np.mean(
            [
                pm["interventional"]["causal_learned"][g]
                < pm["interventional"]["random_action"][g]
                for g in grid
            ]
        )
    )
    eff_present = all(_interventional_effect_probe(s, deltas[0]) for s in seeds[:3])
    null_inert = all(_action_null_inertness(s, deltas[0]) for s in seeds[:3])

    ev = ROOT / "evidence"
    with (ev / "v5_causal_metrics_summary.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    with (ev / "v5_causal_ledger.jsonl").open("w") as f:
        for r in rows:
            f.write(json.dumps(r, default=float) + "\n")

    if args.mode == "sanity":
        print(
            f"[sanity] gain={gain:.4f} null_gap={action_null_gap:.4f} "
            f"win_vs_no_action={win_no:.2f} win_vs_random={win_rnd:.2f} "
            f"eff_present={eff_present} null_inert={null_inert} replay={replay_ok}"
        )
        return 0

    v4_tests = (
        subprocess.run(
            [sys.executable, "-m", "pytest", "tests", "-q",
             "--ignore=tests/test_causal_env.py",
             "--ignore=tests/test_causal_agents.py",
             "--ignore=tests/test_causal_runner.py"],
            cwd=ROOT, env={**_env()}, capture_output=True,
        ).returncode
        == 0
    )
    v4_runner = (
        subprocess.run(
            [sys.executable, "-m", "ctios.runner", "--mode", "full"],
            cwd=ROOT, env={**_env()}, capture_output=True,
        ).returncode
        == 0
    )
    claim_ok = bool(pre.get("forbidden_claims")) and "intelligence" in pre["forbidden_claims"]

    gate = evaluate(
        v4_tests_pass=v4_tests,
        v4_runner_green=v4_runner,
        replay_ok=replay_ok,
        no_leakage_ok=_no_leakage_ok(),
        action_null_gap=action_null_gap,
        interventional_effect_present=eff_present and null_inert,
        causal_gain=gain,
        win_rate_vs_no_action=win_no,
        win_rate_vs_random=win_rnd,
        grid_reproduced=len(seeds) >= 30 and len(deltas) >= 3,
        evidence_written=True,
        claim_boundary_ok=claim_ok,
        thr=thr,
    )

    lines = [
        "# v5 Minimal Causal-Action — Release Gate",
        "",
        f"**Verdict: {'GREEN / PASS' if gate.green else 'RED / FAIL'}**",
        "",
        f"- causal_action_gain: {gain:.4f} (threshold {thr['min_causal_action_gain']})",
        f"- action_null_gap: {action_null_gap:.4f} "
        f"(max {thr['max_allowed_action_null_gap']})",
        f"- win-rate vs no_action: {win_no:.3f}",
        f"- win-rate vs random_action: {win_rnd:.3f}",
        f"- interventional effect present: {eff_present} · "
        f"action_null inert: {null_inert}",
        f"- v4 tests pass: {v4_tests} · v4 runner green: {v4_runner}",
        "",
        "## Claim boundary",
        "Allowed: causal-action gain under hidden temporal rupture, "
        "preregistered, replayable.",
        "Forbidden — NOT claimed: intelligence, consciousness, biological "
        "neuroplasticity-like fidelity, AGI, cognition, understanding time.",
        "",
        "## Checks",
        *[f"- [{'x' if v else ' '}] {k}" for k, v in gate.checks.items()],
    ]
    if gate.reasons:
        lines += ["", "## Failure reasons", *[f"- {r}" for r in gate.reasons]]
    (ev / "v5_causal_release_gate.md").write_text("\n".join(lines))

    if not gate.green:
        _write_negative(gate, gain, action_null_gap, win_no, win_rnd)

    print(f"\n=== v5 minimal causal-action :: {'PASS (GREEN)' if gate.green else 'FAIL (RED)'} ===")
    for k, v in gate.checks.items():
        print(f"  [{'OK' if v else 'XX'}] {k}")
    print(
        f"gain={gain:.4f} null_gap={action_null_gap:.4f} "
        f"win_no={win_no:.3f} win_rnd={win_rnd:.3f}"
    )
    return 0 if gate.green else 1


def _env() -> dict[str, str]:
    import os

    e = dict(os.environ)
    e["PYTHONPATH"] = str(ROOT / "src")
    return e


def _write_negative(gate, gain, gap, win_no, win_rnd) -> None:
    p = ROOT / "evidence" / "NEGATIVE_RESULT_v5.md"
    p.write_text(
        "# NEGATIVE RESULT — v5 minimal causal-action (pinned, not erased)\n\n"
        "**Verdict: RED / FAIL.** Reported as-is. No metric tuned.\n\n"
        f"- causal_action_gain = {gain:.4f}\n"
        f"- action_null_gap = {gap:.4f}\n"
        f"- win-rate vs no_action = {win_no:.3f}\n"
        f"- win-rate vs random_action = {win_rnd:.3f}\n\n"
        "## Failing checks\n" + "\n".join(f"- {r}" for r in gate.reasons) + "\n\n"
        "## Disposition\n"
        "v4 remains frozen and unaffected. The causal-action claim is the "
        "instrument under test; this RED is preserved before any next "
        "lineage. Intelligence / cognition is explicitly NOT claimed.\n"
    )


if __name__ == "__main__":
    raise SystemExit(main())
