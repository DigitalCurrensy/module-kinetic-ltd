# Status

Updated 2026-09-24. This repository is public. The seven part repositories are public. This page is the product.

- Seven checks run in order. One failure saves nothing.
- Tests run on every push and every Monday.
- A house outbox stays in memory until a host sets `DATABASE_URL`. An unset URL writes nothing. No database URL is stored here.
- The signing secret is a host secret. It is not a column and not a file in git.
- The sample readings are authored. They are not a charger, a cabinet, a switch, or a span.
- This repository is not a charger-management server, not a hardware module, and not a grid market.
