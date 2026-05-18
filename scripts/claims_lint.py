# SPDX-License-Identifier: MIT
"""Claim-lexicon linter (audit P1).

Fails loud if external-facing text asserts an ontological claim the
implemented scalar adaptive estimator does not support, or uses a
neuro/cognitive metaphor without an on-line qualifier and outside a
disclaimer block. Run: `python scripts/claims_lint.py` (exit 1 on any
violation). Wired into pytest and CI.
"""

from __future__ import annotations

import fnmatch
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = yaml.safe_load((ROOT / "claims.yaml").read_text())


def _exempt(rel: str) -> bool:
    return any(fnmatch.fnmatch(rel, pat) for pat in SPEC["exempt"])


def _files() -> list[Path]:
    out: list[Path] = []
    for g in SPEC["scan_globs"]:
        out += [p for p in ROOT.glob(g) if not _exempt(str(p.relative_to(ROOT)))]
    return sorted(set(out))


def lint() -> list[str]:
    forb = [t.lower() for t in SPEC["forbidden_assertive"]]
    soft = [t.lower() for t in SPEC["requires_qualifier"]]
    quals = [t.lower() for t in SPEC["qualifier_tokens"]]
    do, dc = SPEC["disclaimer_open"], SPEC["disclaimer_close"]
    violations: list[str] = []

    for f in _files():
        rel = f.relative_to(ROOT)
        in_disc = False
        for i, raw in enumerate(f.read_text().splitlines(), 1):
            line = raw.lower()
            if do in raw:
                in_disc = True
            if dc in raw:
                in_disc = False
                continue
            if in_disc:
                continue
            has_qual = any(q in line for q in quals)
            for t in forb:
                if t in line and not has_qual:
                    violations.append(
                        f"{rel}:{i}: forbidden assertive "
                        f"'{t.strip()}' :: {raw.strip()}"
                    )
            for t in soft:
                if t in line and not has_qual:
                    violations.append(
                        f"{rel}:{i}: unqualified metaphor "
                        f"'{t.strip()}' :: {raw.strip()}"
                    )
    return violations


def main() -> int:
    v = lint()
    if v:
        print("CLAIMS LINT — FAIL\n" + "\n".join(v))
        return 1
    print(f"CLAIMS LINT — PASS ({len(_files())} files clean)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
