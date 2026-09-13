"""Fiberlock — CV-QKD wrap on spans that carry Unitcommit setpoints.

Not a plant sensor. Operator object is a key session and a QBER tape.
"""
from __future__ import annotations

from dataclasses import dataclass

QBER_MAX = 0.11
MIN_KEY_BITS = 128


class WrapRefused(Exception):
    code = "wrap_refused"
    http_status = 422

    def __init__(self, message: str) -> None:
        super().__init__(message)


@dataclass(frozen=True)
class KeySession:
    span_id: str
    session_id: str
    qber: float
    key_bits: int
    wrapped: bool


def wrap_control_path(span_id: str, session_id: str, qber: float, key_bits: int) -> KeySession:
    if qber >= QBER_MAX:
        raise WrapRefused(f"QBER {qber} exceeds {QBER_MAX}")
    if key_bits < MIN_KEY_BITS:
        raise WrapRefused("key material too short to wrap a setpoint")
    return KeySession(span_id, session_id, qber, key_bits, wrapped=True)


def wrap_from_pin(span_id: str, session_id: str, qber: float, key_bits: int, pin) -> KeySession:
    if getattr(pin, "time_source", None) == "gps_peer":
        raise WrapRefused("Fiberlock will not wrap on a gps_peer pin")
    return wrap_control_path(span_id, session_id, qber, key_bits)
