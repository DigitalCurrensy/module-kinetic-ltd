"""The cabinet result is saved once."""
from platforms.cabinetfield.src.application.derate import Observation, issue_derate
from platforms.cabinetfield.src.application.outbox import (
    DuplicateOutboxEvent,
    MissingDerate,
    Outbox,
    enqueue_derate,
)


def test_enqueue_requires_derate():
    try:
        enqueue_derate(Outbox(), None, tenant_id="t1", event_id="evt-1")
        assert False
    except MissingDerate:
        pass


def test_enqueue_idempotent_on_event_id():
    obs = Observation(
        "cab-7",
        "cluster-a",
        "2026-09-13T23:00:00Z",
        2872.0,
        2868.0,
        55.0,
        "oil_pump",
        "warning",
    )
    derate = issue_derate(obs, None)
    box = Outbox()
    row = enqueue_derate(box, derate, tenant_id="t1", event_id="evt-1")
    assert row.factor == 0.85
    assert row.fault_class == "oil_pump"
    assert box.by_event("t1", "evt-1") is row
    try:
        enqueue_derate(box, derate, tenant_id="t1", event_id="evt-1")
        assert False
    except DuplicateOutboxEvent:
        pass
