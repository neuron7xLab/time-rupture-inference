# SPDX-License-Identifier: MIT
"""Derive v8.1 trigger frequency BEFORE the oracle diagnostic. Emits the
precheck artifact. If precheck fails, the diagnostic must not run."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from ctios.diagnostics.trigger_frequency import derive  # noqa: E402

CFG = yaml.safe_load((ROOT / "configs" / "v8_1_scalar_inexpressible_env.yaml").read_text())


def main() -> int:
    d = derive(CFG)
    art = ROOT / "artifacts" / "v8_1"
    art.mkdir(parents=True, exist_ok=True)
    (art / "trigger_frequency_precheck.json").write_text(
        json.dumps(d.as_dict(), indent=2)
    )
    status = "PASS" if d.frequency_precheck_passed else "RED_PRECHECK"
    print(f"v8.1 trigger-frequency precheck: {status}")
    print(json.dumps(d.as_dict(), indent=2))
    if not d.frequency_precheck_passed:
        (ROOT / "evidence" / "RED_PRECHECK_v8_1.md").write_text(
            "# RED_PRECHECK — v8.1 (pinned, not erased)\n\n"
            "Derived trigger frequency failed the pinned minimums BEFORE "
            "the oracle diagnostic. The diagnostic is NOT run. Preserve; "
            "no parameter tuned.\n\n"
            f"```json\n{json.dumps(d.as_dict(), indent=2)}\n```\n"
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
