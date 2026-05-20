# SPDX-License-Identifier: MIT
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def _run(*args: str):
    return subprocess.run([sys.executable, "tools/noise_audit.py", *args], cwd=ROOT, capture_output=True, text=True, check=False)


def test_noise_audit_writes_expected_shape():
    out_rel = "artifacts/noise_audit_test_output.json"
    r = _run("--output", out_rel, "--generated-at-utc", "2026-05-20")
    assert r.returncode == 0, r.stdout + r.stderr
    data = json.loads((ROOT / out_rel).read_text())
    (ROOT / out_rel).unlink()
    assert data["generated_at_utc"] == "2026-05-20"
    assert data["files_scanned"] > 0
    assert sorted(data["matches"].keys()) == ["ai_disclaimer", "brand_mentions", "pseudo_markers", "todo_markers"]


def test_noise_audit_rejects_output_escape(tmp_path: Path):
    r = _run("--output", "../escape.json")
    assert r.returncode != 0
    assert "within repository root" in (r.stdout + r.stderr)


def test_noise_audit_enforce_green_with_strict_allowlist():
    r = _run("--enforce", "--policy-file", ".auditignore.json", "--generated-at-utc", "2026-05-20")
    assert r.returncode == 0, r.stdout + r.stderr


def test_noise_audit_enforce_red_on_unauthorized_mutation():
    r = _run("--enforce", "--policy-file", "missing_policy.json", "--generated-at-utc", "2026-05-20")
    assert r.returncode == 1
    assert "NOISE AUDIT — RED" in (r.stdout + r.stderr)


def test_noise_audit_red_on_invalid_policy_schema(tmp_path: Path):
    bad = ROOT / "artifacts" / "bad_policy.json"
    bad.parent.mkdir(parents=True, exist_ok=True)
    bad.write_text('[{"path":"x"}]')
    r = _run("--policy-file", "artifacts/bad_policy.json")
    bad.unlink()
    assert r.returncode != 0
