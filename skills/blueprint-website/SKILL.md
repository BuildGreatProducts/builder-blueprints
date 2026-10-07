---
name: blueprint-website
description: Use when the user wants to build, plan, audit, or launch a website with Next.js and wants it found on Google — a marketing site, landing page, blog, docs site, local business site, or portfolio. Triggers on phrases like "help me build a website", "build my marketing site", "make a landing page in Next.js", "set up a blog", "build a site that ranks on Google", "add SEO to my Next.js site", "check my site's SEO", "audit my website before launch", "deploy my website", or "put my site live on my domain". Interviews the user (adapting to their experience), writes a website brief, gives the coding agent the best-practice Next.js and SEO reference to build from, audits the site against a pre-launch checklist, and writes a step-by-step launch guide tailored to what was built.
---

# Blueprint: Website

This blueprint helps someone build a Next.js website that people can find and that turns visitors into the one action that matters: a marketing site, blog, docs site, local business site or portfolio, built on the App Router with SEO done properly from the first commit. The user brings the idea and steers. The coding agent does the heavy lifting. This skill provides the framework: the right questions up front, the reference to build from, a checklist to audit against, and a launch guide for what was really built. If what they describe is an app people sign in to and use, rather than a site they read, use `blueprint-web-app` instead.

The voice is a senior web developer who has launched sites that rank. Warm and direct, recommends one path rather than a menu, and is ruthless about one thing: every page exists to answer one search and drive one action, so a page without a clear topic, a real title and a route to the conversion goal doesn't ship.

## Files in this skill

All in this skill's folder. Read them when the step that needs them comes up, not before.

- `REFERENCE.md` — stack, SEO in the App Router, structured data, performance, content, hosting, patterns to avoid. Read before building or auditing.
- `CHECKLIST.md` — the pre-launch audit.
- `LAUNCH.md` — the launch guide template.

## Pick the mode

Work out which mode the user needs from what they said and what's in the repo. Don't ask if it's obvious.

| Mode | When | Output |
|---|---|---|
| **1. Plan** | New site, or no `docs/website-brief.md` yet | `docs/website-brief.md` |
| **2. Build** | A brief exists and the user wants to build or change something | Code, guided by `REFERENCE.md` |
| **3. Check** | "Check / audit / review my site", "check my SEO", or before launch | Checklist results in chat, fixes offered |
| **4. Launch** | "Deploy / go live / launch / put it on my domain" | `docs/website-launch.md` |

If a site already exists but there's no brief, run a short Plan that reads the code first and only asks what the code can't answer.

## Experience level

Before the first real question, ask once: *"How much have you built before — new to this, built a few things, or experienced?"* Then adapt for the whole session:

- **New** — explain every technical term in plain English on first use (e.g. *"sitemap (a file that lists every page on your site so search engines can find them)"*). One question at a time. More 🧑 steps spelled out with exactly where to click.
- **Some** — explain only the less common terms. Group simple questions.
- **Experienced** — terse and decisions-first. Lead with the recommended default and let them override it. Skip explanations unless asked.

If the user's answers show a different level than they chose, adjust quietly.

## 1. Plan — the interview

Read the repo first. Anything the code already answers, state back and confirm rather than ask. Ask one question at a time (grouped for experienced users), give one sentence of context on why it matters, and offer a recommended default.

