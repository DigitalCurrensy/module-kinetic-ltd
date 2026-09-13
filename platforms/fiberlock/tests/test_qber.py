from platforms.fiberlock.src.application.qber import Sample, Tape, can_wrap, record
from platforms.fiberlock.src.application.session import WrapRefused


def test_quiet_tape_allows_wrap():
    tape = Tape("span-1", "ks-1")
    record(tape, Sample("2026-09-13T07:00:00Z", 0.04, 0.01, 1024))
    assert can_wrap(tape) is True
    assert tape.aborted is False


def test_high_qber_aborts():
    tape = Tape("span-1", "ks-1")
    try:
        record(tape, Sample("2026-09-13T07:00:00Z", 0.20, 0.01, 1024))
        assert False
    except WrapRefused:
        pass
    assert tape.aborted is True


def test_high_xi_aborts_even_if_qber_low():
    tape = Tape("span-1", "ks-1")
    try:
        record(tape, Sample("2026-09-13T07:00:00Z", 0.03, 0.12, 1024))
        assert False
    except WrapRefused:
        pass
    assert "excess noise" in (tape.abort_reason or "")
