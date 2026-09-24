"""A small sample of the plan stays the same width."""
from platforms.unitcommit.src.application.build_ising import Cluster, ZoneSnapshot, build_ising
from platforms.unitcommit.src.application.qaoa import from_ising
from platforms.unitcommit.src.application.shots import (
    WidthRefused,
    expectation,
    majority,
    prepare,
    probabilities,
)


def _problem():
    snap = ZoneSnapshot(
        clusters=(Cluster("a", pmin_mw=5.0, pmax_mw=10.0, c_nl=1.0, c_su=2.0),),
        demand_mw=(12.5,),
        reserve_mw=(1.0,),
        interval_s=900,
    )
    return build_ising(snap)


def test_prepare_normalized_and_majority_width():
    problem = _problem()
    circuit = from_ising(problem, p=1)
    state = prepare(problem, circuit)
    assert abs(sum(probabilities(state)) - 1.0) < 1e-9
    bits = majority(state, problem.n)
    assert len(bits) == problem.n
    energy = expectation(problem, state)
    assert isinstance(energy, float)


def test_width_cap():
    class _Wide:
        n = 5
        h = (0.0,) * 5
        j_coo = ()

    class _Circ:
        n = 5
        layers = ()

    try:
        prepare(_Wide(), _Circ())
        assert False
    except WidthRefused:
        pass
