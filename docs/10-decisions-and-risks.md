# Decisions and Risks

Status: Phase 0 decision register
Rule: unresolved business decisions block the affected implementation gate, not unrelated documentation or foundation work.

## 1. Confirmed technical decisions

| ID | Decision | Status | Rationale |
|---|---|---|---|
| TD-01 | Nuxt/Vue/TypeScript storefront and admin, FastAPI backend, Neon PostgreSQL | Approved for planning | Matches requested architecture and independent deployment needs |
| TD-02 | Versioned REST API under `/api/v1` | Approved for planning | Stable contracts and OpenAPI generation |
| TD-03 | Modular monolith first | Approved for planning | Faster delivery while preserving domain boundaries |
| TD-04 | Repository/service layering | Approved for planning | Testability and maintainability |
| TD-05 | UUID identifiers and Alembic migrations | Approved for planning | Required architecture baseline |
| TD-06 | Payment provider adapter pattern | Approved for planning | Avoid provider lock-in and unsafe frontend payment assumptions |
| TD-07 | Sandbox payments before production | Approved for planning | Required security/compliance control |
| TD-08 | No card credential storage | Approved for planning | Security requirement |

## 2. Business decisions required

| ID | Decision | Owner | Needed by | Impact if unresolved |
|---|---|---|---|---|
| BD-01 | Catalogue currency and authoritative price list | Business owner/supplier | Phase 4 publication | **Currency resolved 2026-11-13: prices are KES (Kenyan Shilling, ISO-4217 `KES`).** Authoritative price-list sign-off still required before Phase 4 publication |
| BD-02 | Stock quantities and availability policy | Operations | Phase 5 checkout | Cannot safely enable checkout |
| BD-03 | Brand ownership for speaker/accessory models | Business owner | Phase 4 import | Misleading catalog taxonomy |
| BD-04 | Category mapping for TV wall mounts/accessories | Business owner | Phase 1/4 | Incomplete taxonomy |
| BD-05 | Resolution of catalogue model/description mismatches and source typos | Supplier | Phase 4 | Untrusted catalogue content |
| BD-06 | VAT/tax, delivery zones/fees and returns policy | Finance/operations/legal | Phase 5/launch | Checkout totals and legal pages incomplete |
| BD-07 | Payment providers, merchant accounts and production approval | Business/finance | Phase 7/10 | Payments cannot go live |
| BD-08 | WhatsApp/email/SMS sender identities and support contacts | Business owner | Phase 8 | Customer communications unavailable |
| BD-09 | Warranty, legal entity, privacy and terms content | Legal/business | Public launch | Cannot publish compliant storefront |
| BD-10 | Product image rights and verified image assets | Business/supplier | Phase 4 | Cannot publish trustworthy product pages |

## 3. Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-01 | Catalogue source internally inconsistent or contains OCR/source typos | Medium | High | Reconciled 102 rows; supplier validation gate remains |
| R-02 | Prices published without confirmed currency/authority | Medium | High | Store catalogue price separately; block publication until approved |
| R-03 | Overselling due to concurrent checkout | Medium | High | Transactional reservations, conditional updates and concurrency tests |
| R-04 | Duplicate payment callbacks or frontend spoofing | Medium | High | Signature verification, idempotency, server-side status verification |
| R-05 | Incorrect brand/category mapping | Medium | Medium | Import review workflow and source traceability |
| R-06 | Unverified representative images mislead customers | High | Medium | Mark unverified; require approved assets before publication |
| R-07 | Neon/Vercel/Render costs or limits constrain architecture | Low | Medium | Capacity review during Phase 1/10; avoid premature microservices |
| R-08 | Payment/provider sandbox unavailable or delayed | Medium | Medium | Adapter interface allows mock provider for non-production tests |
| R-09 | Admin permission mistakes expose sensitive operations | Medium | High | RBAC tests, audit logs and principle of least privilege |
| R-10 | Legal/policy content missing at launch | Medium | High | Launch checklist blocks public release until approved |

