# iOS App — Reference

> **Staying current.** Use the current release of Xcode from the Mac App Store or developer.apple.com, not a beta, and check what's installed with `xcodebuild -version` and `xcrun --show-sdk-version --sdk iphoneos`. Apple's frameworks change every June at WWDC and Xcode every few months, so before relying on an API, build setting, `Info.plist` key or command-line flag, read the documentation for the installed SDK: Xcode's documentation window, https://developer.apple.com/documentation, Xcode's built-in agent tools (section 2), Context7, or `xcodebuild -help`. For design: https://developer.apple.com/design/human-interface-guidelines. For review: https://developer.apple.com/app-store/review/guidelines. When this reference and Apple's current docs disagree, the docs win.

## Contents
1. Default stack
2. Toolchain and the agent loop
3. Creating the project
4. Project layout
5. Architecture: SwiftUI, Observation, navigation, concurrency
6. SwiftData
7. CloudKit sync
8. StoreKit 2 and the paywall
9. App Review rules that catch people out
10. Accounts and Sign in with Apple
11. System integrations and permissions
12. Design: HIG, system design language, icon and launch screen
13. Accessibility and localisation
14. Testing
15. Performance
16. Privacy
17. Crashes and metrics
18. Distribution: signing, upload, TestFlight, review
19. Patterns to avoid

---

## 1. Default stack

One default. Change a line only when the brief clearly calls for it.

| Concern | Default | Use instead when… |
|---|---|---|
| IDE and SDK | The current release of Xcode and its iOS SDK, on an Apple silicon Mac | — |
| Language | The latest Swift language mode with strict concurrency, Main Actor default isolation | — |
| UI | SwiftUI with the `App` lifecycle; minimum deployment is the current major iOS release | UIKit only through `UIViewRepresentable` for a gap SwiftUI can't fill. Go back one major iOS version only if the brief's audience needs it. |
| State | Observation (`@Observable`) | — |
| Storage | SwiftData | Core Data only for an existing Core Data app, or when CloudKit sharing is core (section 7). |
| Sync | SwiftData's built-in CloudKit sync (private database) | `CKSyncEngine` for custom sync or sharing. A server and `blueprint-mobile-app` for multi-user or social features. |
| Purchases | StoreKit 2 with the StoreKit SwiftUI views | RevenueCat only if the app also ships on Android (`blueprint-mobile-app`). |
| Identity | None (iCloud and App Store identity) | Sign in with Apple when a server needs to know who the user is. |
| Tests | Swift Testing for logic, XCTest UI tests for the core loop | — |
| Crashes and performance | Xcode Organizer + MetricKit | — |
| CI | None at first; Xcode Cloud when releasing often (25 compute hours/month included in the membership) | — |
| Distribution | TestFlight, then the App Store | — |

## 2. Toolchain and the agent loop

- **Xcode:** use the current release, not a beta. It needs an Apple silicon Mac and a recent macOS; check the minimum macOS on developer.apple.com before updating either. Install it from the Mac App Store or developer.apple.com/download, open it once (or run `xcodebuild -runFirstLaunch`), and add the iOS simulator runtime (`xcodebuild -downloadPlatform iOS`). `xcode-select -p` shows which Xcode the command line uses; `xcodebuild -version` and `xcrun --show-sdk-version --sdk iphoneos` show its version and SDK.
- **Build, test and run from the command line** so the coding agent can close its own loop. Use `-derivedDataPath build` so the built app is in a known place, and `-quiet` to keep output short:

```
xcodebuild -list                                          # schemes and targets
xcrun simctl list devices available                       # simulator names to use below
xcodebuild -scheme <Scheme> -destination 'platform=iOS Simulator,name=<iPhone model>' -derivedDataPath build -quiet build
xcodebuild -scheme <Scheme> -destination 'platform=iOS Simulator,name=<iPhone model>' -derivedDataPath build test
xcodebuild ... test -only-testing:<App>UITests            # just the UI tests
xcrun simctl boot '<iPhone model>' && open -a Simulator
xcrun simctl install booted build/Build/Products/Debug-iphonesimulator/<App>.app
xcrun simctl launch booted <bundle id>
xcrun simctl io booted screenshot screen.png               # look at what you built
xcrun simctl ui booted appearance dark                    # or light
xcrun simctl ui booted content_size accessibility-extra-extra-extra-large
xcrun simctl status_bar booted override --time 9:41       # clean screenshots
```

