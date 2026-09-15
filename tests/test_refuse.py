from platforms.unitcommit.src.application.build_ising import Cluster, ZoneSnapshot, build_ising
from platforms.unitcommit.src.application.clearance import build_and_clear
from platforms.unitcommit.src.application.outbox import UnclearedRun, Outbox, enqueue_cleared_run
from platforms.unitcommit.src.application.qaoa import decode_assignment
from platforms.unitcommit.src.application.residual import solve_residual


def test_tight_tolerance_refuses_and_skips_outbox():
    snapshot = ZoneSnapshot(
        clusters=(Cluster("a", pmin_mw=0.0085, pmax_mw=0.017, c_nl=1.0, c_su=2.0),),
        demand_mw=(0.01,),
        reserve_mw=(0.005,),
        interval_s=900,
    )
    problem = build_ising(snapshot)
    assignment = decode_assignment(problem)
    opf = solve_residual(snapshot, assignment)
    assert opf.residual_mw > 0.001
    run = build_and_clear(
        run_id="run-refuse",
        snapshot=snapshot,
        opf=opf,
        assignment_count=opf.spin_count,
        tolerance_mw=0.001,
        time_source="csac",
        wrapped=True,
    )
    assert run.status == "refused"
    try:
        enqueue_cleared_run(Outbox(), run, tenant_id="t1", event_id="evt-refuse")
        assert False
    except UnclearedRun:
        pass
