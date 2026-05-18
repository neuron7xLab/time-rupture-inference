# SPDX-License-Identifier: MIT
"""Contract: TemporalAgent is deterministic, finite, online, and flags a
regime shift on a synthetic shift. Engineering tool — not a verdict."""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from ctios.agent import BACKENDS, Decision, TemporalAgent  # noqa: E402


def _shift_stream(seed: int, n: int = 600):
    rng = np.random.default_rng(seed)
    return [float((10.0 if k < n // 2 else 17.0) + rng.normal(0, 1)) for k in range(n)]


@pytest.mark.parametrize("backend", list(BACKENDS))
def test_deterministic_and_finite(backend):
    s = _shift_stream(0)
    a = TemporalAgent(backend=backend, seed=0).run(s)
    b = TemporalAgent(backend=backend, seed=0).run(s)
    assert [d.as_dict() for d in a] == [d.as_dict() for d in b]
    assert all(np.isfinite(d.prediction) and np.isfinite(d.error) for d in a)
    assert len(a) == len(s) and isinstance(a[0], Decision)


@pytest.mark.parametrize("backend", list(BACKENDS))
def test_flags_regime_shift_after_change(backend):
    out = TemporalAgent(backend=backend, seed=1, warmup=60).run(_shift_stream(1))
    shifts = [d.step for d in out if d.regime_shift]
    assert shifts, "agent must flag the hidden regime shift"
    assert any(280 <= s <= 420 for s in shifts)  # near the true change @300


def test_bad_backend_fails_loud():
    with pytest.raises(ValueError, match="backend"):
        TemporalAgent(backend="bogus")


def test_online_predict_then_observe_contract():
    ag = TemporalAgent(backend="adaptive", seed=0)
    p = ag.predict()
    d = ag.observe(12.0)
    assert d.prediction == p and d.observed == 12.0 and d.step == 0
