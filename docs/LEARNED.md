# Learned loops — Module Kinetic Ltd

Updated 2026-09-13. Agents propose. These shipped.

1. Houses do not merge. Parent `platforms/{house}` is source of truth.
2. Split only after a compiling unit AND an explicit name. Refresh copies new files only. Check blob SHA.
3. Create children on the DigitalCurrensy **user**. Omit Organization field.
4. Loadclear child enroll SHA differs because the child imports `src.application`, not `platforms.loadclear`. Not dirt.
5. No `update_repository` tool. GitHub list Descriptions are paste-only.
6. Four agents on one path = write lock. GET, one PUT, GET confirm.
7. CONTINUE after persist-closed is not a new house. Hygiene or bind only unless a house is named.
8. Heavy (this desk) is stronger than Grok Build for SHA / 1:1 / no-merge.
9. Receipt law: OCPP 2.1 `NotifyEvent` only. Periodic stream is not a work order.
10. Clearance: residual AND `spin_count == assignment_count == n`.
11. Critical Cabinetfield derate illegal without a covering calibration. Warning legal without cal.
12. Phasepin ladder: CSAC → PTP < 1 ms → holdover < 4 h → `gps_peer`. GPS is a peer.
13. Fiberlock / Photonseal / Phasepin-outbox refuse `gps_peer`.
14. Outbox stores facts that already passed house law. Refused runs are not rows. Signing keys are never stored.
15. HMAC-SHA256 + `hmac.compare_digest`. Empty key on verify → False. Not Ed25519. Not a token.

## Frozen law blobs

| File | Blob |
|---|---|
| `platforms/bayline/src/application/receipt.py` | `49eea447` |
| `platforms/unitcommit/src/application/build_ising.py` | `55a20615` |
| `platforms/cabinetfield/src/application/derate.py` | `bab6281` |
| `platforms/phasepin/src/application/clock.py` | `14522007` |
| `platforms/fiberlock/src/application/session.py` | `3db938d3` |
| `platforms/photonseal/src/application/meter.py` | `dfb7cced` |
