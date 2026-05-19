# SPDX-License-Identifier: MIT
"""PR K — workflow trust audit catches tag-substitution & permission
creep. Pure check_workflow() is unit-tested with negative cases; the
live repo must pass the real audit."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_workflow_trust as awt  # noqa: E402

REC = {"actions/checkout", "actions/setup-python", "actions/upload-artifact"}
SHA = "a" * 40
GOOD = (
    "permissions:\n  contents: read\njobs:\n  j:\n    steps:\n"
    f"      - uses: actions/checkout@{SHA} # v4\n"
)


def test_live_repo_passes_real_audit():
    assert awt.audit() == []


def test_good_workflow_passes():
    assert awt.check_workflow("ci.yml", GOOD, REC) == []


def test_tag_only_action_fails():
    bad = GOOD.replace(f"@{SHA} # v4", "@v4")
    p = awt.check_workflow("ci.yml", bad, REC)
    assert any("40-hex commit SHA" in x for x in p)


def test_sha_without_version_comment_fails():
    bad = GOOD.replace(f"@{SHA} # v4", f"@{SHA}")
    p = awt.check_workflow("ci.yml", bad, REC)
    assert any("lacks a version comment" in x for x in p)


def test_missing_permissions_fails():
    bad = GOOD.replace("permissions:\n  contents: read\n", "")
    p = awt.check_workflow("ci.yml", bad, REC)
    assert any("no explicit top-level permissions" in x for x in p)


def test_write_all_fails():
    bad = GOOD.replace("permissions:\n  contents: read",
                       "permissions: write-all")
    p = awt.check_workflow("ci.yml", bad, REC)
    assert any("write-all forbidden" in x for x in p)


def test_non_release_write_unjustified_fails():
    bad = GOOD.replace("  contents: read", "  contents: write")
    p = awt.check_workflow("ci.yml", bad, REC, contract="")
    assert any("unjustified write permission" in x for x in p)


def test_non_release_write_justified_passes():
    bad = GOOD.replace("  contents: read", "  contents: write")
    ok = awt.check_workflow(
        "ci.yml", bad, REC, contract="ci.yml:contents:write justified")
    assert not any("unjustified write" in x for x in ok)


def test_release_workflow_write_allowed():
    rel = GOOD.replace("  contents: read",
                       "  contents: write\n  id-token: write")
    p = awt.check_workflow("release.yml", rel, REC)
    assert not any("unjustified write" in x for x in p)


def test_unrecorded_action_fails():
    p = awt.check_workflow(
        "ci.yml",
        GOOD.replace("actions/checkout", "evil/action"), REC)
    assert any("not recorded in ACTION_SHA_RESOLUTION" in x for x in p)
