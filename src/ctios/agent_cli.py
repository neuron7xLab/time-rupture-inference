# SPDX-License-Identifier: MIT
"""`tri-agent` — run the TemporalAgent on a real numeric stream.

Input: --file (one number per line, or first CSV column) | --stdin |
--demo (synthetic regime-shift stream). Output: JSONL of per-step
decisions to stdout (or --out); a summary line to stderr.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterator
from pathlib import Path

import numpy as np

from ctios.agent import TemporalAgent


def _from_file(path: Path) -> Iterator[float]:
    for raw in path.read_text().splitlines():
        s = raw.strip()
        if not s:
            continue
        tok = s.split(",")[0].strip()
        try:
            yield float(tok)
        except ValueError:
            continue  # skip header / non-numeric


def _from_stdin() -> Iterator[float]:
    for raw in sys.stdin:
        s = raw.strip().split(",")[0].strip()
        if s:
            try:
                yield float(s)
            except ValueError:
                continue


def _demo(seed: int, n: int = 600) -> Iterator[float]:
    rng = np.random.default_rng(seed)
    for k in range(n):
        mean = 10.0 if k < n // 2 else 17.0  # one hidden regime shift
        yield float(mean + rng.normal(0.0, 1.0))


def main() -> int:
    ap = argparse.ArgumentParser(prog="tri-agent")
    ap.add_argument("--backend", choices=["echo_state", "adaptive"],
                    default="echo_state")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--file", type=Path)
    src.add_argument("--stdin", action="store_true")
    src.add_argument("--demo", action="store_true")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--warmup", type=int, default=60)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    if args.file is not None:
        stream = _from_file(args.file)
    elif args.stdin:
        stream = _from_stdin()
    else:
        stream = _demo(args.seed)

    agent = TemporalAgent(backend=args.backend, seed=args.seed, warmup=args.warmup)
    decisions = agent.run(stream)
    lines = [json.dumps(d.as_dict(), default=float) for d in decisions]
    text = "\n".join(lines) + ("\n" if lines else "")
    if args.out is not None:
        args.out.write_text(text)
    else:
        sys.stdout.write(text)

    n = len(decisions)
    if n:
        mae = sum(abs(d.error) for d in decisions) / n
        shifts = sum(d.regime_shift for d in decisions)
        first = next((d.step for d in decisions if d.regime_shift), None)
    else:
        mae, shifts, first = 0.0, 0, None
    sys.stderr.write(
        f"tri-agent[{args.backend}] steps={n} mae={mae:.4f} "
        f"regime_shifts={shifts} first_shift_step={first}\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
