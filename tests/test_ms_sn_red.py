from __future__ import annotations

import math
from types import ModuleType

import pytest


def _runtime_module() -> ModuleType:
    return pytest.importorskip("ctios.ms_sn_runtime")


def test_red_forced_synchrony_must_raise_model_stasis() -> None:
    runtime = _runtime_module()
    state, config = runtime.build_forced_synchrony_case()
    with pytest.raises(runtime.SystemAnomaly):
        runtime.execute_verification_cycle(state, config)


def test_red_forced_desynchrony_must_raise_desynchrony_collapse() -> None:
    runtime = _runtime_module()
    state, config = runtime.build_forced_desynchrony_case()
    with pytest.raises(runtime.SystemAnomaly):
        runtime.execute_verification_cycle(state, config)


@pytest.mark.parametrize("field", ["gamma", "R", "F", "theta_i", "omega_i", "A_ij"])
def test_red_nonfinite_state_halts_before_mutation(field: str) -> None:
    runtime = _runtime_module()
    state, config = runtime.build_nonfinite_case(field=field, value=math.nan)
    with pytest.raises(runtime.SystemAnomaly):
        runtime.execute_verification_cycle(state, config)
