"""Hard verification of representational compression: deterministic,
compressive, task-retaining, noise-rejecting, and honest about discarded
entropy. Each property is a gate; if compression starts hallucinating
structure or leaking, a test goes red.
"""

from __future__ import annotations

import numpy as np
import pytest

from ctios import entropy_compression as ec


def _ruptured(seed: int, n: int = 400, t_star: int = 200) -> np.ndarray:
    rng = np.random.default_rng(seed)
    x = np.empty(n, dtype=np.float64)
    x[:t_star] = 1.0 + rng.normal(0, 0.1, t_star)
    x[t_star:] = 3.0 + rng.normal(0, 0.1, n - t_star)
    return x


def _flat(seed: int, n: int = 400) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return 2.0 + rng.normal(0, 0.1, n)


# ---- deterministic -------------------------------------------------------
def test_compression_is_byte_identical_on_replay():
    x = _ruptured(1)
    a = ec.compress(x).as_vector()
    b = ec.compress(x).as_vector()
    assert np.array_equal(a, b)


def test_empty_series_rejected():
    with pytest.raises(ValueError, match="empty"):
        ec.compress(np.array([]))


# ---- compressive ---------------------------------------------------------
def test_state_is_fixed_low_dimension():
    st = ec.compress(_ruptured(2))
    assert st.k_out == ec.K_OUT == 6
    assert st.as_vector().size == 6
    assert st.k_out < st.n_in


def test_entropy_is_reduced():
    x = _ruptured(3)
    st = ec.compress(x)
    ratio = ec.compression_ratio(x, st)
    assert ratio > 1.0  # fewer bits out than in
    assert ec.shannon_bits(x) > st.k_out * 64


def test_constant_series_has_zero_bits():
    assert ec.shannon_bits(np.full(100, 5.0)) == 0.0


# ---- task-retaining + noise-rejecting -----------------------------------
def test_rupture_is_retained_in_the_state():
    st = ec.compress(_ruptured(4, t_star=200))
    # the inferred change point lands near the true T*
    assert abs(st.change_index - 200) <= 20
    assert st.change_score > 2.0


def test_flat_series_yields_low_change_score():
    st = ec.compress(_flat(5))
    assert st.change_score < 1.0


def test_discriminates_rupture_from_noise():
    for seed in range(5):
        margin = ec.discriminates(_ruptured(seed), _flat(seed + 100))
        assert margin > 1.0, f"seed {seed}: margin {margin}"


# ---- honest about discarded entropy -------------------------------------
def test_residual_std_exposes_discarded_entropy():
    st = ec.compress(_ruptured(6))
    # the two-segment model leaves only the within-segment noise (~0.1)
    assert 0.0 < st.residual_std < 0.5


def test_pe_energy_higher_for_ruptured_than_flat():
    assert ec.compress(_ruptured(7)).pe_energy > ec.compress(_flat(7)).pe_energy
