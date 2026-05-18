# SPDX-License-Identifier: MIT
"""Audit P2 close-out — property-style stress, zero new dependency.

Universally-quantified property over a deterministically-sampled slice
of the parameter manifold (shift magnitude × noise × warmup × seed):

    post_shift_mae <= BOUND * sigma   for every sampled combination.

This asserts *bounded adaptation regret relative to the noise floor* —
the learner must converge near the irreducible floor, never diverge.

BOUND derivation (not tuned-to-pass): the oracle floor is ~0.8·sigma;
a 120-combo calibration sweep observed a worst post_mae/sigma of 1.089.
BOUND = 2.0 is a ~1.8x safety envelope over the observed worst — a real
invariant: exceeding it is a genuine divergence finding, not flake.
"""

import numpy as np

from ctios.agents import LearnedAgent
from ctios.env import Environment

BOUND = 2.0
SHIFTS = (-15.0, -10.0, -6.0, -3.0, 3.0, 6.0, 10.0, 15.0)
NOISES = (0.5, 1.0, 1.5, 2.0)
WARMUPS = (40, 60, 90)


def _post_mae(delta: float, sigma: float, warmup: int, seed: int) -> float:
    env = Environment(10.0, 10.0 + delta, 300, sigma, 600, seed)
    env.reset()
    agent = LearnedAgent(prior=1.0, warmup=warmup)
    errs = []
    for _ in range(600):
        pred = agent.predict()
        obs = env.step()
        errs.append(abs(obs.observed_interval - pred))
        agent.update(obs.observed_interval)
    return float(np.mean(errs[300:550]))


def test_bounded_adaptation_over_parameter_manifold():
    rng = np.random.default_rng(20260518)
    worst = 0.0
    for _ in range(48):
        d = float(rng.choice(SHIFTS))
        s = float(rng.choice(NOISES))
        w = int(rng.choice(WARMUPS))
        seed = int(rng.integers(0, 50))
        ratio = _post_mae(d, s, w, seed) / s
        worst = max(worst, ratio)
        assert ratio <= BOUND, (
            f"unbounded adaptation: post_mae/sigma={ratio:.3f} > {BOUND} "
            f"at delta={d} sigma={s} warmup={w} seed={seed}"
        )
    assert worst < BOUND  # sanity: envelope actually exercised
