# Mobile App — Reference

> Last verified: 2026-10. Expo, React Native, Clerk and RevenueCat move quickly. Before relying on an API, config key or CLI flag, check the live docs (or Context7): https://docs.expo.dev, https://docs.convex.dev, https://clerk.com/docs/expo, https://www.revenuecat.com/docs, https://developer.apple.com/app-store/review/guidelines/, https://support.google.com/googleplay/android-developer.
>
> Versions at last check: Expo SDK 57 (`expo` 57.0.x, released 30 June 2026; SDK 58 is in beta with React Native 0.88 RC and lands once 0.88 is stable) · React Native 0.86 · React 19.2 · `expo-router` 57 · TypeScript 6.0 (template default) · `convex` 1.46 · `@clerk/expo` 4.8 (supports Expo SDK 54–57) · `react-native-purchases` and `react-native-purchases-ui` 10.11 · `eas-cli` 24.11 · `@sentry/react-native` 8.29 · `posthog-react-native` 4.79 · `jest-expo` 57 · `@testing-library/react-native` 14 · `convex-test` 0.0.60 with `vitest` 5 · `@convex-dev/expo-push-notifications` 0.3.

## Contents
1. Default stack
2. Project setup and the development build
3. Project layout and navigation
4. Protected routes, guests and onboarding
5. Convex: client, schema and functions
6. Auth: Clerk (and the alternative)
7. Store rules that shape the build
8. Payments: RevenueCat
9. Entitlements on the server
10. Testing purchases
11. Push notifications
12. Device features, permissions and privacy
13. Offline and network states
14. App config and EAS Build
15. EAS Update
16. Crash reporting and analytics
17. Testing
18. Store listings
19. Patterns to avoid

---

## 1. Default stack

One default. Change a line only when the brief clearly calls for it.

| Concern | Default | Use instead when… |
|---|---|---|
| App framework | Expo (React Native), TypeScript, the current stable SDK | iOS only with Apple-native features → `blueprint-ios-app` (SwiftUI) |
| Navigation | Expo Router (file-based) | — |
| Dev workflow | A development build (`expo-dev-client`) on a real phone | Expo Go only for a first look; it can't run RevenueCat purchases or native sign-in |
| Backend and database | Convex (queries, mutations, actions, HTTP actions, scheduled functions, file storage) | — |
| Auth | Clerk (`@clerk/expo`) with Convex's first-party Clerk integration | Better Auth via `@convex-dev/better-auth` if the user wants no third-party auth service (section 6) |
| Payments | RevenueCat (`react-native-purchases` + `react-native-purchases-ui`) over Apple and Google in-app purchase | — |
| Notifications | `expo-notifications` + the Expo push service, sent from Convex with `@convex-dev/expo-push-notifications` | — |
| Builds, store submission, updates | EAS Build, EAS Submit, EAS Update | Local builds (`npx expo run:ios`) for debugging native code |
| Crash reporting | Sentry (`@sentry/react-native`) | — |
| Product analytics | PostHog (`posthog-react-native`) for the first-session funnel; RevenueCat Charts for revenue | — |
| Tests | Jest (`jest-expo`) + React Native Testing Library; `convex-test` + Vitest for Convex; Maestro for end-to-end flows | — |

**Why Clerk is the default:** Convex's own auth docs still list Convex Auth as beta (*"it isn't complete and may change in backward-incompatible ways"*) and recommend a third-party provider for the most complete solution, naming Clerk for React Native. Clerk has an Expo-first SDK with native Sign in with Apple and Google, native sign-in screens, and a one-click Convex integration. Re-check this if Convex starts recommending its own auth for Expo.

## 2. Project setup and the development build

```
npx create-expo-app@latest <name> && cd <name>
npx expo install expo-dev-client
npx convex dev                     # creates a dev deployment; name its URL EXPO_PUBLIC_CONVEX_URL in .env.local
npm install -g eas-cli && eas login
eas init && eas build:configure    # creates the EAS project (projectId) and eas.json
eas build --profile development --platform ios      # or android, or all
```

