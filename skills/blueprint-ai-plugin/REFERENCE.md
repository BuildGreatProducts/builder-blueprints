# AI Plugin — Reference

> **Staying current:** plugin and skill formats move quickly. Before relying on a manifest field, frontmatter key, flag or command, check the installed tool's version (`claude --version`, `codex --version`, etc.) and read the live docs: https://code.claude.com/docs/en/plugins-reference, https://code.claude.com/docs/en/skills, https://agentskills.io/specification (or Context7). `claude plugin validate .` is the source of truth for the Claude Code format. When this reference and the live docs disagree, the docs win.

## Contents
1. Default approach
2. Plugin layout
3. Manifests
4. Skills — format and writing
5. Other components (agents, hooks, MCP, userConfig)
6. Paths and variables
7. Versioning and updates
8. Working in Codex and Cursor too
9. Testing
10. Patterns to avoid

---

## 1. Default approach

- **One repo = one marketplace = one plugin** for a single product. Put `marketplace.json` and `plugin.json` side by side in `.claude-plugin/`, with the marketplace entry's `source` set to `"./"`. Users get one add command and one install command.
- **Skills first.** Most plugins are just skills. Add agents, hooks or MCP only when a skill can't do the job.
- **Portable skills.** Write SKILL.md files to the open Agent Skills standard (only `name` and `description` frontmatter), so the same folder works in Claude Code, Codex, Cursor, Gemini CLI, Copilot and others.
- **Self-contained skill folders.** Everything a skill needs lives in its folder, referenced by relative path. A skill copied on its own still works.

## 2. Plugin layout

```
my-plugin/
├── .claude-plugin/
│   ├── plugin.json          # manifest (only file that goes in .claude-plugin/ besides marketplace.json)
│   └── marketplace.json     # makes the repo installable as a marketplace
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md         # required
│       ├── REFERENCE.md     # optional, loaded on demand
│       └── scripts/…        # optional, executed not read
├── agents/                  # optional: <agent>.md subagents
├── hooks/hooks.json         # optional: must wrap events in a top-level "hooks" key
├── .mcp.json                # optional: MCP servers
├── README.md
├── CHANGELOG.md
└── LICENSE
```

Notes:
- Component folders sit at the plugin root, **not** inside `.claude-plugin/`.
- A `CLAUDE.md` at the plugin root is **not** loaded. Instructions belong in skills.
- `commands/` still works but is legacy. Use `skills/`.
- Avoid a top-level `bin/` if you want the plugin to work on claude.ai or in Cowork (they refuse plugins with one). Use `scripts/` instead.

## 3. Manifests

### `.claude-plugin/plugin.json`
Only `name` is required. Recommended:

```json
{
  "name": "my-plugin",
  "displayName": "My Plugin",
  "version": "0.1.0",
  "description": "One or two sentences on what it does and for whom.",
  "author": { "name": "Your Name", "email": "you@example.com", "url": "https://example.com" },
  "homepage": "https://github.com/you/my-plugin",
  "repository": "https://github.com/you/my-plugin",
  "license": "MIT",
  "keywords": ["…"]
}
```

- `name`: kebab-case and **permanent**. Users install and configure by `name@marketplace`, so renaming breaks every install. Use `displayName` for the label people see.
- **Reserved names:** don't start with `claude-`, `anthropic-`, `anthropics-` or `cc-plugin-`. Don't put `official` next to `claude`/`anthropic`. Using `claude` or `anthropic` as a whole word anywhere draws a warning. The same goes for skill names: keep "claude" and "anthropic" out of them.
- `homepage` must parse as a URL, or the plugin fails to load.
- Unknown top-level fields are stripped with a warning.
- Directory listing fields (`icon`, `documentationUrl`, `supportUrl`, `privacyPolicyUrl`, `termsOfServiceUrl`) are read only by Anthropic's directory.

### `.claude-plugin/marketplace.json`

```json
{
  "name": "my-plugin",
  "owner": { "name": "Your Name", "email": "you@example.com" },
  "metadata": { "description": "…" },
  "plugins": [
    { "name": "my-plugin", "source": "./", "description": "…" }
  ]
}
```

- Required: `name`, `owner`, `plugins[]`. Each entry needs `name` and `source`.
- **Keep the entry `name` identical to the manifest `name`.** Mismatches cause "not found in marketplace" errors.
- Relative `source` paths start from the marketplace root (the folder containing `.claude-plugin/`) and must not contain `..`.
- Other source types: `{ "source": "github", "repo": "owner/repo" }`, `git-subdir`, `url`, `archive`, `npm`.
- Set `version` in `plugin.json` **or** the marketplace entry, never both.

