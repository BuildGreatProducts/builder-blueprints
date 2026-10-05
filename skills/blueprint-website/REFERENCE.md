# Website — Reference

> Last verified: 2026-10. Next.js moves quickly. Before relying on an API, config option or file convention, read the version-matched docs bundled with the project in `node_modules/next/dist/docs/` (the project's `AGENTS.md` points there), or https://nextjs.org/docs. For search guidance: https://developers.google.com/search/docs.
>
> Versions at last check: Next.js 16.3 (latest patch 16.3.8; 16.x is Active LTS) · React 19.3 · Node.js 20.9 or later · Tailwind CSS 4.3 · shadcn CLI v4 · Payload 3.x (4.0 in canary) · TypeScript 5.x or 7 (16.3 can type-check with TypeScript 7) · `@opennextjs/cloudflare` 1.x.

## Contents
1. Default approach
2. Project layout
3. Using the bundled docs
4. Metadata
5. Crawling and indexing
6. Structured data (JSON-LD)
7. Social share images
8. Performance and Core Web Vitals
9. Page structure and on-page SEO
10. Content: MDX and CMS
11. Rendering and caching
12. International sites
13. AI search
14. Hosting
15. Analytics, forms and privacy
16. Patterns to avoid

---

## 1. Default approach

- **Next.js App Router, TypeScript, Turbopack.** Turbopack is the default for `next dev` and `next build`; no flag needed.
- **Tailwind CSS v4 + shadcn/ui.** Tailwind v4 is configured in CSS (`@import "tailwindcss";` and `@theme` in `globals.css`); there is no `tailwind.config.js`. shadcn/ui components are copied into the repo, so they're yours to edit.
- **Static by default.** A website's pages should be prerendered at build time. Only reach for request-time rendering when a page genuinely changes per visitor.
- **Content in the repo** as MDX unless non-developers edit regularly (then Sanity; Payload if they want the CMS inside the app).
- **Vercel** for hosting. Cloudflare Workers via OpenNext as the alternative.
- **SEO is built in from the first commit,** not added at the end: metadata, sitemap, robots, structured data and performance budgets come before the second page.

Start a new project with:

```
npx create-next-app@latest <name> --yes
npx shadcn@latest init
```

`--yes` accepts the recommended defaults (TypeScript, Tailwind, App Router, Turbopack, `@/*` import alias). `create-next-app` also writes `AGENTS.md` and `CLAUDE.md`.

## 2. Project layout

```
app/
├── layout.tsx              # root layout: <html lang>, fonts, metadataBase, title template, Organization/WebSite JSON-LD
├── page.tsx                # home
├── not-found.tsx           # custom 404 with links back into the site
├── sitemap.ts
├── robots.ts
├── opengraph-image.tsx     # default share image (or opengraph-image.png)
├── icon.svg / apple-icon.png
├── (marketing)/            # route group: shared layout, no URL segment
│   ├── pricing/page.tsx
│   └── about/page.tsx
├── blog/
│   ├── page.tsx            # index
│   └── [slug]/
│       ├── page.tsx        # generateStaticParams + generateMetadata
│       └── opengraph-image.tsx
└── legal/privacy/page.tsx
components/                 # shadcn/ui in components/ui
content/                    # MDX posts, if content lives in the repo
lib/site.ts                 # site name, URL, social links — one source of truth
mdx-components.tsx          # required when using @next/mdx
next.config.ts              # redirects, images, MDX
```

Notes:
- Keep one `lib/site.ts` with the canonical site URL (from `NEXT_PUBLIC_SITE_URL`), name and default description. Metadata, sitemap, robots and JSON-LD all read from it.
- Route groups `(name)` organise files without changing URLs.
- `proxy.ts` (the v16 replacement for `middleware.ts`) is rarely needed on a website. Prefer `redirects()` in `next.config.ts`. If you must use it, it runs on the Node.js runtime and the codemod `npx @next/codemod@canary middleware-to-proxy .` migrates old files.

## 3. Using the bundled docs

- Every install of `next` ships its docs in `node_modules/next/dist/docs/` (`01-app/` holds getting started, guides and API reference).
- `create-next-app` writes `AGENTS.md` (and a `CLAUDE.md` that imports it). On existing projects, `next dev` writes or updates a managed block in `AGENTS.md` when it detects a coding agent. Commit it. Put your own project instructions outside the `<!-- BEGIN:nextjs-agent-rules -->` / `<!-- END:nextjs-agent-rules -->` markers.
- Opting out (`agentRules: false` in `next.config.ts`) is not recommended.
- When an error message includes a `Learn more` link to `nextjs.org/docs/messages/...`, read it; those pages are written for agents.

## 4. Metadata

Set the defaults once in the root layout. Every page then sets its own `title`, `description` and canonical.

```tsx
// app/layout.tsx
import type { Metadata } from 'next'
import { site } from '@/lib/site'

export const metadata: Metadata = {
  metadataBase: new URL(site.url),            // makes relative URLs absolute
  title: { default: site.name, template: `%s | ${site.name}` },
  description: site.description,
  alternates: { canonical: '/' },
  openGraph: { type: 'website', siteName: site.name, locale: 'en_GB' },
  twitter: { card: 'summary_large_image' },
}
```

```tsx
// app/blog/[slug]/page.tsx
export async function generateMetadata(
  { params }: { params: Promise<{ slug: string }> }
): Promise<Metadata> {
  const { slug } = await params
  const post = await getPost(slug)
  return {
    title: post.title,
    description: post.summary,
    alternates: { canonical: `/blog/${slug}` },
    openGraph: { type: 'article', publishedTime: post.date },
  }
}
```

- `params` and `searchParams` are Promises. Await them.
- `title.template` applies to child segments, not the segment it's defined in, and needs a `default`. Use `title: { absolute: '…' }` for the home page if it shouldn't get the suffix.
- Titles: unique, about 50–60 characters, target phrase near the front. Descriptions: unique, about 140–160 characters, written to earn the click.
- Every indexable page sets `alternates.canonical` to its own clean URL. Never point every page's canonical at the home page.
- `robots: { index: false }` on pages that shouldn't be in search (thank-you pages, internal tools).
- A relative URL in metadata without `metadataBase` is a build error.
- `generateMetadata` may stream after the page for real browsers; Next.js detects HTML-limited bots and blocks for them, so crawlers get metadata in the `<head>`. Leave `htmlLimitedBots` alone.

## 5. Crawling and indexing

**Sitemap** — `app/sitemap.ts`, generated from the same source as the pages so it can't drift:

```ts
import type { MetadataRoute } from 'next'
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const posts = await getAllPosts()
  return [
    { url: `${site.url}/`, lastModified: new Date() },
    ...posts.map((p) => ({ url: `${site.url}/blog/${p.slug}`, lastModified: p.updated })),
  ]
}
```

- Include only canonical, indexable, 200-status URLs. Use real `lastModified` dates; Google ignores `changeFrequency` and `priority`.
- Over 50,000 URLs: split with `generateSitemaps` (its `id` prop is a Promise in v16).

**Robots** — `app/robots.ts`:

```ts
import type { MetadataRoute } from 'next'
export default function robots(): MetadataRoute.Robots {
  const isProd = process.env.VERCEL_ENV === 'production' // or your own SITE_ENV on other hosts
  return isProd
    ? { rules: { userAgent: '*', allow: '/' }, sitemap: `${site.url}/sitemap.xml` }
    : { rules: { userAgent: '*', disallow: '/' } }
}
```

- Keep preview and staging deployments out of search. Never ship `disallow: '/'` to production.
- `robots.txt` controls crawling, not indexing. Use `noindex` metadata to keep a page out of results.

**Redirects** — permanent (308, treated like 301 by Google) in `next.config.ts`:

```ts
async redirects() {
  return [{ source: '/old-page', destination: '/new-page', permanent: true }]
}
```

- Redirect every URL that changes, old site URLs included. Avoid chains (A → B → C).
- Pick one host (`www` or apex) and redirect the other at the host's domain settings.

**Not found** — `app/not-found.tsx` with the site's navigation, a search or key links, and the conversion goal. Call `notFound()` for missing slugs so they return a real 404, not a 200.

## 6. Structured data (JSON-LD)

Render JSON-LD as a plain `<script>` tag in the layout or page (not `next/script`), with `<` escaped to prevent script injection. Type it with `schema-dts`.

```tsx
import type { WithContext, Organization } from 'schema-dts'

export function JsonLd<T>({ data }: { data: WithContext<T> }) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data).replace(/</g, '\\u003c') }}
    />
  )
}
```

Which types to use:

| Page | Type |
|---|---|
| Root layout | `Organization` (name, url, logo, sameAs) and `WebSite` (name, url) |
| Local business home or contact | `LocalBusiness` (or a subtype), with address, phone, opening hours |
| Blog post or article | `Article` / `BlogPosting` (headline, datePublished, dateModified, author, image) |
| Product or plan page | `Product` with `Offer` (price, currency, availability) |
| Any page below the top level | `BreadcrumbList` |
| A page with a visible FAQ | `FAQPage` (helps other tools; Google now shows FAQ rich results only for a few authoritative sites) |

- Mark up only what's visible on the page. No invented reviews, ratings or prices.
- Validate with the Rich Results Test (https://search.google.com/test/rich-results) and the Schema Markup Validator (https://validator.schema.org).

## 7. Social share images

- Add `app/opengraph-image.tsx` (or a static `opengraph-image.png`) for the default, and one per section or post where it adds value. Next.js adds the `og:image` tags.
- Generate with `ImageResponse` from `next/og`. Export `alt`, `size = { width: 1200, height: 630 }` and `contentType = 'image/png'`. `params` is a Promise.
- Load fonts and logos from the file system at module scope (`readFile`), not over the network.
- `twitter-image` uses the same convention; with `twitter.card: 'summary_large_image'` the Open Graph image is used if there's no separate one.
- Size limits: `opengraph-image` 8 MB, `twitter-image` 5 MB (the build fails above them).

## 8. Performance and Core Web Vitals

Targets (75th percentile of real visits): **LCP** ≤ 2.5 s, **INP** ≤ 200 ms, **CLS** ≤ 0.1.

- **Images** — always `next/image` with `width`/`height` (or `fill` inside a sized box) and a real `sizes` attribute for responsive images. On the single LCP image (usually the hero) set `loading="eager"` and `fetchPriority="high"`. The `priority` prop is deprecated in v16; `preload` exists but use it only when one image is always the LCP element, and not together with `loading` or `fetchPriority`. Write descriptive `alt` text; use `alt=""` for decorative images.
- **Image config** — v16 defaults `images.qualities` to `[75]`; add other values explicitly. Allow remote images with `images.remotePatterns`.
- **Fonts** — `next/font/google` or `next/font/local`. Self-hosted, no layout shift. At most two families; prefer variable fonts. Apply via a CSS variable in the root layout.
- **JavaScript** — Server Components by default. Add `'use client'` only to the small interactive leaf that needs it, never to a whole page or layout.
- **Third-party scripts** — `next/script` with `strategy="afterInteractive"` or `"lazyOnload"`. Chat widgets and embeds load on interaction. Every script must earn its place.
- **Video** — never autoplay a large video as the hero LCP; use a poster image.
- **Measure** — Lighthouse in Chrome DevTools (mobile), PageSpeed Insights once deployed, Vercel Speed Insights for real-user data.

## 9. Page structure and on-page SEO

- **One `h1` per page**, matching the page's search intent. Headings in order (`h2` under `h1`, `h3` under `h2`), never chosen for size.
- **Semantic HTML** — `header`, `nav`, `main`, `article`, `section`, `footer`; real `<a href>` links (via `next/link`) and `<button>`s. Content in the initial HTML, not loaded after a click.
- **`<html lang="en-GB">`** (or the right locale) in the root layout.
- **URLs** — short, lowercase, hyphenated, descriptive (`/services/kitchen-fitting`, not `/page?id=7`). Pick a trailing-slash rule and stick to it (default: none).
- **Internal links** — every page reachable within three clicks of the home page; related pages link to each other with descriptive anchor text ("see our kitchen fitting prices", not "click here"). No orphan pages.
- **Content** — answer the search fully, in the visitor's language, with something only this business can say: real prices, photos, examples, process, opinions. Show who's behind it (an About page, author names and bios on articles).
- **Accessibility** — colour contrast at least 4.5:1 for body text, visible focus states, labelled form fields, keyboard navigable. Accessibility and SEO reward the same things.
- **Conversion** — the main call to action is visible without scrolling on mobile and repeated at the end of long pages.

## 10. Content: MDX and CMS

**MDX in the repo (default)**
- Packages: `@next/mdx @mdx-js/loader @mdx-js/react @types/mdx`. Wrap the config with `createMDX`, add `md`/`mdx` to `pageExtensions`, and create `mdx-components.tsx` at the project root (required).
- Store posts in `content/` and render them from `app/blog/[slug]/page.tsx` with `generateStaticParams` and `export const dynamicParams = false` so unknown slugs 404.
- `@next/mdx` doesn't parse frontmatter. Export a `metadata` object from each MDX file, or add `remark-frontmatter` + `remark-mdx-frontmatter`.
- With Turbopack, pass remark/rehype plugins by name as strings (e.g. `'remark-gfm'`) with serialisable options only.
- Style long-form content with `@tailwindcss/typography` (`prose`).

**Sanity (when non-developers edit)**
- Hosted editor and content store; use the official `next-sanity` toolkit. Fetch content in Server Components, tag it, and have a Sanity webhook call a Route Handler that runs `revalidateTag(tag, 'max')` so edits go live without a redeploy. Protect the webhook with a secret.
- Give editors fields for SEO title, description, slug and share image, with sensible fallbacks.

**Payload (when they want the CMS inside the app)**
- Installs into the same Next.js app (admin at `/admin`) and needs a database (Postgres, MongoDB or SQLite). Use the official website template as the starting point. Same revalidation pattern via Payload hooks.

## 11. Rendering and caching

- Pages with no request-time APIs (`cookies()`, `headers()`, uncached fetches, `searchParams`) are prerendered at build time. Keep marketing and content pages that way.
- Dynamic routes with known slugs: `generateStaticParams`.
- CMS content: tag fetches (`fetch(url, { next: { tags: ['posts'] } })`) and revalidate on publish with `revalidateTag('posts', 'max')`. The one-argument form is deprecated.
- **Cache Components** (`cacheComponents: true` in `next.config.ts`, with the `'use cache'` directive, `cacheLife` and `cacheTag`) is opt-in. It replaces the old experimental PPR flag and enables Instant Navigations (with `partialPrefetching: true`). Default for a website: leave it off. Turn it on when the site mixes static pages with per-visitor content, and adopt it with the Next.js `next-cache-components-adoption` skill (`npx skills add vercel/next.js --skill next-cache-components-adoption`).

## 12. International sites

- Only if the brief lists more than one locale. Use a root `[lang]` segment (`app/[lang]/...`); in 16.3, read it anywhere in Server Components with `import { lang } from 'next/root-params'`.
- Every page sets `alternates.languages` (hreflang) for all its translations plus `x-default`, and its own canonical. Add the same `alternates.languages` to sitemap entries.
- Translate the URL slugs and metadata, not just the body. Never auto-redirect by IP; offer a language switcher.

## 13. AI search

- Google's guidance (Search Central, "Optimizing your website for generative AI features on Google Search", 2026): AI Overviews and AI Mode draw on the normal Google index. You don't need special AI files, markup or Markdown copies, and you shouldn't chop content into small chunks. Unique, useful content from real expertise matters most; classic SEO is AI search SEO.
- Structured data isn't required for AI features but still helps rich results.
- `llms.txt` is optional. Google doesn't use it; some other AI tools do. If you add it, generate `app/llms.txt/route.ts` from the same source as the sitemap so it stays accurate. Cheap, but not a priority.
- Don't block AI crawlers in `robots.ts` unless the user decides to. `Google-Extended` controls use for Gemini training, not inclusion in Search.

## 14. Hosting

**Vercel (default)**
- Import the GitHub repo; every push to `main` deploys to production and every branch gets a preview URL. Set environment variables per environment in Project → Settings → Environment Variables.
- Hobby is free but for personal, non-commercial use only. A business site needs Pro ($20 per month per developer seat).
- Add the domain in Project → Settings → Domains; Vercel issues HTTPS automatically and offers to redirect `www` to apex (or the reverse).

**Cloudflare Workers (alternative)**
- Uses the OpenNext adapter: `npm i @opennextjs/cloudflare@latest` and `npm i -D wrangler@latest`, a `wrangler.jsonc` with the `nodejs_compat` flag and `main: ".open-next/worker.js"`, an `open-next.config.ts`, and `preview`/`deploy` scripts. `npm run preview` tests in the Workers runtime; `npm run deploy` ships it.
- Uses the Node.js runtime, not Edge. `proxy.ts` support is still maturing on this adapter; keep redirects in `next.config.ts`.
- Worker size limits: 3 MiB compressed on the free plan, 10 MiB on paid.
- Cloudflare also promotes `vinext`, a Vite-based reimplementation of the Next.js API. It isn't Next.js; don't use it for this blueprint.
- Next.js 16.2 made the Adapter API stable; first-party adapters for Cloudflare and others are being built on it. Check the current Cloudflare docs before setting up.

## 15. Analytics, forms and privacy

- **Analytics** — default to Vercel Web Analytics (`@vercel/analytics`, `<Analytics />` in the root layout) plus Speed Insights (`@vercel/speed-insights`). Both are cookieless. On Cloudflare, use Plausible. Track the conversion goal as a custom event.
- **GA4** — only if the user needs it. Load it with `@next/third-parties/google` (`<GoogleAnalytics gaId=… />`). In the UK and EU it sets cookies that need prior consent: add a consent banner with Google Consent Mode v2, defaulting to denied.
- **Forms** — a Server Action that validates input on the server (e.g. with Zod), sends the enquiry by email (e.g. Resend) and shows a clear success state. Add a honeypot field and rate limiting against spam. Redirect to a `noindex` thank-you page, or fire the conversion event on success.
- **Legal** — a privacy policy (what's collected, by which tools, why, and how to get in touch) linked from the footer and from any form; a cookie policy if cookies need consent; terms if selling. UK limited companies must show their registered name, number and office address.
- **Secrets** — in `.env.local` locally and the host's environment variables in production. Only `NEXT_PUBLIC_` values reach the browser.

## 16. Patterns to avoid

- `middleware.ts` (renamed `proxy.ts` in v16), and redirects done in `proxy.ts` that `next.config.ts` could do.
- `<Image priority>` (deprecated in v16), raw `<img>` for content images, missing `sizes`, and lazy-loading the hero image.
- `'use client'` at the top of pages or layouts; whole pages rendered client-side so content isn't in the initial HTML.
- Duplicate titles and descriptions, the same canonical on every page, and canonicals pointing to redirecting or 404 URLs.
- Shipping `disallow: '/'` or `noindex` to production (often left over from staging).
- JSON-LD rendered with `next/script`, without escaping `<`, or describing content that isn't on the page. Fake reviews or `AggregateRating`.
- Keyword stuffing, near-duplicate location or service pages, and AI-written filler. Placeholder or lorem ipsum copy at launch.
- Multiple `h1`s, headings chosen for size, and "click here" links.
- Hard-coded `http://localhost` or preview URLs in metadata, sitemap or JSON-LD. Always build URLs from `metadataBase` / `NEXT_PUBLIC_SITE_URL`.
- Hosting a commercial site on Vercel Hobby.
- Loading GA4 or other tracking before consent in the UK and EU.
- Chasing `llms.txt`, "AI chunking" or other GEO tricks instead of better content.
- Copying API patterns from memory (e.g. synchronous `params`, one-argument `revalidateTag`) instead of reading the bundled docs.
