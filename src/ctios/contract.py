# SPDX-License-Identifier: MIT
"""Single source of truth for experiment invariants.

The class of bug this module exists to kill: a measurement constant
(`eval_horizon`) living partly in config and partly as a magic literal
in the runner and tests, letting the evaluation window silently drift
out of agreement with the pre-registered metric — a hidden pseudo-GREEN
channel. There is now exactly one place each invariant is defined, and
one fail-loud guard that every consumer must pass through.
"""

from __future__ import annotations

import yaml

from ctios.utils import ROOT

_ENV = yaml.safe_load((ROOT / "configs" / "env.yaml").read_text())
_METRICS = yaml.safe_load((ROOT / "configs" / "metrics.yaml").read_text())

# canonical invariants — read once, never duplicated as literals
EVAL_HORIZON: int = int(_METRICS["eval_horizon"])
RECOVERY_BAND_MULT: float = float(_METRICS["recovery_band_mult"])
RECOVERY_ROLL_WINDOW: int = int(_METRICS["recovery_roll_window"])
N_STEPS: int = int(_ENV["n_steps"])
T_STAR: int = int(_ENV["t_star"])
SIGMA: float = float(_ENV["sigma"])
TAU0: float = float(_ENV["tau0"])


def validate_window(
    t_star: int,
    eval_horizon: int,
    n: int,
    detection_step: int | None = None,
) -> None:
    """Fail loud, fail closed. No silent clamping, ever."""
    if not (0 <= t_star <= n):
        raise ValueError(f"t_star {t_star} must be within [0, {n}]")
    if eval_horizon <= 0:
        raise ValueError(f"eval_horizon {eval_horizon} must be > 0")
    if t_star + eval_horizon > n:
        raise ValueError(
            f"window [{t_star}, {t_star + eval_horizon}) exceeds series length {n}"
        )
    if detection_step is not None and not (0 <= detection_step < n):
        raise ValueError(
            f"detection_step {detection_step} must be within [0, {n - 1}] when provided"
        )


def validate_aligned_lengths(
    n: int, aux_n: int, *, names: tuple[str, str] = ("n", "aux_n")
) -> None:
    """Fail loud when paired series are not index-aligned."""
    if n != aux_n:
        left, right = names
        raise ValueError(
            f"aligned sequence lengths required, got {left}={n} and {right}={aux_n}"
        )
