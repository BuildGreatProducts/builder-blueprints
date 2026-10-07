# Launch guide template — iOS App

Use this template to write `docs/ios-app-launch.md`. Tailor it to what was actually built: fill in the real app name, bundle ID, CloudKit container, product IDs and commands, and delete phases or steps that don't apply (CloudKit if the app is local only, in-app purchases if it's free, account deletion and the demo account if there are no accounts). Keep the legend and the step format.

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

**What you're launching:** <one sentence — what the app does, who it's for, and how it makes money (e.g. free with a Pro subscription at £2.99/month or £19.99/year)>
**Estimated total time:** <x hours of your time, plus 1–3 days for developer account approval (longer for an organisation) and usually 1–2 days for App Review> · **Cost:** <Apple Developer Program 99 USD/year (charged in local currency) · Apple's commission on sales: 15% if you join the App Store Small Business Program, otherwise 30% · a web page for the privacy policy and support (free options are fine) · Xcode Cloud optional, 25 hours/month included>

**Legend**
- 🧑 **You** — needs your accounts, identity, payment or a decision.
- 🤖 **Agent** — paste the prompt into your coding agent.
- 🤝 **Together** — the agent prepares it, you click the final button.

## Phase 0 — Fix blockers (only if the checklist found must-fix items)
- [ ] 🤖 <blocker> — <time>
  > <ready-to-paste prompt>
  You'll know it worked when: <…>

## Phase 1 — Final checks
- [ ] 🤖 Run the build, the tests and the checklist — 20 min
  > Run a clean Release build of the <Scheme> scheme and fix every warning. Run the unit and UI tests on the <iPhone model> simulator. Then audit the app against the blueprint-ios-app CHECKLIST.md and list any [must] failures with a fix for each, marking anything that needs a real device or App Store Connect as "needs you".
  You'll know it worked when: zero warnings, the tests pass, and the only open items are marked "needs you".
- [ ] 🧑 Use the app on your own iPhone for a day — 1 day
  Install it from Xcode (plug in the phone, pick it as the run destination, press Run). Use it the way a customer would, including once with Airplane Mode on.
  You'll know it worked when: you've done the core loop for real, nothing crashed, and nothing embarrassed you.
- [ ] 🤖 List what App Store Connect will ask for — 5 min
  > From the project, list the bundle ID, version and build number, every capability and entitlement, every permission with its usage string, the CloudKit container, and every in-app purchase product ID with its type. Also tell me what data, if any, leaves the device, for the App Privacy questions.
  You'll know it worked when: you have one short list to copy from in the phases below.
- [ ] 🧑 Publish a privacy policy and a support page — 30 min
  Both need public web addresses. A simple page on your website, or a free page builder, is fine. The privacy policy says what the app collects (often: nothing leaves your device except your own iCloud sync), and the support page gives an email address.
  You'll know it worked when: both URLs open on your phone.

## Phase 2 — Apple Developer account
- [ ] 🧑 Enrol in the Apple Developer Program — 30 min, plus 1–3 days for approval · 99 USD/year
  Go to developer.apple.com/programs/enroll, or use the Apple Developer app. As an **individual**, your own name appears as the seller on the App Store. As an **organisation**, you need a legal entity and a free D-U-N-S number from Dun & Bradstreet first (allow up to a couple of weeks), and the company name appears as the seller.
  You'll know it worked when: you can sign in to appstoreconnect.apple.com.
- [ ] 🧑 Sign in to Xcode with that account — 2 min
  Xcode → Settings → Accounts → + → Apple Account. Then, on the app target's **Signing & Capabilities** tab, choose your team with **Automatically manage signing** on.
  You'll know it worked when: there are no signing errors on that tab and the app runs on your iPhone.

## Phase 3 — Agreements, tax and banking (only if the app sells anything)
- [ ] 🧑 Accept the Paid Apps Agreement and add tax and bank details — 30 min
  In App Store Connect → **Business**, accept the Paid Apps Agreement, then complete the tax forms and add a bank account. Without this, purchases can't be tested in TestFlight or sold.
  You'll know it worked when: the Paid Apps Agreement shows as **Active**.
- [ ] 🧑 Apply for the App Store Small Business Program — 10 min
  If you earn under 1 million USD a year from the App Store, apply at developer.apple.com/app-store/small-business-program to pay 15% commission instead of 30%. It isn't automatic.
