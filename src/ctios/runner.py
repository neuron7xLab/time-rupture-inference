"""Orchestrator: multi-seed run, metrics, ledger, plots, fail-closed gate."""

from __future__ import annotations

import argparse
import csv
import hashlib
import time
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from ctios.agents import (
    Agent,
    ExpSmoothingAgent,
    InjectedAgent,
    LastIntervalAgent,
    LearnedAgent,
    MovingAverageAgent,
    OracleAgent,
    RandomAgent,
    make_ablations,
)
from ctios.env import Environment
from ctios.gates import evaluate_gate
from ctios.ledger import append, provenance
from ctios.metrics import Metrics, compute_metrics
from ctios.utils import ROOT, git_commit_epoch, jdump


def _load(name: str) -> dict[str, Any]:
    return yaml.safe_load((ROOT / "configs" / name).read_text())


def _build_agents(env: Environment, ecfg: dict, acfg: dict) -> dict[str, Agent]:
    prior = float(acfg["prior"])
    agents: dict[str, Agent] = {
        "last_interval": LastIntervalAgent(prior),
        f"moving_average_w{acfg['ma_window']}": MovingAverageAgent(acfg["ma_window"], prior),
        f"exp_smoothing_a{acfg['es_alpha']}": ExpSmoothingAgent(acfg["es_alpha"], prior),
        "random": RandomAgent(env.seed, ecfg["tau0"] * 0.5, ecfg["tau1"] * 1.5),
        "injected": InjectedAgent(ecfg["tau0"]),
        "oracle": OracleAgent(env.oracle_view()),
        "learned_full": LearnedAgent(prior=prior),
    }
    agents.update(make_ablations(prior))
    return agents


def _run_agent(env: Environment, agent: Agent, n: int, t_star: int) -> dict[str, Any]:
    env.reset()
    errs = np.empty(n, dtype=float)
    detection_step: int | None = None
    pre_alarms = 0
    for k in range(n):
        pred = agent.predict()
        obs = env.step()
        errs[k] = obs.observed_interval - pred
        agent.update(obs.observed_interval)
        if agent.drift_flag():
            if k < t_star:
                pre_alarms += 1
            elif detection_step is None:
                detection_step = k
    return {"errors": errs, "detection_step": detection_step, "pre_alarms": pre_alarms}


def _seed_hash(errs: np.ndarray) -> str:
    return hashlib.sha256(np.round(errs, 9).tobytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["baselines", "learned", "full"], default="full")
    args = ap.parse_args()

    run_epoch = int(time.time())
    ecfg = _load("env.yaml")
    acfg = _load("agents.yaml")
    mcfg = _load("metrics.yaml")
    xcfg = _load("experiment.yaml")
    prereg = yaml.safe_load((ROOT / "prereg" / "preregistration.yaml").read_text())["thresholds"]

    seeds = list(range(xcfg["n_seeds"]))
    n = ecfg["n_steps"]
    t_star = ecfg["t_star"]
    horizon = mcfg["eval_horizon"]
    band = mcfg["recovery_band_mult"]

    ledger = ROOT / "evidence" / "evidence_ledger.jsonl"
    ledger.unlink(missing_ok=True)
    prov = provenance()

    per_agent: dict[str, list[Metrics]] = {}
    replay_ok = True
    rows: list[dict[str, Any]] = []
    trace_for_plot: dict[str, np.ndarray] = {}

    for seed in seeds:
        env = Environment(ecfg["tau0"], ecfg["tau1"], t_star, ecfg["sigma"], n, seed)
        agents = _build_agents(env, ecfg, acfg)
        for name, agent in agents.items():
            r = _run_agent(env, agent, n, t_star)
            m = compute_metrics(r["errors"], t_star, horizon, r["detection_step"], band)
            d = m.as_dict()
            d["false_alarm_rate"] = r["pre_alarms"] / max(1, t_star)
            m = Metrics(**d)
            per_agent.setdefault(name, []).append(m)

            if seed == 0 and name in ("learned_full", "injected", "oracle"):
                trace_for_plot[name] = r["errors"]
            if seed == 0 and name == "learned_full":
                env2 = Environment(ecfg["tau0"], ecfg["tau1"], t_star, ecfg["sigma"], n, 0)
                a2 = LearnedAgent(prior=float(acfg["prior"]))
                r2 = _run_agent(env2, a2, n, t_star)
                replay_ok = _seed_hash(r["errors"]) == _seed_hash(r2["errors"])

            rec = {
                "run_id": f"{name}-s{seed}",
                "agent_type": name,
                "env_seed": seed,
                **prov,
                **m.as_dict(),
                "replay_hash": _seed_hash(r["errors"]),
            }
            append(ledger, rec)
            rows.append({"agent": name, "seed": seed, **m.as_dict()})

    agg = {
        k: {mk: float(np.mean([getattr(mm, mk) for mm in v])) for mk in v[0].as_dict()}
        for k, v in per_agent.items()
    }

    inj = per_agent["injected"]
    lf = per_agent["learned_full"]
    naive_keys = [k for k in per_agent if k.startswith(("moving_average", "last_interval", "exp_smoothing"))]
    wins_inj = sum(
        1 for i in range(len(seeds)) if lf[i].post_shift_mae < inj[i].post_shift_mae
    )
    wins_base = sum(
        1
        for i in range(len(seeds))
        if lf[i].post_shift_mae < min(per_agent[k][i].post_shift_mae for k in naive_keys)
    )
    wr_inj = wins_inj / len(seeds)
    wr_base = wins_base / len(seeds)

    ablation_ok = (
        agg["learned_full"]["post_shift_mae"] < agg["learned_no_update"]["post_shift_mae"]
        and agg["learned_full"]["post_shift_mae"] < agg["learned_no_drift"]["post_shift_mae"]
        and agg["learned_full"]["area_under_post_shift_error"]
        < agg["learned_frozen_post_shift"]["area_under_post_shift_error"]
    )

    no_leakage_ok = _no_leakage_introspection()
    commit_epoch = git_commit_epoch()
    prereg_before_run = 0 < commit_epoch <= run_epoch

    gate = evaluate_gate(
        agg, prereg, wr_inj, wr_base, ablation_ok, no_leakage_ok, replay_ok, prereg_before_run
    )

    _write_csv(rows)
    _write_plots(trace_for_plot, t_star, agg)
    _write_release(gate, agg, wr_inj, wr_base, prov)
    _write_honest_failures(gate, agg, ablation_ok)

    verdict = "PASS (GREEN)" if gate.green else "FAIL (RED)"
    print(f"\n=== CTI-OS PROOF-OF-LIFE :: {verdict} ===")
    for k, v in gate.checks.items():
        print(f"  [{'OK' if v else 'XX'}] {k}")
    print(f"\nlearned post_mae={agg['learned_full']['post_shift_mae']:.4f} "
          f"injected={agg['injected']['post_shift_mae']:.4f} "
          f"oracle={agg['oracle']['post_shift_mae']:.4f}")
    print(f"win-rate vs injected={wr_inj:.2f}  vs best-naive={wr_base:.2f}")
    print(f"prereg_hash={prov['prereg_hash'][:16]}  commit={prov['git_commit'][:10]}")
    return 0 if gate.green else 1


