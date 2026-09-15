"""Unitcommit OPF residual slave — a real number for require_cleared.

Power-balance first. Optional one-branch AC mismatch when a line is given.
Not Newton-Raphson. Not ADMM. Not QAOA. build_ising.py stays frozen.
Module Kinetic Ltd.
"""
from __future__ import annotations

from dataclasses import dataclass

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


@dataclass(frozen=True)
class AcBranch:
    """One series branch from slack (V=1, θ=0) to the cluster bus."""
    g_pu: float
    b_pu: float
    v_pu: float = 1.0
    theta_rad: float = 0.0


def residual_mw(snapshot: ZoneSnapshot, assignment: tuple[int, ...]) -> float:
    """|sum_k u_{k,t} pmin_k − α D_t| max over t."""
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


def ac_injection_mw(branch: AcBranch) -> float:
    """P from cluster bus into a single series branch to slack.

    P = V_s V_k (G cos θ + B sin θ) with V_s = 1, θ_s = 0, θ = θ_k.
    """
    return branch.v_pu * (branch.g_pu * __import__("math").cos(branch.theta_rad) + branch.b_pu * __import__("math").sin(branch.theta_rad))


def ac_mismatch_mw(
    snapshot: ZoneSnapshot,
    assignment: tuple[int, ...],
    branch: AcBranch | None = None,
) -> float:
    """max(|P-balance|, |P_inj − P_ac|) when a branch exists; else P-balance."""
    import math

    p_res = residual_mw(snapshot, assignment)
    if branch is None:
        return p_res
    problem = build_ising(snapshot)
    t_horizon = problem.t
    peak = p_res
    for tt in range(t_horizon):
        dispatched = 0.0
        for ck, cluster in enumerate(snapshot.clusters):
            if assignment[idx_u(ck, tt, t_horizon)]:
                dispatched += cluster.pmin_mw
        p_ac = branch.v_pu * (
            branch.g_pu * math.cos(branch.theta_rad) + branch.b_pu * math.sin(branch.theta_rad)
        )
        peak = max(peak, abs(dispatched - p_ac))
    return peak


def solve_residual(
    snapshot: ZoneSnapshot,
    assignment: tuple[int, ...],
    branch: AcBranch | None = None,
) -> OpfSolution:
    problem: IsingProblem = build_ising(snapshot)
    value = ac_mismatch_mw(snapshot, assignment, branch) if branch is not None else residual_mw(snapshot, assignment)
    return OpfSolution(residual_mw=value, spin_count=problem.n)
