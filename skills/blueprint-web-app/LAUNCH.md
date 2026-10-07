# Launch guide template — Web App

Use this template to write `docs/web-app-launch.md`. Tailor it to what was actually built: fill in real names, URLs, environment variable names, webhook paths and the real core loop, and delete phases or steps that don't apply (e.g. payments if the app is free, email if it sends none, the Clerk webhook if users can't delete their account through Clerk). Keep the legend and the step format.

**Every step has:**
- a checkbox
- a 🧑/🤖/🤝 marker
- a time estimate (and the cost, if any)
- plain-English instructions, with technical terms explained on first use when the user is new
- a ready-to-paste prompt in a quote block for 🤖 steps
- a **You'll know it worked when…** line

---

```markdown
# Launch guide: <app name>

**What you're launching:** <one sentence — what the app does, who it's for, and where it will live (e.g. https://app.example.com on Vercel + Convex)>
**Estimated total time:** <x hours, plus up to 48 hours for DNS to spread> · **Cost:** <Vercel Pro $20/month (Hobby is non-commercial only) · Convex Free & Starter $0 plus usage, or Professional $25/developer/month for scheduled backups · Clerk free up to 50,000 monthly users · Stripe fees per payment, no monthly fee · Resend free up to 3,000 emails/month (100/day), then $20/month · domain ~£10–15/year if not owned>

**Legend**
- 🧑 **You** — needs your accounts, identity, payment or a decision.
- 🤖 **Agent** — paste the prompt into your coding agent.
- 🤝 **Together** — the agent prepares it, you click the final button.

## Phase 0 — Fix blockers (only if the checklist found must-fix items)
- [ ] 🤖 <blocker> — <time>
  > <ready-to-paste prompt>
  You'll know it worked when: <…>

## Phase 1 — Final checks
- [ ] 🤖 Run the build, the tests and the pre-launch checklist — 30 min
  > Run `npm run build`, `npx convex dev --once` and `npx vitest run`, and fix anything that fails. Then audit the app against the blueprint-web-app CHECKLIST.md and list any [must] failures with a fix for each. Read every public Convex function for the auth and ownership items; don't sample.
  You'll know it worked when: everything passes and there are no [must] failures.
- [ ] 🤖 List every production setting — 10 min
  > Read the code and `.env.example` and give me two tables of the environment variables production needs: one for Convex (set with `npx convex env set --prod`) and one for Vercel. For each: name, what it's for, whether it's secret, and where its value comes from. Don't print any values.
  You'll know it worked when: you have two short lists, e.g. Convex: `CLERK_JWT_ISSUER_DOMAIN`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `RESEND_API_KEY`, `SITE_URL`; Vercel: `CONVEX_DEPLOY_KEY`, `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY`, `NEXT_PUBLIC_SITE_URL`.
- [ ] 🧑 Walk the core loop as a new customer — 20 min
  On your phone, sign up with an email you haven't used before and do <the core loop>. Look for placeholder words, confusing empty screens and anything you wouldn't show a customer.
  You'll know it worked when: you'd happily hand your phone to your first customer.

## Phase 2 — Put it on GitHub
- [ ] 🧑 Create the repository — 5 min
  On github.com, choose New repository, name it `<repo>`, set it to Private, and don't add a README.
- [ ] 🤝 Push the code — 5 min
  > Check that `.env.local` is git-ignored and not in the history, then add the GitHub remote <url> and push the main branch.
  You'll know it worked when: your files show on GitHub, including `convex/_generated`, and `.env.local` doesn't.

## Phase 3 — Domain
- [ ] 🧑 Buy the domain (only if you don't own one) — 10 min · ~£10–15/year
  Buy `<domain>` from a registrar such as Cloudflare Registrar or Namecheap. Clerk's production login needs a domain you control, so this comes before the auth steps.
  You'll know it worked when: you can open the domain's DNS settings at your registrar.

## Phase 4 — The production backend (Convex)
- [ ] 🧑 Generate the production deploy key — 5 min
  In the Convex dashboard, open your project, switch the deployment picker to **Production**, then **Settings → Generate Production Deploy Key**. Copy it straight into a note you'll paste into Vercel in Phase 5. It's a secret.
  You'll know it worked when: the key is copied somewhere safe and the dashboard lists it under deploy keys.
- [ ] 🤝 Set the production environment variables — 15 min
  > Give me the exact `npx convex env set --prod NAME` commands for every Convex variable in the Phase 1 table, with SITE_URL as https://<domain>. For now, use the Clerk development issuer and the Stripe test keys; Phases 6 and 7 swap in the live ones. Don't generate or print secret values.
  Run each command in your own terminal and paste the value when it asks. Secrets go only there, never in the repo or in chat. Every variable must be set before the first deploy: Convex refuses to deploy if `auth.config.ts` or `convex.config.ts` needs one that's missing.
  You'll know it worked when: `npx convex env list --prod --names-only` shows them all.
- [ ] 🧑 Set a usage guard rail — 5 min
  > Give me a `npx convex deployment usage-limits set --prod` command for a monthly `functionCalls` warning at about twice what you expect at launch.
  Run it yourself. A `warning` only emails you; it never pauses the app.

## Phase 5 — Deploy on Vercel
- [ ] 🧑 Import the project — 15 min · $20/month on Pro for a business app
  Sign in at vercel.com with GitHub, choose **Add New → Project**, pick `<repo>`. Before deploying: open **Build and Output Settings**, override the Build Command with `npx convex deploy --cmd 'npm run build'`. Under **Environment Variables**, add `CONVEX_DEPLOY_KEY` (from Phase 4) for **Production only**, plus the other Vercel variables from Phase 1 (use your Clerk development keys for now).
  You'll know it worked when: the build log shows Convex deploying your functions, then Next.js building, and the `.vercel.app` link opens your app.
- [ ] 🧑 Connect your domain — 15 min, plus up to 48 hours to spread
  Project → **Settings → Domains → Add** `<domain>` (and accept the `www` redirect), then copy the DNS records Vercel shows into your registrar.
  You'll know it worked when: `https://<domain>` opens the app with a padlock.
