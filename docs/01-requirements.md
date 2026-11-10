# Vitron E-Commerce Platform — Requirements

Status: Phase 0 baseline, 2026-11-10
Scope: documentation and planning only; no application implementation has started.

## 1. Business objective

Build a multi-brand electronics and home-appliance commerce platform for Vitron, Xiaomi and Sonar. The first release supports public product discovery and quoting, while checkout/payment readiness is gated on payment-provider sandbox acceptance and approved business rules.

The storefront and admin dashboard must be independent deployable applications. Product catalogue data must be traceable to the supplied DOCX catalogue; missing commercial or technical data must not be inferred.

## 2. Evidence reviewed

- Current workspace was initially empty and is now connected to the private repository `devstephenke-sys/vitron-ecommerce`, default branch `main`.
- Repository inspection found one commit, `ef5c44b333f655f6ed6306251d17920aa33e6f09` ("Initial commit"), and only a two-line README. There are no existing application files, tests, CI, or deployment configuration to preserve.
- The supplied `Vitron_Sonar_Xiaomi_Product_Catalogue.docx` lists 10 category sections and 102 model/item entries. Table-level extraction confirms 102 data rows, and a flattened catalogue listing supplied during review was checked against the same sections. The guide does not include TV wall mounts in the requested product categories, although it separately lists four wall-mount entries. The classification must be reconciled before import.
- Catalogue prices have no printed currency. Two TV prices are marked not legible. Several descriptions contain model/capacity mismatches. Images are described in the document as representative links/search results, not confirmed model-specific assets.

## 3. In-scope functional requirements

### Customer storefront

- SEO-friendly public homepage, category and brand browsing, search by product name/model, filters, product details, image gallery, related items and comparison.
- Responsive layouts for desktop and mobile; accessible forms, navigation and product content.
- Customer registration/login/profile, addresses, order history, wishlist and contact/support pages.
- Cart and checkout with server-authoritative pricing, stock and delivery quote. Guest checkout is not approved by default.
- Quotation workflow for items, quantities or delivery arrangements that cannot be purchased online.
- Terms, privacy policy, about, delivery and warranty pages must be populated only with approved content.

### Administration

- Role-separated admin, inventory and sales staff permissions.
- Product, brand, category, image, attribute, inventory and stock-movement management.
- Customer, order, payment, shipment, quotation, promotion and delivery administration.
- Bulk catalogue import/export with validation reports and no silent overwrite of published data.
- Dashboard metrics and sales reports with a defined reporting timezone and date range.
- User administration, role/permission management and immutable audit logs.

### Platform/API

- Versioned REST API under `/api/v1`, OpenAPI schema, structured errors, pagination, filtering and idempotency where retries are possible.
- Authentication, authorization, input validation, audit events, background jobs, notification adapters, payment-provider adapters and object-storage adapter.
- Neon PostgreSQL with migrations, indexes, referential integrity, connection pooling and transaction-safe stock/order/payment operations.

## 4. Out of scope for initial production

- Native mobile applications, subscriptions, loyalty points, marketplace sellers, multi-warehouse branch transfers, B2B credit accounts and automated tax filing.
- Storing card PAN/CVV or any provider credential in the application database.
- Publishing unverified catalogue prices, stock, warranty, dimensions or specifications.
- Treating representative catalogue images or search-result links as verified product imagery.

## 5. Acceptance criteria

1. A customer can browse and search only products approved for publication; unavailable/missing-price products cannot be checked out online.
2. An administrator can import a validated catalogue extract, preview discrepancies, publish approved products, and export current catalogue data.
3. A customer can register/login, maintain an address, add cart items, request a quote or complete checkout subject to approved payment rules.
4. Order, payment and inventory transitions are server-authoritative, transactional and auditable.
5. Payment callbacks are verified, idempotent and never trust frontend payment state.
6. Admin permissions prevent inventory-only or sales-only users from performing unrelated actions.
7. All tests required for auth, authorization, catalogue, cart, order, payment callback and inventory pass in CI.
8. Frontend and backend deploy independently to staging and production with documented rollback procedures.

## 6. Business decisions required before implementation gates

| Decision | Proposed default | Gate |
|---|---|---|
| Currency and pricing source | Do not publish until Vitron confirms currency (likely KES, but not assumed) and authoritative prices. | Before product publication/checkout |
| Product availability | Treat unknown stock as unavailable for online purchase; allow quote requests. | Phase 4 |
| Brands in catalogue rows | Infer brand only where the model/catalogue section establishes it; otherwise require confirmation. | Phase 4 |
| Wall mounts/accessories | Include as accessories only after taxonomy and brand ownership are confirmed. | Phase 1/4 |
| VAT/tax and delivery | Obtain approved rates, thresholds, zones and fees; never hard-code guesses. | Before checkout |
| Warranty and specifications | Keep only source-listed facts; request supplier datasheet for structured attributes. | Phase 4 |
| Payments | Start sandbox-only; select providers and credentials after business approval. | Phase 7 |
| Contact channels | Confirm WhatsApp number, support email, phone and business hours. | Phase 8 |
| Legal identity and policies | Confirm legal entity, address, returns/refund terms and privacy controller details. | Before public launch |

The complete decision register and open risks are in `docs/10-decisions-and-risks.md`.
