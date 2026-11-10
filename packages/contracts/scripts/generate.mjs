// Generates TypeScript types from the FastAPI OpenAPI schema.
// Usage: node scripts/generate.mjs [openapi-url-or-file]
// Defaults to OPENAPI_URL env var, then http://localhost:8000/openapi.json.
import { execFileSync } from "node:child_process";
import { createRequire } from "node:module";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const require = createRequire(import.meta.url);
const openapiTypescriptBin = join(
  dirname(require.resolve("openapi-typescript/package.json")),
  "bin/cli.js",
);

const source =
  process.argv[2] ??
  process.env.OPENAPI_URL ??
  "http://localhost:8000/openapi.json";

execFileSync(
  process.execPath,
  [openapiTypescriptBin, source, "-o", join(root, "src/schema.d.ts")],
  { stdio: "inherit", cwd: root },
);
