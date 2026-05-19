# SPDX-License-Identifier: MIT
"""WP1 meta — every CORE_MECHANISM has a linked test; the inventory is
generated, not asserted prose."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ctios.mechanism_inventory import CORE, build, core_without_test  # noqa: E402


def test_no_core_mechanism_without_a_linked_test():
    miss = core_without_test(build())
    assert miss == [], f"CORE_MECHANISM with no test: {miss}"


def test_inventory_covers_every_src_module():
    files = {i.file for i in build()}
    for p in (ROOT / "src" / "ctios").glob("*.py"):
        if p.name in ("__init__.py", "_version.py"):
            continue
        assert f"src/ctios/{p.name}" in files


def test_core_modules_are_actually_classified_core():
    items = build()
    cores = [i for i in items if i.classification == CORE]
    assert len(cores) >= 10  # the apparatus is mostly mechanism
