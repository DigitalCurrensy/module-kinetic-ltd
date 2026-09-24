"""The cabinet factor shrinks the allowed power before the numbers are checked."""
from __future__ import annotations

from platforms.unitcommit.src.application.build_ising import Cluster


def shrink_cluster(cluster: Cluster, factor: float) -> Cluster:
    if factor < 0 or factor > 1:
        raise ValueError("derate factor must be in [0, 1]")
    return Cluster(
        cluster_id=cluster.cluster_id,
        pmin_mw=cluster.pmin_mw * factor,
        pmax_mw=cluster.pmax_mw * factor,
        c_nl=cluster.c_nl,
        c_su=cluster.c_su,
        mut_steps=cluster.mut_steps,
        initial_on=0 if factor == 0.0 else cluster.initial_on,
    )


def from_flexible(flex) -> Cluster:
    return Cluster(
        cluster_id=flex.cluster_id,
        pmin_mw=flex.pmin_mw,
        pmax_mw=flex.pmax_mw,
        c_nl=flex.c_nl,
        c_su=flex.c_su,
        mut_steps=flex.mut_steps,
        initial_on=flex.initial_on,
    )


def apply_derates(cluster: Cluster, derates) -> Cluster:
    factor = 1.0
    for derate in derates:
        if derate.cluster_id == cluster.cluster_id:
            factor = min(factor, derate.factor)
    return shrink_cluster(cluster, factor)
