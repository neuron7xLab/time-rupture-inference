from __future__ import annotations

from tools.check_cyber_hygiene_governance import main


def test_cyber_hygiene_governance_contract() -> None:
    assert main() == 0
