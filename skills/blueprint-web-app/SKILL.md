---
name: blueprint-web-app
description: Use when the user wants to build, plan, audit, or launch a full-stack web app that people sign in to and use — a SaaS product, internal tool, marketplace, client portal, or dashboard — with Next.js and Convex. Triggers on phrases like "help me build a web app", "build a SaaS", "build an internal tool", "set up Next.js with Convex", "add auth and payments to my app", "add Stripe subscriptions", "is my Convex app secure", "check my app before launch", or "deploy my app". Interviews the user (adapting to their experience), designs the core loop, data model and functions and writes a web app brief, gives the coding agent the best-practice Next.js + Convex reference to build from, audits the app against a pre-launch checklist, and writes a step-by-step launch guide tailored to what was built. For a marketing site, landing page or blog meant to rank on Google, use `blueprint-website` instead.
---

# Blueprint: Web App

This blueprint helps someone build a web app that real people sign in to and use every week: a SaaS product, internal tool, marketplace, client portal or dashboard. It is a Next.js App Router frontend on Vercel with Convex as the database and backend, so data is live in every open tab without extra work. The user brings the idea and steers. The coding agent does the heavy lifting. This skill provides the framework: the right questions up front, the reference to build from, a checklist to audit against, and a launch guide for what was really built.

The voice is a senior full-stack engineer who has shipped products people pay for. Warm and direct, recommends one path rather than a menu, and is ruthless about two things: the core loop (the one thing a user must be able to do end to end) works before anything else gets built, and every public Convex function checks who is calling and whether they may touch *that* record. Convex functions are public endpoints on the internet; the browser is never trusted to say who the user is.

## Files in this skill

All in this skill's folder. Read them when the step that needs them comes up, not before.

- `REFERENCE.md` — default stack, project layout, Convex functions, auth and ownership, data and indexes, server rendering, payments, email, files, testing, deploying, patterns to avoid. Read before building or auditing.
- `CHECKLIST.md` — the pre-launch audit.
- `LAUNCH.md` — the launch guide template.

## Pick the mode

Work out which mode the user needs from what they said and what's in the repo. Don't ask if it's obvious.

| Mode | When | Output |
|---|---|---|
| **1. Plan** | New app, or no `docs/web-app-brief.md` yet | `docs/web-app-brief.md` |
| **2. Build** | A brief exists and the user wants to build or change something | Code, guided by `REFERENCE.md` |
| **3. Check** | "Check / audit / review / secure my app", or before launch | Checklist results in chat, fixes offered |
| **4. Launch** | "Deploy / ship / launch / go live / put it on my domain" | `docs/web-app-launch.md` |

If an app already exists but there's no brief, run a short Plan that reads the code first (`convex/schema.ts`, the functions in `convex/`, the routes in `app/`, the auth setup, env var names) and only asks what the code can't answer.

## Experience level

Before the first real question, ask once: *"How much have you built before — new to this, built a few things, or experienced?"* Then adapt for the whole session:

- **New** — explain every technical term in plain English on first use (e.g. *"mutation (a server function that changes data, like 'create a project'; Convex runs it as one all-or-nothing step)"*). One question at a time. More 🧑 steps spelled out with exactly where to click.
- **Some** — explain only the less common terms. Group simple questions.
- **Experienced** — terse and decisions-first. Lead with the recommended default and let them override it. Skip explanations unless asked.

If the user's answers show a different level than they chose, adjust quietly.

## 1. Plan — the interview

This interview decides the data model, and the data model decides almost everything else. Every table, function and page must trace back to an answer here.

Read the repo first. Anything the code already answers, state back and confirm rather than ask. Ask one question at a time (grouped for experienced users), give one sentence of context on why it matters, and offer a recommended default.

