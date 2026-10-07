# Website — Checklist

Audit the real site against every item. **[must]** blocks launch. **[should]** is strongly recommended. Each item says how to verify it. Run a production build (`next build` then `next start`), run the command or read the output; never assume a pass.

## Build and code
- [ ] **[must]** `next build` completes with no errors and no type errors. *Verify: run it.*
- [ ] **[must]** No secrets in the repo or its git history; `.env*.local` is git-ignored; only browser-safe values use `NEXT_PUBLIC_`. *Verify: `git grep -nE "(sk_|api[_-]?key|secret|token|password)"` and review the hits; read `.gitignore`.*
- [ ] **[must]** Every environment variable the code reads is listed in `.env.example` with a comment. *Verify: `grep -rn "process.env\." app lib components` and compare.*
- [ ] **[should]** No `middleware.ts` (the current convention is `proxy.ts`), and no `proxy.ts` doing work `next.config.ts` redirects could do. *Verify: `ls`, read the file if present.*
- [ ] **[must]** Cache Components is on (`cacheComponents: true`, `partialPrefetching: true`) and no route exports `dynamic`, `revalidate`, `fetchCache` or `dynamicParams`. *Verify: read `next.config.ts`; `grep -rnE "export const (dynamic|revalidate|fetchCache|dynamicParams)\b" app`.*
- [ ] **[should]** The root layout exports `ensureStatic = 'navigation'`, or the brief records which route needs request-time rendering and why. *Verify: read `app/layout.tsx`; `next build` passes with it in place.*
- [ ] **[should]** `'use client'` appears only in small interactive components, never at the top of a `page.tsx` or `layout.tsx`. *Verify: `grep -rln "use client" app`.*

## Metadata
- [ ] **[must]** The root layout sets `metadataBase` from the production URL (not localhost or a preview URL) and a `title` template with a default. *Verify: read `app/layout.tsx` and `lib/site.ts`.*
- [ ] **[must]** Every indexable page has a unique `<title>` and meta description in the initial HTML. *Verify: `curl -s <url> | grep -E "<title>|name=\"description\""` for each page in the brief's site map; compare for duplicates.*
- [ ] **[must]** Every indexable page has a self-referencing canonical with the clean production URL. *Verify: `curl -s <url> | grep canonical` for each page.*
- [ ] **[must]** `<html lang>` is set to the brief's locale. *Verify: view source.*
- [ ] **[should]** Titles are about 50–60 characters with the target phrase near the start; descriptions about 140–160 characters. *Verify: measure with a quick script over the curl output.*
- [ ] **[should]** Pages that shouldn't be found in search (thank-you, internal) are `noindex`. *Verify: curl them and look for `name="robots"`.*

## Crawling and indexing
- [ ] **[must]** `/robots.txt` allows crawling in production and lists the sitemap URL; preview and staging builds disallow it. *Verify: curl `/robots.txt` on the production build with the production env, and on a preview.*
- [ ] **[must]** `/sitemap.xml` lists every indexable page in the brief with absolute production URLs, and nothing that redirects, 404s or is `noindex`. *Verify: curl it and compare with the site map; spot-check status codes with `curl -sI`.*
- [ ] **[must]** Unknown URLs return a real 404 status with the custom not-found page, including unknown blog slugs. *Verify: `curl -sI <site>/does-not-exist` and `<site>/blog/does-not-exist`.*
- [ ] **[must]** If this replaces an old site, every old URL in the brief permanently redirects (308/301) to its new page in a single hop. *Verify: `curl -sI <old-path>` for each row in the brief's redirect table.*
- [ ] **[should]** One trailing-slash rule, and one host (`www` or apex), with the other redirecting. *Verify: curl both variants once deployed.*

