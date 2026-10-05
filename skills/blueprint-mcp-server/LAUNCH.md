# Launch guide template — MCP Server

Use this template to write `docs/mcp-launch.md`. Tailor it to what was actually built: fill in real names, URLs, package names and commands, and delete phases or steps that don't apply (Phase 2A for a local server, Phase 2B for a remote one, directory steps for a private server). Keep the legend and the step format.

**Every step has:**
- a checkbox
- a 🧑/🤖/🤝 marker
- a time estimate (and the cost, if any)
- plain-English instructions, with technical terms explained on first use when the user is new
- a ready-to-paste prompt in a quote block for 🤖 steps
- a **You'll know it worked when…** line

---

```markdown
# Launch guide: <server name>

**What you're launching:** <one sentence — what the server lets an AI do, local or remote, which clients it works in>
**Estimated total time:** <x hours> · **Cost:** <usually free on hosting free tiers; note paid hosting, a paid Claude plan for directory submission, or a paid ChatGPT plan for testing there>

**Legend**
- 🧑 **You** — needs your accounts, identity or a decision.
- 🤖 **Agent** — paste the prompt into your coding agent.
- 🤝 **Together** — the agent prepares it, you click the final button.

## Phase 0 — Fix blockers (only if the checklist found must-fix items)
- [ ] 🤖 <blocker> — <time>
  > <ready-to-paste prompt>
  You'll know it worked when: <…>

## Phase 1 — Final checks
- [ ] 🤖 Run the tests and the Inspector smoke test — 10 min
  > Run the test suite. Then start the server locally and run `npx @modelcontextprotocol/inspector --cli <target> --method tools/list`. Compare the tools with the table in docs/mcp-brief.md and fix any missing title, annotation or field description.
  You'll know it worked when: tests pass and every tool in the brief is listed with a title and a read-only or destructive hint.
- [ ] 🧑 Try every tool in the Inspector — 15 min
  Run `npx @modelcontextprotocol/inspector`, connect to <local URL or command>, open the Tools tab, and call each tool once with good input and once with bad input.
  You'll know it worked when: good calls return what you expect and bad calls return a clear, helpful error.
- [ ] 🧑 Test tool choice in Claude Code — 15 min
  Run `<claude mcp add command>`, start a new session, and ask for each job in your own words without naming the tool (use the phrasings in docs/mcp-brief.md).
  You'll know it worked when: Claude picks the right tool every time with sensible inputs.
- [ ] 🤖 Bump the version and write the changelog entry — 5 min
  > Set the version to <x.y.z> in package.json, the McpServer constructor<, server.json><, manifest.json>, and add a CHANGELOG.md entry with a one-line summary of what this release lets people do.

## Phase 2A — Deploy (remote servers)
- [ ] 🧑 Set production secrets — 10 min
  In <hosting provider>'s dashboard, open <project> → Environment variables (or Secrets) and add: <list of names, never values>. <For OAuth:> In <identity provider>, add the redirect URIs `https://claude.ai/api/mcp/auth_callback`, `http://localhost/callback` and `http://127.0.0.1/callback` (any port), and turn on Client ID Metadata Documents or Dynamic Client Registration.
  You'll know it worked when: the variables show in the dashboard (values hidden).
- [ ] 🤝 Deploy to production — 10 min
  > Deploy the app to <host> with <deploy command>, then confirm <https://…/mcp> answers: an unauthenticated POST should return <a tools/list result | 401 with a WWW-Authenticate resource_metadata header>.
  You'll know it worked when: the production URL responds as described.
- [ ] 🤖 Smoke-test production — 5 min
  > Run `npx @modelcontextprotocol/inspector --cli --transport http --server-url <https://…/mcp> --method tools/list` <with a valid token if auth is on> and report the tool names.
  You'll know it worked when: the production tool list matches the brief.

