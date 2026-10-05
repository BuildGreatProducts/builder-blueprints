# AI Plugin — Checklist

Audit the real repo against every item. **[must]** blocks launch. **[should]** is strongly recommended. Each item says how to verify it. Run the command or read the file; never assume a pass.

## Manifests
- [ ] **[must]** `claude plugin validate .` passes. *Verify: run it.*
- [ ] **[must]** `.claude-plugin/plugin.json` has a kebab-case `name` that isn't reserved (no `claude-`/`anthropic-` prefix, no `claude`/`anthropic` word). *Verify: read the file.*
- [ ] **[must]** The marketplace entry `name` matches the `plugin.json` `name`. *Verify: compare both files.*
- [ ] **[must]** `version` is set in exactly one place and has been bumped since the last release. *Verify: `git log -p .claude-plugin/` or compare with the last tag.*
- [ ] **[should]** `description`, `author`, `homepage`, `repository` and `license` are filled in. *Verify: read the file.*
- [ ] **[should]** If Codex or Cursor manifests exist, their `version` matches `plugin.json`. *Verify: `grep -n '"version"' plugin.json .claude-plugin/plugin.json .cursor-plugin/plugin.json .codex-plugin/plugin.json 2>/dev/null`.*

## Skills
- [ ] **[must]** Every skill folder has a `SKILL.md` whose `name` matches the folder name. *Verify: list `skills/*/SKILL.md` and compare.*
- [ ] **[must]** Every `description` is 1024 characters or fewer, in third person, and says what the skill does **and** when to use it, with real user phrasings. *Verify: measure each with a quick script.*
- [ ] **[must]** Each skill triggers in a fresh session from at least two natural phrasings that don't name it. *Verify: `claude --plugin-dir .`, then test.*
- [ ] **[must]** Every file a SKILL.md mentions exists in that skill's folder. *Verify: grep file names and check each one exists.*
- [ ] **[should]** Each SKILL.md is under ~500 lines, and longer detail lives in reference files linked one level deep. *Verify: `wc -l`.*
- [ ] **[should]** Reference files over 100 lines start with a contents list. *Verify: read them.*
- [ ] **[should]** No versions or dates hard-coded in SKILL.md. They live in a reference file with a "Last verified" line. *Verify: grep for version patterns.*
- [ ] **[should]** No two skills compete for the same trigger phrases. *Verify: read the descriptions side by side.*
- [ ] **[should]** Each skill folder is self-contained: no `../` references to files outside it. *Verify: `grep -rn "\.\./" skills/`.*

## Other components (if present)
- [ ] **[must]** `hooks/hooks.json` wraps events in a top-level `"hooks"` key, and shell-form commands quote `"${CLAUDE_PLUGIN_ROOT}"`. *Verify: read the file; validate warns on this.*
- [ ] **[must]** MCP server config contains no literal credentials. *Verify: read `.mcp.json`; validate warns on credential-like headers.*
- [ ] **[should]** Agents have a clear `description` and the narrowest `tools` list that works. *Verify: read `agents/*.md`.*
- [ ] **[should]** No top-level `bin/` folder if claude.ai/Cowork support matters. *Verify: `ls`.*

## Security
- [ ] **[must]** No secrets, tokens or API keys anywhere in the repo or its git history. *Verify: `git grep -nE "(sk-|api[_-]?key|token|secret)"` and review the hits.*
- [ ] **[must]** Secrets the plugin needs come from `userConfig` with `sensitive: true` or from environment variables. *Verify: read `plugin.json` and the skills.*
- [ ] **[should]** Scripts don't run destructive commands without a confirmation step. *Verify: read `scripts/`.*

## Docs and release
- [ ] **[must]** `README.md` explains what the plugin does and shows the exact install commands (`claude plugin marketplace add <owner/repo>` then `claude plugin install <name>@<marketplace>`). *Verify: read it.*
- [ ] **[should]** README explains how to install a single skill (copy its folder into `~/.claude/skills/`) and how to update. *Verify: read it.*
- [ ] **[should]** `CHANGELOG.md` has an entry for the current version. *Verify: read it.*
- [ ] **[should]** A `LICENSE` file matches the `license` field. *Verify: read both.*
- [ ] **[should]** An install test from a scratch folder succeeds (`claude plugin marketplace add <path or owner/repo>`, then install). *Verify: run it.*
- [ ] **[should]** Evals exist for the most important skills and pass against the no-plugin baseline. *Verify: `claude plugin eval`, if available.*
