"""Unitcommit OPF residual slave — a real number for require_cleared.

P-mismatch from ac_opf (one-island AC injection). Not ADMM. Not QAOA.
build_ising.py stays frozen. Module Kinetic Ltd.
"""
from __future__ import annotations

from platforms.unitcommit.src.application.ac_opf import Branch, p_mismatch_mw
from platforms.unitcommit.src.application.build_ising import (
    IsingProblem,
    OpfSolution,
    ZoneSnapshot,
    build_ising,
)


class ResidualError(Exception):
    code = "residual_error"


class AssignmentWidth(ResidualError):
    code = "assignment_width"


def residual_mw(
    snapshot: ZoneSnapshot,
    assignment: tuple[int, ...],
    *,
    branches: tuple[Branch, ...] = (),
) -> float:
    problem = build_ising(snapshot)
    if len(assignment) != problem.n:
        raise AssignmentWidth(f"assignment width {len(assignment)} != n={problem.n}")
    return p_mismatch_mw(snapshot, assignment, branches=branches)


def solve_residual(
    snapshot: ZoneSnapshot,
    assignment: tuple[int, ...],
    *,
    branches: tuple[Branch, ...] = (),
) -> OpfSolution:
    problem: IsingProblem = build_ising(snapshot)
    return OpfSolution(
        residual_mw=residual_mw(snapshot, assignment, branches=branches),
        spin_count=problem.n,
    )
