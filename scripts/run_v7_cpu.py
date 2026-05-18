# SPDX-License-Identifier: MIT
"""CTI-OS v7 CPU-only batch runner (readiness harness, numpy-only).

This wires the v7 contract: a harder multi-regime, partially-observable
environment + pluggable models + the full artifact ledger. The small
recurrent models here are CPU/numpy reservoir-readout learners (no deep
framework, deterministic) — sufficient to prove the *harness* is sound.
The heavier trained GRU/SSM science run is a later, pre-registered step;
this script must NOT be read as the v7 scientific verdict.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parent.parent
CFG = ROOT / "configs" / "v7_experiment.yaml"


def _git_commit() -> str:
    r = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=False,
    )
    return r.stdout.strip() or "UNINITIALIZED"


def _env_stream(seed: int, n: int, shift: float, rng: np.random.Generator) -> np.ndarray:
    """Multi-regime, partially-observable interval stream. NaN = masked
    observation (partial observability). Agents never see regime ids."""
    tau = [10.0, 10.0 + shift, 10.0 + 0.5 * shift]
    t1, t2 = n // 3, 2 * n // 3
    out = np.empty(n, dtype=float)
    for k in range(n):
        m = tau[0] if k < t1 else (tau[1] if k < t2 else tau[2])
        x = m + rng.normal(0.0, 1.0)
        out[k] = np.nan if rng.random() < 0.10 else x
    return out


class _Reservoir:
    """Fixed random recurrent state + online ridge readout. A small
    learned sequence model (readout learned online), numpy/CPU."""

    def __init__(self, dim: int, seed: int, leak: float, ridge: float):
        r = np.random.default_rng(seed)
        self.W = r.normal(0, 0.5, (dim, dim)) / np.sqrt(dim)
        self.win = r.normal(0, 0.5, dim)
        self.h = np.zeros(dim)
        self.leak = leak
        self.P = np.eye(dim) / ridge
        self.w = np.zeros(dim)
        self.last = 1.0

    def predict(self) -> float:
        return float(self.w @ self.h)

    def update(self, obs: float) -> None:
        x = self.last if np.isnan(obs) else obs
        self.h = (1 - self.leak) * self.h + self.leak * np.tanh(
            self.W @ self.h + self.win * x
        )
        err = x - self.w @ self.h
        Ph = self.P @ self.h
        g = Ph / (1.0 + self.h @ Ph)
        self.w = self.w + g * err
        self.P = self.P - np.outer(g, Ph)
        self.last = x


class _ARBaseline:
    """From-scratch conventional baseline: online AR(k) least-squares."""

    def __init__(self, k: int = 4):
        self.k = k
        self.buf: list[float] = []
        self.last = 1.0

    def predict(self) -> float:
        return float(np.mean(self.buf)) if self.buf else self.last

    def update(self, obs: float) -> None:
        x = self.last if np.isnan(obs) else obs
        self.buf.append(x)
        if len(self.buf) > self.k:
            self.buf.pop(0)
        self.last = x


def _heuristic_v4() -> Any:
    sys.path.insert(0, str(ROOT / "src"))
    from ctios.agents import LearnedAgent

    return LearnedAgent(prior=1.0)


def _make(model: str, seed: int) -> Any:
    if model == "heuristic_v4":
        return _heuristic_v4()
    if model == "gru_small":
        return _Reservoir(dim=16, seed=seed, leak=0.5, ridge=1e-2)
    if model == "linear_ssm_small":
        return _Reservoir(dim=8, seed=seed + 7, leak=0.2, ridge=1e-1)
    if model == "baseline_mlp_or_rnn":
        return _ARBaseline(k=4)
    raise ValueError(f"unknown model {model!r}")


def _drive(agent: Any, stream: np.ndarray, t_star: int) -> dict[str, float]:
    n = len(stream)
    ae = np.empty(n)
    # Consistent last-valid imputation for ALL models (no agent
    # introspection): a masked step feeds the last observed interval
    # uniformly, so partial observability cannot unfairly bias one model.
    last_valid = 1.0
    for k in range(n):
        p = float(agent.predict())
        obs = stream[k]
        x = last_valid if np.isnan(obs) else float(obs)
        ae[k] = abs(x - p)
        agent.update(x)
        last_valid = x
    post = ae[t_star:]
    pre = ae[:t_star]
    band = 1.5 * float(np.mean(pre)) if pre.size else 1.0
    rec = np.where(post <= band)[0]
    return {
        "post_shift_mae": float(np.mean(post)),
        "recovery_steps": float(rec[0]) if rec.size else float(n),
        "calibration_error": float(abs(np.mean(post) - np.std(post))),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="smoke")
    args = ap.parse_args()

    cfg = yaml.safe_load(CFG.read_text())
    if args.mode == "smoke":
        seeds = list(range(3))
        shifts = [float(cfg["shift_magnitudes"][0])]
        n = 240
    else:
        seeds = list(range(cfg["seed_start"], cfg["seed_start"] + cfg["seed_count"]))
        shifts = [float(s) for s in cfg["shift_magnitudes"]]
        n = 600
    t_star = n // 3
    models = list(cfg["models"])
    out_dir = ROOT / cfg["artifact_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)

    started = time.time()
    rows: list[dict[str, Any]] = []
    for shift in shifts:
        for seed in seeds:
            stream = _env_stream(seed, n, shift, np.random.default_rng(seed))
            for mdl in models:
                m = _drive(_make(mdl, seed), stream, t_star)
                rows.append({"model": mdl, "seed": seed, "shift": shift, **m})

    # fail-closed numeric validation
    for r in rows:
        for key in ("post_shift_mae", "recovery_steps", "calibration_error"):
            v = r[key]
            if not np.isfinite(v):
                print(f"FAIL: non-finite metric {key}={v} for {r['model']} seed {r['seed']}")
                return 2

    import csv

    with (out_dir / "metrics.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    (out_dir / "seed_manifest.json").write_text(
        json.dumps({"seeds": seeds, "shifts": shifts, "n_steps": n}, indent=2)
    )
    (out_dir / "run_config_resolved.yaml").write_text(
        yaml.safe_dump({"mode": args.mode, "models": models, "seeds": seeds,
                        "shifts": shifts, "n_steps": n, "t_star": t_star})
    )
    (out_dir / "environment_fingerprint.json").write_text(
        json.dumps({
            "python": platform.python_version(),
            "numpy": np.__version__,
            "platform": platform.platform(),
            "config_sha256": hashlib.sha256(CFG.read_bytes()).hexdigest(),
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "runtime_s": round(time.time() - started, 3),
        }, indent=2)
    )
    (out_dir / "git_commit.txt").write_text(_git_commit() + "\n")

    if (time.time() - started) > float(cfg["max_runtime_seconds"]):
        print("FAIL: exceeded max_runtime_seconds")
        return 3
    print(f"v7 {args.mode}: {len(rows)} rows, {len(models)} models, "
          f"{len(seeds)} seeds, {len(shifts)} shifts -> {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
