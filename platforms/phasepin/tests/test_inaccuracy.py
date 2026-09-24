"""A missing clock error is not a pass. One millisecond is too wide."""
from platforms.phasepin.src.application.clock import pin_time
from platforms.phasepin.src.application.inaccuracy import attach_inaccuracy, grade_inaccuracy


def test_missing_tlv_is_not_refuse():
    assert grade_inaccuracy(None) == "missing"


def test_profile_in_spec():
    assert grade_inaccuracy(250) == "profile_in_spec"
    assert grade_inaccuracy(1_000) == "profile_in_spec"


def test_phasepin_ok_but_not_profile():
    assert grade_inaccuracy(50_000) == "phasepin_ok"


def test_too_wide():
    assert grade_inaccuracy(2_000_000) == "too_wide"


def test_attach_does_not_change_ladder():
    pin = pin_time(
        observed_at="2026-09-13T01:00:00Z",
        csac_ok=True,
        ptp_offset_ns=120,
        holdover_s=0,
        gps_offset_ns=40,
    )
    q = attach_inaccuracy(pin, 400)
    assert q.pin.time_source == "csac"
    assert q.grade == "profile_in_spec"
