"""Photonseal — attested interval as a signed meter, not a token.

Duck-typed bind to a Unitcommit run: status must be cleared.
No Unitcommit import. Houses do not merge.
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
    material = f"{meter_id}|{interval_start}|{interval_s}|{watt_hours:.3f}|{time_source}".encode()
    signature = hmac.new(signing_key.encode(), material, hashlib.sha256).hexdigest()
    return SignedInterval(
        meter_id=meter_id,
        interval_start=interval_start,
        interval_s=interval_s,
        watt_hours=watt_hours,
        time_source=time_source,
        signature=signature,
    )


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
    return seal_interval(
        meter_id=meter_id,
        interval_start=interval_start,
        interval_s=interval_s,
        watt_hours=watt_hours,
        time_source=run.time_source,
        signing_key=signing_key,
    )
