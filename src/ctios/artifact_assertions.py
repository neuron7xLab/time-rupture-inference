# SPDX-License-Identifier: MIT
"""ctios.artifact_assertions — a gate's exit code is not evidence.

A hard gate passes only if its artifact exists, is non-empty, parses,
matches a minimal schema, and is NOT stale (not carried over from a
previous commit). These are the checks the shell gates call so that
"exit 0" can never stand alone.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[2]

# A zero / placeholder commit is the canonical "stale / replayed /
# never-bound" marker — stale in EVERY environment, git or not. Never
# environment-gated.
_PLACEHOLDER_COMMIT = re.compile(r"^0{7,40}$")


class ArtifactError(AssertionError):
    pass


def _head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=_ROOT, capture_output=True, text=True, check=False,
    ).stdout.strip()


def assert_exists(path: Path) -> None:
    if not path.exists():
        raise ArtifactError(f"missing artifact: {path}")


def assert_non_empty(path: Path) -> None:
    assert_exists(path)
    if path.stat().st_size == 0 or not path.read_text().strip():
        raise ArtifactError(f"empty artifact: {path}")


def load_json(path: Path) -> dict[str, Any]:
    assert_non_empty(path)
    try:
        obj = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        raise ArtifactError(f"unparseable JSON {path}: {e}") from e
    if not isinstance(obj, dict):
        raise ArtifactError(f"JSON root must be object: {path}")
    return obj


def assert_schema(obj: dict[str, Any], required: list[str], path: Path) -> None:
    missing = [k for k in required if k not in obj]
    if missing:
        raise ArtifactError(f"{path}: missing keys {missing}")


def _reference_commit() -> tuple[str, str]:
    """Resolve the commit this tree was cut from. git HEAD first; in a
    provenance-stripped archive, a committed ``evidence/SOURCE_COMMIT``
    pin (written by the release packaging step). ``("", "none")`` only
    when NEITHER is available — which is itself an honest, hard state,
    never a silent pass."""
    head = _head()
    if head:
        return head, "git-HEAD"
    pin = _ROOT / "evidence" / "SOURCE_COMMIT"
    if pin.exists():
        v = pin.read_text().strip()
        if v:
            return v, "SOURCE_COMMIT-pin"
    return "", "none"


def assert_fresh_for_commit(
    obj: dict[str, Any], path: Path, key: str = "commit"
) -> None:
    """The artifact must record the commit this tree was cut from. A
    value from a previous commit (stale / replayed) is rejected.

    Fail-closed in EVERY environment:
      * a zero/placeholder commit is stale regardless of git presence;
      * if no reference commit can be resolved (no git, no pin) the
        freshness of a real commit is UNVERIFIABLE — that is a hard
        error, not a skipped check. A provenance-stripped ZIP cannot
        silently inherit the "fresh" claim.
    """
    val = str(obj.get(key, "")).strip()
    if not val or _PLACEHOLDER_COMMIT.match(val):
        raise ArtifactError(
            f"{path}: stale artifact — {key}={val!r} is an empty / "
            f"placeholder commit (never bound to a real revision)"
        )
    ref, src = _reference_commit()
    if not ref:
        raise ArtifactError(
            f"{path}: artifact freshness UNVERIFIABLE — no git HEAD "
            f"and no evidence/SOURCE_COMMIT pin; a provenance-stripped "
            f"archive cannot assert {key} freshness (fail-closed)"
        )
    if val[:12] != ref[:12] and val != ref:
        raise ArtifactError(
            f"{path}: stale artifact — {key}={val!r} != "
            f"{src} {ref[:12]!r}"
        )


def assert_artifact(
    path: Path,
    *,
    required: list[str] | None = None,
    commit_key: str | None = None,
) -> dict[str, Any]:
    obj = load_json(path)
    if required:
        assert_schema(obj, required, path)
    if commit_key:
        assert_fresh_for_commit(obj, path, commit_key)
    return obj


def main() -> int:
    """CLI: validate the known machine artifacts that exist."""
    checks: list[tuple[Path, list[str], str | None]] = [
        (_ROOT / "evidence" / "external_validation_status.json",
         ["status", "real_external_collaborator_run"], None),
        (_ROOT / "evidence" / "CODE_QUALITY_AUDIT_RESULT.json",
         ["clean", "findings", "checks"], None),
    ]
    ok = True
    for p, req, ck in checks:
        try:
            assert_artifact(p, required=req, commit_key=ck)
            print(f"OK   {p.relative_to(_ROOT)}")
        except ArtifactError as e:
            ok = False
            print(f"FAIL {e}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
