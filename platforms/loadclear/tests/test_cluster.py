"""A locked charger adds no power to the group."""
from platforms.loadclear.src.application.cluster import clusters_from_enrollments
from platforms.loadclear.src.application.enroll import EnrollStore, close_fault, enroll_from_bayline


def test_blocked_asset_does_not_add_pmax():
    store = EnrollStore()
    open_wo = enroll_from_bayline(
        store, tenant_id="t1", evse_id="1", station_id="s1", work_order_id="wo-1", lockout_open=True
    )
    live = enroll_from_bayline(
        store, tenant_id="t1", evse_id="2", station_id="s1", work_order_id="wo-2", lockout_open=True
    )
    close_fault(store, "t1", "2")
    cluster = clusters_from_enrollments("site-s1", [open_wo, live], pmax_per_asset_mw=0.02)
    assert cluster.pmax_mw == 0.02
    assert live.asset_id not in cluster.blocked_assets
    assert open_wo.asset_id in cluster.blocked_assets
