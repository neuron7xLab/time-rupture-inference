from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.cyber_hygiene_contract import EVIDENCE_PATH, POLICY_DOC_PATH


def main() -> int:
    report = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    doc = POLICY_DOC_PATH.read_text(encoding="utf-8")

    problems: list[str] = []

    mode = report.get("mode")
    if mode not in {"must_exist", "must_not_exist"}:
        problems.append(f"invalid report.mode: {mode!r}")

    if mode == "must_not_exist":
        if '`mode: "must_not_exist"`' not in doc:
            problems.append('policy doc missing merge criterion: mode must_not_exist')
        if '`present_disallowed_classes: []`' not in doc:
            problems.append('policy doc missing merge criterion: present_disallowed_classes []')
    if mode == "must_exist":
        if '`missing_required_classes: []`' not in doc:
            problems.append('policy doc missing merge criterion: missing_required_classes []')

    if '`dropped_invalid_rows: 0`' not in doc:
        problems.append('policy doc missing merge criterion: dropped_invalid_rows 0')

    if problems:
        print("CYBER HYGIENE GOVERNANCE — FAIL")
        for p in problems:
            print(f"- {p}")
        return 1

    print("CYBER HYGIENE GOVERNANCE — PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
