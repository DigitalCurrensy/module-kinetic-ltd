# AGENTS

Copyright 2026 DIGITAL CURRENSY INC / Module Kinetic Ltd.
Repository: DigitalCurrensy/module-kinetic-ltd. Apache-2.0.

Seven houses. They do not merge. Do not start Wellpath, Tenderbank, Ionlattice, Coilhold, Nitroforge, Phononstack, or Densitywell unless that house is named.

## Order

Bayline, then Loadclear, then Cabinetfield, then Unitcommit, then Phasepin, then Fiberlock, then Photonseal.

A fault becomes a work order, then an asset, then a derate, then a clearance, then a clock grade, then a span wrap, then a signed interval. A refusal writes no later row.

## Rules

- `platforms/{slug}` on this parent is the source. A child repository is a copy of that house, not a second design.
- Do not import one house into another. Pass plain values.
- An outbox row is append-only and unique on tenant and event. Do not drop or truncate a table.
- Do not store a signing key, a database URL, a password, or a certificate private key.
- OCPP 1.6 is not a fault. A periodic stream is not a fault.
- An empty signing key refuses the seal. Checking a signature with an empty key returns false and does not raise.
- Parameterized SQL only.
- Every operational row carries a tenant id.
