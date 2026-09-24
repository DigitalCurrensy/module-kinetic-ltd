"""Do the power numbers add up?

This is the mismatch on one site. It is not a full power-flow solver.
"""
from __future__ import annotations

from dataclasses import dataclass

from platforms.unitcommit.src.application.build_ising import ZoneSnapshot, idx_u


@dataclass(frozen=True)
class Branch:
    x_pu: float
    limit_mw: float


def injection_mw(snapshot: ZoneSnapshot, assignment: tuple[int, ...], tt: int) -> float:
    dispatched = 0.0
    t_horizon = len(snapshot.demand_mw)
    for ck, cluster in enumerate(snapshot.clusters):
        if assignment[idx_u(ck, tt, t_horizon)]:
            dispatched += cluster.pmin_mw
    return dispatched


def p_mismatch_mw(
    snapshot: ZoneSnapshot,
    assignment: tuple[int, ...],
    *,
    branches: tuple[Branch, ...] = (),
) -> float:
    """Peak |P_inj − α D| plus line overload. Q and |V| stay later."""
    peak = 0.0
    t_horizon = len(snapshot.demand_mw)
    for tt in range(t_horizon):
        inj = injection_mw(snapshot, assignment, tt)
        target = snapshot.alpha * snapshot.demand_mw[tt]
        mismatch = abs(inj - target)
        flow = inj
        thermal = 0.0
        for branch in branches:
            thermal = max(thermal, max(0.0, abs(flow) - branch.limit_mw))
        peak = max(peak, mismatch + thermal)
    return peak
