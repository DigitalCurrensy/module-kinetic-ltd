"""A clean line is saved once. A noisy line is not a row."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Kind = Literal["wrap"]


class OutboxError(Exception):
    code = "outbox_error"


class DuplicateOutboxEvent(OutboxError):
    code = "duplicate_outbox_event"


class UnwrappedSession(OutboxError):
    code = "unwrapped"


@dataclass(frozen=True)
class OutboxRow:
    tenant_id: str
    event_id: str
    span_id: str
    session_id: str
    qber: float
    key_bits: int
    kind: Kind = "wrap"


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


def enqueue_wrap(outbox: Outbox, session, *, tenant_id: str, event_id: str) -> OutboxRow:
    if session is None or getattr(session, "wrapped", False) is not True:
        raise UnwrappedSession("outbox will not enqueue an unwrapped session")
    row = OutboxRow(
        tenant_id=tenant_id,
        event_id=event_id,
        span_id=session.span_id,
        session_id=session.session_id,
        qber=session.qber,
        key_bits=session.key_bits,
    )
    return outbox.append(row)
