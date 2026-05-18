# SPDX-License-Identifier: MIT
"""Contract: the v8.2 lineage trains no learned model."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRCS = [
    ROOT / "scripts" / "run_v8_2_trigger_scoped_diagnostic.py",
    ROOT / "src" / "ctios" / "diagnostics" / "oracle_channel_analysis.py",
    ROOT / "src" / "ctios" / "diagnostics" / "carrier_decomposition.py",
]
BANNED = ("torch", "tensorflow", "keras", "GRU(", "LSTM(", ".backward(",
          "optimizer", "nn.Module", "Reservoir", "train(")


def test_no_learned_model_symbols():
    for p in SRCS:
        s = p.read_text()
        for b in BANNED:
            assert b not in s, f"{p.name} references learned-model symbol {b!r}"
