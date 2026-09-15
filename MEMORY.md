# MEMORY — Module Kinetic Ltd

Loop rule: rewrite this file when a parent SHA lands. Code is law. Docs lag is dirt.

- Company: Module Kinetic Ltd
- Parent: DigitalCurrensy/module-kinetic-ltd main (this commit)
- Retired slug: omni-renewal-engine (redirect only; do not build there)
- Brand: Deep Slate #121316, Grid Amber #FFB000, Phosphor Green #00FF66, Off-White #F4F4F6
- Slogan (not the company name): THE GRID IS BROKEN. WE ARE THE RENEWAL ENGINE.
- Live children (heads, 2026-09-15):
  - DigitalCurrensy/bayline `bb8da343`
  - DigitalCurrensy/loadclear `7608be91` (enroll child vs parent 078c26c9 is import-path, not dirt)
  - DigitalCurrensy/unitcommit `c196f558` (shots.py a36a5099 + test_shots.py 95970f42 MATCH)
  - DigitalCurrensy/cabinetfield `79f1ed58` (ingest.py 7f2164ab + test_ingest.py 0a510f8a MATCH)
  - DigitalCurrensy/phasepin `835eb61f` (tti.py ee6960b9 + test_tti.py a393cf1d MATCH)
  - DigitalCurrensy/fiberlock `fe911896` (tape.py c5d80817 + test_tape.py 63be1a67 MATCH)
  - DigitalCurrensy/photonseal `d15f23a8` (key.py 7f79a74c + test_key.py e5c3ff59 MATCH)
- Persist wave CLOSED. Desk bind drains seven outboxes; second pass writes 0; drain_live writes 0 without DATABASE_URL.
- W0–W6 CLOSED on the desk: snapshot.alpha, pg hook, refuse path, Observation ingest, PHOTONSEAL_KEY, operator TTI, tape QBER.
- Bind uses signing_key_from_env, tti_from_operator(400), qber_from_tape({"qber": 0.04}).
- Drain ALLOWED_KINDS includes time_pin + commitment_run. No DROP/TRUNCATE. Retain 400d, compress 7d.
- Parent `platforms/{house}` is source of truth. Houses do not merge. No empty shells.
- Next house only if named. Not Wellpath unless named.
- Build sequence: Bayline receipt → Loadclear enroll/refuse/cluster → Cabinetfield derate → Unitcommit clearance → Phasepin + Fiberlock → Photonseal HMAC.
- Product 6 is Unitcommit (not Unitspin).
- Shared: tenant_id UUID, event_id UUIDv7, outbox, no DROP/TRUNCATE. HMAC stays the tag. No Ed25519.
- Frozen kernels: receipt 49eea447, build_ising 55a20615, derate bab6281, clock 14522007, session 3db938d3, meter dfb7cced.
- Desk skill: artifacts/.grok/skills/module-kinetic-ops + docs/LEARNED.md + AGENTS.md.
