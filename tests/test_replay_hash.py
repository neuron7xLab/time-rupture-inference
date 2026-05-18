import hashlib

import numpy as np

from ctios.agents import LearnedAgent
from ctios.env import Environment


def _run(seed: int) -> str:
    env = Environment(10.0, 17.0, 300, 1.0, 600, seed)
    agent = LearnedAgent(prior=1.0)
    errs = []
    for _ in range(600):
        p = agent.predict()
        o = env.step()
        errs.append(o.observed_interval - p)
        agent.update(o.observed_interval)
    return hashlib.sha256(np.round(np.array(errs), 9).tobytes()).hexdigest()


def test_replay_hash_stable():
    assert _run(0) == _run(0)


def test_replay_hash_seed_sensitive():
    assert _run(0) != _run(3)
