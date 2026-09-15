# MEMORY — Module Kinetic Ltd

Loop rule: rewrite this file when a parent SHA lands. Code is law. Docs lag is dirt.

- Company: Module Kinetic Ltd
- Parent: DigitalCurrensy/module-kinetic-ltd main (this commit)
- Retired slug: omni-renewal-engine (redirect only; do not build there)
- Brand: Deep Slate #121316, Grid Amber #FFB000, Phosphor Green #00FF66, Off-White #F4F4F6
- Slogan (not the company name): THE GRID IS BROKEN. WE ARE THE RENEWAL ENGINE.
- Live children (heads, 2026-09-14):
  - DigitalCurrensy/bayline `bb8da343`
  - DigitalCurrensy/loadclear `7608be91` (enroll child vs parent 078c26c9 is import-path, not dirt)
  - DigitalCurrensy/unitcommit `c196f558` (shots.py a36a5099 + test_shots.py 95970f42 MATCH)
  - DigitalCurrensy/cabinetfield `749ecfdc`
  - DigitalCurrensy/phasepin `540fc525`
  - DigitalCurrensy/fiberlock `407f8d7e`
  - DigitalCurrensy/photonseal `05ec3c75`
- Persist wave CLOSED. Desk bind drains seven outboxes; second pass writes 0.
- Bind residual uses snapshot.alpha, not a 0.4 literal.
- Drain ALLOWED_KINDS includes time_pin + commitment_run.
- W1 next: desk/pg.py DATABASE_URL writer (in-memory if unset, no DROP).
- Parent `platforms/{house}` is source of truth. Houses do not merge. No empty shells.
- Next house only if named. Not Wellpath unless named.
- Build sequence: Bayline receipt → Loadclear enroll/refuse/cluster → Cabinetfield derate → Unitcommit clearance → Phasepin + Fiberlock → Photonseal HMAC.
- Product 6 is Unitcommit (not Unitspin).
- Shared: tenant_id UUID, event_id UUIDv7, outbox, no DROP/TRUNCATE. HMAC stays the tag. No Ed25519.
- Frozen kernels: receipt 49eea447, build_ising 55a20615, derate bab6281, clock 14522007, session 3db938d3.
- Desk skill: artifacts/.grok/skills/module-kinetic-ops + docs/LEARNED.md + AGENTS.md.
