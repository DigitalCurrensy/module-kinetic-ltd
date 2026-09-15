from desk.timescale import (
    DrainStore,
    DrainRow,
    DuplicateDrainEvent,
    ForbiddenPayload,
    SQL_RETENTION,
    drain_outbox_row,
)


def test_drain_rejects_duplicate():
    store = DrainStore()
    row = DrainRow("t1", "e1", "work_order", "2026-09-14T00:00:00Z", {"work_order_id": "wo-1"})
    store.append(row)
    try:
        store.append(row)
        assert False
    except DuplicateDrainEvent:
        pass


def test_drain_rejects_signing_key():
    store = DrainStore()
    try:
        store.append(
            DrainRow("t1", "e2", "signed_meter", "2026-09-14T00:00:00Z", {"signing_key": "secret"})
        )
        assert False
    except ForbiddenPayload:
        pass


def test_retention_sql_never_drops_table():
    assert "DROP TABLE" not in SQL_RETENTION
    assert "TRUNCATE" not in SQL_RETENTION
    assert "add_retention_policy" in SQL_RETENTION


def test_drain_outbox_row_copies_kind():
    class _Row:
        tenant_id = "t1"
        event_id = "e3"
        kind = "pin"
        time_source = "csac"

    stored = drain_outbox_row(DrainStore(), _Row(), observed_at="2026-09-14T00:00:00Z")
    assert stored.kind == "pin"
    assert stored.payload["time_source"] == "csac"
    assert "signing_key" not in stored.payload
