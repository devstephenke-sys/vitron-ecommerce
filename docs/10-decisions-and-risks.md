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
| BD-01 | Catalogue currency and authoritative price list | Business owner/supplier | Phase 4 publication | Products cannot be sold/published online |
| BD-02 | Stock quantities and availability policy | Operations | Phase 5 checkout | Cannot safely enable checkout |
| BD-03 | Brand ownership for speaker/accessory models | Business owner | Phase 4 import | Misleading catalog taxonomy |
| BD-04 | Category mapping for TV wall mounts/accessories | Business owner | Phase 1/4 | Incomplete taxonomy |
| BD-05 | Resolution of catalogue model/description mismatches and 16 missing rows | Supplier | Phase 4 | Incomplete/untrusted catalogue |
| BD-06 | VAT/tax, delivery zones/fees and returns policy | Finance/operations/legal | Phase 5/launch | Checkout totals and legal pages incomplete |
| BD-07 | Payment providers, merchant accounts and production approval | Business/finance | Phase 7/10 | Payments cannot go live |
| BD-08 | WhatsApp/email/SMS sender identities and support contacts | Business owner | Phase 8 | Customer communications unavailable |
| BD-09 | Warranty, legal entity, privacy and terms content | Legal/business | Public launch | Cannot publish compliant storefront |
| BD-10 | Product image rights and verified image assets | Business/supplier | Phase 4 | Cannot publish trustworthy product pages |

## 3. Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-01 | Catalogue source incomplete or internally inconsistent | High | High | Reconcile 86 visible rows vs 102 declared; supplier validation gate |
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
