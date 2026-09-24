"""The signature is saved once. The key is not in the row."""
from platforms.photonseal.src.application.meter import seal_interval
from platforms.photonseal.src.application.outbox import (
    DuplicateOutboxEvent,
    MissingInterval,
    Outbox,
    enqueue_interval,
)


def test_enqueue_requires_signature():
    try:
        enqueue_interval(Outbox(), None, tenant_id="t1", event_id="evt-1")
        assert False
    except MissingInterval:
        pass


def test_enqueue_idempotent_on_event_id():
    interval = seal_interval(
        meter_id="m-1",
        interval_start="2026-09-13T23:00:00Z",
        interval_s=900,
        watt_hours=12.5,
        time_source="csac",
        signing_key="k",
    )
    box = Outbox()
    row = enqueue_interval(box, interval, tenant_id="t1", event_id="evt-1")
    assert row.kind == "signed_meter"
    assert row.signature == interval.signature
    assert box.by_event("t1", "evt-1") is row
    try:
        enqueue_interval(box, interval, tenant_id="t1", event_id="evt-1")
        assert False
    except DuplicateOutboxEvent:
        pass
