# SPDX-License-Identifier: MIT
"""Top-level NCTP packet interface.

This module re-exports the already gated nested prototype contract. It exists as
an integration shim only; it does not expand runtime claims.
"""

from __future__ import annotations

from ctios.nctp_state.packet import TASK_SPECS, NCTPTaskSpec, validate_inference_packet

__all__ = ["NCTPTaskSpec", "TASK_SPECS", "validate_inference_packet"]
