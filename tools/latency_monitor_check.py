# SPDX-License-Identifier: MIT
from __future__ import annotations

import math

from ctios.observability.latency_monitor import BPF_PROGRAM, LatencyMonitorConfig, measure_call_ns


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def expect_value_error(fn, message: str) -> None:
    try:
        fn()
    except ValueError:
        return
    raise AssertionError(message)


def expect_type_error(fn, message: str) -> None:
    try:
        fn()
    except TypeError:
        return
    raise AssertionError(message)


def main() -> int:
    require("uprobe_run_enter" in BPF_PROGRAM, "BPF entry probe missing")
    require("uprobe_run_exit" in BPF_PROGRAM, "BPF exit probe missing")
    require("latency_us" in BPF_PROGRAM, "latency histogram missing")

    cfg = LatencyMonitorConfig(binary_path="python3")
    require(cfg.symbol == "_run", "default symbol drifted")
    require(cfg.latency_budget_ms_p99 == 20.0, "default latency budget drifted")

    value, elapsed = measure_call_ns(lambda x: x + 1, 41)
    require(value == 42, "timed call returned wrong value")
    require(elapsed >= 0, "elapsed time must be non-negative")

    expect_value_error(lambda: LatencyMonitorConfig(binary_path=""), "empty path must fail")
    expect_value_error(lambda: LatencyMonitorConfig(binary_path="   "), "blank path must fail")
    expect_value_error(
        lambda: LatencyMonitorConfig(binary_path="python3", symbol=""),
        "empty symbol must fail",
    )
    expect_value_error(
        lambda: LatencyMonitorConfig(binary_path="python3", symbol="   "),
        "blank symbol must fail",
    )
    expect_value_error(
        lambda: LatencyMonitorConfig(binary_path="python3", latency_budget_ms_p99=0.0),
        "zero latency budget must fail",
    )
    expect_value_error(
        lambda: LatencyMonitorConfig(binary_path="python3", latency_budget_ms_p99=math.inf),
        "infinite latency budget must fail",
    )
    expect_value_error(
        lambda: LatencyMonitorConfig(binary_path="python3", latency_budget_ms_p99=math.nan),
        "nan latency budget must fail",
    )
    expect_type_error(lambda: measure_call_ns(42), "non-callable timer target must fail")

    print("LATENCY_MONITOR_CHECK PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
