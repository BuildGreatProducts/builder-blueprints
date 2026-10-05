# Launch guide template — Website

Use this template to write `docs/website-launch.md`. Tailor it to what was actually built: fill in real names, URLs, environment variable names and commands, and delete phases or steps that don't apply (keep either the Vercel or the Cloudflare steps, not both). Keep the legend and the step format.

**Every step has:**
- a checkbox
- a 🧑/🤖/🤝 marker
- a time estimate (and the cost, if any)
- plain-English instructions, with technical terms explained on first use when the user is new
- a ready-to-paste prompt in a quote block for 🤖 steps
- a **You'll know it worked when…** line

---

```markdown
# Launch guide: <site name>

**What you're launching:** <one sentence — what the site is, its conversion goal, and where it will live (e.g. https://example.co.uk on Vercel)>
**Estimated total time:** <x hours, plus up to 48 hours for DNS to spread> · **Cost:** <domain ~£10–15/year if not owned · Vercel Pro $20/month for a business site (Hobby is non-commercial only) or Cloudflare Workers free plan · paid analytics if chosen>

**Legend**
- 🧑 **You** — needs your accounts, identity or a decision.
- 🤖 **Agent** — paste the prompt into your coding agent.
- 🤝 **Together** — the agent prepares it, you click the final button.

## Phase 0 — Fix blockers (only if the checklist found must-fix items)
- [ ] 🤖 <blocker> — <time>
  > <ready-to-paste prompt>
  You'll know it worked when: <…>

## Phase 1 — Final checks
- [ ] 🤖 Run the production build and the pre-launch checklist — 20 min
  > Run `next build` and fix anything it reports. Then start the production build with `next start` and audit it against the blueprint-website CHECKLIST.md, listing any [must] failures with a fix for each.
  You'll know it worked when: the build passes and there are no [must] failures.
- [ ] 🧑 Read every page once, as a customer — 30 min
  Open each page at phone width. Look for placeholder words, wrong prices, broken images and anything you wouldn't say to a customer's face.
  You'll know it worked when: you'd be happy for your best customer to see every page.
- [ ] 🤖 List the environment variables production needs — 5 min
  > List every environment variable the site reads, which ones are secret, and which must be set in production. Make sure `.env.example` matches, with no real values in it.
  You'll know it worked when: you have a short list of names to copy into the host.

## Phase 2 — Put it on GitHub
- [ ] 🧑 Create the repository — 5 min
  On github.com, choose New repository, name it `<repo>`, and set it to Private. Don't add a README; you already have one.
  You'll know it worked when: you can see the empty repo page.
- [ ] 🤝 Push the code — 5 min
  > Add the GitHub remote <url> and push the main branch.
  You'll know it worked when: your files show on GitHub.

## Phase 3 — Deploy (Vercel)
- [ ] 🧑 Import the project into Vercel — 10 min · $20/month on Pro for a business site
  Sign in at vercel.com with GitHub, choose Add New → Project, pick `<repo>`, and leave the detected Next.js settings alone. Before clicking Deploy, open Environment Variables and add each one from Phase 1 (including `NEXT_PUBLIC_SITE_URL=https://<domain>`).
  You'll know it worked when: Vercel shows "Ready" and a `.vercel.app` link that opens your site.
- [ ] 🧑 Turn on Web Analytics and Speed Insights — 5 min
  In the project, open the Analytics tab and click Enable, then do the same on the Speed Insights tab.
- [ ] 🤖 Add the analytics components — 10 min
  > Install `@vercel/analytics` and `@vercel/speed-insights`, add `<Analytics />` and `<SpeedInsights />` to the root layout, and track a custom event named `<event>` when <the conversion goal> succeeds. Commit and push.
  You'll know it worked when: visits and the `<event>` event appear in the Analytics tab a few minutes after you test it.

## Phase 3 — Deploy (Cloudflare, instead of Vercel)
- [ ] 🤖 Add the OpenNext adapter — 20 min
  > Set this Next.js app up for Cloudflare Workers with @opennextjs/cloudflare, following the current guide at https://opennext.js.org/cloudflare: install the packages, add wrangler.jsonc (with nodejs_compat) and open-next.config.ts, add the preview and deploy scripts, and run `npm run preview` to check every page works in the Workers runtime.
  You'll know it worked when: the preview runs locally and every page loads.
