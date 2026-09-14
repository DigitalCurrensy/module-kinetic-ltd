from platforms.phasepin.src.application.clock import pin_time
from platforms.phasepin.src.application.outbox import (
    DuplicateOutboxEvent,
    GpsPeerRefused,
    MissingPin,
    Outbox,
    enqueue_pin,
)


def test_enqueue_requires_pin():
    try:
        enqueue_pin(Outbox(), None, tenant_id="t1", event_id="evt-1")
        assert False
    except MissingPin:
        pass


def test_enqueue_refuses_gps_peer():
    pin = pin_time(
        observed_at="2026-09-13T23:00:00Z",
        csac_ok=False,
        ptp_offset_ns=5_000_000,
        holdover_s=20_000,
        gps_offset_ns=40,
    )
    assert pin.time_source == "gps_peer"
    try:
        enqueue_pin(Outbox(), pin, tenant_id="t1", event_id="evt-1")
        assert False
    except GpsPeerRefused:
        pass


def test_enqueue_idempotent_on_event_id():
    pin = pin_time(
        observed_at="2026-09-13T23:00:00Z",
        csac_ok=True,
        ptp_offset_ns=120,
        holdover_s=0,
        gps_offset_ns=40,
    )
    box = Outbox()
    row = enqueue_pin(box, pin, tenant_id="t1", event_id="evt-1")
    assert row.time_source == "csac"
    assert box.by_event("t1", "evt-1") is row
    try:
        enqueue_pin(box, pin, tenant_id="t1", event_id="evt-1")
        assert False
    except DuplicateOutboxEvent:
        pass
