# Launch guide template — Node API

Use this template to write `docs/api-launch.md`. Tailor it to what was actually built: fill in real service names, environment variable names, endpoints and commands, and delete phases or steps that don't apply (e.g. webhooks if there are none, sessions if it only uses API keys). The default host is Railway; if the brief chose another host, swap Phases 2–3 for that host's equivalent steps (see `REFERENCE.md` section 16 in this skill's folder, and the Workers variant below). Keep the legend and the step format.

**Every step has:**
- a checkbox
- a 🧑/🤖/🤝 marker
- a time estimate (and the cost, if any)
- plain-English instructions, with technical terms explained on first use when the user is new
- a ready-to-paste prompt in a quote block for 🤖 steps
- a **You'll know it worked when…** line

---

```markdown
# Launch guide: <API name>

**What you're launching:** <one sentence — what the API does and who calls it>
**Estimated total time:** <x hours> · **Cost:** <e.g. Railway Hobby $5/month (includes $5 of usage; a small API and database usually costs $5–15/month), domain ~$10–15/year, Sentry, Upstash and uptime checks on free tiers>

**Legend**
- 🧑 **You** — needs your accounts, identity, payment or a decision.
- 🤖 **Agent** — paste the prompt into your coding agent.
- 🤝 **Together** — the agent prepares it, you click the final button.

## Phase 0 — Fix blockers (only if the checklist found must-fix items)
- [ ] 🤖 <blocker> — <time>
  > <ready-to-paste prompt>
  You'll know it worked when: <…>

## Phase 1 — Final checks
- [ ] 🤖 Run the checks and build the container — 10 min
  > Run `npx tsc --noEmit` and `npx vitest run` and fix anything that fails. Then run `docker build -t <name> .` and start it with a local database to confirm `/health` and `/ready` return 200.
  You'll know it worked when: the type check and tests pass, and the container answers `/health`.
- [ ] 🤖 List every production setting — 5 min
  > Read the code and `.env.example` and give me a table of every environment variable the API needs in production: name, what it's for, whether it's a secret, and where its value comes from. Don't print any values.
  You'll know it worked when: you have a table like `DATABASE_URL`, `BETTER_AUTH_SECRET`, `BETTER_AUTH_URL`, `CORS_ORIGINS`, `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`, `SENTRY_DSN`, <provider keys>.
- [ ] 🤝 Push the code to GitHub — 5 min
  If the repo isn't on GitHub yet, create a private repository on github.com (New repository, no README).
  > Add the GitHub remote <url>, check that `.env` is git-ignored and not in the history, then push the main branch.
  You'll know it worked when: your files show on GitHub and `.env` doesn't.

## Phase 2 — Accounts and the production database
- [ ] 🧑 Create a Railway account and project — 10 min · $5/month (Hobby)
  Sign up at railway.com with GitHub, choose the Hobby plan, then **New Project → Deploy PostgreSQL**.
  You'll know it worked when: a Postgres service shows as active in your project.
- [ ] 🧑 Turn on database backups — 5 min
  Open the Postgres service → **Backups**, and set a daily schedule.
  You'll know it worked when: the schedule shows as active. (Later, also keep an occasional off-site `pg_dump`: deleting the volume deletes its backups.)
- [ ] 🧑 Create a Redis database for rate limits — 5 min · free tier
  Sign up at upstash.com, create a Redis database in the region closest to your Railway region, and keep the REST URL and token page open.
  You'll know it worked when: you can see the REST URL and token.
- [ ] 🧑 Create a Sentry project — 5 min · free tier
  Sign up at sentry.io, create a Node.js project, and keep the DSN (the address errors are sent to) handy.
  You'll know it worked when: you can see the DSN.

## Phase 3 — Deploy the API
- [ ] 🧑 Add the API service — 5 min
  In the Railway project: **New → GitHub Repo**, pick `<repo>`. Railway finds the Dockerfile.
  You'll know it worked when: a new service appears and starts its first build (it may fail until the settings below are in).
- [ ] 🤝 Set the environment variables — 15 min
  > Give me the exact list of Railway variables to set for this API, with `DATABASE_URL` as `${{Postgres.DATABASE_URL}}`, and say where each value comes from. Don't generate or print any secret values.
  For `BETTER_AUTH_SECRET`, run `openssl rand -base64 32` in your own terminal. Paste each value straight into the API service → **Variables**. Secrets go only there, never in the repo or in chat.
  You'll know it worked when: every variable in the Phase 1 table is set.
- [ ] 🧑 Set the migration and health settings — 5 min
  API service → **Settings → Deploy**: set **Pre-deploy Command** to `node src/db/migrate.ts` and **Healthcheck Path** to `/ready`. Then **Settings → Networking → Generate Domain** for a temporary `*.up.railway.app` address.
  You'll know it worked when: the next deploy shows the migration step succeeding, then the service goes live.
- [ ] 🧑 Deploy — 5 min
  Click **Deploy** (or push to main).
  You'll know it worked when: `https://<temp-domain>/health` returns `{"status":"ok"}` and `/ready` returns 200.

## Phase 4 — Custom domain and HTTPS
- [ ] 🧑 Connect your domain — 15 min (DNS can take up to an hour)
  API service → **Settings → Networking → Custom Domain**, enter `api.<yourdomain>`, then add the CNAME record Railway shows at your domain registrar. Railway issues the HTTPS certificate automatically.
  You'll know it worked when: `https://api.<yourdomain>/health` loads with a padlock.
- [ ] 🤝 Point everything at the real addresses — 10 min
  > Update the production settings list: BETTER_AUTH_URL should be https://api.<yourdomain>, and CORS_ORIGINS should be exactly <https://app.yourdomain> (no wildcards). Tell me which Railway variables to change.
  Update the variables in Railway and let it redeploy.
  You'll know it worked when: your frontend can sign in and call the API from its real domain, and a request from any other origin is blocked by the browser.

## Phase 5 — Webhooks (only if the API receives or sends them)
- [ ] 🧑 Register the production webhook endpoint with <provider> — 10 min
  In <provider>'s dashboard (live mode), add `https://api.<yourdomain>/<webhook path>`, select the events <events>, copy the signing secret into the Railway variable `<NAME>`.
  You'll know it worked when: <provider>'s "send test event" shows a 2xx response.
- [ ] 🤖 Check outbound webhook delivery — 10 min
  > Against production, create a test webhook endpoint (e.g. a free request-inspector URL I give you), trigger one event, and confirm it arrives signed and that a failing endpoint is retried.
  You'll know it worked when: the event arrives with valid `webhook-*` signature headers.

## Phase 6 — Monitoring
- [ ] 🤖 Confirm errors reach Sentry — 5 min
  > Add a temporary route or script that throws a test error in production (or use Sentry's test-event option), confirm it appears in Sentry with the request ID, then remove it.
  You'll know it worked when: the test error shows in Sentry.
- [ ] 🧑 Add an uptime check — 5 min · free tier
  In an uptime service (e.g. UptimeRobot or Better Stack), monitor `https://api.<yourdomain>/ready` every minute and alert your email or phone.
  You'll know it worked when: the monitor shows "Up".
- [ ] 🧑 Set Sentry and Railway alerts — 5 min
  Sentry: alert on new issues. Railway: set a usage limit so a traffic spike can't run up a surprise bill.

## Phase 7 — Production smoke test
- [ ] 🤝 Run the smoke test — 15 min
  > Update requests.http so its base URL is https://api.<yourdomain>. Using two fresh test accounts (A and B), run: GET /health and /ready; sign in as A; <happy path, e.g. create a booking, list bookings, get it by ID>; then as B, GET A's <record> by ID and expect 404; one request with no credentials and expect 401; and repeat a create with the same Idempotency-Key and expect one record. Report each status code. Then delete the test data.
  You'll know it worked when: every request returns the expected code, and B cannot see A's data.
- [ ] 🧑 Check the rate limit — 5 min
  Call one endpoint rapidly past its limit (the agent can give you a one-line `curl` loop).
  You'll know it worked when: you get `429` with a `Retry-After` header.

## Phase 8 — Hand it over
- [ ] 🧑 Publish the docs — 5 min
  Open `https://api.<yourdomain>/docs` and check every endpoint is there and described. Share the link with whoever calls the API (your frontend, developers, or the agent configuration).
  You'll know it worked when: someone else can read the docs and make a successful first call.
- [ ] 🤖 (Third-party developers only) Write a quickstart — 20 min
  > Write a short "Getting started" section for the docs: how to get an API key, the base URL, one authenticated curl example, pagination, errors, rate limits and idempotency keys.

## Variant — Cloudflare Workers (replace Phases 2–3 if the brief chose the edge)
- [ ] 🧑 Create a Cloudflare account and a Postgres database (or a D1 database) — 15 min
- [ ] 🤝 Set up Hyperdrive and secrets — 15 min
  > Create a Hyperdrive config for my Postgres connection string, add its binding to wrangler config with the nodejs_compat flag, and list the secrets I need to set with `wrangler secret put`.
- [ ] 🤖 Migrate and deploy — 10 min
  > Run the database migrations against production, then `wrangler deploy`.
  You'll know it worked when: `https://<worker-domain>/health` returns 200.

## After launch
- Re-run the checklist before every release, and add a cross-user test for every new endpoint.
- Watch Sentry weekly and the uptime monitor's alerts daily.
- Restore a backup into a scratch database once, so you know it works before you need it.
- Move the Dockerfile's Node image to the next LTS when it lands, and run the tests.
```
