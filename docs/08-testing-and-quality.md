# Testing and Quality Plan

Status: Phase 1 foundation in place — backend pytest suite (6 tests: health endpoints, readiness failure path, request IDs, error envelopes) runs in CI; frontend typecheck/build gates in CI. Domain test suites are added per phase.
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

### Storefront

- Product card/detail rendering and image fallback.
- Search/filter state and URL synchronization.
- Cart state, quantity validation and checkout form validation.
- Order history and account pages.
- SEO metadata and accessibility basics.

### Admin

- Permission-aware navigation and route guards.
- Product form validation and publication preview.
- Inventory adjustment form and stock movement table.
- Order status actions and confirmation dialogs.
- Import batch upload/error display.

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
