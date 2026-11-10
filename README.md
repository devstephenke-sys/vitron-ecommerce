# Vitron E-Commerce Platform

Custom multi-brand electronics and home-appliance commerce platform for Vitron, Xiaomi and Sonar.

## Current status

Phase 1 — repository and development foundation **implemented** (pending merge of `feat/phase-1-foundation`).

- `apps/api` — FastAPI backend (Python 3.12, SQLAlchemy 2 async, Alembic, health endpoints, structured logging, request IDs, CORS, standard error envelope).
- `apps/storefront` — Nuxt 3 customer storefront (TypeScript, Tailwind CSS, Pinia).
- `apps/admin` — Nuxt 3 admin application with auth-ready route structure and permission-aware navigation foundation.
- `packages/contracts` — TypeScript types generated from the FastAPI OpenAPI schema.
- `infra/docker-compose.yml` — local PostgreSQL for development.
- `.github/workflows` — CI for backend (lint, tests, migrations) and frontend (typecheck, builds).

See `docs/` for the full documentation set. Phase 0 planning documents remain the architecture baseline; Phase 1 deviations are recorded in `docs/10-decisions-and-risks.md`.

## Repository layout

```text
.
├── apps/
│   ├── api/                 # FastAPI application
│   ├── storefront/          # Nuxt customer application
│   └── admin/               # Nuxt administration application
├── packages/
│   └── contracts/           # Generated API types (openapi-typescript)
├── docs/                    # Requirements, architecture, schema, API, roadmap
├── infra/                   # docker-compose for local PostgreSQL
├── .github/workflows/       # CI pipelines
├── .env.example             # Variable names only — never commit real values
└── pnpm-workspace.yaml      # Frontend workspace (pnpm)
```

## Quick start (Windows 11)

Prerequisites: Python 3.12+, [uv](https://docs.astral.sh/uv/), Node.js 22 LTS, pnpm 10, Docker Desktop.

```powershell
# 1. Start local PostgreSQL (host port 5433)
docker compose -f infra/docker-compose.yml up -d

# 2. Backend
cd apps/api
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000

# 3. Frontend dependencies (from repo root, once)
cd ..\..   # back to repo root
pnpm install

# 4. Storefront (new terminal)
cd apps/storefront
pnpm dev    # http://localhost:3000

# 5. Admin (new terminal)
cd ..\admin
pnpm dev    # http://localhost:3001
```

Copy each app's `.env.example` to `.env` to override defaults. The full guide, including Neon as an alternative database and troubleshooting, is in `docs/07-local-development.md`.

## Verification commands

```powershell
# Backend
cd apps/api
uv run ruff check .
uv run ruff format --check .
uv run pytest -q
uv run alembic upgrade head

# Frontend (from each app directory)
pnpm exec nuxi prepare
pnpm exec nuxt typecheck
pnpm build
```

## Documentation

- [Requirements](docs/01-requirements.md)
- [System architecture](docs/02-architecture.md)
- [Database schema baseline](docs/03-database-schema.md)
- [API contract baseline](docs/04-api-contracts.md)
- [Product catalogue baseline](docs/05-product-catalogue.md)
- [Implementation roadmap](docs/06-roadmap.md)
- [Local development](docs/07-local-development.md)
- [Testing and quality](docs/08-testing-and-quality.md)
- [Deployment](docs/09-deployment.md)
- [Decisions and risks](docs/10-decisions-and-risks.md)
- [Maintenance](docs/11-maintenance.md)
