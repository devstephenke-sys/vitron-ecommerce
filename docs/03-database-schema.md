# Database Schema Baseline

Status: Phase 2 migrated — identity/access, addresses, audit_logs and background_jobs tables exist (migration `0002_identity_and_access`); catalog/inventory/commerce tables remain Phase 4+ designs
Database: Neon PostgreSQL
Identifier convention: UUID primary keys unless an external immutable identifier is required. All timestamps are timezone-aware UTC. Monetary values use fixed precision (`NUMERIC(14,2)` initially) plus ISO currency code; fractional quantities are not supported initially.

## 1. Identity and access

- `users`: id, email (unique, normalized), phone (optional unique), password_hash, display_name, status, email_verified_at, phone_verified_at, created_at, updated_at.
- `roles`: id, code (unique), name, description, is_system.
- `permissions`: id, code (unique), description.
- `role_permissions`: role_id, permission_id.
- `user_roles`: user_id, role_id, assigned_by, assigned_at.
- `refresh_tokens`: id, user_id, token_hash, family_id, expires_at, revoked_at, replaced_by_id, created_at.
- `auth_events`: id, user_id nullable, event_type, ip_hash, user_agent_hash, metadata JSONB, created_at.

Authorization must check permissions, not role names only. Customer, administrator, inventory manager and sales staff are role bundles over permissions.

## 2. Addresses and customers

- `addresses`: id, user_id nullable (guest quote/contact may be unlinked), recipient_name, phone, line1, line2, city, county/region, country_code, postal_code, is_default, created_at, updated_at.
- `customer_profiles`: user_id PK/FK, preferred_contact_method, marketing_opt_in, notes restricted by permission, created_at, updated_at.

Do not duplicate customer data into orders; order snapshots retain only the fields needed for fulfilment/history.

## 3. Catalog

- `brands`: id, slug unique, name, legal_name, logo_image_id nullable, status, created_at, updated_at.
- `categories`: id, parent_id nullable self-FK, slug unique per parent or global according to final routing decision, name, description, sort_order, status, timestamps.
- `products`: id, brand_id FK, category_id FK, model_number, name, slug unique, summary, description, status (`draft`, `review`, `published`, `archived`), publication_source, source_reference, price_amount nullable, currency_code nullable, tax_class, warranty_text nullable, created_at, updated_at.
- `product_variants`: id, product_id FK, sku unique, name/option values JSONB or normalized option tables if needed, status. Start with one default variant per product; add variants only when real SKUs require it.
- `product_images`: id, product_id/variant scope, storage_key, alt_text, sort_order, width, height, checksum, source_url nullable, verified_at nullable, status.
- `product_attributes`: id, product_id FK, attribute_key, attribute_value, unit nullable, source, confidence, verified_by/at.
- `attribute_definitions`: id, key unique, label, data_type, unit, filterable, searchable, status — added when structured filters exceed simple JSONB needs.
- `related_products`: product_id, related_product_id, relationship_type, sort_order; composite PK and indexes.

Catalog import rows must retain source row identity and validation state so re-imports are idempotent and reviewable.

## 4. Inventory

- `inventory_items`: id, variant_id unique FK, quantity_on_hand integer non-negative, quantity_reserved integer non-negative, reorder_level nullable, updated_at. Check constraint: reserved <= on_hand where business policy allows; reservations may require a separate policy decision.
- `stock_movements`: id, inventory_item_id FK, movement_type (`receipt`, `reservation`, `release`, `sale`, `return`, `adjustment`, `transfer`), quantity_delta, reason, reference_type/reference_id, actor_user_id nullable, created_at.
- `stock_reservations`: id, order_id or cart/checkout attempt, inventory_item_id, quantity, status, expires_at, created_at, updated_at.

Initial policy proposal: reserve stock during checkout with a short expiry; convert reservation to sale on successful payment; release on payment failure/cancellation. This must be approved before implementation because it affects overselling and customer experience.

## 5. Commerce

