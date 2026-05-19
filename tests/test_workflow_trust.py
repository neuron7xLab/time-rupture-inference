# SPDX-License-Identifier: MIT
"""PR K + K.1 — workflow trust audit BINDS each `uses:` ref to the
recorded resolved_sha + exact tag comment, and schema-validates the
resolution evidence. Every negative case fails closed; live repo passes.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_workflow_trust as awt  # noqa: E402

SHA = "a" * 40
REC = {
    "actions/checkout": {
        "tag": "v4", "resolved_sha": SHA,
        "source_ref": "refs/tags/v4",
        "resolved_at_utc": "2026-05-19T00:00:00Z",
    }
}
GOOD = (
    "permissions:\n  contents: read\njobs:\n  j:\n    steps:\n"
    f"      - uses: actions/checkout@{SHA} # v4\n"
)


def _res(**over):
    base = {
        "resolved_at_utc": "2026-05-19T00:00:00Z",
        "actions": [{
            "action": "actions/checkout", "tag": "v4",
            "resolved_sha": SHA, "source_ref": "refs/tags/v4",
        }],
    }
    base.update(over)
    return base


def test_live_repo_passes_real_audit():
    assert awt.audit() == []


def test_good_workflow_binds_clean():
    assert awt.check_workflow("ci.yml", GOOD, REC) == []


# the 5 required failing cases
def test_sha_mismatch_against_resolution_fails():
    p = awt.check_workflow("ci.yml", GOOD.replace(SHA, "b" * 40), REC)
    assert any("!= recorded resolved_sha" in x for x in p)


def test_wrong_version_comment_fails():
    p = awt.check_workflow("ci.yml", GOOD.replace("# v4", "# banana"), REC)
    assert any("!= exact '# v4'" in x for x in p)


def test_malformed_recorded_sha_fails():
    _, probs = awt.load_resolution(_res(actions=[{
        "action": "x/y", "tag": "v1", "resolved_sha": "NOTHEX",
        "source_ref": "refs/tags/v1",
    }]))
    assert any("not lowercase 40-hex" in p for p in probs)


def test_duplicate_action_record_fails():
    _, probs = awt.load_resolution(_res(actions=[
        {"action": "a/b", "tag": "v1", "resolved_sha": SHA,
         "source_ref": "refs/tags/v1"},
        {"action": "a/b", "tag": "v1", "resolved_sha": SHA,
         "source_ref": "refs/tags/v1"},
    ]))
    assert any("duplicate action record" in p for p in probs)


def test_source_ref_tag_mismatch_fails():
    _, probs = awt.load_resolution(_res(actions=[{
        "action": "a/b", "tag": "v4", "resolved_sha": SHA,
        "source_ref": "refs/tags/v9",
    }]))
    assert any("does not match tag" in p for p in probs)


# additional adversarial cases
def test_uppercase_sha_in_workflow_fails():
    p = awt.check_workflow("ci.yml", GOOD.replace(SHA, "A" * 40), REC)
    assert any("not pinned to a lowercase 40-hex SHA" in x for x in p)


def test_tag_only_ref_fails():
    p = awt.check_workflow("ci.yml", GOOD.replace(f"@{SHA} # v4", "@v4"), REC)
    assert any("lowercase 40-hex SHA" in x for x in p)


def test_missing_version_comment_fails():
    p = awt.check_workflow("ci.yml", GOOD.replace(" # v4", ""), REC)
    assert any("!= exact '# v4'" in x for x in p)


def test_unknown_recorded_action_is_rejected():
    p = awt.check_workflow(
        "ci.yml", GOOD.replace("actions/checkout", "evil/action"), REC)
    assert any("not recorded in ACTION_SHA_RESOLUTION" in x for x in p)


def test_missing_recorded_tag_fails():
    _, probs = awt.load_resolution(_res(actions=[{
        "action": "a/b", "tag": "", "resolved_sha": SHA,
        "source_ref": "refs/tags/v1",
    }]))
    assert any("tag missing" in p for p in probs)


def test_actions_key_missing_is_rejected():
    rec, probs = awt.load_resolution({"resolved_at_utc": "x"})
    assert rec == {} and any("'actions' missing" in p for p in probs)


# permissions still enforced
def test_missing_permissions_fails():
    bad = GOOD.replace("permissions:\n  contents: read\n", "")
    assert any("no explicit top-level permissions" in x
               for x in awt.check_workflow("ci.yml", bad, REC))


def test_write_all_fails():
    bad = GOOD.replace("permissions:\n  contents: read",
                       "permissions: write-all")
    assert any("write-all forbidden" in x
               for x in awt.check_workflow("ci.yml", bad, REC))


def test_non_release_write_unjustified_fails():
    bad = GOOD.replace("  contents: read", "  contents: write")
    assert any("unjustified write permission" in x
               for x in awt.check_workflow("ci.yml", bad, REC, contract=""))


def test_release_write_allowed():
    rel = GOOD.replace("  contents: read",
                       "  contents: write\n  id-token: write")
    assert not any("unjustified write" in x
                   for x in awt.check_workflow("release.yml", rel, REC))
