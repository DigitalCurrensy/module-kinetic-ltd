"""The enrollment is saved once.

The same event is not saved again. A missing enrollment is not a row.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Kind = Literal["enrollment"]


class OutboxError(Exception):
    code = "outbox_error"


class DuplicateOutboxEvent(OutboxError):
    code = "duplicate_outbox_event"


class MissingEnrollment(OutboxError):
    code = "missing_enrollment"


@dataclass(frozen=True)
class OutboxRow:
    tenant_id: str
    event_id: str
    asset_id: str
    evse_id: str
    station_id: str
    bayline_work_order_id: str
    kind: Kind = "enrollment"


@dataclass
class Outbox:
    rows: list[OutboxRow] = field(default_factory=list)
    seen: set[tuple[str, str]] = field(default_factory=set)

    def append(self, row: OutboxRow) -> OutboxRow:
        key = (row.tenant_id, row.event_id)
        if key in self.seen:
            raise DuplicateOutboxEvent(row.event_id)
        self.seen.add(key)
        self.rows.append(row)
        return row

    def by_event(self, tenant_id: str, event_id: str) -> OutboxRow | None:
        for row in self.rows:
            if row.tenant_id == tenant_id and row.event_id == event_id:
                return row
        return None

    def for_tenant(self, tenant_id: str) -> tuple[OutboxRow, ...]:
        return tuple(r for r in self.rows if r.tenant_id == tenant_id)


def enqueue_enrollment(outbox: Outbox, enrollment, event_id: str) -> OutboxRow:
    if enrollment is None or not getattr(enrollment, "bayline_work_order_id", None):
        raise MissingEnrollment("outbox will not enqueue an enrollment without a Bayline work order")
    row = OutboxRow(
        tenant_id=enrollment.tenant_id,
        event_id=event_id,
        asset_id=enrollment.asset_id,
        evse_id=enrollment.evse_id,
        station_id=enrollment.station_id,
        bayline_work_order_id=enrollment.bayline_work_order_id,
    )
    return outbox.append(row)
