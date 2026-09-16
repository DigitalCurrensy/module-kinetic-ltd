# MEMORY — Module Kinetic Ltd

Loop rule: rewrite this file when a parent SHA lands. Code is law. Docs lag is dirt.

- Company: Module Kinetic Ltd
- Parent: DigitalCurrensy/module-kinetic-ltd main (this commit)
- Retired slug: omni-renewal-engine (redirect only; do not build there)
- Brand: Deep Slate #121316, Grid Amber #FFB000, Phosphor Green #00FF66, Off-White #F4F4F6
- Slogan (not the company name): THE GRID IS BROKEN. WE ARE THE RENEWAL ENGINE.
- Live children (heads, 2026-09-15):
  - DigitalCurrensy/bayline `bb8da343` (http.py 1085a760 + test_http.py MATCH; receipt 49eea447 frozen)
  - DigitalCurrensy/loadclear `7608be91` (stream.py 44e5ec3d + test_stream.py 10a401b8 MATCH; enroll 078c26c9 frozen on parent)
  - DigitalCurrensy/unitcommit `c196f558` (shots.py a36a5099 + test_shots.py 95970f42 MATCH)
  - DigitalCurrensy/cabinetfield `79f1ed58` (ingest.py 7f2164ab + test_ingest.py 0a510f8a MATCH)
  - DigitalCurrensy/phasepin `835eb61f` (tti.py ee6960b9 + test_tti.py a393cf1d MATCH)
  - DigitalCurrensy/fiberlock `fe911896` (tape.py c5d80817 + test_tape.py 63be1a67 MATCH)
  - DigitalCurrensy/photonseal `d15f23a8` (key.py 7f79a74c + test_key.py e5c3ff59 MATCH)
- Persist wave CLOSED. DSN drain CLOSED.
- Desk CSMS: NotifyEvent 2.1 → lockout → work order → enroll. Stream attach after enroll writes enrollment only; dispatchable stays false while faulted. NotifyEvent is not a stream. 1.6 stream refused. enroll.py 078c26c9 frozen. stream.py 44e5ec3d already on child.
- Houses do not merge. No Wellpath.
- Frozen kernels: receipt 49eea447, build_ising 55a20615, derate bab6281, clock 14522007, session 3db938d3, meter dfb7cced.
- Product 6 is Unitcommit (not Unitspin).
- Shared: tenant_id UUID, event_id UUIDv7, outbox, no DROP/TRUNCATE. HMAC stays the tag. No Ed25519.
