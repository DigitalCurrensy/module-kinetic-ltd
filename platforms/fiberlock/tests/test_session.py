from platforms.fiberlock.src.application.session import WrapRefused, wrap_control_path


def test_wrap_under_qber():
    session = wrap_control_path("span-4", "ks-1", 0.04, 256)
    assert session.wrapped is True


def test_refuse_high_qber():
    try:
        wrap_control_path("span-4", "ks-2", 0.15, 256)
        assert False
    except WrapRefused as exc:
        assert exc.http_status == 422
