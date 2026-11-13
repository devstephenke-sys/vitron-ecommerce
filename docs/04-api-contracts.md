# API Contract Baseline

Status: Phase 1 health endpoints + Phase 2 auth/account endpoints implemented; OpenAPI available at `/openapi.json`
Base URL: `/api/v1`
Conventions: JSON request/response bodies; UUID resource IDs; cursor or offset pagination with documented limits; ISO-8601 UTC timestamps. Money is standardized as an object `{"amount": "<decimal string>", "currency": "<ISO-4217 code>"}` — `amount` is a fixed-precision decimal string (never a float), `currency` is an ISO-4217 alpha-3 code (e.g. `"KES"`). Errors use a stable envelope `{"error": {"code", "message", "request_id", "details?"}}`; implemented in Phase 1.

## 1. Common endpoints

| Method | Path | Access | Purpose |
|---|---|---|---|
| GET | `/health/live` | Public | Process liveness |
| GET | `/health/ready` | Public (returns no sensitive detail) | Database connectivity readiness; 503 when unavailable |
| GET | `/meta/currencies` | Public | Approved currencies |
| GET | `/meta/brands` | Public | Published brands |
| GET | `/meta/categories` | Public | Published category tree |

## 2. Authentication and account

| Method | Path | Access | Purpose |
|---|---|---|---|
| POST | `/auth/register` | Public, rate-limited | Create customer account |
| POST | `/auth/login` | Public, rate-limited | Issue access/refresh session |
| POST | `/auth/refresh` | Refresh token | Rotate refresh token |
| POST | `/auth/logout` | Authenticated | Revoke session/token family |
| POST | `/auth/password-reset/request` | Public, rate-limited | Request reset without revealing account existence |
| POST | `/auth/password-reset/confirm` | Public, rate-limited | Consume reset token |
| GET/PATCH | `/me` | Customer | Read/update own profile |
| GET/POST | `/me/addresses` | Customer | List/create addresses |
| PATCH/DELETE | `/me/addresses/{address_id}` | Customer | Update/delete owned address |
| GET | `/me/orders` | Customer | Paginated order history |
| GET | `/me/orders/{order_id}` | Customer | Owned order detail |
| GET/POST/DELETE | `/me/wishlist` | Customer | Wishlist operations |

Admin user/role endpoints are under `/admin/users`, `/admin/roles` and require explicit permissions.

Implemented in Phase 2: `POST /auth/register`, `/auth/login`, `/auth/refresh`, `/auth/logout`, `/auth/password-reset/request`, `/auth/password-reset/confirm`, `GET/PATCH /me`, `GET/POST /me/addresses`, `PATCH/DELETE /me/addresses/{id}`, and `GET /admin/audit-logs` (requires `audit.read`). Token response shape: `{access_token, token_type, expires_in, refresh_token, user, permissions}`. Password-reset emails are not sent yet — delivery arrives with Phase 8 communications; the reset token is only stored hashed.

## 3. Catalog and discovery

| Method | Path | Access | Purpose |
|---|---|---|---|
| GET | `/products` | Public | Published products with search/filter/sort/pagination |
| GET | `/products/{slug-or-id}` | Public | Product detail, images, specs, availability summary |
| GET | `/products/{id}/related` | Public | Related products/accessories |
| GET | `/products/compare` | Public | Compare selected published products |
| GET | `/brands/{slug}` | Public | Brand landing data |
| GET | `/categories/{slug}` | Public | Category landing data |

Product filters: brand, category, price range, availability, approved attributes, sort. Search covers name and model number. Responses must not expose draft/review products or internal cost/stock fields.

## 4. Cart, checkout and quotations

