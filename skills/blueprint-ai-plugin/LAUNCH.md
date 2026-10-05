# Launch guide template — AI Plugin

Use this template to write `docs/plugin-launch.md`. Tailor it to what was actually built: fill in real names, repo URLs and commands, and delete phases or steps that don't apply. Keep the legend and the step format.

**Every step has:**
- a checkbox
- a 🧑/🤖/🤝 marker
- a time estimate (and the cost, if any)
- plain-English instructions, with technical terms explained on first use when the user is new
- a ready-to-paste prompt in a quote block for 🤖 steps
- a **You'll know it worked when…** line

---

```markdown
# Launch guide: <plugin name>

**What you're launching:** <one sentence — what the plugin does, which tools it works in>
**Estimated total time:** <x hours> · **Cost:** <usually free; note paid claude.ai plan if submitting to Anthropic's directory>

**Legend**
- 🧑 **You** — needs your accounts, identity or a decision.
- 🤖 **Agent** — paste the prompt into your coding agent.
- 🤝 **Together** — the agent prepares it, you click the final button.

## Phase 0 — Fix blockers (only if the checklist found must-fix items)
- [ ] 🤖 <blocker> — <time>
  > <ready-to-paste prompt>
  You'll know it worked when: <…>

## Phase 1 — Final checks
- [ ] 🤖 Run validation and the trigger tests — 10 min
  > Run `claude plugin validate .` and fix anything it reports. Then list each skill with two natural phrases from docs/plugin-brief.md that should trigger it.
  You'll know it worked when: validation prints "Validation passed" and you have a trigger-test list.
- [ ] 🧑 Trigger-test each skill in a fresh session — 15 min
  Run `claude --plugin-dir .` in a new terminal and type each phrase without naming the skill.
  You'll know it worked when: every skill loads from its phrases.
- [ ] 🤖 Bump the version and write the changelog entry — 5 min
  > Bump the version in .claude-plugin/plugin.json (and any Codex/Cursor manifests) to <x.y.z>, and add a CHANGELOG.md entry with a one-line summary of why this release matters.

## Phase 2 — Put it on GitHub
- [ ] 🧑 Create the repository — 5 min
  On github.com, choose New repository, name it `<repo>`, and set it to Public (or Private for team-only plugins). Don't add a README; you already have one.
  You'll know it worked when: you can see the empty repo page.
- [ ] 🤝 Push the code and tag the release — 5 min
  > Add the GitHub remote <url>, push the main branch, then create and push a tag v<x.y.z>.
  You'll know it worked when: your files and the tag show on GitHub.

## Phase 3 — Install it like a user would
- [ ] 🧑 Install from GitHub in a clean folder — 10 min
  ```
  claude plugin marketplace add <owner>/<repo>
  claude plugin install <name>@<marketplace-name>
  ```
  Start a session and type one of your trigger phrases.
  You'll know it worked when: the skill loads and does its job from the published copy.
- [ ] 🧑 (If supported) Install in Codex / Cursor — 10 min each
  <tool-specific install steps>

## Phase 4 — Get it in front of people
- [ ] 🤖 Polish the README install block and add a short demo — 20 min
  > Make the README's first screen show: what the plugin does in one sentence, the two install commands, how to install a single skill, and one example prompt per skill.
- [ ] 🧑 (Optional) Submit to Anthropic's directory — 30 min
  Needs a paid claude.ai plan. Run `claude plugin validate --strict .`, work through the pre-submission checklist at claude.com/docs/plugins/pre-submission-checklist, then submit at claude.ai/directory/manage.
  You'll know it worked when: the submission shows as "In review".
- [ ] 🧑 (Optional) Submit to the Cursor marketplace or the Codex/ChatGPT plugin directory — 30 min each
- [ ] 🧑 Share it — post the repo link and one example prompt wherever your audience is.

## After launch
- Re-run the checklist before every release, and bump `version` every time.
- Ask early users which phrases they typed when a skill *didn't* trigger, and add those to the description.
- Watch GitHub issues.
```
