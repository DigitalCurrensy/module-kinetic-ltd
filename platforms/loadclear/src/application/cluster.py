"""Chargers that passed are grouped. A locked charger adds no power.

The group is handed on as plain values. This file does not check the power numbers.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FlexibleCluster:
    cluster_id: str
    pmin_mw: float
    pmax_mw: float
    c_nl: float
    c_su: float
    mut_steps: int = 1
    initial_on: int = 0
    enrolled_assets: tuple[str, ...] = ()
    blocked_assets: tuple[str, ...] = ()


def clusters_from_enrollments(
    cluster_id: str,
    enrollments,
    *,
    pmax_per_asset_mw: float,
    pmin_per_asset_mw: float = 0.0,
    c_nl: float = 10.0,
    c_su: float = 5.0,
    mut_steps: int = 1,
    initial_on: int = 0,
) -> FlexibleCluster:
    enrolled = tuple(e.asset_id for e in enrollments)
    blocked = tuple(e.asset_id for e in enrollments if not e.dispatchable)
    n_live = sum(1 for e in enrollments if e.dispatchable)
    return FlexibleCluster(
        cluster_id=cluster_id,
        pmin_mw=pmin_per_asset_mw * n_live,
        pmax_mw=pmax_per_asset_mw * n_live,
        c_nl=c_nl,
        c_su=c_su,
        mut_steps=mut_steps,
        initial_on=initial_on if n_live else 0,
        enrolled_assets=enrolled,
        blocked_assets=blocked,
    )
