"""Is the record signed?

The signature covers the meter, the start, the length, the energy, and the clock.
No key, no signature. A check with an empty or wrong key returns false.
A failed power check, a missing line wrap, a clock that is too wide, or GPS alone is not signed.
"""
from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from typing import Literal

TimeSource = Literal["csac", "ptp", "holdover", "gps_peer"]
SEALABLE = frozenset({"csac", "ptp", "holdover"})


class SealRefused(Exception):
    code = "seal_refused"


@dataclass(frozen=True)
class SignedInterval:
    meter_id: str
    interval_start: str
    interval_s: int
    watt_hours: float
    time_source: TimeSource
    signature: str
    kind: Literal["signed_meter"] = "signed_meter"


def _mac(
    meter_id: str,
    interval_start: str,
    interval_s: int,
    watt_hours: float,
    time_source: str,
    signing_key: str,
) -> str:
    material = f"{meter_id}|{interval_start}|{interval_s}|{watt_hours:.3f}|{time_source}".encode()
    return hmac.new(signing_key.encode(), material, hashlib.sha256).hexdigest()


def seal_interval(
    *,
    meter_id: str,
    interval_start: str,
    interval_s: int,
    watt_hours: float,
    time_source: TimeSource,
    signing_key: str,
) -> SignedInterval:
    if time_source not in SEALABLE:
        raise SealRefused("Photonseal will not seal an interval pinned only by gps_peer")
    if not signing_key:
        raise SealRefused("signing key missing")
    return SignedInterval(
        meter_id=meter_id,
        interval_start=interval_start,
        interval_s=interval_s,
        watt_hours=watt_hours,
        time_source=time_source,
        signature=_mac(meter_id, interval_start, interval_s, watt_hours, time_source, signing_key),
    )


def verify_interval(interval: SignedInterval, signing_key: str) -> bool:
    if not signing_key:
        return False
    expected = _mac(
        interval.meter_id,
        interval.interval_start,
        interval.interval_s,
        interval.watt_hours,
        interval.time_source,
        signing_key,
    )
    return hmac.compare_digest(interval.signature, expected)


def seal_from_run(
    *,
    run,
    meter_id: str,
    interval_start: str,
    interval_s: int,
    watt_hours: float,
    signing_key: str,
) -> SignedInterval:
    if getattr(run, "status", None) != "cleared":
        raise SealRefused("Photonseal will not seal an uncleared commitment run")
    if not getattr(run, "wrapped", False):
        raise SealRefused("Photonseal will not seal an unwrapped control path")
    if getattr(run, "grade", None) == "too_wide":
        raise SealRefused("Photonseal will not seal a too_wide path inaccuracy")
    return seal_interval(
        meter_id=meter_id,
        interval_start=interval_start,
        interval_s=interval_s,
        watt_hours=watt_hours,
        time_source=run.time_source,
        signing_key=signing_key,
    )
