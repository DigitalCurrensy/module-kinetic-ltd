"""Cabinetfield ingest — a measured row becomes an Observation.

Does not compute a derate. issue_derate.py stays frozen.
Module Kinetic Ltd.
"""
from __future__ import annotations

from platforms.cabinetfield.src.application.derate import Observation

REQUIRED = (
    "cabinet_id",
    "cluster_id",
    "observed_at",
    "f_plus_mhz",
    "f_minus_mhz",
    "temp_c",
    "fault_class",
    "severity",
)


class IngestError(Exception):
    code = "ingest_error"


class MissingField(IngestError):
    code = "missing_field"


def observation_from_row(row: dict) -> Observation:
    missing = [name for name in REQUIRED if name not in row or row[name] in (None, "")]
    if missing:
        raise MissingField(",".join(missing))
    return Observation(
        cabinet_id=str(row["cabinet_id"]),
        cluster_id=str(row["cluster_id"]),
        observed_at=str(row["observed_at"]),
        f_plus_mhz=float(row["f_plus_mhz"]),
        f_minus_mhz=float(row["f_minus_mhz"]),
        temp_c=float(row["temp_c"]),
        fault_class=row["fault_class"],
        severity=row["severity"],
    )
