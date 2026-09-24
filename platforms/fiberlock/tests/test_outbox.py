"""A clean line is saved once."""
from platforms.fiberlock.src.application.outbox import (
    DuplicateOutboxEvent,
    Outbox,
    UnwrappedSession,
    enqueue_wrap,
)
from platforms.fiberlock.src.application.session import wrap_control_path


def test_enqueue_requires_wrapped():
    try:
        enqueue_wrap(Outbox(), None, tenant_id="t1", event_id="evt-1")
        assert False
    except UnwrappedSession:
        pass


def test_enqueue_idempotent_on_event_id():
    session = wrap_control_path("span-4", "ks-1", 0.04, 256)
    box = Outbox()
    row = enqueue_wrap(box, session, tenant_id="t1", event_id="evt-1")
    assert row.span_id == "span-4"
    assert box.by_event("t1", "evt-1") is row
    try:
        enqueue_wrap(box, session, tenant_id="t1", event_id="evt-1")
        assert False
    except DuplicateOutboxEvent:
        pass
