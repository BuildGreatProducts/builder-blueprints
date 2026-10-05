# Node API — Reference

> Last verified: 2026-10. Node and its libraries move quickly. Before relying on a function, option or flag, check the live docs (or Context7): https://nodejs.org/api/, https://hono.dev/docs, https://zod.dev, https://orm.drizzle.team/docs, https://www.better-auth.com/docs, https://owasp.org/API-Security/.

## Contents
1. Default stack and versions
2. Runtime: Node and TypeScript
3. Project layout
4. Framework: Hono (and when not)
5. API design conventions
6. Validation, types and OpenAPI docs
7. Errors
8. Auth and ownership
9. Data: Postgres and Drizzle
10. Security: OWASP API Top 10, headers, CORS, rate limits
11. Webhooks
12. Background work
13. Logging, errors and tracing
14. Health, readiness and shutdown
15. Testing
16. Docker and hosts
17. Patterns to avoid

---

## 1. Default stack and versions

One default. Change a line only when the brief clearly calls for it.

| Concern | Default | Version (Oct 2026) | Use instead when… |
|---|---|---|---|
| Runtime | Node, Active LTS | **24** (24.12+). Node **26** becomes LTS on 28 Oct 2026: move to it then. Node 24 enters maintenance on 20 Oct 2026 and is supported until 30 Apr 2028. | — |
| Language | TypeScript, run directly by Node (type stripping) | `typescript` 7.0 for `tsc --noEmit` | — |
| Framework | Hono + `@hono/node-server` | `hono` 4.13, `@hono/node-server` 2.x | Fastify 5.12 (v6 is in alpha) for Node-only, long-running, very high-throughput servers. Express 5.2 only for existing Express code. NestJS 12 only for large teams already standardised on it. |
| Validation + OpenAPI | Zod + `@hono/zod-openapi` | `zod` 4.6, `@hono/zod-openapi` 1.6 (requires Zod 4) | — |
| Docs page | Scalar | `@scalar/hono-api-reference` 0.12 | — |
| Database | Postgres + Drizzle ORM, SQL migrations | `drizzle-orm` 0.45, `drizzle-kit` 0.31 (1.0 is in release candidate; stay on `latest`), `pg` 8 | Prisma 7 (8 is in release candidate) if the team already knows it. |
| User auth | Better Auth | `better-auth` 1.7 | Auth.js is now maintained by the Better Auth team; don't start new projects on it. |
| API keys | Better Auth API key plugin | `@better-auth/api-key` 1.7 | — |
| JWTs (only if needed) | `jose` | 6.2 | — |
| Rate limiting | `hono-rate-limiter` with a Redis store (Upstash) | `hono-rate-limiter` 0.5, `@upstash/redis` 1.39 | — |
| Logging | pino (JSON to stdout) | `pino` 10 | — |
| Errors and tracing | Sentry (built on OpenTelemetry) | `@sentry/node` / `@sentry/hono` 11 | Another OpenTelemetry backend (`@hono/otel` 1.2, `@opentelemetry/sdk-node`) if the team already has one. |
| Background jobs | pg-boss (queue in the same Postgres) | `pg-boss` 12 | Cloudflare Queues on Workers. |
| Tests | Vitest + Testcontainers Postgres | `vitest` 5, `@testcontainers/postgresql` 12 | — |
| Outbound webhooks | Standard Webhooks signing | `standardwebhooks` 1.1 | — |
| Host | Railway (server + managed Postgres) | — | Render (same shape); Fly.io for multi-region; Cloudflare Workers when the brief needs edge/serverless; Vercel Functions if the frontend already lives on Vercel. |

## 2. Runtime: Node and TypeScript

