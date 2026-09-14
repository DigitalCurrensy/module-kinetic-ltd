"""Photonseal meter outbox — persist a signed interval, do not mutate it.

Append-only. Idempotent on event_id. No DROP / TRUNCATE.
An unsigned interval is not a row. Signing key is never stored.
HMAC stays the tag. Module Kinetic Ltd.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Kind = Literal["signed_meter"]


class OutboxError(Exception):
    code = "outbox_error"


class DuplicateOutboxEvent(OutboxError):
    code = "duplicate_outbox_event"


class UnsignedInterval(OutboxError):
    code = "unsigned_interval"


@dataclass(frozen=True)
class OutboxRow:
    tenant_id: str
    event_id: str
    meter_id: str
    interval_start: str
    interval_s: int
    watt_hours: float
    time_source: str
    signature: str
    kind: Kind = "signed_meter"


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


def enqueue_interval(outbox: Outbox, interval, *, tenant_id: str, event_id: str) -> OutboxRow:
    if interval is None or not getattr(interval, "signature", None):
        raise UnsignedInterval("outbox will not enqueue an unsigned interval")
    if getattr(interval, "kind", None) != "signed_meter":
        raise UnsignedInterval("outbox will not enqueue a token")
    row = OutboxRow(
        tenant_id=tenant_id,
        event_id=event_id,
        meter_id=interval.meter_id,
        interval_start=interval.interval_start,
        interval_s=interval.interval_s,
        watt_hours=interval.watt_hours,
        time_source=interval.time_source,
        signature=interval.signature,
    )
    return outbox.append(row)
