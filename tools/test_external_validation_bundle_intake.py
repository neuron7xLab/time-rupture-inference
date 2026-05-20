# SPDX-License-Identifier: MIT
"""Manual self-test for the external validation bundle intake helper.

This file intentionally lives under tools/, not tests/, because adding it to the
canonical pytest suite changes the README-enforced total test count. Run it with:

    python tools/test_external_validation_bundle_intake.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "validate_external_validation_bundle.py"
H = "a" * 64


def _head_commit() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "--short=12", "HEAD"],
        cwd=ROOT,
        text=True,
    ).strip()


def _bundle(tmp_path: Path, **overrides) -> Path:
    obj = {
        "reviewer_id": "external-team",
        "reviewer_pubkey_sha256": H,
        "timestamp_utc": "2026-05-20T00:00:00Z",
        "repo_commit": _head_commit(),
        "spec_sha256": H,
        "verdict_sha256": H,
        "no_leakage_attestation": True,
        "command_transcript_sha256": H,
        "environment": {"os": "Ubuntu 24.04", "python": "3.12.3"},
        "commands_run": ["pytest tests -q"],
        "observed_metrics": {
            "learned_post_mae": 0.8830,
            "injected_post_mae": 8.0028,
            "oracle_post_mae": 0.7933,
            "causal_gain": 0.8680,
            "causal_null_gap": 0.0,
        },
    }
    obj.update(overrides)
    p = tmp_path / "bundle.json"
    p.write_text(json.dumps(obj), encoding="utf-8")
    return p


def _run(path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(path), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)

        r = _run(_bundle(tmp))
        _assert(r.returncode == 0 and "intake-valid" in r.stdout, "valid candidate failed")

        r = _run(ROOT / "templates" / "EXTERNAL_VALIDATION_BUNDLE.example.json")
        _assert(r.returncode == 1 and "example bundle is not evidence" in r.stderr, "example-as-evidence accepted")

        r = _run(ROOT / "templates" / "EXTERNAL_VALIDATION_BUNDLE.example.json", "--allow-example")
        _assert(r.returncode == 0 and "intake-valid" in r.stdout, "template maintenance mode failed")

        r = _run(_bundle(tmp, reviewer_id="neuron7xLab"))
        _assert(r.returncode == 1 and "repository author" in r.stderr, "self-run accepted")

        r = _run(_bundle(tmp, environment={"os": "Ubuntu"}))
        _assert(r.returncode == 1 and "environment.python" in r.stderr, "missing python accepted")

        r = _run(_bundle(tmp, commands_run=[]))
        _assert(r.returncode == 1 and "commands_run" in r.stderr, "missing commands accepted")

        r = _run(
            _bundle(
                tmp,
                observed_metrics={
                    "learned_post_mae": 99.0,
                    "injected_post_mae": 8.0028,
                    "oracle_post_mae": 0.7933,
                    "causal_gain": 0.8680,
                    "causal_null_gap": 0.0,
                },
            )
        )
        _assert(r.returncode == 1 and "learned_post_mae drift" in r.stderr, "metric drift accepted")

        r = _run(_bundle(tmp, repo_commit="not-a-sha"))
        _assert(r.returncode == 1 and "repo_commit" in r.stderr, "bad commit format accepted")

        r = _run(_bundle(tmp, repo_commit="deadbee"))
        _assert(r.returncode == 1 and "does not resolve" in r.stderr, "non-existent commit accepted")

        r = _run(_bundle(tmp, timestamp_utc="Z"))
        _assert(r.returncode == 1 and "ISO-8601 UTC" in r.stderr, "malformed timestamp accepted")

        r = _run(_bundle(tmp, timestamp_utc="2026-05-20T00:00:00+00:00"))
        _assert(r.returncode == 1 and "ISO-8601 UTC" in r.stderr, "non-Z timestamp accepted")

        r = _run(_bundle(tmp, no_leakage_attestation="true"))
        _assert(r.returncode == 1 and "no_leakage_attestation" in r.stderr, "string leakage flag accepted")

    print("PASS: external validation bundle intake helper self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
