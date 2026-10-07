# Launch guide template — Mobile App

Use this template to write `docs/mobile-app-launch.md`. Tailor it to what was actually built: fill in real names, bundle IDs, product IDs, prices, environment variable names and commands, and delete phases or steps that don't apply (e.g. Android if it's iOS only, notifications if there are none, the closed test if the Play account belongs to an organisation). Put the slow steps first: Apple and Google account approval and Google's 14-day closed test can't be rushed. Keep the legend and the step format.

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

**What you're launching:** <one sentence — what the app does, for whom, on which platforms, and how it makes money (e.g. "Pro" monthly £4.99 / annual £39.99 with a 7-day trial)>
**Estimated total time:** <x hours of work, plus 1–3 days for account approval, 14 days of closed testing on a new personal Play account, and 1–3 days for each review> · **Cost:** Apple Developer Program $99/year · Google Play Console $25 one-off · EAS Free (15 iOS + 15 Android builds a month) or Starter $19/month · Convex free to start, Professional $25 per developer/month when you outgrow it · Clerk free up to 50,000 monthly retained users (Pro $25/month for more social logins, MFA and no Clerk branding) · RevenueCat free up to $2,500 monthly tracked revenue, then 1% · store commission 15% for most small developers · a domain ~£10–15/year (needed for Clerk production and your privacy policy) · Sentry and PostHog free tiers

**Legend**
- 🧑 **You** — needs your accounts, identity, payment or a decision.
- 🤖 **Agent** — paste the prompt into your coding agent.
- 🤝 **Together** — the agent prepares it, you click the final button.

## Start today — the slow steps
- [ ] 🧑 Enrol in the Apple Developer Program — 30 min, then up to a few days · $99/year
  At developer.apple.com/programs/enroll, sign in with the Apple Account you'll keep for the business and enrol as an individual or an organisation (organisations need a D-U-N-S number, which is free but can take a week or more).
  You'll know it worked when: you can sign in to appstoreconnect.apple.com.
- [ ] 🧑 Create your Google Play Console account — 30 min, then up to a few days · $25 one-off
  At play.google.com/console/signup, choose personal or organisation, pay the fee and complete identity verification. For a new personal account, also start collecting the Google account emails of at least 12 testers (ask a few more: if the count drops below 12, the 14-day clock restarts).
  You'll know it worked when: you can create an app in Play Console.

## Phase 0 — Fix blockers (only if the checklist found must-fix items)
- [ ] 🤖 <blocker> — <time>
  > <ready-to-paste prompt>
  You'll know it worked when: <…>

## Phase 1 — Final checks
- [ ] 🤖 Run the checks and the pre-submission audit — 30 min
  > Run `npx expo-doctor`, `npx expo install --check`, `npx tsc --noEmit` and all the tests, and fix anything they report. Then audit the app against the blueprint-mobile-app CHECKLIST.md and list any [must] failures with a fix for each.
  You'll know it worked when: everything passes and there are no [must] failures.
- [ ] 🧑 Use the app once, as a brand-new customer — 30 min
  Delete the app, install a fresh preview build on your phone, and go from first launch to <the magic moment>, then through sign-up and the paywall. Note anything confusing, slow or unfinished.
  You'll know it worked when: you'd be happy for a stranger's first two minutes to look like yours.
- [ ] 🤖 List every production setting — 10 min
  > List every environment variable and secret this app needs in production, split into: EAS (`EXPO_PUBLIC_` values that ship in the app), EAS build-time secrets (e.g. SENTRY_AUTH_TOKEN), and Convex production secrets. Say where each value comes from. Don't print any values.
  You'll know it worked when: you have three short lists of names.

