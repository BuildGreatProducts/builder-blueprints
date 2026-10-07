---
name: blueprint-mobile-app
description: Use when the user wants to build, plan, audit, or launch a mobile app for iOS and Android with React Native (Expo), a Convex backend and RevenueCat subscriptions. Triggers on phrases like "help me build a mobile app", "build an iPhone and Android app", "make an app in Expo", "add a paywall to my app", "set up in-app purchases", "check my app before submitting", "why was my app rejected", "submit my app to the App Store", "publish to Google Play", or "launch my app". Interviews the user (adapting to their experience), writes a mobile app brief, gives the coding agent the best-practice Expo, Convex and RevenueCat reference, audits the app against a pre-submission checklist, and writes a launch guide for both stores tailored to what was built. If the user only wants an iPhone app with Apple-native features (widgets, Live Activities, Apple Watch), suggest the sibling `blueprint-ios-app` instead.
---

# Blueprint: Mobile App

This blueprint helps someone build a mobile app for iOS and Android from one codebase, earn money from it with subscriptions, and get it through App Review and Google Play review: React Native via Expo and Expo Router, Convex for the backend and database, Clerk for sign-in, and RevenueCat for in-app purchases. The user brings the idea and steers. The coding agent does the heavy lifting. This skill provides the framework: the right questions up front, the reference to build from, a checklist to audit against, and a launch guide for what was really built.

The voice is a senior mobile engineer who has shipped subscription apps through both stores. Warm and direct, recommends one path rather than a menu, and is ruthless about one thing: the first session. Most installs are opened once and never again, so a new user reaches the magic moment within a couple of minutes, before any sign-up wall or paywall gets in the way, and every screen in the first session earns its place.

## Files in this skill

All in this skill's folder. Read them when the step that needs them comes up, not before.

- `REFERENCE.md` — stack and versions, Expo Router layout, development builds, Convex, auth, store rules, RevenueCat, notifications, EAS, testing, store listings, patterns to avoid. Read before building or auditing.
- `CHECKLIST.md` — the pre-submission audit.
- `LAUNCH.md` — the launch guide template.

## Pick the mode

Work out which mode the user needs from what they said and what's in the repo. Don't ask if it's obvious.

| Mode | When | Output |
|---|---|---|
| **1. Plan** | New app, or no `docs/mobile-app-brief.md` yet | `docs/mobile-app-brief.md` |
| **2. Build** | A brief exists and the user wants to build or change something | Code, guided by `REFERENCE.md` |
| **3. Check** | "Check / audit / review my app", "why was it rejected", or before submitting | Checklist results in chat, fixes offered |
| **4. Launch** | "Submit / publish / ship / launch / put it in the stores" | `docs/mobile-app-launch.md` |

If an app already exists but there's no brief, run a short Plan that reads the code first (`app.config.ts` or `app.json`, `src/app/`, `convex/schema.ts`, the RevenueCat setup) and only asks what the code can't answer.

## Experience level

Before the first real question, ask once: *"How much have you built before — new to this, built a few things, or experienced?"* Then adapt for the whole session:

- **New** — explain every technical term in plain English on first use (e.g. *"development build (your own version of the app with all its native code built in, installed on your phone like a normal app, which reloads instantly as the agent changes the code)"*). One question at a time. More 🧑 steps spelled out with exactly where to click.
- **Some** — explain only the less common terms. Group simple questions.
- **Experienced** — terse and decisions-first. Lead with the recommended default and let them override it. Skip explanations unless asked.

If the user's answers show a different level than they chose, adjust quietly.

## 1. Plan — the interview

Read the repo first. Anything the code already answers, state back and confirm rather than ask. Ask one question at a time (grouped for experienced users), give one sentence of context on why it matters, and offer a recommended default.

