"""The structural anti-self-deception test: a learning agent must be
incapable of receiving the hidden schedule, by construction."""

import dataclasses
import inspect

from ctios import agents
from ctios.env import Observation


def test_observation_exposes_only_step_and_interval():
    fields = {f.name for f in dataclasses.fields(Observation)}
    assert fields == {"step", "observed_interval"}


def test_learning_agents_take_no_hidden_params():
    forbidden = {"tau0", "tau1", "t_star", "sigma", "hidden", "schedule"}
    for cls in (
        agents.LearnedAgent,
        agents.LastIntervalAgent,
        agents.MovingAverageAgent,
        agents.ExpSmoothingAgent,
        agents.RandomAgent,
    ):
        params = set(inspect.signature(cls.__init__).parameters)
        assert not (params & forbidden), f"{cls.__name__} leaks {params & forbidden}"


def test_learned_source_never_references_hidden():
    src = inspect.getsource(agents.LearnedAgent)
    for token in ("_HiddenSchedule", "tau0", "tau1", "t_star", "eval_true_mean"):
        assert token not in src


def test_only_oracle_and_injected_take_privileged_input():
    # injected legitimately takes tau0 (it IS the strawman); oracle takes the
    # schedule (it IS the upper bound). Nothing else may.
    assert "tau0" in set(inspect.signature(agents.InjectedAgent.__init__).parameters)
    assert "hidden" in set(inspect.signature(agents.OracleAgent.__init__).parameters)
