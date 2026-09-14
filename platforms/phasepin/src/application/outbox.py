"""Phasepin time-pin outbox — persist a pin, do not mutate it.

Append-only. Idempotent on event_id. No DROP / TRUNCATE.
A missing pin is not a row. GPS peer is still a pin. Module Kinetic Ltd.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Kind = Literal["time_pin"]


class OutboxError(Exception):
    code = "outbox_error"


class DuplicateOutboxEvent(OutboxError):
    code = "duplicate_outbox_event"


class MissingPin(OutboxError):
    code = "missing_pin"


@dataclass(frozen=True)
class OutboxRow:
    tenant_id: str
    event_id: str
    observed_at: str
    time_source: str
    offset_ns: int
    holdover_s: int
    grade: str | None
    kind: Kind = "time_pin"


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


def enqueue_pin(outbox: Outbox, pin, *, tenant_id: str, event_id: str) -> OutboxRow:
    if pin is None or not getattr(pin, "time_source", None):
        raise MissingPin("outbox will not enqueue a missing time pin")
    row = OutboxRow(
        tenant_id=tenant_id,
        event_id=event_id,
        observed_at=pin.observed_at,
        time_source=pin.time_source,
        offset_ns=pin.offset_ns,
        holdover_s=pin.holdover_s,
        grade=getattr(pin, "grade", None),
    )
    return outbox.append(row)
