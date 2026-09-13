"""Unitcommit intake — duck-typed Loadclear clusters, then Cabinetfield shrink.

Module Kinetic Ltd. No Loadclear import. Houses do not merge.
"""
from __future__ import annotations

from platforms.unitcommit.src.application.apply_derate import apply_derates, from_flexible
from platforms.unitcommit.src.application.build_ising import Cluster


def clusters_from_flex(flex_list, derates=()) -> tuple[Cluster, ...]:
    out: list[Cluster] = []
    for flex in flex_list:
        cluster = from_flexible(flex)
        cluster = apply_derates(cluster, derates)
        out.append(cluster)
    return tuple(out)
