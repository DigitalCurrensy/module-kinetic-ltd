"""The on and off plan is built from groups."""
from platforms.unitcommit.src.application.build_ising import (
    ClearanceError,
    Cluster,
    OpfSolution,
    ZoneSnapshot,
    build_ising,
    can_clear,
    idx_u,
    idx_v,
    require_cleared,
)


def _snap():
    return ZoneSnapshot(
        clusters=(
            Cluster("a", pmin_mw=10, pmax_mw=50, c_nl=10, c_su=40, mut_steps=2, initial_on=0),
            Cluster("b", pmin_mw=8, pmax_mw=30, c_nl=15, c_su=25, mut_steps=1, initial_on=1),
        ),
        demand_mw=(55.0, 60.0),
        reserve_mw=(40.0, 40.0),
        interval_s=900,
    )


def test_build_ising_shapes():
    problem = build_ising(_snap())
    assert problem.index_spec == {"K": 2, "T": 2, "n_u": 4, "n_v": 4, "n": 8}
    assert problem.n == 8
    assert len(problem.h) == 8
    assert all(i < j for i, j, _ in problem.j_coo)


def test_startup_coupling_present():
    problem = build_ising(_snap())
    pairs = {(i, j) for i, j, _ in problem.j_coo}
    assert (0, 4) in pairs


def test_index_helpers():
    assert idx_u(1, 1, 2) == 3
    assert idx_v(0, 0, 2, 4) == 4


def test_clearance_gate():
    problem = build_ising(_snap())
    assert can_clear(problem, OpfSolution(0.2, 8), 1.0, 8) is True
    assert can_clear(problem, OpfSolution(2.0, 8), 1.0, 8) is False
    assert can_clear(problem, OpfSolution(0.0, 8), 1.0, 7) is False
    try:
        require_cleared(problem, OpfSolution(2.0, 8), 1.0, 8)
        assert False
    except ClearanceError:
        pass
