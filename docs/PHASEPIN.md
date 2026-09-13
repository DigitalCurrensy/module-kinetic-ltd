# Phasepin — CSAC clock pin

GPS is a peer sensor. It is never source of truth.

Live ladder in `platforms/phasepin/src/application/clock.py`:

1. `csac_ok` → source `csac`, offset 0
2. else `|ptp_offset_ns| < 1_000_000` (1 ms) → source `ptp`
3. else `holdover_s < 14400` → source `holdover`
4. else source `gps_peer`

Photonseal `SEALABLE = {csac, ptp, holdover}`. A `gps_peer` pin will not seal.

CSAC is a physics package (typically 87Rb CPT, ~120 mW, 1 PPS in/out). It is not a GNSS receiver. Holdover is the free-running atomic oscillator after the last good discipline, not a guess.
