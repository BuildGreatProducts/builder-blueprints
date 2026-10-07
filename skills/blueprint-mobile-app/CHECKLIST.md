# Mobile App — Checklist

Audit the real app against every item. **[must]** blocks submission. **[should]** is strongly recommended. Each item says how to verify it. Run the command, build it, or try it on a real phone; never assume a pass. Section numbers refer to `REFERENCE.md` in this skill's folder.

## Brief and first session
- [ ] **[must]** Every screen, table, function, product and permission in `docs/mobile-app-brief.md` exists in the code, and nothing significant exists that isn't in the brief. *Verify: list `src/app/`, `convex/schema.ts`, the exported functions in `convex/`, the RevenueCat offerings and the permissions in `npx expo config --type public`, and compare with the brief's tables.*
- [ ] **[must]** A new user reaches the magic moment without being forced to sign up or pay first (unless the brief records why). *Verify: delete the app, install a fresh build, and time first launch to the magic moment on a real phone.*
- [ ] **[should]** Permissions are asked in context, not on first launch, and a denied permission shows a way forward. *Verify: fresh install; deny each permission and follow the screen it shows.*

## Builds and config
- [ ] **[must]** `npx expo-doctor` reports no problems, and native packages match the SDK. *Verify: run `npx expo-doctor` and `npx expo install --check`.*
- [ ] **[must]** The type check and tests pass. *Verify: run `npx tsc --noEmit`, the Jest tests and the Convex tests (`npx vitest run`).*
- [ ] **[must]** Production builds succeed for both platforms. *Verify: `eas build --profile production --platform ios` and `eas build --profile production --platform android` (or `--platform all`) finish without errors.*
- [ ] **[must]** The bundle ID, package name, app name and version are final and match the store records. *Verify: `npx expo config --type public` and compare with App Store Connect and Play Console.*
- [ ] **[must]** EAS Update uses a safe runtime version policy (`fingerprint`, or `appVersion` with a strict rule to bump the version on every native change), and production builds point at the `production` channel. *Verify: read `runtimeVersion` in `npx expo config --type public` and the `channel` in `eas.json`; run `eas fingerprint:compare` after a native change.*
- [ ] **[should]** Unused Android permissions are blocked and the Android manifest asks for nothing the brief doesn't list. *Verify: read `android.permissions` and `android.blockedPermissions`; inspect the merged manifest of a preview build (or `npx expo prebuild` into a scratch copy).*

## Secrets and environment
- [ ] **[must]** No secrets in the app bundle: only safe values (Convex URL, Clerk publishable key, RevenueCat public SDK keys, Sentry DSN) use `EXPO_PUBLIC_`. *Verify: `grep -rn "EXPO_PUBLIC_" src app.config.ts` and review each; run `npx expo export --platform all` and `grep -rE "sk_|secret|rcsk_|whsec_" dist/`.*
- [ ] **[must]** No secrets in the repo or its git history; `.env*.local` is git-ignored and `.env.example` has names only. *Verify: `git grep -nEi "(secret|sk_live|sk_test|api[_-]?key|token)"` and review the hits; read `.gitignore`.*
- [ ] **[must]** Production builds use production values: the prod Convex URL, Clerk's `pk_live_` key and the platform RevenueCat keys, never the Test Store key. *Verify: `eas env:list --environment production`; the RevenueCat SDK crashes a release build that uses a Test Store key, so a production build that launches is a good sign.*
- [ ] **[must]** Server secrets are set on the production Convex deployment (`CLERK_FRONTEND_API_URL`, `CLERK_SECRET_KEY`, `REVENUECAT_SECRET_KEY`, `REVENUECAT_WEBHOOK_AUTH`). *Verify: `npx convex env list --prod --names-only` (names only, so no secret is printed).*

