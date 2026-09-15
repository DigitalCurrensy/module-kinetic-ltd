from desk.drain import (
    BadKind,
    DrainRow,
    DrainStore,
    ForbiddenSql,
    SQL_COMPRESS,
    SQL_RETAIN,
    SigningKeyForbidden,
    assert_safe_sql,
    drain_outbox,
    drain_row,
    row_from_outbox,
)


def test_sql_policies_are_safe():
    assert_safe_sql(SQL_COMPRESS)
    assert_safe_sql(SQL_RETAIN)
    try:
        assert_safe_sql("DROP TABLE desk_outbox")
        assert False
    except ForbiddenSql:
        pass


def test_duplicate_returns_none():
    store = DrainStore()
    row = DrainRow("t1", "e1", "work_order", "2026-09-14T00:00:00Z", {"work_order_id": "wo-1"})
    assert drain_row(store, row) is row
    assert drain_row(store, row) is None


def test_signing_key_forbidden():
    store = DrainStore()
    try:
        drain_row(
            store,
            DrainRow("t1", "e2", "signed_meter", "2026-09-14T00:00:00Z", {"signing_key": "secret"}),
        )
        assert False
    except SigningKeyForbidden:
        pass


def test_row_from_outbox_copies_signature_not_key():
    class _Interval:
        tenant_id = "t1"
        event_id = "e3"
        kind = "signed_meter"
        meter_id = "m1"
        signature = "abc"
        watt_hours = 1.5

    row = row_from_outbox(_Interval(), observed_at="2026-09-14T00:00:00Z")
    assert row.signature == "abc"
    assert "signing_key" not in row.payload
    assert row.payload["watt_hours"] == 1.5


def test_bad_kind_refused():
    class _Row:
        tenant_id = "t1"
        event_id = "e4"
        kind = "token"

    try:
        row_from_outbox(_Row(), observed_at="2026-09-14T00:00:00Z")
        assert False
    except BadKind:
        pass


def test_drain_outbox_counts_new_rows():
    class _Box:
        rows = [
            type("R", (), {"tenant_id": "t1", "event_id": "e5", "kind": "pin", "time_source": "csac"})()
        ]

    store = DrainStore()
    assert drain_outbox(store, _Box(), observed_at="2026-09-14T00:00:00Z") == 1
    assert drain_outbox(store, _Box(), observed_at="2026-09-14T00:00:00Z") == 0
