"""A local atomic clock wins. GPS alone does not."""
from platforms.phasepin.src.application.clock import pin_time


def test_csac_wins():
    pin = pin_time(
        observed_at="2026-09-13T01:00:00Z",
        csac_ok=True,
        ptp_offset_ns=120,
        holdover_s=0,
        gps_offset_ns=40,
    )
    assert pin.time_source == "csac"
    assert pin.offset_ns == 0


def test_gps_is_peer_not_truth():
    pin = pin_time(
        observed_at="2026-09-13T01:00:00Z",
        csac_ok=False,
        ptp_offset_ns=None,
        holdover_s=20_000,
        gps_offset_ns=80,
    )
    assert pin.time_source == "gps_peer"