- **Run `.ts` files directly.** Type stripping is stable (from Node 24.12 and 25.2) and on by default: `node src/server.ts`. No build step, no `tsx`, no `dist/`.
- **Node does not type-check.** It only removes types. Run `tsc --noEmit` in CI and before every deploy.
- **Only erasable syntax.** No `enum`, no runtime `namespace`, no constructor parameter properties. Use `as const` objects or union types instead. `erasableSyntaxOnly` makes `tsc` enforce this.
- **Imports need the `.ts` extension** (`import { app } from './app.ts'`). `tsconfig` `paths` aliases don't work at runtime; use relative imports or `package.json` `"imports"` (`#lib/*`).
- **Type-only imports** must say `import type`. `verbatimModuleSyntax` enforces it.
- Built in, no packages needed: `--watch` (dev restarts), `--env-file=.env` (load env vars), global `fetch`, `node --test`, `crypto.randomUUID()`, `crypto.timingSafeEqual()`.

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "esnext",
    "module": "nodenext",
    "noEmit": true,
    "strict": true,
    "allowImportingTsExtensions": true,
    "erasableSyntaxOnly": true,
    "verbatimModuleSyntax": true,
    "skipLibCheck": true
  }
}
```

```json
// package.json (extract)
{
  "type": "module",
  "engines": { "node": ">=24.12" },
  "scripts": {
    "dev": "node --watch --env-file=.env src/server.ts",
    "start": "node src/server.ts",
    "typecheck": "tsc --noEmit",
    "test": "vitest run",
    "db:generate": "drizzle-kit generate",
    "db:migrate": "node --env-file=.env src/db/migrate.ts"
  }
}
```

## 3. Project layout

```
my-api/
├── src/
│   ├── server.ts            # starts the HTTP server, handles shutdown
│   ├── app.ts               # builds the app (tests import this, not server.ts)
│   ├── env.ts               # parses process.env with Zod; crash at startup if invalid
│   ├── auth.ts              # Better Auth instance
│   ├── db/
│   │   ├── client.ts        # Drizzle + pg pool
│   │   ├── schema.ts        # tables
│   │   └── migrate.ts       # runs migrations (pre-deploy command)
│   ├── middleware/          # requireUser, requireApiKey, rate limits, logging
│   ├── routes/<resource>.ts # one file per resource: schemas + routes + handlers
│   └── lib/                 # problem+json, pagination, idempotency, webhooks
├── drizzle/                 # generated SQL migrations (committed)
├── test/
├── requests.http            # smoke-test requests (VS Code REST Client / JetBrains)
├── Dockerfile
├── .env.example             # every variable name, no values
├── drizzle.config.ts
├── tsconfig.json
└── package.json
```

- **Config:** read env vars in one place (`env.ts`) through a Zod schema, and import `env` everywhere else. A missing secret should stop the server at boot, not fail on the first request.
- `.env` is in `.gitignore`. `.env.example` is committed.

## 4. Framework: Hono (and when not)

Hono is built on Web Standards (`Request`/`Response`), so the same app runs on Node, Bun, Deno, Cloudflare Workers and Vercel. It has typed routes, first-class Zod/OpenAPI support, and an RPC client (`hc` from `hono/client`) that gives a TypeScript frontend fully typed calls with no code generation.

```ts
// src/app.ts (shape, not complete)
import { OpenAPIHono } from '@hono/zod-openapi'
import { requestId } from 'hono/request-id'
import { secureHeaders } from 'hono/secure-headers'
import { cors } from 'hono/cors'
import { bodyLimit } from 'hono/body-limit'
import { Scalar } from '@scalar/hono-api-reference'

export const app = new OpenAPIHono<AppEnv>({ defaultHook: returnValidationProblem })

app.use(requestId())
app.use(secureHeaders())
app.use('*', cors({ origin: env.CORS_ORIGINS, credentials: true }))
app.use(bodyLimit({ maxSize: 1024 * 1024 }))

app.on(['GET', 'POST'], '/api/auth/*', (c) => auth.handler(c.req.raw)) // Better Auth
app.route('/v1', bookingsRoutes)

app.doc31('/openapi.json', { openapi: '3.1.0', info: { title: 'Bookings API', version: '1.0.0' } })
app.get('/docs', Scalar({ url: '/openapi.json' }))

