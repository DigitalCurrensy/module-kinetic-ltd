# PTP handover vs Phasepin pin

IEEE 1588 BMCA elects a grandmaster. Phasepin does not run BMCA.
Live `pin_time` only accepts an already-measured `ptp_offset_ns`.

## What the network does

Announce messages carry priority1, clockClass, clockAccuracy, variance, priority2, clockIdentity, stepsRemoved.
GM is lost after `announceReceiptTimeout × 2^logAnnounceInterval` seconds (typical: 3 × 1 s).
A port-down toward the GM can skip the timeout and start BMCA immediately.
Power-profile targets (C37.238 / IEC 61850-9-3) are sub-microsecond in a substation fabric — tighter than Phasepin's 1 ms `PTP_GOOD_NS` gate.

## What Phasepin does

```
csac_ok → csac
else |ptp_offset_ns| < 1_000_000 → ptp
else holdover_s < 14400 → holdover
else gps_peer
```

A BMCA failover that leaves `|offset| ≥ 1 ms` is not a PTP pin. It falls to holdover or gps_peer.
Photonseal will not seal gps_peer.
