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


def test_step_moves_angles():
    problem = _problem()
    start = from_ising(problem, p=1)
    g0 = (start.layers[0].gamma,)
    b0 = (start.layers[0].beta,)
    landed = step(problem, g0, b0, a=0.05, c=0.05, seed=3)
    assert landed.loss == surrogate_loss(problem, landed.gammas, landed.betas)
    assert landed.gammas != g0 or landed.betas != b0


def test_bad_depth_refused():
    problem = _problem()
    try:
        step(problem, (0.1, 0.2, 0.3, 0.4), (0.1, 0.2, 0.3, 0.4), a=0.01, c=0.01, seed=1)
        assert False
    except DepthRefused:
        pass
