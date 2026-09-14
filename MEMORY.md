# MEMORY — Module Kinetic Ltd

Loop rule: rewrite this file when a parent SHA lands. Code is law. Docs lag is dirt.

- Company: Module Kinetic Ltd
- Parent: DigitalCurrensy/module-kinetic-ltd
- Retired slug: omni-renewal-engine (redirect only; do not build there)
- Brand: Deep Slate #121316, Grid Amber #FFB000, Phosphor Green #00FF66, Off-White #F4F4F6
- Slogan (not the company name): THE GRID IS BROKEN. WE ARE THE RENEWAL ENGINE.
- Live children: DigitalCurrensy/bayline `e853163`, DigitalCurrensy/loadclear `906b053`, DigitalCurrensy/unitcommit `39a90797`, DigitalCurrensy/cabinetfield `749ecfd`, DigitalCurrensy/phasepin `540fc525`, DigitalCurrensy/fiberlock `407f8d7`, DigitalCurrensy/photonseal `05ec3c75`
- Persist wave CLOSED on all seven locked-sequence houses (outbox + test on parent and child).
- Parent `platforms/{house}` is source of truth. Houses do not merge. No empty shells.
- No Wellpath unless named.
- Desk bind: tests/test_desk_bind.py chains the seven kernels duck-typed.
- Build sequence: Bayline receipt → Loadclear enroll/refuse/cluster → Unitcommit clearance → Cabinetfield derate → Phasepin + Fiberlock → Photonseal HMAC.
- Product 6 is Unitcommit (not Unitspin).
- Shared: tenant_id UUID, event_id UUIDv7, outbox, no DROP/TRUNCATE.
