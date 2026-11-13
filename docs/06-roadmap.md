# Implementation Roadmap

Status: Phase 1 and Phase 2 merged to `main`; Phase 3 implemented on `feat/phase-3-ui-system` (pending merge); Phases 4+ not started
Rule: complete each phase with tests, documentation, commit and explicit go/no-go evidence before starting the next dependent phase.

## Phase 0 — Requirements, architecture and planning (current)

Deliverables:

- Repository inspection and baseline documented.
- Requirements, architecture, database schema, API contracts and catalogue rules documented.
- Decision register and risk register created.
- Implementation roadmap and local development plan created.

Exit gate: business owner reviews currency, availability, taxonomy, payment scope and policy decisions; architecture baseline approved.

## Phase 1 — Repository and backend foundation — COMPLETE (pending merge)

Implemented on `feat/phase-1-foundation`:

- Monorepo layout: `apps/api`, `apps/storefront`, `apps/admin`, `packages/contracts`, `infra/`, `.github/workflows/`.
- Backend tooling: Python 3.12 + `uv`, FastAPI, Pydantic v2, SQLAlchemy 2 (async/asyncpg), Alembic, Ruff, Pytest. (mypy deferred — see `docs/10-decisions-and-risks.md` TD-18.)
- Frontend tooling: Nuxt 3.21, TypeScript, Pinia, Tailwind CSS, pnpm workspaces, `openapi-typescript` contract generation. (Vitest/Playwright deferred to Phase 3 — TD-17.)
- Health checks (`/api/v1/health/live`, `/api/v1/health/ready`), pydantic-settings configuration, structured logging with request IDs, standard error envelope, explicit-origin CORS, test harness (6 tests passing).
- CI: `backend.yml` (ruff, format, pytest, alembic upgrade against Postgres service) and `frontend.yml` (nuxi prepare, typecheck, production build for both apps).
- Local development: Docker Compose PostgreSQL (host port 5433), verified commands in `docs/07-local-development.md`.

Verified evidence: `uv sync`, `alembic upgrade head` on empty DB, uvicorn serving live/ready endpoints (ready returns 200 with DB, 503 without), `pytest` 6/6, `pnpm install`, `nuxt typecheck` and `nuxt build` for both apps.

## Phase 2 — Database, identity and authorization — IMPLEMENTED (pending merge)

Implemented on `feat/phase-2-identity-rbac`:

- Schema migration `0002_identity_and_access`: users, roles, permissions, role_permissions, user_roles, refresh_tokens, password_reset_tokens, auth_events, addresses, customer_profiles, audit_logs, background_jobs — plus idempotent seed of 4 system roles and 25 permissions.
- Identity: Argon2id password hashing, register/login (JWT access token + rotating opaque refresh tokens with reuse detection), refresh rotation, logout, password-reset request/confirm (delivery deferred to Phase 8), `/me` profile read/update.
- Addresses: `/me/addresses` CRUD with per-user ownership enforcement.
- RBAC: permission catalogue checked server-side per request via `require_permission`/`require_any_permission` dependencies; JWT carries no permission claims; `GET /admin/audit-logs` demonstrates enforcement.
- Rate limits on auth endpoints (in-memory sliding window — see TD-19 in docs/10).
- Admin app: real login page, auth store with refresh-token persistence, session hydration plugin, Bearer token injection, sign-out; admin app switched to SPA mode (`ssr: false`).
- `scripts/create_admin.py` bootstrap for the first administrator.
- Tests: 33 pytest tests including DB-backed auth flows, refresh-reuse family revocation, password reset, address ownership and RBAC permission matrix — all passing against real PostgreSQL.

Exit gate evidence: customer/admin auth tests pass; no secrets in repository; migrations run from empty database (CI `alembic upgrade head` plus pytest session fixture).

## Phase 3 — Storefront and admin UI system — IMPLEMENTED (pending merge)

Implemented on `feat/phase-3-ui-system`:

