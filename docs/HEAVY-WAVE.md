# Heavy wave — Module Kinetic Ltd

Parent `e04c271`. Live children: bayline `2aa5c59`, loadclear `8a6dcf1`, unitcommit `d0ea81c`.
Parent platforms/ is source of truth. Houses do not merge.

```
Bayline receipt (OCPP 2.1 NotifyEvent)
    → Loadclear enroll + refuse + cluster
    → Cabinetfield derate factor f
    → Unitcommit clusters_from_flex + build_ising + clearance
    → Phasepin pin (CSAC → PTP 1ms → holdover 4h → gps_peer)
    → attach_inaccuracy (missing | profile_in_spec | phasepin_ok | too_wide)
    → Fiberlock wrap_from_pin (no gps_peer; QBER < 0.11; ξ < 0.08 SNU)
    → Photonseal HMAC-SHA256
         seal refuses: uncleared | unwrapped | too_wide | gps_peer | empty key
         verify: _mac + compare_digest (empty/wrong key → False)
```

Unitcommit child is split at d0ea81c (8/8 blob match). Next child when called: Cabinetfield.
Ed25519 is not shipped. HMAC remains the meter tag.
