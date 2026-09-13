# QKD clock vs Phasepin

Fiberlock needs a clock. Fiberlock is not the clock.

CV-QKD with a local LO recovers frequency and phase from a pilot tone on the same fiber (or a second wavelength). Symbol timing is DSP: preamble / PRBS correlation, then digital timing recovery. Coarse wall-clock for `interval_start` is Phasepin (CSAC / PTP / holdover).

QBER and ξ on the Fiberlock tape measure the quantum channel after that alignment. A Phasepin holdover does not raise QBER by itself. A lost pilot tone does — that is excess noise, not a PTP announce timeout.

Do not put BMCA inside Fiberlock. Do not put QBER inside Phasepin.
