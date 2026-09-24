"""The power mismatch is a number."""
from platforms.unitcommit.src.application.ac_opf import Branch, p_mismatch_mw
from platforms.unitcommit.src.application.build_ising import Cluster, ZoneSnapshot, build_ising
from platforms.unitcommit.src.application.residual import solve_residual


def _snap():
    return ZoneSnapshot(
        clusters=(Cluster("a", pmin_mw=5.0, pmax_mw=10.0, c_nl=1.0, c_su=2.0),),
        demand_mw=(12.5,),
        reserve_mw=(1.0,),
        interval_s=900,
    )


def test_no_branch_matches_energy_balance():
    snap = _snap()
    problem = build_ising(snap)
    assignment = (1,) + (0,) * (problem.n - 1)
    assert p_mismatch_mw(snap, assignment) == 0.0
    assert solve_residual(snap, assignment).residual_mw == 0.0


def test_line_limit_adds_thermal():
    snap = _snap()
    problem = build_ising(snap)
    assignment = (1,) + (0,) * (problem.n - 1)
    hot = p_mismatch_mw(snap, assignment, branches=(Branch(x_pu=0.1, limit_mw=1.0),))
    assert hot == 4.0
