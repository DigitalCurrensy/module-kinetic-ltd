"""The plan description matches the width of the problem."""
from platforms.unitcommit.src.application.build_ising import Cluster, ZoneSnapshot, build_ising
from platforms.unitcommit.src.application.qaoa import (
    DepthRefused,
    WidthMismatch,
    cost,
    decode_assignment,
    from_ising,
)


def _problem():
    snap = ZoneSnapshot(
        clusters=(Cluster("a", pmin_mw=5.0, pmax_mw=10.0, c_nl=1.0, c_su=2.0),),
        demand_mw=(12.5,),
        reserve_mw=(1.0,),
        interval_s=900,
    )
    return build_ising(snap)


def test_from_ising_p1():
    problem = _problem()
    circuit = from_ising(problem, p=1)
    assert circuit.n == problem.n == 2
    assert circuit.p == 1
    assert circuit.mixer == "x"
    assert len(circuit.layers) == 1


def test_p_too_deep_refused():
    try:
        from_ising(_problem(), p=4)
        assert False
    except DepthRefused:
        pass


def test_cost_and_decode_width():
    problem = _problem()
    bits = decode_assignment(problem)
    assert len(bits) == problem.n
    value = cost(problem, bits)
    assert isinstance(value, float)
    try:
        cost(problem, (1,))
        assert False
    except WidthMismatch:
        pass