1. **The job and who it's for.** What does the app let someone do, in one sentence, and who is the first user? Push for a concrete sentence (*"lets wedding planners share a live supplier checklist with each couple"*), not a category (*"a project management tool"*). Is it a product for the public, or an internal tool for one company?
2. **The core loop.** What is the one thing a new user must be able to do, start to finish, to get value — the magic moment? (*"Sign up, create a checklist, invite the couple, and watch them tick an item off live."*) Write it as numbered steps. This is built first and smoke-tested last; everything else waits.
3. **The data model.** What are the *things* in this app, in the user's own words (checklists, items, suppliers, couples)? For each: its key fields, what it belongs to, roughly how many there will be per user (ten, or ten thousand?), and how it will be looked up (*"all items in a checklist, newest first"*). Those lookups become indexes. Lists that grow without limit become their own table, never an array inside a document.
4. **Users, auth and roles.** Does each person have their own private data, or do people work together in teams or organisations? Are there roles (owner, member, viewer, admin)? Can someone be invited who doesn't have an account yet? Default: Clerk for sign-in, a `users` table in Convex, and, for teams, `teams` and `memberships` tables in Convex that every function checks. This decides the ownership rule on every function.
5. **Real time and collaboration.** Should other people's changes appear without a refresh? With Convex, every `useQuery` is live by default, so the question is really *what* should be shared live, and whether anything needs presence (*"who's viewing"*) or optimistic updates (instant feedback before the server confirms).
6. **Business model and payments.** Free, subscription (monthly, yearly, per seat?), one-off purchase, or a free trial? What does a paying user get that a free one doesn't? Default: Stripe Checkout through the official Convex Stripe component, with Stripe's Customer Portal for managing billing. For a marketplace that pays sellers, flag Stripe Connect as a separate, bigger job.
7. **Integrations and AI.** Which outside services does it call (an LLM, a CRM, Slack, a maps API)? Which send it webhooks? AI features run in Convex actions, never in the browser, with rate limits per user so one person can't run up the bill.
8. **Files, email and background work.** Will users upload files (images, PDFs, CSVs)? How big, and who may see them? Which emails does the app send (invites, receipts, reminders, digests)? Anything scheduled (a daily digest, trial-ending reminders, cleaning up old data)? Default: Convex file storage, Resend through the Convex Resend component, and Convex scheduled functions and crons.
9. **Design.** Is there a `DESIGN.md`, brand guide, or an app they love the feel of? If there's a `DESIGN.md`, it's the source of truth for tokens. If there's nothing, ask for one reference app and build a clean, calm default with shadcn/ui.
10. **Public pages, domain and hosting.** Which pages must be public and found on Google (home, pricing, legal)? Keep SEO to those; everything behind sign-in is `noindex`. If the marketing site is a big job of its own, suggest building it with `blueprint-website`. Do they own a domain, and where is it registered? Default host: Vercel for Next.js and Convex Cloud for the backend.
11. **Data sensitivity and constraints.** Personal data, payments, health data or data about children? Which countries are users in? A monthly budget ceiling, and any service they already pay for? Personal data in the UK or EU means UK GDPR/GDPR: collect only what's needed, and let people export and delete their data.

### Turn the answers into the design

Read `REFERENCE.md` sections 1, 5, 7 and 8 before designing. Then:

- Turn each thing into a table with its fields (as Convex validators), its owner field (`userId` or `teamId`), and an index for every lookup the answers mention. Name indexes after their fields (`by_teamId_and_createdAt`).
- Turn each action in the core loop and the answers into functions: queries to read, mutations to change, actions to call the outside world, internal functions for anything only the server should run. Give each one a **Who can call** value (Public, Signed in, Team member, Owner, Admin, Internal) and its ownership rule.
- Mark every list as paginated or with a hard limit. Add the webhook HTTP routes (Stripe, Clerk, Resend) and any crons.
- List the pages and routes: public, signed-in, and admin, with what each one reads.

Close the interview by playing back the whole design in one compact block (job, core loop, tables, functions, pages, auth model, payments) and getting a clear yes. Ask specifically: *"Is anything here that you don't need, or missing that you do?"* Cut what isn't needed for the core loop and the first paying user. Then write `docs/web-app-brief.md`:

```markdown
# Web app brief: <name>
> Experience level: <new|some|experienced> · Last updated: <date>

## Job
<one sentence> — for <who> · <public product / internal tool>

## Core loop
1. <step> 2. <step> 3. <step> … · Magic moment: <the instant they get value> · Tracked as: <analytics event>

## Stack
Next.js (App Router) + Convex · Auth: <Clerk> · Payments: <Stripe via @convex-dev/stripe / none> · Email: <Resend via @convex-dev/resend / none> · Host: Vercel + Convex Cloud

## Data model
| Table | Key fields | Belongs to | Indexes | Expected size |
|---|---|---|---|---|

## Functions
| Function | Type | Purpose | Who can call | Ownership rule / notes |
|---|---|---|---|---|
| users.current | query | The signed-in user's profile | Signed in | Own record only |
| http POST /stripe/webhook | HTTP action | Stripe events | Stripe (signed) | Signature verified by the component |

## Pages and routes
| Route | Page | Access | Reads | SEO |
|---|---|---|---|---|
| / | Home | Public | — | Indexed |
| /app | Dashboard | Signed in | <queries> | noindex |

## Auth and roles
<single-user / teams · roles · invitations · the ownership rule in one sentence>

## Payments
<free / subscription / one-off · plans and prices · what's gated · trial — or "None">

## Integrations, AI, files, email and jobs
<outside APIs and webhooks · AI features and their limits · uploads (types, size, who sees them) · emails sent · crons — or "None">

## Design
<DESIGN.md / reference app — and what to take from it>

## Data sensitivity and compliance
<personal data held · regions · export and deletion — or "No personal data beyond sign-in">

## Domain and hosting
Domain: <domain or "to buy"> · Registrar: <…> · Host: Vercel + Convex Cloud

## Decisions and reasons
- <decision> — <why>
```

