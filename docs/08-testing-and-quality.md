# Testing and Quality Plan

Status: Phase 3 in place — backend pytest suite (33 tests: auth flows, RBAC matrix, refresh rotation/reuse, password reset, ownership) runs in CI; frontend Vitest suites (34 tests: utils, components, stores, navigation/auth UX) plus typecheck/build gates run in CI for both Nuxt apps. Domain test suites are added per phase.
Quality principle: critical commerce, inventory and payment behavior must be proven by automated tests before production deployment.

## 1. Backend tests

### Unit tests

- Password hashing/verification and token rotation.
- Money calculations, tax/discount rounding, order totals and snapshots.
- Product publication state transitions.
- Payment state machine and callback parsing/verification.
- Inventory reservation, release, deduction and adjustment rules.
- Promotion/coupon eligibility and limits.
- Import row validation and normalization.

### Integration/API tests

- Register/login/refresh/logout and password reset.
- RBAC authorization for admin, inventory and sales roles.
- Public catalog search/filter/pagination and unpublished-product exclusion.
- Cart operations and checkout preview with server-side totals.
- Order creation, idempotency, order history and status transitions.
- Payment initiation, sandbox callback, duplicate callback, signature failure and reconciliation.
- Stock reservation expiry, successful deduction, failure release and oversell prevention.
- Bulk import dry-run/commit and export authorization.
- Audit log creation for sensitive mutations.

### Database tests

- Migrations from empty database.
- Transaction rollback on failures.
- Unique constraints, foreign keys, non-negative inventory and order totals.
- Concurrent checkout tests for stock races.
- Audit append-only expectations at application level.

## 2. Frontend tests

Tooling (Phase 3, TD-30): Vitest 3 + `@vitejs/plugin-vue` + `@vue/test-utils` + happy-dom, configured per app via `vitest.config.ts`; `pnpm test` runs in Frontend CI. Playwright browser E2E deferred to Phase 9 (TD-28).

### Storefront (27 tests)

- `utils/format`: money formatting (KES, decimal-string amounts, invalid input) and date formatting.
- `utils/catalog`: query-string building, price/name sorting (priceless items last), text filtering.
- Components: `ProductCard` (link, price, stock label, image fallback), `Pagination` emit/disable logic, `UiAlert`/`UiButton`/`EmptyState` rendering.
- `catalog` store: idle state, success population, API error → error state, `fetchProduct` null-on-failure.

Planned next: search/filter URL synchronization, cart/checkout state, SEO metadata, accessibility checks.

### Admin (7 tests)

- Navigation registry: all sections present, permission filtering, permission-free items always visible.
- Auth store: unauthenticated default, login applies session+permissions, `clearSession` resets, login errors propagate without session.

Planned next: route-middleware permission redirects, product/inventory/order forms, import error display.

### Browser/end-to-end

- Customer registration → browse → product detail → cart → checkout preview → order placement.
- Admin login → product import preview → publish → verify storefront visibility.
- Inventory manager cannot publish products; sales staff cannot adjust stock.
- Payment sandbox callback path and duplicate callback path.
- Mobile viewport navigation, search, cart and checkout smoke test.

## 3. CI quality gates

Phase 1 will establish jobs for:

- Backend: format/lint, type check, unit tests, integration tests with PostgreSQL service, migration check.
- Storefront/admin: install, lint, typecheck, unit/component tests, production build.
- E2E: Playwright against local/staging-like services with test providers.
- Security: dependency audit, secret scan and OpenAPI validation.
- Documentation: links and required Phase 0 docs presence.

No deployment workflow should run until required checks pass.

## 4. Test data rules

- Use synthetic customers/products/orders only.
- Never use production customer data in local/staging tests.
- Use provider sandbox/test modes for payment, SMS, email and WhatsApp.
- Seed deterministic catalogue fixtures from approved test extracts, not unverified production guesses.

## 5. Coverage and evidence

Coverage percentages are secondary to critical-path coverage. Required evidence for each milestone:

- Command output or CI run link.
- Migration/test summary.
- Known flaky tests and remediation owner.
- Security-sensitive test names for auth, payment callback and inventory.
