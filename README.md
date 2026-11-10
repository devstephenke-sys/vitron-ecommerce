# Vitron E-Commerce Platform

Custom multi-brand electronics and home-appliance commerce platform for Vitron, Xiaomi and Sonar.

## Current status

Phase 0 — requirements, architecture and technical planning.

The repository has been cloned and inspected. No application implementation has started yet. Phase 0 documentation is available under `docs/`.

## Documentation

- [Requirements](docs/01-requirements.md)
- [System architecture](docs/02-architecture.md)
- [Database schema baseline](docs/03-database-schema.md)
- [API contract baseline](docs/04-api-contracts.md)
- [Product catalogue baseline](docs/05-product-catalogue.md)
- [Implementation roadmap](docs/06-roadmap.md)
- [Local development](docs/07-local-development.md)
- [Testing and quality](docs/08-testing-and-quality.md)
- [Deployment](docs/09-deployment.md)
- [Decisions and risks](docs/10-decisions-and-risks.md)
- [Maintenance](docs/11-maintenance.md)

## Phase 0 findings

- Repository `devstephenke-sys/vitron-ecommerce` is private and accessible to the configured GitHub account.
- `main` contains only the initial README at the time of inspection.
- The supplied product catalogue declares 102 entries; table-level extraction and a flattened listing check confirm 102 rows.
- Catalogue currency, stock, warranty, verified images and several model/specification details require supplier/business confirmation before publication.
- Payment integration will remain sandbox/test until provider credentials and business approval are available.

## Next step

Review `docs/10-decisions-and-risks.md`, resolve the business decisions that affect publication/checkout, then approve Phase 1 repository and backend foundation work.
