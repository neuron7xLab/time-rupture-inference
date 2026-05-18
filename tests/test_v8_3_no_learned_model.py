# SPDX-License-Identifier: MIT
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRCS = [
    ROOT / "scripts" / "run_v8_3_correct_history_diagnostic.py",
    ROOT / "src" / "ctios" / "oracles" / "correct_history_oracle.py",
    ROOT / "src" / "ctios" / "diagnostics" / "causal_bound.py",
]
BANNED = ("torch", "tensorflow", "keras", "GRU(", "LSTM(", ".backward(",
          "optimizer", "nn.Module", "Reservoir", "train(")


def test_no_learned_model_symbols():
    for p in SRCS:
        s = p.read_text()
        for b in BANNED:
            assert b not in s, f"{p.name} references {b!r}"
