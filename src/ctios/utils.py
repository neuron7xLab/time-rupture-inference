"""Shared primitives: hashing, RNG discipline, lock-hash."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_files(paths: Iterable[Path]) -> str:
    """Order-independent content hash over a set of files."""
    h = hashlib.sha256()
    for p in sorted(paths, key=lambda x: str(x)):
        h.update(p.as_posix().encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def project_source_hash() -> str:
    files = sorted((ROOT / "src").rglob("*.py")) + sorted((ROOT / "configs").rglob("*.yaml"))
    return sha256_files(files)


def prereg_hash() -> str:
    files = sorted((ROOT / "prereg").glob("*.yaml"))
    return sha256_files(files)


def dependency_lock_hash() -> str:
    out = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True, check=False
    ).stdout
    return sha256_text(out)


def git_commit() -> str:
    r = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    return r.stdout.strip() or "UNINITIALIZED"


def git_commit_epoch() -> int:
    r = subprocess.run(
        ["git", "-C", str(ROOT), "show", "-s", "--format=%ct", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        return int(r.stdout.strip())
    except ValueError:
        return -1


def rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def jdump(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=float)