## Phase 2 — Store records
- [ ] 🧑 Create the app in App Store Connect — 15 min
  Apps → + → New App: platform iOS, name `<app name>`, bundle ID `<bundle id>` (register it under Certificates, Identifiers & Profiles first if it isn't listed, with Sign in with Apple and Push Notifications ticked), SKU `<sku>`.
  You'll know it worked when: the app appears in App Store Connect with your bundle ID.
- [ ] 🧑 Sign the Paid Applications Agreement and add tax and banking — 20 min, then up to a day to activate
  App Store Connect → Business: accept the Paid Applications Agreement, add your bank account and complete the tax forms. Apply for the App Store Small Business Program (15% commission instead of 30%) at developer.apple.com/app-store/small-business-program.
  You'll know it worked when: the agreement shows as Active. Purchases won't work, even in sandbox, until it does.
- [ ] 🧑 Create the app in Play Console and set up payments — 20 min
  Create app → name `<app name>`, app or game, free (subscriptions are separate), accept the declarations. Then Settings → Payments profile: set up the merchant account.
  You'll know it worked when: the app's dashboard opens and the payments profile is complete.
- [ ] 🤝 Upload a first Android build by hand — 30 min
  > Run `eas build --profile production --platform android` and give me the download link for the .aab file.
  This build only unlocks Play's subscription setup; the real one comes in Phase 6. In Play Console → Testing → Internal testing → Create new release, upload the .aab (Google requires the first upload to be by hand), add yourself as a tester and roll it out.
  You'll know it worked when: the internal release shows as available and you can install it from the testing link.

## Phase 3 — Subscriptions in the stores
- [ ] 🧑 Create the subscriptions in App Store Connect — 30 min
  Your app → Monetization → Subscriptions: create a group `<group>`, then `<product id monthly>` (1 month, <price>) and `<product id annual>` (1 year, <price>, introductory offer: <trial>). Add a display name, description and review screenshot (a screenshot of your paywall) to each.
  You'll know it worked when: each subscription shows "Ready to Submit".
- [ ] 🧑 Create the subscriptions in Play Console — 30 min
  Monetize with Play → Products → Subscriptions: create `<product id>` with base plans `monthly` (<price>) and `annual` (<price>), plus a free trial offer on the annual plan. Activate each.
  You'll know it worked when: the subscriptions and base plans show as Active.

## Phase 4 — RevenueCat
- [ ] 🧑 Create the RevenueCat project and connect the stores — 45 min · free up to $2,500 monthly tracked revenue
  At app.revenuecat.com, create project `<name>`. Add an App Store app (bundle ID, plus the In-App Purchase Key .p8 from App Store Connect → Users and Access → Integrations, which is required for purchases to be recorded) and a Play Store app (package name, plus a Google Cloud service account JSON key with access granted in Play Console; follow RevenueCat's guide).
  You'll know it worked when: both apps show valid credentials in RevenueCat.
- [ ] 🧑 Set up products, the entitlement and the offering — 20 min
  Import the products from both stores. Create entitlement `pro` and attach every product. Create offering `default` with `$rc_monthly` and `$rc_annual` packages and make it current.
  You'll know it worked when: the offering lists both packages for both platforms.
- [ ] 🤝 Design the paywall — 30 min
  In RevenueCat → Paywalls, build the paywall for the `default` offering from a template, in your brand colours.
  > Check our RevenueCat paywall against App Store guideline 3.1.2 and REFERENCE.md section 7: list exactly what it must show (prices, periods, trial terms, auto-renewal, Restore, Terms of Use and Privacy Policy links) and the Terms and Privacy URLs to use: <urls>.
  You'll know it worked when: the paywall shows every item on that list on both platforms.
- [ ] 🧑 Connect the store notifications — 15 min
  In RevenueCat's App Store app settings, click **Apply in App Store Connect** for Server Notifications (Version 2). In the Play Store app settings, create the Pub/Sub topic, paste its ID into Play Console → Monetize with Play → Monetization setup → Real-time developer notifications, and send a test notification.
  You'll know it worked when: RevenueCat shows the test notification as received.

## Phase 5 — Backend and sign-in in production
- [ ] 🤖 Deploy Convex to production — 15 min · free to start
  > Deploy the Convex functions to production with `npx convex deploy`, then tell me the production URL and which production environment variables still need setting (names only).
  You'll know it worked when: the Convex dashboard shows the production deployment with your functions and tables.
- [ ] 🧑 Create Clerk's production instance — 30 min, plus DNS time
  In the Clerk dashboard, create the production instance for `<domain>`, add the DNS records it lists at your domain provider, and set up Sign in with Apple and Google with your own credentials, following Clerk's Expo guides (they need your Apple Team ID, bundle ID, package name and signing certificate fingerprint). Activate the Convex integration for production.
  You'll know it worked when: Clerk shows the domain verified and both social connections enabled.
- [ ] 🤝 Set the production secrets and webhook — 20 min
  > Give me the exact `npx convex env set --prod` commands to run for CLERK_FRONTEND_API_URL, CLERK_SECRET_KEY, REVENUECAT_SECRET_KEY and REVENUECAT_WEBHOOK_AUTH, with placeholders instead of values, and tell me where each value comes from.
  Run them in your own terminal with the real values. For `REVENUECAT_WEBHOOK_AUTH`, generate a value with `openssl rand -base64 32`. Then in RevenueCat → Integrations → Webhooks, add `https://<deployment>.convex.site/revenuecat` with that value as the Authorization header, and send a test event.
  You'll know it worked when: the test event returns 200 and the Convex logs show it processed.
- [ ] 🤝 Set the EAS production environment — 15 min
  > Give me the `eas env:set` commands for the production environment: EXPO_PUBLIC_CONVEX_URL (prod), EXPO_PUBLIC_CLERK_PUBLISHABLE_KEY (pk_live), EXPO_PUBLIC_REVENUECAT_IOS_KEY, EXPO_PUBLIC_REVENUECAT_ANDROID_KEY and EXPO_PUBLIC_SENTRY_DSN as plain text, and SENTRY_AUTH_TOKEN as a secret, with placeholders.
  Run them with the real values. Never use the RevenueCat Test Store key here.
  You'll know it worked when: `eas env:list --environment production` lists every name.

## Phase 6 — Production builds and testing
- [ ] 🤖 Build and submit both apps — 45 min (mostly waiting)
  > Run `eas build --profile production --platform all --auto-submit`. If EAS asks to create an App Store Connect API key or push key, let it. Report the build numbers when they're uploaded.
  You'll know it worked when: the iOS build appears in TestFlight and the Android build in Play Console's internal testing track.
- [ ] 🧑 Test purchases on real phones — 45 min
  iOS: install from TestFlight, sign in with a sandbox Apple Account (Settings → Developer → Sandbox Apple Account), buy the annual trial, check the paid feature unlocks, cancel, and restore on a second device. Android: add your Google account as a licence tester (Play Console → Settings → License testing), install from the internal track, and repeat.
  You'll know it worked when: every step works and the RevenueCat customer page and the Convex `entitlements` table agree.
- [ ] 🧑 (New personal Play accounts only) Run the closed test — 15 min, then 14 days
  Play Console → Testing → Closed testing: create a track, promote the build, add your 12+ testers' emails and send them the opt-in link. Keep a few spare testers.
  You'll know it worked when: Play Console shows 12 or more opted-in testers and the 14-day counter running. When it ends, apply for production access from the dashboard.

## Phase 7 — Store listings and privacy
- [ ] 🤝 Write the listings — 45 min
  > Write the App Store listing (name ≤30 characters, subtitle ≤30, keywords ≤100 characters, description) and the Play listing (short description ≤80, full description) for <app name> from docs/mobile-app-brief.md. Lead with the magic moment, in the customer's words. Include the Terms of Use link in the App Store description. No claims we can't prove.
  Paste them in, adding the support URL and privacy policy URL.
  You'll know it worked when: both listings are saved without warnings.
- [ ] 🧑 Add screenshots and graphics — 1–2 hours
  App Store: the iPhone size(s) App Store Connect asks for (at last check an iPhone with Dynamic Island, e.g. 1206 × 2622 or 1320 × 2868), plus iPad if supported. Play: a 512 × 512 icon, a 1024 × 500 feature graphic and at least two phone screenshots. Show the magic moment first.
- [ ] 🤝 Fill in the privacy answers — 30 min
  > List every type of data the app and its SDKs collect (Clerk, RevenueCat, Sentry, PostHog, Convex and any others in package.json), whether it's linked to the user, whether it's used for tracking, and why, so I can answer Apple's App Privacy questions and Google's Data safety form. Include the account deletion web link Google needs.
  Answer both forms from that list.
  You'll know it worked when: App Privacy shows as published and the Data safety form is submitted.
- [ ] 🧑 Age rating, content rating and app access — 20 min
  Answer Apple's age rating and Google's content rating, target audience and ads questions. In App Review Information (Apple) and App access (Google), give a demo account and say where the paywall is.

## Phase 8 — Submit for review
- [ ] 🧑 Submit to the App Store — 10 min, then usually 1–3 days
  Select the build, add the subscriptions to this version (the first ones must go with an app version), and Submit for Review. Choose manual release so you decide the launch moment.
  Common rejections: crashes or placeholder content (2.1), no demo account, missing paywall terms or restore (3.1.2), no in-app account deletion (5.1.1(v)), Google sign-in without Sign in with Apple (4.8), vague permission strings, screenshots that don't match the app.
  You'll know it worked when: the status is "Pending Developer Release" (or "Ready for Distribution").
- [ ] 🧑 Submit to Google Play — 10 min, then usually a few days
  Promote the tested build to Production, set a staged rollout (e.g. 20%), and send for review.
  You'll know it worked when: the release shows as approved or available.

## Phase 9 — Release and smoke test
- [ ] 🧑 Release, then smoke test from the stores — 30 min
  Release the App Store version, and increase the Play rollout once the first users show no problems. Then, on a real iPhone and Android phone, on mobile data: install from the store, reach the magic moment, sign up, start the trial (it's a real purchase now: cancel straight after), restore on a second device, and delete the account.
  You'll know it worked when: everything works and the purchase shows as PRODUCTION in RevenueCat.

## After launch
- Ship JavaScript fixes with `eas update --channel production --environment production --message "<what changed>"`, using `--rollout-percentage` for anything risky. Anything native needs a new store build.
- Check Sentry daily for the first week, then weekly. Check RevenueCat Charts weekly: trial starts, trial conversion, churn.
- Reply to store reviews, and feed what people say back into the brief.
- Re-run the checklist before every store submission, and keep old Convex functions working until no supported build calls them.
```
