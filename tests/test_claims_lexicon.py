"""Audit P1 enforced: external-facing text cannot inflate the claim.

The linter is the gate; this binds it to pytest + CI so local ≡ cloud.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import claims_lint  # noqa: E402


def test_no_claim_inflation_in_external_text():
    violations = claims_lint.lint()
    assert not violations, "claim-lexicon violations:\n" + "\n".join(violations)


def test_lint_actually_detects_a_planted_violation(tmp_path, monkeypatch):
    bad = tmp_path / "BAD.md"
    bad.write_text("This system has consciousness and is intelligent.\n")
    monkeypatch.setattr(claims_lint, "_files", lambda: [bad])
    monkeypatch.setattr(
        claims_lint, "ROOT", tmp_path
    )  # so relative_to(ROOT) resolves
    assert claims_lint.lint(), "linter must catch a planted ontological claim"