## 4. Architecture alternatives considered

### Nuxt SSR vs Vite SPA

Nuxt is preferred because product pages require SEO, metadata and server rendering. Vite remains the underlying build tooling where applicable. If SSR creates deployment complexity, a static/SSR hybrid can be evaluated after Phase 1 without changing the API contract.

### Separate storefront/admin apps vs one Nuxt app

Separate applications are preferred for independent deployment and stricter admin access control. Shared UI primitives may be extracted only after duplication is proven; premature shared packages can couple release cycles.

### PostgreSQL job queue vs Redis/broker

Start with a database-backed job table to reduce infrastructure. Move to Redis/broker only if job throughput, scheduling or retry requirements exceed what PostgreSQL handles safely.

### Product variants now vs later

Start with one default variant per product to match the current catalogue. Add normalized variants only when real SKU/option data exists; do not invent variants from descriptions.

## 5. Phase 0 approval checklist

- [x] Repository inspected.
- [x] Catalogue inspected and discrepancies recorded.
- [x] Requirements documented.
- [x] Architecture documented.
- [x] Database baseline documented.
- [x] API baseline documented.
- [x] Roadmap and local development plan documented.
- [x] Testing/deployment/maintenance plans documented.
- [ ] Business owner approves unresolved decisions or delegates defaults.
- [ ] Phase 1 implementation may begin after approval.

## 6. Phase 1 implementation decisions

| ID | Decision | Status | Rationale |
|---|---|---|---|
| TD-09 | `uv` for Python dependency management (`pyproject.toml` + `uv.lock`) | Implemented | Fast, reproducible installs; single tool for sync/run |
| TD-10 | `pnpm` workspaces for all JS/TS (`pnpm-workspace.yaml` + `pnpm-lock.yaml`) | Implemented | One lockfile, strict dependency isolation, workspace scripts |
| TD-11 | Async SQLAlchemy 2 + asyncpg; Alembic runs async migrations via `asyncio.run` in `env.py` | Implemented | Non-blocking DB access; single driver for app and migrations |
| TD-12 | API contracts: TypeScript types generated from FastAPI OpenAPI via `openapi-typescript` into `packages/contracts` | Implemented | Single source of truth in Pydantic schemas; no hand-maintained duplicates |
| TD-13 | `@vitron/contracts` consumed by Nuxt apps via `file:` dependency | Implemented | Apps stay independently installable without a publish step |
| TD-14 | Local Docker PostgreSQL published on host port **5433** | Implemented | Port 5432 was already bound by a local PostgreSQL service on the development machine |
| TD-15 | Baseline Alembic revision `0001_baseline` is intentionally empty | Implemented | Establishes the migration chain; domain tables arrive per phase |
| TD-16 | Money representation standardized as `{"amount": "<decimal string>", "currency": "<ISO-4217>"}` | Approved | Consistent contract before client generation; no floats for money |
| TD-17 | Vitest/Playwright frontend test tooling deferred to Phase 3 | Deferred | Phase 1 scope requires lint/typecheck/build only; UI test harness belongs with the design-system phase |
| TD-18 | Backend type checking via Ruff + pytest; mypy not configured in Phase 1 | Deferred | Revisit when domain modules grow; noted as a Phase 1/9 quality gate item |

## 7. Phase 1 residual risks

| ID | Risk | Severity | Mitigation |
|---|---|---|---|
| R-11 | Async engine/session are module-level singletons; no connection recycling policy yet | Low | `pool_pre_ping` enabled; revisit pooling under Phase 9 load testing |
| R-12 | No rate limiting, auth or RBAC yet — expected at this phase | Info | Implemented in Phase 2; admin app already guards routes client-side (server enforcement comes with identity) |
| R-13 | CI frontend jobs run `pnpm install` at workspace root inside each job | Low | Acceptable duplication; can be optimized with a changesets-style filter later |
