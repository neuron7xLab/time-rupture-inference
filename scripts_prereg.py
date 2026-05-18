"""Freeze the pre-registration: write sha_pin.txt over prereg+configs+src.

Run BEFORE the experiment and git-commit the result. The runner refuses
to go GREEN unless the pinned commit predates the run timestamp.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from ctios.utils import prereg_hash, project_source_hash  # noqa: E402

ROOT = Path(__file__).resolve().parent


def main() -> None:
    ph = prereg_hash()
    sh = project_source_hash()
    text = (
        f"prereg_hash={ph}\n"
        f"source_config_hash={sh}\n"
        f"pinned_at_utc={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n"
    )
    (ROOT / "prereg" / "sha_pin.txt").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