## 4. Skills — format and writing

### Frontmatter (portable)

```markdown
---
name: doing-the-thing
description: Does X and Y. Use when the user wants …, mentions …, or asks to "…", "…". Writes … to ….
---
```

- `name`: 1–64 characters, lowercase letters, digits and hyphens. No leading, trailing or double hyphens. **Must match the folder name.**
- `description`: 1–1024 characters, third person, saying **what it does + when to use it**, with the real phrases users type. This is the only thing the model sees when deciding whether to load the skill. It matters more than the body.
- Claude Code also accepts extra fields (`when_to_use`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `model`, `effort`, `context: fork`, `arguments`, `paths`). Use them only when needed, and know that other tools ignore them. `description` + `when_to_use` are truncated together at 1,536 characters in Claude Code's listing.
- Use `disable-model-invocation: true` for skills that should only run when the user explicitly asks (deploys, sending messages).

### Writing the body

- **Assume the model is smart.** Only write what it wouldn't already know: your process, your judgement calls, your formats, your gotchas.
- **SKILL.md under ~500 lines** (aim for 100–300). Move detail into files in the skill folder, linked **one level deep** from SKILL.md. Give reference files over 100 lines a contents list.
- **Say when to read each file** ("Read `REFERENCE.md` before building"), so the model loads it at the right moment.
- **Set the degree of freedom deliberately:**
  - prose for judgement calls
  - a template for preferred formats
  - an exact script for fragile steps ("Run exactly: `python scripts/x.py`")
- **Workflows:** numbered steps, a validate → fix → repeat loop for anything quality-critical, and a clear "done" definition.
- **One default, not a menu.** Give an escape hatch only for a real alternative case.
- **Keep skills evergreen.** No version numbers or dates in the skill. State guiding principles and the current conventions, and tell the agent to check the installed version and the live docs before relying on anything that changes between releases. Time-sensitive detail never goes in SKILL.md; put deprecated approaches under "patterns to avoid".
- **Consistent terminology.** Pick one word per concept and stick to it.
- **Scripts:** handle errors inside the script, document every constant, list dependencies, and use forward-slash paths.
- **MCP tools:** refer to them fully qualified (`ServerName:tool_name`).

### Description recipe

> Use when the user [situation] and wants [outcome]. Triggers on phrases like "…", "…", "…", or any request to [general form]. [What it reads] → [what it does] → [what it writes, with exact paths]. [Optional: where it fits in a larger workflow.]

Test it: in a fresh session, type the user's own phrasings without naming the skill. If it doesn't trigger, the description is wrong.

## 5. Other components

- **Agents** (`agents/<name>.md`): frontmatter `name`, `description`, optional `tools`, `model`. Use for work that needs its own context or a restricted toolset (e.g. a read-only reviewer). Namespaced as `plugin:agent`.
- **Hooks** (`hooks/hooks.json`): deterministic actions on events (`PreToolUse`, `PostToolUse`, `SessionStart`, …). The file needs a top-level `"hooks"` wrapper. Quote `"${CLAUDE_PLUGIN_ROOT}"` in shell-form commands. Claude Code only.
- **MCP servers** (`.mcp.json`, or `mcpServers` in `plugin.json`): for live data or actions in external systems. Reference bundled servers with `${CLAUDE_PLUGIN_ROOT}`. A `.mcpb` bundle path also works.
- **userConfig** (in `plugin.json`): values Claude Code asks the user for when the plugin is enabled. Each option is a strict object with `type`, `title`, `description` (plus optional `required`, `default`, `sensitive`, `options`). `sensitive: true` masks input and stores the value in the keychain. Reference values as `${user_config.KEY}` in MCP/LSP config, exec-form hook args, and skill content (sensitive values are not substituted into skill content).

## 6. Paths and variables

- Component paths in manifests are relative and start with `./`, and must stay inside the plugin root (no `..`).
- `${CLAUDE_PLUGIN_ROOT}` is the installed plugin folder. It **changes on every update**, so never write state there.
- `${CLAUDE_PLUGIN_DATA}` is persistent per-plugin data (survives updates; deleted on uninstall).
- `${CLAUDE_SKILL_DIR}` is the current skill's folder. `${CLAUDE_PROJECT_DIR}` is the project root.
- These variables are substituted into skill/agent Markdown, hook commands and MCP config. They are **not** present in the environment of commands Claude runs through Bash, so write the `${...}` reference in the skill text.
- For portability outside Claude Code, refer to bundled files by name "in this skill's folder" rather than relying only on `${CLAUDE_SKILL_DIR}`.