def _no_leakage_introspection() -> bool:
    import inspect

    from ctios import agents as A

    for cls in (A.LearnedAgent, A.LastIntervalAgent, A.MovingAverageAgent, A.ExpSmoothingAgent):
        sig = set(inspect.signature(cls.__init__).parameters)
        if sig & {"tau0", "tau1", "t_star", "hidden", "schedule", "sigma"}:
            return False
    src = inspect.getsource(A.LearnedAgent)
    return "_HiddenSchedule" not in src and "tau0" not in src and "t_star" not in src


def _write_csv(rows: list[dict[str, Any]]) -> None:
    p = ROOT / "evidence" / "metrics_summary.csv"
    with p.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def _write_plots(trace: dict[str, np.ndarray], t_star: int, agg: dict) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    pd = ROOT / "plots"
    for nm, e in trace.items():
        plt.figure(figsize=(9, 3))
        plt.plot(np.abs(e), lw=0.7)
        plt.axvline(t_star, color="r", ls="--", label="T*")
        plt.title(f"|prediction error| — {nm}")
        plt.xlabel("step")
        plt.legend()
        plt.tight_layout()
        plt.savefig(pd / f"error_{nm}.png", dpi=110)
        plt.close()

    names = [k for k in agg if k in ("learned_full", "injected", "oracle", "last_interval")]
    plt.figure(figsize=(7, 4))
    plt.bar(names, [agg[k]["post_shift_mae"] for k in names])
    plt.ylabel("post-shift MAE (mean over seeds)")
    plt.title("learned vs injected vs baseline vs oracle")
    plt.tight_layout()
    plt.savefig(pd / "post_shift_mae_compare.png", dpi=110)
    plt.close()


def _write_release(gate, agg, wr_inj, wr_base, prov) -> None:
    p = ROOT / "evidence" / "release_gate.md"
    lines = [
        "# CTI-OS Proof-of-Life — Release Gate",
        "",
        f"**Verdict: {'GREEN / PASS' if gate.green else 'RED / FAIL'}**",
        "",
        f"- prereg_hash: `{prov['prereg_hash']}`",
        f"- git_commit: `{prov['git_commit']}`",
        f"- config_source_hash: `{prov['config_source_hash']}`",
        f"- win-rate learned>injected: {wr_inj:.2f}",
        f"- win-rate learned>best-naive: {wr_base:.2f}",
        "",
        "## Checks",
    ]
    lines += [f"- [{'x' if v else ' '}] {k}" for k, v in gate.checks.items()]
    if gate.reasons:
        lines += ["", "## Failure reasons", *[f"- {r}" for r in gate.reasons]]
    lines += ["", "## Aggregate metrics", "```", jdump(agg), "```"]
    p.write_text("\n".join(lines))


def _write_honest_failures(gate, agg, ablation_ok) -> None:
    p = ROOT / "evidence" / "honest_failures.md"
    out = ["# Honest failures register — CTI-OS proof-of-life", ""]
    if gate.green:
        out += [
            "Run is GREEN. Acknowledged residual limitations (not papered over):",
            "",
            "- Single synthetic environment family (step change in a Gaussian "
            "interval). Generality across regime shapes is untested → next lineage.",
            "- `last_interval` adapts instantly but is noise-dominated; learned wins "
            "on variance, not on adaptation latency alone — claim scoped accordingly.",
            f"- Oracle gap remains (learned post_mae={agg['learned_full']['post_shift_mae']:.3f} "
            f"vs oracle={agg['oracle']['post_shift_mae']:.3f}): regret > 0, not solved.",
        ]
    else:
        out += ["Run is RED. Failing checks recorded verbatim, no tuning applied:", ""]
        out += [f"- {r}" for r in gate.reasons]
    if not ablation_ok:
        out += ["", "- Ablation necessity NOT shown: error-update/drift may be inert."]
    p.write_text("\n".join(out))


if __name__ == "__main__":
    raise SystemExit(main())
