from platforms.fiberlock.src.application.session import WrapRefused, wrap_control_path, wrap_from_pin


class _Pin:
    def __init__(self, time_source):
        self.time_source = time_source


def test_wrap_under_qber():
    session = wrap_control_path("span-4", "ks-1", 0.04, 256)
    assert session.wrapped is True


def test_refuse_high_qber():
    try:
        wrap_control_path("span-4", "ks-2", 0.15, 256)
        assert False
    except WrapRefused as exc:
        assert exc.http_status == 422


def test_wrap_from_csac_pin():
    session = wrap_from_pin("span-4", "ks-3", 0.04, 256, _Pin("csac"))
    assert session.wrapped is True


def test_refuse_gps_peer_pin():
    try:
        wrap_from_pin("span-4", "ks-4", 0.04, 256, _Pin("gps_peer"))
        assert False
    except WrapRefused:
        pass
