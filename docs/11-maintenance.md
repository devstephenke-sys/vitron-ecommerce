# Maintenance and Operations Guide

Status: Phase 0 baseline; procedures to be validated during Phase 9/10
Purpose: keep the platform secure, recoverable and understandable after launch.

## 1. Routine operations

### Daily

- Review failed background jobs, payment callbacks and webhook errors.
- Review stock movements for unusual adjustments or negative-stock prevention alerts.
- Review order exceptions: failed payments, unpaid reservations, delivery exceptions.
- Confirm automated backups completed.

### Weekly

- Review audit logs for privileged actions and export activities.
- Review dependency/security alerts.
- Reconcile payment provider settlement reports against internal payment records.
- Review catalogue import errors and unpublished product backlog.

### Monthly/quarterly

- Perform database restore rehearsal in a non-production environment.
- Review API error rates, latency, job backlog and storage growth.
- Rotate secrets according to policy and provider requirements.
- Review user access and disable inactive privileged accounts.
- Re-run authorization and payment security tests.

## 2. Incident response

1. Identify severity and affected component (storefront, admin, API, database, provider).
2. Preserve logs and correlation IDs; avoid copying secrets or payment payloads.
3. Stop unsafe writes if needed: disable checkout/payment initiation or provider callbacks.
4. Communicate status to business owner and customers if personal/data impact is possible.
5. Apply smallest safe fix or rollback.
6. Verify health checks, critical workflows and data integrity.
7. Record timeline, root cause, corrective actions and follow-up owners.

## 3. Database maintenance

- Apply migrations only through reviewed deployment process.
- Monitor table/index growth, slow queries and connection usage.
- Keep audit/order/payment tables append-only at application level.
- Archive old background jobs/outbox events only after retention policy approval.
- Never manually edit financial/order records; use audited adjustment workflows.

## 4. Security maintenance

- Rotate database, JWT, object-storage, payment, email, SMS and WhatsApp credentials on schedule or suspected compromise.
- Review CORS origins, admin access, webhook secrets and rate limits after infrastructure changes.
- Keep dependency updates in non-production first; automate security alerts.
- Ensure logs redact tokens, passwords, payment credentials and unnecessary personal data.

## 5. Release maintenance

- Maintain changelog/release notes for user-visible and operational changes.
- Tag releases and record deployed commit SHA.
- Verify frontend/backend/API versions are compatible through contract tests.
- Keep rollback instructions current for Vercel, Render and Neon.

## 6. Documentation maintenance

Update these docs whenever architecture, API contracts, schema, deployment or business rules change:

- `docs/01-requirements.md`
- `docs/02-architecture.md`
- `docs/03-database-schema.md`
- `docs/04-api-contracts.md`
- `docs/05-product-catalogue.md`
- `docs/06-roadmap.md`
- `docs/07-local-development.md`
- `docs/08-testing-and-quality.md`
- `docs/09-deployment.md`
- `docs/10-decisions-and-risks.md`

## 7. Support contacts and ownership

To be completed before launch:

- Technical owner.
- Database/operations owner.
- Payment provider support contacts.
- Customer support channels.
- On-call/escalation path.
- Business owner approval authority for refunds, price changes and catalogue publication.