- Storefront design system: `UiAlert`, `UiButton`, `UiSpinner`, `EmptyState` primitives plus `ProductCard`, `ProductGrid`, `CatalogToolbar`, `Pagination`, `CatalogBrowser` catalog components; money/date formatting helpers (`formatMoney` renders KES without floats).
- Storefront pages: home, `/products` listing, `/products/[slug]` detail (gallery, specs, breadcrumbs), `/brands/[slug]`, `/categories/[slug]` — all sharing `CatalogBrowser` with URL-synced search/sort/page state, loading/empty/error states and `useSeoMeta` metadata. Header search and layout/footer shell in `layouts/default.vue`.
- Catalog data layer: Pinia `catalog` store + `~/types/catalog.ts` local types mirroring the planned `/products` contract (replaced by generated contracts when Phase 4 lands — TD-27).
- Admin: permission-aware route middleware (`definePageMeta({ permission })`, any-of arrays), nav registry (`utils/navigation.ts`) filtered by auth-store permissions, section placeholder pages (catalog/orders/inventory/customers/users) and a working `/audit-logs` page against `GET /admin/audit-logs`.
- Frontend test tooling (resolves TD-17 for unit/component scope): Vitest 3 + `@vitejs/plugin-vue` + `@vue/test-utils` + happy-dom in both apps; 34 tests covering money/catalog utils, product card/pagination/UI primitives, catalog store state/error paths, admin navigation filtering and auth-store permission UX. `pnpm test` wired into Frontend CI for both apps.
- Playwright browser E2E remains deferred to Phase 9 (TD-28).

Verified evidence: `pnpm test` 27/27 storefront + 7/7 admin, `nuxt typecheck` clean for both apps, `nuxt build` succeeds for both apps.

Exit gate: accessibility/responsive smoke checks pass; no catalog mutation yet.

## Phase 4 — Catalogue and import

- Implement brands, categories, products, attributes, images and publication workflows.
- Build bulk import/export pipeline with dry-run, validation, batch status and row errors.
- Import only approved catalogue extract; preserve source traceability and unknown values.
- Add admin catalog tests and public read-only catalog API tests.

Exit gate: approved sample catalogue imports, publishes, searches and exports with reconciliation report.

## Phase 5 — Cart, checkout and orders

- Implement carts, server-side pricing, promotions placeholders, checkout preview, order creation and order history.
- Implement addresses, wishlist, quotations and customer account pages.
- Implement stock reservation policy and transactional inventory deduction.
- Add end-to-end tests for browse → cart → checkout → order → inventory.

Exit gate: checkout cannot oversell or trust client totals; all critical workflows have automated tests.

## Phase 6 — Administration and operations

- Complete admin dashboard, orders, customers, inventory, stock movements, quotations, shipments, promotions, reports and audit logs.
- Add role-specific permissions for admin, inventory manager and sales staff.
- Add bulk operations, export controls and operational dashboards.

Exit gate: permission matrix tests pass; staff cannot access unauthorized actions; reports reconcile to order data.

## Phase 7 — Payments

- Implement provider adapter interface and sandbox M-Pesa/card/mock adapters.
- Add payment intents, server-side verification, signed/idempotent callbacks, reconciliation, failed/pending states and refunds where supported.
- Add webhook security tests, duplicate callback tests and payment state-machine tests.

Exit gate: no order is marked paid without verified provider status; duplicate callbacks are safe; production payment remains disabled until approved.

## Phase 8 — Communications, notifications and analytics

- Add email/SMS/WhatsApp adapters, templates, order notifications, quotation notifications and background job processing.
- Add product analytics events with privacy controls and admin reporting dashboards.
- Add delivery provider adapter interface and shipment tracking.

Exit gate: provider failures do not block order placement; jobs retry safely; notifications are auditable.

## Phase 9 — Security, testing and performance

- Run threat model, dependency audit, secrets scan, authorization audit, file upload review and payment review.
- Complete unit, integration, API, component, browser and end-to-end suites.
- Add load tests for catalog/search/cart/checkout and database query/index review.
- Document backup, restore, incident response, deployment rollback and maintenance procedures.

Exit gate: all critical tests pass; no high-severity security findings remain open; performance budgets are documented and met.

## Phase 10 — Production deployment

- Provision Neon production branch/database, Vercel projects and Render web/worker services.
- Configure separate environment variables, CORS, callback URLs, object storage and provider credentials.
- Run migrations, smoke tests, backup verification and rollback rehearsal.
- Deploy storefront/admin/API independently and monitor logs/alerts.

Exit gate: production smoke tests pass; monitoring/alerts active; business owner signs off.

## Milestone evidence template

Every milestone commit/PR must record:

- Scope completed.
- Tests run and results.
- Documentation updated.
- Known defects/risks.
- Business decisions still pending.
- Deployment/rollback status.
