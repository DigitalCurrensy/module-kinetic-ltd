# Learned loops — Module Kinetic Ltd

Updated 2026-09-24. Agents propose. These shipped.

1. Houses do not merge. Parent `platforms/{house}` is source of truth.
2. Split only after a compiling unit AND an explicit name. Refresh copies new files only. Check blob SHA.
3. Create children on the DigitalCurrensy **user**. Omit Organization field.
4. Loadclear child enroll SHA differs because the child imports `src.application`, not `platforms.loadclear`. Not dirt. Do not rewrite enroll to chase it.
5. No repository-description API in this loop. GitHub About text is a human paste.
6. Four agents on one path = write lock. GET, one commit, GET confirm.
7. CONTINUE after a closed wave is not a new house.
8. Receipt law: OCPP 2.1 `NotifyEvent` only. Periodic stream is not a work order. OCPP 1.6 is not a receipt.
9. Same (tenant, correlation) twice is DuplicateEvent. Work order before lockout is LockoutRequired.
10. Enroll refuses a missing work_order_id. New enrollments start faulted and lockout_open. dispatchable stays false until close_fault.
11. Stream before enroll is missing_receipt. NotifyEvent on the stream handler is stream_is_a_receipt.
12. ARM while lockout_open is DispatchRefused, 422, zero rows. ARM after close_fault writes enrollment armed.
13. Clearance: residual AND `spin_count == assignment_count == n`. A clearance that cannot fail is not a clearance.
14. Critical Cabinetfield derate illegal without a covering calibration. Warning legal without cal.
15. Phasepin ladder: CSAC → PTP < 1 ms → holdover < 4 h → `gps_peer`. GPS is a peer.
16. Fiberlock / Photonseal / Phasepin-outbox refuse `gps_peer`. QBER at or above 0.11 aborts. A literal 0.04 is a fixture.
17. Outbox stores facts that already passed house law. Refused runs are not rows. Signing keys are never stored.
18. HMAC-SHA256 + `hmac.compare_digest`. Empty key on seal raises. Empty key on verify returns False. Not Ed25519. Not a token.
19. Timescale hypertable/compression are best-effort. Failure rolls back that attempt so INSERT can land. No DROP. Unset DATABASE_URL writes 0.
20. Do not open the parked seven. Do not put QAOA on the desk before a residual that can fail.

## Frozen law blobs

| File | Blob |
|---|---|
| `platforms/bayline/src/application/receipt.py` | `49eea447` |
| `platforms/loadclear/src/application/enroll.py` | `078c26c9` |
| `platforms/loadclear/src/application/refuse.py` | `04a48547` |
| `platforms/unitcommit/src/application/build_ising.py` | `55a20615` |
| `platforms/cabinetfield/src/application/derate.py` | `bab6281` |
| `platforms/phasepin/src/application/clock.py` | `14522007` |
| `platforms/fiberlock/src/application/session.py` | `3db938d3` |
| `platforms/photonseal/src/application/meter.py` | `dfb7cced` |

## Where this stopped

Operator desk has Bayline and Loadclear. Next slice is Cabinetfield derate on the desk. No Wellpath.
