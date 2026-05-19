# SPDX-License-Identifier: MIT
"""PR N — SBOM is valid SPDX-2.3, generated from the lock, no drift."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate_sbom as gs  # noqa: E402

SBOM = ROOT / "sbom.spdx.json"


def test_sbom_exists_and_valid_spdx():
    d = json.loads(SBOM.read_text())
    assert d["spdxVersion"] == "SPDX-2.3"
    assert d["creationInfo"]["created"]
    assert "documentNamespace" in d and "packages" in d


def test_sbom_matches_lock_no_drift():
    assert gs.verify() == []


def test_sbom_has_required_runtime_and_ci_deps():
    names = {p["name"].lower() for p in json.loads(SBOM.read_text())["packages"]}
    for req in ("numpy", "pyyaml", "pytest", "ruff", "mypy"):
        assert req in names, f"{req} absent from SBOM"


def test_sbom_package_set_does_not_exceed_lock(tmp_path, monkeypatch):
    doc = json.loads(SBOM.read_text())
    doc["packages"].append({
        "name": "ghost", "SPDXID": "SPDXRef-Package-ghost",
        "versionInfo": "9.9.9", "downloadLocation": "NOASSERTION",
        "licenseConcluded": "NOASSERTION", "filesAnalyzed": False,
    })
    f = tmp_path / "sbom.spdx.json"
    f.write_text(json.dumps(doc))
    monkeypatch.setattr(gs, "_SBOM", f)
    assert any("absent from lock" in p for p in gs.verify())


def test_regenerated_sbom_is_deterministic():
    a = json.dumps(gs.build()["packages"], sort_keys=True)
    b = json.dumps(gs.build()["packages"], sort_keys=True)
    assert a == b
