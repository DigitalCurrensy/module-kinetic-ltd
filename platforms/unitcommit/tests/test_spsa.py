"""The adjustment stays at the center and moves when it starts away from it."""
from platforms.unitcommit.src.application.build_ising import Cluster, ZoneSnapshot, build_ising
from platforms.unitcommit.src.application.qaoa import DepthRefused, from_ising
from platforms.unitcommit.src.application.spsa import optimize, step, surrogate_loss


def _problem():
    snap = ZoneSnapshot(
        clusters=(Cluster("a", pmin_mw=5.0, pmax_mw=10.0, c_nl=1.0, c_su=2.0),),
        demand_mw=(12.5,),
        reserve_mw=(1.0,),
        interval_s=900,
    )
    return build_ising(snap)


def test_optimize_keeps_width_and_depth():
    problem = _problem()
    circuit = optimize(problem, p=1, steps=3)
    assert circuit.n == problem.n == 2
    assert circuit.p == 1
    assert circuit.mixer == "x"


def test_step_stays_at_the_pull_and_moves_away_from_it():
    problem = _problem()
    start = from_ising(problem, p=1)
    g0 = (start.layers[0].gamma,)
    b0 = (start.layers[0].beta,)
    parked = step(problem, g0, b0, a=0.05, c=0.05, seed=3)
    assert parked.loss == surrogate_loss(problem, parked.gammas, parked.betas)
    assert parked.gammas == g0
    assert parked.betas == b0
    moved = step(problem, (0.9,), (0.1,), a=0.05, c=0.05, seed=3)
    assert moved.gammas != (0.9,)


def test_bad_depth_refused():
    problem = _problem()
    try:
        step(problem, (0.1, 0.2, 0.3, 0.4), (0.1, 0.2, 0.3, 0.4), a=0.01, c=0.01, seed=1)
        assert False
    except DepthRefused:
        pass
