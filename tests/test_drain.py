from desk.drain import (
    SQL_COMPRESS,
    SQL_INSERT,
    SQL_RETAIN,
    DrainRow,
    DrainStore,
    ForbiddenSql,
    SigningKeyForbidden,
    assert_safe_sql,
    drain_outbox,
    drain_row,
)
from platforms.bayline.src.application.outbox import Outbox as BaylineOutbox, enqueue_work_order
from platforms.bayline.src.application.receipt import (
    Component,
    IncomingMessage,
    NotifyEventRow,
    ReceiptStore,
    Variable,
    ingest,
    open_work_order,
    set_lockout,
)
from platforms.photonseal.src.application.meter import seal_interval
from platforms.photonseal.src.application.outbox import Outbox as SealOutbox, enqueue_interval


def test_insert_sql_is_conflict_do_nothing():
    assert "ON CONFLICT (tenant_id, event_id) DO NOTHING" in SQL_INSERT
    assert_safe_sql(SQL_INSERT)


def test_retention_is_chunk_policy_not_truncate():
    assert "add_retention_policy" in SQL_RETAIN
    assert "add_compression_policy" in SQL_COMPRESS
    assert_safe_sql(SQL_RETAIN)
    assert_safe_sql(SQL_COMPRESS)
    try:
        assert_safe_sql("DROP TABLE desk_outbox")
        assert False
    except ForbiddenSql:
        pass


def test_duplicate_event_is_noop():
    store = DrainStore()
    row = DrainRow("t1", "evt-1", "work_order", "2026-09-14T00:00:00Z", {"work_order_id": "wo-1"})
    assert drain_row(store, row) is row
    assert drain_row(store, row) is None
    assert len(store.rows) == 1


def test_signing_key_forbidden():
    store = DrainStore()
    try:
        drain_row(
            store,
            DrainRow("t1", "evt-k", "signed_meter", "2026-09-14T00:00:00Z", {"signing_key": "k"}),
        )
        assert False
    except SigningKeyForbidden:
        pass


def test_drain_bayline_and_photonseal_outboxes():
    receipts = ReceiptStore()
    row = NotifyEventRow(
        event_id=1,
        timestamp="2026-09-14T00:00:00Z",
        trigger="Alerting",
        actual_value="Faulted",
        component=Component("EVSE", evse_id=1),
        variable=Variable("AvailabilityState"),
    )
    msg = IncomingMessage("t1", "s1", "c1", "ocpp2.1", "NotifyEvent", (row,))
    ingest(receipts, msg)
    set_lockout(receipts, "t1", "c1")
    receipt = open_work_order(receipts, msg, row, "wo-1")
    bay = BaylineOutbox()
    enqueue_work_order(bay, receipt, "evt-wo")
    interval = seal_interval(
        meter_id="m-1",
        interval_start="2026-09-14T00:00:00Z",
        interval_s=900,
        watt_hours=12.5,
        time_source="csac",
        signing_key="k",
    )
    seal = SealOutbox()
    enqueue_interval(seal, interval, tenant_id="t1", event_id="evt-sm")
    store = DrainStore()
    assert drain_outbox(store, bay, observed_at="2026-09-14T00:00:00Z") == 1
    assert drain_outbox(store, seal, observed_at="2026-09-14T00:00:00Z") == 1
    sm = store.by_event("t1", "evt-sm")
    assert sm is not None
    assert sm.signature == interval.signature
    assert "signing_key" not in sm.payload
