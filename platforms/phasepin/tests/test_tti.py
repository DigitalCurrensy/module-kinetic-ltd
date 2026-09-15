from platforms.phasepin.src.application.clock import pin_time
from platforms.phasepin.src.application.inaccuracy import attach_inaccuracy
from platforms.phasepin.src.application.tti import BadTti, MissingTti, tti_from_operator


def test_operator_integer_grades_in_spec():
    tti = tti_from_operator(400)
    pin = pin_time(
        observed_at="2026-09-13T23:00:00Z",
        csac_ok=True,
        ptp_offset_ns=120,
        holdover_s=0,
        gps_offset_ns=40,
    )
    quality = attach_inaccuracy(pin, tti)
    assert quality.grade == "profile_in_spec"
    assert quality.total_time_inaccuracy_ns == 400


def test_missing_and_negative_refused():
    try:
        tti_from_operator(None)
        assert False
    except MissingTti:
        pass
    try:
        tti_from_operator(-1)
        assert False
    except BadTti:
        pass
