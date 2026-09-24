# Module Kinetic Ltd

A charger fault becomes a signed energy interval, or it is refused.

Apache-2.0. One desk. Seven checks. Houses do not merge.

## Who it is for

A charge-point operator or a grid operator who must show why a charger was cleared. Not a carbon spreadsheet. Not a token.

## The seven checks

| Check | What it does | What it refuses |
| --- | --- | --- |
| Bayline | Turns an OCPP 2.0.1 or 2.1 fault into a work order | OCPP 1.6, or a periodic stream used as a fault |
| Loadclear | Turns that charger into an asset | No work order, or arming while the lock is open |
| Cabinetfield | Applies a derate from a cabinet reading | A critical fault with no covering calibration |
| Unitcommit | Clears power only if the mismatch and the spin count both pass | A power mismatch |
| Phasepin | Grades the clock | A GPS-only clock, or a bound that is too wide |
| Fiberlock | Wraps the path when the span is quiet enough | A span error rate at or above 0.11, or a key shorter than 128 bits |
| Photonseal | Signs the interval | An empty key, or the literal key `k` |

A repeated station and event id is one work order. Later checks are not written after a refusal.

## How to check

This repository is the law. It is not the operator screen. GitHub will not start that screen.

```bash
python -m pip install pytest
PYTHONPATH=. python -m pytest tests
```

With no `DATABASE_URL`, a live drain writes nothing. Do not put a database password or a signing key in the repo.

## Repos

The parent `platforms/{slug}` is the source. Each live house has its own repo. A child is copied only after that house compiles, and only when a split is named. Do not merge the houses.

| House | Repo |
| --- | --- |
| Bayline | `DigitalCurrensy/bayline` |
| Loadclear | `DigitalCurrensy/loadclear` |
| Cabinetfield | `DigitalCurrensy/cabinetfield` |
| Unitcommit | `DigitalCurrensy/unitcommit` |
| Phasepin | `DigitalCurrensy/phasepin` |
| Fiberlock | `DigitalCurrensy/fiberlock` |
| Photonseal | `DigitalCurrensy/photonseal` |

Wellpath, Tenderbank, Ionlattice, Coilhold, Nitroforge, Phononstack, and Densitywell are not started. They are not unfinished percent of this desk.

## License and selling

Copyright 2026 Module Kinetic Ltd. Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE).

Apache-2.0 lets anyone use, change, and sell copies of this code, including in a commercial product. That grant is permanent for the versions published under it. The copyright holder can still sell a hosted service, a support contract, or a separate license for code that was never published here. The name Module Kinetic is not granted as a trademark.