## 2. Build

Read `REFERENCE.md` before writing any app code. Then let the user steer: build what they ask for, in the order they choose, keeping the brief as the source of truth. If a table, function or decision changes, update the brief first.

If the user has no preference, recommend this order, so the core loop is real early:

1. Project setup: Next.js, Convex, Clerk, shadcn/ui, design tokens, the Convex AI files.
2. `convex/schema.ts`, the `users` table, and the auth helpers every function will use.
3. The core loop end to end, with its tests, including a test that a second user can't read or change the first user's records.
4. The rest of the brief's functions and pages, one feature at a time.
5. Teams, invitations and roles, if the brief has them.
6. Payments, with the plan gate enforced in Convex functions, not just hidden in the UI.
7. Emails, files, background jobs and AI features.
8. Public pages (home, pricing, legal) with proper metadata, `noindex` on the app, then empty, loading and error states, account deletion and data export.

While building:

- Use the project's own docs for API detail. Next.js writes an `AGENTS.md` pointing at the version-matched docs in `node_modules/next/dist/docs/`; `npx convex ai-files install` adds Convex's own guidelines. Read them before using an API you aren't certain of. Both move fast and older patterns in training data are often wrong.
- Keep `npx convex dev` running: it type-checks, pushes every change to the dev deployment and regenerates `convex/_generated`. Write the schema and validators from the brief before the functions.
- For every function that takes an ID, write the forbidden test first: user B tries user A's record and is refused. Then make it pass.
- After each feature: run the tests, use it in the browser as two different users in two windows, and check the Convex dashboard logs for errors.

## 3. Check

Read `CHECKLIST.md` and audit the actual repo against every item. Run the commands the checklist names rather than guessing: the build (`npm run build` and `npx convex dev --once`), the tests (`npx vitest run`), every public `query`, `mutation` and `action` in `convex/` read in full, and the running app in two browser windows signed in as two different users. The auth and ownership items are never "probably fine".

Report in chat:

- A one-line verdict (e.g. *"Ready to launch"*, or *"3 must-fix items before launch"*).
- **Must** failures first, then **should** failures. Each with what's wrong, where (file:line or route), and a fix. Phrase fixes for new users as a ready-to-paste prompt.
- What passed, collapsed to one line.

Offer to fix the must-fix items now. Never mark an item as passing without checking it.

## 4. Launch

Read the actual codebase and brief to establish: the auth provider, payments and webhooks, email, every environment variable (split into Convex variables and Vercel variables), crons, the public pages, and the domain situation. Confirm the picture with the user in one short message, plus anything you genuinely can't tell (e.g. *"Do you already own the domain? Is your Stripe account activated for live payments?"*).

Then read `LAUNCH.md` and write `docs/web-app-launch.md` from it, tailored to this app. Delete the phases and steps that don't apply (e.g. payments if it's free, email domain if it sends no email). Fill in real names, URLs, environment variable names, webhook paths and the real core loop for the smoke test. If the Check found must-fix items, they become Phase 0.

Walk the user in. Don't just drop the file. Summarise in chat: number of steps, the 🧑 steps only they can do, the monthly cost, and the first step. Offer to do the first 🤖 step now.

## Rules

- Recommend one path. Mention an alternative only when the user's situation clearly calls for it.
- Never put secrets in code, examples, commits or chat. Server secrets live in Convex environment variables (and Vercel's, for the few Next.js needs); `.env.local` is git-ignored. Only values that are safe for anyone to see get the `NEXT_PUBLIC_` prefix.
- Never invent Convex, Next.js or Clerk APIs, options or CLI flags. If unsure, read the bundled docs or the official docs linked in `REFERENCE.md`.
- Every public Convex function validates its arguments and works out the user from `ctx.auth`, never from an argument. Every function that takes a record ID checks the caller may access that record. No exceptions, including admin functions.
- Gate paid features in Convex functions, not only in the UI. Hidden buttons are not security.
- Keep every skill self-contained. A skill folder must work if copied on its own. Bundled files are referenced by name relative to the skill's folder.
- The app isn't launched until it's live on its real domain over HTTPS and a brand-new user has completed the core loop in production, including paying if the app takes money.

## What "done" looks like

- `docs/web-app-brief.md` describes the app, and every table, function and route in it exists in the code (and nothing important exists that isn't in it).
- The build and tests pass, including a forbidden-access test for every function that takes a record ID, and every [must] item in `CHECKLIST.md` passes.
- `docs/web-app-launch.md` exists, tailored to this app, and the user knows their first step.

Next step after launch: watch where new users drop out of the core loop, talk to the first ten, and feed what you learn back into the brief. Re-run the Check after every significant change.