- [ ] 🧑 (Optional) Preview backends for branches — 5 min
  Convex project **Settings → Generate Preview Deploy Key**, then add it in Vercel as `CONVEX_DEPLOY_KEY` scoped to **Preview** only. Each branch then gets its own throwaway backend.

## Phase 6 — Sign-in for real users (Clerk production)
- [ ] 🧑 Create the production instance — 30 min, plus DNS time
  In the Clerk Dashboard, use the Development dropdown → **Create production instance**, set the domain to `<domain>`, and add every DNS record from its **Domains** page at your registrar. When they verify, click **Deploy certificates**.
  You'll know it worked when: the Domains page shows every record verified.
- [ ] 🧑 Set up social logins with your own credentials — 20 min per provider
  For each social login (e.g. Google), create OAuth credentials in that provider's console and paste them into Clerk's production instance. Development's shared credentials don't work in production.
- [ ] 🤝 Connect Clerk production to Convex — 15 min
  In Clerk's production instance, activate the **Convex integration** and copy its Frontend API URL (it looks like `https://clerk.<domain>`). Then run `npx convex env set --prod CLERK_JWT_ISSUER_DOMAIN <url>`. In Vercel, replace the Clerk keys with the production ones (`pk_live_…`, `sk_live_…`) and redeploy.
  > Check that convex/auth.config.ts reads CLERK_JWT_ISSUER_DOMAIN and tell me how to confirm, from the browser and the Convex production logs, that a signed-in user is recognised by Convex.
  You'll know it worked when: you can sign up on `https://<domain>` and the app shows your data, not a "Not signed in" error.
- [ ] 🧑 Register the Clerk webhook (if the app syncs users) — 10 min
  Clerk production → **Webhooks → Add Endpoint**: `https://<prod-deployment>.convex.site/clerk-users-webhook`, events `user.updated` and `user.deleted`. Copy the signing secret and run `npx convex env set --prod CLERK_WEBHOOK_SECRET`.
  You'll know it worked when: Clerk's test event shows a 2xx response.

## Phase 7 — Take real payments (Stripe live mode)
- [ ] 🧑 Activate your Stripe account — 20 min
  In the Stripe dashboard, complete business details and bank account so live mode is enabled. Turn on Stripe Tax if you need to charge VAT.
