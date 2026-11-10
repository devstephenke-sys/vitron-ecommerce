# System Architecture

Status: Phase 0 baseline
Decision summary: two independently deployable applications communicate only through a versioned REST/OpenAPI contract. PostgreSQL is the system of record.

## 1. Architecture decision

| Area | Decision | Rationale |
|---|---|---|
| Frontend | Nuxt 3 + Vue 3 + TypeScript + Pinia + Tailwind CSS | SSR/SEO, typed component model, shared storefront/admin code only where genuinely common |
| Storefront and admin | Separate Nuxt applications (or clearly isolated Nuxt modules/routes with independent deployment configuration) | Independent release and permission boundaries |
| Backend | Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic | Typed API contracts, mature ORM/migrations and test ecosystem |
| Database | Neon PostgreSQL | Managed PostgreSQL, pooling support, migrations and backups |
| API style | REST under `/api/v1`; OpenAPI generated from FastAPI | Stable contracts and generated client types |
| Background work | Render Background Worker using the same backend package; database-backed job queue initially | Avoid premature broker complexity while keeping request paths responsive |
| Object storage | Cloudinary-compatible adapter; local filesystem only for development | Provider-neutral uploads and image transformations |
| Payments | Provider adapter interface, sandbox first | Keep M-Pesa/card/provider behavior out of domain services |
| Notifications | Adapter interfaces for email/SMS/WhatsApp | Business rules stay provider-independent |

## 2. Logical components

```text
Customer browser / admin browser
          | HTTPS
          v
Vercel: Nuxt storefront          Vercel: Nuxt admin
          | /api/v1                    | /api/v1
          +-------------+--------------+
                        v
Render: FastAPI modular monolith
  API layer -> authn/authz -> application services -> repositories
       |              |                    |
       |              v                    v
       |       background jobs        audit/outbox events
       v                                 |
PostgreSQL (Neon) <-----------------------+
       ^
Cloudinary-compatible media storage
       ^
Payment, email, SMS, WhatsApp and delivery provider adapters
```

The frontend never receives database credentials or provider secrets. Server-side environment variables are used for all secrets. CORS allows only explicit storefront/admin origins per environment.

## 3. Backend module boundaries

Each module owns routes, schemas, service/application logic, repository/persistence and tests:

- `identity` — users, roles, permissions, sessions/refresh tokens, auth events.
- `catalog` — brands, categories, products, specifications, images, publication state.
- `inventory` — stock balances, reservations, stock movements and concurrency controls.
- `commerce` — carts, checkout, orders, order items, pricing snapshots and order lifecycle.
- `payments` — payment intents, provider adapters, callbacks, reconciliation and idempotency.
- `fulfilment` — addresses, shipments, delivery zones/providers and tracking.
- `sales` — quotations, promotions/coupons and sales reports.
- `engagement` — wishlist, notifications and customer communications.
- `platform` — audit logs, feature flags, background jobs, health checks and admin operations.

Modules communicate through explicit service interfaces, not by importing another module's ORM models into route handlers. Cross-module writes that must be atomic share one database transaction.

## 4. Key workflows

### Product publication

1. Import/validate catalogue record with source reference and confidence state.
2. Attach confirmed brand/category/specifications/images.
3. Set commercial fields only from approved data.
4. Preview publication impact.
5. Publish transactionally; audit actor, timestamp and source.

### Cart/checkout

1. Cart items reference product variant/SKU and quantity.
2. Checkout re-prices every line server-side from current published product and promotion rules.
3. Validate customer, addresses, delivery option and stock availability.
4. Create order and immutable order-item snapshots in one transaction.
5. Reserve stock with an expiry policy; release reservations on cancellation/timeout.
6. Create a payment intent; never mark paid from browser response.

### Payment callback

1. Receive provider callback at a provider-specific adapter endpoint.
2. Verify signature/authenticity and parse provider event.
3. Use provider transaction reference plus local idempotency key to prevent duplicates.
4. Query provider status server-side when supported.
5. Transition payment/order state transactionally and emit audit/outbox event.

### Inventory

- Use integer stock quantities; keep monetary values as fixed-precision decimal/currency values.
- Stock changes are append-only movements with actor, reason, order reference and resulting balance.
- Use row-level locking or atomic conditional updates for reservation/deduction.
- Historical order lines retain SKU, model, description, unit price, tax and totals at purchase time.

## 5. Environment strategy

| Environment | Frontend | Backend | Database | External providers |
|---|---|---|---|---|
| Local | Nuxt dev servers | FastAPI dev server / Docker | Local PostgreSQL or Neon development branch | Mock/sandbox adapters |
| Staging | Vercel preview/staging | Render staging | Neon staging branch | Sandbox/test credentials |
| Production | Vercel production | Render production | Neon production branch | Approved live credentials after security review |

Development, staging and production must use separate databases, secrets, CORS origins, callback URLs and provider accounts where supported. Production migrations run as a controlled deployment step, not automatically from an unreviewed branch.

## 6. Cross-cutting controls

- Argon2id password hashing; short-lived access tokens and rotating refresh tokens stored securely.
- RBAC permissions checked server-side on every protected operation.
- Request schemas validated with Pydantic; frontend validation is only UX.
- Rate limits on auth, search, checkout, quotation and payment endpoints.
- Secure upload validation, image re-encoding/size limits and signed/private asset URLs where needed.
- Structured logs without secrets or full payment payloads; correlation IDs across requests/jobs.
- Append-only audit records for authentication, catalogue publication, pricing, inventory, orders, payments, user/role changes and exports.
- Backups, restore rehearsal, migration rollback plan and incident runbook before production.

## 7. Scalability and future expansion

The modular monolith can be split later by domain if traffic or team boundaries require it. SKU/product variants, warehouses, branches, B2B accounts and wholesale price lists should be introduced as explicit schema extensions rather than implicit product attributes. API versioning allows storefront and admin clients to upgrade independently.
