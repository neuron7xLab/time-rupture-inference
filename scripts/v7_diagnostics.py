# SPDX-License-Identifier: MIT
"""v7 diagnostics — discriminate the root cause of the v6+v7 negatives.

Pre-registered (docs/prereg/cti_os_v7_diagnostics_preregistration.md):
measure headroom = (heuristic - oracle) / heuristic on the v7 grid.
NO_HEADROOM (<=0.15) => environment is the boundary; LEARNABLE_GAP (>0.15)
=> model/optimization is the boundary. No threshold tuned after results.
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
PRE = ROOT / "docs" / "prereg" / "cti_os_v7_diagnostics_preregistration.md"
HEADROOM_MAX = 0.15  # pinned in the pre-registration, pre-run


class _Oracle:
    """Regime-aware upper bound: predicts the true regime mean. Its error
    is the irreducible noise floor — the information limit of the env."""

    def __init__(self, n: int, shift: float):
        self._tau = [10.0, 10.0 + shift, 10.0 + 0.5 * shift]
        self._t1, self._t2 = n // 3, 2 * n // 3
        self._k = 0

    def predict(self) -> float:
        k = self._k
        return self._tau[0] if k < self._t1 else (
            self._tau[1] if k < self._t2 else self._tau[2]
        )

    def update(self, obs: float) -> None:
        self._k += 1


def _agg(model_factory, seeds: list[int], shifts: list[float], n: int, t_star: int) -> float:
    vals = []
    for sh in shifts:
        for sd in seeds:
            stream = _env_stream(sd, n, sh, np.random.default_rng(sd))
            vals.append(_drive(model_factory(sd, sh), stream, t_star)["post_shift_mae"])
    return float(np.mean(vals))


def _latent_separability(seed: int, n: int, shift: float) -> float:
    """Reservoir hidden-state across-regime vs within-regime variance
    ratio. Descriptive only (smoothing ≈ low, representation ≈ higher)."""
    from run_v7_cpu import _Reservoir

    res = _Reservoir(dim=16, seed=seed, leak=0.5, ridge=1e-2)
    stream = _env_stream(seed, n, shift, np.random.default_rng(seed))
    t1, t2 = n // 3, 2 * n // 3
    H = np.empty((n, res.h.size))
    last = 1.0
    for k in range(n):
        x = last if np.isnan(stream[k]) else float(stream[k])
        res.update(x)
        H[k] = res.h
        last = x
    groups = [H[:t1], H[t1:t2], H[t2:]]
    means = np.array([g.mean(0) for g in groups])
    between = float(np.var(means, axis=0).mean())
    within = float(np.mean([g.var(0).mean() for g in groups])) + 1e-9
    return between / within


def main() -> int:
    seeds = list(range(CFG["seed_start"], CFG["seed_start"] + CFG["seed_count"]))
    shifts = [float(s) for s in CFG["shift_magnitudes"]]
    n, t_star = 600, 200

    agg_heur = _agg(lambda sd, sh: _make("heuristic_v4", sd), seeds, shifts, n, t_star)
    agg_orac = _agg(lambda sd, sh: _Oracle(n, sh), seeds, shifts, n, t_star)
    headroom = (agg_heur - agg_orac) / agg_heur if agg_heur > 0 else 0.0
    branch = "NO_HEADROOM" if headroom <= HEADROOM_MAX else "LEARNABLE_GAP"
    sep = float(np.mean([_latent_separability(s, n, shifts[0]) for s in seeds[:5]]))

    summary = {
        "agg_heuristic_v4": agg_heur,
        "agg_oracle": agg_orac,
        "headroom_ratio": headroom,
        "headroom_max_pinned": HEADROOM_MAX,
        "branch": branch,
        "esn_latent_separability": sep,
        "grid": f"{len(seeds)} seeds x {len(shifts)} shifts",
    }
    (ROOT / "docs" / "reports" / "cti_os_v7_diagnostics_verdict.md").write_text(
        "# CTI-OS v7 diagnostics — convergence verdict\n\n"
        f"**BRANCH: {branch}** (headroom_ratio={headroom:.4f}, "
        f"pinned max={HEADROOM_MAX})\n\n"
        f"- agg heuristic_v4 = {agg_heur:.4f}\n"
        f"- agg oracle (info floor) = {agg_orac:.4f}\n"
        f"- esn latent separability (descriptive) = {sep:.4f}\n\n"
        "## Convergence reading (v6 RED + v7 RED + this)\n"
        + (
            "The scalar heuristic operates within "
            f"{headroom * 100:.1f}% of the regime-aware oracle. The v7 "
            "environment cannot reward added model complexity — the "
            "boundary is the **environment**, not the model class. "
            "Redirect: build an environment with structure a scalar "
            "provably cannot represent (long-range / latent dependence) "
            "BEFORE any further 'stronger model' lineage. v6/v7 negatives "
            "are explained, not mysterious.\n"
            if branch == "NO_HEADROOM"
            else
            "The oracle substantially beats the heuristic yet the learned "
            "models lost: the boundary is **model/optimization**, not the "
            "environment. The no-headroom reading is REFUTED; redirect to "
            "stronger learners on this same env.\n"
        )
        + "\nClaim boundary: a localized boundary condition, not a "
        "capability. No intelligence / cognition / AGI claim.\n"
    )
    if branch == "NO_HEADROOM":
        (ROOT / "evidence" / "CONVERGENCE_v6_v7.md").write_text(
            "# CONVERGENCE — v6 + v7 negatives, one boundary (pinned)\n\n"
            f"Two surface-distinct REDs (v6 precision-weighting, v7 "
            f"reservoir/SSM) converge: on this rupture class the scalar "
            f"heuristic is within {headroom * 100:.1f}% of the oracle "
            f"floor (agg {agg_heur:.4f} vs {agg_orac:.4f}). No model "
            "class can pay its complexity here — there is no headroom. "
            "This is a delivered boundary artifact, not a string of "
            "failures: the v7 environment must change (provable "
            "scalar-inexpressible structure) before any stronger-model "
            "question is scientifically askable. Frozen v4 untouched.\n"
        )

    print(f"\n=== v7 DIAGNOSTICS :: {branch} ===")
    print(f"heuristic={agg_heur:.4f} oracle={agg_orac:.4f} "
          f"headroom={headroom:.4f} (max {HEADROOM_MAX}) sep={sep:.3f}")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
