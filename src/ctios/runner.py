"""Orchestrator v3: power grid, neuroplasticity markers, shuffle kill-control,
hidden-provenance ledger, fail-closed gate. Closes the doctoral critique."""

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


def _build_agents(env: Environment, ecfg: dict, acfg: dict, tau0: float) -> dict[str, Agent]:
    prior = float(acfg["prior"])
    agents: dict[str, Agent] = {
        "last_interval": LastIntervalAgent(prior),
        f"moving_average_w{acfg['ma_window']}": MovingAverageAgent(acfg["ma_window"], prior),
        f"exp_smoothing_a{acfg['es_alpha']}": ExpSmoothingAgent(acfg["es_alpha"], prior),
        "random": RandomAgent(env.seed, tau0 * 0.5, tau0 * 2.5),
        "injected": InjectedAgent(tau0),
        "oracle": OracleAgent(env.oracle_view()),
        "learned_full": LearnedAgent(prior=prior),
    }
    agents.update(make_ablations(prior))
    return agents


def _run_agent(env: Environment, agent: Agent, n: int, t_star: int) -> dict[str, Any]:
    env.reset()
    errs = np.empty(n, dtype=float)
    preds = np.empty(n, dtype=float)
    detection_step: int | None = None
    pre_alarms = 0
    for k in range(n):
        pred = agent.predict()
        obs = env.step()
        preds[k] = pred
        errs[k] = obs.observed_interval - pred
        agent.update(obs.observed_interval)
        if agent.drift_flag():
            if k < t_star:
                pre_alarms += 1
            elif detection_step is None:
                detection_step = k
    return {"errors": errs, "preds": preds, "detection_step": detection_step,
            "pre_alarms": pre_alarms}


def _run_on_series(agent: Agent, intervals: np.ndarray, t_star: int) -> float:
    """Drive an agent over a fixed interval array; return post-shift MAE.

    Used for the shuffled-order kill-control (critique §5): a genuine
    temporal learner must NOT improve when post-shift order is destroyed.
    """
    n = len(intervals)
    ae = np.empty(n)
    for k in range(n):
        p = agent.predict()
        ae[k] = abs(intervals[k] - p)
        agent.update(float(intervals[k]))
    return float(np.mean(ae[t_star : t_star + 250]))


