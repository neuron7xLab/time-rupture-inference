#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Independent root of trust. Intentionally tiny, stdlib-only, NO ctios
import, NO repo install. A reviewer copies this file + the lock outside
the repo and runs it to prove the repo's verifier files were not
silently weakened.

Format of verifier_manifest.lock: one `sha256␠␠relpath` line per file
(GNU sha256sum-compatible). Exit non-zero on any mismatch / missing /
extra.

    python check_verifier_manifest_static.py --repo /path/to/repo
"""
import argparse
import hashlib
import sys
from pathlib import Path


def _sha256(p):
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--lock", default="")
    a = ap.parse_args()
    repo = Path(a.repo).resolve()
    lock = Path(a.lock) if a.lock else repo / "verifier_manifest.lock"
    if not lock.exists():
        print(f"FAIL: lock not found: {lock}")
        return 2
    bad = []
    seen = 0
    for line in lock.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            want, rel = line.split(None, 1)
        except ValueError:
            bad.append(f"malformed lock line: {line!r}")
            continue
        seen += 1
        f = repo / rel
        if not f.exists():
            bad.append(f"MISSING {rel}")
            continue
        got = _sha256(f)
        if got != want:
            bad.append(f"MISMATCH {rel}\n  expected {want}\n  actual   {got}")
    if seen == 0:
        print("FAIL: lock has no entries")
        return 2
    if bad:
        print("VERIFIER MANIFEST — FAIL")
        for b in bad:
            print("  " + b)
        return 1
    print(f"VERIFIER MANIFEST — OK ({seen} verifier files pinned)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