- `create-expo-app` gives the default template: TypeScript, Expo Router with routes in `src/app/`, native tabs, typed routes, and the React Compiler on (`experiments.reactCompiler: true`). Keep the compiler on and don't hand-write `useMemo`/`useCallback` everywhere.
- **The New Architecture is always on** from SDK 55. Every native library you add must support it; check its README first.
- **Use a development build, not Expo Go.** Expo Go only contains Expo's own native modules, now needs a login, and isn't meant for production apps. RevenueCat, Clerk's native sign-in, Sign in with Apple and push notifications need your own native code. (`react-native-purchases` detects Expo Go and switches to a *Preview API Mode* with JavaScript mocks: screens load, but nothing can be bought.)
- Install the development build from the link EAS prints, run `npx expo start`, and the app loads your code from your computer. Rebuild only when native code changes. iPhones need registering first (`eas device:create`) and Developer Mode switched on.
- Always add native packages with `npx expo install <package>` so versions match the SDK. Run `npx expo-doctor` after every install and before every build.
- Upgrading the SDK: one major version at a time, with `npx expo install expo@^<next> --fix`, then read that SDK's changelog. Check your auth and payments SDKs support the new version first (e.g. `@clerk/expo` 4.8 lists Expo `<58` as its supported range).

## 3. Project layout and navigation

```
src/app/                  # Expo Router: every file is a route
├── _layout.tsx           # root: providers (Clerk, Convex), splash, theme, root Stack
├── (onboarding)/         # route group: first-session screens, no URL segment
├── (app)/                # the app itself: _layout.tsx (tabs), index.tsx, settings.tsx
├── sign-in.tsx
└── paywall.tsx           # presented as a modal
src/components/  src/hooks/ (useEntitlement…)  src/lib/ (purchases.ts, analytics.ts)
convex/
├── schema.ts  auth.config.ts  convex.config.ts (components)
├── http.ts               # HTTP actions: RevenueCat webhook
├── model/                # helpers: requireUser, requireEntitlement
└── <feature>.ts          # short public functions that call model/
assets/  .maestro/  app.config.ts  eas.json  .env.local  .env.example
```

