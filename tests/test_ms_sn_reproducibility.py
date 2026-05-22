# SPDX-License-Identifier: MIT
from __future__ import annotations

import importlib.util
import json
from pathlib import Path


def _load_ms_sn_evidence_module():
    module_path = Path("scripts/ms_sn_evidence.py")
    spec = importlib.util.spec_from_file_location("ms_sn_evidence", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load ms_sn_evidence module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_canonical_json_and_hash_are_deterministic() -> None:
    mod = _load_ms_sn_evidence_module()
    payload = {"b": 1, "a": [3, 2, 1]}
    out1 = mod.canonical_json(payload)
    out2 = mod.canonical_json({"a": [3, 2, 1], "b": 1})
    assert out1 == out2
    assert mod.sha256_bytes(out1) == mod.sha256_bytes(out2)
    assert json.loads(out1.decode("utf-8")) == {"a": [3, 2, 1], "b": 1}
