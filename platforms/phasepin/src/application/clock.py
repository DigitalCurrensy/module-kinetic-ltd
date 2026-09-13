"""Phasepin — CSAC + PTP pin time. GPS is a peer sensor, never source of truth."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

TimeSource = Literal["csac", "ptp", "holdover", "gps_peer"]
PTP_GOOD_NS = 1_000_000
HOLDOVER_LIMIT_S = 4 * 3600


@dataclass(frozen=True)
class TimePin:
    observed_at: str
    offset_ns: int
    holdover_s: int
    time_source: TimeSource
    gps_peer_offset_ns: int | None


def pin_time(
    *,
    observed_at: str,
    csac_ok: bool,
    ptp_offset_ns: int | None,
    holdover_s: int,
    gps_offset_ns: int | None,
) -> TimePin:
    if csac_ok:
        return TimePin(observed_at, 0, holdover_s, "csac", gps_offset_ns)
    if ptp_offset_ns is not None and abs(ptp_offset_ns) < PTP_GOOD_NS:
        return TimePin(observed_at, ptp_offset_ns, holdover_s, "ptp", gps_offset_ns)
    if holdover_s < HOLDOVER_LIMIT_S:
        return TimePin(observed_at, ptp_offset_ns or 0, holdover_s, "holdover", gps_offset_ns)
    return TimePin(observed_at, gps_offset_ns or 0, holdover_s, "gps_peer", gps_offset_ns)
