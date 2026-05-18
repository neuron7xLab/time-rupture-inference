# SPDX-License-Identifier: MIT
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRCS = [
    ROOT / "scripts" / "run_v8_4_rederived_diagnostic.py",
    ROOT / "src" / "ctios" / "envs" / "latent_context_temporal_rupture_v8_4.py",
]
BANNED = ("torch", "tensorflow", "keras", "GRU(", "LSTM(", ".backward(",
          "optimizer", "nn.Module", "Reservoir", "train(")


def test_no_learned_model_symbols():
    for p in SRCS:
        s = p.read_text()
        for b in BANNED:
            assert b not in s, f"{p.name} references {b!r}"
