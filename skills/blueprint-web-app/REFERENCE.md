# Web App — Reference

> Last verified: 2026-10. Next.js, Convex and Clerk all move quickly. Before relying on an API, option or CLI flag, read the version-matched Next.js docs in `node_modules/next/dist/docs/` (the project's `AGENTS.md` points there), the Convex guidelines installed by `npx convex ai-files install`, or the live docs: https://docs.convex.dev, https://nextjs.org/docs, https://clerk.com/docs, https://docs.stripe.com.
>
> Versions at last check: `convex` 1.46 · Next.js 16.4 (16.x is Active LTS; 16.3.8 is the last 16.3 patch) · React 19.3 · `@clerk/nextjs` 7.9 · `@convex-dev/stripe` 0.1 · `@convex-dev/resend` 0.2 · `@convex-dev/rate-limiter` 0.4 · `@convex-dev/workpool` 0.4 · `convex-helpers` 0.1 · `convex-test` 0.0.60 · Vitest 5.0 · `@convex-dev/eslint-plugin` 5.0 · Tailwind CSS 4.3 · shadcn CLI v4 · TypeScript 7.0.

## Contents
1. Default stack
2. Project setup
3. Project layout
4. Docs and AI files
5. Convex functions
6. Validators
7. Auth: Clerk and the users table
8. Ownership and roles
9. Data: schema, indexes and queries
10. Next.js and Convex together
11. Side effects: actions, scheduling, crons and components
12. Payments: Stripe
13. Email: Resend
14. File storage
15. AI features
16. Environment variables
17. Testing
18. Deploying: Vercel + Convex
19. Public pages, SEO and analytics
20. Patterns to avoid

---

## 1. Default stack

One default. Change a line only when the brief clearly calls for it.

| Concern | Default | Use instead when… |
|---|---|---|
| Frontend | Next.js App Router, TypeScript, Turbopack, Tailwind CSS v4 + shadcn/ui | — |
| Backend and database | Convex Cloud (queries, mutations, actions, HTTP actions, scheduler, crons, file storage) | — |
| Auth | **Clerk** via `ConvexProviderWithClerk` | The user wants no third-party auth service: Better Auth through the `@convex-dev/better-auth` component. Convex Auth (`@convex-dev/auth`) is still beta, with a v2 in progress; don't start new production apps on it. |
| Payments | Stripe Checkout + Customer Portal through the official `@convex-dev/stripe` component | Polar (`@convex-dev/polar`) if they want a merchant of record that handles sales tax for them. Stripe Connect for marketplaces that pay out to sellers. |
| Email | Resend through `@convex-dev/resend` | — |
| Rate limits | `@convex-dev/rate-limiter` | — |
| Tests | Vitest + `convex-test` + `@edge-runtime/vm` | — |
| Hosting | Vercel (Next.js) + Convex Cloud (backend), deployed together by one build command | — |

**Why Clerk is the default.** Convex itself has no single default, but its docs list the third-party providers first, and Clerk has the most mature fit: a first-party Convex integration (`convex/react-clerk`), a Next.js SDK with prebuilt sign-in, sign-up and profile UI, and Organizations for team apps. Convex Auth is beta and its own docs say it has fewer features. The Better Auth component is the right choice when the user wants everything in their own Convex database and no extra vendor; it costs more setup and more maintenance.

## 2. Project setup

```
npx create-next-app@latest <name> --yes
cd <name>
npm install convex
npx convex dev            # log in, create the project, write .env.local, create convex/
npx shadcn@latest init
npm install @clerk/nextjs # or: npx -y clerk@latest init
```

- `--yes` accepts the recommended Next.js defaults (TypeScript, Tailwind, App Router, Turbopack, `@/*` alias) and writes `AGENTS.md` and `CLAUDE.md`.
- `npx convex dev` writes `CONVEX_DEPLOYMENT` and `NEXT_PUBLIC_CONVEX_URL` to `.env.local`, creates `convex/`, and offers to install the Convex AI files. Keep it running in a second terminal while building, or run both with `npx convex dev --start 'next dev'`.
- `npm create convex@latest` has Next.js + Clerk templates, but at last check they still used Next.js 14 and Tailwind 3. Start from `create-next-app` instead.

## 3. Project layout

```
app/
├── layout.tsx                 # <html lang>, fonts, ClerkProvider > ConvexClientProvider, metadataBase
├── ConvexClientProvider.tsx   # 'use client': ConvexReactClient + ConvexProviderWithClerk
├── (marketing)/               # public, indexed: home, pricing, legal
│   ├── page.tsx
│   └── pricing/page.tsx
├── (app)/                     # signed in, noindex
│   ├── layout.tsx             # app shell, robots: { index: false }
│   └── dashboard/page.tsx
├── sign-in/[[...sign-in]]/page.tsx
├── sitemap.ts / robots.ts     # public pages only
└── not-found.tsx
proxy.ts                       # clerkMiddleware (v16 name for middleware.ts)
convex/
├── schema.ts                  # tables, validators, indexes
├── auth.config.ts             # tells Convex to trust Clerk's tokens
├── convex.config.ts           # components (app.use(...)) and typed env vars
├── http.ts                    # HTTP actions: Stripe, Clerk, Resend webhooks
├── crons.ts
├── lib/auth.ts                # getCurrentUser, requireUser, requireMember
├── users.ts, teams.ts, <feature>.ts
├── <feature>.test.ts          # convex-test tests live next to the functions
└── _generated/                # written by Convex; commit it, never edit it
components/                    # shadcn/ui in components/ui
```

- `convex/_generated/` holds the typed `api`, `internal`, `components` and `env` objects and the `query`/`mutation`/`action` builders. Always import builders from `./_generated/server`, never from `convex/server`.
- `proxy.ts` replaced `middleware.ts` in Next.js 16 and runs on the Node.js runtime. Clerk's docs say to name the file by the Next.js version: `proxy.ts` on 16+.
- `params` and `searchParams` are Promises in Next.js 16. Await them.

## 4. Docs and AI files

- **Next.js:** `AGENTS.md` points at the version-matched docs in `node_modules/next/dist/docs/`. Keep your own instructions outside its `<!-- BEGIN:nextjs-agent-rules -->` markers.
- **Convex AI files:** `npx convex ai-files install` writes `convex/_generated/ai/guidelines.md`, adds managed sections to `AGENTS.md` and `CLAUDE.md`, and installs Convex's agent skills. `npx convex ai-files status` and `update` keep them current. Read the guidelines before writing Convex code.
- **Convex plugin and MCP server:** in Claude Code, `/plugin install convex@claude-plugins-official` adds Convex's skills, a reviewer agent and the Convex MCP server (tables, data, logs, function specs, env vars). Elsewhere, `npx -y convex@latest mcp start`. Production access is off by default; leave it off.
- **Lint:** add `@convex-dev/eslint-plugin` (`...convexPlugin.configs.recommended` in `eslint.config.js`). Also turn on `require-access-control` and `no-collect-in-query`, which aren't in the recommended set.

## 5. Convex functions

| Type | Use for | Can | Can't |
|---|---|---|---|
| `query` | Reading data; every `useQuery` is a live subscription | Read the database | Write, call `fetch`, read the clock reliably |
| `mutation` | Changing data, as one transaction | Read and write the database, schedule functions | Call `fetch` or third-party APIs |
| `action` | Calling the outside world (Stripe, AI, email APIs) | `fetch`, SDKs, `ctx.runQuery`/`ctx.runMutation` | Touch `ctx.db` directly; not transactional |
| `internalQuery` / `internalMutation` / `internalAction` | Anything only the server should run (webhook handlers, crons, follow-up work) | Same as above | Be called from the browser |
| `httpAction` (in `http.ts`) | Webhooks and public HTTP endpoints, at `https://<deployment>.convex.site/<path>` | Read the raw request, call `ctx.runMutation` | Use `ctx.db` directly |

- **Public functions are public endpoints.** Anyone can call any exported `query`, `mutation` or `action` with any arguments. If only your own code should call it, make it `internal*` and call it through `internal.<file>.<name>`.
- **Mutations are transactions.** Everything inside one either commits or doesn't, and conflicting writes retry automatically. Put a whole user action in one mutation; don't split it across several calls from the client or an action.
- **The side-effect pattern:** a mutation writes the record and calls `ctx.scheduler.runAfter(0, internal.x.doWork, { id })`; the internal action calls the API and saves the result with `ctx.runMutation(internal.x.saveResult, …)`. The scheduled call only runs if the mutation commits.
- **Database calls name the table:** `ctx.db.get("items", id)`, `ctx.db.patch("items", id, { done: true })`, `ctx.db.delete("items", id)`. The ESLint rule `explicit-table-ids` enforces it.
- **Errors:** throw `new ConvexError("Not found")` (from `convex/values`) for errors the user should see. Production deployments hide the message of any other thrown error from the client.
- **No wall clock in queries.** Queries don't re-run as time passes. Pass the time in as an argument, or set a flag with a scheduled mutation.
- `"use node";` only in files whose actions need Node.js built-ins or a Node-only SDK, and never in a file that exports queries or mutations. `fetch` works without it.

## 6. Validators

Every function has `args` validators, and public functions also have `returns` validators, so nothing is returned by accident and the client gets exact types.

```ts
import { ConvexError, v } from "convex/values";
import { mutation } from "./_generated/server";
import { requireMember } from "./lib/auth";

export const rename = mutation({
  args: { checklistId: v.id("checklists"), title: v.string() },
  returns: v.null(),
  handler: async (ctx, { checklistId, title }) => {
    const checklist = await ctx.db.get("checklists", checklistId);
    if (!checklist) throw new ConvexError("Not found");
    await requireMember(ctx, checklist.teamId, ["owner", "editor"]);
    if (title.trim().length === 0 || title.length > 200) throw new ConvexError("Title must be 1–200 characters");
    await ctx.db.patch("checklists", checklistId, { title: title.trim() });
    return null;
  },
});
```

- `v.id("table")` for IDs, never `v.string()`. Use `v.union(v.literal(…), …)` for fixed choices and `v.optional(…)` for optional fields.
- Validators don't check lengths or ranges. Check limits in the handler (string length, array size, number ranges).
- Define a shape once in `schema.ts` and derive variants with `.pick()`, `.omit()`, `.partial()` and `.extend()`; `schema.doc("table")` gives the validator for a whole stored document.
- Lists use `paginationOptsValidator` for args and `paginationResultValidator(item)` for `returns` (both from `convex/server`).
- Never accept `userId`, `role`, `ownerId` or `plan` as arguments for authorisation. Derive them on the server.

## 7. Auth: Clerk and the users table

**Wiring (follow https://docs.convex.dev/auth/clerk for current detail):**
1. In the Clerk Dashboard, activate the **Convex integration** and copy the Frontend API URL (the issuer).
2. `npx convex env set CLERK_JWT_ISSUER_DOMAIN <url>`. Clerk's own guide calls the same value `CLERK_FRONTEND_API_URL`; the name only has to match `auth.config.ts`.
3. `convex/auth.config.ts`:
   ```ts
   import type { AuthConfig } from "convex/server";
   export default {
     providers: [{ domain: process.env.CLERK_JWT_ISSUER_DOMAIN!, applicationID: "convex" }],
   } satisfies AuthConfig;
   ```
4. `app/ConvexClientProvider.tsx` (`'use client'`): create `new ConvexReactClient(process.env.NEXT_PUBLIC_CONVEX_URL!)` and render `<ConvexProviderWithClerk client={convex} useAuth={useAuth}>` (`ConvexProviderWithClerk` from `convex/react-clerk`, `useAuth` from `@clerk/nextjs`).
5. In `app/layout.tsx`, `<ClerkProvider>` wraps `<ConvexClientProvider>`.
6. `proxy.ts` exports `clerkMiddleware()` with the matcher from Clerk's quickstart. Use `createRouteMatcher` and `auth.protect()` to send signed-out visitors on `/app` routes to sign-in. This is for user experience only; the real check is in every Convex function.

- In the UI, gate on Convex's view of auth, not just Clerk's: `useConvexAuth()`, or `<Authenticated>`, `<Unauthenticated>` and `<AuthLoading>` from `convex/react`. Clerk can be signed in a moment before Convex has validated the token.
- Clerk's prebuilt components (`<SignInButton>`, `<UserButton>`, `<UserProfile>`, `<OrganizationSwitcher>`) save building auth screens.
- In production, Clerk needs a production instance on your own domain (DNS records), `pk_live_`/`sk_live_` keys, and your own OAuth credentials for Google and other social logins.

**The users table.** Store app users in Convex, keyed by `identity.tokenIdentifier` (the stable, canonical ID Convex gives every signed-in identity):

```ts
// convex/schema.ts (extract)
users: defineTable({
  tokenIdentifier: v.string(),
  clerkId: v.string(),            // identity.subject, for Clerk webhooks
  name: v.string(),
  email: v.string(),
}).index("by_tokenIdentifier", ["tokenIdentifier"]).index("by_clerkId", ["clerkId"]),
```

- A `users.store` mutation, called once by the client after sign-in, inserts or updates the row from `ctx.auth.getUserIdentity()` (see https://docs.convex.dev/auth/database-auth).
- A Clerk webhook at `/clerk-users-webhook` in `convex/http.ts`, verified with the `svix` package and `CLERK_WEBHOOK_SECRET`, handles `user.updated` and `user.deleted`, so profile changes and account deletion in Clerk's UI reach Convex.

**Helpers every function uses:**

```ts
// convex/lib/auth.ts
import { ConvexError } from "convex/values";
import type { QueryCtx } from "../_generated/server";
import type { Doc, Id } from "../_generated/dataModel";

export async function getCurrentUser(ctx: QueryCtx) {
  const identity = await ctx.auth.getUserIdentity();
  if (!identity) return null;
  return await ctx.db.query("users")
    .withIndex("by_tokenIdentifier", (q) => q.eq("tokenIdentifier", identity.tokenIdentifier))
    .unique();
}

export async function requireUser(ctx: QueryCtx) {
  const user = await getCurrentUser(ctx);
  if (!user) throw new ConvexError("Not signed in");
  return user;
}

export async function requireMember(ctx: QueryCtx, teamId: Id<"teams">, roles?: Doc<"memberships">["role"][]) {
  const user = await requireUser(ctx);
  const membership = await ctx.db.query("memberships")
    .withIndex("by_teamId_and_userId", (q) => q.eq("teamId", teamId).eq("userId", user._id))
    .unique();
  if (!membership || (roles && !roles.includes(membership.role))) throw new ConvexError("Not found");
  return { user, membership };
}
```

Mutations can pass their `ctx` to these helpers. To make the check impossible to forget, wrap the builders with `customQuery`/`customMutation` and `customCtx` from `convex-helpers/server/customFunctions`, so `ctx.user` always exists in signed-in functions.

## 8. Ownership and roles

**The most important rule in this file.** `ctx.auth` says who the caller is. It says nothing about whether *this* checklist is theirs. Every function that takes a record ID loads the record, then checks it belongs to the caller (or the caller's team) before reading or changing it.

- **Single-user apps:** every owned table has a `userId: v.id("users")` field and an index starting with it. Compare `doc.userId === user._id`; if it doesn't match, throw the same "Not found" as a missing record, so nobody can probe which IDs exist.
- **Team apps:** every team-owned table has `teamId` and an index starting with it. Check membership (and the role, for destructive or admin actions) with `requireMember`. Lists query `withIndex("by_teamId…", q => q.eq("teamId", teamId))` after the membership check, never the whole table.
- **Teams live in Convex.** Keep `teams`, `memberships` (`teamId`, `userId`, `role`) and `invitations` tables in Convex and check them in every function. If you use Clerk Organizations for the UI, sync them into these tables with Clerk's webhooks; don't rely on organisation claims in the token, which don't update live when a user switches organisation.
- **Invitations:** store a random token and the invited email; the accepting mutation checks the signed-in user's email matches and the invitation hasn't expired or been used.
- **Plan gates:** a mutation that creates something paid-only checks the team's or user's subscription status in Convex before writing.
- **Admins:** an `isAdmin` field set by hand in the dashboard (never by a mutation the user can call), checked by an admin helper. Admin functions still validate arguments.
- Component functions (Stripe, Resend, rate limiter) aren't callable from the browser. Your own functions wrap them, so do the auth check before calling into a component.
- Every function that takes an ID has a test where user B is refused user A's record (section 17).

## 9. Data: schema, indexes and queries

- **One `convex/schema.ts`** with `defineSchema` and `defineTable` from `convex/server`. Every document gets `_id` and `_creationTime` automatically.
- **Relationships are ID fields** (`checklistId: v.id("checklists")`) with an index, not nested arrays. Anything that grows without limit (items, comments, messages, events) is its own table. Documents have a 1 MB limit, and every update rewrites the whole document.
- **Indexes for every lookup** in the brief. Name them after their fields in order (`by_teamId_and_status`); query fields in that same order. `_creationTime` is appended to every index, so `withIndex("by_teamId", …).order("desc")` gives newest first for free.
- **`withIndex`, not `.filter`.** `.filter()` scans every row the query reads; on a table that grows, it gets slow and expensive. Use it only for an extra condition after an index has narrowed the range.
- **No unbounded `.collect()`.** Use `.take(n)` for "the latest few" or `.paginate(args.paginationOpts)` with `usePaginatedQuery` in the client for anything a user scrolls. `.collect()` is fine only on a range that is small by design (a team's members, a checklist's ten settings).
- **Counting:** there's no `count()`. Keep a counter field updated in the same mutation, or use `@convex-dev/aggregate` for counts, sums and rankings over many rows.
- **Search:** `searchIndex` in the schema and `withSearchIndex` for full-text search; `vectorIndex` and `ctx.vectorSearch` (actions only) for semantic search.
- **Schema changes on live data:** add new fields as `v.optional`, backfill with `@convex-dev/migrations`, then make them required. Adding an index to a big table blocks the deploy while it backfills; declare it with `staged: true` first.
- Keep fast-changing data (presence, typing, counters) in its own small table, away from documents many queries read.

## 10. Next.js and Convex together

- **Client components** use `useQuery(api.items.list, { checklistId })`, `useMutation` and `useAction`. Results are live: when data changes, every open tab updates. `useQuery` returns `undefined` while loading; pass `"skip"` as the args until you have them.
- **Server rendering for first paint** where it matters (the dashboard, a shared page): `preloadQuery` in a Server Component and `usePreloadedQuery` in the client component, which then stays live.

```tsx
// app/(app)/checklists/[id]/page.tsx
import { preloadQuery } from "convex/nextjs";
import { auth } from "@clerk/nextjs/server";
import { api } from "@/convex/_generated/api";
import type { Id } from "@/convex/_generated/dataModel";

export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const token = (await (await auth()).getToken()) ?? undefined;
  const preloaded = await preloadQuery(api.checklists.get, { id: id as Id<"checklists"> }, { token });
  return <Checklist preloaded={preloaded} />;
}
```

- `fetchQuery`, `fetchMutation` and `fetchAction` (from `convex/nextjs`) call Convex from Server Components, Server Actions and Route Handlers, non-reactively. Always pass `{ token }` for signed-in calls. Separate `fetchQuery` calls on one page aren't guaranteed to see the same snapshot.
- `preloadQuery` opts the page out of static rendering. Keep public marketing pages free of it so they stay static.
- A record ID from the URL is only a string. The function's `v.id()` validator rejects malformed IDs; treat that error as "Not found".
- **Optimistic updates** (`useMutation(...).withOptimisticUpdate(...)`) for actions that must feel instant, like ticking a box. Don't build a second API layer in Route Handlers or Server Actions for things the client can call Convex for directly.

## 11. Side effects: actions, scheduling, crons and components

- **Scheduling:** `ctx.scheduler.runAfter(ms, internal.x.y, args)` and `runAt(timestamp, …)` from mutations and actions. Use them for follow-up work, reminders and retries.
- **Crons:** `convex/crons.ts` with `cronJobs()`, using `crons.interval(...)` or `crons.cron(...)` and an `internal` function reference. Avoid scheduling everything at the top of the hour.
- **Big jobs:** a mutation processes one batch (`.take(100)`) and schedules itself for the next, so no single transaction hits its limits.
- **Components** are installable building blocks with their own tables. `npm install` the package, then `app.use(...)` in `convex/convex.config.ts`; reference them as `components.<name>`. Official ones to reach for first:

| Need | Component |
|---|---|
| Per-user or global rate limits (sign-ups, AI calls, invites) | `@convex-dev/rate-limiter` |
| Queues with limited parallelism, retries, completion callbacks | `@convex-dev/workpool` |
| Long multi-step processes that survive failures | `@convex-dev/workflow` |
| Counts, sums and leaderboards | `@convex-dev/aggregate` |
| Payments | `@convex-dev/stripe` (or `@convex-dev/polar`) |
| Email | `@convex-dev/resend` |
| Who's online / viewing | `@convex-dev/presence` |
| AI chat threads with history and tools | `@convex-dev/agent` |
| Streaming AI text to the browser | `@convex-dev/persistent-text-streaming` |
| Data migrations | `@convex-dev/migrations` |

Most are 0.x. Check each component's README for the current API before using it.

## 12. Payments: Stripe

Default: the official **`@convex-dev/stripe`** component. It creates Checkout sessions and Customer Portal sessions, links Stripe customers to your users or teams, verifies Stripe's webhook signature, and syncs customers, subscriptions, payments and invoices into its own tables so you can query them live.

- `app.use(stripe)` in `convex.config.ts`; `registerRoutes(http, components.stripe, { webhookPath: "/stripe/webhook" })` in `convex/http.ts`.
- Convex env vars `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET`. The webhook endpoint in Stripe is `https://<deployment>.convex.site/stripe/webhook`, subscribed to the events the component's README lists.
- A public **action** creates the session: check `ctx.auth`, `getOrCreateCustomer` for that user (or team), then `createCheckoutSession` with the price ID, mode (`subscription` or `payment`), success and cancel URLs built from a `SITE_URL` env var, and the user or team ID in the metadata. The client redirects to the returned URL.
- **Entitlements:** a query reads the subscription from the component (e.g. `listSubscriptionsByUserId`, `getSubscriptionByOrgId`) and returns the user's plan. Mutations that gate paid features check it. Never trust a "plan" sent by the client, and never grant access from the success URL alone: wait for the webhook.
- Add custom logic for an event (a welcome email, provisioning) with the `events` option on `registerRoutes`.
- Manage billing with `createCustomerPortalSession`. Turn on Stripe Tax if the user needs to charge VAT or sales tax. Keep price IDs in env vars or one config file.
- Test end to end in test mode with the Stripe CLI (`stripe listen --forward-to https://<dev-deployment>.convex.site/stripe/webhook`) and test cards, then switch to live keys and a live webhook endpoint at launch.

## 13. Email: Resend

- `@convex-dev/resend`: `app.use(resend)`, then `new Resend(components.resend, { testMode: false })` once you're ready to email real addresses (it defaults to `testMode: true`, which only delivers to Resend's test addresses).
- `resend.sendEmail(ctx, { from, to, subject, html })` from a mutation or action. The component queues, batches, retries and de-duplicates, so a retried mutation doesn't send twice.
- Env vars `RESEND_API_KEY` and, for delivery status, `RESEND_WEBHOOK_SECRET` with a route at `/resend-webhook` calling `resend.handleResendEventWebhook(ctx, req)`.
- Verify a sending domain (e.g. `mail.<domain>`) in Resend with its DNS records before launch. Clerk sends the auth emails (verification codes, magic links) itself.
- Every marketing or digest email has an unsubscribe link and respects a preference stored in Convex.

## 14. File storage

1. A mutation checks auth and returns `await ctx.storage.generateUploadUrl()`.
2. The client `POST`s the file to that URL with its `Content-Type` and gets back `{ storageId }`.
3. A second mutation checks auth and ownership, reads the file's size and type with `ctx.db.system.get("_storage", storageId)`, deletes it with `ctx.storage.delete(storageId)` if it's too big or the wrong type, and otherwise saves `storageId` (`v.id("_storage")`) on the record.

- Serve files with `ctx.storage.getUrl(storageId)` from a query that checks the caller may see the record. The URL works for anyone who has it, so only hand it to people allowed to see the file.
- Delete the stored file when its record is deleted. Don't use the deprecated `ctx.storage.getMetadata`.

## 15. AI features

- Call models from **actions** (or internal actions scheduled by a mutation), never from the browser. Keys live in Convex env vars.
- Rate-limit every AI call per user with `@convex-dev/rate-limiter`, and cap free-plan usage in Convex, so one user can't run up the bill.
- Save results through internal mutations; the UI updates live as they land. For chat with history and tools, use `@convex-dev/agent`; to stream tokens to the browser, `@convex-dev/persistent-text-streaming`.
- For semantic search, store embeddings with a `vectorIndex` and query with `ctx.vectorSearch` in an action, then load the documents through an internal query that also checks access.
- Treat model output as untrusted input: validate it before writing, and never let it choose which records to touch.

## 16. Environment variables

Two places, and they don't share values:

| Variable | Where | Notes |
|---|---|---|
| `CONVEX_DEPLOYMENT`, `NEXT_PUBLIC_CONVEX_URL` | `.env.local` (written by `npx convex dev`) | In Vercel builds, `npx convex deploy` sets `NEXT_PUBLIC_CONVEX_URL` itself |
| `CONVEX_DEPLOY_KEY` | Vercel only: production key in Production, preview key in Preview | Secret |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY` | `.env.local` and Vercel | Secret key is secret |
| `NEXT_PUBLIC_SITE_URL` | `.env.local` and Vercel | For metadata and the sitemap |
| `CLERK_JWT_ISSUER_DOMAIN`, `CLERK_WEBHOOK_SECRET` | Convex | Different values in dev and prod |
| `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` | Convex | Test values in dev, live in prod |
| `RESEND_API_KEY`, `RESEND_WEBHOOK_SECRET` | Convex | |
| `SITE_URL`, AI provider keys | Convex | |

- Convex variables are per deployment: `npx convex env set NAME value` for dev, add `--prod` for production, or the dashboard (Deployment Settings → Environment Variables). `npx convex env list --prod --names-only` shows what's set without printing values.
- **Typed env:** declare variables in `convex/convex.config.ts` with `defineApp({ env: { STRIPE_SECRET_KEY: v.string(), … } })` and read them as `env.NAME` from `./_generated/server`. Declared variables are checked at deploy time, so a missing secret fails the deploy instead of the first payment. The ESLint rule `no-process-env` steers code to `env`.
- Set project-level default env vars for preview deployments in the Convex dashboard, so Vercel previews get test keys.
- `.env.local` is git-ignored. Commit a `.env.example` with names only.

## 17. Testing

- `npm install -D vitest convex-test @edge-runtime/vm`, and `vitest.config.ts` with `test: { environment: "edge-runtime" }`. Tests live in `convex/` and pass `import.meta.glob("./**/*.ts")` to `convexTest(schema, modules)` (add `/// <reference types="vite/client" />` at the top of test files).
- `t.withIdentity({ name: "Alice", tokenIdentifier: "test|alice" })` gives a signed-in caller; `t.run(async (ctx) => …)` seeds data directly.
- **Required tests per function** that takes an ID: happy path; not signed in is refused; **user B is refused user A's record**; wrong role is refused where roles apply; a free user is refused a paid feature where plans apply.

```ts
test("another user can't rename my checklist", async () => {
  const t = convexTest(schema, modules);
  const asAlice = t.withIdentity({ tokenIdentifier: "test|alice" });
  const asBob = t.withIdentity({ tokenIdentifier: "test|bob" });
  const id = await seedChecklistOwnedBy(t, "test|alice");
  await expect(asBob.mutation(api.checklists.rename, { checklistId: id, title: "Mine now" }))
    .rejects.toThrow("Not found");
});
```

- `convex-test` is a mock backend; it doesn't enforce every production limit. Use the dev deployment and two real browser windows for the rest.
- CI on every push: `npm ci`, `npx tsc --noEmit`, ESLint, `npx vitest run`, `npm run build`.

## 18. Deploying: Vercel + Convex

Vercel builds the Next.js app and, in the same build, deploys the Convex functions, so the two can never drift.

- **Production key:** Convex dashboard → the project's production deployment → Settings → **Generate Production Deploy Key**. In Vercel, add it as `CONVEX_DEPLOY_KEY`, scoped to **Production** only.
- **Build command** (Vercel → Settings → Build and Deployment → Build Command, override): `npx convex deploy --cmd 'npm run build'`. It deploys the Convex functions, schema and indexes, then runs the Next.js build with `NEXT_PUBLIC_CONVEX_URL` pointing at production.
- **Previews:** Convex project Settings → **Generate Preview Deploy Key**, added as `CONVEX_DEPLOY_KEY` scoped to **Preview**. Each branch gets its own preview backend (kept 5 days on Free and Starter, 14 on Pro). Seed it with `--cmd 'npm run build' --preview-run 'seed:init'` if useful.
- `npx convex deploy` type-checks and refuses to push if the schema doesn't match the existing data. Fix the data (or make the field optional) rather than forcing it.
- **Production env vars** are set on the production deployment (`--prod`) before the first deploy that needs them.
- **Plans:** Convex Free & Starter is $0/month plus pay-as-you-go above the included limits (1M function calls, 0.5 GB database, 1 GB egress a month). Convex Professional is $25 per developer per month, adds scheduled daily or weekly backups, log streaming and exception reporting, and raises the limits. Vercel Hobby is non-commercial only; a business app needs Vercel Pro ($20 per developer seat per month). Clerk is free up to 50,000 monthly retained users per app, with Pro at $25/month ($20 billed annually).
- **Backups:** any plan can take a manual backup (Dashboard → Backups → Backup Now; kept 7 days). Periodic backups need Pro. `npx convex export --prod --path <file>.zip` (add `--include-file-storage`) gives an off-site copy.
- **Watching production:** the Convex dashboard's Logs and Health pages, `npx convex logs --prod`, and `npx convex insights --prod` (write conflicts and resource-limit warnings over the last 72 hours).

## 19. Public pages, SEO and analytics

- SEO is for the public pages only: home, pricing, features, legal, and any public share pages. Follow the Next.js metadata conventions (root `metadataBase` and title template, unique title, description and canonical per page, `app/sitemap.ts` and `app/robots.ts`). For a serious marketing site, build it with `blueprint-website`.
- The signed-in app layout sets `robots: { index: false }`; the sitemap lists only public pages; `robots.ts` disallows `/app` (or whatever the app prefix is).
- Public pages stay static: no `preloadQuery`, no `cookies()`, no Clerk calls that force request-time rendering.
- **Analytics:** Vercel Web Analytics (`@vercel/analytics`, cookieless) with a custom event for the magic moment in the core loop and one for a paid conversion. Add a product analytics tool only if the user will actually read funnels; in the UK and EU, cookie-setting tools need consent first.
- **Accessibility:** shadcn/ui gives accessible primitives; keep labels on every field, visible focus, 4.5:1 text contrast, and full keyboard use of the core loop.

## 20. Patterns to avoid

- Public functions without an auth check, or that take `userId`, `role`, `teamId` membership or `plan` from the client as proof of anything.
- Checking that the user is signed in but not that the record is theirs.
- Sensitive functions exported as `query`/`mutation`/`action` when they should be `internal*` (webhook handlers, crons, anything that grants credit or changes plans).
- Missing `args` validators, `v.any()` in public functions, and `v.string()` where `v.id()` belongs.
- `.filter()` instead of an index on tables that grow; unbounded `.collect()`; `.collect().length` to count.
- Unbounded arrays inside documents; fast-changing fields on widely read documents.
- `ctx.db` in actions, `fetch` in mutations, `Date.now()` in queries, and chains of `ctx.runQuery`/`ctx.runMutation` from an action that should be one mutation.
- Importing builders from `convex/server` instead of `./_generated/server`, or editing `convex/_generated`.
- Gating paid features only in the UI, or granting access from the Checkout success URL instead of the webhook.
- Secrets in `NEXT_PUBLIC_` variables, in code, or set only in Vercel when Convex functions read them.
- `middleware.ts` on Next.js 16 (it's `proxy.ts`); synchronous `params`; `'use client'` on whole pages and layouts.
- Indexing the signed-in app in Google, or rendering public marketing pages per request.
- Starting new production apps on Convex Auth while it's in beta; hand-rolled password auth.
- A second hand-written API in Route Handlers duplicating what Convex functions already do.
- Shipping with Clerk development keys, Stripe test keys or Resend `testMode` in production.
- Copying Convex patterns from memory (old `ctx.db.get(id)` without the table name, `crons.daily`, `ctx.storage.getMetadata`) instead of reading the installed guidelines.
