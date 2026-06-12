"""Smoke + contract tests for the `tri-architect` CLI."""

from __future__ import annotations

import json

import pytest

from ctios import architect_cli


def test_self_mode_human_output(capsys):
    rc = architect_cli.main(["--self"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "score_class" in out
    assert "tier" in out
    assert "confidence" in out


def test_self_mode_json_is_well_formed(capsys):
    rc = architect_cli.main(["--self", "--json"])
    out = capsys.readouterr().out
    assert rc == 0
    data = json.loads(out)
    assert "scoring_model" in data
    assert "dimension_rationale" in data
    # Self-evaluation must never silently claim production without a real
    # external run — this repo records real_external_collaborator_run=false.
    assert data["scoring_model"]["score_class"] != "ELITE_VALIDATED_PRODUCTION"


def test_self_mode_confidence_capped_below_independent(capsys):
    architect_cli.main(["--self", "--json"])
    data = json.loads(capsys.readouterr().out)
    # No real external run -> tier <= REPEATED_REGRESSION -> conf <= 0.95.
    assert data["final_confidence"] <= 0.95


def test_firewall_mode_clean(tmp_path, capsys):
    f = tmp_path / "clean.txt"
    f.write_text("The agent adapts under preregistered metrics, bounded in scope.\n")
    rc = architect_cli.main(["--firewall", str(f)])
    assert rc == 0
    assert "clean" in capsys.readouterr().out


def test_firewall_mode_critical_exits_nonzero(tmp_path, capsys):
    f = tmp_path / "dirty.txt"
    f.write_text("This proves the theorem is certain.\n")
    rc = architect_cli.main(["--firewall", str(f), "--json"])
    assert rc == 1
    data = json.loads(capsys.readouterr().out)
    assert any(h["severity"] == "CRITICAL" for h in data["firewall_hits"])


def test_requires_a_mode():
    with pytest.raises(SystemExit):
        architect_cli.main([])
