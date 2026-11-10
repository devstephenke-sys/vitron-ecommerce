# Deployment Architecture

Status: Phase 0 plan; no deployment has been performed
Target: independently deployable frontend and backend with managed PostgreSQL and object storage.

## 1. Target topology

| Component | Platform | Notes |
|---|---|---|
| Storefront | Vercel | Nuxt SSR/SSG as appropriate; public SEO routes |
| Admin | Vercel | Separate project/environment; stricter access and no public indexing |
| API | Render Web Service | FastAPI with `/api/v1`; horizontal scaling only after statelessness verified |
| Background jobs | Render Background Worker | Same backend image/package; database-backed queue initially |
| Database | Neon PostgreSQL | Separate development/staging/production branches/projects |
| Media | Cloudinary or compatible object storage | Signed uploads, transformations, backup/export plan |
| DNS/TLS | Vercel/Render managed or approved DNS | Enforce HTTPS and security headers |

## 2. Environment promotion

1. Local development uses synthetic data and sandbox providers.
2. Pull request previews may use staging backend/database branch where safe.
3. `main` deploys to staging automatically after CI passes.
4. Production deployment is manual or protected-branch controlled after staging smoke tests and approval.
5. Database migrations are backward-compatible when possible; destructive migrations require maintenance window and backup.

## 3. Backend deployment requirements

- Single container/image for web and worker, selected by command.
- Health endpoints for platform checks and readiness including database connectivity.
- Stateless application instances; sessions/tokens stored in database or signed token design, not local memory.
- Environment-specific CORS origins, callback URLs, allowed hosts and trusted proxies.
- Graceful shutdown for background jobs and HTTP requests.
- Structured logs with request/correlation IDs and no secrets/payment payloads.
- Render autoscaling only after load test evidence; connection pool sized below Neon limits.

## 4. Frontend deployment requirements

- Separate Vercel projects for storefront and admin to allow independent domains, env vars, access controls and rollback.
- Storefront uses public API base URL; admin uses authenticated API base URL.
- Runtime vs build-time env vars must be deliberate; secrets never exposed through `NUXT_PUBLIC_`/`PUBLIC_` variables.
- Admin should support IP allowlist, Vercel Authentication/SSO or equivalent if approved.
- SEO metadata, sitemap, robots and canonical URLs configured for storefront only.
- Image optimization through approved CDN/object-storage provider.

## 5. Database and backup

- Neon branching for development/staging; production branch protected.
- Automated backups/PITR enabled according to Neon plan.
- Restore rehearsal documented and performed before production launch and quarterly thereafter.
- Migration credentials separated from application runtime credentials where supported.
- Connection pooling configured for serverless frontend/serverful API patterns.

## 6. Secrets and configuration

- Store all secrets in Vercel/Render/Neon/provider dashboards or approved secrets manager.
- Rotate provider keys and webhook secrets on suspected exposure.
- Use separate credentials per environment.
- Document required environment variable names in each app's `.env.example`.
- Never place secrets in Git, screenshots, tickets or logs.

## 7. Deployment checklist

- [ ] CI green on release commit.
- [ ] Database backup completed.
- [ ] Alembic migrations reviewed and applied to target environment.
- [ ] Environment variables verified without printing values.
- [ ] CORS/callback URLs point to correct environment.
- [ ] Payment provider remains sandbox/test until explicit production approval.
- [ ] Storefront/admin/API health checks pass.
- [ ] Critical smoke tests pass.
- [ ] Monitoring/alerts verified.
- [ ] Rollback version and procedure recorded.
- [ ] Business owner approves release.

## 8. Rollback

- Frontend: redeploy previous Vercel deployment.
- API/worker: redeploy previous Render deploy; avoid incompatible schema rollback unless migration plan supports it.
- Database: prefer forward-fix migrations; restore from backup only for catastrophic data loss with explicit approval.
- Provider callbacks: disable or route to maintenance state if verification fails.
