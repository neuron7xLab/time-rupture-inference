# SPDX-License-Identifier: MIT
from __future__ import annotations

import json

from scripts.ms_sn_evidence import canonical_json, sha256_bytes


def test_canonical_json_and_hash_are_deterministic() -> None:
    payload = {'b': 1, 'a': [3, 2, 1]}
    out1 = canonical_json(payload)
    out2 = canonical_json({'a': [3, 2, 1], 'b': 1})
    assert out1 == out2
    assert sha256_bytes(out1) == sha256_bytes(out2)
    assert json.loads(out1.decode('utf-8')) == {'a': [3, 2, 1], 'b': 1}
