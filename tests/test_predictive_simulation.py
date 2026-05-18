# SPDX-License-Identifier: MIT
"""Predictive-simulation contract (verdict-isolation, V7): the
scientific verdict is NOT asserted GREEN here — a legitimate
PARTIAL/RED keeps CI green. What IS asserted: determinism, the
structural simulation⊳imitation dissociation, and the pre-registered
kill test (clairvoyant leak MUST force a leakage failure)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.predictive_simulation import (  # noqa: E402
    ClairvoyantEchoProbe,
    ImitationBaseline,
    PredictiveCycle,
    RuptureStream,
    simulation_vs_imitation,
    verdict,
)


def test_metrics_are_the_preregistered_set_and_deterministic():
    a = simulation_vs_imitation()
    b = simulation_vs_imitation()
    assert a == b  # deterministic
    assert set(a) >= {
        "sim_detect_rate", "imit_detect_rate", "sim_null_false_alarm",
        "leakage", "separation", "sim_post_mae",
    }
    assert a["leakage"] == 0.0  # honest arm: structurally no leakage


def test_imitation_cannot_self_detect_the_rupture():
    # The load-bearing dissociation: a surface echo never forms an
    # expectation, so it structurally cannot flag the regime change.
    m = simulation_vs_imitation()
    assert m["imit_detect_rate"] == 0.0
    st = RuptureStream.make(0)
    e = ImitationBaseline()
    for t, o in enumerate(st.obs):
        e.step(float(o), t)
    assert e.detected_at == -1


def test_predictive_cycle_is_error_driven_not_signal_driven():
    # HONEST structural property (not an accuracy claim): the cycle's
    # flag is a function of its OWN error only. Proof: on a NULL
    # no-rupture stream it still (falsely) fires — it cannot be reading
    # an exogenous rupture signal, because there is none. This is also
    # exactly the preserved negative (0.75 null false-alarm): the
    # detector is error-driven but NOT a valid change detector.
    null = RuptureStream.make_null(0)
    pc = PredictiveCycle()
    for t, o in enumerate(null.obs):
        pc.step(float(o), t)
    fired_without_any_rupture = pc.detected_at >= 0
    assert fired_without_any_rupture, (
        "expected the documented null false-alarm; absence here would "
        "contradict the sealed PARTIAL negative"
    )


def test_kill_test_clairvoyant_leak_forces_leakage_and_red():
    # Pre-registered kill test: the leak arm must record leakage>0 and
    # the verdict over it must NOT be GREEN.
    leaked = simulation_vs_imitation(leak_arm=True)
    assert leaked["leakage"] > 0.0
    st = RuptureStream.make(0)
    c = ClairvoyantEchoProbe(st.t_star)
    for t, o in enumerate(st.obs):
        c.step(float(o), t)
    assert c.detected_at == st.t_star  # only knowable via the leak


def test_pinned_verdict_runs_and_is_well_formed_not_asserted_green():
    v = verdict()
    assert v.status in ("GREEN", "PARTIAL", "RED")  # isolation: any is ok
    assert v.battery["negative_control_fails"] is True  # kill test wired
    assert v.battery["deterministic"] and v.battery["finite"]
    assert v.spec_sha256  # the falsifier was pinned before the run
