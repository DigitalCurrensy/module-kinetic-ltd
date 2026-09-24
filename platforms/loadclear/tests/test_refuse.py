"""A locked, hot, empty, or over-limit charger is refused."""
from platforms.loadclear.src.application.refuse import AssetOffer, DispatchInstruction, DispatchRefused, evaluate


def _offer(**kw):
    base = dict(
        asset_id="a1",
        evse_id="1",
        soc=0.6,
        soc_min=0.2,
        soc_max=0.9,
        cycles_used=1.0,
        cycle_budget=10.0,
        temp_c=25.0,
        temp_max_c=50.0,
        export_kw=20.0,
        export_cap_kw=25.0,
        depart_in_s=3600,
        instruction_s=900,
        site_faulted=False,
        lockout_open=False,
    )
    base.update(kw)
    return AssetOffer(**base)


def test_arm_when_quiet():
    evaluate(_offer(), DispatchInstruction("a1", 15.0, 900))


def test_lockout_422():
    try:
        evaluate(_offer(lockout_open=True), DispatchInstruction("a1", 15.0, 900))
        assert False
    except DispatchRefused as exc:
        assert exc.code == "lockout_open"
        assert exc.http_status == 422
