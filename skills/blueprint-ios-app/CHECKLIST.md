# iOS App — Checklist

Audit the real project against every item. **[must]** blocks submission. **[should]** is strongly recommended. Each item says how to verify it. Build from the command line, inspect the built app, and drive the Simulator or a real iPhone; never assume a pass. Items that need a real device or App Store Connect are reported as *"needs you"* until the user confirms them. Section numbers refer to `REFERENCE.md` in this skill's folder. In the commands, `<dest>` is `'platform=iOS Simulator,name=<iPhone model>'` with a name from `xcrun simctl list devices available`, and `<App>.app` is the built app under `build/Build/Products/`.

## Build and code
- [ ] **[must]** A Release build succeeds with zero warnings, in Swift 6 language mode. *Verify: `xcodebuild -scheme <Scheme> -configuration Release -destination 'generic/platform=iOS Simulator' -derivedDataPath build clean build 2>&1 | grep -c "warning:"` returns 0; `xcodebuild -showBuildSettings -scheme <Scheme> | grep -E "SWIFT_VERSION|SWIFT_DEFAULT_ACTOR_ISOLATION"` shows 6 and MainActor.*
- [ ] **[must]** The unit tests pass. *Verify: `xcodebuild -scheme <Scheme> -destination <dest> test`.*
- [ ] **[must]** A UI test runs the core loop from a fresh install to the magic moment, and passes. *Verify: read the UI test, then `xcodebuild -scheme <Scheme> -destination <dest> test -only-testing:<App>UITests`.*
- [ ] **[must]** No secrets, API keys or private URLs in the source, the git history or the bundle. *Verify: `git grep -nEi "(api[_-]?key|secret|token|password|bearer)"` and review the hits; `strings build/Build/Products/Release-iphonesimulator/<App>.app/<App> | grep -Ei "key|secret|token"`.*
- [ ] **[must]** No placeholder copy or invented content: no `TODO:`, lorem ipsum, fake reviews or made-up statistics on any screen or the paywall. *Verify: `grep -rniE "TODO:|lorem|ipsum|example\.com" --include=*.swift --include=*.xcstrings .`, then look at every screen.*
- [ ] **[should]** No force unwraps or `try!` outside previews and tests. *Verify: `grep -rnE "try!|as!|[A-Za-z0-9_)]!" --include=*.swift <App>/` and review the hits.*
- [ ] **[should]** New code uses `@Observable`, not `ObservableObject`/`@Published`, and no Combine. *Verify: `grep -rnE "ObservableObject|@Published|@StateObject|import Combine" --include=*.swift .`.*
- [ ] **[should]** Every screen has a `#Preview` with sample data, and none use `PreviewProvider`. *Verify: `grep -rln "#Preview" --include=*.swift .` against the feature folders; `grep -rn "PreviewProvider"`.*

## Data and sync
- [ ] **[must]** The core loop works offline: with Wi-Fi and mobile data off, the user can create, edit and see their data. *Verify: on a real iPhone in Airplane Mode; or the Simulator with the Mac offline. Needs you if no device.*
- [ ] **[must]** If the app syncs, every `@Model` is CloudKit-compatible: no `.unique` attributes, every property optional or defaulted, every relationship optional, no `.deny` delete rule. *Verify: `grep -rnE "\.unique|deleteRule: \.deny" --include=*.swift Models/`, then read every model.*
- [ ] **[must]** If the app syncs, the CloudKit schema is deployed to Production and matches the current models. *Verify: CloudKit Console → container → Schema, compare Production record types with the models. Needs you.*
- [ ] **[must]** If the app syncs, a change on one device appears on a second device signed in to the same iCloud account, using a TestFlight build. *Verify: on two devices. Needs you.*
- [ ] **[must]** If the schema changed since the last TestFlight or App Store build, there's a new `VersionedSchema` and a migration stage, and the old build's data survives an upgrade. *Verify: read `Models/`; install the previous build, add data, install the new one over it.*
- [ ] **[should]** The app works without an iCloud account, keeping data on the device. *Verify: sign out of iCloud in a Simulator, run the core loop.*

## Purchases (if the app sells anything)
- [ ] **[must]** A `Transaction.updates` listener starts at launch, and access is derived from `Transaction.currentEntitlements`, not a saved flag. *Verify: read the `App` struct and the store service.*
- [ ] **[must]** Every verified transaction is `finish()`ed after access is granted. *Verify: `grep -rn "finish()" --include=*.swift .` and read each purchase path.*
- [ ] **[must]** Purchase, restore, renewal, cancellation, refund and Ask to Buy all behave correctly. *Verify: the StoreKit configuration in the Simulator with Debug → StoreKit → Manage Transactions (expire, refund, approve), then a Sandbox Apple Account on a real iPhone.*
- [ ] **[must]** The paywall shows each plan's name, length and price per period, what happens when the trial ends, a visible close button, a Restore Purchases button, and working Terms of Use and privacy policy links. *Verify: screenshot the paywall at default and largest text sizes; tap every link.*
- [ ] **[must]** The product IDs in the code match the StoreKit configuration and the products in App Store Connect. *Verify: `grep -rn "com\." Services/Store.swift` against the `.storekit` file and App Store Connect.*
- [ ] **[should]** Settings has Manage Subscription and Restore Purchases. *Verify: open Settings in the Simulator.*

