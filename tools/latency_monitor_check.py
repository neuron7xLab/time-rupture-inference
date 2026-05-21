# SPDX-License-Identifier: MIT
from __future__ import annotations

from ctios.observability.latency_monitor import BPF_PROGRAM, LatencyMonitorConfig, measure_call_ns


def main() -> int:
    assert "uprobe_run_enter" in BPF_PROGRAM
    assert "uprobe_run_exit" in BPF_PROGRAM
    assert "latency_us" in BPF_PROGRAM

    cfg = LatencyMonitorConfig(binary_path="python3")
    assert cfg.symbol == "_run"
    assert cfg.latency_budget_ms_p99 == 20.0

    value, elapsed = measure_call_ns(lambda x: x + 1, 41)
    assert value == 42
    assert elapsed >= 0

    for bad_path in ("",):
        try:
            LatencyMonitorConfig(binary_path=bad_path)
        except ValueError:
            pass
        else:
            raise AssertionError("empty binary_path must fail")

    print("LATENCY_MONITOR_CHECK PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