- [ ] 🤝 Create the live products and prices — 15 min
  > List the products and prices the app uses in test mode, and the env vars or config that hold their price IDs, so I can recreate them in live mode.
  Recreate them in live mode, then update the price IDs where the agent says.
- [ ] 🧑 Add the live webhook and keys — 10 min
  Stripe (live mode) → **Developers → Webhooks → Add endpoint**: `https://<prod-deployment>.convex.site/stripe/webhook`, with the events listed in the `@convex-dev/stripe` README. Copy its signing secret, then replace the test values: `npx convex env set --prod STRIPE_WEBHOOK_SECRET` and `npx convex env set --prod STRIPE_SECRET_KEY` (the `sk_live_…` key).
  You'll know it worked when: Stripe's "send test event" shows a 2xx response.
- [ ] 🧑 Configure the Customer Portal — 5 min
  Stripe → **Settings → Billing → Customer portal**: allow cancelling and updating payment methods, and add your terms and privacy links.

## Phase 8 — Email from your domain
- [ ] 🧑 Verify your sending domain in Resend — 15 min, plus DNS time · free up to 3,000 emails/month
  Resend → **Domains → Add Domain** (e.g. `mail.<domain>`), add its DNS records at your registrar, and wait for "Verified". Create a production API key and run `npx convex env set --prod RESEND_API_KEY`.
- [ ] 🤖 Switch off test mode — 10 min
  > Make sure the Resend component is created with testMode: false in production, sends from an address on mail.<domain>, and that the /resend-webhook route is registered. Commit and push.
  Then add the webhook in Resend (`https://<prod-deployment>.convex.site/resend-webhook`, all `email.*` events) and set `RESEND_WEBHOOK_SECRET` with `npx convex env set --prod`.
  You'll know it worked when: an invite or welcome email arrives in a real inbox, not spam, and shows "delivered" in Resend.

## Phase 9 — Analytics, backups and monitoring
- [ ] 🤝 Turn on analytics — 10 min
  In Vercel, open the **Analytics** tab and click Enable.
  > Install @vercel/analytics, add <Analytics /> to the root layout, and track custom events named `<core-loop event>` when <the magic moment> happens and `<paid event>` when a payment succeeds. Commit and push.
  You'll know it worked when: both events appear in the Analytics tab after you trigger them.
- [ ] 🧑 Take the first backup — 5 min
  Convex dashboard (Production) → **Backups → Backup Now**. On Convex Professional, also turn on daily backups there.
  You'll know it worked when: the backup shows as complete.

## Phase 10 — Smoke test as a real customer
- [ ] 🧑 Sign up and do the core loop on your phone — 15 min
  On mobile data, open `https://<domain>`, sign up with a new email, and complete <the core loop>.
  You'll know it worked when: you reach <the magic moment> with no errors, and the event shows in analytics.
- [ ] 🧑 Pay for real — 10 min · refunded afterwards
  Upgrade with your own card, check the paid feature unlocks, open the Customer Portal, then refund yourself in Stripe and cancel.
  You'll know it worked when: the plan unlocked only after the webhook arrived, and cancelling removed access at period end.
- [ ] 🤝 Check two users can't see each other's data — 10 min
  > Give me a short script of steps for two accounts (A and B) in two browsers: A creates <record>, B tries to open A's <record> URL directly, and B tries the same through the browser console with A's record ID.
  You'll know it worked when: B sees "Not found" every time, and any shared data updates live for both.
- [ ] 🧑 Delete the test account — 5 min
  Delete one test account from inside the app and check its data is gone from the Convex dashboard's Data page.

## After launch
- Check the Convex dashboard's Logs and Health pages (or `npx convex logs --prod` and `npx convex insights --prod`) daily for the first week, then weekly.
- Watch where new users drop out of the core loop, and talk to the first ten.
- Export an off-site copy now and then: `npx convex export --prod --include-file-storage --path backup.zip`. Restore a backup into a dev deployment once, so you know it works before you need it.
- Re-run the checklist before every significant release, and add a cross-user test for every new function that takes an ID.
```
