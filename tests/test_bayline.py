"""Bayline — a real charger fault, or a refusal. Nothing else."""
from platforms.bayline.src.application.receipt import (
    Component,
    DuplicateEvent,
    IncomingMessage,
    LockoutRequired,
    NotifyEventRow,
    ProtocolRejected,
    ReceiptError,
    ReceiptStore,
    StreamIsNotAReceipt,
    Variable,
    ingest,
    open_work_order,
    set_lockout,
)


def _row(trigger="Alerting", variable="AvailabilityState", value="Faulted", cleared=False):
    return NotifyEventRow(
        event_id=1,
        timestamp="2026-09-24T16:00:00Z",
        trigger=trigger,
        actual_value=value,
        component=Component(name="EVSE", evse_id=1),
        variable=Variable(name=variable),
        cleared=cleared,
    )


def _msg(action="NotifyEvent", protocol="ocpp2.1", rows=(), correlation="c1"):
    return IncomingMessage(
        tenant_id="t1",
        station_id="s1",
        correlation_id=correlation,
        protocol=protocol,
        action=action,
        rows=rows,
    )


def test_alerting_fault_is_kept():
    rows = ingest(ReceiptStore(), _msg(rows=(_row(),)))
    assert len(rows) == 1


def test_faulted_state_change_is_kept():
    row = _row(trigger="Delta", variable="AvailabilityState", value="Faulted")
    rows = ingest(ReceiptStore(), _msg(rows=(row,), correlation="c2"))
    assert len(rows) == 1


def test_cleared_fault_is_not_kept():
    rows = ingest(ReceiptStore(), _msg(rows=(_row(cleared=True),)))
    assert rows == []


def test_status_update_is_not_a_fault():
    rows = ingest(ReceiptStore(), _msg(rows=(_row(trigger="Periodic"),)))
    assert rows == []


def test_available_state_is_not_a_fault():
    row = _row(trigger="Delta", variable="AvailabilityState", value="Available")
    rows = ingest(ReceiptStore(), _msg(rows=(row,), correlation="c3"))
    assert rows == []


def test_old_protocol_is_refused():
    try:
        ingest(ReceiptStore(), _msg(action="StatusNotification", protocol="ocpp1.6"))
        assert False
    except ProtocolRejected:
        pass


def test_charger_update_stream_is_not_a_fault():
    try:
        ingest(ReceiptStore(), _msg(action="NotifyPeriodicEventStream"))
        assert False
    except StreamIsNotAReceipt:
        pass


def test_newer_protocol_is_accepted():
    rows = ingest(ReceiptStore(), _msg(protocol="ocpp2.0.1", rows=(_row(),), correlation="c4"))
    assert len(rows) == 1


def test_same_fault_twice_is_one_record():
    store = ReceiptStore()
    ingest(store, _msg(rows=(_row(),)))
    try:
        ingest(store, _msg(rows=(_row(),)))
        assert False
    except DuplicateEvent:
        pass


def test_repair_job_before_lock_is_refused():
    store = ReceiptStore()
    row = _row()
    msg = _msg(rows=(row,))
    ingest(store, msg)
    try:
        open_work_order(store, msg, row, "wo-1")
        assert False
    except LockoutRequired:
        pass
    set_lockout(store, "t1", "c1")
    receipt = open_work_order(store, msg, row, "wo-1")
    assert receipt.work_order_id == "wo-1"
    assert receipt.lockout is True


def test_lock_without_a_fault_is_refused():
    try:
        set_lockout(ReceiptStore(), "t1", "missing")
        assert False
    except ReceiptError as error:
        assert error.code == "missing_event"
