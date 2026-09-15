"""Desk live drain — DATABASE_URL Timescale writer, optional.

Unset URL → no connection, 0 writes. Set URL → CREATE IF NOT EXISTS
+ INSERT ON CONFLICT DO NOTHING. Never DROP / TRUNCATE.
Timescale hypertable / policies are best-effort: failure rolls back
that statement only so vanilla Postgres and Neon still accept rows.
Reuses desk.drain SQL. Module Kinetic Ltd.
"""
from __future__ import annotations

import json
import os

from desk.drain import (
    DrainRow,
    FORBIDDEN_SQL,
    SQL_COMPRESS,
    SQL_CREATE,
    SQL_HYPERTABLE,
    SQL_INSERT,
    SQL_RETAIN,
    assert_safe_sql,
)


class PgError(Exception):
    code = "pg_error"


class DatabaseUrlMissing(PgError):
    code = "database_url_missing"


def database_url() -> str | None:
    url = os.environ.get("DATABASE_URL", "").strip()
    return url or None


def _guard(statement: str) -> str:
    assert_safe_sql(statement)
    upper = statement.upper()
    for token in FORBIDDEN_SQL:
        if token in upper:
            raise PgError(token)
    if "DROP " in upper or upper.startswith("DROP") or "TRUNCATE" in upper:
        raise PgError("drop_or_truncate")
    return statement


def connect(url: str | None = None):
    target = url if url is not None else database_url()
    if not target:
        raise DatabaseUrlMissing("DATABASE_URL unset — in-memory drain only")
    try:
        import psycopg
    except ImportError as exc:
        raise PgError("psycopg not installed") from exc
    return psycopg.connect(target)


def bootstrap(conn) -> None:
    cur = conn.cursor()
    cur.execute(_guard(SQL_CREATE))
    conn.commit()
    try:
        cur = conn.cursor()
        cur.execute(_guard(SQL_HYPERTABLE))
        conn.commit()
    except Exception:
        conn.rollback()
    try:
        cur = conn.cursor()
        cur.execute(_guard(SQL_COMPRESS))
        cur.execute(_guard(SQL_RETAIN))
        conn.commit()
    except Exception:
        conn.rollback()


def insert_row(conn, row: DrainRow) -> int:
    cur = conn.cursor()
    cur.execute(
        _guard(SQL_INSERT),
        (
            row.tenant_id,
            row.event_id,
            row.kind,
            row.observed_at,
            json.dumps(row.payload),
            row.signature,
        ),
    )
    conn.commit()
    return cur.rowcount or 0


def drain_live(store_rows: list[DrainRow], *,
    url: str | None = None,
) -> int:
    """Write already-drained memory rows. No-op if DATABASE_URL unset."""
    target = url if url is not None else database_url()
    if not target:
        return 0
    conn = connect(target)
    try:
        bootstrap(conn)
        written = 0
        for row in store_rows:
            written += insert_row(conn, row)
        return written
    finally:
        conn.close()