## Phase 2B — Package (local servers)
- [ ] 🧑 Create or sign in to your npm account — 5 min
  At npmjs.com, sign up (or sign in) and turn on two-factor authentication. Then run `npm login` in your terminal.
  You'll know it worked when: `npm whoami` prints your username.
- [ ] 🤝 Publish the package — 10 min
  > Check package.json has name <package>, a bin entry, "files" limited to the build output, and <"mcpName": "io.github.<user>/<server>" if listing in the MCP Registry>. Build, run `npm pack --dry-run`, and show me the file list. I'll run `npm publish`.
  You'll know it worked when: `npx -y <package>` starts the server in a scratch folder.
- [ ] 🤖 Build the .mcpb bundle — 15 min
  > Install @anthropic-ai/mcpb, run `mcpb init` to create manifest.json for this server (declare <secrets> as sensitive user_config, add a privacy_policies URL if any data leaves the machine), then run `mcpb validate .` and `mcpb pack .`.
  You'll know it worked when: opening the .mcpb file in Claude Desktop shows an install dialog and the tools work after install.
- [ ] 🤝 Attach the bundle to a GitHub release — 5 min
  > Create a git tag v<x.y.z>, push it, and draft a GitHub release with the .mcpb file attached. Print its SHA-256 with `openssl dgst -sha256 <file>.mcpb`.
  You'll know it worked when: the release page shows the .mcpb download.

## Phase 3 — Install it like a user would
- [ ] 🧑 Claude Code from a clean folder — 5 min
  ```
  <claude mcp add --transport http <name> <url>  |  claude mcp add --transport stdio <name> -- npx -y <package>>
  ```
  Run `/mcp` to sign in if asked, then make a real request.
  You'll know it worked when: you get a correct answer from your production server.
- [ ] 🧑 <Second client: Claude / ChatGPT / Cursor / VS Code / Codex> — 10 min
  <exact steps or config snippet for that client, from REFERENCE.md §11>
  You'll know it worked when: the same request works there.
- [ ] 🤖 Write the README install section — 15 min
  > Make the README's first screen show: what the server does in one sentence, the tool list with one example request each, and a copy-paste install snippet for <clients>. Never include real keys; use placeholders like YOUR_API_KEY.

## Phase 4 — Get it in front of people
- [ ] 🤝 (Optional) List it in the MCP Registry — 20 min
  > Install mcp-publisher, run `mcp-publisher init`, and fill server.json with name io.github.<user>/<server>, a description, version <x.y.z>, and <packages: the npm package | packages: the .mcpb release URL with fileSha256 | remotes: streamable-http at <url>>. Then run `mcp-publisher validate`.
  Then you run `mcp-publisher login github` and `mcp-publisher publish`.
  You'll know it worked when: searching the registry at registry.modelcontextprotocol.io returns your server.
- [ ] 🧑 (Optional, remote servers) Submit to Anthropic's connector directory — 45 min
  Needs a paid Claude plan (an Owner on Team or Enterprise). Have ready: documentation URL, privacy policy URL, support contact, icon, and a fully populated test account for reviewers. Add your server as a custom connector in Claude first and run every tool. Then submit at claude.ai/directory/manage → Submit new → MCP connector.
  You'll know it worked when: the submission shows in the portal and later lists as a Community connector.
- [ ] 🧑 (Optional, local servers) Ship it in a Claude Code plugin — see the `blueprint-ai-plugin` blueprint. Anthropic's directory no longer takes standalone local bundles.
- [ ] 🧑 (Optional) Submit to other client directories (ChatGPT apps, Cursor) — 30 min each. Check each one's current submission rules first.
- [ ] 🧑 Share it — post the install snippet and one example request wherever your users are.

## After launch
- Re-run the checklist before every release, and bump the version everywhere it appears.
- Watch for requests where the AI picked the wrong tool or passed bad inputs, and improve those names and descriptions first.
- Never rename or remove a tool without a major version bump and a note in the changelog.
- Watch error rates and auth failures in <hosting logs>, and GitHub issues.
```
