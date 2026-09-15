"""Loadclear stream attach — NotifyPeriodicEventStream is telemetry, not a receipt.

Bayline refuses this action as a work order. Loadclear binds stream_id onto
an already-enrolled EVSE. attach_stream in enroll.py stays frozen.
ARM still goes through refuse.evaluate. Module Kinetic Ltd.
"""
from __future__ import annotations

from dataclasses import dataclass

from platforms.loadclear.src.application.enroll import (
    EnrollStore,
    attach_stream,
    offer_for,
)
from platforms.loadclear.src.application.refuse import DispatchInstruction, evaluate


class StreamError(Exception):
    code = "stream_error"


class BadStreamEnvelope(StreamError):
    code = "bad_stream_envelope"


class StreamIsNotAWorkOrder(StreamError):
    code = "stream_is_not_a_work_order"


class ProtocolRejected(StreamError):
    code = "protocol_rejected"


@dataclass(frozen=True)
class StreamAttach:
    tenant_id: str
    evse_id: str
    stream_id: int
    asset_id: str
    dispatchable: bool
    stream_ids: tuple[int, ...]


def _require(envelope: dict, key: str) -> str:
    value = envelope.get(key)
    if value is None or value == "":
        raise BadStreamEnvelope(f"stream envelope missing {key}")
    return str(value)


def handle_periodic_stream(
    store: EnrollStore,
    envelope: dict,
    *,
    try_arm: bool = False,
    arm_kw: float = 15.0,
) -> StreamAttach:
    """Bind NotifyPeriodicEventStream onto an enrolled EVSE. Never open a work order."""
    action = envelope.get("action") or "NotifyPeriodicEventStream"
    protocol = envelope.get("protocol") or "ocpp2.1"
    if action in {"NotifyEvent", "StatusNotification"}:
        raise StreamIsNotAWorkOrder("NotifyEvent stays on Bayline; this is the telemetry plane")
    if action != "NotifyPeriodicEventStream":
        raise StreamIsNotAWorkOrder(f"action {action} is not a Loadclear stream")
    if protocol == "ocpp1.6":
        raise ProtocolRejected("OCPP 1.6 is not a Loadclear stream")
    if protocol not in {"ocpp2.1", "ocpp2.0.1"}:
        raise ProtocolRejected(f"unsupported protocol {protocol}")

    tenant_id = _require(envelope, "tenant_id")
    evse_id = _require(envelope, "evse_id")
    payload = envelope.get("payload") or {}
    raw_id = payload.get("streamId") or envelope.get("stream_id")
    if raw_id is None:
        raise BadStreamEnvelope("stream envelope missing stream_id")
    stream_id = int(raw_id)

    enrollment = attach_stream(store, tenant_id, evse_id, stream_id)
    if try_arm:
        offer = offer_for(enrollment)
        evaluate(offer, DispatchInstruction(asset_id=enrollment.asset_id, kw=arm_kw, duration_s=900))
    return StreamAttach(
        tenant_id=enrollment.tenant_id,
        evse_id=enrollment.evse_id,
        stream_id=stream_id,
        asset_id=enrollment.asset_id,
        dispatchable=enrollment.dispatchable,
        stream_ids=tuple(enrollment.stream_ids),
    )
