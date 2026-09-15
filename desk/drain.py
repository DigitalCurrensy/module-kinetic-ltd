"""Desk Timescale drain — persist house outbox rows, do not merge houses.

In-memory first. SQL is the intended Timescale shape.
UNIQUE (tenant_id, event_id). No DROP / TRUNCATE. Signing keys never stored.
Module Kinetic Ltd.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Kind = Literal[
    "work_order",
    "enrollment",
    "derate",
    "pin",
    "time_pin",
    "wrap",
    "cleared_run",
    "commitment_run",
    "signed_meter",
]

ALLOWED_KINDS = frozenset(
    {
        "work_order",
        "enrollment",
        "derate",
        "pin",
        "time_pin",
        "wrap",
        "cleared_run",
        "commitment_run",
        "signed_meter",
    }
)
FORBIDDEN_SQL = ("DROP TABLE", "TRUNCATE", "DROP HYPERABLE")

SQL_CREATE = """
CREATE TABLE IF NOT EXISTS desk_outbox (
    tenant_id   UUID        NOT NULL,
    event_id    TEXT        NOT NULL,
    kind        TEXT        NOT NULL,
    observed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    payload     JSONB       NOT NULL,
    signature   TEXT,
    PRIMARY KEY (tenant_id, event_id),
    CONSTRAINT desk_outbox_kind CHECK (kind IN (
        'work_order','enrollment','derate','pin','time_pin','wrap',
        'cleared_run','commitment_run','signed_meter'
    ))
);
"""

SQL_HYPERTABLE = (
    "SELECT create_hypertable('desk_outbox', 'observed_at', "
    "chunk_time_interval => INTERVAL '1 day', if_not_exists => TRUE);"
)

SQL_INSERT = (
    "INSERT INTO desk_outbox (tenant_id, event_id, kind, observed_at, payload, signature) "
    "VALUES (%s, %s, %s, %s, %s, %s) "
    "ON CONFLICT (tenant_id, event_id) DO NOTHING;"
)

SQL_COMPRESS = (
    "SELECT add_compression_policy('desk_outbox', INTERVAL '7 days', if_not_exists => TRUE);"
)

SQL_RETAIN = (
    "SELECT add_retention_policy('desk_outbox', INTERVAL '400 days', if_not_exists => TRUE);"
)


class DrainError(Exception):
    code = "drain_error"


class ForbiddenSql(DrainError):
    code = "forbidden_sql"


class BadKind(DrainError):
    code = "bad_kind"


class SigningKeyForbidden(DrainError):
    code = "signing_key_forbidden"


class DuplicateDrainEvent(DrainError):
    code = "duplicate_drain_event"


@dataclass(frozen=True)
class DrainRow:
    tenant_id: str
    event_id: str
    kind: Kind
    observed_at: str
    payload: dict[str, Any]
    signature: str | None = None


@dataclass
class DrainStore:
    rows: list[DrainRow] = field(default_factory=list)
    seen: set[tuple[str, str]] = field(default_factory=set)

    def by_event(self, tenant_id: str, event_id: str) -> DrainRow | None:
        for row in self.rows:
            if row.tenant_id == tenant_id and row.event_id == event_id:
                return row
        return None


def assert_safe_sql(statement: str) -> None:
    upper = statement.upper()
    for token in FORBIDDEN_SQL:
        if token in upper:
            raise ForbiddenSql(token)


def _payload_of(row) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for name in (
        "work_order_id",
        "station_id",
        "evse_id",
        "correlation_id",
        "asset_id",
        "cluster_id",
        "factor",
        "time_source",
        "grade",
        "wrapped",
        "status",
        "meter_id",
        "interval_start",
        "interval_s",
        "watt_hours",
        "spin_count",
        "residual_mw",
        "run_id",
        "span_id",
        "bayline_work_order_id",
    ):
        if hasattr(row, name):
            payload[name] = getattr(row, name)
    return payload


def row_from_outbox(row, *, observed_at: str) -> DrainRow:
    kind = getattr(row, "kind", None)
    if kind not in ALLOWED_KINDS:
        raise BadKind(str(kind))
    payload = _payload_of(row)
    if "signing_key" in payload or getattr(row, "signing_key", None):
        raise SigningKeyForbidden("drain will not persist a signing key")
    return DrainRow(
        tenant_id=str(row.tenant_id),
        event_id=str(row.event_id),
        kind=kind,
        observed_at=observed_at,
        payload=payload,
        signature=getattr(row, "signature", None),
    )


def drain_row(store: DrainStore, row: DrainRow) -> DrainRow | None:
    """In-memory ON CONFLICT DO NOTHING. Returns None on duplicate."""
    key = (row.tenant_id, row.event_id)
    if key in store.seen:
        return None
    if "signing_key" in row.payload:
        raise SigningKeyForbidden("drain will not persist a signing key")
    store.seen.add(key)
    store.rows.append(row)
    return row


def drain_outbox(store: DrainStore, outbox, *, observed_at: str) -> int:
    """Drain every duck-typed house outbox row. Houses stay separate packages."""
    written = 0
    for raw in getattr(outbox, "rows", ()):    
        landed = drain_row(store, row_from_outbox(raw, observed_at=observed_at))
        if landed is not None:
            written += 1
    return written