## Convex backend
- [ ] **[must]** Every public query, mutation and action has argument validators. *Verify: read every exported `query`/`mutation`/`action` in `convex/` for `args`.*
- [ ] **[must]** Every public function that isn't deliberately public checks the caller with `ctx.auth.getUserIdentity()` (via `requireUser`), and none takes a user ID from the app to decide whose data to use. *Verify: read every exported function. Never sample.*
- [ ] **[must]** Every function that takes a record ID checks that the record belongs to the caller, with a test where user B is refused user A's record. *Verify: read the handlers; grep the Convex tests for cross-user cases.*
- [ ] **[must]** Scheduled functions and crons call only `internal.*` functions, and every promise is awaited. *Verify: `grep -rn "scheduler\.\|crons\." convex` and check each target is `internal.*`; read each call for a missing `await` (typescript-eslint's `no-floating-promises` rule catches these if the project uses it).*
- [ ] **[should]** Reads use `.withIndex`, not `.filter`, and no list uses an unbounded `.collect()`. *Verify: `grep -rn "\.filter(\|\.collect()" convex` and review each.*
- [ ] **[should]** Public functions are backwards compatible with the oldest build still in use (no removed functions or newly required arguments). *Verify: `git diff <last release tag> -- convex/` and read the changed exports.*

## Auth and accounts
- [ ] **[must]** If any third-party or social login is offered, Sign in with Apple (or an equivalent meeting guideline 4.8) is offered too, on iOS. *Verify: open the sign-in screen on an iPhone.*
- [ ] **[must]** Users can delete their account inside the app, and it removes their Convex data and their Clerk user, signs them out, and tells them how to cancel a store subscription. *Verify: delete a test account on a real build; check the Convex dashboard and Clerk dashboard afterwards.*
- [ ] **[must]** Sessions are stored with `expo-secure-store` (Clerk's `tokenCache`), never AsyncStorage. *Verify: read the `ClerkProvider` setup; `grep -rn "AsyncStorage" src`.*
- [ ] **[should]** Guests can use the core loop and keep their data when they sign up (if the brief allows guest use). *Verify: use the app as a guest, sign up, and check the data is still there.*

## Payments
- [ ] **[must]** Paid features check the entitlement (e.g. `pro`), never a product ID, in the app. *Verify: `grep -rn "entitlements.active\|productIdentifier" src`.*
- [ ] **[must]** Paid features that read or write data are also gated in Convex with `requireEntitlement`. *Verify: read each paid function; call one as a free test user and get an error.*
- [ ] **[must]** Users are identified with `Purchases.logIn(<Convex user ID>)` after sign-in and `logOut()` on sign-out. *Verify: read the auth flow; check the customer's App User ID in the RevenueCat dashboard after a test sign-in.*
- [ ] **[must]** The paywall shows each plan's name, price and period, the price after any trial and when it starts, that it renews automatically until cancelled, a Restore Purchases button, and working Terms of Use and Privacy Policy links. *Verify: open the paywall on both platforms and tap each link.*
- [ ] **[must]** Restore works from the paywall and from Settings. *Verify: buy in sandbox, delete and reinstall (or use a second device), sign in, tap Restore.*
- [ ] **[must]** Purchase, renewal, cancellation, expiry and restore are tested in sandbox on both platforms, and the Convex `entitlements` row follows each one. *Verify: RevenueCat Test Store, then an App Store sandbox account and a Play licence tester; watch the RevenueCat customer page and the Convex table.*
- [ ] **[must]** The RevenueCat webhook rejects requests without the right Authorization header, and processes each event ID once. *Verify: `curl -X POST https://<deployment>.convex.site/revenuecat -d '{}'` returns 401; send a test event twice from the RevenueCat dashboard and check one sync.*
- [ ] **[should]** Users can manage or cancel their subscription from Settings (Customer Center or the store's subscription page). *Verify: tap it on both platforms.*

## Store rules and privacy
- [ ] **[must]** Every permission string says why, in the user's terms, and matches what the feature does. *Verify: read the `infoPlist` and plugin permission options in `npx expo config --type public`; trigger each prompt.*
- [ ] **[must]** A privacy policy is linked inside the app and names every SDK that collects data (Clerk, RevenueCat, Sentry, PostHog…). *Verify: open it from Settings.*
- [ ] **[must]** App Store privacy labels, the iOS privacy manifest and Google's Data safety form match what the code and its SDKs actually collect. *Verify: list the SDKs in `package.json`, read each one's privacy documentation, and compare with the store answers and `ios.privacyManifests`.*
- [ ] **[must]** No placeholder copy, test data, or "beta" wording in the build. *Verify: `grep -rniE "TODO:|lorem|ipsum|example\.com|test@" src`.*

## Polish and resilience
- [ ] **[must]** The app icon and splash screen are final on both platforms (including Android's adaptive and monochrome icon layers). *Verify: install a preview build; look at the home screen, the app switcher and the splash in light and dark mode.*
- [ ] **[must]** Every screen has loading, empty, error and offline states, and nothing crashes or hangs in aeroplane mode. *Verify: use each screen in aeroplane mode and on a throttled connection on a real phone.*
- [ ] **[should]** Dark mode and the largest text size look right on every screen. *Verify: switch the phone to dark mode and the largest text size and walk through the app.*
- [ ] **[should]** Push notifications arrive on both platforms, open the right screen when tapped, and can be switched off in Settings. *Verify: send one with Expo's push notifications tool and one from a Convex function to a preview build.*
- [ ] **[should]** Crashes reach Sentry with readable stack traces from a production build. *Verify: trigger a test error in a preview build and read it in Sentry.*
- [ ] **[should]** The first-session funnel events arrive in analytics. *Verify: go through onboarding on a fresh install and watch the events arrive.*
- [ ] **[should]** An end-to-end flow (fresh install → magic moment → paywall) passes in Maestro. *Verify: `maestro test .maestro/`.*