## 7. Versioning and updates

- If `version` is set, users only receive an update when it changes. **Bump it on every release**, or omit it entirely to track git commits.
- Semver: patch for wording fixes, minor for new skills or behaviour, major for renames or removals.
- Keep a `CHANGELOG.md` with `## X.Y.Z — Month YYYY` headings and a one-line "why" per release.
- Tag releases (`vX.Y.Z`, or `claude plugin tag --push` for `{name}--v{version}` tags when others depend on you).
- Users update with `claude plugin update <plugin>@<marketplace>` (or `/plugin marketplace update <marketplace>`). Auto-update is off by default for third-party marketplaces; users can enable it under **Marketplaces** in `/plugin`.
- Never rename a published plugin. If you must, add a `renames` map to `marketplace.json`.
- Optional: ship an update skill that compares the installed version with the repo's `plugin.json`, shows the changelog delta, and runs the update commands.

## 8. Working in Codex and Cursor too

The SKILL.md format is shared, so the same `skills/` folder works across tools. Each tool has its own manifest folder pointing at it:

- **Codex:**
  - A root `plugin.json` in the portable Agent Plugins format: `"$schema"` set to the current schema URL from agent-plugins.org (copy it from the live docs rather than from memory), plus `name`, `version`, `description` and the usual metadata.
  - Skills are found automatically in the root `skills/` folder.
  - Codex-only settings go under `extensions.com.openai`, e.g. an `interface` block with `displayName`, `shortDescription`, `longDescription`, `developerName`, `category`, `capabilities`, `websiteURL`, `defaultPrompt`.
  - The marketplace file is `.agents/plugins/marketplace.json`, whose entries take `source: { "source": "local", "path": "." }` and a `policy` block.
  - Users add it with `codex plugin marketplace add owner/repo`, then install from `/plugins`.
  - Older `.codex-plugin/plugin.json` files still work as a fallback.
- **Cursor:**
  - `.cursor-plugin/plugin.json` (with `"skills": "./skills/"`) and `.cursor-plugin/marketplace.json` (whose plugin entry uses `"source": "."`).
  - Users install with `/add-plugin` pointed at a **git clone**. A ZIP download fails because Cursor needs a resolvable `HEAD`.
  - Publish to the Cursor marketplace at cursor.com/marketplace/publish.
- Keep `version` identical across all manifests.
- Hooks, agents and `${CLAUDE_*}` variables are Claude Code features; say so in the README.
- Check each tool's current docs before adding its manifest. These formats are newer and change more often.

Users who want just one skill can copy its folder into `~/.claude/skills/` (Claude Code), or the equivalent skills folder in their tool.

## 9. Testing

- `claude plugin validate .` checks manifests, paths and MCP config. Use `--strict` in CI to fail on warnings.
- `claude --plugin-dir .` loads the plugin for one session without installing it. Use `/reload-plugins` after edits.
- **Trigger test:** in a fresh session, type 2–3 natural phrasings per skill without naming it, and confirm it loads.
- **Behaviour test:** run each skill on a realistic task and check the output files and steps.
- **Evals (recommended):** `claude plugin eval` (confirm your installed Claude Code has it with `claude plugin --help`) runs cases in `evals/<case>/prompt.md` with graders, with and without the plugin, and reports the difference. Write about three cases per important skill.
- **Install test:** `claude plugin marketplace add ./` then `claude plugin install <name>@<marketplace>` in a scratch folder, exactly as a user would.

## 10. Patterns to avoid

- Vague descriptions ("Helps with websites"). They never trigger.
- First- or second-person descriptions ("I can help you…"). Write in third person.
- Many tiny overlapping skills that compete for the same phrases.
- Giant SKILL.md files that paste whole API docs. Link to the docs or put them in a reference file.
- Reference chains (SKILL → A → B → C). Keep everything one level deep.
- Hard-coded tool versions and dates in skills. State the principle and point to the live docs instead.
- Secrets in files, examples or `.mcp.json`. Use `userConfig` with `sensitive: true` or environment variables.
- Paths with `..`, Windows backslashes, or absolute paths to your own machine.
- Changing files without bumping `version` (users never get the update).
- Renaming a published plugin or skill.
- Skill or plugin names containing "claude" or "anthropic".
