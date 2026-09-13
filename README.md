# Module Kinetic Ltd

**MODULE KINETIC LTD**

**THE GRID IS BROKEN. WE ARE THE RENEWAL ENGINE.**

Private company monorepo for fourteen industrial energy houses. Hardware-software tight coupling. Edge-native diagnosis and dispatch. No carbon-accounting SaaS.

Owner: `DigitalCurrensy` · Classification: Confidential
Canonical slug: `DigitalCurrensy/module-kinetic-ltd`
Prior slug `omni-renewal-engine` is retired as a company name. Product house names did not change.

## Repo policy (clear)

**Yes — each house gets its own private repo. Not yet for the unsplit houses.**

| Layer | Repo | SHA |
|-------|------|-----|
| Company desk | `DigitalCurrensy/module-kinetic-ltd` | parent |
| Bayline | `DigitalCurrensy/bayline` | `2aa5c59` |
| Loadclear | `DigitalCurrensy/loadclear` | `8a6dcf1` |
| Unitcommit | `DigitalCurrensy/unitcommit` | `d0ea81c` (8/8) |

Copy `platforms/{slug}/` one-to-one into the child after a compiling first slice AND an explicit split call. Do not delete this parent. Do not merge houses. Do not stand up fourteen empty shells. Next child when called: Cabinetfield.

## Houses

| # | House | Slug | First slice |
|---|-------|------|-------------|
| 1 | Bayline | `bayline` | scan → lockout → work order on OCPP 2.1 |
| 2 | Loadclear | `loadclear` | enroll that EVSE + refuse path |
| 3 | Wellpath | `wellpath` | survey → path (separate house) |
| 4 | Tenderbank | `tenderbank` | consist SOC (separate house) |
| 5 | Ionlattice | `ionlattice` | VQE job (separate house) |
| 6 | Unitcommit | `unitcommit` | clustered Ising + OPF clearance gate |
| 7 | Cabinetfield | `cabinetfield` | ODMR → derate; no critical without calibration |
| 8 | Fiberlock | `fiberlock` | CV-QKD wrap |
| 9 | Coilhold | `coilhold` | MHD surrogate (separate house) |
| 10 | Phasepin | `phasepin` | CSAC + PTP stamp |
| 11 | Nitroforge | `nitroforge` | catalyst bench (separate house) |
| 12 | Photonseal | `photonseal` | signed meter interval |
| 13 | Phononstack | `phononstack` | heat layout (separate house) |
| 14 | Densitywell | `densitywell` | gravimetry fusion (separate house) |

## Build sequence (do not skip)

1. Bayline first receipt on OCPP 2.1 `NotifyEvent` — not 1.6 polling.
2. Enroll that EVSE into Loadclear with a refuse path.
3. Feed Loadclear clusters into Unitcommit. Refuse `cleared` unless OPF residual and spin count match.
4. Cabinetfield derates on the same iron. Refuse `critical` without a calibration row.
5. Phasepin timestamps. Fiberlock wraps control paths where fiber exists.
6. Photonseal settles attested intervals as signed meters, not tokens.
7. Wellpath, Densitywell, Ionlattice, Nitroforge, Phononstack, Tenderbank, Coilhold stay separate houses.

## Shared contracts

- `tenant_id` on every operational row
- ingest idempotent on `event_id` UUIDv7
- outbox for money, parts, firmware, derates, settlement
- edge owns inference; cloud owns identity, parts, registry, settlement
- no `DROP` / `TRUNCATE` in migrations
- brand: `#121316` `#FFB000` `#00FF66` `#F4F4F6`