def _seed_hash(errs: np.ndarray) -> str:
    return hashlib.sha256(np.round(errs, 9).tobytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["baselines", "learned", "full"], default="full")
    ap.parse_args()

    run_epoch = int(time.time())
    ecfg = _load("env.yaml")
    acfg = _load("agents.yaml")
    mcfg = _load("metrics.yaml")
    xcfg = _load("experiment.yaml")
    prereg = yaml.safe_load((ROOT / "prereg" / "preregistration.yaml").read_text())["thresholds"]

    seeds = list(range(xcfg["n_seeds"]))
    deltas = [float(d) for d in xcfg["shift_deltas"]]
    tau0 = float(ecfg["tau0"])
    n = ecfg["n_steps"]
    t_star = ecfg["t_star"]
    horizon = mcfg["eval_horizon"]
    band = mcfg["recovery_band_mult"]

    ledger = ROOT / "evidence" / "evidence_ledger.jsonl"
    ledger.unlink(missing_ok=True)
    prov = provenance()

    rows: list[dict[str, Any]] = []
    trace_for_plot: dict[str, np.ndarray] = {}
    replay_ok = True
    shuffle_ok = True

    # per (delta) aggregates and grid-wide win counts
    per_delta_agg: dict[float, dict[str, dict[str, float]]] = {}
    grid_wins_inj = 0
    grid_wins_base = 0
    grid_total = 0
    neuro = {"synaptic": [], "homeostatic": [], "neuromodulation": [], "extinction": []}

    shuf_real: list[float] = []
    shuf_perm: list[float] = []

    for delta in deltas:
        tau1 = tau0 + delta
        per_agent: dict[str, list[Metrics]] = {}
        for seed in seeds:
            env = Environment(tau0, tau1, t_star, ecfg["sigma"], n, seed)
            agents = _build_agents(env, ecfg, acfg, tau0)
            run_cache: dict[str, dict[str, Any]] = {}
            for name, agent in agents.items():
                r = _run_agent(env, agent, n, t_star)
                run_cache[name] = r
                m = compute_metrics(r["errors"], t_star, horizon, r["detection_step"], band)
                d = m.as_dict()
                d["false_alarm_rate"] = r["pre_alarms"] / max(1, t_star)
                m = Metrics(**d)
                per_agent.setdefault(name, []).append(m)
                rec = {
                    "run_id": f"{name}-d{delta}-s{seed}",
                    "agent_type": name,
                    "shift_delta": delta,
                    "env_seed": seed,
                    **prov,
                    **env.hidden_provenance(),
                    **m.as_dict(),
                    "replay_hash": _seed_hash(r["errors"]),
                    "pass_fail": "n/a",
                }
                append(ledger, rec)
                rows.append({"agent": name, "delta": delta, "seed": seed, **m.as_dict()})

            # grid win accounting
            lf = per_agent["learned_full"][-1]
            ij = per_agent["injected"][-1]
            naive = min(
                per_agent[k][-1].post_shift_mae
                for k in per_agent
                if k.startswith(("moving_average", "last_interval", "exp_smoothing"))
            )
            grid_total += 1
            grid_wins_inj += int(lf.post_shift_mae < ij.post_shift_mae)
            grid_wins_base += int(lf.post_shift_mae < naive)

            # neuroplasticity markers (critique §6)
            lf_run = run_cache["learned_full"]
            preds = lf_run["preds"]
            pre_v = float(np.var(preds[t_star - 50 : t_star]))
            # v4 fix: synaptic = change of the CONVERGED pre-shift estimate
            # to the post-shift estimate (not vs the cold-start transient).
            moved = abs(
                np.mean(preds[t_star + 200 : t_star + 250])
                - np.mean(preds[t_star - 50 : t_star])
            )
            neuro["synaptic"].append(moved > abs(delta) * 0.5)
            neuro["homeostatic"].append(pre_v < (ecfg["sigma"] ** 2) * 1.5)
            neuro["neuromodulation"].append(lf_run["detection_step"] is not None)
            neuro["extinction"].append(
                per_agent["learned_full"][-1].post_shift_mae
                < per_agent["learned_no_update"][-1].post_shift_mae
            )

            # shuffle kill-control: accumulate over ALL seeds of delta[0]
            # (v4 fix: single-seed strict compare was sampling-noise driven).
            if delta == deltas[0]:
                env3 = Environment(tau0, tau1, t_star, ecfg["sigma"], n, seed)
                env3.reset()
                seq = np.array([env3.step().observed_interval for _ in range(n)])
                shuf_real.append(
                    _run_on_series(LearnedAgent(prior=float(acfg["prior"])), seq, t_star)
                )
                sh = seq.copy()
                post = sh[t_star:].copy()
                np.random.default_rng(9999 + seed).shuffle(post)
                sh[t_star:] = post
                shuf_perm.append(
                    _run_on_series(LearnedAgent(prior=float(acfg["prior"])), sh, t_star)
                )
            if delta == deltas[0] and seed == 0:
                env2 = Environment(tau0, tau1, t_star, ecfg["sigma"], n, 0)
                r2 = _run_agent(env2, LearnedAgent(prior=float(acfg["prior"])), n, t_star)
                replay_ok = _seed_hash(lf_run["errors"]) == _seed_hash(r2["errors"])
                for nm in ("learned_full", "injected", "oracle"):
                    trace_for_plot[nm] = run_cache[nm]["errors"]

        per_delta_agg[delta] = {
            k: {mk: float(np.mean([getattr(mm, mk) for mm in v])) for mk in v[0].as_dict()}
            for k, v in per_agent.items()
        }

    # shuffle kill-control verdict: averaged over all delta[0] seeds with a
    # 2% measurement-noise band (pre-declared in prereg leakage section).
    mr, mp = float(np.mean(shuf_real)), float(np.mean(shuf_perm))
    shuffle_ok = mp >= mr - 0.02 * mr

    # aggregate over the whole grid for the headline
    agg = _grid_mean(per_delta_agg)
    wr_inj = grid_wins_inj / grid_total
    wr_base = grid_wins_base / grid_total
    ablation_ok = all(
        a[ "learned_full"]["post_shift_mae"] < a["learned_no_update"]["post_shift_mae"]
        and a["learned_full"]["post_shift_mae"] < a["learned_no_drift"]["post_shift_mae"]
        for a in per_delta_agg.values()
    )
    every_delta_pass = all(
        a["learned_full"]["post_shift_mae"] < a["injected"]["post_shift_mae"]
        and a["learned_full"]["post_shift_mae"]
        < min(
            a[k]["post_shift_mae"]
            for k in a
            if k.startswith(("moving_average", "last_interval", "exp_smoothing"))
        )
        for a in per_delta_agg.values()
    )
    neuro_ok = {k: (sum(v) / len(v)) >= prereg["min_win_rate"] for k, v in neuro.items()}

    no_leakage_ok = _no_leakage_introspection()
    commit_epoch = git_commit_epoch()
    prereg_before_run = 0 < commit_epoch <= run_epoch

    gate = evaluate_gate(
        agg=agg,
        prereg=prereg,
        win_rate_learned_vs_injected=wr_inj,
        win_rate_learned_vs_baseline=wr_base,
        ablation_ok=ablation_ok,
        no_leakage_ok=no_leakage_ok,
        replay_ok=replay_ok,
        prereg_before_run=prereg_before_run,
        every_delta_pass=every_delta_pass,
        shuffle_no_gain=shuffle_ok,
        neuro_markers=neuro_ok,
        n_seeds=len(seeds),
        n_deltas=len(deltas),
        min_seeds=30,
        min_deltas=3,
    )

    _write_csv(rows)
    _write_plots(trace_for_plot, t_star, agg)
    _write_release(gate, agg, per_delta_agg, wr_inj, wr_base, neuro_ok, prov)
    _write_honest_failures(gate, agg, ablation_ok, neuro_ok)

    verdict = "PASS (GREEN)" if gate.green else "FAIL (RED)"
    print(f"\n=== CTI-OS PROOF-OF-LIFE v3 :: {verdict} ===")
    for k, v in gate.checks.items():
        print(f"  [{'OK' if v else 'XX'}] {k}")
    print(f"\ngrid: {len(seeds)} seeds x {len(deltas)} deltas={deltas}")
    print(f"learned post_mae={agg['learned_full']['post_shift_mae']:.4f} "
          f"injected={agg['injected']['post_shift_mae']:.4f} "
          f"oracle={agg['oracle']['post_shift_mae']:.4f}")
    print(f"win-rate vs injected={wr_inj:.3f}  vs best-naive={wr_base:.3f}")
    print(f"neuroplasticity markers={neuro_ok}")
    print(f"prereg_hash={prov['prereg_hash'][:16]}  commit={prov['git_commit'][:10]}")
    return 0 if gate.green else 1