app.notFound((c) => problem(c, 404, 'Not Found'))
app.onError(handleError)
```

```ts
// src/server.ts
import { serve } from '@hono/node-server'
const server = serve({ fetch: app.fetch, port: env.PORT })
```

- Type `c.get('user')` and friends with an `AppEnv` type (`{ Variables: { user: User; requestId: string } }`).
- **Fastify instead** when the brief says Node-only, long-running and very high throughput, or the team already runs Fastify. Use `fastify-type-provider-zod` with `@fastify/swagger`, plus `@fastify/helmet`, `@fastify/cors` and `@fastify/rate-limit`. Every other section here still applies.
- **Express 5** only to extend an existing Express app. Don't start new APIs on it.

## 5. API design conventions

- **Resources are plural nouns:** `/v1/bookings`, `/v1/bookings/{id}`. Nest one level at most (`/v1/groomers/{id}/bookings`); deeper relationships become filters (`/v1/bookings?customerId=…`).
- **Domain actions** that aren't plain updates are `POST` on a sub-path: `POST /v1/bookings/{id}/cancel`, `POST /v1/payments/{id}/refund`.
- **Version in the path** from day one: `/v1`. Infrastructure endpoints (`/health`, `/ready`, `/openapi.json`, `/docs`) sit at the root.
- **JSON fields in camelCase.** Timestamps in ISO 8601 UTC (`2026-10-05T09:30:00Z`). Money as integer minor units plus a currency (`{ "amount": 2500, "currency": "GBP" }`).
- **IDs are UUIDs**, never sequential integers (they let anyone count your records and guess others').
- **Methods and status codes:**

| Situation | Code |
|---|---|
| Read OK / update OK | 200 |
| Created | 201 with a `Location` header |
| Deleted, nothing to return | 204 |
| Malformed request (bad JSON) | 400 |
| Not signed in, or bad API key | 401 |
| Signed in, but the role isn't allowed this action | 403 |
| Doesn't exist, **or exists but belongs to someone else** | 404 (don't reveal it exists) |
| Conflict (duplicate, wrong state) | 409 |
| Validation failed | 422 |
| Rate limited | 429 with `Retry-After` |
| Unexpected failure | 500 (no stack traces in the body) |

- **Cursor pagination on every list.** `GET /v1/bookings?limit=20&cursor=…` returns `{ "data": [...], "nextCursor": "…" | null }`. The cursor is an opaque base64url string of the last row's sort key (e.g. `createdAt` + `id`). Default limit 20, maximum 100. Never return unbounded lists. Avoid offset pagination: it gets slow and skips or repeats rows as data changes.
- **Idempotency keys** on any `POST` that creates something or moves money. The client sends `Idempotency-Key: <uuid>`. Store `(callerId, key) → request hash, status, response body` for 24 hours. A repeat with the same body returns the stored response; a repeat with a different body returns 422; a repeat while the first is still running returns 409.
- **Partial updates** use `PATCH` with only the changed fields. Use `PUT` only for full replacement.

## 6. Validation, types and OpenAPI docs

**Zod is the single source of truth.** Each route's schemas validate the request, type the handler, and generate the OpenAPI 3.1 document. Never write types or docs separately from the schema.

```ts
import { createRoute, z } from '@hono/zod-openapi'

const Booking = z.object({
  id: z.uuid(),
  startsAt: z.iso.datetime(),
  status: z.enum(['pending', 'confirmed', 'cancelled']),
}).openapi('Booking')

