"""Desk bind — seven kernels + seven outboxes, one run, no house merge.

Bayline receipt → Loadclear enroll/cluster → Cabinetfield derate
→ Unitcommit build+clear → Phasepin pin → Fiberlock wrap → Photonseal HMAC.
"""
import os

from desk.drain import DrainStore, drain_outbox
from desk.pg import drain_live
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
from platforms.unitcommit.src.application.build_ising import Cluster, ZoneSnapshot, build_ising
from platforms.unitcommit.src.application.clearance import build_and_clear
from platforms.unitcommit.src.application.from_clusters import clusters_from_flex
from platforms.unitcommit.src.application.outbox import Outbox as UnitOutbox, UnclearedRun, enqueue_cleared_run
from platforms.unitcommit.src.application.qaoa import decode_assignment
from platforms.unitcommit.src.application.residual import solve_residual
from platforms.unitcommit.src.application.spsa import optimize


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
    bay_box = BaylineOutbox()
    wo = enqueue_work_order(bay_box, receipt, "evt-wo")
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
    load_box = LoadclearOutbox()
    enq = enqueue_enrollment(load_box, enrollment, "evt-en")
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
    cab_box = CabinetOutbox()
    dr = enqueue_derate(cab_box, derate, tenant_id="t1", event_id="evt-dr")
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
    problem = build_ising(snapshot)
    circuit = optimize(problem, p=1, steps=3)
    assert circuit.n == problem.n
    assert circuit.p == 1
    assignment = decode_assignment(problem)
    assert len(assignment) == problem.n
    opf = solve_residual(snapshot, assignment)
    dispatched = (0.01 * 0.85) if assignment[0] else 0.0
    assert opf.residual_mw == abs(dispatched - snapshot.alpha * snapshot.demand_mw[0])
    pin = pin_time(
        observed_at="2026-09-13T23:00:00Z",
        csac_ok=True,
        ptp_offset_ns=120,
        holdover_s=0,
        gps_offset_ns=40,
    )
    quality = attach_inaccuracy(pin, 400)
    assert quality.grade == "profile_in_spec"
    phase_box = PhaseOutbox()
    pp = enqueue_pin(phase_box, pin, tenant_id="t1", event_id="evt-pin")
    assert pp.time_source == "csac"

    session = wrap_from_pin("span-4", "ks-1", 0.04, 256, quality)
    assert session.wrapped is True
    fiber_box = FiberOutbox()
    wr = enqueue_wrap(fiber_box, session, tenant_id="t1", event_id="evt-wr")
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
    unit_box = UnitOutbox()
    cr = enqueue_cleared_run(unit_box, run, tenant_id="t1", event_id="evt-uc")
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
    seal_box = SealOutbox()
    sm = enqueue_interval(seal_box, interval, tenant_id="t1", event_id="evt-sm")
    assert sm.signature == interval.signature

    store = DrainStore()
    observed = "2026-09-13T23:00:00Z"
    written = 0
    for box in (bay_box, load_box, cab_box, phase_box, fiber_box, unit_box, seal_box):
        written += drain_outbox(store, box, observed_at=observed)
    assert written == 7
    assert len(store.rows) == 7
    again = 0
    for box in (bay_box, load_box, cab_box, phase_box, fiber_box, unit_box, seal_box):
        again += drain_outbox(store, box, observed_at=observed)
    assert again == 0
    os.environ.pop("DATABASE_URL", None)
    assert drain_live(store.rows) == 0


def test_tight_tolerance_refuses_and_blocks_outbox():
    snapshot = ZoneSnapshot(
        clusters=(Cluster("a", pmin_mw=0.0085, pmax_mw=0.017, c_nl=1.0, c_su=2.0),),
        demand_mw=(0.01,),
        reserve_mw=(0.005,),
        interval_s=900,
    )
    assignment = decode_assignment(build_ising(snapshot))
    opf = solve_residual(snapshot, assignment)
    assert opf.residual_mw > 0.0
    run = build_and_clear(
        run_id="run-refuse",
        snapshot=snapshot,
        opf=opf,
        assignment_count=opf.spin_count,
        tolerance_mw=0.0,
        time_source="csac",
        wrapped=True,
    )
    assert run.status == "refused"
    try:
        enqueue_cleared_run(UnitOutbox(), run, tenant_id="t1", event_id="evt-refuse")
        assert False
    except UnclearedRun:
        pass
