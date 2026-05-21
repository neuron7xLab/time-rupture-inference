from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from pathlib import PurePosixPath

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.cyber_hygiene_contract import EXPECTED_CLASS_COUNT, TARGETS_PATH


@dataclass(frozen=True)
class FindingClass:
    key: str
    title: str
    rationale: str


DEFAULT_TARGET_7: tuple[FindingClass, ...] = (
    FindingClass("B607", "PATH-hijack subprocess execution", "partial executable path in subprocess enables PATH hijack in compromised runner"),
    FindingClass("B603", "Untrusted subprocess execution surface", "subprocess calls without explicit trust boundary widen command-injection blast radius"),
    FindingClass("B404", "Direct subprocess usage without policy guard", "raw subprocess usage bypasses centralized execution policy and audit hooks"),
    FindingClass("B101", "Runtime assert used as security control", "assert can be stripped with optimization and must not enforce safety"),
    FindingClass("B105", "Hardcoded secret-like literal", "embedded secret-like literals increase credential disclosure risk"),
    FindingClass("SCRIPTS", "Concentrated operational risk in scripts/", "risk clusters in operational scripts create repeatable exploit surface"),
    FindingClass("SRC", "Runtime library risk in src/", "runtime modules carrying findings propagate risk into production paths"),
)
TEST_ID_RE = re.compile(r"^[A-Z0-9_]+$")
FILENAME_RE = re.compile(r"^[a-zA-Z0-9_./-]+$")


def _load_bandit(path: Path, *, max_bytes: int = 20_000_000) -> tuple[list[dict], int]:
    if path.stat().st_size > max_bytes:
        raise ValueError(f"Bandit JSON too large: {path.stat().st_size} > {max_bytes}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Bandit JSON contract violation: top-level object must be a dict")
    results = raw.get("results", [])
    if not isinstance(results, list):
        raise ValueError("Bandit JSON contract violation: 'results' must be a list")
    cleaned: list[dict] = []
    dropped = 0
    for row in results:
        test_id = str(row.get("test_id", ""))
        filename = str(row.get("filename", ""))
        if not TEST_ID_RE.fullmatch(test_id):
            dropped += 1
            continue
        if not FILENAME_RE.fullmatch(filename):
            dropped += 1
            continue
        if ".." in PurePosixPath(filename).parts:
            dropped += 1
            continue
        cleaned.append({"test_id": test_id, "filename": filename})
    return cleaned, dropped


def _load_targets(path: Path | None) -> tuple[FindingClass, ...]:
    if path is None:
        return DEFAULT_TARGET_7
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("targets contract violation: expected top-level list")
    out: list[FindingClass] = []
    for item in payload:
        if not isinstance(item, dict):
            raise ValueError("targets contract violation: each item must be an object")
        out.append(FindingClass(key=item["key"], title=item["title"], rationale=item["rationale"]))
    if len(out) != EXPECTED_CLASS_COUNT:
        raise ValueError(
            f"targets contract violation: expected exactly {EXPECTED_CLASS_COUNT} classes, got {len(out)}"
        )
    keys = [x.key for x in out]
    if len(set(keys)) != len(keys):
        raise ValueError("targets contract violation: duplicate class keys are forbidden")
    return tuple(out)


def build_report(
    results: list[dict],
    targets: tuple[FindingClass, ...] = DEFAULT_TARGET_7,
    *,
    dropped_count: int = 0,
    strict: bool = True,
    mode: str = "must_exist",
) -> dict:
    by_test: dict[str, list[dict]] = defaultdict(list)
    for row in results:
        by_test[row.get("test_id", "UNKNOWN")].append(row)
    by_test["SCRIPTS"] = [r for r in results if _top_dir(r.get("filename", "")) == "scripts"]
    by_test["SRC"] = [r for r in results if _top_dir(r.get("filename", "")) == "src"]
    missing = [f.key for f in targets if not by_test.get(f.key)]
    nonzero = [f.key for f in targets if by_test.get(f.key)]

    top = []
    for cls in targets:
        rows = by_test.get(cls.key, [])
        files = Counter(r.get("filename", "") for r in rows)
        ranked = sorted(files.items(), key=lambda kv: (-kv[1], kv[0]))
        top.append(
            {
                "id": cls.key,
                "title": cls.title,
                "criticality": "CRITICAL",
                "count": len(rows),
                "rationale": cls.rationale,
                "top_files": [
                    {"file": fname, "count": cnt}
                    for fname, cnt in ranked[:5]
                ],
            }
        )

    status_ok = not missing if mode == "must_exist" else not nonzero
    status_ok = status_ok and (dropped_count == 0 or not strict)
    return {
        "status": "PASS" if status_ok else "FAIL",
        "exactly_7_classes": len(targets),
        "mode": mode,
        "missing_required_classes": missing,
        "present_disallowed_classes": nonzero if mode == "must_not_exist" else [],
        "dropped_invalid_rows": dropped_count,
        "findings": top,
    }


def _top_dir(filename: str) -> str:
    path = PurePosixPath(filename)
    parts = path.relative_to("/").parts if path.is_absolute() else path.parts
    if not parts:
        return ""
    if ".." in parts:
        return ""
    return parts[0]


def main() -> int:
    ap = argparse.ArgumentParser(description="Extract exactly 7 recurrent critical hygiene defects from Bandit JSON.")
    ap.add_argument("--bandit-json", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--targets-json", type=Path, default=TARGETS_PATH)
    ap.add_argument("--allow-sanitized-drops", action="store_true")
    ap.add_argument(
        "--mode",
        choices=("must_exist", "must_not_exist"),
        default="must_not_exist",
        help="Policy mode: fail if classes are missing (must_exist) or fail if classes are present (must_not_exist).",
    )
    args = ap.parse_args()

    findings, dropped = _load_bandit(args.bandit_json)
    targets = _load_targets(args.targets_json)
    report = build_report(
        findings,
        targets,
        dropped_count=dropped,
        strict=not args.allow_sanitized_drops,
        mode=args.mode,
    )
    tmp = args.output.with_suffix(args.output.suffix + ".tmp")
    tmp.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    tmp.replace(args.output)

    if report["status"] != "PASS":
        print("CYBER HYGIENE AUDIT — FAIL")
        if args.mode == "must_exist":
            print("missing required recurring classes:", ", ".join(report["missing_required_classes"]))
        else:
            print("present disallowed classes:", ", ".join(report["present_disallowed_classes"]))
        if report["dropped_invalid_rows"]:
            print("invalid rows dropped:", report["dropped_invalid_rows"])
        return 1

    print("CYBER HYGIENE AUDIT — PASS (exactly 7 critical recurring classes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
