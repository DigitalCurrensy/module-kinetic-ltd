"""Bayline CSMS ingest — one NotifyEvent POST, live receipt law.

Stdlib only. No FastAPI. receipt.py stays frozen.
NotifyPeriodicEventStream is still not a work order.
Module Kinetic Ltd.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from platforms.bayline.src.application.outbox import Outbox, enqueue_work_order
from platforms.bayline.src.application.receipt import (
    Component,
    IncomingMessage,
    NotifyEventRow,
    ReceiptStore,
    ReceiptError,
    Variable,
    ingest,
    open_work_order,
    set_lockout,
)


class HttpIngestError(Exception):
    code = "http_ingest_error"
    http_status = 400

    def __init__(self, message: str, *, code: str | None = None, http_status: int | None = None) -> None:
        super().__init__(message)
        if code:
            self.code = code
        if http_status is not None:
            self.http_status = http_status


@dataclass(frozen=True)
class IngestResult:
    http_status: int
    work_order_id: str | None
    diagnoses: int
    event_id: str
    code: str = "accepted"


def _row_from_event(raw: dict[str, Any]) -> NotifyEventRow:
    component = raw.get("component") or {}
    evse = component.get("evse") or {}
    variable = raw.get("variable") or {}
    return NotifyEventRow(
        event_id=int(raw["eventId"]),
        timestamp=str(raw["timestamp"]),
        trigger=raw["trigger"],
        actual_value=str(raw.get("actualValue", "")),
        component=Component(
            name=str(component.get("name", "EVSE")),
            evse_id=evse.get("id"),
            connector_id=component.get("connectorId"),
        ),
        variable=Variable(name=str(variable.get("name", ""))),
        tech_code=raw.get("techCode"),
        tech_info=raw.get("techInfo"),
        cleared=bool(raw.get("cleared", False)),
        severity=raw.get("actualSeverity"),
    )


def message_from_body(body: dict[str, Any]) -> IncomingMessage:
    if not isinstance(body, dict):
        raise HttpIngestError("body must be an object", http_status=400)
    required = ("tenant_id", "station_id", "correlation_id", "protocol", "action")
    missing = [k for k in required if not body.get(k)]
    if missing:
        raise HttpIngestError(f"missing {missing[0]}", http_status=400)
    rows = tuple(_row_from_event(item) for item in body.get("eventData") or ())
    return IncomingMessage(
        tenant_id=str(body["tenant_id"]),
        station_id=str(body["station_id"]),
        correlation_id=str(body["correlation_id"]),
        protocol=body["protocol"],
        action=body["action"],
        rows=rows,
        stream_id=body.get("stream_id"),
    )


def accept_notify_event(
    store: ReceiptStore,
    outbox: Outbox,
    body: dict[str, Any],
    *,
    work_order_id: str,
    event_id: str,
) -> IngestResult:
    """POST /ocpp/NotifyEvent → ingest → lockout → work order → outbox."""
    message = message_from_body(body)
    try:
        diagnosed = ingest(store, message)
    except ReceiptError as exc:
        status = 409 if getattr(exc, "code", "") == "duplicate" else 422
        raise HttpIngestError(str(exc), code=exc.code, http_status=status) from exc
    if not diagnosed:
        raise HttpIngestError("no diagnosis row in NotifyEvent", code="not_a_diagnosis", http_status=422)
    set_lockout(store, message.tenant_id, message.correlation_id)
    receipt = open_work_order(store, message, diagnosed[0], work_order_id)
    enqueue_work_order(outbox, receipt, event_id)
    return IngestResult(
        http_status=202,
        work_order_id=receipt.work_order_id,
        diagnoses=len(diagnosed),
        event_id=event_id,
        code="accepted",
    )
