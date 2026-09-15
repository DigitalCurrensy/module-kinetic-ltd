"""Fiberlock QBER tape — a measured row becomes a qber float.

session.py wrap law stays frozen. Module Kinetic Ltd.
"""
from __future__ import annotations


class TapeError(Exception):
    code = "tape_error"


class MissingQber(TapeError):
    code = "missing_qber"


class BadQber(TapeError):
    code = "bad_qber"


def qber_from_tape(row: dict) -> float:
    raw = row.get("qber", row.get("qber_rolling"))
    if raw is None or raw == "":
        raise MissingQber("tape row missing qber")
    try:
        value = float(raw)
    except (TypeError, ValueError) as exc:
        raise BadQber("qber must be a float") from exc
    if value < 0.0:
        raise BadQber("qber cannot be negative")
    return value