- **Xcode's MCP server.** Xcode exposes its tools to external agents through `xcrun mcpbridge`. Turn it on in **Xcode → Settings → Intelligence → Model Context Protocol → Allow external agents to use Xcode tools** (confirm the menu path in the installed Xcode), then, for Claude Code, run `claude mcp add --transport stdio xcode -- xcrun mcpbridge`. Keep the project open in Xcode. The tools build, run tests, render SwiftUI previews and search the docs; recent releases also let agents boot simulators, launch the app, tap and take screenshots, read build settings and entitlements, read crash insights and edit String Catalogs. The tool set grows with each release, so list what the server offers rather than assuming. If Apple's docs describe running the server without an open workspace (`xcrun mcp-server`) as a preview, don't rely on it.
- Without the MCP server, `xcodebuild` and `simctl` are enough. Both paths work; use whichever is connected.

## 3. Creating the project

In Xcode: **File → New → Project → iOS → App**. Interface **SwiftUI**, language **Swift**, testing system **Swift Testing** (with XCTest UI tests), storage **SwiftData** if offered (or none, and add the models yourself). Then, on the app target:

- **Bundle identifier** — reverse-DNS on a domain you own (`com.example.runlog`). It can't change after the app is on the App Store.
- **Signing & Capabilities** — your team, **Automatically manage signing** on.
- **General → Minimum Deployments** — the brief's minimum iOS (by default the current major release). **Supported Destinations** — iPhone only; remove iPad, Mac and Vision unless the brief includes them.
- **Build Settings** — check **Default Actor Isolation = MainActor**, **Approachable Concurrency = Yes** and **Swift Language Version**. The app template has lagged behind on the language version, so check the project's Swift Language Version build setting and set it to the latest, so data-race checking is complete.
- **Capabilities** (Signing & Capabilities → + Capability), only those the brief needs: **iCloud** with CloudKit and a container `iCloud.<bundle id>` (Xcode adds Push Notifications with it), **Background Modes → Remote notifications** (for CloudKit sync), **App Groups** (`group.<bundle id>`, to share the store with widgets), **In-App Purchase**, **Sign in with Apple**, **HealthKit**.

New projects use folders that stay in sync with the disk, so new Swift files in a target's folder are picked up without editing the project file.

## 4. Project layout

```
RunLog/
├── RunLog.xcodeproj
├── RunLog/
│   ├── RunLogApp.swift          # @main: model container, Store, root view
│   ├── Features/
│   │   ├── Runs/                # RunsList.swift, RunDetail.swift, LogRunSheet.swift
│   │   ├── Onboarding/
│   │   ├── Paywall/
│   │   └── Settings/
│   ├── Models/                  # @Model types, SchemaV1.swift, MigrationPlan.swift
│   ├── Services/                # Store.swift (StoreKit), Notifications.swift
│   ├── Shared/                  # small reusable views, formatters
│   ├── Preview Content/         # SampleData.swift (in-memory container for previews)
│   ├── Resources/
│   │   ├── Assets.xcassets      # accent colour, images
│   │   ├── Localizable.xcstrings
│   │   └── AppIcon.icon         # from Icon Composer
│   ├── PrivacyInfo.xcprivacy
│   ├── RunLog.entitlements
│   └── Products.storekit        # StoreKit configuration for local testing
├── RunLogWidgets/               # widget extension, if the brief has one
├── RunLogTests/                 # Swift Testing
└── RunLogUITests/               # XCTest UI tests
```

- Group by feature, not by type. A feature folder holds its views and any logic only it uses.
- One place for product IDs, the CloudKit container ID and URLs (privacy policy, terms, support), e.g. `Shared/AppConfig.swift`.

## 5. Architecture: SwiftUI, Observation, navigation, concurrency

