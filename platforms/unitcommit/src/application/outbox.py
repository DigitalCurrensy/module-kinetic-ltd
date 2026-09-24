"""A passed power check is saved once. A mismatch is not a row."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Kind = Literal["commitment_run"]


class OutboxError(Exception):
    code = "outbox_error"


class DuplicateOutboxEvent(OutboxError):
    code = "duplicate_outbox_event"


class UnclearedRun(OutboxError):
    code = "uncleared_run"


@dataclass(frozen=True)
class OutboxRow:
    tenant_id: str
    event_id: str
    run_id: str
    status: str
    spin_count: int
    assignment_count: int
    residual_mw: float
    kind: Kind = "commitment_run"


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


def enqueue_cleared_run(outbox: Outbox, run, *, tenant_id: str, event_id: str) -> OutboxRow:
    if run is None or getattr(run, "status", None) != "cleared":
        raise UnclearedRun("outbox will not enqueue a run that is not cleared")
    row = OutboxRow(
        tenant_id=tenant_id,
        event_id=event_id,
        run_id=run.run_id,
        status=run.status,
        spin_count=run.spin_count,
        assignment_count=run.assignment_count,
        residual_mw=run.residual_mw,
    )
    return outbox.append(row)