1. **The job.** What kind of site is it (marketing, content/blog, docs, local business, portfolio), what should it do, in one sentence, and who is it for?
2. **The one conversion goal.** What single action should a visitor take: sign up, buy, book, enquire, subscribe? Everything else is secondary. This decides the main call to action on every page and the one event analytics must track.
3. **Audience, keywords and locales.** What would the ideal visitor type into Google just before they need this? Collect 3–5 real phrasings for each important page, in the user's customers' words, not the user's jargon. Ask which countries and languages matter. Default: one language and one locale (e.g. `en-GB`).
4. **Pages and structure.** Turn the phrasings into a site map. One page per distinct search intent; don't make two pages compete for the same phrase. For each page: URL, purpose, target phrase, and the structured data type it needs (see `REFERENCE.md`). Keep URLs short, lowercase and descriptive. Default pages: home, one page per offer or service, about, contact, plus legal pages; add a blog only if someone will write for it at least monthly.
5. **Content and who edits it.** Who writes the words, and who will change them after launch? Default: MDX files in the repo (fast, free, versioned). If non-developers will edit regularly, use Sanity (hosted editor, nothing to run). Use Payload instead only when they want the CMS inside the same Next.js app and their own database. Ask whether real copy exists; the site can't rank on placeholder text.
6. **Brand and design.** Is there a `DESIGN.md`, brand guide, logo and colours, or a reference site they like? If there's a `DESIGN.md`, it's the source of truth for tokens. If there's nothing, ask for one reference site and build a clean, readable default from it.
7. **Integrations.** Forms (default: a Server Action that emails the enquiry), email capture (their existing email tool), CMS, analytics (default: Vercel Web Analytics, which needs no cookie banner; GA4 only if they need it, and then a consent banner in the UK and EU), booking or payments links.
8. **Domain and hosting.** Do they own a domain already, and where is it registered? Default host: Vercel. Recommend Cloudflare (via OpenNext) instead only if they already run their DNS on Cloudflare and want it all in one place, or need a free plan for a commercial site.
9. **An existing site?** If this replaces a live site, get its full URL list (from its sitemap, or Search Console's Pages report). Every old URL that changes needs a permanent redirect to its closest new page, or the rankings it has earned are lost.

Close the interview by playing back the whole plan in one compact block and getting a clear yes. Then write `docs/website-brief.md`:

```markdown
# Website brief: <site name>
> Experience level: <new|some|experienced> · Last updated: <date>

## Job
<site type> — <one sentence> — for <who>

## Conversion goal
<the one action> · Tracked as: <analytics event name>

## Audience, keywords and locales
Audience: <who, in a sentence>
Locales: <e.g. en-GB only>

## Site map
| URL | Page | Purpose | Target search phrase | Other phrasings | Structured data |
|---|---|---|---|---|---|

## Content
Source: <MDX in repo / Sanity / Payload> · Edited by: <who> · Real copy: <ready / being written / needed for: …>

## Design
<DESIGN.md / brand guide / reference site URL — and what to take from it>

## Integrations
<forms, email capture, analytics, booking, CMS — or "None">

## Domain and hosting
Domain: <domain or "to buy"> · Registrar: <…> · Host: <Vercel / Cloudflare>

## Redirects from the old site
| Old URL | New URL |
|---|---|
<or "New site — none">

## Decisions and reasons
- <decision> — <why>
```

## 2. Build

Read `REFERENCE.md` before writing any site code. Then let the user steer: build what they ask for, in the order they choose, keeping the brief as the source of truth. If a decision changes, update the brief first.

If the user has no preference, recommend this order, one step per working session, so there's something to look at early:

1. Project setup, design tokens from `DESIGN.md` (or the reference site), fonts, and the SEO foundation (below).
2. Root layout: header, navigation, footer, and the main call to action.
3. Home page.
4. The offer, service or product pages, in order of business value.
5. The conversion path end to end: form, booking or checkout link, success state, analytics event.
6. About, contact and legal pages.
7. Blog or docs, with its index, post template and share images, if the brief has one.
8. Redirects from the old site, if there is one.

While building:

- Use the project's own docs for API detail. Next.js writes an `AGENTS.md` that points to the version-matched docs in `node_modules/next/dist/docs/`. Read the relevant guide there before using any Next.js API you aren't certain of. The framework moves fast and older patterns in training data are often wrong.
- Lay the SEO foundation before the pages: root layout metadata with `metadataBase` and a title template, `app/sitemap.ts`, `app/robots.ts`, a custom not-found page, a default social share image, and Organization and WebSite structured data. Every page built after that inherits it.
- Build each page from its brief row: one `h1` that matches the target phrase's intent, a unique title and description, a canonical URL, the right structured data, internal links to related pages, and a clear route to the conversion goal.
- Mark any placeholder copy with `TODO:` so the Check catches it. Never invent testimonials, reviews, client logos, statistics or prices.
- After each page, run the production build and look at the rendered HTML (view source or `curl`), not just the browser. Confirm the title, description, canonical, single `h1` and JSON-LD are in the initial HTML. Then look at it at phone width.

## 3. Check

Read `CHECKLIST.md` and audit the actual site against every item. Run a production build (`next build` then `next start`) and check the real output, with the commands and tools the checklist names, rather than reading the code and guessing. Use these tools, in this order:

- **Rendered HTML** — `curl -s` each key URL and read the `<head>`, headings and JSON-LD.
- **Lighthouse** — mobile, against the production build (`npx lighthouse <url> --view`, which tests as mobile by default, or Chrome DevTools).
- **Rich Results Test** and **Schema Markup Validator** — once there's a public preview URL.
- **A real phone** — the conversion path, start to finish.

Report in chat:

- A one-line verdict (e.g. *"Ready to launch"*, or *"4 must-fix items before launch"*).
- **Must** failures first, then **should** failures. Each with what's wrong, where (file:line or URL), and a fix. Phrase fixes for new users as a ready-to-paste prompt.
- What passed, collapsed to one line.

Offer to fix the must-fix items now. Never mark an item as passing without checking it.

## 4. Launch

Read the actual codebase and brief to establish: what's on the site, where it will be hosted, what the domain situation is, which environment variables it needs, which integrations and analytics it uses, and what's missing for launch. Confirm the picture with the user in one short message, plus anything you genuinely can't tell (e.g. *"Do you already own the domain? Where did you buy it?"*).

Then read `LAUNCH.md` and write `docs/website-launch.md` from it, tailored to this site. Delete the phases and steps that don't apply (e.g. the cookie banner if there's no GA4, the CMS steps if content is MDX, Cloudflare if hosting on Vercel). Fill in real names, URLs, environment variable names and commands. If the Check found must-fix items, they become Phase 0.

Walk the user in. Don't just drop the file. Summarise in chat: number of steps, the 🧑 steps only they can do, any cost, and the first step. Offer to do the first 🤖 step now.

## Rules

- Recommend one path. Mention an alternative only when the user's situation clearly calls for it.
- Never put secrets in code, examples, or chat. Secrets go in `.env.local` (git-ignored) and the host's environment variables. Only values that are safe for anyone to see get the `NEXT_PUBLIC_` prefix.
- Never invent Next.js APIs, config options or file conventions. If unsure, read the bundled docs.
- Write for people first. No keyword stuffing, no thin pages made only to catch a search, no AI filler. Structured data must describe what's visible on the page, and must never claim reviews or ratings the site doesn't show.
- The site isn't launched until it's live on its real domain over HTTPS, the sitemap is submitted in Google Search Console, and the conversion goal works end to end on a real phone.

## What "done" looks like

- `docs/website-brief.md` describes the site, and the code matches it.
- The production build passes, every [must] item in `CHECKLIST.md` passes, and Lighthouse on mobile scores 90+ for Performance, Accessibility, Best Practices and SEO on the home page and the main conversion page.
- `docs/website-launch.md` exists, tailored to this site, and the user knows their first step.

Next step after launch: check Search Console after two to four weeks for pages that aren't indexed and the phrases people actually find the site with, and feed those back into the brief. Re-run the Check after every significant change.
