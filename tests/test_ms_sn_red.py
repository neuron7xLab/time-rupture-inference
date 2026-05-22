from __future__ import annotations
import math
import pytest

def test_red_forced_synchrony_must_raise_model_stasis():
    pytest.importorskip("ctios.ms_sn_runtime")
    from ctios.ms_sn_runtime import SystemAnomaly, build_forced_synchrony_case, execute_verification_cycle
    state, config = build_forced_synchrony_case()
    with pytest.raises(SystemAnomaly):
        execute_verification_cycle(state, config)

def test_red_forced_desynchrony_must_raise_desynchrony_collapse():
    pytest.importorskip("ctios.ms_sn_runtime")
    from ctios.ms_sn_runtime import SystemAnomaly, build_forced_desynchrony_case, execute_verification_cycle
    state, config = build_forced_desynchrony_case()
    with pytest.raises(SystemAnomaly):
        execute_verification_cycle(state, config)

@pytest.mark.parametrize("field", ["gamma", "R", "F", "theta_i", "omega_i", "A_ij"])
def test_red_nonfinite_state_halts_before_mutation(field: str):
    pytest.importorskip("ctios.ms_sn_runtime")
    from ctios.ms_sn_runtime import SystemAnomaly, build_nonfinite_case, execute_verification_cycle
    state, config = build_nonfinite_case(field=field, value=math.nan)
    with pytest.raises(SystemAnomaly):
        execute_verification_cycle(state, config)
