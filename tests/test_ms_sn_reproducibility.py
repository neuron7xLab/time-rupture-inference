from __future__ import annotations
import pytest

def test_same_seed_produces_identical_trajectory_hash():
    pytest.importorskip("ctios.ms_sn_runtime")
