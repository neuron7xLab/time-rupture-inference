import numpy as np

from ctios.neural_agent import NeuralTemporalAdapter


def _run(seed: int, stream: np.ndarray) -> list[tuple[float, float, float]]:
    m = NeuralTemporalAdapter(seed=seed)
    return [(s.prediction, s.error, s.uncertainty) for s in [m.step(float(x)) for x in stream]]


def test_same_seed_same_stream_identical_outputs():
    stream = np.random.default_rng(0).normal(10.0, 1.0, 128)
    assert _run(7, stream) == _run(7, stream)


def test_same_seed_same_stream_identical_with_bounded_history():
    stream = np.random.default_rng(1).normal(9.0, 1.2, 256)
    def run():
        m = NeuralTemporalAdapter(seed=11, max_history=8)
        out = []
        for x in stream:
            step = m.step(float(x))
            out.append((step.prediction, step.error, step.uncertainty))
        return out
    assert run() == run()
