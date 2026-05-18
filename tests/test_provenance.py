# SPDX-License-Identifier: MIT
"""Audit P1 #3 enforced: provenance manifest in sync, SPDX present,
external-scan status honestly OPEN (cannot be silently closed)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import provenance_attest as prov  # noqa: E402

SRC = Path(__file__).resolve().parents[1]


def test_manifest_in_sync_no_drift():
    assert prov.verify() == [], "provenance drift — run scripts/provenance_attest.py --write"


def test_every_python_source_has_spdx():
    missing = [
        str(p.relative_to(SRC))
        for g in ("src/ctios/*.py", "scripts/*.py")
        for p in SRC.glob(g)
        if "SPDX-License-Identifier: MIT" not in p.read_text()
    ]
    assert not missing, f"missing SPDX: {missing}"


def test_external_scan_status_stays_open():
    import json

    rec = json.loads((SRC / "provenance_manifest.json").read_text())
    assert rec["external_similarity_scan"].startswith("OPEN"), (
        "external similarity scan must remain honestly OPEN — no silent "
        "no-plagiarism claim"
    )
