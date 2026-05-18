# SPDX-License-Identifier: MIT
"""`python -m ctios.spec_cli compile <spec.yaml> --out <dir>`.

Compiles a redacted hypothesis to a BLOCKED_UNTIL_PROBED research
object and writes the evidence contract + next-experiment policy. It
never runs a probe and never produces a verdict.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from ctios.redacted_io import load_redacted_spec, validate_redacted_spec
from ctios.spec_compiler import compile_redacted_hypothesis, evidence_contract_md


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="ctios.spec_cli")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("compile", help="compile a redacted hypothesis")
    c.add_argument("spec", type=Path)
    c.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)

    spec = load_redacted_spec(args.spec)
    issues = validate_redacted_spec(spec)
    compiled = compile_redacted_hypothesis(spec)

    out: Path = args.out
    out.mkdir(parents=True, exist_ok=True)
    (out / "compiled_spec.json").write_text(
        json.dumps(compiled.as_dict(), indent=2, default=str)
    )
    (out / "evidence_contract.md").write_text(evidence_contract_md(compiled))
    (out / "next_experiment_policy.yaml").write_text(
        yaml.safe_dump(compiled.next_experiment_policy, sort_keys=False)
    )

    print(f"compiled {spec.hypothesis_id}  sha={compiled.spec_sha256[:16]}")
    print(f"initial_verdict={compiled.initial_verdict}  out={out}")
    for i in issues:
        print(f"  [{i.severity}] {i.code}: {i.message}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
