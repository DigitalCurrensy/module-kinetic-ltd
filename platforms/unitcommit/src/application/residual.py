"""Unitcommit OPF residual slave — a real number for require_cleared.

Not AC-OPF. Not ADMM. Power-balance residual on the derated snapshot.
build_ising.py stays frozen. Module Kinetic Ltd.
"""
from __future__ import annotations

from platforms.unitcommit.src.application.build_ising import (
    IsingProblem,
    OpfSolution,
    ZoneSnapshot,
    build_ising,
    idx_u,
)


class ResidualError(Exception):
    code = "residual_error"


class AssignmentWidth(ResidualError):
    code = "assignment_width"


def residual_mw(snapshot: ZoneSnapshot, assignment: tuple[int, ...]) -> float:
    """|sum_k u_{k,t} pmin_k − α D_t| max over t. Continuous p,q,V stay later."""
    problem = build_ising(snapshot)
    if len(assignment) != problem.n:
        raise AssignmentWidth(f"assignment width {len(assignment)} != n={problem.n}")
    peak = 0.0
    t_horizon = problem.t
    for tt in range(t_horizon):
        dispatched = 0.0
        for ck, cluster in enumerate(snapshot.clusters):
            u = assignment[idx_u(ck, tt, t_horizon)]
            if u:
                dispatched += cluster.pmin_mw
        target = snapshot.alpha * snapshot.demand_mw[tt]
        peak = max(peak, abs(dispatched - target))
    return peak


def solve_residual(snapshot: ZoneSnapshot, assignment: tuple[int, ...]) -> OpfSolution:
    problem: IsingProblem = build_ising(snapshot)
    return OpfSolution(residual_mw=residual_mw(snapshot, assignment), spin_count=problem.n)