## Structured data and sharing
- [ ] **[must]** JSON-LD is rendered in a plain `<script type="application/ld+json">` with `<` escaped, and parses as valid JSON. *Verify: grep for `application/ld+json` in the code and check the `.replace(/</g, '\\u003c')`; extract and `JSON.parse` it from the curl output.*
- [ ] **[must]** Structured data describes only what's visible on the page, with no invented reviews, ratings or prices. *Verify: compare each JSON-LD block with the page.*
- [ ] **[should]** Organization and WebSite on the root layout, plus the type each page's brief row names (Article, Product, LocalBusiness, BreadcrumbList, FAQPage). *Verify: curl each page; run the Rich Results Test on a preview URL.*
- [ ] **[should]** Every page has an Open Graph image at 1200×630 with alt text, and `og:title`/`og:description`. *Verify: curl for `og:image`; paste the preview URL into a link preview checker such as opengraph.xyz.*

## Performance
- [ ] **[must]** Lighthouse on mobile scores 90+ for Performance, Accessibility, Best Practices and SEO on the home page and the main conversion page. *Verify: `npx lighthouse <url> --view` against the production build.*
- [ ] **[must]** All content images use `next/image` with `alt` text; the LCP image uses `loading="eager"` and `fetchPriority="high"`; nothing uses the deprecated `priority` prop. *Verify: `grep -rn "<img\|priority" app components`; check the Lighthouse LCP element.*
- [ ] **[should]** Lab Core Web Vitals within budget: LCP ≤ 2.5 s, CLS ≤ 0.1, Total Blocking Time low (INP is measured on real visits after launch). *Verify: Lighthouse report.*
- [ ] **[should]** Responsive images have a `sizes` attribute that matches the layout. *Verify: grep `fill` and full-width `Image` usages for `sizes`.*
- [ ] **[should]** Fonts load through `next/font`, at most two families. *Verify: read `app/layout.tsx`; grep for `fonts.googleapis.com` (should be absent).*
- [ ] **[should]** Third-party scripts load through `next/script` with a non-blocking strategy, and each has a reason in the brief. *Verify: `grep -rn "<script\|next/script" app components`.*

## Content and structure
- [ ] **[must]** No placeholder copy: no `TODO:`, lorem ipsum, "Your company", or example.com in rendered pages. *Verify: `grep -rniE "TODO:|lorem|ipsum|example\.com|your company" app content components`.*
- [ ] **[must]** Exactly one `h1` per page, matching the page's target search intent; headings in order. *Verify: curl each page and count `<h1`; read the heading outline.*
- [ ] **[must]** The conversion goal works end to end: the form submits, the user sees success, the owner receives it, and the analytics event fires. *Verify: submit it on the production build and check the inbox and the analytics dashboard or network tab.*
- [ ] **[should]** Every page is linked from at least one other page with descriptive anchor text, and is within three clicks of home. *Verify: compare the site map with links in the nav, footer and body.*
- [ ] **[should]** URLs are short, lowercase, hyphenated and descriptive. *Verify: read the site map.*
- [ ] **[should]** Text contrast is at least 4.5:1, focus states are visible, and form fields have labels. *Verify: Lighthouse Accessibility audit; tab through the home page.*

## Privacy and legal
- [ ] **[must]** A privacy policy is linked from the footer and from every form, and names the tools that collect data. *Verify: read it and the footer.*
- [ ] **[must]** If GA4 or any cookie-setting tracker is used for UK or EU visitors, nothing loads before consent, and the banner offers reject as easily as accept. *Verify: load the page in a private window and watch the network tab before clicking the banner.*
- [ ] **[should]** Forms validate on the server and have spam protection (honeypot or rate limit). *Verify: read the Server Action; submit an empty and an invalid form.*
- [ ] **[should]** UK limited companies show their registered name, number and office address. *Verify: read the footer or legal page.*

## AI search
- [ ] **[should]** `robots.ts` doesn't block search or AI crawlers unless the brief records that decision. *Verify: read `/robots.txt`.*
- [ ] **[should]** If `llms.txt` exists, it's generated from the same source as the sitemap and lists only live, canonical pages. *Verify: curl `/llms.txt` and compare.*
