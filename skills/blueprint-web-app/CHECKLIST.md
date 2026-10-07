# Web App — Checklist

Audit the real app against every item. **[must]** blocks launch. **[should]** is strongly recommended. Each item says how to verify it. Run the command, read the function or use the app; never assume a pass. Section numbers refer to `REFERENCE.md` in this skill's folder.

## Brief and design
- [ ] **[must]** Every table, function and route in `docs/web-app-brief.md` exists in the code, and every public Convex function in the code is in the brief's function table. *Verify: `grep -rnE "export const \w+ = (query|mutation|action)\(" convex --include=*.ts | grep -v _generated` and compare with the table; `npx convex function-spec` lists what's deployed.*
- [ ] **[must]** Every row of the function table has a "Who can call" value and, if it takes a record ID, an ownership rule. *Verify: read the table.*

## Build and code health
- [ ] **[must]** The production build passes with no type errors. *Verify: run `npm run build` and `npx tsc --noEmit`.*
- [ ] **[must]** The Convex functions type-check and push cleanly. *Verify: run `npx convex dev --once`; for production, `npx convex deploy --dry-run` prints what would be pushed without deploying.*
- [ ] **[must]** The tests pass. *Verify: run `npx vitest run`.*
- [ ] **[should]** ESLint with `@convex-dev/eslint-plugin` (recommended set plus `require-access-control` and `no-collect-in-query`) reports no errors. *Verify: run `npx eslint convex`.*
- [ ] **[should]** No `middleware.ts` (it's `proxy.ts` on Next.js 16), and `'use client'` appears only in interactive components, never at the top of a page or layout. *Verify: `ls`; `grep -rln "use client" app`.*

## Auth and ownership
- [ ] **[must]** Every public `query`, `mutation` and `action` either calls the auth helper (or a custom builder that does) or is deliberately public with a reason in the brief. *Verify: read every one; `grep -rnE "(query|mutation|action)\(\{" convex --include=*.ts | grep -v _generated`. Never sample.*
- [ ] **[must]** Every function that takes a record ID loads the record and checks it belongs to the caller or the caller's team (and the role, where needed) before reading or changing it. *Verify: read every such handler.*
- [ ] **[must]** No function trusts a user ID, role, team membership or plan passed as an argument. *Verify: `grep -rnE "userId: v\.|role: v\.|plan: v\." convex --include=*.ts` and read each use.*
- [ ] **[must]** Webhook handlers, crons and anything that grants access, credit or plans are `internal*` functions, not public ones. *Verify: read `convex/http.ts`, `convex/crons.ts` and what they call.*
- [ ] **[must]** Every function that takes an ID has a test where a second user is refused the first user's record. *Verify: grep the tests for cross-user cases and match them against the function table.*
- [ ] **[must]** `convex/auth.config.ts` points at the right Clerk issuer for each deployment. *Verify: `npx convex env get CLERK_JWT_ISSUER_DOMAIN` and `npx convex env get CLERK_JWT_ISSUER_DOMAIN --prod`.*
- [ ] **[should]** Paid features are gated in Convex functions, not only hidden in the UI. *Verify: call a paid mutation as a free user in a test or from the browser console.*

## Validation and errors
- [ ] **[must]** Every Convex function has `args` validators; IDs use `v.id(...)`; no `v.any()` in public functions. *Verify: `grep -rn "v.any()" convex`; the ESLint rule `require-argument-validators`; read each function.*
- [ ] **[should]** Public functions have `returns` validators and return only fields the caller may see, and free-text inputs have length limits checked in the handler. *Verify: read each public function.*
- [ ] **[should]** User-facing errors use `ConvexError`, and the UI shows them helpfully. *Verify: trigger a validation error in the app.*

## Data and queries
- [ ] **[must]** No `.filter()` on a table that grows; every lookup uses `withIndex` with a matching index in `schema.ts`. *Verify: `grep -rn "\.filter(" convex --include=*.ts | grep -v _generated` and read each hit.*
- [ ] **[must]** No unbounded `.collect()`; lists use `.take(n)` or `.paginate()`. *Verify: `grep -rn "\.collect()" convex --include=*.ts | grep -v _generated` and confirm each range is small by design.*
- [ ] **[should]** No unbounded arrays inside documents; growing lists are their own tables. *Verify: read `convex/schema.ts` for `v.array(v.object(`.*
- [ ] **[should]** No health warnings on the dev or production deployment. *Verify: `npx convex insights` and `npx convex insights --prod`.*

## Secrets and environment
- [ ] **[must]** No secrets in the repo or its history; `.env.local` is git-ignored; only browser-safe values use `NEXT_PUBLIC_`. *Verify: `git grep -nE "(sk_live|sk_test|whsec_|re_[A-Za-z0-9]{8}|secret|api[_-]?key)"` and review the hits; read `.gitignore`.*
- [ ] **[must]** Every variable the Convex code reads is set on the production deployment, and every variable Next.js reads is set in Vercel. *Verify: `npx convex env list --prod --names-only`; Vercel → Settings → Environment Variables; compare with `.env.example`.*
- [ ] **[should]** Required Convex variables are declared in `convex.config.ts` so a missing one fails the deploy. *Verify: read `convex/convex.config.ts`.*

## Payments and webhooks
- [ ] **[must]** Every inbound webhook verifies its signature (the Stripe component and Resend component do this; Clerk via `svix`). *Verify: read `convex/http.ts`; send an unsigned request with `curl -X POST https://<deployment>.convex.site/<path>` and get a 4xx.*
- [ ] **[must]** Access is granted from the webhook-synced subscription, never from the Checkout success URL. *Verify: read the entitlement query and the success page.*
- [ ] **[must]** A full test-mode purchase works end to end: checkout, webhook received, plan unlocked, Customer Portal opens, cancelling removes access at period end. *Verify: run it with a Stripe test card and `stripe listen`.*
- [ ] **[must]** At launch, production uses live Stripe keys and a live webhook endpoint pointing at the production `.convex.site` URL. *Verify: Stripe dashboard (live mode) → Webhooks; `npx convex env list --prod --names-only`.*

## Product
- [ ] **[must]** The core loop works end to end for a brand-new user, in production. *Verify: sign up with a new email on a phone and complete every step in the brief.*
- [ ] **[must]** Two users in two windows see each other's shared changes live, and never see each other's private data. *Verify: do it.*
- [ ] **[must]** Every list and page has a loading state, an empty state with a next step, and an error state. *Verify: use the app with a new account and with the network throttled.*
- [ ] **[must]** No placeholder copy or fake data: no `TODO:`, lorem ipsum, or example.com in rendered pages. *Verify: `grep -rniE "TODO:|lorem|ipsum|example\.com" app components convex`.*
- [ ] **[should]** Lighthouse Accessibility is 90+ on the public pages and the main app screen, the core loop works with the keyboard alone, and the app works at phone width. *Verify: `npx lighthouse <url> --view`; tab through the core loop; try it on a real phone.*

## Privacy and accounts
- [ ] **[must]** A user can delete their account, and their data (including stored files) is deleted or anonymised. *Verify: delete a test account and check the Convex dashboard's Data page.*
- [ ] **[must]** A privacy policy and terms are linked from the footer and the sign-up page, and name the services that process data (Clerk, Convex, Stripe, Resend, analytics). *Verify: read them.*
- [ ] **[should]** A user can export their data on request (a download, or a documented manual process). *Verify: read the brief and the code.*
- [ ] **[should]** Rate limits protect sign-up flows, invitations, emails and AI calls. *Verify: read the functions that send or spend; call one past its limit.*

## Public pages
- [ ] **[must]** The signed-in app is `noindex` and absent from the sitemap; the public pages have unique titles, descriptions and canonicals. *Verify: `curl -s <url>/app | grep robots`; `curl -s <url>/sitemap.xml`; curl each public page's `<head>`.*
- [ ] **[should]** Public pages are prerendered: the `(marketing)` layout exports `ensureStatic = 'navigation'`, and they use no `preloadQuery` or per-request APIs. *Verify: read the layout; `next build` passes and its output marks them static.*

## Operations
- [ ] **[must]** Vercel's build command is `npx convex deploy --cmd 'npm run build'` with `CONVEX_DEPLOY_KEY` scoped to Production (and a preview key to Preview, if used). *Verify: Vercel → Settings → Build and Deployment, and Environment Variables.*
- [ ] **[must]** Production uses Clerk's production instance on the real domain with `pk_live_`/`sk_live_` keys, and Resend has `testMode` off with a verified sending domain. *Verify: Vercel env var prefixes; Clerk dashboard; Resend → Domains.*
- [ ] **[should]** There's a recent production backup, and the user knows how to restore it. *Verify: Convex dashboard → Backups.*
- [ ] **[should]** Analytics records the core-loop event and paid conversions. *Verify: trigger them and check the dashboard.*
