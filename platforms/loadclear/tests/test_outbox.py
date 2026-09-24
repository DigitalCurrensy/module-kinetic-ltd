"""The enrollment is saved once."""
from platforms.loadclear.src.application.enroll import EnrollStore, enroll_from_bayline
from platforms.loadclear.src.application.outbox import (
    DuplicateOutboxEvent,
    MissingEnrollment,
    Outbox,
    enqueue_enrollment,
)


def test_enqueue_requires_work_order():
    try:
        enqueue_enrollment(Outbox(), None, "evt-1")
        assert False
    except MissingEnrollment:
        pass


def test_enqueue_idempotent_on_event_id():
    store = EnrollStore()
    enrollment = enroll_from_bayline(
        store,
        tenant_id="t1",
        evse_id="1",
        station_id="s1",
        work_order_id="wo-1",
        lockout_open=True,
    )
    box = Outbox()
    row = enqueue_enrollment(box, enrollment, "evt-1")
    assert row.bayline_work_order_id == "wo-1"
    assert row.asset_id == enrollment.asset_id
    assert box.by_event("t1", "evt-1") is row
    try:
        enqueue_enrollment(box, enrollment, "evt-1")
        assert False
    except DuplicateOutboxEvent:
        pass
