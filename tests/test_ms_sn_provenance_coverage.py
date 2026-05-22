# SPDX-License-Identifier: MIT
from __future__ import annotations

import json
from pathlib import Path

REQUIRED_PROVENANCE_PATHS = {
    "configs/ms_sn_v1_0_0.yaml",
    "scripts/ms_sn_evidence.py",
}

REQUIRED_LOAD_BEARING_PATHS = {
    "README_PACKAGE.md",
    "docs/research/MS_SN_v1_0_0_CI_GATE.md",
    "docs/research/MS_SN_v1_0_0_EVIDENCE_SCHEMA.md",
    "docs/research/MS_SN_v1_0_0_PREREG_LOCK.md",
    "docs/research/MS_SN_v1_0_0_TEST_PROTOCOL.md",
    "docs/research/NCTP_ROLE_DYNAMICS_BOUNDARY.md",
    "docs/research/PR74_CONTEXT.md",
    "evidence/ms_sn_v1_0_0/manifest.json",
}


def test_ms_sn_core_files_are_represented_in_provenance_manifest() -> None:
    manifest = json.loads(Path("provenance_manifest.json").read_text(encoding="utf-8"))
    paths = {entry["path"] for entry in manifest["files"]}
    missing = sorted(REQUIRED_PROVENANCE_PATHS - paths)
    assert not missing, "MS-SN core files missing from provenance_manifest.json:\n" + "\n".join(missing)


def test_ms_sn_load_bearing_docs_and_evidence_exist() -> None:
    missing = sorted(path for path in REQUIRED_LOAD_BEARING_PATHS if not Path(path).exists())
    assert not missing, "MS-SN load-bearing files missing from repository:\n" + "\n".join(missing)
