# Launch guide template — Three.js Game

Use this template to write `docs/game-launch.md`. Tailor it to what was actually built: fill in real names, URLs and commands, and delete phases or steps that don't apply. Keep the legend and the step format.

**Every step has:**
- a checkbox
- a 🧑/🤖/🤝 marker
- a time estimate (and the cost, if any)
- plain-English instructions, with technical terms explained on first use when the user is new
- a ready-to-paste prompt in a quote block for 🤖 steps
- a **You'll know it worked when…** line

---

```markdown
# Launch guide: <game name>

**What you're launching:** <one sentence — what the game is, and which devices it plays on>
**Estimated total time:** <x hours> · **Cost:** <usually free: itch.io and Cloudflare Pages cost nothing at this scale; a custom domain is about £10/year if you want one>

**Legend**
- 🧑 **You** — needs your accounts, identity or a decision.
- 🤖 **Agent** — paste the prompt into your coding agent.
- 🤝 **Together** — the agent prepares it, you click the final button.

## Phase 0 — Fix blockers (only if the checklist found must-fix items)
- [ ] 🤖 <blocker> — <time>
  > <ready-to-paste prompt>
  You'll know it worked when: <…>

## Phase 1 — Final checks
- [ ] 🤖 Build and test the production version — 15 min
  > Run the asset build script, then `npm run build` and `npx vite preview`. Fix any errors. Confirm vite.config.ts has `base: './'` and that no code uses absolute asset paths. Tell me the size of dist/ and the URL to play the preview.
  You'll know it worked when: the preview plays from start screen to game-over with no errors in the browser console.
- [ ] 🧑 Play it on every target device — 30 min
  On your computer, and on a real phone if you support mobile (open the preview's network URL on the same Wi-Fi). Play to a win and to a game-over. Try switching tabs mid-game and rotating the phone.
  You'll know it worked when: it's smooth, the controls work, sound plays after you tap Play, and it pauses when you switch away.
- [ ] 🧑 Watch one other person play — 20 min
  Hand it to someone who hasn't seen it. Don't explain anything. Note where they get stuck.
  You'll know it worked when: they reach game-over without your help (or you've fixed what stopped them).
- [ ] 🤖 Check credits — 5 min
  > Compare CREDITS.md with every model, texture, sound and font in the project. List anything missing a source or licence, and add the credits to the menu or end screen.

## Phase 2 — Store page assets
- [ ] 🤖 Capture screenshots — 15 min
  > Add a dev-only key (F9) that saves a PNG of the canvas at 1920×1080 with the HUD hidden. Then tell me which five moments best show the game.
  You'll know it worked when: you have five sharp screenshots showing the core loop, not the menu.
- [ ] 🧑 Record a GIF and a short trailer — 45 min
  Record 30–60 seconds of real play with your screen recorder (on a Mac, Shift-Cmd-5). Start with the most exciting moment. Cut a 5–10 second loop for the GIF.
  You'll know it worked when: someone can tell what the game is from the GIF with no sound and no text.
- [ ] 🤖 Write the store text — 10 min
  > From docs/game-brief.md, write a store description for itch.io: a one-line hook, three short paragraphs (what you do, what makes it different, controls), a controls list for each device, and credits. Also write a short tagline of under 100 characters.
  You'll know it worked when: you'd click on it yourself.
- [ ] 🧑 Make a cover image — 20 min
  itch.io uses a 630×500 cover image. Use your best screenshot with the game's name on it.

## Phase 3 — Publish on itch.io
- [ ] 🤖 Package the game — 5 min
  > Run `npm run build`, then create `release/<game>-web.zip` containing the contents of dist/ (index.html at the root of the ZIP, not inside a folder). List the files and confirm it's under 500 MB and 1,000 files.
  You'll know it worked when: `unzip -l` shows `index.html` with no folder in front of it.
- [ ] 🧑 Create the itch.io project — 20 min
  Sign in at itch.io (free account), choose **Upload new project**, set **Kind of project** to **HTML**, upload the ZIP and tick **This file will be played in the browser**. Set the viewport size (e.g. 1280×720), tick **Mobile friendly** if you support phones, and tick **Fullscreen button**. Leave **SharedArrayBuffer support** off unless your agent says the build uses threads. Add the cover, screenshots, GIF, trailer link and text. Choose **No payments** or **Donations** (browser games on itch.io take donations, not fixed prices).
  You'll know it worked when: the draft page's preview plays the game.
- [ ] 🧑 Publish — 2 min
  Set visibility to **Public** and save.
  You'll know it worked when: the game plays from the public link in a private browser window and on your phone.

## Phase 4 — Your own URL (optional)
- [ ] 🧑 Create a Cloudflare account — 5 min (free)
- [ ] 🤝 Deploy to Cloudflare Pages — 15 min
  > Add `public/_headers` that gives `/assets/*` `Cache-Control: public, max-age=31536000, immutable`. Then run `npx wrangler pages deploy dist --project-name <game>` and give me the URL. Afterwards run `curl -I` on one hashed asset and on any .wasm file and show me the headers.
  You approve the Cloudflare login in your browser when wrangler asks.
  You'll know it worked when: the game plays at `<game>.pages.dev`, and the asset shows the immutable cache header.
- [ ] 🧑 (Optional) Connect a custom domain — 15 min (about £10/year)
  In the Cloudflare dashboard, open the Pages project › **Custom domains** › **Set up a domain**.

## Phase 5 — Get it in front of players
- [ ] 🧑 Post a devlog on your itch.io page — 20 min
  What it is, the GIF, one thing you learned making it.
- [ ] 🧑 Share it where players and makers are — 30 min
  The three.js forum (discourse.threejs.org, Showcase), r/threejs and r/WebGames, and Discord servers for your genre. Lead with the GIF and a direct play link.
- [ ] 🧑 (Optional) Enter a game jam on itch.io — the deadlines and ready-made audience help.
- [ ] 🤖 Add simple, privacy-friendly analytics — 15 min
  > Add a lightweight event count for: game started, reached level 2 (or halfway), game over, and play again. No personal data. Tell me where to see the numbers.
  You'll know it worked when: you can see how many people started and how many finished.

## After launch
- Re-run the checklist before every update, and test on a phone each time.
- Watch the drop-off between "game started" and "game over". That's where the next update should focus.
- Read every comment on itch.io and reply.
- Keep a short changelog in the devlog. Multiplayer, new levels and bigger features go in the brief's "Later" list first.
```