| Method | Path | Access | Purpose |
|---|---|---|---|
| GET/POST | `/cart` | Customer or guest token if approved | Read/create cart |
| PATCH/DELETE | `/cart/items/{item_id}` | Cart owner | Update/remove item |
| POST | `/checkout/preview` | Customer | Server-authoritative totals, tax, delivery and stock validation |
| POST | `/orders` | Customer | Place order from checkout attempt |
| GET | `/orders/{order_id}` | Owner/admin permission | Order status/detail |
| POST | `/quotations` | Customer/public lead | Request quote |
| GET | `/quotations/{reference}` | Customer/admin | Quote status where access rules allow |

Checkout accepts selected address/delivery/payment method references, never client-calculated totals. Idempotency keys are required for order creation and payment initiation.

## 5. Payments

| Method | Path | Access | Purpose |
|---|---|---|---|
| POST | `/payments` | Customer/order owner | Create payment intent for pending order |
| GET | `/payments/{payment_id}` | Owner/admin permission | Payment status after server-side checks |
| POST | `/payments/{payment_id}/verify` | Customer/order owner | Trigger provider status verification |
| POST | `/webhooks/payments/{provider}` | Provider signature verification | Signed callback endpoint |
| POST | `/admin/payments/{payment_id}/reconcile` | Finance/admin permission | Manual reconciliation with audit reason |

The public API must never accept a client claim that a payment succeeded as proof of payment.

## 6. Admin catalog and inventory

| Method | Path | Access | Purpose |
|---|---|---|---|
| GET/POST | `/admin/brands` | Catalog permission | List/create brands |
| PATCH/DELETE | `/admin/brands/{id}` | Catalog permission | Update/archive brands |
| GET/POST | `/admin/categories` | Catalog permission | List/create categories |
| PATCH/DELETE | `/admin/categories/{id}` | Catalog permission | Update/archive categories |
| GET/POST | `/admin/products` | Catalog permission | List/create products |
| GET/PATCH | `/admin/products/{id}` | Catalog permission | Detail/update product |
| POST | `/admin/products/{id}/publish` | Publish permission | Validate and publish |
| POST | `/admin/products/{id}/images` | Catalog permission | Secure upload/attach image |
| GET/POST | `/admin/inventory` | Inventory permission | Stock balances |
| POST | `/admin/inventory/{id}/adjustments` | Inventory permission | Audited stock adjustment |
| GET | `/admin/stock-movements` | Inventory permission | Movement history |
| POST | `/admin/catalog/imports` | Import permission | Upload/validate import batch |
| POST | `/admin/catalog/imports/{id}/commit` | Import permission | Commit validated batch |
| GET | `/admin/catalog/exports` | Export permission | Catalogue export job/download |

Bulk operations are asynchronous where large; responses expose job/batch status and row-level errors.

## 7. Admin operations

| Method | Path | Access | Purpose |
|---|---|---|---|
| GET | `/admin/dashboard/summary` | Admin/report permission | Aggregated KPI response |
| GET | `/admin/orders` | Orders permission | Filtered order list |
| PATCH | `/admin/orders/{id}/status` | Orders permission | Authorized transition with reason |
| GET | `/admin/customers` | Customer permission | Customer list/detail with minimization |
| GET/POST | `/admin/quotations` | Sales permission | Quote queue/actions |
| GET/POST | `/admin/promotions` | Promotion permission | Coupon/promotion management |
| GET/POST | `/admin/shipments` | Fulfilment permission | Delivery records/providers |
| GET | `/admin/audit-logs` | Audit permission | Immutable audit search |
| GET | `/admin/reports/sales` | Report permission | Date-range sales report |

All admin mutations require an `Idempotency-Key` or equivalent replay protection where retries can duplicate effects, plus audit logging.

## 8. Error and pagination contract

Example error:

```json
{
  "error": {
    "code": "INSUFFICIENT_STOCK",
    "message": "One or more items are unavailable in the requested quantity.",
    "details": [{"variant_id": "...", "available": 2}],
    "request_id": "req_..."
  }
}
```

Stable error codes will be enumerated in the generated OpenAPI document. Pagination responses include `items`, `page`/`page_size` or `next_cursor`, and `total` only where efficient and authorized.