- `carts`: id, user_id FK, status, currency_code, created_at, updated_at, expires_at.
- `cart_items`: id, cart_id FK, variant_id FK, quantity, unit_price_snapshot nullable, added_at; unique(cart_id, variant_id) if one line per variant.
- `orders`: id, order_number unique, user_id FK, status, currency_code, subtotal, discount_total, tax_total, shipping_total, grand_total, shipping_address_snapshot JSONB, billing_address_snapshot JSONB, customer_snapshot JSONB, coupon_id nullable, quotation_id nullable, placed_at, cancelled_at, created_at, updated at.
- `order_items`: id, order_id FK, variant_id nullable for historical tolerance, sku_snapshot, model_snapshot, name_snapshot, quantity, unit_price, discount_amount, tax_amount, line_total, attributes_snapshot JSONB.
- `order_status_history`: id, order_id FK, from_status, to_status, reason, actor_user_id nullable, created_at.
- `wishlist_items`: user_id, variant_id/product_id, created_at; composite uniqueness.

Prices are revalidated at checkout. Order totals are immutable after confirmation except through explicit refund/adjustment workflows.

## 6. Payments and fulfilment

- `payments`: id, order_id FK, provider, provider_payment_id nullable, idempotency_key unique, amount, currency_code, status (`pending`, `authorized`, `paid`, `failed`, `cancelled`, `refunded`), phone_number_reference nullable, callback_received_at, verified_at, created_at, updated_at.
- `payment_events`: id, payment_id FK, provider_event_id, event_type, signature_valid boolean, payload_hash, processed_at, created_at; unique provider event identity where available.
- `payment_refunds`: id, payment_id FK, amount, currency_code, status, provider_refund_id, reason, created_at.
- `shipments`: id, order_id FK, provider, status, tracking_number, shipped_at, delivered_at, address_snapshot JSONB, created_at, updated_at.
- `delivery_zones`: id, name, areas JSONB or normalized area table later, fee_amount, currency_code, estimated_days_min/max, active.
- `quotations`: id, reference unique, user_id/contact details, status, currency_code, valid_until, internal_notes restricted, created_at, updated_at.
- `quotation_items`: id, quotation_id FK, product/variant reference nullable, description_snapshot, quantity, unit_price nullable, notes.

Never store raw callback payloads containing unnecessary personal/payment data; retain a hash and minimal verified metadata.

## 7. Promotions and engagement

- `coupons`: id, code unique, type (`percentage`, `fixed_amount`), value, currency_code nullable, max_discount, min_order_amount, usage_limit, per_user_limit, starts_at, ends_at, status.
- `coupon_redemptions`: id, coupon_id FK, user_id/order_id, redeemed_at; enforce limits transactionally.
- `notifications`: id, user_id nullable, channel, template_key, status, provider_reference, sent_at, created_at.
- `notification_templates`: key, channel, locale, subject/body template, status.

Promotion eligibility and stacking rules require business approval before checkout enablement.

## 8. Audit and operations

- `audit_logs`: id, actor_user_id nullable, action, entity_type, entity_id, before_jsonb, after_jsonb, ip_hash, user_agent_hash, correlation_id, created_at. Records are append-only at the application layer; database grants should prevent normal update/delete where practical.
- `background_jobs`: id, job_type, payload JSONB, status, run_at, attempts, locked_at, locked_by, last_error, created_at, updated_at.
- `outbox_events`: id, aggregate_type, aggregate_id, event_type, payload JSONB, occurred_at, published_at nullable. Use for notifications/reporting without coupling core transactions to providers.
- `import_batches`: id, source_filename, source_hash, status, total_rows, valid_rows, invalid_rows, uploaded_by, created_at, completed_at.
- `import_row_results`: id, import_batch_id FK, source_row_number, entity_type, external_key, status, errors JSONB, entity_id nullable.

## 9. Required constraints and indexes

- Foreign keys for all owned relationships; `ON DELETE` behavior chosen explicitly (prefer restrict for financial/catalog history).
- Unique constraints for normalized email, SKU, product slug, coupon code, order number, payment idempotency key and provider event identity.
- Indexes on product status/brand/category/price, product model/name search fields (choose PostgreSQL full-text or trigram extension during Phase 2), order user/status/placed_at, payment provider/status, inventory variant, audit entity/time and job status/run_at.
- Check constraints for non-negative quantities, valid totals, status enums and currency format.
- Database transactions for cart conversion, order creation, stock reservation/deduction, payment state transition and coupon redemption.

## 10. Migration and data integrity rules

1. Every schema change has an Alembic revision and rollback/forward-fix strategy.
2. Never edit a published migration; add a new revision.
3. Seed roles/permissions/categories only through controlled migrations or idempotent seed commands.
4. Catalogue import must be dry-runnable and report row-level errors before commit.
5. Production data changes require backup confirmation and audit actor.