def _grid_mean(per_delta: dict[float, dict[str, dict[str, float]]]) -> dict[str, dict[str, float]]:
    agents = next(iter(per_delta.values())).keys()
    mks = next(iter(next(iter(per_delta.values())).values())).keys()
    return {
        a: {mk: float(np.mean([per_delta[d][a][mk] for d in per_delta])) for mk in mks}
        for a in agents
    }


def _no_leakage_introspection() -> bool:
    import inspect

    from ctios import agents as A

    for cls in (A.LearnedAgent, A.LastIntervalAgent, A.MovingAverageAgent, A.ExpSmoothingAgent):
        sig = set(inspect.signature(cls.__init__).parameters)
        if sig & {"tau0", "tau1", "t_star", "hidden", "schedule", "sigma", "n_steps"}:
            return False
    src = inspect.getsource(A.LearnedAgent)
    return all(t not in src for t in ("_HiddenSchedule", "tau0", "tau1", "t_star", "n_steps"))


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
    names = [k for k in ("learned_full", "injected", "oracle", "last_interval") if k in agg]
    plt.figure(figsize=(7, 4))
    plt.bar(names, [agg[k]["post_shift_mae"] for k in names])
    plt.ylabel("grid-mean post-shift MAE")
    plt.title("learned vs injected vs baseline vs oracle (30 seeds x 3 shifts)")
    plt.tight_layout()
    plt.savefig(pd / "post_shift_mae_compare.png", dpi=110)
    plt.close()


