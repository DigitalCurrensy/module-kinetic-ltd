"""The on and off plan is built from groups, not from one charger per switch.

On is 1. Off is 0. The power mismatch is checked separately.
"""

from __future__ import annotations

from dataclasses import dataclass, field


class ClearanceError(Exception):
    pass


@dataclass(frozen=True)
class Cluster:
    cluster_id: str
    pmin_mw: float
    pmax_mw: float
    c_nl: float
    c_su: float
    mut_steps: int = 1
    initial_on: int = 0


@dataclass(frozen=True)
class ZoneSnapshot:
    clusters: tuple[Cluster, ...]
    demand_mw: tuple[float, ...]
    reserve_mw: tuple[float, ...]
    interval_s: int
    lambda_logic: float = 50.0
    lambda_mut: float = 40.0
    lambda_r: float = 20.0
    lambda_d: float = 8.0
    alpha: float = 0.4
    normalize: str = "per_unit"


@dataclass(frozen=True)
class IsingProblem:
    h: tuple[float, ...]
    j_coo: tuple[tuple[int, int, float], ...]
    n: int
    n_u: int
    n_v: int
    k: int
    t: int
    index_spec: dict
    penalties: dict


@dataclass(frozen=True)
class OpfSolution:
    residual_mw: float
    spin_count: int


def idx_u(k: int, t: int, t_horizon: int) -> int:
    return k * t_horizon + t


def idx_v(k: int, t: int, t_horizon: int, n_u: int) -> int:
    return n_u + k * t_horizon + t


def _scale(snapshot: ZoneSnapshot) -> float:
    peak = max((c.pmax_mw for c in snapshot.clusters), default=1.0)
    if snapshot.normalize != "per_unit":
        return 1.0
    return peak if peak > 0 else 1.0


def build_ising(snapshot: ZoneSnapshot) -> IsingProblem:
    k = len(snapshot.clusters)
    t_horizon = len(snapshot.demand_mw)
    if t_horizon != len(snapshot.reserve_mw):
        raise ValueError("demand and reserve horizons must match")
    n_u = k * t_horizon
    n_v = k * t_horizon
    n = n_u + n_v
    q = [0.0] * n
    Q: dict[tuple[int, int], float] = {}

    def add_q(i: int, j: int, w: float) -> None:
        if i == j:
            q[i] += w
            return
        a, b = (i, j) if i < j else (j, i)
        Q[(a, b)] = Q.get((a, b), 0.0) + w

    scale = _scale(snapshot)

    for ck, cluster in enumerate(snapshot.clusters):
        for tt in range(t_horizon):
            q[idx_u(ck, tt, t_horizon)] += cluster.c_nl
            q[idx_v(ck, tt, t_horizon, n_u)] += cluster.c_su

    lam_l = snapshot.lambda_logic
    for ck, cluster in enumerate(snapshot.clusters):
        for tt in range(t_horizon):
            u = idx_u(ck, tt, t_horizon)
            v = idx_v(ck, tt, t_horizon, n_u)
            u_prev_bit = cluster.initial_on if tt == 0 else None
            if tt == 0:
                # (u - u0 - v)^2 = u^2 + v^2 + u0^2 - 2u u0 - 2u v + 2 v u0
                add_q(u, u, lam_l)
                add_q(v, v, lam_l)
                q[u] += -2.0 * lam_l * cluster.initial_on
                add_q(u, v, -2.0 * lam_l)
                q[v] += 2.0 * lam_l * cluster.initial_on
            else:
                u_prev = idx_u(ck, tt - 1, t_horizon)
                add_q(u, u, lam_l)
                add_q(u_prev, u_prev, lam_l)
                add_q(v, v, lam_l)
                add_q(u, u_prev, -2.0 * lam_l)
                add_q(u, v, -2.0 * lam_l)
                add_q(u_prev, v, 2.0 * lam_l)
            add_q(v, v, lam_l)
            add_q(v, u, -lam_l)
            if tt == 0:
                q[v] += lam_l * cluster.initial_on
            else:
                add_q(v, idx_u(ck, tt - 1, t_horizon), lam_l)
            _ = u_prev_bit

    lam_m = snapshot.lambda_mut
    for ck, cluster in enumerate(snapshot.clusters):
        mut = max(cluster.mut_steps, 1)
        for tt in range(t_horizon):
            v = idx_v(ck, tt, t_horizon, n_u)
            for tau in range(1, mut):
                if tt + tau >= t_horizon:
                    break
                u_future = idx_u(ck, tt + tau, t_horizon)
                q[v] += lam_m
                add_q(v, u_future, -lam_m)

    for tt in range(t_horizon):
        caps = [c.pmax_mw / scale for c in snapshot.clusters]
        pmins = [c.pmin_mw / scale for c in snapshot.clusters]
        r = snapshot.reserve_mw[tt] / scale
        d = snapshot.alpha * snapshot.demand_mw[tt] / scale
        for i, ci in enumerate(snapshot.clusters):
            ui = idx_u(i, tt, t_horizon)
            q[ui] += snapshot.lambda_r * (caps[i] ** 2 - 2.0 * caps[i] * r)
            q[ui] += snapshot.lambda_d * (pmins[i] ** 2 - 2.0 * pmins[i] * d)
            for j in range(i + 1, k):
                uj = idx_u(j, tt, t_horizon)
                add_q(ui, uj, 2.0 * snapshot.lambda_r * caps[i] * caps[j])
                add_q(ui, uj, 2.0 * snapshot.lambda_d * pmins[i] * pmins[j])

    h = [0.0] * n
    j_coo: list[tuple[int, int, float]] = []
    for i in range(n):
        h[i] += 0.5 * q[i]
    for (i, j), w in Q.items():
        h[i] += 0.25 * w
        h[j] += 0.25 * w
        j_coo.append((i, j, 0.25 * w))

    return IsingProblem(
        h=tuple(h),
        j_coo=tuple(j_coo),
        n=n,
        n_u=n_u,
        n_v=n_v,
        k=k,
        t=t_horizon,
        index_spec={"K": k, "T": t_horizon, "n_u": n_u, "n_v": n_v, "n": n},
        penalties={
            "p_logic": snapshot.lambda_logic,
            "p_mut": snapshot.lambda_mut,
            "p_reserve": snapshot.lambda_r,
            "p_demand": snapshot.lambda_d,
            "normalize": snapshot.normalize,
        },
    )


def can_clear(problem: IsingProblem, opf: OpfSolution, tolerance_mw: float, assignment_count: int) -> bool:
    if opf.residual_mw > tolerance_mw:
        return False
    if assignment_count != problem.n or opf.spin_count != problem.n:
        return False
    return True


def require_cleared(problem: IsingProblem, opf: OpfSolution, tolerance_mw: float, assignment_count: int) -> None:
    if not can_clear(problem, opf, tolerance_mw, assignment_count):
        raise ClearanceError("run cannot reach cleared: residual or spin_count mismatch")
