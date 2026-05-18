# SPDX-License-Identifier: MIT
"""Artifact-schema validator self-tests on synthetic fixtures."""

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_artifacts as ca  # noqa: E402

GOOD = [
    {"model": "heuristic_v4", "seed": 0, "shift": 7.0, "post_shift_mae": 0.9,
     "recovery_steps": 12.0, "calibration_error": 0.1},
    {"model": "esn_small", "seed": 0, "shift": 7.0, "post_shift_mae": 0.8,
     "recovery_steps": 10.0, "calibration_error": 0.1},
    {"model": "linear_ssm_small", "seed": 0, "shift": 7.0, "post_shift_mae": 0.8,
     "recovery_steps": 10.0, "calibration_error": 0.1},
    {"model": "ar_baseline", "seed": 0, "shift": 7.0, "post_shift_mae": 1.0,
     "recovery_steps": 14.0, "calibration_error": 0.2},
]


def _write(tmp: Path, rows: list[dict]) -> None:
    art = tmp / "art"
    art.mkdir()
    # stable superset header so a row missing a key writes blank (which
    # the validator must then reject) instead of crashing the writer.
    with (art / "metrics.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(GOOD[0]), restval="")
        w.writeheader()
        w.writerows(rows)
    (art / "seed_manifest.json").write_text(json.dumps({"seeds": [0], "shifts": [7.0]}))
    (art / "run_config_resolved.yaml").write_text("mode: smoke\n")
    (art / "environment_fingerprint.json").write_text(json.dumps({"config_sha256": "x"}))
    (art / "git_commit.txt").write_text("abc123\n")
    ca.ART = art


def test_valid_fixture_passes(tmp_path, monkeypatch):
    _write(tmp_path, [dict(r) for r in GOOD])
    monkeypatch.setattr(ca, "CFG", {"artifact_dir": "art", "models": [
        "heuristic_v4", "esn_small", "linear_ssm_small", "ar_baseline"]})
    assert ca.check() == []


def test_missing_field_fails(tmp_path, monkeypatch):
    bad = [dict(r) for r in GOOD]
    del bad[0]["post_shift_mae"]
    _write(tmp_path, bad)
    monkeypatch.setattr(ca, "CFG", {"artifact_dir": "art", "models": [
        "heuristic_v4", "esn_small", "linear_ssm_small", "ar_baseline"]})
    assert ca.check()


def test_nan_metric_fails(tmp_path, monkeypatch):
    bad = [dict(r) for r in GOOD]
    bad[1]["post_shift_mae"] = float("nan")
    _write(tmp_path, bad)
    monkeypatch.setattr(ca, "CFG", {"artifact_dir": "art", "models": [
        "heuristic_v4", "esn_small", "linear_ssm_small", "ar_baseline"]})
    assert any("non-finite" in p for p in ca.check())


def test_wrong_model_name_fails(tmp_path, monkeypatch):
    bad = [dict(r) for r in GOOD]
    bad[0]["model"] = "rogue_model"
    _write(tmp_path, bad)
    monkeypatch.setattr(ca, "CFG", {"artifact_dir": "art", "models": [
        "heuristic_v4", "esn_small", "linear_ssm_small", "ar_baseline"]})
    assert any("unknown models" in p for p in ca.check())
