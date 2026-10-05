# MCP Server — Checklist

Audit the real repo and the running server against every item. **[must]** blocks launch. **[should]** is strongly recommended. Each item says how to verify it. Run the command or read the file; never assume a pass. Skip sections marked "if present" when they don't apply, and say so in the report.

## Protocol and architecture
- [ ] **[must]** The server uses the current SDK generation (see `REFERENCE.md` §2): no `@modelcontextprotocol/sdk` imports, no TypeScript `server.tool(...)`, no `mcp.server.fastmcp` imports in Python, no hand-wired session transports. *Verify: read `package.json` (or `pyproject.toml`) and `grep -rnE "@modelcontextprotocol/sdk|server\.tool\(|mcp\.server\.fastmcp|Mcp-Session-Id|sessionIdGenerator" src/ app/ lib/`.*
- [ ] **[must]** Tools, resources and prompts are registered inside a factory that returns a fresh server, not on a shared module-level instance. *Verify: read the serving entry point.*
- [ ] **[must]** No per-user state is held in server memory between requests. Anything that spans calls uses a handle backed by storage. *Verify: read the handlers for module-level maps, caches keyed by user, or globals that change.*
- [ ] **[must]** Remote servers use Streamable HTTP at one endpoint. No HTTP+SSE (`/sse`, `/message`) routes. *Verify: read the routes; `grep -rn "sse" src/ app/`.*
- [ ] **[must]** The architecture matches `docs/mcp-brief.md` (embedded vs standalone, local vs remote, framework). *Verify: compare the brief with the code.*
- [ ] **[should]** No deprecated features adopted: Roots, Sampling, the Logging capability, pushed `elicitInput`/`requestSampling`, Cloudflare `McpAgent` for new code. *Verify: `grep -rnE "listRoots|createMessage|requestSampling|elicitInput|McpAgent|sendLoggingMessage" .` excluding `node_modules`.*

## Tools
- [ ] **[must]** The tool list matches the brief's tool table, and there are no more than about 10 tools. *Verify: `npx @modelcontextprotocol/inspector --cli <target> --method tools/list` and compare with the brief.*
- [ ] **[must]** Every tool has a `title`, a description that says what it does **and when to use it**, and the correct `readOnlyHint` or `destructiveHint`. *Verify: read the `tools/list` output.*
- [ ] **[must]** Every input field has a description, and fixed choices use enums. *Verify: read each `inputSchema` in the `tools/list` output.*
- [ ] **[must]** Tool names are unique, consistent and prefixed (`service_verb_noun`), using only letters, digits and underscores. *Verify: read the `tools/list` output.*
- [ ] **[must]** Execution failures return `isError: true` with text that tells the model how to fix the call (or the user what went wrong). *Verify: call each tool with a bad or missing value in the Inspector and read the result.*
- [ ] **[must]** Each tool is chosen correctly from at least two of the user's own phrasings in a fresh Claude Code session, without naming the tool. *Verify: `claude mcp add …`, then test.*
- [ ] **[should]** List-style tools paginate with a cursor and default to a concise response, with a detailed option. *Verify: call them with a large account and check size (well under 10,000 tokens).*
- [ ] **[should]** Tools whose data a client or app will use declare `outputSchema` and return matching `structuredContent` alongside readable text. *Verify: read the registrations; call the tool.*
- [ ] **[should]** Destructive or costly actions ask for confirmation through `input_required` before acting. *Verify: call one in the Inspector and confirm it asks first.*
- [ ] **[should]** Tools are returned in a stable order. *Verify: run `tools/list` twice and compare.*

## Security
- [ ] **[must]** No secrets, tokens or API keys in the repo, its git history, `server.json`, `manifest.json`, README examples or tool output. *Verify: `git grep -nE "(sk-|api[_-]?key|token|secret|Bearer )"` and review the hits.*
- [ ] **[must]** Every tool enforces the caller's permissions in the handler (through the app's existing checks for embedded servers). Annotations are not treated as enforcement. *Verify: read each handler's data access.*
- [ ] **[must]** Local HTTP servers bind to `127.0.0.1` and validate `Host` and `Origin`. Public servers set `allowedHosts`. *Verify: read the app factory call and `listen` call; send a request with `Host: evil.example` and expect it to be rejected (`403`, or `421` from the Python SDK).*
- [ ] **[must]** Anything the client echoes back (`requestState`, handles, cursors carrying filters) is HMAC-sealed or looked up server-side with an ownership check. *Verify: read where they're minted and read back.*
- [ ] **[must]** stdio servers write nothing but protocol messages to stdout. *Verify: `grep -rn "console.log\|print(" src/` and review.*
- [ ] **[should]** Content from outside sources (web, email, user uploads) is returned as clearly labelled data, and no handler acts on instructions found in it. *Verify: read the handlers that fetch external content.*
- [ ] **[should]** Requests are rate-limited per user or token, and downstream calls have timeouts. *Verify: read the middleware and HTTP client config.*
- [ ] **[should]** Logs never include tokens or full personal data. *Verify: grep logging calls near auth and tool handlers.*

