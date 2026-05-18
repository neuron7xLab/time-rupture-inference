import dataclasses
import hashlib

import numpy as np

from ctios.causal_env import CausalEnvironment, CausalObservation


def _series(env, actions):
    env.reset()
    return [env.step(a).observed_interval for a in actions]


def _h(xs):
    return hashlib.sha256(np.round(np.array(xs), 9).tobytes()).hexdigest()


def test_same_seed_same_actions_identical():
    a = ["observe"] * 600
    e1 = CausalEnvironment(10.0, 14.0, 300, 1.0, 600, 0, mode="interventional")
    e2 = CausalEnvironment(10.0, 14.0, 300, 1.0, 600, 0, mode="interventional")
    assert _h(_series(e1, a)) == _h(_series(e2, a))


def test_observation_hides_hidden_variables():
    fields = {f.name for f in dataclasses.fields(CausalObservation)}
    assert fields == {"step", "observed_interval", "previous_action", "previous_error"}


def test_action_null_ignores_action_effects():
    e = CausalEnvironment(10.0, 14.0, 300, 1.0, 600, 1, mode="action_null")
    s_stab = _series(e, ["stabilize"] * 600)
    s_obs = _series(e, ["observe"] * 600)
    assert _h(s_stab) == _h(s_obs)


def test_interventional_mode_action_changes_trajectory():
    e = CausalEnvironment(10.0, 14.0, 300, 1.0, 600, 1, mode="interventional")
    s_stab = _series(e, ["stabilize"] * 600)
    s_obs = _series(e, ["observe"] * 600)
    assert _h(s_stab) != _h(s_obs)


def test_positive_and_negative_shifts_work():
    for delta in (4.0, -4.0):
        e = CausalEnvironment(10.0, 10.0 + delta, 300, 0.0, 600, 0, mode="interventional")
        e.reset()
        xs = [e.step("observe").observed_interval for _ in range(600)]
        assert abs(xs[100] - 10.0) < 1e-6
        assert abs(xs[400] - (10.0 + delta)) < 1e-6


def test_stabilize_reduces_post_shift_error_interventional():
    def post_mae(action):
        e = CausalEnvironment(10.0, 18.0, 300, 1.0, 600, 0, mode="interventional")
        e.reset()
        ae = []
        for k in range(600):
            o = e.step(action)
            ae.append(abs(o.observed_interval - (10.0 if k < 300 else 18.0)))
        return float(np.mean(ae[300:550]))

    assert post_mae("stabilize") < post_mae("observe")
