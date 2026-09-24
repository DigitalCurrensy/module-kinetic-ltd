"""A passed record is signed. A failed check is not."""
from platforms.photonseal.src.application.meter import (
    SealRefused,
    seal_from_run,
    seal_interval,
    verify_interval,
)


class _Run:
    def __init__(self, status, time_source, wrapped=True, grade=None):
        self.status = status
        self.time_source = time_source
        self.wrapped = wrapped
        self.grade = grade


def test_seal_and_verify():
    interval = seal_interval(
        meter_id="m-1",
        interval_start="2026-09-13T01:00:00Z",
        interval_s=900,
        watt_hours=12.5,
        time_source="csac",
        signing_key="k",
    )
    assert len(interval.signature) == 64
    assert verify_interval(interval, "k") is True
    assert verify_interval(interval, "wrong") is False
    assert verify_interval(interval, "") is False


def test_refuse_too_wide_grade():
    try:
        seal_from_run(
            run=_Run("cleared", "csac", True, "too_wide"),
            meter_id="m-1",
            interval_start="2026-09-13T01:00:00Z",
            interval_s=900,
            watt_hours=12.5,
            signing_key="k",
        )
        assert False
    except SealRefused:
        pass
