# AGENTS — Module Kinetic Ltd

Company: Module Kinetic Ltd
Repo: DigitalCurrensy/module-kinetic-ltd
Grok is team lead. Architect owns wiring. Backend owns use-cases. Database owns schema + invariants.

## Rules
- Company name is Module Kinetic Ltd. Do not revive OMNI Renewal Engine as the company title.
- House names stay locked. Houses do not merge.
- Never run DROP TABLE or TRUNCATE without an explicit verified ticket.
- Parameterized SQL or ORM only.
- Every operational table carries `tenant_id`.
- Ingest is idempotent on `event_id` (UUIDv7).
- Settlement, parts, firmware, derates go through `outbox_events`.
- Do not skip the locked build sequence.
- Child private repos copy `platforms/{slug}/` only after that house compiles a first slice.

## Locked houses
Bayline, Loadclear, Wellpath, Tenderbank, Ionlattice, Unitcommit, Cabinetfield, Fiberlock, Coilhold, Phasepin, Nitroforge, Photonseal, Phononstack, Densitywell.
