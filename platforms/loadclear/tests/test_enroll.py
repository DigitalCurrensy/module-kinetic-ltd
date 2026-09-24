"""No repair job, no enrollment. The lock blocks turn-on."""
from platforms.loadclear.src.application.enroll import (
    EnrollStore,
    MissingReceipt,
    attach_stream,
    close_fault,
    enroll_from_bayline,
    try_arm,
)
from platforms.loadclear.src.application.refuse import DispatchRefused


def test_enroll_requires_work_order():
    store = EnrollStore()
    try:
        enroll_from_bayline(store, tenant_id="t1", evse_id="evse-1", station_id="s1", work_order_id=None, lockout_open=True)
        assert False
    except MissingReceipt:
        pass


def test_enroll_yes_arm_no_while_open():
    store = EnrollStore()
    enrollment = enroll_from_bayline(
        store, tenant_id="t1", evse_id="evse-1", station_id="s1", work_order_id="wo-1", lockout_open=True
    )
    assert enrollment.dispatchable is False
    try:
        try_arm(enrollment)
        assert False
    except DispatchRefused as exc:
        assert exc.http_status == 422
        assert exc.code in {"lockout_open", "site_faulted"}


def test_arm_after_fault_clears():
    store = EnrollStore()
    enrollment = enroll_from_bayline(
        store, tenant_id="t1", evse_id="evse-1", station_id="s1", work_order_id="wo-1", lockout_open=True
    )
    attach_stream(store, "t1", "evse-1", 5)
    close_fault(store, "t1", "evse-1")
    result = try_arm(enrollment)
    assert result["decision"] == "ARM"
    assert result["http"] == 200
