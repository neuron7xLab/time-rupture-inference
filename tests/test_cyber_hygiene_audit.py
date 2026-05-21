from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.cyber_hygiene_contract import TARGETS_PATH
from tools.cyber_hygiene_audit import _load_bandit, _load_targets, build_report


def _base_results() -> list[dict]:
    return [
        {"test_id": "B607", "filename": "src/a.py"},
        {"test_id": "B603", "filename": "src/a.py"},
        {"test_id": "B404", "filename": "scripts/z.py"},
        {"test_id": "B101", "filename": "scripts/a.py"},
        {"test_id": "B105", "filename": "src/b.py"},
        {"test_id": "B603", "filename": "scripts/a.py"},
    ]


def test_build_report_pass_has_exactly_7_classes() -> None:
    report = build_report(_base_results())
    assert report["status"] == "PASS"
    assert report["exactly_7_classes"] == 7
    assert len(report["findings"]) == 7
    assert report["missing_required_classes"] == []


def test_build_report_fail_when_required_class_missing() -> None:
    results = [r for r in _base_results() if r["test_id"] != "B105"]
    report = build_report(results)
    assert report["status"] == "FAIL"
    assert "B105" in report["missing_required_classes"]


def test_load_bandit_contract_validation(tmp_path: Path) -> None:
    broken = tmp_path / "broken.json"
    broken.write_text(json.dumps({"results": {"x": 1}}), encoding="utf-8")
    with pytest.raises(ValueError):
        _load_bandit(broken)
    broken_top = tmp_path / "broken_top.json"
    broken_top.write_text(json.dumps([{"results": []}]), encoding="utf-8")
    with pytest.raises(ValueError):
        _load_bandit(broken_top)


def test_load_bandit_sanitization_counts_drops(tmp_path: Path) -> None:
    payload = tmp_path / "payload.json"
    payload.write_text(json.dumps({"results": [{"test_id": "B607", "filename": "src/a.py"}, {"test_id": "bad-id", "filename": "../oops.py"}]}), encoding="utf-8")
    rows, dropped = _load_bandit(payload)
    assert len(rows) == 1
    assert dropped == 1


def test_load_bandit_blocks_dotdot_path(tmp_path: Path) -> None:
    payload = tmp_path / "payload2.json"
    payload.write_text(json.dumps({"results": [{"test_id": "B607", "filename": "../scripts/evil.py"}]}), encoding="utf-8")
    rows, dropped = _load_bandit(payload)
    assert rows == []
    assert dropped == 1


def test_top_file_sorting_is_deterministic() -> None:
    report = build_report(
        [
            {"test_id": "B607", "filename": "src/z.py"},
            {"test_id": "B607", "filename": "src/a.py"},
            {"test_id": "B603", "filename": "src/a.py"},
            {"test_id": "B404", "filename": "scripts/a.py"},
            {"test_id": "B101", "filename": "scripts/a.py"},
            {"test_id": "B105", "filename": "src/a.py"},
        ]
    )
    b607 = next(x for x in report["findings"] if x["id"] == "B607")
    assert b607["top_files"][0]["file"] == "src/a.py"


def test_hotspot_path_normalization_blocks_traversal() -> None:
    report = build_report(
        [
            {"test_id": "B607", "filename": "../scripts/evil.py"},
            {"test_id": "B603", "filename": "scripts/ok.py"},
            {"test_id": "B404", "filename": "src/ok.py"},
            {"test_id": "B101", "filename": "src/ok.py"},
            {"test_id": "B105", "filename": "src/ok.py"},
        ]
    )
    scripts = next(x for x in report["findings"] if x["id"] == "SCRIPTS")
    assert scripts["count"] == 1


def test_hotspot_payload_absolute_path_handling() -> None:
    report = build_report(
        [
            {"test_id": "B603", "filename": "/src/ctios/utils.py"},
            {"test_id": "B404", "filename": "/scripts/ci_gate_watch.py"},
            {"test_id": "B101", "filename": "src/ok.py"},
            {"test_id": "B105", "filename": "scripts/ok.py"},
            {"test_id": "B607", "filename": "src/ok.py"},
        ],
        mode="must_not_exist",
    )
    src_finding = next(x for x in report["findings"] if x["id"] == "SRC")
    scripts_finding = next(x for x in report["findings"] if x["id"] == "SCRIPTS")
    assert src_finding["count"] == 3
    assert scripts_finding["count"] == 2


def test_strict_mode_fails_on_dropped_rows() -> None:
    report = build_report(_base_results(), dropped_count=2, strict=True)
    assert report["status"] == "FAIL"


def test_must_not_exist_mode_fails_when_findings_present() -> None:
    report = build_report(_base_results(), mode="must_not_exist")
    assert report["status"] == "FAIL"
    assert "B607" in report["present_disallowed_classes"]


def test_targets_loaded_from_config_contract() -> None:
    targets = _load_targets(TARGETS_PATH)
    assert len(targets) == 7


def test_targets_reject_duplicate_keys(tmp_path: Path) -> None:
    bad = tmp_path / "targets.json"
    bad.write_text(
        json.dumps(
            [
                {"key": "B607", "title": "a", "rationale": "a"},
                {"key": "B607", "title": "b", "rationale": "b"},
                {"key": "B404", "title": "c", "rationale": "c"},
                {"key": "B101", "title": "d", "rationale": "d"},
                {"key": "B105", "title": "e", "rationale": "e"},
                {"key": "SCRIPTS", "title": "f", "rationale": "f"},
                {"key": "SRC", "title": "g", "rationale": "g"},
            ]
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        _load_targets(bad)
