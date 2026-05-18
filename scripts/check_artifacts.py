# SPDX-License-Identifier: MIT
"""v7 artifact contract validator. PASS/FAIL, exit 1 on any violation."""

from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CFG = yaml.safe_load((ROOT / "configs" / "v7_experiment.yaml").read_text())
ART = ROOT / CFG["artifact_dir"]
REQUIRED = (
    "metrics.csv",
    "seed_manifest.json",
    "run_config_resolved.yaml",
    "environment_fingerprint.json",
    "git_commit.txt",
)
METRIC_COLS = ("post_shift_mae", "recovery_steps", "calibration_error")


def check() -> list[str]:
    p: list[str] = []
    for f in REQUIRED:
        if not (ART / f).exists():
            p.append(f"missing artifact: {f}")
    if p:
        return p

    rows = list(csv.DictReader((ART / "metrics.csv").open()))
    if not rows:
        return ["metrics.csv empty"]
    cols = set(rows[0])
    if not ({"model", "seed", "shift"} | set(METRIC_COLS)) <= cols:
        p.append(f"metrics.csv schema invalid: {sorted(cols)}")
    for r in rows:
        for c in METRIC_COLS:
            try:
                if not math.isfinite(float(r[c])):
                    p.append(f"non-finite {c} for {r.get('model')} seed {r.get('seed')}")
            except (ValueError, KeyError):
                p.append(f"bad metric cell {c}: {r}")

    man = json.loads((ART / "seed_manifest.json").read_text())
    seeds_in_csv = {int(r["seed"]) for r in rows}
    if set(man["seeds"]) != seeds_in_csv:
        p.append(f"seed manifest != csv seeds ({man['seeds']} vs {sorted(seeds_in_csv)})")

    models_in_csv = {r["model"] for r in rows}
    if models_in_csv - set(CFG["models"]):
        p.append(f"unknown models in csv: {models_in_csv - set(CFG['models'])}")
    if set(CFG["models"]) - models_in_csv:
        p.append(f"prereg models missing from csv: {set(CFG['models']) - models_in_csv}")

    commit = (ART / "git_commit.txt").read_text().strip()
    if not commit or commit == "UNINITIALIZED":
        p.append("git_commit.txt missing/uninitialized")
    fp = json.loads((ART / "environment_fingerprint.json").read_text())
    if "config_sha256" not in fp or not fp["config_sha256"]:
        p.append("environment_fingerprint missing config_sha256")
    return p


def main() -> int:
    problems = check()
    if problems:
        print("ARTIFACT CHECK — FAIL\n" + "\n".join(f"- {x}" for x in problems))
        return 1
    print(f"ARTIFACT CHECK — PASS ({ART})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
