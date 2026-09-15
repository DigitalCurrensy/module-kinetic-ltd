"""Desk Timescale drain — persist the seven house outboxes, do not merge houses.

In-memory first. SQL constants are the contract for a later live hypertable.
No DROP / TRUNCATE. Signing keys never stored. Module Kinetic Ltd.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Kind = Literal[
    "work_order",
    "enrollment",
    "derate",
    "pin",
    "wrap",
    "cleared_run",
    "signed_meter",
]

KINDS: frozenset[str] = frozenset(
    {"work_order", "enrollment", "derate", "pin", "wrap", "cleared_run", "signed_meter"}
)

FORBIDDEN_KEYS = frozenset({"signing_key", "key", "hmac_key"})

SQL_CREATE = """
CREATE TABLE IF NOT EXISTS desk_outbox (
    tenant_id    uuid        NOT NULL,
    event_id     uuid        NOT NULL,
    kind         text        NOT NULL,
    observed_at  timestamptz NOT NULL,
    payload      jsonb       NOT NULL DEFAULT '{}',
    UNIQUE (tenant_id, event_id),
    CHECK (kind IN (
        'work_order','enrollment','derate','pin','wrap','cleared_run','signed_meter'
    ))
);
SELECT create_hypertable('desk_outbox', 'observed_at',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE);
"""

SQL_INSERT = """
INSERT INTO desk_outbox (tenant_id, event_id, kind, observed_at, payload)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (tenant_id, event_id) DO NOTHING;
"""

SQL_RETENTION = """
SELECT add_compression_policy('desk_outbox', INTERVAL '7 days');
SELECT add_retention_policy('desk_outbox', INTERVAL '400 days');
-- drop_chunks expires old chunks. Never DROP TABLE desk_outbox.
"""


class DrainError(Exception):
    code = "drain_error"


class DuplicateDrainEvent(DrainError):
    code = "duplicate_drain_event"


class ForbiddenPayload(DrainError):
    code = "forbidden_payload"


class UnknownKind(DrainError):
    code = "unknown_kind"


@dataclass(frozen=True)
class DrainRow:
    tenant_id: str
    event_id: str
    kind: Kind
    observed_at: str
    payload: dict


@dataclass
class DrainStore:
    rows: list[DrainRow] = field(default_factory=list)
    seen: set[tuple[str, str]] = field(default_factory=set)

    def append(self, row: DrainRow) -> DrainRow:
        if row.kind not in KINDS:
            raise UnknownKind(row.kind)
        if FORBIDDEN_KEYS & set(row.payload):
            raise ForbiddenPayload("signing keys do not belong in desk_outbox")
        key = (row.tenant_id, row.event_id)
        if key in self.seen:
            raise DuplicateDrainEvent(row.event_id)
        self.seen.add(key)
        self.rows.append(row)
        return row

    def by_event(self, tenant_id: str, event_id: str) -> DrainRow | None:
        for row in self.rows:
            if row.tenant_id == tenant_id and row.event_id == event_id:
                return row
        return None


def drain_outbox_row(store: DrainStore, row, *, observed_at: str) -> DrainRow:
    """Copy a house outbox fact into the desk drain. Duck-typed."""
    kind = getattr(row, "kind", None)
    if kind not in KINDS:
        raise UnknownKind(str(kind))
    payload = {
        k: getattr(row, k)
        for k in vars(row)
        if k not in {"tenant_id", "event_id", "kind"} and k not in FORBIDDEN_KEYS
    }
    return store.append(
        DrainRow(
            tenant_id=row.tenant_id,
            event_id=row.event_id,
            kind=kind,
            observed_at=observed_at,
            payload=payload,
        )
    )
