# MEMORY — Module Kinetic Ltd

Loop rule: rewrite this file when a parent SHA lands. Code is law. Docs lag is dirt.

- Company: Module Kinetic Ltd
- Parent: DigitalCurrensy/module-kinetic-ltd main `1fc79881`
- Retired slug: omni-renewal-engine (redirect only; do not build there)
- Brand: Deep Slate #121316, Grid Amber #FFB000, Phosphor Green #00FF66, Off-White #F4F4F6
- Slogan (not the company name): THE GRID IS BROKEN. WE ARE THE RENEWAL ENGINE.
- Live children (heads, 2026-09-14):
  - DigitalCurrensy/bayline `bb8da343`
  - DigitalCurrensy/loadclear `7608be91` (enroll child vs parent 078c26c9 is import-path, not dirt)
  - DigitalCurrensy/unitcommit `44061c6d` (shots child refresh is the next 1:1)
  - DigitalCurrensy/cabinetfield `749ecfdc`
  - DigitalCurrensy/phasepin `540fc525`
  - DigitalCurrensy/fiberlock `407f8d7e`
  - DigitalCurrensy/photonseal `05ec3c75`
- Persist wave CLOSED on all seven locked-sequence houses (outbox.py + test 1:1 on each child).
- Desk bind `33b96c21` drains seven outboxes into DrainStore; second pass writes 0.
- Drain ALLOWED_KINDS includes time_pin + commitment_run (house kinds, not renamed).
- Parent `platforms/{house}` is source of truth. Houses do not merge. No empty shells.
- Next house only if named. Not Wellpath unless named.
- Build sequence: Bayline receipt → Loadclear enroll/refuse/cluster → Cabinetfield derate → Unitcommit clearance → Phasepin + Fiberlock → Photonseal HMAC.
- Product 6 is Unitcommit (not Unitspin).
- Shared: tenant_id UUID, event_id UUIDv7, outbox, no DROP/TRUNCATE. HMAC stays the tag. No Ed25519.
- Frozen kernels: receipt 49eea447, build_ising 55a20615, derate bab6281, clock 14522007, session 3db938d3.
- Desk skill: artifacts/.grok/skills/module-kinetic-ops + docs/LEARNED.md + AGENTS.md.