- **Views are small structs.** Keep state as close as possible to where it's used. No view model per screen by default; SwiftUI views plus `@Query` are the view model for most screens.
- **Property wrappers:** `@State` for view-local values and to own an `@Observable` object; `.environment(store)` and `@Environment(Store.self)` to share one; `@Bindable` to bind controls to an observable's properties; `@Query` to read SwiftData; `@Environment(\.modelContext)` to write.
- **Add an `@Observable` class** when logic is shared across screens, talks to a framework (StoreKit, notifications, HealthKit), or needs testing on its own.
- **Navigation:** `NavigationStack(path:)` bound to an array of a `Hashable` route enum, with `.navigationDestination(for:)`. `TabView` with `Tab` for top-level sections. Sheets with `.sheet(item:)`.
- **Concurrency (strict checking):** with Main Actor default isolation, app code runs on the main actor unless marked otherwise, which is right for UI. Move heavy work off it with an `actor`, a `@concurrent` function or a `@ModelActor` for background SwiftData imports. Use `.task { }` for async work tied to a view; it's cancelled when the view goes away. Treat every concurrency warning as a bug.
- **SwiftData across actors:** `ModelContext` and model objects aren't `Sendable`. Pass a `PersistentIdentifier` and fetch it again on the other side.
- **Errors:** handle them where the user can act, with a message that says what to do next. No `try!` or force unwraps in app code.

## 6. SwiftData

```swift
// Models/Run.swift — CloudKit-ready: every property has a default, relationships are optional
import SwiftData

@Model
final class Run {
    var date: Date = Date.now
    var distanceMetres: Double = 0
    var notes: String = ""
    @Relationship(deleteRule: .nullify, inverse: \Shoe.runs)
    var shoe: Shoe?

    init(date: Date = .now, distanceMetres: Double) {
        self.date = date
        self.distanceMetres = distanceMetres
    }
}
```

```swift
// RunLogApp.swift
@main
struct RunLogApp: App {
    @State private var store = Store()   // starts the StoreKit listener at launch (section 8)

    var body: some Scene {
        WindowGroup {
            RunsList().environment(store)
        }
        .modelContainer(for: [Run.self, Shoe.self])
    }
}

// RunsList.swift
@Query(sort: \Run.date, order: .reverse) private var runs: [Run]
@Environment(\.modelContext) private var context
// context.insert(Run(distanceMetres: 5000)) — autosave writes it shortly after
```

