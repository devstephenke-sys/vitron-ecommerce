# @vitron/contracts

Shared TypeScript types for the Vitron storefront and admin applications.

## Approach

Types are **generated from the FastAPI OpenAPI schema** (`/openapi.json`)
using [`openapi-typescript`](https://openapi-ts.dev/). Backend Pydantic
schemas remain the single source of truth — frontend code never
duplicates API models by hand.

`src/schema.d.ts` is a generated file. Do not edit it manually.

## Regenerating types

1. Start the API:

   ```powershell
   cd apps/api
   uv run uvicorn app.main:app --reload --port 8000
   ```

2. From this directory, with the API running:

   ```powershell
   pnpm install        # first time only
   pnpm generate       # reads http://localhost:8000/openapi.json
   ```

   Or point at any environment:

   ```powershell
   $env:OPENAPI_URL="https://api-staging.example.com/openapi.json"; pnpm generate
   ```

3. Commit the regenerated `src/schema.d.ts` together with the backend
   change that altered the API.

## Usage in Nuxt apps

Consume the generated `paths`/`components` types, e.g.:

```ts
import type { paths } from "@vitron/contracts";

type HealthLiveResponse =
  paths["/api/v1/health/live"]["get"]["responses"][200]["content"]["application/json"];
```

The package is consumed as source (TypeScript) — no build step is
required for Phase 1.
