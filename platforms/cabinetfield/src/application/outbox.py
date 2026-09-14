"""Cabinetfield derate outbox — persist an issued derate, do not mutate it.

Append-only. Idempotent on event_id. No DROP / TRUNCATE.
A missing derate is not a row. Module Kinetic Ltd.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Kind = Literal["derate"]


class OutboxError(Exception):
    code = "outbox_error"


class DuplicateOutboxEvent(OutboxError):
    code = "duplicate_outbox_event"


class MissingDerate(OutboxError):
    code = "missing_derate"


@dataclass(frozen=True)
class OutboxRow:
    tenant_id: str
    event_id: str
    cabinet_id: str
    cluster_id: str
    factor: float
    severity: str
    fault_class: str
    calibration_run_id: str | None
    kind: Kind = "derate"


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


def enqueue_derate(outbox: Outbox, derate, *, tenant_id: str, event_id: str) -> OutboxRow:
    if derate is None or getattr(derate, "factor", None) is None:
        raise MissingDerate("outbox will not enqueue a missing derate")
    row = OutboxRow(
        tenant_id=tenant_id,
        event_id=event_id,
        cabinet_id=derate.cabinet_id,
        cluster_id=derate.cluster_id,
        factor=derate.factor,
        severity=derate.severity,
        fault_class=derate.fault_class,
        calibration_run_id=derate.calibration_run_id,
    )
    return outbox.append(row)
