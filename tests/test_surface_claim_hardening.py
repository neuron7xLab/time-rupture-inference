# SPDX-License-Identifier: MIT
"""WP2 — broad unscoped claim language must not appear on the external
surface (README + release/** + docs/**). Negated / bounded / disclaimer
uses are allowed; bare promotional uses are not. This is stricter than
claims-lint and targets *inflation*, not vocabulary."""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

# Exempt: documents whose JOB is to enumerate the boundary / risks /
# negatives (same rationale as claims-lint exemptions).
_EXEMPT = (
    "docs/reports/",
    "docs/AUDIT_",
    "docs/RCA_",
    "docs/CRITIQUE_",
    "docs/INDI_LIMITATIONS.md",
    "docs/OPENAI_STYLE_REVIEW.md",
    "docs/FAILURE_TAXONOMY.md",
    "docs/CONTRIBUTION_CLAIMS.md",
    "docs/EXTERNAL_VALIDATION_PROTOCOL.md",
    "docs/CODE_QUALITY_AUDIT.md",
    "docs/FRONTIER_READINESS_REPORT.md",
    "docs/NO_AUTHOR_REQUIRED_REVIEW.md",
    "docs/prereg/",
    "CLAIM_BOUNDARY.md",
    "RESIDUAL_RISKS.md",
    "EXPECTED_OUTPUTS.md",
)

_DENY = re.compile(
    r"\b(productiz\w*|market[- ]validat\w*|market value|"
    r"commercially validated|dario|ilya|karpathy|agi-level|"
    r"frontier-lab level)\b|\bthis proves\b|\bwe prove\b",
    re.I,
)
# A line is OK if it bounds/negates the term on the same line.
_SCOPE = re.compile(
    r"\b(not|no|never|forbidden|defect|does not|do not|cannot|"
    r"scoped|bounded|synthetic|pinned|falsifier|invariant|"
    r"byte-identical|disclaimer|open)\b",
    re.I,
)
_DISC_OPEN = "<!-- claims:disclaimer -->"
_DISC_CLOSE = "<!-- claims:end -->"


def _surface() -> list[Path]:
    files = [ROOT / "README.md"]
    files += sorted((ROOT / "docs").glob("**/*.md"))
    files += sorted((ROOT / "release").glob("**/*.md"))
    out = []
    for f in files:
        rel = str(f.relative_to(ROOT))
        if any(e in rel for e in _EXEMPT):
            continue
        out.append(f)
    return out


def _violations() -> list[str]:
    bad: list[str] = []
    for f in _surface():
        in_disc = False
        for i, raw in enumerate(f.read_text().splitlines(), 1):
            if _DISC_OPEN in raw:
                in_disc = True
            if _DISC_CLOSE in raw:
                in_disc = False
                continue
            if in_disc:
                continue
            if _DENY.search(raw) and not _SCOPE.search(raw):
                bad.append(f"{f.relative_to(ROOT)}:{i}: {raw.strip()[:90]}")
    return bad


def test_no_unscoped_promotional_claims_on_surface():
    v = _violations()
    assert v == [], "unscoped claim inflation:\n" + "\n".join(v)


def test_readme_hero_lines_are_bounded():
    r = (ROOT / "README.md").read_text()
    assert "causal change of the future" not in r
    assert "A learned temporal model that survives" not in r
    # bare "proven" must not headline a section
    assert "## What is proven" not in r


def test_guard_actually_fires_on_a_planted_inflation(tmp_path):
    p = ROOT / "docs" / "_tmp_inflation.md"
    p.write_text("This is productizable and market-validated.\n")
    try:
        assert any("_tmp_inflation.md" in x for x in _violations())
    finally:
        p.unlink()
