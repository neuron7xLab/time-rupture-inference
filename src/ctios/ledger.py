"""Append-only evidence ledger (one JSON object per line)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from ctios.utils import (
    dependency_lock_hash,
    git_commit,
    prereg_hash,
    project_source_hash,
)


def provenance() -> dict[str, Any]:
    import sys

    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_commit": git_commit(),
        "python_version": sys.version.split()[0],
        "dependency_lock_hash": dependency_lock_hash(),
        "config_source_hash": project_source_hash(),
        "prereg_hash": prereg_hash(),
    }


def append(ledger_path: Path, record: dict[str, Any]) -> None:
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True, default=float) + "\n")
