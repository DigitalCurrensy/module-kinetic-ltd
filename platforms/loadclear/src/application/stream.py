"""A stream of updates is not a fault.

It updates a charger that already has a repair job. The fault check stays in Bayline.
"""
from __future__ import annotations

from dataclasses import dataclass

from platforms.loadclear.src.application.enroll import (
    EnrollError,
    Enrollment,
    EnrollStore,
    attach_stream,
    try_arm,
)


class StreamError(EnrollError):
    code = "stream_error"


class BadStreamEnvelope(StreamError):
    code = "bad_stream_envelope"


class StreamIsAReceipt(StreamError):
    code = "stream_is_a_receipt"


class ProtocolRejected(StreamError):
    code = "protocol_rejected"


@dataclass(frozen=True)
class StreamResult:
    enrollment: Enrollment
    stream_id: int
    dispatchable: bool
    arm: dict | None


def _require(envelope: dict, key: str):
    value = envelope.get(key)
    if value is None or value == "":
        raise BadStreamEnvelope(f"stream envelope missing {key}")
    return value


def handle_periodic_stream(
    store: EnrollStore,
    envelope: dict,
    *,
    try_dispatch: bool = False,
    kw: float = 15.0,
) -> StreamResult:
    """POST NotifyPeriodicEventStream → attach_stream → optional refuse/ARM."""
    protocol = envelope.get("protocol") or "ocpp2.1"
    action = envelope.get("action") or "NotifyPeriodicEventStream"
    if protocol == "ocpp1.6" or action == "StatusNotification":
        raise ProtocolRejected("OCPP 1.6 StatusNotification is not a Loadclear stream")
    if action == "NotifyEvent":
        raise StreamIsAReceipt("NotifyEvent is a Bayline receipt, not a Loadclear stream")
    if action != "NotifyPeriodicEventStream":
        raise ProtocolRejected(f"action {action} is not a Loadclear stream")
    tenant_id = str(_require(envelope, "tenant_id"))
    evse_id = str(_require(envelope, "evse_id"))
    payload = envelope.get("payload") or {}
    stream_id = payload.get("streamId") or payload.get("stream_id") or envelope.get("stream_id")
    if stream_id is None:
        raise BadStreamEnvelope("stream envelope missing stream_id")
    stream_id = int(stream_id)
    enrollment = attach_stream(store, tenant_id, evse_id, stream_id)
    arm = None
    if try_dispatch:
        arm = try_arm(enrollment, kw=kw)
    return StreamResult(
        enrollment=enrollment,
        stream_id=stream_id,
        dispatchable=enrollment.dispatchable,
        arm=arm,
    )
