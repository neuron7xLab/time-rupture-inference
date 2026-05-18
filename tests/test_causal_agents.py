import inspect

from ctios.causal_agents import CausalLearnedAgent, NoActionAgent, RandomActionAgent


def test_no_action_only_emits_observe():
    a = NoActionAgent()
    assert all(a.select_action(e) == "observe" for e in (None, 0.1, 9.0, -5.0))


def test_random_action_deterministic_under_seed():
    a1 = RandomActionAgent(seed=7)
    a2 = RandomActionAgent(seed=7)
    s1 = [a1.select_action(0.0) for _ in range(50)]
    s2 = [a2.select_action(0.0) for _ in range(50)]
    assert s1 == s2
    assert set(s1) <= {"observe", "stabilize", "destabilize"}
    assert RandomActionAgent(seed=1).select_action(0.0) is not None


def test_causal_learned_changes_action_after_large_error():
    a = CausalLearnedAgent()
    for _ in range(40):
        a.select_action(0.05)  # calm -> observe
    assert a.select_action(0.05) == "observe"
    a.select_action(50.0)  # huge surprise
    assert a.select_action(0.05) == "stabilize"


def test_causal_learned_does_not_access_hidden_schedule():
    params = set(inspect.signature(CausalLearnedAgent.__init__).parameters)
    assert not (params & {"tau0", "tau1", "t_star", "sigma", "hidden", "regime"})
    src = inspect.getsource(CausalLearnedAgent)
    assert all(t not in src for t in ("tau0", "tau1", "t_star", "_Hidden", "regime"))
