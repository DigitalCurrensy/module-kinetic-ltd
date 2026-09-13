"""Phasepin — grade a fabric-announced totalTimeInaccuracy.

The number is supplied by the operator / switch. This module does not
parse IEEE_C37_238 TLV bytes or run BMCA.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from platforms.phasepin.src.application.clock import PTP_GOOD_NS, TimePin

PROFILE_IN_SPEC_NS = 1_000  # 9-3 / C37.238 1 µs IED budget
Grade = Literal["missing", "profile_in_spec", "phasepin_ok", "too_wide"]


@dataclass(frozen=True)
class PinQuality:
    pin: TimePin
    total_time_inaccuracy_ns: int | None
    grade: Grade


def grade_inaccuracy(total_time_inaccuracy_ns: int | None) -> Grade:
    if total_time_inaccuracy_ns is None:
        return "missing"
    if total_time_inaccuracy_ns <= PROFILE_IN_SPEC_NS:
        return "profile_in_spec"
    if total_time_inaccuracy_ns < PTP_GOOD_NS:
        return "phasepin_ok"
    return "too_wide"


def attach_inaccuracy(pin: TimePin, total_time_inaccuracy_ns: int | None) -> PinQuality:
    return PinQuality(pin, total_time_inaccuracy_ns, grade_inaccuracy(total_time_inaccuracy_ns))
