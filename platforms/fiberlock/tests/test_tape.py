"""The error rate must be a reading under 0.11."""
from platforms.fiberlock.src.application.session import wrap_from_pin
from platforms.fiberlock.src.application.tape import BadQber, MissingQber, qber_from_tape
from platforms.phasepin.src.application.clock import pin_time
from platforms.phasepin.src.application.inaccuracy import attach_inaccuracy
from platforms.phasepin.src.application.tti import tti_from_operator


def test_tape_qber_wraps():
    qber = qber_from_tape({"span_id": "span-4", "qber": 0.04})
    pin = pin_time(
        observed_at="2026-09-13T23:00:00Z",
        csac_ok=True,
        ptp_offset_ns=120,
        holdover_s=0,
        gps_offset_ns=40,
    )
    quality = attach_inaccuracy(pin, tti_from_operator(400))
    session = wrap_from_pin("span-4", "ks-1", qber, 256, quality)
    assert session.wrapped is True
    assert session.qber == 0.04


def test_missing_and_high_qber_refused():
    try:
        qber_from_tape({})
        assert False
    except MissingQber:
        pass
    try:
        qber_from_tape({"qber": 0.12})
        assert False
    except BadQber:
        pass
