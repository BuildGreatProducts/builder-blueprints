# Changelog

## 0.2.1 — October 2026

**Evergreen blueprints: no more version numbers.**

- Every blueprint drops pinned versions and "last verified" dates for guiding principles: start from the official create command, check what's installed, read the version-matched docs, and let the docs win when they disagree with the blueprint
- Each `REFERENCE.md` now opens with a "Staying current" note tailored to its stack
- `blueprint-website`: Cache Components on, `ensureStatic = 'navigation'` to keep every page static, `notFound()` instead of `dynamicParams`, CMS data tagged with `cacheTag`
- `blueprint-web-app`: signed-in server rendering inside `<Suspense>`, `ClerkProvider` inside `<body>`, marketing pages kept static with `ensureStatic`

## 0.2.0 — October 2026

**Three new app blueprints: web, mobile and native iOS.**

- `blueprint-web-app`: full-stack web apps with Next.js and Convex
- `blueprint-mobile-app`: iOS and Android apps with Expo, Convex and RevenueCat
- `blueprint-ios-app`: native iPhone apps with SwiftUI, SwiftData, CloudKit and StoreKit

## 0.1.0 — October 2026

**First release: five build blueprints, each with an interview, a reference, a checklist and a launch guide, plus an update skill.**

- `blueprint-website`: Next.js with strong SEO
- `blueprint-ai-plugin`: Claude Code plugins and agent skills
- `blueprint-threejs-game`: three.js games with a Blender asset pipeline
- `blueprint-mcp-server`: MCP servers, embedded in an app or standalone
- `blueprint-node-api`: Node.js APIs designed around your use case
- `blueprint-update`: pulls the latest blueprints from the public repo
