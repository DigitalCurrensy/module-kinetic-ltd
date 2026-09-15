# Heavy wave — Module Kinetic Ltd

Parent main cited after hygiene. Live children: bayline `e853163`, loadclear `906b053`, unitcommit `39a90797`, cabinetfield `749ecfd`, phasepin `540fc525`, fiberlock `407f8d7`, photonseal `05ec3c75`.
Parent `platforms/` is source of truth. Houses do not merge. Persist wave CLOSED.

```
Bayline receipt (OCPP 2.1 NotifyEvent) + work-order outbox
    → Loadclear enroll + refuse + cluster + enrollment outbox
    → Cabinetfield derate factor f + derate outbox
    → Unitcommit clusters_from_flex + build_ising + clearance + cleared-run outbox
    → Phasepin pin (CSAC → PTP 1ms → holdover 4h → gps_peer) + pin outbox (no gps_peer)
    → attach_inaccuracy (missing | profile_in_spec | phasepin_ok | too_wide)
    → Fiberlock wrap_from_pin (no gps_peer; QBER < 0.11) + wrap outbox
    → Photonseal HMAC-SHA256 + signed-meter outbox (key never stored)
         seal refuses: uncleared | unwrapped | too_wide | gps_peer | empty key
         verify: _mac + compare_digest (empty/wrong key → False)
```

Desk bind: `tests/test_desk_bind.py` walks that chain and enqueues all seven outboxes.
Next house only when named. Not Wellpath unless named.
Ed25519 is not shipped. HMAC remains the meter tag.
