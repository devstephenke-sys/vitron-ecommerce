# Local Development and Repository Structure

Status: Phase 0 baseline
Current repository state: private GitHub repo cloned successfully; only `README.md` exists on `main`.

## 1. Proposed repository layout

```text
.
├── apps/
│   ├── api/                 # FastAPI application
│   ├── storefront/          # Nuxt customer application
│   └── admin/               # Nuxt administration application
├── packages/
│   └── contracts/           # Optional shared API types; avoid coupling apps to backend internals
├── docs/
│   ├── 01-requirements.md
│   ├── 02-architecture.md
│   ├── 03-database-schema.md
│   ├── 04-api-contracts.md
│   ├── 05-product-catalogue.md
│   ├── 06-roadmap.md
│   ├── 07-local-development.md
│   ├── 08-testing-and-quality.md
│   ├── 09-deployment.md
│   ├── 10-decisions-and-risks.md
│   └── 11-maintenance.md
├── infra/                   # Docker, CI support, deployment scripts/config templates
├── .github/workflows/       # CI only; no secrets committed
├── .env.example             # Variable names only, never values
└── README.md
```

Do not create empty directories until the corresponding phase begins. Keep backend and frontend dependencies independently installable.

## 2. Prerequisites

- Windows 11 with Docker Desktop running.
- Git.
- Python 3.12+.
- Node.js LTS compatible with the selected Nuxt version (verify at Phase 1; current machine reports Node 22.13.1).
- Package managers pinned by lockfiles (`uv`/`pip` decision and `pnpm`/`npm` decision made in Phase 1).
- A Neon development branch and local PostgreSQL service/container.
- Provider sandbox credentials only when the relevant integration phase begins.

## 3. Initial local commands (planned, not yet available)

```powershell
# backend
cd apps/api
uv sync                 # or pip install -e .[dev], depending on Phase 1 decision
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000

# storefront
cd apps/storefront
pnpm install
pnpm dev

# admin
cd apps/admin
pnpm install
pnpm dev
```

The exact package manager and commands will be updated after Phase 1 tooling is selected and verified.

## 4. Environment variables

Use `.env.example` files per app with names only. Required groups:

- `APP_ENV`, `API_BASE_URL`, `PUBLIC_API_BASE_URL`.
- Database URL/pooled URL, migration URL and connection limits.
- JWT/access-token settings, refresh-token encryption/signing keys.
- CORS origins and trusted proxy settings.
- Cloudinary/object-storage credentials.
- Payment provider sandbox credentials and webhook secrets.
- Email/SMS/WhatsApp provider credentials.
- Sentry/observability settings if approved.

Never commit `.env`, provider secrets, database URLs, webhook secrets or service-account files. Use a secrets manager or platform environment variables in deployed environments.

## 5. Git workflow

- `main` is protected and deployable.
- Feature branches use `feat/phase-x-description` or `fix/...`.
- Pull requests require CI, review and documentation updates.
- Conventional commit messages are preferred but not enforced until Phase 1.
- Do not commit generated build output, local databases, uploaded files or secrets.

## 6. Current inspection evidence

- Workspace path: `C:\Users\DBTECH AFRICA\Desktop\E-SHOP`.
- Repository clone succeeded from the private GitHub URL.
- Branch: `main`, tracking `origin/main`.
- HEAD: `ef5c44b333f655f6ed6306251d17920aa33e6f09` (`Initial commit`).
- Files at inspection time: `README.md` only.
- Working tree was clean after clone before documentation was added.