- [ ] 🧑 Connect the repo in Cloudflare — 15 min · free plan is fine for most sites
  In the Cloudflare dashboard, open Workers & Pages → Create → Import a repository, choose `<repo>`, and set the deploy command to `npm run deploy`. Add the environment variables from Phase 1 under Settings → Variables and Secrets (and the build variables under Builds).
  You'll know it worked when: the build succeeds and the `.workers.dev` link opens your site.
- [ ] 🧑 Set up Plausible analytics — 15 min · paid plan after the free trial
  Create an account at plausible.io, add `<domain>`, and create a goal for `<event>`.
- [ ] 🤖 Add the analytics script and goal — 10 min
  > Add the Plausible script for <domain> with next/script, and send a `<event>` custom event when <the conversion goal> succeeds. Commit and push.

## Phase 4 — Connect your domain
- [ ] 🧑 Buy the domain (only if you don't own one) — 10 min · ~£10–15/year
  Buy `<domain>` from a registrar such as Cloudflare Registrar, Namecheap or your host.
- [ ] 🤝 Point the domain at the site — 15 min, plus up to 48 hours to spread
  On Vercel: Project → Settings → Domains → Add `<domain>`, accept the offer to redirect `www` to it, then copy the DNS records Vercel shows into your registrar's DNS settings. On Cloudflare: Worker → Settings → Domains & Routes → Add → Custom domain (the domain must be on your Cloudflare account).
  You'll know it worked when: `https://<domain>` opens the site with a padlock, and `www.<domain>` redirects to it.
- [ ] 🤖 Confirm production URLs — 5 min
  > Check that NEXT_PUBLIC_SITE_URL is https://<domain> in production, then curl https://<domain>/robots.txt, /sitemap.xml and the home page's canonical and og:image tags, and confirm they all use https://<domain>, not a preview URL.
  You'll know it worked when: every URL in those files starts with `https://<domain>`.

## Phase 5 — Tell the search engines
- [ ] 🧑 Verify the site in Google Search Console — 15 min
  At search.google.com/search-console, add a **Domain** property for `<domain>` and add the TXT record it gives you at your DNS provider. Click Verify (it can take a few minutes).
  You'll know it worked when: Search Console says "Ownership verified".
- [ ] 🧑 Submit the sitemap — 2 min
  In Search Console, open Sitemaps, enter `sitemap.xml`, and click Submit.
  You'll know it worked when: the status shows "Success" with the number of pages you expect.
- [ ] 🧑 Request indexing for the key pages — 5 min
  Paste the home page and <main conversion page> into the URL Inspection bar at the top and click Request indexing.
- [ ] 🧑 (Optional) Add the site to Bing Webmaster Tools — 5 min
  At bing.com/webmasters, choose Import from Google Search Console. Bing also feeds several AI assistants.

## Phase 6 — Privacy (only if using GA4 or other cookie-setting tools)
- [ ] 🤖 Add a consent banner — 30 min
  > Add a cookie consent banner with Accept and Reject buttons of equal prominence. Load GA4 through @next/third-parties with the current version of Google Consent Mode, defaulting to denied, and only grant analytics storage after the visitor accepts. Link the banner to the privacy policy.
  You'll know it worked when: in a private window, no requests go to Google Analytics until you click Accept.

## Phase 7 — Smoke test the live site
- [ ] 🧑 Test the conversion goal on your phone — 10 min
  On mobile data, not Wi-Fi, open `https://<domain>`, go from the home page to <the conversion goal>, and complete it.
  You'll know it worked when: you see the success message, you receive the enquiry or sale, and the event shows in analytics.
- [ ] 🧑 Check speed on the live site — 5 min
  Run the home page and <main conversion page> through pagespeed.web.dev.
  You'll know it worked when: both score 90+ on mobile for Performance and SEO.
- [ ] 🧑 Check rich results and link previews — 10 min
  Paste a page with structured data into search.google.com/test/rich-results, and paste the home page link into a message to yourself (or opengraph.xyz).
  You'll know it worked when: the test shows no errors, and the link preview shows the right title, description and image.
- [ ] 🧑 Share it — post the link wherever your customers are, and ask two people to try the conversion path.

## After launch
- In two to four weeks, open Search Console: fix anything under Pages → "Why pages aren't indexed", and note which search phrases bring visitors. Add those to the brief.
- Watch Core Web Vitals (Search Console and Speed Insights) once real traffic arrives.
- Re-run the checklist after every significant change, and add a redirect whenever a URL changes.
- Publish useful, original content regularly; it's what gets a site found, in classic and AI search alike.
```
