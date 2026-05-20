import inspect
from pathlib import Path

import numpy as np

from ctios.neural_agent import NeuralTemporalAdapter


def test_source_scan_rejects_hidden_schedule_tokens_in_step_signature():
    src = inspect.getsource(NeuralTemporalAdapter.step)
    sig_line = src.splitlines()[0]
    for token in ("tau0", "tau1", "t_star", "regime_label", "hidden_context"):
        assert token not in sig_line


def test_file_has_no_hidden_context_identifier_usage():
    txt = Path("src/ctios/neural_agent.py").read_text()
    for token in ("hidden_context", "regime_label", "tau0", "tau1", "t_star"):
        assert f"{token}=" not in txt


def test_causal_mask_blocks_future_attention():
    m = NeuralTemporalAdapter(seed=5)
    for x in (10.0, 11.0, 12.0, 13.0):
        m.step(x)
    _, weights, _ = m._forward_from_history()
    assert np.allclose(np.triu(weights, k=1), 0.0)


def test_prefix_prediction_invariant_to_future_suffix():
    prefix = [10.0, 9.5, 10.2, 9.8]
    suffix_a = [5.0, 5.0, 5.0]
    suffix_b = [20.0, 20.0, 20.0]

    def pred_after_prefix(suffix: list[float]) -> float:
        m = NeuralTemporalAdapter(seed=13)
        for x in prefix:
            m.step(x)
        p = m.predict()
        for x in suffix:
            m.step(x)
        return p

    assert pred_after_prefix(suffix_a) == pred_after_prefix(suffix_b)
