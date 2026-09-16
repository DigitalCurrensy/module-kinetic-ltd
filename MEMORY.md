# MEMORY — Module Kinetic Ltd

Loop rule: rewrite this file when a parent SHA lands. Code is law. Docs lag is dirt.

- Company: Module Kinetic Ltd
- Parent: DigitalCurrensy/module-kinetic-ltd main (this commit)
- Retired slug: omni-renewal-engine (redirect only; do not build there)
- Brand: Deep Slate #121316, Grid Amber #FFB000, Phosphor Green #00FF66, Off-White #F4F4F6
- Slogan (not the company name): THE GRID IS BROKEN. WE ARE THE RENEWAL ENGINE.
- Live children (heads, 2026-09-15):
  - DigitalCurrensy/bayline `bb8da343` (http.py 1085a760; receipt 49eea447 frozen)
  - DigitalCurrensy/loadclear `7608be91` (stream.py 44e5ec3d; refuse.py 04a48547; enroll 078c26c9 frozen on parent)
  - DigitalCurrensy/unitcommit `c196f558`
  - DigitalCurrensy/cabinetfield `79f1ed58`
  - DigitalCurrensy/phasepin `835eb61f`
  - DigitalCurrensy/fiberlock `fe911896`
  - DigitalCurrensy/photonseal `d15f23a8`
- Persist wave CLOSED. DSN drain CLOSED.
- Desk CSMS: NotifyEvent 2.1 → lockout → work order → enroll → stream attach. ARM refused while lockout_open (0 writes, 422). close_fault clears both flags; ARM then writes enrollment armed, dispatchable true. enroll.py 078c26c9 and refuse.py 04a48547 frozen.
- Houses do not merge. No Wellpath.
- Frozen kernels: receipt 49eea447, build_ising 55a20615, derate bab6281, clock 14522007, session 3db938d3, meter dfb7cced.
- Product 6 is Unitcommit (not Unitspin).
- Shared: tenant_id UUID, event_id UUIDv7, outbox, no DROP/TRUNCATE. HMAC stays the tag. No Ed25519.
