"""Fiberlock QBER tape — a measured row, not a constant.

session.py stays frozen. Missing or QBER ≥ 0.11 is refused here too.
Module Kinetic Ltd.
"""
from __future__ import annotations

from platforms.fiberlock.src.application.session import QBER_MAX


class TapeError(Exception):
    code = "tape_error"


class MissingQber(TapeError):
    code = "missing_qber"


class BadQber(TapeError):
    code = "bad_qber"


def qber_from_tape(row: dict) -> float:
    if row is None or row.get("qber") in (None, ""):
        raise MissingQber("span tape has no qber")
    try:
        qber = float(row["qber"])
    except (TypeError, ValueError) as exc:
        raise BadQber("qber must be a number") from exc
    if qber < 0.0:
        raise BadQber("qber cannot be negative")
    if qber >= QBER_MAX:
        raise BadQber(f"qber {qber} exceeds {QBER_MAX}")
    return qber
