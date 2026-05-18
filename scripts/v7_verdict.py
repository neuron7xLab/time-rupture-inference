# SPDX-License-Identifier: MIT
"""PR #3 — v7 scientific verdict. Full deterministic grid + the
pre-registered decision rule. GREEN/RED, no threshold tuning, RED
preserved as evidence/NEGATIVE_RESULT_v7.md.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from run_v7_cpu import _drive, _env_stream, _make  # noqa: E402

CFG = yaml.safe_load((ROOT / "configs" / "v7_experiment.yaml").read_text())
LEARNED = ("esn_small", "linear_ssm_small")
HEUR, BASE = "heuristic_v4", "ar_baseline"
MIN_WR = 0.60  # from prereg acceptance thresholds (unchanged)


def _cell(model: str, seed: int, n: int, shift: float, t_star: int) -> float:
    stream = _env_stream(seed, n, shift, np.random.default_rng(seed))
    return _drive(_make(model, seed), stream, t_star)["post_shift_mae"]


def main() -> int:
    seeds = list(range(CFG["seed_start"], CFG["seed_start"] + CFG["seed_count"]))
    shifts = [float(s) for s in CFG["shift_magnitudes"]]
    n, t_star = 600, 200
    grid = [(sh, sd) for sh in shifts for sd in seeds]

    pm: dict[str, dict[tuple[float, int], float]] = {
        m: {} for m in (*LEARNED, HEUR, BASE)
    }
    for m in pm:
        for sh, sd in grid:
            pm[m][(sh, sd)] = _cell(m, sd, n, sh, t_star)

    # determinism replay on one cell
    replay_ok = _cell("esn_small", seeds[0], n, shifts[0], t_star) == pm["esn_small"][
        (shifts[0], seeds[0])
    ]
    finite_ok = all(np.isfinite(v) for d in pm.values() for v in d.values())

    def agg(m: str) -> float:
        return float(np.mean([pm[m][g] for g in grid]))

    def winrate(m: str, ref: str) -> float:
        return float(np.mean([pm[m][g] < pm[ref][g] for g in grid]))

    def holds_each_shift(m: str, ref: str) -> bool:
        for sh in shifts:
            cells = [(sh, sd) for sd in seeds]
            if not np.mean([pm[m][c] for c in cells]) < np.mean(
                [pm[ref][c] for c in cells]
            ):
                return False
        return True

    results = {}
    green = False
    winner = None
    for lm in LEARNED:
        ok = (
            agg(lm) < agg(HEUR)
            and agg(lm) < agg(BASE)
            and winrate(lm, HEUR) >= MIN_WR
            and winrate(lm, BASE) >= MIN_WR
            and holds_each_shift(lm, HEUR)
            and holds_each_shift(lm, BASE)
        )
        results[lm] = {
            "agg": agg(lm),
            "wr_vs_heuristic": winrate(lm, HEUR),
            "wr_vs_baseline": winrate(lm, BASE),
            "passes": bool(ok),
        }
        if ok and replay_ok and finite_ok:
            green = True
            winner = lm

    verdict = "GREEN" if green else "RED"
    summary = {
        "verdict": verdict,
        "winner": winner,
        "agg_heuristic_v4": agg(HEUR),
        "agg_ar_baseline": agg(BASE),
        "learned": results,
        "deterministic_replay": replay_ok,
        "finite_metrics": finite_ok,
        "grid": f"{len(seeds)} seeds x {len(shifts)} shifts",
    }

    rep = ROOT / "docs" / "reports" / "cti_os_v7_scientific_verdict.md"
    lines = [
        "# CTI-OS v7 — Scientific Verdict (PR #3)",
        "",
        f"**VERDICT: {verdict}**" + (f" — winner: `{winner}`" if winner else ""),
        "",
        "Decision rule (pre-registered, unchanged): a learned model "
        "(`esn_small` / `linear_ssm_small`) must beat BOTH the frozen v4 "
        "heuristic AND the AR baseline on aggregate post-shift MAE, with "
        f"win-rate ≥ {MIN_WR} vs each, holding on every shift, across "
        f"{len(seeds)} seeds, deterministic, finite.",
        "",
        f"- agg post_shift_mae  heuristic_v4={agg(HEUR):.4f}  "
        f"ar_baseline={agg(BASE):.4f}",
    ]
    for lm in LEARNED:
        r = results[lm]
        lines.append(
            f"- {lm}: agg={r['agg']:.4f}  wr_vs_heuristic={r['wr_vs_heuristic']:.3f}  "
            f"wr_vs_baseline={r['wr_vs_baseline']:.3f}  passes={r['passes']}"
        )
    lines += [
        f"- deterministic_replay={replay_ok}  finite={finite_ok}",
        "",
        "Claim boundary: a learned reservoir-readout sequence model with a "
        "representational advantage on a harder nonstationary task — NOT "
        "intelligence, NOT cognition, NOT AGI.",
        "",
        "```json",
        json.dumps(summary, indent=2),
        "```",
    ]
    rep.write_text("\n".join(lines))

    if not green:
        (ROOT / "evidence" / "NEGATIVE_RESULT_v7.md").write_text(
            "# NEGATIVE RESULT — v7 scientific verdict (pinned, not erased)\n\n"
            f"**Verdict: RED.** Reported as-is. No threshold tuned.\n\n"
            f"- heuristic_v4 agg={agg(HEUR):.4f}, ar_baseline agg={agg(BASE):.4f}\n"
            + "".join(
                f"- {lm}: agg={results[lm]['agg']:.4f}, "
                f"wr_vs_heuristic={results[lm]['wr_vs_heuristic']:.3f}, "
                f"wr_vs_baseline={results[lm]['wr_vs_baseline']:.3f}\n"
                for lm in LEARNED
            )
            + "\n## Disposition\nThe learned reservoir-readout models did "
            "not beat BOTH the disciplined scalar heuristic and the AR "
            "baseline under the pre-registered rule. Representational "
            "capacity alone is not sufficient on this rupture class. "
            "Preserved negative; frozen v4 untouched. NOT a defeat — a "
            "killed hypothesis is a valid artifact.\n"
        )

    print(f"\n=== v7 SCIENTIFIC VERDICT :: {verdict} ===")
    print(f"heuristic={agg(HEUR):.4f} baseline={agg(BASE):.4f}")
    for lm in LEARNED:
        print(f"  {lm}: agg={results[lm]['agg']:.4f} "
              f"wr_h={results[lm]['wr_vs_heuristic']:.3f} "
              f"wr_b={results[lm]['wr_vs_baseline']:.3f} pass={results[lm]['passes']}")
    return 0 if green else 1


if __name__ == "__main__":
    raise SystemExit(main())