## Privacy and permissions
- [ ] **[must]** Every permission the app requests has a clear, specific usage string, and nothing is requested at launch. *Verify: `plutil -p <App>.app/Info.plist | grep UsageDescription`; launch a fresh install and confirm no prompt appears before the user taps the feature.*
- [ ] **[must]** The entitlements are exactly the capabilities the brief needs. *Verify: `codesign -d --entitlements - <App>.app` against the brief's integrations table.*
- [ ] **[must]** `PrivacyInfo.xcprivacy` exists, is valid, and declares every required-reason API the code uses (including `UserDefaults`/`@AppStorage`). *Verify: `plutil -lint <App>/PrivacyInfo.xcprivacy`; `grep -rnE "UserDefaults|@AppStorage|systemUptime|volumeAvailableCapacity|creationDate|modificationDate" --include=*.swift .`; Organizer → Generate Privacy Report on an archive.*
- [ ] **[must]** A privacy policy is linked inside the app and describes what the app actually collects. *Verify: tap the link in Settings; read it against the brief.*
- [ ] **[must]** If users can create an account, they can delete it in the app. *Verify: follow the path in the Simulator.*
- [ ] **[should]** `ITSAppUsesNonExemptEncryption` is set to NO if the app uses only the system's encryption. *Verify: `plutil -p <App>.app/Info.plist | grep ITSAppUsesNonExemptEncryption`.*

## Accessibility, design and localisation
- [ ] **[must]** The core loop is fully usable at the largest accessibility text size, with nothing clipped or overlapping. *Verify: `xcrun simctl ui booted content_size accessibility-extra-extra-extra-large`, run the core loop, take screenshots with `xcrun simctl io booted screenshot`.*
- [ ] **[must]** The core loop works with VoiceOver: every control has a meaningful label and the order makes sense. *Verify: `try app.performAccessibilityAudit()` in the UI test; Accessibility Inspector audit; VoiceOver on a real device. Needs you for the device pass.*
- [ ] **[must]** Every screen looks right in dark mode. *Verify: `xcrun simctl ui booted appearance dark` and screenshot each screen.*
- [ ] **[must]** The app has a final icon (an Icon Composer `.icon` set as the target's app icon, or a 1024 × 1024 asset-catalog icon), and a launch screen configured in `Info.plist`. *Verify: read the target's General tab or `grep -rn "ASSETCATALOG_COMPILER_APPICON_NAME" *.xcodeproj/project.pbxproj`; `plutil -p <App>.app/Info.plist | grep UILaunchScreen`.*
- [ ] **[should]** All user-facing strings are in a String Catalog, none hard-coded with string concatenation. *Verify: open `Localizable.xcstrings` and look for stale or missing entries; `grep -rn 'Text(".*" *+' --include=*.swift .`.*
- [ ] **[should]** Text and icons meet 4.5:1 contrast and nothing relies on colour alone. *Verify: Accessibility Inspector audit.*

## Device and App Store readiness
- [ ] **[must]** The app runs on a real iPhone, from fresh install through the core loop and the paywall, with no crash or hang. *Verify: install from Xcode or TestFlight. Needs you.*
- [ ] **[must]** Version and build numbers are set, and the build number is higher than any already uploaded. *Verify: `xcodebuild -showBuildSettings -scheme <Scheme> | grep -E "MARKETING_VERSION|CURRENT_PROJECT_VERSION"`.*
- [ ] **[must]** The built SDK meets App Store Connect's current minimum (Xcode 26 / iOS 26 SDK or later at last check). *Verify: `xcodebuild -version`; check https://developer.apple.com/news/upcoming-requirements.*
- [ ] **[should]** Screenshots exist at the sizes App Store Connect currently requires (at last check: iPhone with Dynamic Island, e.g. 1206 × 2622 or 1320 × 2868; plus iPad 13-inch 2064 × 2752 only if the app runs natively on iPad). *Verify: `sips -g pixelWidth -g pixelHeight <file>.png` against App Store Connect's screenshot specifications.*
- [ ] **[should]** The supported destinations match the brief (iPhone only unless stated). *Verify: `xcodebuild -showBuildSettings -scheme <Scheme> | grep TARGETED_DEVICE_FAMILY` (1 = iPhone).*
