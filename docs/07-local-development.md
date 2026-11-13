# Local Development and Repository Structure

Status: Phase 1 — commands below were executed and verified on Windows 11 during Phase 1 implementation.
Repository state: monorepo with `apps/api` (FastAPI), `apps/storefront` and `apps/admin` (Nuxt 3), `packages/contracts`, `infra/` and `.github/workflows/`.

## 1. Repository layout (implemented)

```text
.
├── apps/
│   ├── api/                 # FastAPI application (Python 3.12, uv)
│   ├── storefront/          # Nuxt 3 customer application
│   └── admin/               # Nuxt 3 administration application
├── packages/
│   └── contracts/           # TypeScript types generated from OpenAPI
├── docs/                    # 01–11 planning and engineering documents
├── infra/
│   └── docker-compose.yml   # Local PostgreSQL 16 (host port 5433)
├── .github/workflows/       # backend.yml, frontend.yml
├── .env.example             # Shared variable names only
├── pnpm-workspace.yaml      # pnpm workspace: apps/*, packages/*
└── README.md
```

Applications are independently installable: each Nuxt app has its own `package.json`, `.env.example` and scripts. `@vitron/contracts` is consumed via a `file:` dependency so apps do not require publishing.

## 2. Prerequisites (verified versions)

- Windows 11 with Docker Desktop running.
- Git.
- Python 3.12.3 (verified) with [`uv`](https://docs.astral.sh/uv/) 0.12+.
- Node.js 22.13.1 LTS (verified) with pnpm 10.x (`corepack enable` or `npm i -g pnpm`).
- npm 10+ is also present but pnpm is the selected package manager for all JS/TS work.

## 3. Verified local commands

```powershell
# --- infrastructure ---
docker compose -f infra/docker-compose.yml up -d     # PostgreSQL on localhost:5433
docker compose -f infra/docker-compose.yml down

# --- backend (apps/api) ---
cd apps/api
uv sync                                              # creates .venv, installs deps
uv run alembic upgrade head                          # apply migrations
uv run alembic revision --autogenerate -m "message"  # new migration (future phases)
uv run uvicorn app.main:app --reload --port 8000     # API on :8000
uv run ruff check . && uv run ruff format --check .  # lint
uv run pytest -q                                     # tests (needs Postgres running — see below)
uv run python scripts/create_admin.py --email you@example.com --password 'a-strong-password'  # first admin

# --- frontend dependencies (repo root, once) ---
cd ..\..   # or: cd <repo root>
pnpm install                                           # installs all workspace projects

# --- storefront (apps/storefront) ---
cd apps/storefront
pnpm dev        # http://localhost:3000
pnpm build      # production build -> .output/
pnpm exec nuxi prepare && pnpm exec nuxt typecheck

# --- admin (apps/admin) ---
cd apps/admin
pnpm dev        # http://localhost:3001
pnpm build
pnpm exec nuxi prepare && pnpm exec nuxt typecheck
```

## 4. Environment variables

Each app ships a `.env.example`. Copy to `.env` to override; never commit `.env`.

| App | Variables |
|---|---|
| `apps/api` | `APP_ENV`, `DATABASE_URL` (asyncpg URL), `CORS_ORIGINS` (comma-separated), `LOG_LEVEL`, `API_V1_PREFIX`, `AUTH_SECRET_KEY`, `ACCESS_TOKEN_TTL_SECONDS`, `REFRESH_TOKEN_TTL_SECONDS`, `PASSWORD_RESET_TTL_SECONDS` |
| `apps/storefront` | `NUXT_PUBLIC_API_BASE`, `NUXT_PUBLIC_APP_NAME`, optional `NUXT_API_BASE_SERVER` |
| `apps/admin` | same as storefront |

`NUXT_PUBLIC_*` values are embedded in the browser bundle — never place secrets there. Server-only secrets belong in `NUXT_*` runtime config or platform env vars.

**Neon alternative:** set `DATABASE_URL` in `apps/api/.env` to a Neon development-branch connection string (use the `postgresql+asyncpg://` form; Neon provides `postgresql://` — swap the scheme). Alembic reads the same variable.

## 5. API contract type generation

TypeScript types for the frontend are generated from the FastAPI OpenAPI schema — see `packages/contracts/README.md`. Short version: start the API, then `cd packages/contracts && pnpm generate`. Commit the regenerated `src/schema.d.ts` with the backend change.

## 6. Git workflow

- `main` is the deployable branch; work happens on `feat/phase-x-...` branches with pull requests.
- Conventional commit messages are used.
- Never commit `.env`, `.venv`, `node_modules`, `.nuxt`, `.output`, local databases or secrets (enforced by `.gitignore`).

## 7. Known local-environment notes

- The Docker Compose PostgreSQL publishes host port **5433** (not 5432) because this development machine already runs a PostgreSQL service on 5432. If your machine has no local PostgreSQL, you may change the mapping back to `5432:5432` and update `DATABASE_URL` accordingly.
- `uv run pytest` requires a reachable PostgreSQL: the session fixture runs `alembic upgrade head` against `DATABASE_URL`, and DB-backed tests truncate data tables between tests. Start `infra/docker-compose.yml` first.
- To log in to the admin app locally: run migrations, create an admin with `scripts/create_admin.py`, start the API and `apps/admin` (`pnpm dev`, port 3001), then sign in at `/login`.
- pnpm warns about ignored build scripts for `esbuild`/`vue-demi` on first install; builds work without approving them, but `pnpm approve-builds` can be used if a tool requires it.
