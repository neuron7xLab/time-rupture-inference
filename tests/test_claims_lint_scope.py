# SPDX-License-Identifier: MIT
"""WP2 — the claim-boundary lint covers the extended outward-facing
surface (docs/examples/scripts/workflows), and the disclaimer escape
hatch only permits forbidden vocabulary when bounded/negated."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import claims_lint  # noqa: E402
import yaml  # noqa: E402

SPEC = yaml.safe_load((ROOT / "claims.yaml").read_text())


def test_scope_covers_outward_surfaces():
    globs = set(SPEC["scan_globs"])
    for required in (
        "docs/**/*.md",
        "examples/**/*.yaml",
        "scripts/**/*.py",
        "scripts/**/*.sh",
        ".github/workflows/**/*.yml",
    ):
        assert required in globs, f"scan scope missing {required}"


def test_repo_is_currently_clean_under_extended_scope():
    # The whole tracked corpus must pass the extended gate.
    assert claims_lint.lint() == []


def test_forbidden_wording_outside_disclaimer_fails(tmp_path, monkeypatch):
    bad = ROOT / "docs" / "_tmp_scope_violation.md"
    bad.write_text("This system has cognition and is conscious AGI.\n")
    try:
        viol = claims_lint.lint()
        assert any("_tmp_scope_violation.md" in v for v in viol), (
            "extended scope failed to catch a forbidden cognition/AGI "
            "claim in a docs/*.md file"
        )
    finally:
        bad.unlink()


def test_same_wording_inside_disclaimer_is_allowed(tmp_path):
    ok = ROOT / "docs" / "_tmp_scope_ok.md"
    ok.write_text(
        "<!-- claims:disclaimer -->\n"
        "No cognition, consciousness, or AGI is claimed here.\n"
        "<!-- claims:end -->\n"
    )
    try:
        viol = [v for v in claims_lint.lint() if "_tmp_scope_ok.md" in v]
        assert viol == [], f"disclaimer block should be exempt, got {viol}"
    finally:
        ok.unlink()


def test_negated_wording_on_same_line_is_allowed(tmp_path):
    ok = ROOT / "docs" / "_tmp_scope_neg.md"
    # 'not' is a qualifier token; a bounded negation must pass.
    ok.write_text("This is not a cognition claim and never an AGI claim.\n")
    try:
        viol = [v for v in claims_lint.lint() if "_tmp_scope_neg.md" in v]
        assert viol == [], f"negated line should pass, got {viol}"
    finally:
        ok.unlink()
