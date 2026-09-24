# MEMORY — Module Kinetic Ltd

Loop rule: rewrite this file when a parent SHA lands. Code is law. Docs lag is dirt.
Updated 2026-09-24 after the operator-desk status pass. No kernel edits.

- Company: Module Kinetic Ltd
- Parent: DigitalCurrensy/module-kinetic-ltd main (this commit)
- Retired slug: omni-renewal-engine (redirect only; do not build there)
- Brand: Deep Slate #121316, Grid Amber #FFB000, Phosphor Green #00FF66, Off-White #F4F4F6
- Slogan (not the company name): THE GRID IS BROKEN. WE ARE THE RENEWAL ENGINE.
- Live children (heads, still 2026-09-15; not re-split this pass):
  - DigitalCurrensy/bayline `bb8da343` (http.py 1085a760; receipt 49eea447 frozen)
  - DigitalCurrensy/loadclear `7608be91` (stream.py 44e5ec3d; refuse.py 04a48547; enroll 078c26c9 frozen on parent)
  - DigitalCurrensy/unitcommit `c196f558`
  - DigitalCurrensy/cabinetfield `79f1ed58`
  - DigitalCurrensy/phasepin `835eb61f`
  - DigitalCurrensy/fiberlock `fe911896`
  - DigitalCurrensy/photonseal `d15f23a8`
- Persist wave CLOSED. DSN drain CLOSED on FakeConn and PGLite. No Timescale URL was pasted. Unset URL writes 0. No DROP/TRUNCATE.
- Parent law W0–W6 CLOSED: snapshot.alpha, pg hook, refuse path, Observation ingest, PHOTONSEAL_KEY, operator TTI, tape QBER.
- Operator desk CLOSED through Loadclear only: NotifyEvent → lockout → work order → enroll → stream attach. ARM refused while lockout_open (0 writes). close_fault then ARM writes enrollment armed.
- Operator desk NOT started: Cabinetfield derate, Unitcommit clearance, Phasepin pin, Fiberlock wrap, Photonseal seal.
- Houses do not merge. No Wellpath.
- Next named slice: Cabinetfield derate on the desk. Critical without a calibration row refuses. derate.py bab6281 stays frozen.
- Frozen kernels: receipt 49eea447, enroll 078c26c9, refuse 04a48547, build_ising 55a20615, derate bab6281, clock 14522007, session 3db938d3, meter dfb7cced.
- Product 6 is Unitcommit (not Unitspin).
- Shared: tenant_id UUID, event_id UUID, outbox, HMAC-SHA256. No Ed25519. No token.
- Completion (honest, 2026-09-24): parent law ~78%. Operator desk ~30% (2 of 7 houses). Real iron / live DSN ~20%. Sellable clearance ~10%. Parked seven houses 0% on purpose.
