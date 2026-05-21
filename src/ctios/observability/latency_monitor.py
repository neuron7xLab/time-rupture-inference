# SPDX-License-Identifier: MIT
"""Optional runtime latency monitor scaffold.

The monitor is isolated from simulation math. Kernel-backed collection is
optional and explicit; development and CI use the deterministic userspace timer.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from time import perf_counter_ns
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

BPF_PROGRAM = r"""
#include <uapi/linux/ptrace.h>
struct start_key_t { u32 pid; };
BPF_HASH(start_ns, struct start_key_t, u64);
BPF_HISTOGRAM(latency_us);

int uprobe_run_enter(struct pt_regs *ctx) {
    struct start_key_t key = { .pid = bpf_get_current_pid_tgid() >> 32 };
    u64 ts = bpf_ktime_get_ns();
    start_ns.update(&key, &ts);
    return 0;
}

int uprobe_run_exit(struct pt_regs *ctx) {
    struct start_key_t key = { .pid = bpf_get_current_pid_tgid() >> 32 };
    u64 *start = start_ns.lookup(&key);
    if (!start) { return 0; }
    u64 delta_us = (bpf_ktime_get_ns() - *start) / 1000;
    latency_us.increment(bpf_log2l(delta_us));
    start_ns.delete(&key);
    return 0;
}
"""


@dataclass(frozen=True)
class LatencyMonitorConfig:
    binary_path: str
    symbol: str = "_run"
    latency_budget_ms_p99: float = 20.0

    def __post_init__(self) -> None:
        if not self.binary_path:
            raise ValueError("binary_path must be non-empty")
        if not self.symbol:
            raise ValueError("symbol must be non-empty")
        if self.latency_budget_ms_p99 <= 0.0:
            raise ValueError("latency_budget_ms_p99 must be positive")


def deploy_kernel_latency_monitor(config: LatencyMonitorConfig) -> object:
    """Attach uprobes when the host has BCC support.

    The function fails closed when optional kernel tooling is unavailable.
    """

    try:
        from bcc import BPF  # type: ignore[import-not-found]
    except Exception as exc:  # pragma: no cover - host dependent
        raise RuntimeError("bcc is not available in this environment") from exc

    bpf = BPF(text=BPF_PROGRAM)
    bpf.attach_uprobe(name=config.binary_path, sym=config.symbol, fn_name="uprobe_run_enter")
    bpf.attach_uretprobe(
        name=config.binary_path,
        sym=config.symbol,
        fn_name="uprobe_run_exit",
    )
    return bpf


def measure_call_ns(fn: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> tuple[R, int]:
    """Measure one function call with a deterministic userspace timer."""

    start = perf_counter_ns()
    result = fn(*args, **kwargs)
    elapsed = perf_counter_ns() - start
    if elapsed < 0:
        raise RuntimeError("monotonic timer returned negative elapsed time")
    return result, elapsed
