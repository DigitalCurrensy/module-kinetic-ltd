from platforms.unitcommit.src.application.build_ising import Cluster, ZoneSnapshot, build_ising
from platforms.unitcommit.src.application.clearance import build_and_clear
from platforms.unitcommit.src.application.outbox import Outbox, UnclearedRun, enqueue_cleared_run
from platforms.unitcommit.src.application.qaoa import decode_assignment
from platforms.unitcommit.src.application.residual import solve_residual


def test_one_mw_mismatch_refuses():
    snapshot = ZoneSnapshot(
        clusters=(Cluster("a", pmin_mw=0.85, pmax_mw=1.7, c_nl=1.0, c_su=2.0),),
        demand_mw=(5.0,),
        reserve_mw=(0.2,),
        interval_s=900,
    )
    assignment = decode_assignment(build_ising(snapshot))
    opf = solve_residual(snapshot, assignment)
    assert opf.residual_mw > 1.0
    run = build_and_clear(
        run_id="run-site",
        snapshot=snapshot,
        opf=opf,
        assignment_count=opf.spin_count,
        tolerance_mw=1.0,
        time_source="csac",
        wrapped=True,
    )
    assert run.status == "refused"
    try:
        enqueue_cleared_run(Outbox(), run, tenant_id="t1", event_id="evt-site")
        assert False
    except UnclearedRun:
        pass
