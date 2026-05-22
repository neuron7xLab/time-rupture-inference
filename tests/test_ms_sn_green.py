from __future__ import annotations
import pytest

def test_green_overload_triggered_growth_is_atomic():
    pytest.importorskip("ctios.ms_sn_runtime")
