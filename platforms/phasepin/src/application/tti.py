"""Phasepin TTI — operator/switch announced totalTimeInaccuracy.

An integer nanosecond bound. Not a C37.238 TLV parser. Not BMCA.
clock.py and inaccuracy.py stay frozen. Module Kinetic Ltd.
"""
from __future__ import annotations


class TtiError(Exception):
    code = "tti_error"


class MissingTti(TtiError):
    code = "missing_tti"


class BadTti(TtiError):
    code = "bad_tti"


def tti_from_announced(total_time_inaccuracy_ns) -> int:
    if total_time_inaccuracy_ns is None or total_time_inaccuracy_ns == "":
        raise MissingTti("switch did not announce TTI")
    try:
        value = int(total_time_inaccuracy_ns)
    except (TypeError, ValueError) as exc:
        raise BadTti("TTI must be an integer nanosecond bound") from exc
    if value < 0:
        raise BadTti("TTI cannot be negative")
    return value
