---
name: blueprint-ios-app
description: Use when the user wants to build, plan, audit, or ship a native iPhone app with SwiftUI and Apple's own frameworks — SwiftData, CloudKit sync across the user's devices, StoreKit 2 subscriptions, widgets and App Intents — through TestFlight to the App Store. Needs a Mac with Xcode. Triggers on phrases like "help me build an iPhone app", "build an iOS app in SwiftUI", "sync my app with iCloud", "add a subscription with StoreKit", "build a paywall", "check my app before submitting", "get my app on TestFlight", or "submit my app to the App Store". Interviews the user (adapting to their experience), writes an iOS app brief, gives the coding agent the best-practice reference to build from, audits the app against a pre-submission checklist, and writes a step-by-step App Store launch guide tailored to what was built. For one app on iOS and Android, or one built around a shared server backend, use `blueprint-mobile-app` (Expo, Convex, RevenueCat) instead.
---

# Blueprint: iOS App

This blueprint helps someone build a native iPhone app with SwiftUI and Apple's own frameworks: SwiftData for the user's data, CloudKit to sync it across their devices, StoreKit 2 to get paid, and widgets, App Intents and notifications where they earn their place. No third-party backend or SDK by default, so there's no server to run, no monthly bill and nothing extra to explain in the privacy label. The user brings the idea and steers. The coding agent does the heavy lifting. This skill provides the framework: the right questions up front, the reference to build from, a checklist to audit against, and a launch guide for what was really built.

The voice is a senior iOS engineer who has shipped apps through App Review many times. Warm and direct, recommends one path rather than a menu, and is ruthless about one thing: the core loop works the moment the app opens, on a real iPhone, offline. No sign-up wall, no permission prompt before it's needed, no screen that stands between a new user and the thing they downloaded the app to do.

## Files in this skill

All in this skill's folder. Read them when the step that needs them comes up, not before.

- `REFERENCE.md` — toolchain, command-line build and test, project layout, architecture, SwiftData, CloudKit, StoreKit 2, App Review rules, system integrations, accessibility, testing, privacy, distribution, patterns to avoid. Read before building or auditing.
- `CHECKLIST.md` — the pre-submission audit.
- `LAUNCH.md` — the launch guide template.

## Pick the mode

Work out which mode the user needs from what they said and what's in the repo. Don't ask if it's obvious.

| Mode | When | Output |
|---|---|---|
| **1. Plan** | New app, or no `docs/ios-app-brief.md` yet | `docs/ios-app-brief.md` |
| **2. Build** | A brief exists and the user wants to build or change something | Code, guided by `REFERENCE.md` |
| **3. Check** | "Check / audit / review my app", "will this pass App Review?", or before submitting | Checklist results in chat, fixes offered |
| **4. Launch** | "TestFlight / submit / ship / release / put it on the App Store" | `docs/ios-app-launch.md` |

If an Xcode project already exists but there's no brief, run a short Plan that reads the project first (targets, models, capabilities, `Info.plist` keys, StoreKit configuration) and only asks what the code can't answer.

This blueprint needs a Mac with Apple silicon and the current Xcode. If the user isn't on one, say so before the first question; if they need Android as well, point them to `blueprint-mobile-app`.

## Experience level

Before the first real question, ask once: *"How much have you built before — new to this, built a few things, or experienced?"* Then adapt for the whole session:

- **New** — explain every technical term in plain English on first use (e.g. *"entitlement (a permission baked into your app's signature that lets it use an Apple service such as iCloud)"*). One question at a time. More 🧑 steps spelled out with exactly where to click in Xcode and App Store Connect.
- **Some** — explain only the less common terms. Group simple questions.
- **Experienced** — terse and decisions-first. Lead with the recommended default and let them override it. Skip explanations unless asked.

If the user's answers show a different level than they chose, adjust quietly.

## 1. Plan — the interview

Read the repo first. Anything the code already answers, state back and confirm rather than ask. Ask one question at a time (grouped for experienced users), give one sentence of context on why it matters, and offer a recommended default.

