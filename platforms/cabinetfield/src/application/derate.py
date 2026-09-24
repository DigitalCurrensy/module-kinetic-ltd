"""Was the cabinet measured?

A serious fault with no calibration for that cabinet and that time is refused.
The result is a factor from 0 to 1. That factor shrinks the power the next check may use.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Severity = Literal["healthy", "warning", "critical"]
FaultClass = Literal["winding_hotspot", "bushing_leak", "core_sat", "pd_burst", "oil_pump", "healthy"]

GAMMA_MHZ_PER_MT = 28.024
D_MHZ = 2870.0


class CabinetfieldError(Exception):
    code = "cabinetfield_error"

    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        if code:
            self.code = code


class CalibrationRequired(CabinetfieldError):
    code = "calibration_required"


@dataclass(frozen=True)
class CalibrationRun:
    run_id: str
    cabinet_id: str
    valid_from: str
    valid_to: str
    baseline_d_mhz: float = D_MHZ


@dataclass(frozen=True)
class Observation:
    cabinet_id: str
    cluster_id: str
    observed_at: str
    f_plus_mhz: float
    f_minus_mhz: float
    temp_c: float
    fault_class: FaultClass
    severity: Severity


@dataclass(frozen=True)
class Derate:
    cabinet_id: str
    cluster_id: str
    factor: float
    severity: Severity
    fault_class: FaultClass
    calibration_run_id: str | None
    b_parallel_ut: float


def covers(cal: CalibrationRun, observed_at: str, cabinet_id: str) -> bool:
    return cal.cabinet_id == cabinet_id and cal.valid_from <= observed_at <= cal.valid_to


def axial_field_ut(obs: Observation) -> float:
    b_mt = (obs.f_plus_mhz - obs.f_minus_mhz) / (2.0 * GAMMA_MHZ_PER_MT)
    return b_mt * 1000.0


def derate_factor(severity: Severity, fault_class: FaultClass) -> float:
    if severity == "healthy" or fault_class == "healthy":
        return 1.0
    if severity == "warning":
        return 0.70 if fault_class == "winding_hotspot" else 0.85
    if fault_class in {"winding_hotspot", "pd_burst"}:
        return 0.0
    return 0.40


def issue_derate(obs: Observation, calibration: CalibrationRun | None) -> Derate:
    if obs.severity == "critical":
        if calibration is None or not covers(calibration, obs.observed_at, obs.cabinet_id):
            raise CalibrationRequired("critical illegal without calibration_run covering observed_at")
    cal_id = None
    if calibration is not None and covers(calibration, obs.observed_at, obs.cabinet_id):
        cal_id = calibration.run_id
    return Derate(
        cabinet_id=obs.cabinet_id,
        cluster_id=obs.cluster_id,
        factor=derate_factor(obs.severity, obs.fault_class),
        severity=obs.severity,
        fault_class=obs.fault_class,
        calibration_run_id=cal_id,
        b_parallel_ut=axial_field_ut(obs),
    )
