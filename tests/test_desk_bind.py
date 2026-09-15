"""Desk bind — seven kernels + seven outboxes, one run, no house merge.

Bayline receipt → Loadclear enroll/cluster → Cabinetfield derate
→ Unitcommit build+clear → Phasepin pin → Fiberlock wrap → Photonseal HMAC.
"""
from platforms.bayline.src.application.outbox import Outbox as BaylineOutbox, enqueue_work_order
from platforms.bayline.src.application.receipt import (
    Component,
    IncomingMessage,
    NotifyEventRow,
    ReceiptStore,
    Variable,
    ingest,
    open_work_order,
    set_lockout,
)
from platforms.cabinetfield.src.application.derate import Observation, issue_derate
from platforms.cabinetfield.src.application.outbox import Outbox as CabinetOutbox, enqueue_derate
from platforms.fiberlock.src.application.outbox import Outbox as FiberOutbox, enqueue_wrap
from platforms.fiberlock.src.application.session import wrap_from_pin
from platforms.loadclear.src.application.cluster import clusters_from_enrollments
from platforms.loadclear.src.application.enroll import (
    EnrollStore,
    close_fault,
    enroll_from_bayline,
)
from platforms.loadclear.src.application.outbox import Outbox as LoadclearOutbox, enqueue_enrollment
from platforms.phasepin.src.application.clock import pin_time
from platforms.phasepin.src.application.inaccuracy import attach_inaccuracy
from platforms.phasepin.src.application.outbox import Outbox as PhaseOutbox, enqueue_pin
from platforms.photonseal.src.application.meter import seal_from_run, verify_interval
from platforms.photonseal.src.application.outbox import Outbox as SealOutbox, enqueue_interval
from platforms.unitcommit.src.application.build_ising import ZoneSnapshot
from platforms.unitcommit.src.application.clearance import build_and_clear
from platforms.unitcommit.src.application.from_clusters import clusters_from_flex
from platforms.unitcommit.src.application.outbox import Outbox as UnitOutbox, enqueue_cleared_run
from platforms.unitcommit.src.application.residual import solve_residual


def test_desk_bind_cleared_wrapped_sealed():
    receipts = ReceiptStore()
    row = NotifyEventRow(
        event_id=7,
        timestamp="2026-09-13T23:00:00Z",
        trigger="Alerting",
        actual_value="Faulted",
        component=Component("Connector", evse_id=1),
        variable=Variable("AvailabilityState"),
    )
    msg = IncomingMessage(
        tenant_id="t1",
        station_id="s1",
        correlation_id="corr-1",
        protocol="ocpp2.1",
        action="NotifyEvent",
        rows=(row,),
    )
    diagnosed = ingest(receipts, msg)
    assert len(diagnosed) == 1
    set_lockout(receipts, "t1", "corr-1")
    receipt = open_work_order(receipts, msg, row, "wo-1")
    assert receipt.work_order_id == "wo-1"
    wo = enqueue_work_order(BaylineOutbox(), receipt, "evt-wo")
    assert wo.work_order_id == "wo-1"

    enrollments = EnrollStore()
    enrollment = enroll_from_bayline(
        enrollments,
        tenant_id="t1",
        evse_id="1",
        station_id="s1",
        work_order_id=receipt.work_order_id,
        lockout_open=True,
    )
    close_fault(enrollments, "t1", "1")
    enq = enqueue_enrollment(LoadclearOutbox(), enrollment, "evt-en")
    assert enq.bayline_work_order_id == "wo-1"
    flex = clusters_from_enrollments(
        "cluster-a",
        [enrollment],
        pmax_per_asset_mw=0.02,
        pmin_per_asset_mw=0.01,
    )
    assert flex.pmax_mw == 0.02
    assert flex.pmin_mw == 0.01

    obs = Observation(
        "cab-7",
        "cluster-a",
        "2026-09-13T23:00:00Z",
        2872.0,
        2868.0,
        55.0,
        "oil_pump",
        "warning",
    )
    derate = issue_derate(obs, None)
    assert derate.factor == 0.85
    dr = enqueue_derate(CabinetOutbox(), derate, tenant_id="t1", event_id="evt-dr")
    assert dr.factor == 0.85

    uc_clusters = clusters_from_flex((flex,), (derate,))
    assert uc_clusters[0].pmax_mw == 0.02 * 0.85
    assert uc_clusters[0].pmin_mw == 0.01 * 0.85

    snapshot = ZoneSnapshot(
        clusters=uc_clusters,
        demand_mw=(0.01,),
        reserve_mw=(0.005,),
        interval_s=900,
    )
    assignment = (1, 0)
    opf = solve_residual(snapshot, assignment)
    assert opf.residual_mw == abs(0.01 * 0.85 - 0.4 * 0.01)
    pin = pin_time(
        observed_at="2026-09-13T23:00:00Z",
        csac_ok=True,
        ptp_offset_ns=120,
        holdover_s=0,
        gps_offset_ns=40,
    )
    quality = attach_inaccuracy(pin, 400)
    assert quality.grade == "profile_in_spec"
    pp = enqueue_pin(PhaseOutbox(), pin, tenant_id="t1", event_id="evt-pin")
    assert pp.time_source == "csac"

    session = wrap_from_pin("span-4", "ks-1", 0.04, 256, quality)
    assert session.wrapped is True
    wr = enqueue_wrap(FiberOutbox(), session, tenant_id="t1", event_id="evt-wr")
    assert wr.span_id == "span-4"

    run = build_and_clear(
        run_id="run-1",
        snapshot=snapshot,
        opf=opf,
        assignment_count=opf.spin_count,
        tolerance_mw=1.0,
        time_source=pin.time_source,
        wrapped=session.wrapped,
    )
    assert run.status == "cleared"
    cr = enqueue_cleared_run(UnitOutbox(), run, tenant_id="t1", event_id="evt-uc")
    assert cr.run_id == "run-1"

    class _SealRun:
        status = run.status
        wrapped = run.wrapped
        time_source = run.time_source
        grade = quality.grade

    interval = seal_from_run(
        run=_SealRun(),
        meter_id="m-1",
        interval_start="2026-09-13T23:00:00Z",
        interval_s=900,
        watt_hours=12.5,
        signing_key="k",
    )
    assert interval.kind == "signed_meter"
    assert verify_interval(interval, "k") is True
    assert verify_interval(interval, "") is False
    sm = enqueue_interval(SealOutbox(), interval, tenant_id="t1", event_id="evt-sm")
    assert sm.signature == interval.signature
