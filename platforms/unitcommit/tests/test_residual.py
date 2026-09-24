"""The mismatch number can fail."""
from platforms.unitcommit.src.application.build_ising import Cluster, ZoneSnapshot, build_ising
from platforms.unitcommit.src.application.residual import AssignmentWidth, solve_residual


def _snap():
    return ZoneSnapshot(
        clusters=(Cluster("a", pmin_mw=5.0, pmax_mw=10.0, c_nl=1.0, c_su=2.0),),
        demand_mw=(12.5,),
        reserve_mw=(1.0,),
        interval_s=900,
    )


def test_residual_fills_opf_solution():
    snap = _snap()
    problem = build_ising(snap)
    assignment = (1,) + (0,) * (problem.n - 1)
    opf = solve_residual(snap, assignment)
    assert opf.spin_count == problem.n
    assert opf.residual_mw == 0.0


def test_width_mismatch_refused():
    try:
        solve_residual(_snap(), (1,))
        assert False
    except AssignmentWidth:
        pass
