#!/usr/bin/env python3
from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from noise_policy import evaluate_policy, load_policy_file  # type: ignore
from noise_scan import RULES, scan_repository  # type: ignore



def _resolve_output_path(root: Path, output_relpath: str) -> Path:
    out = (root / output_relpath).resolve()
    root_resolved = root.resolve()
    if out == root_resolved or root_resolved not in out.parents:
        raise ValueError("--output must stay within repository root")
    return out


def _assert_summary_invariants(summary: dict) -> None:
    expected = {r.name for r in RULES}
    got = set(summary["matches"])
    if got != expected:
        raise ValueError(f"summary rule keys mismatch: expected={sorted(expected)} got={sorted(got)}")
    for r in RULES:
        m = summary["matches"][r.name]
        zone_total = sum(m["by_zone"].values())
        if zone_total != m["total"]:
            raise ValueError(f"zone/total mismatch for {r.name}: {zone_total} != {m['total']}")


def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Deterministic repository noise hygiene audit")
    ap.add_argument("--output", default="evidence/noise_hygiene/latest.json")
    ap.add_argument("--snapshot-tag", default=None)
    ap.add_argument("--generated-at-utc", default=datetime.now(UTC).strftime("%Y-%m-%d"))
    ap.add_argument("--policy-file", default=".auditignore.json")
    ap.add_argument("--enforce", action="store_true")
    return ap.parse_args()


def main() -> int:
    args = _parse_args()
    out = _resolve_output_path(ROOT, args.output)
    summary = scan_repository(ROOT, args.generated_at_utc, args.output)
    _assert_summary_invariants(summary)

    policy = load_policy_file(ROOT / args.policy_file)
    policy_result = evaluate_policy(summary, policy, current_date=args.generated_at_utc)
    summary["policy"] = policy_result

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if args.snapshot_tag:
        snap = out.parent / f"snapshot_{args.snapshot_tag}.json"
        snap.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if args.enforce and policy_result["status"] == "RED":
        print("NOISE AUDIT — RED")
        for v in policy_result["violations"]:
            print(f"- {v}")
        return 1

    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