const getBooking = createRoute({
  method: 'get',
  path: '/bookings/{id}',
  summary: 'Get one booking',
  description: 'Returns a booking the caller owns.', // agents read these: write them well
  request: { params: z.object({ id: z.uuid() }) },
  responses: {
    200: { description: 'The booking', content: { 'application/json': { schema: Booking } } },
    404: { description: 'Not found', content: { 'application/problem+json': { schema: Problem } } },
  },
})
```

- **Response schemas are separate from database rows.** Map rows to response objects explicitly, so internal fields (password hashes, other users' emails, cost prices) can never leak by accident.
- Reject unknown input fields on writes (`z.strictObject` or `.strict()`), so callers can't set fields they shouldn't (e.g. `role`, `ownerId`).
- Put limits on everything: string `max`, array `max`, number `min`/`max`.
- Serve the spec at `/openapi.json` and the Scalar page at `/docs`. If AI agents are callers, every route and field needs a plain-English `description`.

## 7. Errors

Use **RFC 9457 problem details** (`Content-Type: application/problem+json`) for every error, so clients and agents can handle them one way.

```json
{
  "type": "https://api.example.com/problems/validation",
  "title": "Validation failed",
  "status": 422,
  "detail": "startsAt must be in the future",
  "instance": "/v1/bookings",
  "requestId": "0c6a…",
  "errors": [{ "path": "startsAt", "message": "Must be in the future" }]
}
```

- One `onError` handler turns thrown `HTTPException`s into problem responses and everything else into a generic 500, which is logged with the request ID and sent to Sentry.
- The `defaultHook` on `OpenAPIHono` turns Zod failures into the 422 shape above.
- Never put stack traces, SQL or internal hostnames in a response.

## 8. Auth and ownership

**Users (sessions):** Better Auth, mounted at `/api/auth/*`, with the Drizzle adapter. Generate its tables with `npx auth@latest generate`, then create a Drizzle migration for them. Email and password plus any social logins the brief needs. Cookies are `HttpOnly`, `Secure` and `SameSite=Lax` in production. A `requireUser` middleware calls `auth.api.getSession({ headers: c.req.raw.headers })` and returns 401 if there's none.

**Machine clients (API keys):** the `@better-auth/api-key` plugin. Keys are hashed before storage by default (never turn that off), shown to the user once, sent in the `x-api-key` header, and can expire and carry permissions. Set a recognisable prefix (e.g. `bk_live_`) so leaked keys are easy to spot and revoke. Rate-limit per key.

**JWTs:** only when another system issues or requires them (e.g. verifying tokens from an identity provider). Use `jose` with the provider's JWKS (`createRemoteJWKSet` + `jwtVerify`), and check `iss`, `aud` and `exp`. Don't invent your own JWT sessions when Better Auth already does sessions.

**Ownership (object-level authorisation) — the most important rule in this file.** Authentication says who the caller is. It says nothing about whether *this* booking is theirs. Every query that takes an ID from the request includes the owner condition in the same query:

```ts
const [booking] = await db.select().from(bookings)
  .where(and(eq(bookings.id, id), eq(bookings.groomerId, user.id)))
if (!booking) throw new HTTPException(404, { message: 'Not Found' })
```

- Apply it to reads, updates, deletes, domain actions, nested routes and list filters alike.
- For organisations, check membership: `eq(bookings.orgId, user.activeOrgId)` plus the role.
- Role checks (function-level authorisation) are separate: an admin-only route checks the role, then still scopes by organisation.
- Every such endpoint has a test where user B asks for user A's record and gets 404.

## 9. Data: Postgres and Drizzle

- **Postgres** for almost everything. Use the host's managed Postgres with daily backups on.
- **Drizzle** schema in `src/db/schema.ts`; `drizzle-kit generate` writes SQL migrations to `drizzle/`, which are committed and reviewed. Never use `drizzle-kit push` against production.
- **Run migrations on deploy** from a small script, as the host's pre-deploy (release) step, so the app never starts against an old schema:

```ts
// src/db/migrate.ts
import { drizzle } from 'drizzle-orm/node-postgres'
import { migrate } from 'drizzle-orm/node-postgres/migrator'
const db = drizzle(process.env.DATABASE_URL!)
await migrate(db, { migrationsFolder: './drizzle' })
await db.$client.end()
```

- **Safe migrations:** add columns as nullable or with a default; backfill; then tighten. Rename in two releases (add new, copy, switch, drop old). Never drop a column the running version still reads.
- Columns: `uuid('id').primaryKey().defaultRandom()`, `createdAt`/`updatedAt` timestamps with time zone, a foreign key and an **index on every owner column** (`groomerId`, `orgId`) you filter by.
- Use transactions (`db.transaction(async (tx) => …)`) for multi-step writes, especially anything involving money.
- Existing database: `drizzle-kit pull` introspects it into a schema file.
- Set a pool size that fits the plan's connection limit, and a statement timeout.

## 10. Security: OWASP API Top 10, headers, CORS, rate limits

The **OWASP API Security Top 10 (2023)** is still the current edition. Map each to a defence:

| # | Risk | Defence in this stack |
|---|---|---|
| API1 | Broken object level authorisation | Owner condition in every query (section 8) + cross-user tests |
| API2 | Broken authentication | Better Auth; hashed API keys; rate-limited auth routes |
| API3 | Broken object property level authorisation | Strict input schemas; explicit response mapping (section 6) |
| API4 | Unrestricted resource consumption | Rate limits, body limit, pagination caps, timeouts, upload size limits |
| API5 | Broken function level authorisation | Role checks on admin and destructive routes |
| API6 | Unrestricted access to sensitive business flows | Tighter limits and abuse checks on sign-up, checkout, invites, messaging |
| API7 | Server-side request forgery | Never fetch user-supplied URLs without an allow-list or a private-IP block |
| API8 | Security misconfiguration | Secure headers, locked CORS, no debug output, `NODE_ENV=production` |
| API9 | Improper inventory management | Brief table = OpenAPI doc = code; old versions retired |
| API10 | Unsafe consumption of APIs | Validate third-party responses with Zod; timeouts on every outbound `fetch` (`AbortSignal.timeout(…)`) |

- **Secure headers:** `secureHeaders()` from `hono/secure-headers` on every response.
- **CORS:** `cors()` from `hono/cors` with an explicit list of real origins from `env`. Never `*` with credentials. APIs called only by servers and agents don't need CORS at all.
- **Rate limiting:** `rateLimiter` from `hono-rate-limiter` with its `RedisStore` and an Upstash Redis client, so limits hold across restarts and instances. Key by user ID or API key when signed in, and by client IP otherwise (read the IP from the header your host documents, and only when behind that proxy). Send standard `RateLimit` headers and `Retry-After`. Use tighter limits on auth, sign-up and anything that sends email or costs money.
- **Body limits** with `bodyLimit()`; **request timeouts** with `timeout()` from `hono/timeout` on slow routes.
- Dependencies: `npm audit --omit=dev` in CI; commit the lockfile.

## 11. Webhooks

**Receiving (e.g. from a payment provider):**
- Read the **raw body** (`await c.req.text()`) and verify the signature before parsing. Prefer the provider's SDK helper; otherwise HMAC-SHA256 with the shared secret and `crypto.timingSafeEqual`.
- Reject events whose timestamp is more than 5 minutes old (replay protection).
- **Idempotent handler:** store each event ID in a `processed_events` table with a unique constraint and skip duplicates. Providers retry and can deliver twice.
- Return 2xx quickly and do slow work in a background job.

**Sending (to your customers):**
- Sign with the **Standard Webhooks** scheme (`standardwebhooks` package): `webhook-id`, `webhook-timestamp` and `webhook-signature` headers, one secret per endpoint, shown once.
- Store each delivery in a table; retry failures with exponential backoff and jitter (e.g. 1 min, 5 min, 30 min, 2 h, 6 h, 24 h), then mark the endpoint failing and tell the owner.
- Customer-supplied URLs must be HTTPS and must not resolve to private or internal IPs (SSRF). Use a short timeout.
- Document every event type and payload in the docs.

## 12. Background work

- Anything slow or retry-worthy (emails, AI calls, file processing, outbound webhooks) goes on a queue, not in the request.
- Default: **pg-boss** in the same Postgres. No extra service. Run the worker in the same process at launch; split it into its own service when load needs it.
- Jobs must be idempotent (they can run twice) and carry IDs, not whole objects.
- On Cloudflare Workers, use Cloudflare Queues instead.

## 13. Logging, errors and tracing

- **pino**, JSON to stdout; the host collects it. One line per request: method, path, status, duration, request ID, user or key ID.
- **Redact** `authorization`, `cookie`, `x-api-key`, passwords and tokens with pino's `redact` option. Never log request bodies that contain personal data.
- **Sentry** for errors and performance: initialise it in `src/instrument.ts` and load it first (`node --import ./src/instrument.ts src/server.ts`), and add `@sentry/hono`. Follow Sentry's current Hono guide for the exact setup.
- Sentry is built on OpenTelemetry; if the team already has an OTel backend, use `@opentelemetry/sdk-node` with the `pg` and `http` instrumentations and `@hono/otel` instead.

## 14. Health, readiness and shutdown

- `GET /health` → 200 `{ "status": "ok" }`, no database call. The host and Docker `HEALTHCHECK` use it to see the process is alive.
- `GET /ready` → `SELECT 1` with a short timeout; 200 if fine, 503 if the database is unreachable or the server is shutting down. Use it as the host's deploy health check so traffic only switches to a ready instance.
- **Graceful shutdown** on `SIGTERM` (sent by every host on redeploy): mark not-ready, `server.close()` to stop new connections and let in-flight requests finish, stop the job worker, close the DB pool (`db.$client.end()`), then exit. Force-exit after ~20 seconds.

## 15. Testing

- **Vitest**. Import `app` from `src/app.ts` and call `app.request('/v1/bookings', { headers })`. No running server needed.
- **Testcontainers** starts a real Postgres in Docker in Vitest's global setup and runs the migrations. Don't mock the database; ownership bugs live in queries.
- **Required tests per endpoint:** happy path; validation failure (422); not signed in (401); **cross-user access (404)**; role denied (403) where roles apply. Plus: idempotent repeat returns the same response; webhook with a bad signature is rejected; rate limit returns 429 (one test is enough).
- `requests.http` holds hand-runnable requests for the smoke test: sign in, create, list, get, and a cross-user get with a second account.
- CI on every push: `npm ci`, `tsc --noEmit`, `vitest run`, `npm audit --omit=dev`.

## 16. Docker and hosts

**Dockerfile** — multi-stage, slim, non-root, with a health check. No build stage needed because Node runs the TypeScript directly.

```dockerfile
FROM node:24-slim AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

FROM node:24-slim
ENV NODE_ENV=production
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY package.json ./
COPY src ./src
COPY drizzle ./drizzle
USER node
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD node -e "fetch('http://127.0.0.1:'+(process.env.PORT||3000)+'/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"
CMD ["node", "src/server.ts"]
```

Add a `.dockerignore` (`node_modules`, `.env`, `.git`, `test`). Once Sentry is set up, the last line becomes `CMD ["node", "--import", "./src/instrument.ts", "src/server.ts"]`. Change `24` to `26` once Node 26 is LTS. Listen on `process.env.PORT`.

**Railway (default).** A service deployed from the GitHub repo (it uses the Dockerfile), plus a Railway Postgres service. Set `DATABASE_URL` as a reference variable (`${{Postgres.DATABASE_URL}}`). Set **Settings → Deploy → Pre-deploy Command** to `node src/db/migrate.ts`; if it fails, the deploy stops and the old version keeps running. Set the healthcheck path to `/ready`. Turn on scheduled backups for the Postgres volume (note: wiping the volume deletes its backups, so also take an occasional off-site `pg_dump`). Hobby plan: $5/month including $5 of usage.

**Render** is the same shape (web service + Render Postgres, pre-deploy command, health check path) if the user prefers it.

**Fly.io** when the brief needs several regions close to users: `fly launch` reads the Dockerfile, migrations go in `[deploy] release_command` in `fly.toml`, and Postgres via Fly's managed Postgres.

**Cloudflare Workers** only when the brief needs edge or serverless (global low latency, spiky traffic, already on Cloudflare). Hono runs natively; `export default app` instead of `serve()`. Postgres through **Hyperdrive** (connection pooling to an existing Postgres), or **D1** (SQLite) for simple data. Secrets via `wrangler secret put`, deploy with `wrangler deploy`, enable the `nodejs_compat` flag. Differences: no long-running process (no graceful shutdown, no in-process worker: use Queues), no pino (use structured `console.log`), and run migrations from CI before deploy.

**Vercel Functions** if the frontend already lives on Vercel: Hono deploys with zero config. Use a marketplace Postgres (e.g. Neon), run migrations in CI before deploy, and keep functions short.

## 17. Patterns to avoid

- Checking that the user is signed in but not that the record is theirs (BOLA, API1).
- Returning database rows straight to the client, or accepting whole objects into `update()`.
- Sequential integer IDs in URLs.
- Offset pagination and unbounded lists.
- Hand-written types or docs that drift from the Zod schemas.
- `enum`, `namespace` and other non-erasable TypeScript (Node can't strip them).
- Skipping `tsc --noEmit` because "it runs fine".
- Secrets in code, `.env.example`, Dockerfiles, logs or chat. Committing `.env`.
- `cors({ origin: '*' })` on an API that uses cookies.
- In-memory rate limits in production with more than one instance.
- `drizzle-kit push` against production, or running migrations by hand.
- Verifying webhook signatures against parsed-then-restringified JSON (use the raw body).
- Doing slow work (emails, AI calls) inside the request.
- Stack traces in error responses. Logging tokens or request bodies with personal data.
- Running as root in the container. Using `latest` Node images.
- Starting new projects on Express, Auth.js or Node 22.
- Mocking the database in tests that are meant to catch authorisation bugs.
