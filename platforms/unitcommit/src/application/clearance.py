"""A mismatch is refused.

A plan of on and off is not a dispatch. The count of that plan must match.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from platforms.unitcommit.src.application.build_ising import (
    ClearanceError,
    IsingProblem,
    OpfSolution,
    ZoneSnapshot,
    build_ising,
    require_cleared,
)

Status = Literal["built", "solved", "cleared", "refused"]


@dataclass(frozen=True)
class CommitmentRun:
    run_id: str
    status: Status
    spin_count: int
    assignment_count: int
    residual_mw: float
    tolerance_mw: float
    time_source: str
    wrapped: bool


def build_and_clear(
    *,
    run_id: str,
    snapshot: ZoneSnapshot,
    opf: OpfSolution,
    assignment_count: int,
    tolerance_mw: float,
    time_source: str,
    wrapped: bool,
) -> CommitmentRun:
    problem = build_ising(snapshot)
    try:
        require_cleared(problem, opf, tolerance_mw, assignment_count)
    except ClearanceError:
        return CommitmentRun(
            run_id=run_id,
            status="refused",
            spin_count=problem.n,
            assignment_count=assignment_count,
            residual_mw=opf.residual_mw,
            tolerance_mw=tolerance_mw,
            time_source=time_source,
            wrapped=wrapped,
        )
    return CommitmentRun(
        run_id=run_id,
        status="cleared",
        spin_count=problem.n,
        assignment_count=assignment_count,
        residual_mw=opf.residual_mw,
        tolerance_mw=tolerance_mw,
        time_source=time_source,
        wrapped=wrapped,
    )
