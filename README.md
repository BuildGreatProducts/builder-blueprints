# Builder Blueprints

Skills that help you build real products with an AI coding agent, without the guesswork.

Each blueprint:
- **interviews you** and adapts to your experience
- gives your agent the **best-practice reference** to build from
- **audits** what you built against a checklist
- writes a **launch guide** for exactly what you built

You steer and the agent does the heavy lifting.

| Blueprint | What it helps you build |
|---|---|
| `blueprint-website` | A Next.js website with strong SEO, ready to rank and convert |
| `blueprint-web-app` | A full-stack web app with Next.js and Convex, ready for real users |
| `blueprint-mobile-app` | An iOS and Android app with Expo, Convex and RevenueCat subscriptions |
| `blueprint-ios-app` | A native iPhone app in SwiftUI, built on Apple's own frameworks |
| `blueprint-ai-plugin` | A Claude Code plugin or set of agent skills, ready to publish |
| `blueprint-threejs-game` | A browser game in three.js, with a Blender asset pipeline |
| `blueprint-mcp-server` | An MCP server, either inside your existing app or standalone |
| `blueprint-node-api` | A Node.js API designed around your use case |
| `blueprint-update` | Pulls the latest blueprints from this repo |

## Install

### Whole plugin (recommended)

In your terminal:

```bash
claude plugin marketplace add BuildGreatProducts/builder-blueprints
claude plugin install builder-blueprints@builder-blueprints
```

Or inside Claude Code:

```
/plugin marketplace add BuildGreatProducts/builder-blueprints
/plugin install builder-blueprints@builder-blueprints
```

### Codex

```bash
codex plugin marketplace add BuildGreatProducts/builder-blueprints
```

Then open `/plugins` in Codex and install **Builder Blueprints**.

### Cursor

Clone the repo. Cursor needs a real git clone, not a ZIP download:

```bash
git clone https://github.com/BuildGreatProducts/builder-blueprints
```

Then type `/add-plugin` in Cursor and point it at the cloned folder. Cursor finds all the skills in `skills/` automatically.

### Just one blueprint

Every blueprint is a self-contained folder. Copy the one you want into your skills folder:

```bash
git clone --depth 1 https://github.com/BuildGreatProducts/builder-blueprints /tmp/bb
cp -R /tmp/bb/skills/blueprint-website ~/.claude/skills/
```

The folders follow the open [Agent Skills](https://agentskills.io) format, so they also work in other tools that support skills (Codex, Cursor, Gemini CLI and others). Copy the folder into that tool's skills directory.

## Use

Just describe what you want to build. For example:

- "Help me build a website for my bakery that ranks on Google"
- "I want to build a SaaS app where teams can track their projects"
- "Let's make a habit tracker for iPhone and Android with a subscription"
- "Build me a native iPhone app for logging my climbs, synced with iCloud"
- "I want to turn my prompts into a Claude Code plugin"
- "Let's make a low-poly racing game in the browser"
- "Add an MCP server to my Next.js app so Claude can manage my tasks"
- "I need an API for my booking app"

Each blueprint works in four modes, which it picks from what you ask:

1. **Plan:** a short interview. Writes `docs/<type>-brief.md`, which your agent builds from.
2. **Build:** you steer and the agent builds, following the blueprint's reference.
3. **Check:** "check my site", "audit my API". Runs the checklist and offers fixes.
4. **Launch:** "help me launch", "deploy this". Writes `docs/<type>-launch.md`, a step-by-step guide that marks what you do (🧑), what your agent does (🤖) and what you do together (🤝).

## Update

Say "update my blueprints" and the `blueprint-update` skill shows what's new and updates your copy.

You can also update from the terminal:

```bash
claude plugin update builder-blueprints@builder-blueprints
```

- **Codex:** run `codex plugin marketplace upgrade`.
- **Cursor:** run `git pull` in your clone, then reload the window.

To get updates automatically: open `/plugin`, go to **Marketplaces**, choose `builder-blueprints`, then **Enable auto-update**.

## Contributing

Each blueprint lives in `skills/blueprint-<type>/` and has the same four files:

| File | Purpose |
|---|---|
| `SKILL.md` | Interview and workflow |
| `REFERENCE.md` | Stack, best practice, patterns to avoid |
| `CHECKLIST.md` | Audit items |
| `LAUNCH.md` | Launch guide template |

Version numbers live only in `REFERENCE.md`, under a "Last verified" date.

Before opening a PR, run `claude plugin validate .`.

When you release, bump `version` in all three manifests (`.claude-plugin/plugin.json`, `plugin.json` for Codex, and `.cursor-plugin/plugin.json`) and add a `CHANGELOG.md` entry.

## Licence

MIT. See [LICENSE](LICENSE).
