# SPDX-License-Identifier: MIT
"""Loader, validator, deterministic hash."""

import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.redacted_io import (  # noqa: E402
    load_redacted_spec,
    spec_sha256,
    validate_redacted_spec,
)

EXAMPLE = ROOT / "examples" / "indi_redacted_cognitive_time.yaml"


def test_bundled_example_loads_and_hashes():
    s = load_redacted_spec(EXAMPLE)
    assert s.hypothesis_id == "indi_redacted_cognitive_time_demo"
    assert len(s.falsifiers) == 2
    assert spec_sha256(s) == spec_sha256(s)  # deterministic
    assert len(spec_sha256(s)) == 64


def _write(tmp_path: Path, d: dict) -> Path:
    p = tmp_path / "s.yaml"
    p.write_text(yaml.safe_dump(d))
    return p


def _base() -> dict:
    return {
        "hypothesis_id": "h",
        "claim": "c",
        "null": "n",
        "assumptions": ["a1", "a2"],
        "variables": [{"name": "m", "role": "measured"},
                      {"name": "c", "role": "control"}],
        "falsifiers": [
            {"metric": "m", "op": "<=", "threshold_key": "k", "threshold": 1.0}
        ],
        "forbidden_inferences": ["no agi"],
        "evidence_requirements": ["sealed"],
    }


def test_forbidden_private_fields_fail_load(tmp_path):
    d = _base()
    d["private_mechanism"] = "secret"
    with pytest.raises(ValueError, match="forbidden private field"):
        load_redacted_spec(_write(tmp_path, d))


def test_missing_falsifier_fails_load(tmp_path):
    d = _base()
    d["falsifiers"] = []
    with pytest.raises(ValueError):
        load_redacted_spec(_write(tmp_path, d))


def test_hash_changes_on_falsifier_change(tmp_path):
    a = load_redacted_spec(_write(tmp_path, _base()))
    d = _base()
    d["falsifiers"][0]["metric"] = "other"
    b = load_redacted_spec(_write(tmp_path, d))
    assert spec_sha256(a) != spec_sha256(b)


def test_hash_changes_on_threshold_change(tmp_path):
    a = load_redacted_spec(_write(tmp_path, _base()))
    d = _base()
    d["falsifiers"][0]["threshold"] = 2.0
    b = load_redacted_spec(_write(tmp_path, d))
    assert spec_sha256(a) != spec_sha256(b)


def test_reviewer_notes_excluded_from_hash_unless_optin(tmp_path):
    d = _base()
    d["reviewer_notes"] = "private"
    s = load_redacted_spec(_write(tmp_path, d))
    d2 = _base()
    d2["reviewer_notes"] = "different"
    s2 = load_redacted_spec(_write(tmp_path, d2))
    assert spec_sha256(s) == spec_sha256(s2)
    assert spec_sha256(s, include_notes=True) != spec_sha256(
        s2, include_notes=True
    )


def test_validate_flags_thin_assumptions(tmp_path):
    d = _base()
    d["assumptions"] = ["only-one"]
    s = load_redacted_spec(_write(tmp_path, d))
    codes = {i.code for i in validate_redacted_spec(s)}
    assert "thin_assumptions" in codes