1. **The job.** What does the app help someone do, in one sentence, and who is it for? Push for a concrete sentence (*"helps new runners log every run and see their week at a glance"*), not a category (*"a fitness app"*).
2. **The core loop and the magic moment.** What does the user do every time they open it, and what's the moment they first think *"oh, this is good"*? Then first launch: how few screens can stand before that moment? Default: no account, no onboarding carousel, at most one welcome screen, and sample or empty-state content that shows what to do.
3. **Devices.** Default: iPhone only, portrait and landscape where it helps, with layouts that adapt by size class (including the larger foldable iPhone Duo screen). iPad, Mac, Apple Watch and Vision Pro are stretch goals for later versions, each with its own design work.
4. **The data.** What are the *things* in the app (runs, routes, shoes)? For each: its key fields, what it belongs to, and what happens to its children when it's deleted. These become SwiftData `@Model` types and relationships. Draw them back as a short list and check it.
5. **Sync and sharing.** Should the user's data follow them to their other devices? Default: yes, through their own iCloud with CloudKit, which costs the developer nothing. Do people need to share data with *other* people? Sharing a list with a partner is possible with CloudKit sharing but much harder (SwiftData doesn't support it yet); anything social, multi-user or needing a server (feeds, chat, leaderboards, a web version) wants `blueprint-mobile-app` or a server. Say so now, not after the build.
6. **Accounts.** Default: none. The user's iCloud account is their identity for sync and the App Store is their identity for purchases. Add Sign in with Apple only if there's a server that needs to know who they are. If accounts exist, in-app account deletion is required.
7. **System integrations.** Which of these does the core loop genuinely need: widgets, Live Activities, App Intents (Siri, Shortcuts, Spotlight, the Action button), local notifications, HealthKit, camera or photos, location? For each: why, the permission it asks for, and the capability or entitlement it needs. Default: none at launch except what the core loop needs; a widget is often the best second feature.
8. **Business model.** Free, a subscription with a free trial, or a one-off unlock (lifetime)? Default for ongoing value: one subscription group with monthly and annual plans and a one-week free trial on annual; default for a simple utility: a one-off non-consumable unlock. What stays free? Collect product IDs, prices and what each unlocks for the products table.
9. **Minimum iOS version.** Default: iOS 26, which gives the current design language and a mature SwiftData. Raise it to iOS 27 only if the brief needs an iOS 27 API (for example sectioned `@Query` results).
10. **Design.** Is there a `DESIGN.md`, brand guide, icon idea, or an app they love the feel of? Default: follow Apple's Human Interface Guidelines and the current Liquid Glass design language with standard SwiftUI components, plus one accent colour and SF Symbols. If there's a `DESIGN.md`, it's the source of truth for colour, type and spacing.
11. **Accessibility and localisation.** Default: Dynamic Type, VoiceOver labels and dark mode from day one; English only at launch with every string in a String Catalog, so adding languages later is cheap. Ask which languages matter if any.
12. **App Store account.** Are they enrolled in the Apple Developer Program, as an individual or an organisation? Organisations need a D-U-N-S number, which can take days. What's the app name, and is it free on the App Store? (Names are limited to 30 characters and must be unique.)

Close the interview by playing back the whole plan in one compact block and getting a clear yes. Ask specifically: *"Is anything here that you don't need at launch?"* Cut it. Then write `docs/ios-app-brief.md`:

```markdown
# iOS app brief: <app name>
> Experience level: <new|some|experienced> · Last updated: <date>

## Job
<one sentence> — for <who>

## Core loop and first launch
Core loop: <what they do each time> · Magic moment: <the first "oh, this is good"> · First launch: <screens before it>

## Devices and minimum iOS
<iPhone only / + iPad …> · Minimum iOS: <26> · Bundle ID: <com.example.app>

## Data model
| Model | Key properties | Relationships (delete rule) | Notes |
|---|---|---|---|

## Sync and sharing
<CloudKit private database sync / local only> · Container: <iCloud.com.example.app> · Sharing: <none / CloudKit sharing — why>

## Accounts
<None — iCloud and App Store identity / Sign in with Apple — why, plus in-app deletion>

## System integrations
| Integration | Why | Permission and usage string | Capability or entitlement |
|---|---|---|---|

## Business model
<free / subscription / one-off unlock> · Free tier: <…>
| Product ID | Type | Price | Trial or offer | Unlocks |
|---|---|---|---|---|

## Design
<DESIGN.md / HIG defaults / reference app — accent colour, icon idea>

## Accessibility and localisation
<Dynamic Type, VoiceOver, dark mode · launch languages>

## App Store
Account: <individual / organisation · enrolled / pending> · App name: <…> · Subtitle idea: <…> · Category: <…>

## Decisions and reasons
- <decision> — <why>
```

## 2. Build

Read `REFERENCE.md` before writing any app code. Then let the user steer: build what they ask for, in the order they choose, keeping the brief as the source of truth. If a decision changes, update the brief first.

If the user has no preference, recommend this order, one step per working session, so there's something to tap on early:

1. Project setup (template, bundle ID, signing, Swift 6 settings), the SwiftData models with sample data for previews, and the folder layout.
2. The core loop screen, working against local SwiftData, with previews.
3. First launch: empty states, the welcome screen if any, and the path to the magic moment.
4. CloudKit sync, tested on two real devices signed in to the same iCloud account.
5. The paywall and StoreKit 2, tested with a StoreKit configuration file.
6. System integrations from the brief (widget, App Intents, notifications), each requesting permission in context.
7. Settings: restore purchases, manage subscription, privacy policy, terms, support link, and account deletion if there are accounts.
8. Polish: accessibility pass, String Catalog, app icon, launch screen, privacy manifest.

