from platforms.photonseal.src.application.meter import SealRefused, seal_interval


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
    assert interval.signature.startswith("0x")


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
