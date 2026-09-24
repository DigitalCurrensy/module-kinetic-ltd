"""Is this charger allowed back on?

No repair job, no enrollment. A second enrollment of the same charger reopens the lock.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from platforms.loadclear.src.application.refuse import AssetOffer, DispatchInstruction, evaluate


class EnrollError(Exception):
    code = "enroll_error"


class MissingReceipt(EnrollError):
    code = "missing_receipt"


class AlreadyEnrolled(EnrollError):
    code = "already_enrolled"


@dataclass
class Enrollment:
    tenant_id: str
    evse_id: str
    station_id: str
    asset_id: str
    bayline_work_order_id: str
    site_faulted: bool
    lockout_open: bool
    stream_ids: list[int] = field(default_factory=list)

    @property
    def dispatchable(self) -> bool:
        return not (self.site_faulted or self.lockout_open)


@dataclass
class EnrollStore:
    by_evse: dict[tuple[str, str], Enrollment] = field(default_factory=dict)


def enroll_from_bayline(store, *, tenant_id, evse_id, station_id, work_order_id, lockout_open):
    if not work_order_id:
        raise MissingReceipt("Loadclear will not enroll an EVSE without a Bayline work order id")
    key = (tenant_id, evse_id)
    if key in store.by_evse:
        raise AlreadyEnrolled(evse_id)
    enrollment = Enrollment(
        tenant_id=tenant_id,
        evse_id=evse_id,
        station_id=station_id,
        asset_id=f"lc:{tenant_id}:{evse_id}",
        bayline_work_order_id=work_order_id,
        site_faulted=True,
        lockout_open=lockout_open,
    )
    store.by_evse[key] = enrollment
    return enrollment


def attach_stream(store, tenant_id, evse_id, stream_id):
    enrollment = store.by_evse.get((tenant_id, evse_id))
    if enrollment is None:
        raise MissingReceipt("stream cannot attach before enrollment")
    if stream_id not in enrollment.stream_ids:
        enrollment.stream_ids.append(stream_id)
    return enrollment


def close_fault(store, tenant_id, evse_id):
    enrollment = store.by_evse[(tenant_id, evse_id)]
    enrollment.site_faulted = False
    enrollment.lockout_open = False
    return enrollment


def offer_for(enrollment, *, soc=0.6):
    return AssetOffer(
        asset_id=enrollment.asset_id,
        evse_id=enrollment.evse_id,
        soc=soc,
        soc_min=0.2,
        soc_max=0.9,
        cycles_used=0.0,
        cycle_budget=10.0,
        temp_c=25.0,
        temp_max_c=50.0,
        export_kw=20.0,
        export_cap_kw=25.0,
        depart_in_s=3600,
        instruction_s=900,
        site_faulted=enrollment.site_faulted,
        lockout_open=enrollment.lockout_open,
    )


def try_arm(enrollment, kw=15.0):
    offer = offer_for(enrollment)
    instruction = DispatchInstruction(asset_id=enrollment.asset_id, kw=kw, duration_s=900)
    evaluate(offer, instruction)
    return {"decision": "ARM", "http": 200, "asset_id": enrollment.asset_id, "kw": kw}