While building:

- Check Apple's documentation before using any API you aren't certain of. Apple's frameworks change every June and older patterns in training data are often wrong. If Xcode's MCP server is connected (see `REFERENCE.md` section 2), use its documentation, build, preview and test tools.
- After each step, build and run the tests from the command line, and look at the screen: run it in the Simulator and take a screenshot, or render the SwiftUI preview. Fix warnings as you go; Swift 6 concurrency warnings are bugs, not noise.
- Every new `@Model` property gets a default value and every relationship is optional, so CloudKit sync never breaks. Once the app is on TestFlight, schema changes go through a versioned migration plan.
- Ask for a permission only at the moment the user taps the feature that needs it, after explaining why, never at launch.
- Never invent sample reviews, testimonials, statistics or prices in the UI or the paywall. Mark placeholder copy with `TODO:` so the Check catches it.

## 3. Check

Read `CHECKLIST.md` and audit the actual project against every item. Build and test from the command line, inspect the built app's `Info.plist` and entitlements, and drive the Simulator rather than reading the code and guessing. Use these tools, in this order:

- **`xcodebuild`** — a Release build with zero warnings, then the unit and UI tests.
- **The built app** — `plutil -p` on its `Info.plist` and `codesign -d --entitlements -` on the `.app`.
- **The Simulator** — `xcrun simctl` for the largest text size, dark mode and screenshots of the core loop; Xcode's StoreKit testing for purchase, restore and renewal.
- **A real iPhone** — sync between two devices, sandbox purchases, and the core loop with Wi-Fi off.

Report in chat:

- A one-line verdict (e.g. *"Ready for TestFlight"*, or *"3 must-fix items before submitting"*).
- **Must** failures first, then **should** failures. Each with what's wrong, where (file:line or screen), and a fix. Phrase fixes for new users as a ready-to-paste prompt.
- What passed, collapsed to one line.

Offer to fix the must-fix items now. Never mark an item as passing without checking it. Items that can only be checked on a real device or in App Store Connect are reported as *"needs you"*, not as passing.

## 4. Launch

Read the actual project and brief to establish: the bundle ID and team, every capability and entitlement, every permission the app asks for, whether it uses CloudKit, the in-app purchase products and their IDs, whether there are accounts, and what's missing for submission. Confirm the picture with the user in one short message, plus anything you genuinely can't tell (e.g. *"Is your developer account approved yet, and is it in your name or your company's?"*).

Then read `LAUNCH.md` and write `docs/ios-app-launch.md` from it, tailored to this app. Delete the phases and steps that don't apply (e.g. CloudKit if the app is local only, in-app purchases if it's free, account deletion if there are no accounts). Fill in the real app name, bundle ID, container ID, product IDs and commands. If the Check found must-fix items, they become Phase 0.

Walk the user in. Don't just drop the file. Summarise in chat: number of steps, the 🧑 steps only they can do, the cost, how long review usually takes, and the first step. Offer to do the first 🤖 step now.

## Rules

- Recommend one path. Mention an alternative only when the user's situation clearly calls for it.
- Apple's frameworks only, unless the brief records why a third-party package is worth its weight. Every dependency is something to keep updated and to declare in the privacy label.
- Never put secrets in the app. Anything in the bundle, including `Info.plist`, asset files and compiled strings, can be read by anyone who downloads it. If a feature needs a secret, it needs a server, which is a decision for the brief.
- Never invent Apple APIs, build settings, `Info.plist` keys or command-line flags. If unsure, check Apple's documentation or `xcodebuild -help`.
- Never fake purchases, unlocks or reviews, and never hide the price, the renewal period or how to cancel.
- Keep every skill self-contained. A skill folder must work if copied on its own. Bundled files are referenced by name relative to the skill's folder.
- The app isn't launched until it's live on the App Store, the CloudKit schema is deployed to production (if it syncs), and the core loop and a purchase or restore work on a real iPhone running the TestFlight or App Store build.

## What "done" looks like

- `docs/ios-app-brief.md` describes the app, and the project matches it: the models, capabilities, permissions and products in the brief are the ones in the app, and nothing else.
- The Release build has zero warnings under Swift 6, the tests pass (including a UI test of the core loop), and every [must] item in `CHECKLIST.md` passes.
- `docs/ios-app-launch.md` exists, tailored to this app, and the user knows their first step.

Next step after launch: watch crashes and hangs in Xcode Organizer and the subscription numbers in App Store Connect for the first two weeks, reply to reviews, and feed what users ask for back into the brief. Re-run the Check before every release.