- Filter with `#Predicate` in `@Query(filter:)`, or `FetchDescriptor` in services. The main context autosaves; call `try context.save()` when it must be on disk now (e.g. before an App Intent returns).
- **Previews:** a `@MainActor` `SampleData` with an in-memory container (`ModelConfiguration(isStoredInMemoryOnly: true)`) filled with realistic data, applied with `.modelContainer(SampleData.container)`. Use `#Preview`; `PreviewProvider` is the deprecated older form.
- **Widgets and App Intents** read the same store through an App Group: `ModelConfiguration(groupContainer: .identifier("group.com.example.runlog"))`. Decide this before the first TestFlight build; moving the store later strands existing data.
- **Large data** (photos, files): `@Attribute(.externalStorage)`.
- **Newer SwiftData APIs** (check each one's availability in the docs, and use `if #available` if the minimum iOS predates it): `@Query(…, sectionBy:)` for sectioned lists, `@Attribute(.codable)` for types SwiftData can't store natively (opaque: can't sort or filter on them), `ResultsObserver` to observe a query outside views, and `HistoryObserver` for persistent history changes.

**CloudKit constraints** (if the app syncs — design for them from the first model):
- No `@Attribute(.unique)`. CloudKit can't enforce it.
- Every property is optional or has a default value.
- Every relationship is optional, with an explicit inverse where SwiftData can't infer it. No `.deny` delete rule.
- Once the schema is in production it's additive only: add new properties and models; never rename, retype or delete existing ones.

**Migrations.** Before the first TestFlight build, wrap the models in `SchemaV1`. Every later change adds a new version and a stage:

```swift
enum SchemaV1: VersionedSchema {
    static let versionIdentifier = Schema.Version(1, 0, 0)
    static var models: [any PersistentModel.Type] { [Run.self, Shoe.self] }
    // @Model classes nested here, or typealiased
}

enum RunLogMigrationPlan: SchemaMigrationPlan {
    static var schemas: [any VersionedSchema.Type] { [SchemaV1.self, SchemaV2.self] }
    static var stages: [MigrationStage] {
        [.lightweight(fromVersion: SchemaV1.self, toVersion: SchemaV2.self)]
    }
}

// let container = try ModelContainer(for: Schema(versionedSchema: SchemaV2.self),
//                                    migrationPlan: RunLogMigrationPlan.self)
```

- Adding a property with a default is lightweight. Use `.custom(fromVersion:toVersion:willMigrate:didMigrate:)` to transform data.
- Test a migration by installing the previous TestFlight build, adding data, then installing the new build over it.

## 7. CloudKit sync

- **Turn it on:** the iCloud capability with CloudKit and the container, plus Background Modes → Remote notifications. SwiftData finds the container in the entitlements and syncs the private database automatically. To choose the container explicitly: `ModelConfiguration(cloudKitDatabase: .private("iCloud.com.example.runlog"))`; for a local-only store, `.none`.
- **Two environments.** Builds run from Xcode use the **Development** environment; TestFlight and App Store builds use **Production**. Data in one never appears in the other.
- **The schema.** Record types are created in Development as the app saves data (Apple also documents `initializeCloudKitSchema()` in a `#if DEBUG` block to create them all at once). **Before the first TestFlight build that syncs**, open the CloudKit Console (icloud.developer.apple.com), choose the container and **Deploy Schema Changes** to Production. Repeat after every model change, before uploading. Forget this and sync silently fails for every real user.
- **Testing.** Use two real devices (or a device and a Simulator) signed in to the same iCloud account. Sync takes seconds to minutes, not milliseconds. `xcrun simctl icloud_sync booted` nudges a Simulator. Test deleting on one device and editing on the other.
- **No iCloud account.** The app must still work: SwiftData keeps data local and syncs once the user signs in. Check `CKContainer.default().accountStatus()` only to show a quiet note in Settings.
- **Cost.** The private database counts against the user's iCloud storage, not yours.
- **Sharing with other people.** Check whether SwiftData supports CloudKit sharing in the installed SDK. Until it does, the routes are Core Data with `NSPersistentCloudKitContainer` sharing, or `CKSyncEngine` with shared record zones and `CKShare`. Both are significant work. If sharing or social features are central, recommend `blueprint-mobile-app` or a server instead.
- **`CKSyncEngine`** is the lower-level option when you need control over records, conflicts or the shared database. More code; choose it only when the brief needs it.

## 8. StoreKit 2 and the paywall

**Set up locally first.** Create a StoreKit configuration file (File → New → File → StoreKit Configuration File) with the brief's products, and select it in **Edit Scheme → Run → Options → StoreKit Configuration**. Purchases then work in the Simulator with no App Store Connect setup. Once the products exist in App Store Connect, the file can sync from them.

**Start listening at launch** and derive access from the current entitlements, never from a flag you saved yourself:

```swift
// Services/Store.swift — import StoreKit only; SwiftUI also has a type called Transaction
import StoreKit
import Observation

@Observable
final class Store {
    static let proIDs: Set<String> = ["com.example.runlog.pro.monthly", "com.example.runlog.pro.annual"]
    static let groupID = "<subscription group ID>"
    private(set) var isPro = false
    private var updates: Task<Void, Never>?

    init() {
        updates = Task { await listenForTransactions() }
        Task { await refreshEntitlements() }
    }

    private func listenForTransactions() async {
        for await result in Transaction.updates {        // renewals, Ask to Buy, offer codes, other devices
            guard case .verified(let transaction) = result else { continue }
            await refreshEntitlements()
            await transaction.finish()
        }
    }

    func refreshEntitlements() async {
        var pro = false
        for await result in Transaction.currentEntitlements {
            if case .verified(let t) = result, t.revocationDate == nil, Self.proIDs.contains(t.productID) { pro = true }
        }
        isPro = pro
    }
}
```

**The paywall** — use the StoreKit views; they load products, show localised prices and periods, and handle the purchase sheet:

```swift
SubscriptionStoreView(groupID: Store.groupID) {
    PaywallHeader()   // what they get, in plain words
}
.storeButton(.visible, for: .restorePurchases)
.subscriptionStorePolicyDestination(url: AppConfig.termsURL, for: .termsOfService)
.subscriptionStorePolicyDestination(url: AppConfig.privacyURL, for: .privacyPolicy)
```

- One-off unlock: `ProductView(id:)` or `StoreView(ids:)`.
- Custom buttons: load with `try await Product.products(for: ids)`; in SwiftUI buy with `@Environment(\.purchase)` (`try await purchase(product)`), elsewhere `try await product.purchase()`. Handle `.success(.verified(transaction))` (unlock, then `await transaction.finish()`), `.userCancelled` and `.pending` (Ask to Buy; the result arrives later through `Transaction.updates`).
- Always `finish()` a transaction after granting access, or StoreKit delivers it again.
- `.subscriptionStatusTask(for: groupID)` keeps a view in step with the subscription state. `.manageSubscriptionsSheet(isPresented:)` opens Apple's manage-subscription sheet. `.offerCodeRedemption(isPresented:)` redeems offer codes.
- **Restore:** StoreKit restores automatically on a new device, but App Review expects a **Restore Purchases** button. It calls `try await AppStore.sync()`, which may ask the user to sign in, so only call it from a tap.
- **No server needed.** StoreKit 2 transactions are signed and verified on the device (`VerificationResult`). App Store Server Notifications and the App Store Server API are only for apps with their own server.
- **Testing, in three tiers:** (1) the StoreKit configuration in the Simulator, with Xcode's transaction manager (**Debug → StoreKit → Manage Transactions**) to refund, expire and speed up renewals, and, in recent releases, test offer codes; automate with `SKTestSession` from the `StoreKitTest` framework; (2) on a device with a **Sandbox Apple Account** (App Store Connect → Users and Access → Sandbox); (3) TestFlight, where purchases are free and renewals are accelerated.
- In App Store Connect each subscription needs a reference name, product ID matching the code, duration, price, a display name and description per localisation, and a review screenshot of the paywall. The first in-app purchase must be submitted with an app version.

## 9. App Review rules that catch people out

- **3.1.1** — unlocking features or content must use in-app purchase; restorable purchases need a restore mechanism.
- **3.1.2(a)** — subscriptions must give ongoing value, last at least seven days, and work on all the user's devices.
- **3.1.2(c)** — before asking someone to subscribe, describe clearly what they get for the price, and meet Schedule 2 of the Apple Developer Program License Agreement. In practice the paywall shows the subscription name, length and price per period, what happens when a trial ends, and working links to the Terms of Use (EULA) and privacy policy. Put the same links in the App Store metadata (the privacy policy URL field, and the terms in the description or a custom licence agreement). The close button must be visible; the price must not be the smallest, faintest text on the screen.
- **2.1** — the build must be complete: no placeholder text, nothing broken, in-app purchases visible and working for the reviewer, and demo instructions in the review notes if anything is hard to reach.
- **5.1.1(i)** — a privacy policy link in App Store Connect and inside the app.
- **5.1.1(ii)** — purpose strings must say clearly why the app needs the data; paid features can't depend on granting access to data.
- **5.1.1(v)** — don't require a login unless the app has significant account-based features; if users can create an account, they must be able to delete it in the app.
- **4.8** — if the app uses a third-party or social login for the primary account, it must also offer an equivalent privacy-focused option such as Sign in with Apple.
- **4.2** — the app must be more than a repackaged website, and genuinely useful.
- **2.3.7** — app name at most 30 characters; no prices or competitor names in the name, subtitle or keywords.

## 10. Accounts and Sign in with Apple

- **Default: no accounts.** iCloud identifies the user for sync; the App Store for purchases. Guideline 5.1.1(v) rewards this.
- **If a server needs identity:** Sign in with Apple via `SignInWithAppleButton` (AuthenticationServices) and the Sign in with Apple capability. Store the user identifier in the Keychain and check `ASAuthorizationAppleIDProvider().getCredentialState(forUserID:)` at launch.
- **Account deletion** must be available in the app, and for Sign in with Apple it must also revoke the user's tokens through Apple's REST API, which needs a server. Accounts are a server decision; if the brief has one, consider whether `blueprint-mobile-app` or a separate API fits better.

## 11. System integrations and permissions

| Integration | Framework | Permission and `Info.plist` key | Capability |
|---|---|---|---|
| Local notifications | UserNotifications | `requestAuthorization(options:)` at the moment it's useful; no key | None (remote push needs a server) |
| Widgets | WidgetKit (widget extension target) | None | App Group to share the SwiftData store |
| Live Activities | ActivityKit | `NSSupportsLiveActivities` = YES | Widget extension |
| Siri, Shortcuts, Spotlight, Action button | App Intents (`AppIntent`, `AppShortcutsProvider`) | None | None |
| Health data | HealthKit | `NSHealthShareUsageDescription`, `NSHealthUpdateUsageDescription` | HealthKit |
| Camera | AVFoundation | `NSCameraUsageDescription` | — |
| Choosing photos | PhotosUI `PhotosPicker` | None (it runs outside the app) | — |
| Location | CoreLocation | `NSLocationWhenInUseUsageDescription` | — |
| Microphone | AVFoundation | `NSMicrophoneUsageDescription` | — |

- Write usage strings as one sentence about the user's benefit (*"RunLog uses your location to map each run. It never leaves your iPhone."*). Set them in the target's **Info** tab and localise them.
- Ask only when the user taps the feature that needs it. If they decline, keep the app working and offer a button to Settings (`UIApplication.openSettingsURLString`).
- A first App Intent is a few lines and makes the app usable from Siri, Shortcuts and Spotlight:

```swift
struct LogRunIntent: AppIntent {
    static let title: LocalizedStringResource = "Log a run"
    @Parameter(title: "Distance (km)") var kilometres: Double
    func perform() async throws -> some IntentResult & ProvidesDialog {
        // insert into the shared store, then save
        return .result(dialog: "Logged \(kilometres) km.")
    }
}
```

- Widgets read the shared store and refresh through their timeline; call `WidgetCenter.shared.reloadAllTimelines()` after the app changes data they show.

## 12. Design: HIG, system design language, icon and launch screen

- **Follow the Human Interface Guidelines** and use standard components: `NavigationStack`, `TabView`, `List`, `Form`, toolbars, sheets, `Label`, SF Symbols. They get the current look, Dynamic Type and accessibility for free.
- **The current system design language** (Liquid Glass at the time of writing): standard bars, tab bars, sheets and controls adopt it automatically. The current SDK ignores the `UIDesignRequiresCompatibility` opt-out, so every app built with current Xcode gets it; confirm in Apple's docs before relying on any opt-out. Use `.buttonStyle(.glass)` / `.glassProminent` and `.glassEffect()` sparingly, for controls that float above content; never for content itself. Don't paint custom backgrounds behind navigation and tab bars.
- **Colour:** semantic colours (`.primary`, `.secondary`, system backgrounds) plus one accent colour in the asset catalog, checked in light and dark mode.
- **Layout:** adapt by size class (`@Environment(\.horizontalSizeClass)`), never by device model. The foldable iPhone Duo's inner screen reports a regular width, like an iPad.
- **App icon:** design it in **Icon Composer** (use the version that matches the installed Xcode; it previews how the icon renders across the system's appearances). Drag the `.icon` file into the project as a normal resource (not into the asset catalog), set the target's **App Icon** name to match it, and remove any old asset-catalog app icon. A single 1024 × 1024 PNG in the asset catalog still works, and the system renders it in the current style, but you lose control of how it looks.
- **Launch screen:** apps built with the current SDK must have one configured in `Info.plist`. The SwiftUI template generates a `UILaunchScreen` entry; keep it and set its background colour to match the first screen.

## 13. Accessibility and localisation

- **Dynamic Type:** system text styles (`.font(.body)`, `.headline`), never fixed point sizes. Let text wrap; switch horizontal stacks to vertical at accessibility sizes (`@Environment(\.dynamicTypeSize)` with `.isAccessibilitySize`, or `ViewThatFits`).
- **VoiceOver:** every icon-only button has a label (`Label("Add run", systemImage: "plus")` gives one free); `.accessibilityLabel` and `.accessibilityValue` for custom controls; `.accessibilityElement(children: .combine)` for rows; `Image(decorative:)` for decoration.
- Contrast at least 4.5:1 for text, never colour alone to carry meaning, and respect Reduce Motion (`@Environment(\.accessibilityReduceMotion)`).
- **Audit:** Accessibility Inspector (Xcode → Open Developer Tool) and `try app.performAccessibilityAudit()` in a UI test. Then declare what the app supports in App Store Connect's **Accessibility Nutrition Labels**.
- **Localisation:** a `Localizable.xcstrings` String Catalog. `Text("…")` literals are extracted automatically; use `String(localized:)` outside views, plural variants in the catalog, and `.formatted()` for numbers, dates and measurements. Xcode's agent tools can translate a String Catalog; have a native speaker review before shipping a language.

## 14. Testing

- **Swift Testing** for logic: `import Testing`, `@Test`, `#expect`, `#require`, `@Test(arguments:)` for tables of cases. Test models against an in-memory `ModelContainer`, and entitlement logic with `SKTestSession`.
- **One UI test for the core loop**, from a fresh install to the magic moment. Launch with an argument (e.g. `-ui-testing`) that the app reads to use an in-memory store and skip the welcome screen. Find elements by `accessibilityIdentifier`, not by text, and call `performAccessibilityAudit()` on the main screens.
- **Previews** for every screen, with sample data, including empty state, long text and the largest Dynamic Type size.
- **Real device** before every TestFlight build: the core loop, with Wi-Fi and mobile data off.

## 15. Performance

- **`body` must be cheap.** No fetching, sorting large arrays, creating formatters or decoding images inside it. Let `@Query` sort and filter; precompute in the model.
- Long content in `List` or `LazyVStack` with stable identities. Downsample large photos before showing them.
- **Launch:** nothing before the first frame that the first screen doesn't need. No network calls blocking launch.
- **Measure** with Instruments (SwiftUI, Time Profiler, Hangs, Swift Concurrency), and after release with Organizer's launch time, hangs and hitches.

## 16. Privacy

- **Privacy manifest:** add `PrivacyInfo.xcprivacy` (File → New → File → App Privacy). Declare every required-reason API the app uses, with its reason code. `UserDefaults` (including `@AppStorage`) is one: category `NSPrivacyAccessedAPICategoryUserDefaults`, reason `CA92.1` for data only the app reads. File timestamps, system boot time and disk space have their own codes; pick them from Apple's list. Set `NSPrivacyTracking` to false and list any collected data types.
- **Check it:** archive, then in Organizer right-click the archive → **Generate Privacy Report**.
- **App Privacy label** in App Store Connect describes data that leaves the device to you or a third party. With no server, analytics or third-party SDKs, that's often nothing; data synced only to the user's own private iCloud database isn't data you can access. Read Apple's App Privacy definitions and answer honestly.
- No tracking, so no App Tracking Transparency prompt.
- Tokens and anything sensitive go in the Keychain, never `UserDefaults` or files.
- **Export compliance:** if the app uses only the encryption built into iOS (HTTPS, CloudKit), set `ITSAppUsesNonExemptEncryption` to NO in `Info.plist` so uploads don't stop to ask.

## 17. Crashes and metrics

- **Xcode Organizer → Crashes, Hangs, Energy, Disk Writes, Launch Time, Hitches, Storage** for TestFlight and App Store builds, from users who share analytics. Where Organizer offers **Generate Recommendations**, use it to analyse a diagnostic and point at the code.
- **TestFlight feedback** (screenshots and comments from testers) appears in App Store Connect and Organizer.
- **MetricKit** for in-app access to the same reports: the current convention is `MetricManager`, which delivers metric and diagnostic reports as async sequences (the older `MXMetricManager` subscriber is deprecated); if the minimum iOS predates `MetricManager`, keep the subscriber behind `if #available`. Confirm which the installed SDK offers.
- Keep symbol upload on (the default) so crash logs show your function names. No third-party crash SDK by default.

## 18. Distribution: signing, upload, TestFlight, review

- **Signing:** automatic signing with the team creates the certificates, App ID and profiles. With the account added in Xcode (Settings → Accounts), nothing else is needed.
- **Versions:** `MARKETING_VERSION` (1.0, what users see) and `CURRENT_PROJECT_VERSION` (the build). Xcode's upload manages build numbers by default.
- **Upload from Xcode:** **Product → Archive** (destination *Any iOS Device*), then in Organizer **Distribute App → App Store Connect**.
- **Upload from the command line** with an App Store Connect API key (Users and Access → Integrations → App Store Connect API → Team Keys, role App Manager; the `.p8` file downloads once, keep it outside the repo):

```
xcodebuild -scheme <Scheme> -destination 'generic/platform=iOS' -archivePath build/<App>.xcarchive archive
xcodebuild -exportArchive -archivePath build/<App>.xcarchive -exportOptionsPlist ExportOptions.plist \
  -exportPath build/export -allowProvisioningUpdates \
  -authenticationKeyPath <path/AuthKey_ID.p8> -authenticationKeyID <key id> -authenticationKeyIssuerID <issuer id>
```

  `ExportOptions.plist` sets `method` to `app-store-connect` and `destination` to `upload`. (`xcrun altool --upload-package` and the Transporter app also still upload builds.)
- **SDK minimum:** Apple raises the minimum Xcode and SDK for App Store uploads each spring; check https://developer.apple.com/news/upcoming-requirements before uploading.
- **TestFlight:** internal testers (up to 100 members of your App Store Connect team) get builds as soon as they process, with no review. External testers (up to 10,000, by email or public link) need the first build of each version to pass Beta App Review. Builds expire after 90 days. TestFlight uses the CloudKit **Production** environment and free sandbox purchases.
- **Xcode Cloud** (optional): builds, tests and uploads on Apple's servers; 25 compute hours a month are included in the membership. Worth it once releases are frequent.
- **App Review:** Apple reviews at least 50% of submissions within 24 hours and 90% within 48 hours. Choose manual or automatic release; for updates, phased release spreads automatic updates over seven days and can be paused.

## 19. Patterns to avoid

- `ObservableObject`, `@Published`, `@StateObject` and `@EnvironmentObject` in new code (use `@Observable`, `@State`, `@Environment`).
- Combine for new code (use async/await and Observation). Core Data for new apps (use SwiftData unless sharing is core).
- UIKit screens where SwiftUI works; `UIDesignRequiresCompatibility` to dodge the system design language (the current SDK ignores it).
- A view model for every screen, and `NavigationView` or untyped navigation.
- Force unwraps and `try!` in app code; ignoring strict-concurrency warnings or dropping to an older Swift language mode to silence them.
- Heavy work in `body` or on the main actor; network calls before the first frame.
- Secrets, API keys or "premium" flags in the bundle, `UserDefaults` or `Info.plist`.
- Saving "isPro" yourself instead of checking `Transaction.currentEntitlements`; not starting the `Transaction.updates` listener at launch; forgetting `finish()`.
- `@Attribute(.unique)`, non-optional relationships or properties without defaults in a CloudKit-synced model; renaming or deleting synced properties.
- Shipping without deploying the CloudKit schema to production.
- Asking for every permission at launch; vague usage strings; onboarding carousels and sign-up walls before the core loop.
- Fixed font sizes, icon-only buttons without labels, colours that only work in light mode.
- Third-party analytics, crash or ad SDKs added without a reason in the brief (each one changes the privacy label).
- Hiding the subscription price, renewal terms or the close button on the paywall.
- `PreviewProvider` (deprecated; use `#Preview`) and copying API patterns from memory instead of checking the current docs.
