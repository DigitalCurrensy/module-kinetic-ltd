"""An update stream is not a fault."""
from platforms.loadclear.src.application.enroll import (
    EnrollStore,
    MissingReceipt,
    close_fault,
    enroll_from_bayline,
)
from platforms.loadclear.src.application.refuse import DispatchRefused
from platforms.loadclear.src.application.stream import (
    BadStreamEnvelope,
    ProtocolRejected,
    StreamIsAReceipt,
    handle_periodic_stream,
)


def _enroll(store, evse="1"):
    return enroll_from_bayline(
        store,
        tenant_id="t1",
        evse_id=evse,
        station_id="s1",
        work_order_id="wo-1",
        lockout_open=True,
    )


def _envelope(**overrides):
    body = {
        "tenant_id": "t1",
        "evse_id": "1",
        "protocol": "ocpp2.1",
        "action": "NotifyPeriodicEventStream",
        "payload": {"streamId": 5},
    }
    body.update(overrides)
    return body


def test_stream_attaches_after_enroll():
    store = EnrollStore()
    _enroll(store)
    result = handle_periodic_stream(store, _envelope())
    assert result.stream_id == 5
    assert 5 in result.enrollment.stream_ids
    assert result.dispatchable is False


def test_stream_before_enroll_is_missing_receipt():
    store = EnrollStore()
    try:
        handle_periodic_stream(store, _envelope())
        assert False
    except MissingReceipt:
        pass


def test_notify_event_is_not_a_stream():
    store = EnrollStore()
    _enroll(store)
    try:
        handle_periodic_stream(store, _envelope(action="NotifyEvent"))
        assert False
    except StreamIsAReceipt:
        pass


def test_status_notification_rejected():
    store = EnrollStore()
    try:
        handle_periodic_stream(
            store, _envelope(action="StatusNotification", protocol="ocpp1.6")
        )
        assert False
    except ProtocolRejected:
        pass


def test_missing_stream_id_is_bad_envelope():
    store = EnrollStore()
    _enroll(store)
    try:
        handle_periodic_stream(store, _envelope(payload={}))
        assert False
    except BadStreamEnvelope:
        pass


def test_dispatch_refused_while_lockout_open():
    store = EnrollStore()
    _enroll(store)
    try:
        handle_periodic_stream(store, _envelope(), try_dispatch=True)
        assert False
    except DispatchRefused as exc:
        assert exc.http_status == 422
        assert exc.code in {"lockout_open", "site_faulted"}


def test_arm_after_close_fault():
    store = EnrollStore()
    _enroll(store)
    handle_periodic_stream(store, _envelope())
    close_fault(store, "t1", "1")
    result = handle_periodic_stream(store, _envelope(), try_dispatch=True)
    assert result.dispatchable is True
    assert result.arm["decision"] == "ARM"
