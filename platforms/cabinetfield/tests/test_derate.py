from platforms.cabinetfield.src.application.derate import (
    CalibrationRequired,
    CalibrationRun,
    Observation,
    issue_derate,
)


def _cal():
    return CalibrationRun("cal-1", "cab-7", "2026-09-01T00:00:00Z", "2026-10-01T00:00:00Z")


def test_critical_requires_calibration():
    obs = Observation(
        "cab-7", "cluster-a", "2026-09-13T01:00:00Z", 2885.0, 2855.0, 68.0, "winding_hotspot", "critical"
    )
    try:
        issue_derate(obs, None)
        assert False
    except CalibrationRequired:
        pass
    derate = issue_derate(obs, _cal())
    assert derate.factor == 0.0
    assert derate.calibration_run_id == "cal-1"


def test_warning_without_cal_is_legal():
    obs = Observation(
        "cab-7", "cluster-a", "2026-09-13T01:00:00Z", 2872.0, 2868.0, 55.0, "oil_pump", "warning"
    )
    derate = issue_derate(obs, None)
    assert derate.factor == 0.85
    assert derate.calibration_run_id is None


def test_critical_expired_cal_refuses():
    obs = Observation(
        "cab-7", "cluster-a", "2026-09-13T01:00:00Z", 2885.0, 2855.0, 68.0, "winding_hotspot", "critical"
    )
    expired = CalibrationRun("cal-old", "cab-7", "2026-07-01T00:00:00Z", "2026-08-01T00:00:00Z")
    try:
        issue_derate(obs, expired)
        assert False
    except CalibrationRequired:
        pass


def test_critical_wrong_cabinet_refuses():
    obs = Observation(
        "cab-7", "cluster-a", "2026-09-13T01:00:00Z", 2885.0, 2855.0, 68.0, "winding_hotspot", "critical"
    )
    other = CalibrationRun("cal-8", "cab-8", "2026-09-01T00:00:00Z", "2026-10-01T00:00:00Z")
    try:
        issue_derate(obs, other)
        assert False
    except CalibrationRequired:
        pass
