# MEMORY — Module Kinetic Ltd

Loop rule: rewrite this file when a parent SHA lands. Code is law. Docs lag is dirt.
Updated 2026-09-24. No kernel edits. derate.py bab6281 unchanged.

- Company: Module Kinetic Ltd
- Parent: DigitalCurrensy/module-kinetic-ltd main (this commit)
- Operator desk: all seven houses. Run plant writes work_order, enrollment, derate, commitment_run, time_pin, wrap, signed_meter.
- Refuse critical (no calibration) writes the receipt and enrollment only. Refuse residual writes through derate and no commitment_run.
- gps_peer, QBER >= 0.11, and an empty Photonseal key write 0. Empty key on verify returns false. Key is not stored.
- pmax_committed = 2.0 * f. Clear iff residual <= 1 MW and spin count matches and derated pmax >= pmin.
- No Timescale DSN pasted. Not a CSMS. Not an HSM. Not a live ODMR ADC, switch TTI, or span modem.
- Houses do not merge. No Wellpath.
- Frozen kernels: receipt 49eea447, enroll 078c26c9, refuse 04a48547, build_ising 55a20615, derate bab6281, clock 14522007, session 3db938d3, meter dfb7cced.
- Completion: operator path of the seven houses is closed. Real iron and a sellable clearance are not. Parked seven stay at 0%.