- `_layout.tsx` files define navigators: `Stack`, `Tabs` (JavaScript tab bar) or `NativeTabs` (the platform's own tab bar; the SDK 57 template imports it from `expo-router/unstable-native-tabs`, and SDK 58 makes it stable). Route groups `(name)` organise files without changing URLs. Older projects keep routes in `app/` at the root; both work, but don't mix them.
- Present the paywall as a modal so dismissing it returns the user to where they were. Set `scheme` in the app config so deep links and auth redirects work.
- Settings holds account deletion, restore, manage subscription, notification choices, and the privacy policy and terms links.

## 4. Protected routes, guests and onboarding

Use `Stack.Protected` (and `Tabs.Protected`) with a `guard`. When a guard is false, the screen can't be reached and anyone on it is sent to the first available screen. SDK 58 adds a `redirectTo` prop.

```tsx
// src/app/_layout.tsx
import { ClerkProvider, useAuth } from '@clerk/expo'
import { tokenCache } from '@clerk/expo/token-cache'
import { ConvexReactClient, useConvexAuth } from 'convex/react'
import { ConvexProviderWithClerk } from 'convex/react-clerk'
import { Stack } from 'expo-router'

const convex = new ConvexReactClient(process.env.EXPO_PUBLIC_CONVEX_URL!, {
  unsavedChangesWarning: false,
})

export default function RootLayout() {
  return (
    <ClerkProvider publishableKey={process.env.EXPO_PUBLIC_CLERK_PUBLISHABLE_KEY!} tokenCache={tokenCache}>
      <ConvexProviderWithClerk client={convex} useAuth={useAuth}>
        <RootStack />
      </ConvexProviderWithClerk>
    </ClerkProvider>
  )
}

function RootStack() {
  const { isLoading, isAuthenticated } = useConvexAuth()
  const hasOnboarded = useHasOnboarded()          // e.g. a flag kept with expo-secure-store
  if (isLoading) return null                       // keep the splash screen up
  return (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Protected guard={!hasOnboarded}>
        <Stack.Screen name="(onboarding)" />
      </Stack.Protected>
      <Stack.Protected guard={hasOnboarded}>
        <Stack.Screen name="(app)" />
        <Stack.Screen name="paywall" options={{ presentation: 'modal' }} />
      </Stack.Protected>
      <Stack.Protected guard={!isAuthenticated}>
        <Stack.Screen name="sign-in" />
      </Stack.Protected>
    </Stack>
  )
}
```

- Guards are client-side only. They decide what the user sees; Convex decides what they can read and change.
- Use `useConvexAuth()` (not only Clerk's `isSignedIn`) to decide whether to call authenticated queries: it's true only once Convex has the token.
- Keep the splash screen up (`SplashScreen.preventAutoHideAsync()`, then `hideAsync()`) until auth and the first data are loaded, so the app never flashes the wrong screen.
- **Guest use:** if the core loop works before sign-up, let guests use it. Keep guest data on the device (or in Convex under an anonymous ID the app holds) and move it to the account in one mutation when they sign up. Ask for sign-up at a moment of value (*"Save your streak"*), not on the first screen.

## 5. Convex: client, schema and functions

**Client:** one `ConvexReactClient` at module scope (section 4), `useQuery`, `useMutation`, `useAction` and `usePaginatedQuery` from `convex/react`. Queries are live: screens update when data changes, with no refetching code.

**Schema** — every table defined, every lookup indexed:

```ts
// convex/schema.ts
import { defineSchema, defineTable } from 'convex/server'
import { v } from 'convex/values'

export default defineSchema({
  users: defineTable({ tokenIdentifier: v.string(), name: v.optional(v.string()) })
    .index('by_token', ['tokenIdentifier']),
  runs: defineTable({ userId: v.id('users'), distanceMetres: v.number(), startedAt: v.number() })
    .index('by_user_and_started', ['userId', 'startedAt']),
  entitlements: defineTable({
    userId: v.id('users'),
    entitlement: v.string(),            // e.g. 'pro'
    isActive: v.boolean(),
    expiresAt: v.optional(v.number()),
    environment: v.string(),            // 'SANDBOX' | 'PRODUCTION'
  }).index('by_user_and_entitlement', ['userId', 'entitlement']),
  revenuecatEvents: defineTable({ eventId: v.string() }).index('by_event_id', ['eventId']),
})
```

**Functions** — validators on every public function, the caller checked inside it, and only indexed, bounded reads:

```ts
// convex/model/users.ts
import { ConvexError } from 'convex/values'
import type { QueryCtx, MutationCtx } from '../_generated/server'

export async function requireUser(ctx: QueryCtx | MutationCtx) {
  const identity = await ctx.auth.getUserIdentity()
  if (!identity) throw new ConvexError('Not signed in')
  const user = await ctx.db.query('users')
    .withIndex('by_token', (q) => q.eq('tokenIdentifier', identity.tokenIdentifier))
    .unique()
  if (!user) throw new ConvexError('Account not found')
  return user
}

// convex/runs.ts
import { query } from './_generated/server'
import { paginationOptsValidator } from 'convex/server'
import { requireUser } from './model/users'

export const listMine = query({
  args: { paginationOpts: paginationOptsValidator },
  handler: async (ctx, { paginationOpts }) => {
    const user = await requireUser(ctx)
    return await ctx.db.query('runs')
      .withIndex('by_user_and_started', (q) => q.eq('userId', user._id))
      .order('desc')
      .paginate(paginationOpts)
  },
})
```

- **Never accept a user ID from the app** to decide whose data to read or write. Derive it from `ctx.auth.getUserIdentity()`. For a record ID in the arguments, load it and check `doc.userId === user._id` before returning or changing it.
- **Indexes, not `.filter`.** Use `.withIndex()`; `.filter` scans every row. Don't keep both `by_user` and `by_user_and_started`; the longer one covers both.
- **No unbounded `.collect()`.** Use `.paginate()` for lists, `.take(n)` for "latest few", `.first()` / `.unique()` for one.
- **Queries and mutations** are transactional and deterministic: no `fetch`, and no `Date.now()` in queries (they won't re-run when time passes; pass the time in, or store a flag).
- **Actions** (`action`) call outside services (RevenueCat's REST API, an LLM, email). They read and write through `ctx.runQuery` / `ctx.runMutation` with `internal.*` functions; keep each to as few calls as possible, since each is its own transaction. Add `'use node'` at the top of the file only when an npm package needs Node.
- **HTTP actions** (`httpRouter` in `convex/http.ts`) receive webhooks at `https://<deployment>.convex.site/<path>`. **Scheduled functions** (`ctx.scheduler.runAfter`, `runAt`) and **crons** (`convex/crons.ts`) only ever call `internal.*` functions. Await every promise.
- **Old app versions stay in use for months.** Treat public functions as a versioned API: add optional arguments rather than changing or removing them, and keep old functions until no supported build calls them.
- Secrets for Convex code: `npx convex env set NAME value` (add `--prod` for production). Read them with `process.env.NAME` inside functions.

## 6. Auth: Clerk (and the alternative)

**Setup:** `npx expo install @clerk/expo expo-secure-store`, add the `@clerk/expo` config plugin, set `EXPO_PUBLIC_CLERK_PUBLISHABLE_KEY`, and wrap the app as in section 4. `tokenCache` from `@clerk/expo/token-cache` keeps the session in the iOS Keychain and Android Keystore via `expo-secure-store`. Never store tokens in AsyncStorage.

**Convex integration:** in the Clerk dashboard, activate the Convex integration, then:

```ts
// convex/auth.config.ts
import type { AuthConfig } from 'convex/server'
export default {
  providers: [{ domain: process.env.CLERK_FRONTEND_API_URL!, applicationID: 'convex' }],
} satisfies AuthConfig
```

`npx convex env set CLERK_FRONTEND_API_URL <Clerk Frontend API URL>` for each deployment (dev and prod use different Clerk instances).

**Sign-in screens:** default to Clerk's native `<AuthView />` (`@clerk/expo/native`), which handles email codes, Sign in with Apple and Sign in with Google with native UI. It needs a development build and iOS 17 or later. For a fully custom screen, use `useSignInWithApple()` from `@clerk/expo/apple` (with `expo-apple-authentication` and `expo-crypto`) and `useSignInWithGoogle()` from `@clerk/expo/google`, following Clerk's Expo guide for each. Set `ios.usesAppleSignIn: true` in the app config.

**Users in Convex:** after sign-in, call a `users.store` mutation that finds or creates the `users` row by `identity.tokenIdentifier`. Then call `Purchases.logIn(user._id)` (section 8).

**Account deletion** (required, section 7): a Settings button that confirms, then calls a Convex action that deletes the user's Convex data (in batches, via internal mutations and the scheduler if large), deletes the Clerk user through Clerk's Backend API with `CLERK_SECRET_KEY`, and signs out. Tell the user that deleting the account doesn't cancel a store subscription, and link to manage it. If they signed in with Apple, confirm Apple's tokens are revoked as part of deletion (check Clerk's current docs).

**Production:** a Clerk production instance needs a domain you own (it adds DNS records), its own `pk_live_` key, and your own Apple and Google credentials for social sign-in. Register the native apps (bundle ID, Team ID, package name, signing certificate fingerprint) where Clerk's guides say.

**The alternative — no third-party auth service:** Better Auth through its Convex component (`@convex-dev/better-auth` with `@better-auth/expo`). Users then live in your Convex database and there's no per-user bill, but you build and maintain more of the sign-in UI yourself, including native Sign in with Apple. Convex Auth (`@convex-dev/auth`) is still beta; don't start new production apps on it.

## 7. Store rules that shape the build

Read the current wording before review: https://developer.apple.com/app-store/review/guidelines/ and the Google Play policy centre.

- **Sign in with Apple, or an equivalent (Apple 4.8).** An app that uses a third-party or social login (Google, Facebook…) for the primary account must also offer an equivalent login that limits data to name and email, lets the user hide their email, and doesn't track for ads without consent. Sign in with Apple meets this; offer it whenever Google sign-in is offered. Email-only sign-in doesn't trigger the rule.
- **Account deletion in the app (Apple 5.1.1(v)).** *"If your app supports account creation, you must also offer account deletion within the app."* Not just a support email. Google Play also requires in-app deletion plus a web link where people can request deletion, entered in the Data safety form.
- **Don't force sign-in for no reason (Apple 5.1.1(v)).** If the core features don't need an account, let people use them without one.
- **In-app purchase for digital features (Apple 3.1.1, Google Play Payments policy).** Unlocking features or content inside the app must use the store's in-app purchase. In the United States storefront, apps may also link to their own website checkout; elsewhere, don't. Physical goods and real-world services are exempt.
- **Subscriptions (Apple 3.1.2).** At least seven days long, working on all the user's devices, with ongoing value. Before asking anyone to subscribe, the paywall must make clear: the subscription's name, what they get, the length of each period, the price (and the price after any trial or intro offer, and when it starts), that it renews automatically until cancelled, a **Restore Purchases** control, and working links to the **Terms of Use (EULA)** and **Privacy Policy**. The price must be the most prominent number; don't make the trial bigger than the price.
- **Privacy policy (Apple 5.1.1(i)).** Linked in the store metadata and inside the app, saying what's collected, by which third parties (Clerk, RevenueCat, Sentry, PostHog…), how long it's kept, and how to delete it.
- **Build requirements.** App Store uploads must be built with Xcode 26 and the iOS 26 SDK or later (EAS uses current images). Google Play submissions from 31 August 2026 must target Android 16 (API level 36); current Expo SDKs do.

## 8. Payments: RevenueCat

**Concepts:** *products* are the store's subscriptions and purchases (set up in App Store Connect and Play Console); an *entitlement* (e.g. `pro`) is what a product unlocks; an *offering* is the set of packages (monthly, annual) a paywall shows; a *paywall* is designed in the RevenueCat dashboard and drawn natively by `react-native-purchases-ui`.

**Install and configure** with `npx expo install react-native-purchases react-native-purchases-ui`, then:

```ts
// src/lib/purchases.ts
import { Platform } from 'react-native'
import Purchases, { LOG_LEVEL } from 'react-native-purchases'

export function configurePurchases() {
  if (__DEV__) Purchases.setLogLevel(LOG_LEVEL.DEBUG)
  Purchases.configure({ apiKey: Platform.OS === 'ios'
    ? process.env.EXPO_PUBLIC_REVENUECAT_IOS_KEY!
    : process.env.EXPO_PUBLIC_REVENUECAT_ANDROID_KEY! })
}
```

- Configure once, at startup. The keys are RevenueCat's **public** SDK keys, one per platform; they're safe in the bundle. RevenueCat's secret API key never goes in the app.
- **Identify users** with `await Purchases.logIn(user._id)` once the Convex user exists, so purchases follow the account across devices and the webhook can find the user. Call `Purchases.logOut()` when a signed-in user signs out. Never use an email or a fixed string as the App User ID.
- Guests who buy before signing up are anonymous (`$RCAnonymousID:…`); `logIn` later links the purchase to the account. Check the project's restore behaviour setting in RevenueCat so a restore on a new account does what the brief wants.
- **Check entitlements, never product IDs:** `(await Purchases.getCustomerInfo()).entitlements.active['pro'] !== undefined`. Wrap this in a `useEntitlement('pro')` hook that also listens with `Purchases.addCustomerInfoUpdateListener` (and removes the listener on unmount).
- **Paywalls:** `RevenueCatUI.presentPaywallIfNeeded({ requiredEntitlementIdentifier: 'pro' })` when a free user taps a paid feature; `RevenueCatUI.presentPaywall()` after onboarding; or the `<RevenueCatUI.Paywall />` component inside your own screen (with `onPurchaseCompleted`, `onRestoreCompleted`, `onDismiss`). Results are `PAYWALL_RESULT.PURCHASED`, `RESTORED`, `CANCELLED`, `NOT_PRESENTED` or `ERROR`. Check the dashboard template shows every 3.1.2 disclosure and the Terms and Privacy links.
- **Restore** with `Purchases.restorePurchases()` from the paywall and from Settings. Add **Manage subscription** with `RevenueCatUI.presentCustomerCenter()` (or `Purchases.showManageSubscriptions()`).
- After a purchase, call a Convex action that syncs this user's entitlements from RevenueCat (section 9), so the server agrees immediately rather than waiting for the webhook.
- Use offerings and placements (`Purchases.getOfferings()`, `getCurrentOfferingForPlacement`) to change prices and paywalls from the dashboard without a release.

**Store setup** (details in `LAUNCH.md`):
- **Apple:** the Paid Applications Agreement, tax and banking in App Store Connect; a subscription group with monthly and annual subscriptions (each with a review screenshot); an **In-App Purchase Key** (.p8) uploaded to RevenueCat (required for StoreKit 2, or purchases aren't recorded); App Store Server Notifications V2 pointed at RevenueCat (one click, *Apply in App Store Connect*, in the RevenueCat app settings).
- **Google:** a merchant account; subscriptions with base plans and offers in Play Console (you can only create them after uploading a build that contains the billing library); a Google Cloud service account with Play Console access whose JSON key goes into RevenueCat; Real-time Developer Notifications via the Pub/Sub topic RevenueCat creates.
- Commission: 15% for most small developers (Apple's Small Business Program, which you apply for; Google's 15% on subscriptions and on the first $1M a year), 30% otherwise.

## 9. Entitlements on the server

Paid features that touch data are gated in Convex, not only in the app. RevenueCat tells Convex through a webhook; Convex keeps an `entitlements` table.

```ts
// convex/http.ts
import { httpRouter } from 'convex/server'
import { httpAction } from './_generated/server'
import { internal } from './_generated/api'

const http = httpRouter()
http.route({
  path: '/revenuecat',
  method: 'POST',
  handler: httpAction(async (ctx, request) => {
    if (request.headers.get('Authorization') !== process.env.REVENUECAT_WEBHOOK_AUTH) {
      return new Response('Unauthorised', { status: 401 })
    }
    const { event } = await request.json()
    await ctx.runMutation(internal.billing.recordEvent, { eventId: event.id, appUserId: event.app_user_id })
    return new Response(null, { status: 200 })
  }),
})
export default http
```

- In RevenueCat → Integrations → Webhooks, set the URL to `https://<deployment>.convex.site/revenuecat` and the **Authorization header** to a long random value, stored in Convex as `REVENUECAT_WEBHOOK_AUTH`. For extra protection, turn on HMAC webhook signing and verify the `X-RevenueCat-Webhook-Signature` header: HMAC-SHA256 over `<timestamp>.<raw body>` with the signing secret, using Web Crypto, before parsing the JSON, rejecting timestamps older than five minutes.
- `recordEvent` (an internal mutation) skips event IDs it has seen (RevenueCat retries, up to five times) and schedules `internal.billing.syncCustomer`. That action calls RevenueCat's REST API for the customer (`GET /v1/subscribers/{app_user_id}` with the secret key in `REVENUECAT_SECRET_KEY`, as RevenueCat recommends) and writes the current state of each entitlement. Syncing the whole customer is simpler and safer than interpreting each event type.
- Respond 200 quickly; anything else counts as a failure. Resolve `app_user_id` to a user with `ctx.db.normalizeId('users', id)` and ignore anonymous IDs (they'll arrive again after `logIn`).
- Don't drop `SANDBOX` events in production: App Review and TestFlight testers buy in sandbox against your production backend. Store the environment instead.
- A `requireEntitlement(ctx, user, 'pro')` helper reads the table in every paid mutation and query. In mutations, also check `expiresAt` against `Date.now()`.

## 10. Testing purchases

1. **RevenueCat Test Store** — create it in the dashboard and use its Test Store API key in development builds only. Purchases behave like real ones (CustomerInfo, entitlements, webhooks) with no store setup, and subscriptions renew on a fast clock (a weekly one every 5 minutes) up to five times, then cancel. The SDK deliberately crashes a release build configured with a Test Store key: never ship it.
2. **App Store sandbox** — a sandbox Apple Account (App Store Connect → Users and Access → Sandbox) on a development or TestFlight build. Renewals are accelerated. Test buy, renew, cancel (from the device's subscription settings), restore on a second device, and the trial.
3. **Google Play** — add testers as licence testers in Play Console, install from an internal testing track, and test the same cases. Test cards renew on an accelerated schedule.

For each: the paywall shows the right prices, the entitlement unlocks the feature, the Convex `entitlements` row updates, and restore works after reinstalling.

## 11. Push notifications

- `npx expo install expo-notifications expo-device expo-constants`, and add the `expo-notifications` plugin (with an Android notification icon and colour).
- Ask permission when the user switches on something that needs it, after explaining the value on your own screen first. On Android, create a notification channel before asking.
- Get the token with `Notifications.getExpoPushTokenAsync({ projectId })`, where `projectId` comes from `Constants.expoConfig?.extra?.eas?.projectId ?? Constants.easConfig?.projectId`. Send it to a Convex mutation that records it for the signed-in user.
- Send from Convex with the `@convex-dev/expo-push-notifications` component (`app.use(pushNotifications)` in `convex/convex.config.ts`): `recordToken`, `sendPushNotification`, and pause and resume per user. It batches calls to Expo's push service and retries. Trigger sends from mutations, scheduled functions or crons.
- Credentials: EAS creates the Apple push key when you build (or via `eas credentials`); Android needs Firebase Cloud Messaging V1 credentials uploaded to EAS. Test with a real device and Expo's push notifications tool.
- Remove a user's tokens on sign-out and account deletion. Let users choose which notifications they get in Settings.

## 12. Device features, permissions and privacy

- Use the Expo package for each feature (`expo-camera`, `expo-image-picker`, `expo-location`, `expo-audio`, `expo-contacts`, `expo-local-authentication`…) and set its permission text through its config plugin options or `ios.infoPlist` (e.g. `NSCameraUsageDescription`). Write the reason in the user's terms: *"Take a photo of your meal to log it"*, not *"This app needs camera access"*. Vague strings are a common rejection.
- Ask for each permission just before the feature that needs it, and handle *denied* with a screen that explains and links to Settings (`Linking.openSettings()`).
- Android: remove permissions you don't use with `android.blockedPermissions` (libraries sometimes add them), and declare only what you need in `android.permissions`.
- **Privacy manifests (iOS):** Expo packages ship their own `PrivacyInfo.xcprivacy`. Add any extra required-reason API declarations under `ios.privacyManifests` in the app config, and check each third-party SDK's documentation.
- Health data, background location, contacts and tracking bring extra review on both stores; keep them out unless the core loop needs them. Use App Tracking Transparency (`expo-tracking-transparency`) only if you track users across other companies' apps or sites (usually ads); first-party analytics don't need it, but still go on the privacy labels.

## 13. Offline and network states

- Convex keeps a live connection and retries; while disconnected, queries show their last value and mutations wait to be sent. It doesn't keep data or queued mutations across an app restart, so a closed app starts empty until it reconnects.
- Every screen needs four states: loading (`useQuery` returns `undefined`), empty, error, and offline. Show connection state with `useConvexConnectionState()` from `convex/react`, or `expo-network`.
- Use optimistic updates (`useMutation(...).withOptimisticUpdate(...)`) for actions the user repeats often, so the app feels instant on slow networks.
- If the brief says offline-first, decide the approach before building (e.g. writing locally with `expo-sqlite` and syncing through idempotent mutations), and check Convex's current docs for any official offline or local-first support first.
- Test on a slow network and in aeroplane mode, on a real phone.

## 14. App config and EAS Build

Use `app.config.ts` so values can come from the environment. One build per variant, installable side by side:

```ts
// app.config.ts
import type { ExpoConfig } from 'expo/config'
const IS_DEV = process.env.APP_VARIANT === 'development'

export default (): ExpoConfig => ({
  name: IS_DEV ? 'Stride (Dev)' : 'Stride',
  slug: 'stride', scheme: 'stride', version: '1.0.0', orientation: 'portrait',
  userInterfaceStyle: 'automatic',             // light and dark mode
  runtimeVersion: { policy: 'fingerprint' },
  ios: {
    bundleIdentifier: IS_DEV ? 'com.example.stride.dev' : 'com.example.stride',
    supportsTablet: false,
    usesAppleSignIn: true,
    config: { usesNonExemptEncryption: false },  // skips the export compliance question for standard HTTPS
  },
  android: { package: IS_DEV ? 'com.example.stride.dev' : 'com.example.stride', blockedPermissions: [] },
  plugins: ['expo-router', '@clerk/expo', 'expo-apple-authentication', 'expo-notifications', '@sentry/react-native/expo'],
  experiments: { typedRoutes: true, reactCompiler: true },
  extra: { eas: { projectId: '<from eas init>' } },
})
```

```json
// eas.json
{
  "cli": { "version": ">= 24.0.0", "appVersionSource": "remote" },
  "build": {
    "development": {
      "developmentClient": true, "distribution": "internal",
      "environment": "development", "env": { "APP_VARIANT": "development" }
    },
    "preview": { "distribution": "internal", "environment": "preview", "channel": "preview" },
    "production": { "autoIncrement": true, "environment": "production", "channel": "production" }
  },
  "submit": { "production": {} }
}
```

- **Bundle ID and package name are permanent** once the app is in a store. `npx expo config --type public` prints the config the app will ship with; check names, IDs, permissions and plugins there.
- **Environment variables:** `EXPO_PUBLIC_` values are inlined into the JavaScript bundle and readable by anyone. Store per-environment values in EAS (`eas env:set`, `eas env:list`, `eas env:pull --environment development` for local `.env.local`), with each build profile's `environment` choosing the set. EAS *secret* visibility protects values used during the build (e.g. `SENTRY_AUTH_TOKEN`), not values you put in the app. Server secrets (`REVENUECAT_SECRET_KEY`, `CLERK_SECRET_KEY`, `REVENUECAT_WEBHOOK_AUTH`) belong in Convex, not EAS.
- **Build and submit:** `eas build --profile production --platform all`, then `eas submit --platform ios` and `eas submit --platform android` (or `--auto-submit` on the build). EAS manages signing credentials; let it. Google requires the very first Android upload to be done by hand in Play Console. `eas submit` needs an App Store Connect API key (EAS can create it) and a Google service account JSON key.
- `appVersionSource: "remote"` with `autoIncrement` lets EAS manage build numbers; you change `version` for each store release.

## 15. EAS Update

- `npx expo install expo-updates`, then `eas update:configure`. Builds pick up updates from their channel (`production`, `preview`).
- Publish: `eas update --channel production --environment production --message "Fix streak count"`. Roll out gradually with `--rollout-percentage`, and roll back by republishing the previous update.
- **Runtime version policy `fingerprint`** (the Expo docs' safest option): the runtime version changes whenever anything native changes, so an update can never reach a build it would crash. Check with `eas fingerprint:compare`.
- **What can't ship over the air:** native packages and their versions, config plugins, permissions and their text, the app icon, splash screen, name, bundle ID, entitlements, and SDK upgrades. Those need a new store build.
- Store rules allow updates that fix bugs and improve the app, not ones that change its main purpose or add features that would need review.

## 16. Crash reporting and analytics

- **Sentry:** run `npx @sentry/wizard@latest -i reactNative`. It installs `@sentry/react-native`, adds the `@sentry/react-native/expo` plugin and `getSentryExpoConfig` in `metro.config.js`, and sets up source map uploads. Call `Sentry.init({ dsn })` in the root layout and export `Sentry.wrap(RootLayout)`. Store `SENTRY_AUTH_TOKEN` as an EAS secret. Upload source maps for EAS Update too (`eas update` has `--upload-source-maps`; follow Sentry's Expo guide). Tag events with the signed-in user's Convex ID, never their email.
- **Product analytics:** PostHog (`posthog-react-native`) to measure the first-session funnel: app opened → onboarding step → magic moment → sign-up → paywall viewed → trial started. Name events in the brief. Use RevenueCat Charts for trials, conversion, churn and revenue rather than rebuilding them.
- Declare every SDK's data collection on the App Store privacy labels and Google's Data safety form.

## 17. Testing

- **Components and hooks:** Jest with the `jest-expo` preset and React Native Testing Library (`npx expo install jest-expo jest @testing-library/react-native -- --save-dev`). Mock `react-native-purchases` and Convex hooks at the edge.
- **Convex functions:** `convex-test` with Vitest (and `@edge-runtime/vm`), against the real schema. For every function that takes a record ID, test that user B gets an error for user A's record. Test the webhook with a missing or wrong Authorization header (401), a repeated event ID (processed once), and that `requireEntitlement` refuses an expired entitlement.
- **End to end:** Maestro flows in `.maestro/` (install the CLI from maestro.dev), run with `maestro test .maestro/` against a simulator build, or in EAS Workflows with a `maestro` job. At minimum: first launch → onboarding → magic moment, and free user → paid feature → paywall shown.
- CI on every push: `npx tsc --noEmit`, `npx expo-doctor`, the Jest and Convex tests.
- Before each store submission: the full sandbox purchase matrix (section 10) on both platforms.

## 18. Store listings

**App Store Connect**
- Screenshots: at least one per required size; App Store Connect lists the current sizes (the largest iPhone size, 6.9-inch, accepts e.g. 1320 × 2868 portrait). iPad screenshots too if `supportsTablet` is true. Up to 10 per size; show the magic moment first.
- Name (30 characters), subtitle, keywords, description, support URL, privacy policy URL, and a Terms of Use link (in the description or as a custom EULA) for subscription apps.
- **App Privacy** (the "nutrition labels"): every data type the app and its SDKs collect, whether it's linked to the user, and whether it's used for tracking.
- Age rating questionnaire, category, and App Review notes with a working demo account (or explain guest use) and how to reach the paywall.
- Each subscription needs a display name, description and review screenshot. The first subscriptions must be submitted together with an app version.

**Google Play Console**
- App icon 512 × 512 PNG, feature graphic 1024 × 500, at least two phone screenshots (four or more at 1080 px recommended).
- Data safety form (including the account deletion web link), content rating questionnaire, target audience, ads declaration, and app access instructions with a demo login.
- **New personal developer accounts** (created after 13 November 2023) must run a closed test with at least 12 testers opted in for the last 14 days in a row before production access is granted. Organisation accounts are exempt. Start this as soon as there's a usable build.

## 19. Patterns to avoid

- A sign-up wall or paywall before the user has felt any value; asking for every permission on first launch.
- Secrets in the app: RevenueCat's secret key, Clerk's secret key, webhook secrets or any API key in an `EXPO_PUBLIC_` variable or in code. Treat the bundle as public.
- Trusting the app: user IDs passed as arguments, Convex functions without auth checks, paid features gated only by hiding a button.
- Checking product IDs instead of entitlements; forgetting restore; calling `Purchases.configure` more than once; using an email as the App User ID.
- A paywall missing the price, period, auto-renewal terms, restore, or Terms and Privacy links. Google sign-in without Sign in with Apple; account deletion by email only.
- `.filter` instead of indexes, unbounded `.collect()`, `fetch` in queries or mutations, scheduling `api.*` instead of `internal.*` functions, unawaited promises.
- Breaking or removing Convex functions that older app versions still call. Dropping RevenueCat `SANDBOX` events in production (App Review purchases fail to unlock).
- Shipping native changes over the air, or an `appVersion` runtime policy that lets an update reach an incompatible build.
- Vague permission strings, unused permissions left in the Android manifest, privacy labels that don't match the SDKs.
- Changing the bundle ID or package name after release; installing native packages with `npm install` instead of `npx expo install`.
- Leaving the 14-day Play closed test, Apple enrolment or the Paid Applications Agreement until launch week.
- Copying Expo, Clerk or RevenueCat APIs from memory instead of checking the current docs.