## Auth (if the server requires sign-in)
- [ ] **[must]** An unauthenticated request gets `401` with `WWW-Authenticate: Bearer resource_metadata="…"`. *Verify: `curl -si -X POST <url> -H 'Content-Type: application/json' -d '{}'`.*
- [ ] **[must]** The Protected Resource Metadata document is served, its `resource` equals the exact MCP URL, and `authorization_servers` lists the issuer first. *Verify: `curl` the `resource_metadata` URL.*
- [ ] **[must]** Tokens are checked for audience (issued for this server), expiry and required scopes. *Verify: read the verifier; try a token issued for another audience and expect `401`.*
- [ ] **[must]** The client's token is never passed through to downstream APIs. *Verify: read every outbound API call.*
- [ ] **[must]** The authorisation server allows `https://claude.ai/api/mcp/auth_callback` and loopback redirects (`localhost` and `127.0.0.1`, any port), supports PKCE S256, and supports Client ID Metadata Documents or Dynamic Client Registration. *Verify: read the provider's settings and its `/.well-known/oauth-authorization-server` (or OpenID) metadata.*
- [ ] **[should]** Sensitive tools require a narrower scope than read-only ones. *Verify: read the scope configuration.*
- [ ] **[should]** Sign-in works end to end from a clean Claude Code and one hosted client, and an expired token triggers re-auth cleanly. *Verify: run it.*

## Local server packaging (if present)
- [ ] **[must]** The package runs from a clean install (`npx -y <package>` or `uvx <package>`) with only the documented environment variables. *Verify: run it in a scratch folder and connect the Inspector.*
- [ ] **[should]** An `.mcpb` bundle validates and packs, declares secrets as `sensitive` user config, and includes `privacy_policies` if data leaves the machine. *Verify: `mcpb validate .` and `mcpb pack .`.*

## MCP Apps (if present)
- [ ] **[must]** Each UI is a `ui://` resource with MIME type `text/html;profile=mcp-app`, linked from its tool via `_meta.ui.resourceUri`. *Verify: `resources/list` and `tools/list` in the Inspector.*
- [ ] **[must]** The tool's text result makes sense on its own for clients that don't render apps. *Verify: call it in the Inspector and read the text.*
- [ ] **[should]** External origins the page loads are declared in `_meta.ui.csp`, and nothing else is fetched. *Verify: read the resource metadata and the bundled HTML.*

## Testing
- [ ] **[must]** Every tool lists and calls cleanly in a current MCP Inspector, against the production URL (remote) or the published package (local). *Verify: run the Inspector CLI or web UI.*
- [ ] **[must]** The server works in Claude Code and at least one other target client from the brief. *Verify: connect and run a real request in each.*
- [ ] **[should]** Automated tests call each tool through an in-memory client, including one failure case per tool. *Verify: run the test suite.*
- [ ] **[should]** A smoke test (`--cli … --method tools/list` with a pinned Inspector version) runs in CI or after deploy. *Verify: read the CI config.*

## Docs and release
- [ ] **[must]** `README.md` says what the server does in one sentence, lists the tools, and gives install snippets for each target client. *Verify: read it.*
- [ ] **[must]** Remote servers in a public listing have a public documentation URL and privacy policy URL. *Verify: open both.*
- [ ] **[should]** `version` matches across `package.json`, the server's declared version, `server.json` and `manifest.json`, and `CHANGELOG.md` has an entry for it. *Verify: `grep -rn '"version"'` across those files and read the changelog.*
- [ ] **[should]** If listing in the MCP Registry: `server.json` validates and its `name` matches `mcpName` in `package.json` (for npm packages). *Verify: `mcp-publisher validate` and compare.*
- [ ] **[should]** A `LICENSE` file exists and matches the package's `license` field. *Verify: read both.*
