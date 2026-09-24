"""A passed power check is saved once. A mismatch is not a row."""
from platforms.unitcommit.src.application.outbox import (
    DuplicateOutboxEvent,
    Outbox,
    UnclearedRun,
    enqueue_cleared_run,
)


class _Run:
    def __init__(self, status, run_id="run-1"):
        self.status = status
        self.run_id = run_id
        self.spin_count = 2
        self.assignment_count = 2
        self.residual_mw = 0.1


def test_enqueue_requires_cleared():
    try:
        enqueue_cleared_run(Outbox(), _Run("refused"), tenant_id="t1", event_id="evt-1")
        assert False
    except UnclearedRun:
        pass


def test_enqueue_idempotent_on_event_id():
    box = Outbox()
    row = enqueue_cleared_run(box, _Run("cleared"), tenant_id="t1", event_id="evt-1")
    assert row.run_id == "run-1"
    assert box.by_event("t1", "evt-1") is row
    try:
        enqueue_cleared_run(box, _Run("cleared"), tenant_id="t1", event_id="evt-1")
        assert False
    except DuplicateOutboxEvent:
        pass
