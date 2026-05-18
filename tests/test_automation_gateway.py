# SPDX-License-Identifier: MIT
import json
from pathlib import Path

from ctios.automation import AutomationContract, run_automation


def test_automation_gateway_green(tmp_path: Path) -> None:
    out = tmp_path / "status.json"
    channels = (
        AutomationContract(name="ok", command=("python", "-c", "raise SystemExit(0)")),
    )
    code = run_automation(channels, out)
    payload = json.loads(out.read_text(encoding="utf-8"))

    assert code == 0
    assert payload["status"] == "green"
    assert payload["started_utc"].endswith("+00:00")
    assert payload["results"][0]["ok"] is True


def test_automation_gateway_red(tmp_path: Path) -> None:
    out = tmp_path / "status.json"
    channels = (
        AutomationContract(name="boom", command=("python", "-c", "raise SystemExit(2)")),
    )
    code = run_automation(channels, out)
    payload = json.loads(out.read_text(encoding="utf-8"))

    assert code == 1
    assert payload["status"] == "red"
    assert payload["results"][0]["returncode"] == 2