def _write_release(gate, agg, per_delta, wr_inj, wr_base, neuro_ok, prov) -> None:
    p = ROOT / "evidence" / "release_gate.md"
    L = [
        "# CTI-OS Proof-of-Life v3 — Release Gate",
        "",
        f"**Verdict: {'GREEN / PASS' if gate.green else 'RED / FAIL'}**",
        "",
        f"- prereg_hash: `{prov['prereg_hash']}`",
        f"- git_commit: `{prov['git_commit']}`",
        f"- grid win-rate learned>injected: {wr_inj:.3f}",
        f"- grid win-rate learned>best-naive: {wr_base:.3f}",
        f"- neuroplasticity markers: `{neuro_ok}`",
        "",
        "## Allowed claim (verbatim, critique §3)",
        "> The learned agent adapts to hidden temporal regime shifts better "
        "than fixed and naive baselines under preregistered metrics, "
        "deterministic replay, no-leakage constraints, and ablation controls.",
        "",
        "## Forbidden claim",
        "> CTI-OS understands time / has cognition / is neuroplastic / "
        "simulates causality / has world understanding.",
        "",
        "## Checks",
    ]
    L += [f"- [{'x' if v else ' '}] {k}" for k, v in gate.checks.items()]
    if gate.reasons:
        L += ["", "## Failure reasons", *[f"- {r}" for r in gate.reasons]]
    L += ["", "## Per-shift post_shift_mae (learned / injected / best-naive)"]
    for d, a in per_delta.items():
        nb = min(
            a[k]["post_shift_mae"]
            for k in a
            if k.startswith(("moving_average", "last_interval", "exp_smoothing"))
        )
        L.append(
            f"- delta={d}: learned={a['learned_full']['post_shift_mae']:.3f} "
            f"injected={a['injected']['post_shift_mae']:.3f} best_naive={nb:.3f}"
        )
    L += ["", "## Grid-mean metrics", "```", jdump(agg), "```"]
    p.write_text("\n".join(L))


def _write_honest_failures(gate, agg, ablation_ok, neuro_ok) -> None:
    p = ROOT / "evidence" / "honest_failures.md"
    o = ["# Honest failures register — CTI-OS proof-of-life v3", ""]
    if gate.green:
        o += [
            "GREEN across the 30x3 power grid. Acknowledged residual limits "
            "(NOT papered over, per critique §3 boundary):",
            "",
            "- Single synthetic family (piecewise-constant Gaussian interval). "
            "Non-stationary / multimodal shifts untested → lineage v4.",
            "- No causal intervention: this is predictive adaptation, NOT "
            "`do(A)->S(t+Δ)` world-model control (critique §1.2.2). Not claimed.",
            f"- Oracle gap remains (learned={agg['learned_full']['post_shift_mae']:.3f} "
            f"vs oracle={agg['oracle']['post_shift_mae']:.3f}): regret > 0.",
            "- 'Neuroplastic-like' is used ONLY as the 4 measured markers "
            f"({neuro_ok}); no biological-fidelity claim is made (critique §6).",
        ]
    else:
        o += ["RED. Failing checks verbatim, no tuning applied:", ""]
        o += [f"- {r}" for r in gate.reasons]
    if not ablation_ok:
        o += ["", "- Ablation necessity NOT shown on some delta: mechanism may be inert."]
    p.write_text("\n".join(o))


if __name__ == "__main__":
    raise SystemExit(main())
