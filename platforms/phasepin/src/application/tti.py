"""The clock error must be a whole number of nanoseconds.

inaccuracy.py grades that number. A missing or negative number is refused.
"""
from __future__ import annotations


class TtiError(Exception):
    code = "tti_error"


class MissingTti(TtiError):
    code = "missing_tti"


class BadTti(TtiError):
    code = "bad_tti"


def tti_from_operator(total_time_inaccuracy_ns) -> int:
    if total_time_inaccuracy_ns is None or total_time_inaccuracy_ns == "":
        raise MissingTti("switch did not announce totalTimeInaccuracy")
    try:
        value = int(total_time_inaccuracy_ns)
    except (TypeError, ValueError) as exc:
        raise BadTti("TTI must be an integer nanosecond bound") from exc
    if value < 0:
        raise BadTti("TTI cannot be negative")
    return value
