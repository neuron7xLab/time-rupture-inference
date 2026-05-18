# SPDX-License-Identifier: MIT
"""ctios.predictive_simulation — verified predictive-error regime inference.

The object under test is the difference between a *verified simulation*
and an *imitation*:

  * **simulation** — an internal predictive cycle (predict → observe →
    error → self-update) that infers a hidden regime rupture τ₀→τ₁
    purely from its OWN prediction error, never from any exogenous
    change signal. It is admitted only because a falsifier was run.
  * **imitation** — surface mimicry (echo / last-value lookup) with no
    internal predictive model and no error-driven update.

The falsifier (``simulation_vs_imitation``) is fail-closed: the
simulation must (a) detect the rupture from its own error statistic,
(b) beat the imitation post-rupture by a pinned margin, (c) carry a
structural no-leakage invariant (it is never shown τ₀, τ₁ or T*),
(d) be deterministic. Otherwise the verdict is not GREEN.

No biological or cognition claim is made anywhere: this is a functional
dynamical contract, scoped to a synthetic hidden-rupture stream.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from ctios.falsify import HypothesisSpec, Verdict, falsify

_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class RuptureStream:
    """A hidden inter-event interval that ruptures τ₀→τ₁ at an unseen
    step. The observer is given ONLY ``obs``; ``tau0/tau1/t_star`` exist
    solely to score the run and are never passed to any agent."""

    obs: np.ndarray
    tau0: float
    tau1: float
    t_star: int
    sigma: float

    @staticmethod
    def make(seed: int, n: int = 600) -> RuptureStream:
        rng = np.random.default_rng(seed)
        tau0, tau1, sigma = 10.0, 4.0, 1.0
        t_star = n // 2
        clean = np.where(np.arange(n) < t_star, tau0, tau1).astype(np.float64)
        obs = clean + rng.normal(0.0, sigma, n)
        return RuptureStream(obs, tau0, tau1, t_star, sigma)

    @staticmethod
    def make_null(seed: int, n: int = 600) -> RuptureStream:
        """No-rupture control: a detector firing here is a false alarm.
        t_star = n (never) by construction."""
        rng = np.random.default_rng(10_000 + seed)
        obs = 10.0 + rng.normal(0.0, 1.0, n)
        return RuptureStream(obs, 10.0, 10.0, n, 1.0)


@dataclass
class PredictiveCycle:
    """Internal predictive model: one scalar estimate updated by its own
    error, with a cumulative-error trigger that flags a regime change
    from the error signal alone (Page-Hinkley style, warmed up)."""

    gain: float = 0.18
    warmup: int = 40
    ph_lambda: float = 8.0
    ph_delta: float = 0.05
    m: float = field(default=0.0)
    _mean: float = field(default=0.0)
    _cum: float = field(default=0.0)
    _min: float = field(default=0.0)
    _n: int = field(default=0)
    detected_at: int = field(default=-1)

    def step(self, o: float, t: int) -> float:
        pred = self.m if self._n > 0 else o
        err = o - pred
        self.m = pred + self.gain * err
        self._n += 1
        # Page-Hinkley: estimate the in-control |error| mean ONLY during
        # warmup, then freeze it. Continuing to update the reference past
        # the change would absorb the rupture into the baseline (a
        # classic PH misuse). No exogenous regime signal is consulted.
        ae = abs(err)
        if self._n <= self.warmup:
            self._mean += (ae - self._mean) / self._n
            if self._n == self.warmup:  # begin monitoring on a clean ref
                self._cum = 0.0
                self._min = 0.0
            return float(pred)
        self._cum += ae - self._mean - self.ph_delta
        self._min = min(self._min, self._cum)
        if (
            self.detected_at < 0
            and t >= self.warmup
            and self._cum - self._min > self.ph_lambda
        ):
            self.detected_at = t
        return float(pred)


class ImitationBaseline:
    """Surface mimicry: echoes the previous observation. No predictive
    model, no error-driven update, no change statistic — it cannot
    detect a rupture because it never forms an expectation to violate."""

    def __init__(self) -> None:
        self._last: float | None = None
        self.detected_at: int = -1

    def step(self, o: float, t: int) -> float:
        pred = self._last if self._last is not None else o
        self._last = o
        return float(pred)


class ClairvoyantEchoProbe(ImitationBaseline):
    """ADVERSARIAL. A surface echo with NO predictive model that
    hard-codes detection at t_star. It can only know t_star by being
    handed it — so the verdict run records leakage>0 for this arm and
    the leakage check forces RED. This blocks the false GREEN a naive
    detect-rate-only gate would grant."""

    def __init__(self, t_star: int) -> None:
        super().__init__()
        self._leak_t = int(t_star)  # the leak: it received t_star

    def step(self, o: float, t: int) -> float:
        if t >= self._leak_t and self.detected_at < 0:
            self.detected_at = t
        return super().step(o, t)


def _post_mae(pred: np.ndarray, stream: RuptureStream) -> float:
    s = stream.t_star
    return float(np.mean(np.abs(pred[s:] - stream.obs[s:])))


def _run(agent: PredictiveCycle | ImitationBaseline,
         stream: RuptureStream) -> tuple[np.ndarray, int]:
    preds = np.empty_like(stream.obs)
    for t, o in enumerate(stream.obs):
        preds[t] = agent.step(float(o), t)
    return preds, agent.detected_at


def simulation_vs_imitation(
    seeds: int = 12,
    *,
    leak_arm: bool = False,
) -> dict[str, float]:
    """Produce exactly the pre-registered metric set
    (prereg/predictive_simulation.yaml). Window for a detection hit:
    [t_star, t_star + 0.2*n]. MAE / separation are report-only and are
    NOT gated. ``leak_arm`` swaps the imitation for the clairvoyant
    leak probe — the kill test: it MUST drive leakage>0 (verdict RED)."""
    sim_mae, imit_mae = [], []
    sim_hits = imit_hits = null_fa = 0
    leakage = 0.0
    for sd in range(seeds):
        st = RuptureStream.make(sd)
        n = st.obs.size
        tol = int(0.2 * n)
        ps, sd_at = _run(PredictiveCycle(), st)
        imit: ImitationBaseline
        if leak_arm:
            imit = ClairvoyantEchoProbe(st.t_star)
            leakage = 1.0  # it was handed t_star — by definition leakage
        else:
            imit = ImitationBaseline()
        pi, id_at = _run(imit, st)
        sim_mae.append(_post_mae(ps, st))
        imit_mae.append(_post_mae(pi, st))
        if 0 <= sd_at - st.t_star <= tol:
            sim_hits += 1
        if 0 <= id_at - st.t_star <= tol:
            imit_hits += 1
        # null (no-rupture) stream: any predictive-cycle trigger is a
        # false alarm.
        nst = RuptureStream.make_null(sd)
        _, nd_at = _run(PredictiveCycle(), nst)
        if nd_at >= 0:
            null_fa += 1
    return {
        "sim_post_mae": float(np.mean(sim_mae)),
        "imit_post_mae": float(np.mean(imit_mae)),
        "separation": float(np.mean(imit_mae) - np.mean(sim_mae)),
        "sim_detect_rate": sim_hits / seeds,
        "imit_detect_rate": imit_hits / seeds,
        "sim_null_false_alarm": null_fa / seeds,
        "leakage": leakage,
    }


def _candidate(_t: dict[str, float]) -> dict[str, float]:
    return simulation_vs_imitation()


def _negative_control(_t: dict[str, float]) -> dict[str, float]:
    # The clairvoyant-leak arm: leakage>0 -> MUST fail the leakage check
    # (this is the pre-registered kill test wired as the control).
    return simulation_vs_imitation(leak_arm=True)


def verdict() -> Verdict:
    """Run the PINNED falsifier exactly once. The spec hash is recorded;
    no threshold is edited after this. A RED is sealed, not nudged."""
    spec = HypothesisSpec.load(_ROOT / "prereg" / "predictive_simulation.yaml")
    return falsify(
        spec,
        _candidate,
        negative_control=_negative_control,
        evidence_dir=_ROOT / "evidence",
        prereg_dir=_ROOT / "prereg",
    )


def main() -> int:
    v = verdict()
    print(f"PREDICTIVE-SIMULATION :: {v.status}  [{v.hid}]")
    for k, ok in {**v.checks, **v.battery}.items():
        print(f"  [{'OK' if ok else 'XX'}] {k}")
    import json

    print(f"spec_sha256={v.spec_sha256[:16]}  metrics={json.dumps(v.metrics)}")
    if v.reasons:
        print("reasons: " + "; ".join(v.reasons))
    return 0 if v.status in ("GREEN", "PARTIAL") else 1


if __name__ == "__main__":
    raise SystemExit(main())