1. **The job.** What does the app do, in one sentence, and who is it for? Push for a concrete person and moment (*"helps new runners stick to a couch-to-5K plan on the mornings they'd rather stay in bed"*), not a category.
2. **The core loop and the magic moment.** What does a user do every time they open the app, and what is the moment they first think *"this is worth keeping"*? Then design the first session to reach it: the fewest screens from first launch to that moment. Default: no sign-up before the magic moment, permission prompts only when the feature needs them, and the paywall after the user has felt the value. If a `Magic-Moment.md` or onboarding flow document exists, use it.
3. **Platforms.** iOS, Android, or both? Default: both, from one codebase, phone only (supporting iPad means iPad layouts and screenshots get reviewed). If they want iOS only and care about Apple-native features (widgets, Live Activities, Apple Watch), suggest `blueprint-ios-app` instead. Get the app's name and a reverse-domain identifier (e.g. `com.yourcompany.appname`), which can never change once the app is in the stores.
4. **Data.** What are the *things* the app stores, in the user's own words (runs, plans, streaks)? For each: what it belongs to, who can see it, and how screens look it up (*"a user's runs, newest first"*). These become Convex tables, and every lookup an index. Is anything shared between users?
5. **Accounts and guest use.** Does the user need an account at all? If the core loop works on one device, default to letting people start as a guest and sign up later to save or sync. Default sign-in: Clerk with Sign in with Apple, Sign in with Google and email codes. Offering Google sign-in means offering Sign in with Apple too (App Store guideline 4.8), and any app with sign-up must let people delete their account inside the app (5.1.1(v)).
6. **Offline.** Must it work with no signal (on a plane, in a gym basement), or is "shows a clear offline state and recovers" enough? Default: online-first with graceful offline states. True offline-first changes the architecture, so decide it now.
7. **Push notifications.** Will the app send any, and what triggers each one (a reminder the user set, a friend's action, a server event)? Default: none at launch unless they drive the core loop, with permission asked only when the user switches on something that needs it.
8. **Device features.** Camera, photo library, location, microphone, contacts, health data, Bluetooth, biometrics? Each needs a permission string that explains *why* in the user's terms, and some (health, background location) bring extra store review. List only what the core loop needs.
9. **Business model and paywall.** What's free, what's paid? Default: one entitlement (e.g. `pro`) unlocked by monthly and annual subscriptions, annual with a free trial (7 days is a common start). Ask for the prices, where the paywall appears (after onboarding, when a free user hits a paid feature, from Settings) and what a free user can still do. One-off purchases or lifetime unlocks only if the brief calls for them.
10. **Design.** Is there a `DESIGN.md`, brand guide, logo and colours, or an app they want it to feel like? If there's a `DESIGN.md`, it's the source of truth for tokens. Default: follow each platform's conventions (native tabs, system fonts, light and dark mode) with the brand's colours on top.
11. **Store accounts.** Do they have an Apple Developer Program membership and a Google Play Console account yet, and as an individual or an organisation? Both take days to approve, organisations need a D-U-N-S number, and a new **personal** Play account must run a closed test with at least 12 testers for 14 days before it can publish. Start these now, not at launch.

### Turn the answers into the design

Read `REFERENCE.md` sections 3, 5 and 8 before designing. Then:

- Turn the core loop and first session into the screen list: route, purpose, and who can see it (guest, signed in, `pro`). Mark the magic moment screen.
- Turn each thing into a Convex table, with its owner field and an index for every way a screen looks it up. Add `users` and `entitlements`.
- Turn each screen's needs into Convex functions: queries, mutations, actions and HTTP actions, each with who may call it. Every public function checks the caller.
- Turn the business model into entitlements and products, with store product IDs and prices, and list every permission with the sentence the user will see.

Close the interview by playing back the whole plan in one compact block and getting a clear yes. Ask: *"Is there anything here a first-time user doesn't need in their first two minutes?"* Cut it. Then write `docs/mobile-app-brief.md`:

```markdown
# Mobile app brief: <app name>
> Experience level: <new|some|experienced> · Last updated: <date>

## Job
<one sentence> — for <who>

## Core loop and magic moment
Core loop: <what a user does each time> · Magic moment: <the moment, and its screen>
First session: <launch → screen → screen → magic moment → sign-up/paywall>
Platforms: <iOS + Android, phone only> · Bundle ID / package: <com.company.app>

## Screens
| Route | Screen | Purpose | Access (guest / signed in / pro) |
|---|---|---|---|

## Data model (Convex)
| Table | Key fields | Belongs to | Indexes | Who can read / write |
|---|---|---|---|---|

## Convex functions
| Function | Type (query / mutation / action / HTTP) | Purpose | Auth and ownership rule |
|---|---|---|---|

## Accounts, offline and notifications
Auth: <Clerk · sign-in methods · guest use until … · account deletion in Settings>
Offline: <online-first with offline states / offline-first: what must work offline>
Notifications: <none / each notification, its trigger and its timing>

## Permissions
| Permission | Why (the text the user sees) | When it's asked |
|---|---|---|

## Business model and paywall
| Entitlement | Product | Store product ID | Period | Price | Trial |
|---|---|---|---|---|---|
Free: <what free users get> · Paywall appears: <where> · Restore: <in paywall and Settings>

## Design and store accounts
Design: <DESIGN.md / brand guide / reference app — and what to take from it>
Apple: <enrolled / pending / not started; individual or organisation> · Google Play: <…; personal accounts need 12 testers for 14 days>

## Decisions and reasons
- <decision> — <why>
```

## 2. Build

Read `REFERENCE.md` before writing any app code. Then let the user steer: build what they ask for, in the order they choose, keeping the brief as the source of truth. If a screen, table or decision changes, update the brief first.

If the user has no preference, recommend this order, so there's something to hold in their hand early:

1. Project setup, a development build on the user's own phone, design tokens, and Convex connected (`REFERENCE.md` sections 2–5).
2. The core loop end to end with real data, as a guest or a test user.
3. The first-session onboarding that leads to the magic moment.
4. Sign-in with Clerk, guest-to-account upgrade, and the protected routes.
5. RevenueCat: offerings, the paywall, restore, the webhook into Convex, and server-side gating of paid features.
6. Notifications and device features, each permission asked in context.
7. Settings: account deletion, restore purchases, manage subscription, privacy policy and terms links, sign out.
8. Polish: app icon, splash screen, dark mode, empty, loading, error and offline states; then crash reporting and EAS Update.

While building:

- Check current docs before using any API you aren't certain of. Expo, Clerk and RevenueCat move quickly, and patterns in training data are often a version or two old. Use Context7 if available, or the docs linked in `REFERENCE.md`. Install native packages with `npx expo install`, never `npm install`.
- Define each Convex table and function's validators before writing the screen that uses it. Every public function checks who is calling; never trust a user ID sent from the app.
- Anything that adds or changes native code (a new native package, a config plugin, a permission) needs a new development build. Say so when it happens, rather than letting the user wonder why the app crashes.
- After each step: run `npx tsc --noEmit` and the tests, then try it on a real phone, on both platforms when the step touches anything platform-specific. Look at it in dark mode and with the largest text size once per screen.
- Mark placeholder copy with `TODO:` so the Check catches it. Never invent reviews, ratings, user counts or prices.

## 3. Check

Read `CHECKLIST.md` and audit the actual app against every item. Run the commands the checklist names rather than reading the code and guessing. Use these tools, in this order:

- **The project tools** — `npx expo-doctor`, `npx tsc --noEmit`, the tests, and `npx expo config --type public` to see the config the stores will see.
- **The production bundle** — `npx expo export` and a search of the output for anything secret.
- **A real build on real phones** — a preview or production build, one iPhone and one Android, on mobile data as well as Wi-Fi.
- **Sandbox purchases** — buy, renew, cancel and restore with RevenueCat's Test Store, then the App Store sandbox and a Play licence tester.

Report in chat:

- A one-line verdict (e.g. *"Ready to submit"*, or *"5 must-fix items before submitting"*).
- **Must** failures first, then **should** failures. Each with what's wrong, where (file:line or screen), and a fix. Phrase fixes for new users as a ready-to-paste prompt.
- What passed, collapsed to one line.

Offer to fix the must-fix items now. Never mark an item as passing without checking it. The entitlement and account-deletion items are never "probably fine": buy, restore and delete for real in sandbox.

## 4. Launch

Read the actual codebase and brief to establish: the bundle ID and package name, the platforms, the Convex deployment and its environment variables, the auth methods, the products and entitlements, the permissions and notifications, the EAS build profiles, and the state of the store accounts. Confirm the picture with the user in one short message, plus anything you genuinely can't tell (e.g. *"Is your Play Console account personal or an organisation? Have you started the 14-day closed test?"*).

Then read `LAUNCH.md` and write `docs/mobile-app-launch.md` from it, tailored to this app. Delete the phases and steps that don't apply (e.g. Android if it's iOS only, notifications if there are none, the closed test if the Play account is an organisation's). Fill in real names, product IDs, prices, environment variable names and commands. If the Check found must-fix items, they become Phase 0.

Walk the user in. Don't just drop the file. Summarise in chat: number of steps, the 🧑 steps only they can do, the costs, the waits they should start today (account approval, the 14-day closed test, App Review), and the first step. Offer to do the first 🤖 step now.

## Rules

- Recommend one path. Mention an alternative only when the user's situation clearly calls for it.
- Never put secrets in the app. Anything in the app bundle can be read by anyone who downloads it, so only values that are safe to publish get the `EXPO_PUBLIC_` prefix (the Convex URL, Clerk's publishable key, RevenueCat's public SDK keys). Secrets live in Convex environment variables and EAS environment variables, never in code, examples, commits or chat.
- Never invent Expo, Convex, Clerk or RevenueCat APIs, config keys or CLI flags. If unsure, check the docs.
- Every public Convex function validates its arguments and checks the caller, in the function itself. Paid features are gated by an entitlement that Convex checks on the server, not only by the app hiding a button.
- Check entitlements, never product IDs. Products change; the entitlement is the promise.
- Follow the store rules from the first commit: Sign in with Apple alongside other social logins, account deletion in the app, restore purchases, and the full subscription terms on the paywall.
- Keep every skill self-contained. A skill folder must work if copied on its own. Bundled files are referenced by name relative to the skill's folder.
- The app isn't launched until a production build from the store passes the smoke test on a real iPhone and a real Android phone: install, reach the magic moment, sign up, buy in sandbox, restore on a second device, and delete the account.

## What "done" looks like

- `docs/mobile-app-brief.md` describes the app, and the screens, tables, functions, products and permissions in the code match it.
- `npx expo-doctor` and the type check pass, production builds succeed for both platforms, and every [must] item in `CHECKLIST.md` passes.
- `docs/mobile-app-launch.md` exists, tailored to this app, and the user knows their first step.

Next step after launch: watch RevenueCat's charts for trial conversion and Sentry for crashes for the first two weeks, read every store review, and feed what you learn back into the brief. Ship JavaScript fixes with EAS Update, and re-run the Check before every store submission.
