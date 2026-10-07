# Node API — Checklist

Audit the real repo against every item. **[must]** blocks launch. **[should]** is strongly recommended. Each item says how to verify it. Run the command or read the file; never assume a pass. Section numbers refer to `REFERENCE.md` in this skill's folder.

## Brief and design
- [ ] **[must]** Every row in the endpoint table of `docs/api-brief.md` exists in the code, and every route in the code is in the table. *Verify: list routes from the code (grep `createRoute`/`app.get|post|…`) and `/openapi.json`, and compare with the table.*
- [ ] **[must]** Every endpoint in the table has an Auth value and, if it takes a record ID, an ownership rule in Notes. *Verify: read the table.*
- [ ] **[should]** Paths follow the conventions: plural nouns, `/v1` prefix, nesting one level at most, domain actions as `POST /things/{id}/action`. *Verify: read the route list.*
- [ ] **[should]** Records use UUIDs, not sequential integers, in URLs. *Verify: read `src/db/schema.ts`.*

## Code health
- [ ] **[must]** The type check passes. *Verify: run `npx tsc --noEmit`.*
- [ ] **[must]** The tests pass. *Verify: run `npx vitest run` (Docker must be running for Testcontainers).*
- [ ] **[must]** The server starts with Node's built-in TypeScript support and the code uses only erasable syntax (no `enum`, no runtime `namespace`). *Verify: `node src/server.ts` starts; `erasableSyntaxOnly` is set in `tsconfig.json`.*
- [ ] **[should]** `package.json` sets `engines.node` to the current Active LTS range, and the lockfile is committed. *Verify: read `package.json`; `git ls-files package-lock.json`.*
- [ ] **[should]** Env vars are parsed in one place with a Zod schema, and the app refuses to start when one is missing. *Verify: read `src/env.ts`; start without `.env` and see it fail clearly.*

## Ownership and auth
- [ ] **[must]** Every handler that takes a record ID (read, update, delete, domain action, nested route) includes the owner or organisation condition in its database query. *Verify: read every such handler. Never sample.*
- [ ] **[must]** Every such endpoint has a test where a second user requests the first user's record and gets 404. *Verify: grep the tests for cross-user cases and match them against the endpoint table.*
- [ ] **[must]** Every non-public endpoint returns 401 without credentials. *Verify: the tests, or call each with no session or key.*
- [ ] **[must]** Admin or role-restricted endpoints check the role and return 403 otherwise. *Verify: read the middleware and its tests.*
- [ ] **[must]** API keys (if used) are stored hashed, never logged, and shown to the user only once. *Verify: read the auth config and the key table; grep the logger config for redaction.*
- [ ] **[should]** Session cookies are `HttpOnly`, `Secure` and `SameSite` in production. *Verify: read the auth config; inspect a `Set-Cookie` header.*

## Input, output and errors
- [ ] **[must]** Every endpoint validates params, query and body with a Zod schema, and write schemas reject unknown fields. *Verify: read each route definition.*
- [ ] **[must]** Responses are mapped from rows explicitly; no password hashes, tokens or other users' data can appear. *Verify: read each handler's return; search for rows returned directly.*
- [ ] **[must]** Errors are RFC 9457 problem details, and no response contains a stack trace or SQL. *Verify: trigger a 404, a 422 and a forced 500 and read the bodies.*
- [ ] **[must]** Every list endpoint is cursor-paginated with a maximum page size. *Verify: read the list handlers; request `?limit=10000`.*
- [ ] **[should]** POSTs that create things or move money honour an `Idempotency-Key`. *Verify: send the same request twice with one key; one record is created.*
- [ ] **[should]** `/openapi.json` is served, `/docs` renders it, and every route and field has a description. *Verify: open both locally.*

## Security
- [ ] **[must]** No secrets in the repo or its git history; `.env` is git-ignored and `.env.example` has names only. *Verify: `git grep -nEi "(secret|api[_-]?key|token|password|DATABASE_URL=)"` and review the hits; `git log --all -- .env`.*
- [ ] **[must]** CORS allows only the real frontend origins from config (or is off for server-to-server APIs), never `*` with credentials. *Verify: read the CORS setup.*
- [ ] **[must]** Rate limiting is on, keyed by user or API key when signed in and by IP otherwise, with a shared store in production and tighter limits on auth and costly routes. *Verify: read the middleware; hit an endpoint past its limit and get 429.*
- [ ] **[must]** Secure headers are set on every response. *Verify: `curl -I` an endpoint and look for `Strict-Transport-Security`, `X-Content-Type-Options`.*
- [ ] **[must]** A request body size limit is set. *Verify: read the middleware; send an oversized body and get 413.*
- [ ] **[should]** Each item of the OWASP API Security Top 10 has a defence (`REFERENCE.md` section 10). *Verify: walk the table against the code.*
- [ ] **[should]** Outbound `fetch` calls have timeouts, and any user-supplied URL is blocked from private IP ranges. *Verify: grep `fetch(`.*
- [ ] **[should]** `npm audit --omit=dev` reports no high or critical issues. *Verify: run it.*

## Data
- [ ] **[must]** Schema changes are SQL migration files committed in `drizzle/` (or the ORM's equivalent), and a migrate script runs them. *Verify: `ls drizzle/`; run the migrate script against a fresh database.*
- [ ] **[must]** Multi-step writes involving money or several tables run in a transaction. *Verify: read those handlers.*
- [ ] **[should]** Every owner and foreign-key column used in filters has an index. *Verify: read the schema.*
- [ ] **[should]** Personal data is collected only where the brief needs it, and there's a way to delete a user's data. *Verify: compare the schema with the brief's data section.*

## Webhooks (if present)
- [ ] **[must]** Inbound webhooks verify the signature on the raw body and reject stale timestamps. *Verify: read the handler; send a request with a bad signature and get 400/401.*
- [ ] **[must]** Inbound handlers are idempotent (event IDs stored with a unique constraint). *Verify: send the same signed event twice; it's processed once.*
- [ ] **[should]** Outbound webhooks are signed, retried with backoff, and logged per delivery. *Verify: read the sender and the deliveries table.*

## Operations
- [ ] **[must]** `GET /health` returns 200 without touching the database, and `GET /ready` checks the database. *Verify: call both; stop the database and call `/ready` (503).*
- [ ] **[must]** The server shuts down gracefully on `SIGTERM` (stops accepting, finishes in-flight requests, closes the pool). *Verify: read `src/server.ts`; send `SIGTERM` during a request.*
- [ ] **[must]** The Dockerfile is multi-stage, uses a slim image of the current Node LTS (major pinned), runs as a non-root user, and has a `HEALTHCHECK`. *Verify: read it; `docker build .` and `docker run` it.*
- [ ] **[should]** Logs are JSON with request IDs, and redact authorisation headers, cookies, keys and passwords. *Verify: read the logger config; make a signed-in request and read the log line.*
- [ ] **[should]** Errors reach Sentry (or the chosen OpenTelemetry backend). *Verify: trigger a test error and see it arrive.*
- [ ] **[should]** CI runs the type check, tests and audit on every push. *Verify: read the CI workflow.*
- [ ] **[should]** `requests.http` covers sign-in, the happy path for each resource, and a cross-user request. *Verify: read it and run it locally.*
