"""A mismatch is refused."""
from platforms.unitcommit.src.application.apply_derate import apply_derates, from_flexible
from platforms.unitcommit.src.application.build_ising import Cluster, OpfSolution, ZoneSnapshot
from platforms.unitcommit.src.application.clearance import build_and_clear
from platforms.loadclear.src.application.cluster import FlexibleCluster


def test_derate_shrinks_pmax_before_clearance():
    flex = FlexibleCluster("a", pmin_mw=10, pmax_mw=50, c_nl=10, c_su=40, mut_steps=2, initial_on=1)
    cluster = from_flexible(flex)

    class _D:
        cluster_id = "a"
        factor = 0.4

    shrunk = apply_derates(cluster, [_D()])
    assert shrunk.pmax_mw == 20.0

    snap = ZoneSnapshot(
        clusters=(shrunk, Cluster("b", 8, 30, 15, 25, 1, 1)),
        demand_mw=(20.0, 22.0),
        reserve_mw=(8.0, 8.0),
        interval_s=900,
    )
    refused = build_and_clear(
        run_id="r1",
        snapshot=snap,
        opf=OpfSolution(residual_mw=9.0, spin_count=8),
        assignment_count=8,
        tolerance_mw=1.0,
        time_source="csac",
        wrapped=True,
    )
    assert refused.status == "refused"
    cleared = build_and_clear(
        run_id="r2",
        snapshot=snap,
        opf=OpfSolution(residual_mw=0.2, spin_count=8),
        assignment_count=8,
        tolerance_mw=1.0,
        time_source="csac",
        wrapped=True,
    )
    assert cleared.status == "cleared"
