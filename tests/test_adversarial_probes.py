# SPDX-License-Identifier: MIT
"""WP3 — every degenerate probe is caught; none reaches a clean PASS;
the minimal valid probe still passes."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.adversarial_probes import (  # noqa: E402
    MinimalValidProbe,
    all_adversarial_probes,
)
from ctios.falsifier_stress import _evaluate, _spec, run_stress  # noqa: E402
from ctios.redacted_io import spec_sha256  # noqa: E402


def test_every_adversarial_probe_is_caught_and_none_passes():
    spec = _spec()
    sha = spec_sha256(spec)
    for p in all_adversarial_probes():
        row = _evaluate(p, spec, sha)
        assert row["final_status"] != "PASS", (
            f"{p.name} reached a clean PASS — battery escape"
        )
        assert row["final_status"] == "INADMISSIBLE", (
            f"{p.name} expected INADMISSIBLE, got {row['final_status']} "
            f"({row['reasons']})"
        )
        assert row["reasons"], f"{p.name} caught without a recorded reason"


def test_expected_status_matches_observed():
    spec = _spec()
    sha = spec_sha256(spec)
    for p in all_adversarial_probes():
        row = _evaluate(p, spec, sha)
        assert row["expected"] == row["final_status"], (
            f"{p.name}: declared {row['expected']} but observed "
            f"{row['final_status']} — honesty invariant broken"
        )


def test_minimal_valid_probe_is_data_sensitive_and_passes_control():
    payload = run_stress()
    mv = payload["minimal_valid_probe"]
    assert mv["passes_control"] is True
    assert mv["family_metric_std"] > 1e-9
    assert isinstance(MinimalValidProbe().evaluate([1.0, 2.0, 3.0, 4.0],
                                                   {"k": 1.0}), dict)


def test_stress_is_fail_closed_and_deterministic():
    a = run_stress()
    b = run_stress()
    assert a["ok"] is True
    assert not a["fail_closed"]["adversarial_escaped_to_pass"]
    assert not a["fail_closed"]["expected_caught_but_missed"]
    assert a["artifact_sha256"] == b["artifact_sha256"]  # deterministic
