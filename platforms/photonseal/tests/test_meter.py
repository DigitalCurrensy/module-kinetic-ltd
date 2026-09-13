from platforms.photonseal.src.application.meter import SealRefused, seal_from_run, seal_interval


class _Run:
    def __init__(self, status, time_source, wrapped=True):
        self.status = status
        self.time_source = time_source
        self.wrapped = wrapped


def test_seal_csac_interval():
    interval = seal_interval(
        meter_id="m-1",
        interval_start="2026-09-13T01:00:00Z",
        interval_s=900,
        watt_hours=12.5,
        time_source="csac",
        signing_key="k",
    )
    assert interval.kind == "signed_meter"
    assert len(interval.signature) == 64


def test_refuse_gps_peer():
    try:
        seal_interval(
            meter_id="m-1",
            interval_start="2026-09-13T01:00:00Z",
            interval_s=900,
            watt_hours=12.5,
            time_source="gps_peer",
            signing_key="k",
        )
        assert False
    except SealRefused:
        pass


def test_seal_from_cleared_wrapped_run():
    interval = seal_from_run(
        run=_Run("cleared", "csac", True),
        meter_id="m-1",
        interval_start="2026-09-13T01:00:00Z",
        interval_s=900,
        watt_hours=12.5,
        signing_key="k",
    )
    assert len(interval.signature) == 64


def test_refuse_uncleared_run():
    try:
        seal_from_run(
            run=_Run("refused", "csac", True),
            meter_id="m-1",
            interval_start="2026-09-13T01:00:00Z",
            interval_s=900,
            watt_hours=12.5,
            signing_key="k",
        )
        assert False
    except SealRefused:
        pass


def test_refuse_unwrapped_run():
    try:
        seal_from_run(
            run=_Run("cleared", "csac", False),
            meter_id="m-1",
            interval_start="2026-09-13T01:00:00Z",
            interval_s=900,
            watt_hours=12.5,
            signing_key="k",
        )
        assert False
    except SealRefused:
        pass
