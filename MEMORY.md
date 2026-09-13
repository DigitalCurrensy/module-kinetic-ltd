# MEMORY — Module Kinetic Ltd

Loop rule: rewrite this file when a parent SHA lands. Code is law. Docs lag is dirt.

- Company: Module Kinetic Ltd
- Parent: DigitalCurrensy/module-kinetic-ltd main `b4590c7`
- Retired slug: omni-renewal-engine (redirect only; do not build there)
- Brand: Deep Slate #121316, Grid Amber #FFB000, Phosphor Green #00FF66, Off-White #F4F4F6
- Slogan (not the company name): THE GRID IS BROKEN. WE ARE THE RENEWAL ENGINE.
- Live children: DigitalCurrensy/bayline `2aa5c59`, DigitalCurrensy/loadclear `8a6dcf1`, DigitalCurrensy/unitcommit `d0ea81c`
- Unitcommit child compiling unit 8/8. build_ising.py blob `55a20615` MATCH. Parent `platforms/unitcommit/` remains source of truth.
- Parent `platforms/{house}` is source of truth. Houses do not merge. No empty shells.
- Build sequence: Bayline receipt → Loadclear enroll/refuse/cluster → Unitcommit clearance → Cabinetfield derate → Phasepin + Fiberlock → Photonseal HMAC.
- Product 6 is Unitcommit (not Unitspin).
- Unitcommit code law: σ = 2u − 1, x = (σ + 1) / 2, σ = +1 ON. λ_logic=50, λ_mut=40. Clearance = residual AND spin_count == assignment_count == n.
- Phasepin ladder: csac_ok → |ptp_offset_ns|<1e6 → holdover_s<14400 → gps_peer. GPS is a peer.
- Phasepin quality: attach_inaccuracy. None=missing, ≤1000ns=profile_in_spec, <1e6=phasepin_ok, else too_wide. No TLV parse. No BMCA.
- Fiberlock: wrap_from_pin refuses gps_peer and too_wide. QBER_MAX=0.11.
- Photonseal: HMAC-SHA256. verify = _mac + compare_digest. Empty key on verify → False. Seal refuses empty key, gps_peer, uncleared, unwrapped, too_wide. Not Ed25519. Not a token.
- Shared: tenant_id UUID, event_id UUIDv7, outbox settlement, Timescale + Redis hot state, no DROP/TRUNCATE.