- [ ] 🧑 Set your EU trader status — 5 min (only if you'll sell in the EU)
  In App Store Connect → **Business**, complete the Digital Services Act trader status. Say whether you're a trader; traders must give contact details that are shown on the EU App Store, and apps without a status can't be updated there.

## Phase 4 — Create the app in App Store Connect
- [ ] 🧑 Add the app record — 10 min
  App Store Connect → Apps → **+ → New App**: platform iOS, name `<app name>` (30 characters at most, unique on the store), primary language, bundle ID `<bundle id>` (it appears here once Xcode has registered it), and a SKU (any private reference, e.g. `runlog-ios`).
  You'll know it worked when: the app page opens with an empty 1.0 version.

## Phase 5 — In-app purchases (only if the app sells anything)
- [ ] 🤝 Create the products — 30 min
  > From the StoreKit configuration file, give me, for each product: type, reference name, product ID, subscription group and duration (for subscriptions), price, any free trial, and an English display name and description of at most the lengths App Store Connect allows. Keep the IDs identical to the code.
  In App Store Connect → your app → **Monetization → Subscriptions** (or **In-App Purchases** for a one-off unlock), create the group and products from that list. Add a localisation for the group and each product, a review screenshot of the paywall, and turn Family Sharing on or off.
  You'll know it worked when: each product shows **Ready to Submit**, and the product IDs match the code exactly.

## Phase 6 — CloudKit production schema (only if the app syncs)
- [ ] 🧑 Deploy the schema to Production — 10 min
  Open icloud.developer.apple.com → CloudKit Console → `<container>`. Check the Development schema has every record type (run the latest build from Xcode and save one of each kind of item first). Then choose **Deploy Schema Changes** and confirm. Repeat this before every future upload that changes the data model.
  You'll know it worked when: the Production environment shows the same record types as Development.

## Phase 7 — Upload the first build
- [ ] 🤝 Archive and upload — 20 min
  In Xcode, choose **Any iOS Device** as the destination, then **Product → Archive**. In the Organizer window that opens, choose **Distribute App → App Store Connect** and follow the prompts.
  > (Command-line alternative) Using my App Store Connect API key at <path>, key ID <id> and issuer ID <issuer>, archive the <Scheme> scheme for generic iOS and upload it with `xcodebuild -exportArchive` and an ExportOptions.plist with method app-store-connect and destination upload. Don't print or commit the key.
  You'll know it worked when: the build appears under **TestFlight** in App Store Connect and its status changes from Processing to ready (usually 10–30 minutes). Answer the export compliance question if asked.

## Phase 8 — TestFlight
- [ ] 🧑 Test with your own team first — 15 min, then a few days of use
  App Store Connect → TestFlight → **Internal Testing** → add a group with yourself (and up to 100 people on your team). Install the TestFlight app on your iPhone and install the build.
  You'll know it worked when: the TestFlight build runs on your phone. If it syncs, check data moves between two of your devices; if it sells, buy and restore (TestFlight purchases are free).
- [ ] 🧑 Invite outside testers — 15 min, plus usually a day for Beta App Review
  **External Testing** → new group → add the build, fill in the test information, and submit for Beta App Review. Then share the public link with 5–20 people who match the brief's user.
  You'll know it worked when: testers can install it, and their feedback and crashes appear in TestFlight.

## Phase 9 — The App Store listing
- [ ] 🤝 Write the listing — 45 min
  > Draft the App Store listing from docs/ios-app-brief.md: subtitle (30 characters), promotional text (170), description (plain text, first three lines do the selling), and keywords (100 characters, comma-separated, no spaces, no words already in the name). No prices, competitor names or claims we can't back up.
  Paste it into the 1.0 version page, along with the support URL, privacy policy URL, category, and copyright line.
- [ ] 🤖 Make the screenshots — 30 min
  > Seed realistic sample data, boot the <iPhone model with Dynamic Island> simulator, set the status bar to 9:41 with `xcrun simctl status_bar booted override --time 9:41`, and capture the core loop, the magic moment and the paywall with `xcrun simctl io booted screenshot`. Check they match the sizes App Store Connect currently requires.
  You'll know it worked when: you have 3–6 screenshots at an accepted size that tell the story in order.
- [ ] 🧑 Answer App Privacy, age rating and pricing — 20 min
  **App Privacy**: answer from the Phase 1 list. **Age rating**: complete the questionnaire, which also asks about in-app controls, capabilities, medical or wellness topics and social features. **Pricing and Availability**: price (usually free, with in-app purchases) and countries. Optionally declare **Accessibility Nutrition Labels** for what the app supports.
  You'll know it worked when: none of these sections shows a warning.

## Phase 10 — Submit for review
- [ ] 🧑 Submit — 15 min
  On the 1.0 version: choose the build, add the in-app purchases to this version (the first ones must go with an app version), and write **review notes** saying how to reach the paywall and any feature that's hard to find. If the app has accounts, give a demo account. Choose **Manually release this version** so you control the launch moment. Click **Add for Review**, then **Submit**.
  You'll know it worked when: the status shows **Waiting for Review**. Apple reviews at least half of submissions within 24 hours and 90% within 48 hours.
- [ ] 🤝 If it's rejected — 30 min
  > Here is App Review's message: <paste>. Explain which guideline it cites, what they saw, and the smallest change that fixes it. Draft a short, polite reply for Resolution Center.
  Common reasons: crashes or broken features on the reviewer's device; paywall missing price, period, terms or privacy links; no Restore Purchases; placeholder content; vague permission strings; a login wall without account features; missing account deletion.

## Phase 11 — Release
- [ ] 🧑 Release the app — 2 min
  When the status is **Pending Developer Release**, click **Release This Version**. It appears on the App Store within a few hours.
  You'll know it worked when: you can find it by name in the App Store on your phone and install it.
- [ ] 🧑 Smoke test the App Store build — 15 min
  Delete the TestFlight version, install from the App Store, run the core loop, and restore or make a real purchase (refund yourself afterwards through reportaproblem.apple.com if you like).
  You'll know it worked when: the core loop and the purchase work, and data syncs to your second device.

## After launch
- Check Xcode Organizer (Crashes, Hangs) and App Store Connect (Analytics, Subscriptions) every few days for the first two weeks.
- Reply to App Store reviews, especially the critical ones; it's visible to everyone who reads them.
- For updates, use **phased release** so problems reach only a few users first, and deploy the CloudKit schema before uploading any build that changes the data model.
- Re-run the checklist before every submission, and keep Xcode current: App Store Connect raises the minimum SDK each spring.
```
