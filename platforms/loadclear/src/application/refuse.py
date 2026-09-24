"""Turning the charger on while it is locked is refused.

A charger that is too hot, too empty, over its export limit, or past its cycle budget is also refused.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

RefuseCode = Literal[
    "soc_band",
    "cycle_budget",
    "temp_derate",
    "export_cap",
    "departure",
    "site_faulted",
    "lockout_open",
]


class DispatchRefused(Exception):
    def __init__(self, code: RefuseCode, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.http_status = 422


@dataclass(frozen=True)
class AssetOffer:
    asset_id: str
    evse_id: str | None
    soc: float
    soc_min: float
    soc_max: float
    cycles_used: float
    cycle_budget: float
    temp_c: float
    temp_max_c: float
    export_kw: float
    export_cap_kw: float
    depart_in_s: int | None
    instruction_s: int
    site_faulted: bool
    lockout_open: bool


@dataclass(frozen=True)
class DispatchInstruction:
    asset_id: str
    kw: float
    duration_s: int


def evaluate(offer: AssetOffer, instruction: DispatchInstruction) -> None:
    if offer.lockout_open:
        raise DispatchRefused("lockout_open", "Bayline LOTO still open on this EVSE")
    if offer.site_faulted:
        raise DispatchRefused("site_faulted", "Bayline or Cabinetfield fault is open")
    if offer.soc < offer.soc_min or offer.soc > offer.soc_max:
        raise DispatchRefused("soc_band", "SOC outside armed band")
    if offer.cycles_used >= offer.cycle_budget:
        raise DispatchRefused("cycle_budget", "cycle budget exhausted")
    if offer.temp_c >= offer.temp_max_c:
        raise DispatchRefused("temp_derate", "pack too hot to move watts")
    if abs(instruction.kw) > offer.export_cap_kw or abs(instruction.kw) > offer.export_kw:
        raise DispatchRefused("export_cap", "instruction exceeds interconnection cap")
    if offer.depart_in_s is not None and instruction.duration_s > offer.depart_in_s:
        raise DispatchRefused("departure", "dispatch outlives the departure constraint")
