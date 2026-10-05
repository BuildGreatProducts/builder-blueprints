# MCP Server — Reference

> Last verified: 2026-10. MCP changed a lot in 2026. Before relying on an API, option, or command, check the live docs: https://modelcontextprotocol.io/specification/latest, https://ts.sdk.modelcontextprotocol.io/v2/, https://py.sdk.modelcontextprotocol.io/, https://github.com/vercel/mcp-handler, https://developers.cloudflare.com/agents/model-context-protocol/.
>
> Versions at last check:
> - MCP spec **2026-07-28** (previous: 2025-11-25)
> - TypeScript SDK `@modelcontextprotocol/server` **2.3.x** and adapters `@modelcontextprotocol/express` / `hono` / `fastify` / `node` **2.0.x**. ESM, Node 20+. Zod **4**
> - `mcp-handler` **2.2.x** (needs SDK ^2 and Node 20+)
> - Cloudflare Agents SDK `agents` **0.26.x**, `@cloudflare/workers-oauth-provider` **1.2.x**
> - Python SDK `mcp` **2.3.x** (Python 3.10+). Standalone `fastmcp` **4.0.x**
> - MCP Inspector **2.9.x** (needs Node 22.19+)
> - MCP Apps: `@modelcontextprotocol/ext-apps` **2.0.x**, extension spec **2026-01-26**
> - MCP Bundles: `@anthropic-ai/mcpb` CLI **2.1.x**, `manifest_version` **0.3**
> - MCP Registry: `mcp-publisher` from registry release **1.8.x**

Anthropic also publishes a general `mcp-builder` skill covering MCP server development in several languages. This blueprint is the opinionated end-to-end path: interview, one recommended architecture, build, audit, launch.

## Contents
1. Default approach
2. What changed in 2026
3. Architecture decision path
4. Serving recipes
5. Designing tools
6. Resources, prompts and MCP Apps
7. Asking the user mid-call, and state across calls
8. Authentication and authorisation
9. Security
10. Testing
11. Distribution
12. Patterns to avoid

---

## 1. Default approach

- **Embed when there's an app.** Serve MCP from the app the user already runs, at `/mcp` on its own domain. It reuses the app's data layer, permission checks, auth and deploys.
- **Remote and stateless by default.** Streamable HTTP, a fresh server instance per request, nothing kept in memory between requests. Go local (stdio) only when the server must touch the user's own machine.
- **TypeScript SDK v2** unless the app is Python. Register everything inside a factory function.
- **Few, outcome-shaped tools.** 3–7 tools that each finish a job the user would ask for, not one tool per API endpoint.
- **Annotate everything.** Every tool has a `title`, accurate hints, a description that says when to use it, and `.describe()` on every input.
- **OAuth with the app's existing identity provider** for anything that touches user data remotely. The MCP server verifies tokens; it never issues them unless it has to.

## 2. What changed in 2026

The 2026-07-28 spec is a breaking redesign. Code written for the 2025 generation (`@modelcontextprotocol/sdk`, `server.tool(...)`, `StreamableHTTPServerTransport` + `connect()`, session maps, SSE endpoints) is the old way. Migrate with the SDK's codemod and upgrade guide (https://ts.sdk.modelcontextprotocol.io/v2/ → Migration).

- **Stateless core.** No `initialize` handshake and no `Mcp-Session-Id`. Every request carries its protocol version and client capabilities in `_meta`. Servers must implement `server/discover` (the SDK does this for you).
- **State lives in handles.** Anything that must survive between calls is a server-minted ID passed back as an ordinary tool argument (e.g. `draft_id`), backed by your own storage.
- **Multi Round-Trip Requests (MRTR).** Server-pushed requests (elicitation, sampling, roots) are replaced: the handler returns `resultType: "input_required"` with `inputRequests`, and the client retries the same call with `inputResponses`. Every result now carries `resultType`.
- **Notifications.** `subscriptions/listen` (one long-lived POST stream) replaces the GET stream and `resources/subscribe`. Progress still flows on the request's own response stream. SSE resumability (`Last-Event-ID`) is gone.
- **HTTP headers.** `Mcp-Method` and `Mcp-Name` are required on Streamable HTTP POSTs (the SDKs set them).
- **Caching.** List and read results carry `ttlMs` and `cacheScope`. Return tools in a deterministic order so clients and prompt caches can reuse them.
- **Schemas.** `inputSchema` and `outputSchema` accept any JSON Schema 2020-12. `structuredContent` can be any JSON value.
- **Logging.** `logging/setLevel` and `ping` are removed. Log level travels per request in `_meta`.
- **Deprecated** (still work, don't adopt): Roots, Sampling, Logging (use stderr or OpenTelemetry), the HTTP+SSE transport, and Dynamic Client Registration (replaced by Client ID Metadata Documents).
- **Extensions.** Tasks (`io.modelcontextprotocol/tasks`) for long-running work, and MCP Apps (`io.modelcontextprotocol/ui`) for interactive UI.
- **Old clients still connect.** The TypeScript SDK's entry points serve 2025-era clients from the same factory by default (stateless on HTTP), so one server works for both generations.

## 3. Architecture decision path

| Situation | Build | Transport | Default host |
|---|---|---|---|
| Existing Next.js / Nuxt / SvelteKit app | `mcp-handler` route | Streamable HTTP | Wherever the app runs |
| Existing Express / Hono / Fastify / Node app | SDK `createMcpHandler` + official adapter | Streamable HTTP | Wherever the app runs |
| Existing Cloudflare Workers app | Agents SDK `createMcpHandler` (+ `workers-oauth-provider`) | Streamable HTTP | Cloudflare |
| Existing Python app (FastAPI, Django, Flask) | Python SDK `MCPServer`, mounted | Streamable HTTP | Wherever the app runs |
| Existing app in another stack | Standalone remote server calling the app's API | Streamable HTTP | Cloudflare Workers |
| Standalone, one user, their machine | SDK `serveStdio` | stdio | User's machine (npm + `.mcpb`) |
| Standalone, many users or claude.ai/ChatGPT | SDK `createMcpHandler` on Workers | Streamable HTTP | Cloudflare Workers |

Notes:
- claude.ai, Claude mobile and ChatGPT only connect to public HTTPS servers. A local stdio server reaches them only through a desktop app.
- Cloudflare's `McpAgent` (Durable Object based) is deprecated and feature-frozen. Use `createMcpHandler`.
- For Python without an existing app, the official SDK's `MCPServer` is the default. The standalone `fastmcp` package is a reasonable alternative if the user already uses it.

## 4. Serving recipes

Register tools inside a **factory** that builds and returns a fresh `McpServer`. The serving entry calls it once per HTTP request (or once per stdio connection). Create connection pools and caches once at module scope and close over them. Never register on a shared instance.

### TypeScript SDK — local (stdio)

```ts
import { McpServer } from '@modelcontextprotocol/server';
import { serveStdio } from '@modelcontextprotocol/server/stdio';

const handle = serveStdio(() => {
    const server = new McpServer({ name: 'acme', version: '1.0.0' });
    // server.registerTool(...)
    return server;
});
process.on('SIGINT', () => void handle.close());
```

stdout is the protocol channel. Log with `console.error` only. One `console.log` corrupts the stream.

### TypeScript SDK — HTTP with Express

```ts
import { createMcpExpressApp } from '@modelcontextprotocol/express';
import { toNodeHandler } from '@modelcontextprotocol/node';
import { createMcpHandler, McpServer } from '@modelcontextprotocol/server';

const handler = createMcpHandler(({ authInfo }) => {
    const server = new McpServer({ name: 'acme', version: '1.0.0' });
    // register tools; authInfo is the verified caller (see §8)
    return server;
});

const app = createMcpExpressApp(); // express.json() + Host/Origin checks on localhost binds
const node = toNodeHandler(handler);
app.all('/mcp', (req, res) => void node(req, res, req.body));
app.listen(3000);
```

Install: `npm install @modelcontextprotocol/server @modelcontextprotocol/express @modelcontextprotocol/node express`. In production, bind publicly with `createMcpExpressApp({ host: '0.0.0.0', allowedHosts: ['api.example.com'] })`. Fastify has the same shape with `@modelcontextprotocol/fastify` (see its recipe in the SDK docs).

### TypeScript SDK — HTTP with Hono (also Bun, Deno, Workers)

```ts
import { createMcpHonoApp } from '@modelcontextprotocol/hono';
import { createMcpHandler, McpServer } from '@modelcontextprotocol/server';
import type { Context } from 'hono';

const handler = createMcpHandler(() => new McpServer({ name: 'acme', version: '1.0.0' }) /* + tools */);
const app = createMcpHonoApp();
app.all('/mcp', (c: Context) => handler.fetch(c.req.raw, { parsedBody: c.get('parsedBody') }));
export default app;
```

`handler.fetch` is a web-standard `(Request) => Promise<Response>`, so on any fetch runtime `export default handler` also works (put Host/Origin checks in front, see §9). Options worth knowing: `responseMode: 'json'` (never stream) and `legacy: 'reject'` (refuse 2025-era clients). Defaults are right for most servers.

### Next.js — `mcp-handler`

```ts
// app/api/mcp/route.ts
import { createMcpHandler } from 'mcp-handler';
import { z } from 'zod';

const handler = createMcpHandler((server) => {
  server.registerTool(
    'acme_search_invoices',
    {
      title: 'Search invoices',
      description: 'Find invoices by customer, status or date. Use for any question about what a customer owes or has paid.',
      inputSchema: z.object({ customer: z.string().describe('Customer name or ID') }),
      annotations: { readOnlyHint: true },
    },
    async ({ customer }, ctx) => ({ content: [{ type: 'text', text: `…` }] }),
  );
});

export { handler as GET, handler as POST };
```

Install: `npm install mcp-handler@^2 @modelcontextprotocol/server@^2 zod@^4`. The route path is a convention; the client URL is `https://<app>/api/mcp`. Version 2 has no `[transport]` route, Redis or SSE. In handlers, the caller is `ctx.http?.authInfo`. Wrap with `withMcpAuth` for OAuth (§8). Note `mcp-handler`'s callback receives the server to register on; the SDK's factory returns one.

### Cloudflare Workers — Agents SDK

```ts
import { createMcpHandler } from 'agents/mcp/server';
import { McpServer } from '@modelcontextprotocol/server';

function createServer() {
  const server = new McpServer({ name: 'acme', version: '1.0.0' });
  // server.registerTool(...)
  return server;
}

export default {
  fetch(request, env, ctx) {
    return createMcpHandler(createServer)(request, env, ctx);
  },
} satisfies ExportedHandler;
```

With OAuth via `workers-oauth-provider`: `export default new OAuthProvider({ apiRoute: '/mcp', apiHandler: createMcpHandler(createServer), defaultHandler: <your login/consent handler>, authorizeEndpoint: '/authorize', tokenEndpoint: '/token', ... })`. Start from Cloudflare's `mcp-worker` and `mcp-worker-authenticated` examples (github.com/cloudflare/agents/tree/main/examples), not the older `McpAgent` templates. Deploy with `npx wrangler deploy`.

### Python — official SDK

```python
from mcp.server import MCPServer

mcp = MCPServer("Acme")

@mcp.tool()
def search_invoices(customer: str) -> str:
    """Find invoices for a customer. Use for any question about what a customer owes or has paid."""
    ...
```

Type hints are the schema, the docstring is the description. Run locally with `mcp.run()` (stdio) or `uv run mcp run server.py --transport streamable-http`. To embed in FastAPI/Starlette, `mcp.streamable_http_app()` returns an ASGI app to mount. The host app's lifespan must enter `mcp.session_manager.run()`, and a deployed app must pass a `transport_security=` host allowlist or every request gets `421`. Read https://py.sdk.modelcontextprotocol.io/run/asgi/ before wiring it.

## 5. Designing tools

The model sees only each tool's name, title, description, input schema and annotations. Design them like a product surface.

### Shape

- **3–7 tools that each complete a job.** Merge list/get/filter into one search tool. Combine multi-step workflows the AI would always chain (e.g. `schedule_meeting` finds a slot and books it).
- **Names:** `service_verb_noun` in snake_case (`acme_search_invoices`, `acme_create_refund`). The prefix stops clashes when users connect several servers. Keep to letters, digits and underscores, under 64 characters.
- **Description:** what it does, **when to use it** (and when not to), what it returns, and any limits. Write it for a smart new colleague. The first sentence carries the most weight.
- **Inputs:** `.describe()` on every field. Use enums for fixed choices, defaults for optional fields, and accept human identifiers (names, emails) rather than internal IDs where you can resolve them.

### Registering a tool (TypeScript SDK v2)

```ts
import * as z from 'zod/v4';

server.registerTool(
    'acme_search_invoices',
    {
        title: 'Search invoices',
        description:
            'Search invoices by customer, status and date range. Use for any question about what a customer owes, has paid, or was billed. Returns newest first.',
        inputSchema: z.object({
            customer: z.string().describe('Customer name, email or ID'),
            status: z.enum(['open', 'paid', 'overdue', 'any']).default('any').describe('Invoice status filter'),
            detail: z.enum(['concise', 'detailed']).default('concise').describe('concise = one line per invoice; detailed = line items too'),
            cursor: z.string().optional().describe('Pass nextCursor from a previous call to get the next page')
        }),
        outputSchema: z.object({
            invoices: z.array(z.object({ id: z.string(), total: z.number(), status: z.string() })),
            nextCursor: z.string().optional()
        }),
        annotations: { readOnlyHint: true, openWorldHint: false }
    },
    async ({ customer, status, detail, cursor }, ctx) => {
        const page = await invoices.search({ customer, status, cursor, user: ctx.http?.authInfo });
        return {
            content: [{ type: 'text', text: formatInvoices(page, detail) }],
            structuredContent: { invoices: page.items, nextCursor: page.nextCursor }
        };
    }
);
```

The SDK turns the Zod schema into JSON Schema (descriptions included), validates arguments before the handler runs, and validates `structuredContent` against `outputSchema`. Arguments that fail validation come back as an `isError: true` result automatically.

### Annotations

| Hint | Set it when | Effect in clients |
|---|---|---|
| `readOnlyHint: true` | The tool changes nothing | May run without asking |
| `destructiveHint: true` | It deletes, overwrites, sends, pays, or is otherwise hard to undo | Asks the user first |
| `idempotentHint: true` | Calling twice with the same input has the same effect as once | Safe to retry |
| `openWorldHint: true` | It reaches the open internet or third parties | Signals untrusted content |

Every tool needs a `title` and at least the read-only or destructive hint. Anthropic's connector directory rejects tools without them. Hints are hints: enforce permissions in the handler regardless.

### Responses

- **Concise by default.** Offer a `detail` (or `response_format`) input for the long version. Return names and meaningful fields, not raw database rows or opaque IDs alone.
- **Paginate with cursors.** Return `nextCursor` and a sensible default page size. Claude Code warns above about 10,000 tokens of tool output and truncates at 25,000 by default, so cap and summarise large results.
- **Structured output** (`outputSchema` + `structuredContent`) when a client or MCP App will use the data. Always include a readable `content` text block too.
- **Errors the model can fix.** Return `{ content: [{ type: 'text', text: 'No customer "Acm". Did you mean "Acme Ltd" (cus_123)?' }], isError: true }`. Thrown exceptions also become `isError` results with the message as text, so write useful messages. Protocol errors (bad request shapes, unknown resources) are JSON-RPC errors; the SDK handles those, or throw `ProtocolError` in resource/prompt callbacks.

## 6. Resources, prompts and MCP Apps

- **Resources** are read-only data the client can attach as context (docs, schemas, records by URI). Use them for reference material, not for actions. Most servers launch with tools only.
- **Prompts** are user-chosen templates (often shown as slash commands). Add one only for a workflow users will pick deliberately.
- **MCP Apps** (`io.modelcontextprotocol/ui`) let one tool render interactive HTML in the chat, in a sandboxed iframe. Supported by Claude (web and desktop), VS Code Copilot, Goose and others; other clients just see the text result, so the text must stand alone.
  - The UI is a resource with a `ui://` URI and MIME type `text/html;profile=mcp-app`, usually one bundled HTML file.
  - The tool links to it in its definition with `_meta: { ui: { resourceUri: 'ui://acme/invoice-dashboard' } }` (the older flat `_meta["ui/resourceUri"]` is deprecated).
  - The resource's `_meta.ui.csp` lists external origins the page may load from; `_meta.ui.permissions` requests things like the camera.
  - The page talks to the host over `postMessage`: it receives the tool result and can call other tools on your server.
  - Use the helpers in `@modelcontextprotocol/ext-apps`: `registerAppTool` and `registerAppResource` from `@modelcontextprotocol/ext-apps/server` on the server, and the `App` class (or `@modelcontextprotocol/ext-apps/react`) in the page. Read the quickstart at https://apps.extensions.modelcontextprotocol.io before writing it, and start from an example in github.com/modelcontextprotocol/ext-apps/tree/main/examples.

## 7. Asking the user mid-call, and state across calls

### `input_required` (replaces pushed elicitation)

A handler that needs a confirmation or a missing value returns `inputRequired(...)` instead of a result. The client asks the user and retries the call; the handler runs again and reads the answer. Write it "write-once": on every entry, read what has arrived and request only what's still missing.

```ts
import type { CallToolResult, InputRequiredResult } from '@modelcontextprotocol/server';
import { acceptedContent, createRequestStateCodec, inputRequired } from '@modelcontextprotocol/server';

const confirmSchema = z.object({ confirm: z.boolean() });

async ({ invoiceId }, ctx): Promise<CallToolResult | InputRequiredResult> => {
    const answer = acceptedContent(ctx.mcpReq.inputResponses, 'confirm', confirmSchema);
    if (answer?.confirm !== true) {
        return inputRequired({
            inputRequests: {
                confirm: inputRequired.elicit({ message: `Refund invoice ${invoiceId}?`, requestedSchema: confirmSchema })
            }
        });
    }
    // do the refund
}
```

- Elicitation schemas must be flat objects of primitives (strings, numbers, booleans, enums).
- `inputRequired.elicitUrl({ message, url })` sends the user to a URL (e.g. to connect a third-party account) instead of a form.
- `ctx.mcpReq.inputResponses` is client input: always validate it (`acceptedContent` does, with the schema you pass).
- The legacy shim serves the same handler to 2025-era clients by pushing a real elicitation request.
- Sampling and roots builders exist but are deprecated. Don't use them in new servers.

### `requestState` across rounds

For multi-step flows, return an opaque `requestState` with `inputRequired`; the client echoes it back. It's attacker-controlled on return, so seal it with the SDK's HMAC codec and only record what earlier rounds proved:

```ts
const stateCodec = createRequestStateCodec<{ step: string }>({ key: secretKeyBytes /* ≥32 bytes, shared across instances */, ttlSeconds: 600 });
const server = new McpServer({ name: 'acme', version: '1.0.0' }, { requestState: { verify: stateCodec.verify } });
// mint: requestState: await stateCodec.mint({ step: 'confirmed' })
// read: ctx.mcpReq.requestState<{ step: string }>()
```

It's signed, not encrypted. Keep secrets out.

### Handles across calls

For state that spans separate tool calls (a draft, an upload, a long job), mint an ID, store the state in your database or KV store keyed by that ID **and the user**, and return the ID for the model to pass to the next tool. Check ownership on every use. For long-running work, look at the Tasks extension before inventing your own polling.

## 8. Authentication and authorisation

### Choosing

| Case | Auth |
|---|---|
| Local stdio server acting as the user | None for local data. For third-party APIs, an API key from an environment variable, supplied by the client config or the `.mcpb` sensitive user config |
| Remote, public data only | None. Add rate limits |
| Remote, internal tool for one team | OAuth with the team's identity provider. A static API key header works in Claude Code, Cursor and VS Code, but in Claude's hosted apps only as a limited beta |
| Remote, the app's users and their data | OAuth with the app's existing identity provider |

### OAuth model (remote servers)

- The MCP server is an **OAuth resource server**. It verifies access tokens issued by an authorisation server (the app's identity provider: Auth0, Clerk, WorkOS, Stytch, Supabase, Cloudflare Access, Entra…). It doesn't issue tokens itself, except on Cloudflare where `workers-oauth-provider` can act as the authorisation server in front of a third-party login.
- **Discovery:** unauthenticated requests get `401` with `WWW-Authenticate: Bearer resource_metadata="https://…/.well-known/oauth-protected-resource/mcp"`. That URL serves Protected Resource Metadata (RFC 9728): `resource` equal to the exact MCP URL, and `authorization_servers` listing the issuer (Claude uses only the first).
- **Audience:** accept only tokens issued for this server (the `aud`/resource matches the MCP URL). Reject everything else.
- **No token passthrough.** Never forward the client's token to downstream APIs. Use the server's own credentials, scoped to the verified user.
- **Scopes:** gate the endpoint with required scopes, and step up per tool for sensitive actions.
- **Client registration:** the 2026 spec prefers Client ID Metadata Documents (CIMD) over Dynamic Client Registration (DCR). Claude uses CIMD only when the authorisation server metadata advertises `"client_id_metadata_document_supported": true` and `"none"` in `token_endpoint_auth_methods_supported`, otherwise it falls back to DCR. Support CIMD, and keep DCR on if the provider offers it.
- **Redirect URIs to allow:** `https://claude.ai/api/mcp/auth_callback` for Claude's hosted apps, and loopback `http://localhost/callback` and `http://127.0.0.1/callback` on **any port** for Claude Code and other native clients. Add each other target client's documented callback.
- **PKCE S256** must be supported and advertised. The token endpoint must accept `application/x-www-form-urlencoded`. Rotate refresh tokens and return `invalid_grant` when one is no longer valid.

### Wiring it (TypeScript SDK, Express)

```ts
import { createMcpExpressApp, getOAuthProtectedResourceMetadataUrl, mcpAuthMetadataRouter, requireBearerAuth } from '@modelcontextprotocol/express';

const mcpServerUrl = new URL('https://api.example.com/mcp');
const auth = requireBearerAuth({
    verifier: { verifyAccessToken },               // your function: token string → AuthInfo (set expiresAt and resource)
    requiredScopes: ['mcp'],
    resourceMetadataUrl: getOAuthProtectedResourceMetadataUrl(mcpServerUrl),
    expectedResource: mcpServerUrl                  // audience check
});
app.use(mcpAuthMetadataRouter({ oauthMetadata, resourceServerUrl: mcpServerUrl }));
app.all('/mcp', auth, (req, res) => void node(req, res, req.body));
```

Handlers read the caller as `ctx.http?.authInfo` (undefined over stdio). On fetch runtimes, `requireBearerAuth` and `oauthMetadataResponse` from `@modelcontextprotocol/server` do the same with web-standard requests. Upgrade `@modelcontextprotocol/express` together with the server package: early 2.0.x adapters ignored `expectedResource`. Per-tool scopes: `scopeChallenge: requireScopes('invoices:write')` in the tool config. Full guide: https://ts.sdk.modelcontextprotocol.io/v2/ → Serving → Authorization.

**Next.js:** `withMcpAuth(handler, verifyToken, { required: true, requiredScopes: [...], resourceMetadataPath: '/.well-known/oauth-protected-resource' })`, plus `protectedResourceHandler` at `app/.well-known/oauth-protected-resource/route.ts`. See `docs/AUTHORIZATION.md` in the `mcp-handler` repo.

**Cloudflare:** `workers-oauth-provider` wraps the handler as shown in §4. See Cloudflare's Authorization guide for provider-specific examples.

## 9. Security

- **Treat tool output as untrusted.** Content from web pages, emails, tickets or user uploads can carry prompt injection. Label it as data in the response, never follow instructions found in it server-side, and keep destructive tools behind `destructiveHint` plus an `input_required` confirmation.
- **Least privilege.** Each tool does only what its name says, with the caller's permissions, through the app's existing authorisation checks.
- **DNS rebinding.** Local HTTP servers bind to `127.0.0.1`, not `0.0.0.0`, and validate `Host` and `Origin`. The SDK's `createMcpExpressApp` / `createMcpHonoApp` / `createMcpFastifyApp` do this by default on localhost binds; on public binds pass `allowedHosts`. On bare `node:http` use `localhostHostValidation()` / `localhostOriginValidation()` from `@modelcontextprotocol/node`; on fetch runtimes use `hostHeaderValidationResponse` / `originValidationResponse`.
- **Seal round-tripped state.** Anything the client echoes back (`requestState`, cursors that encode filters, handles) is signed (HMAC) or looked up server-side and ownership-checked.
- **Validate everything.** Schemas validate tool arguments; also validate `inputResponses`, resource URIs and anything parsed from strings. Cap array sizes (`maxToolInputElements` on `McpServer`).
- **Rate limit** per user or per token, and time out slow downstream calls.
- **Secrets** live in environment variables or the platform's secret store. Never in code, `server.json`, `manifest.json`, logs or tool output. Don't return or log `authInfo.token`.
- **Logs:** stderr for stdio servers, OpenTelemetry or the platform's logs for remote ones. Never log tokens or full personal data.

## 10. Testing

- **MCP Inspector** (supports the 2026 spec):
  - Web UI: `npx @modelcontextprotocol/inspector`, then enter the URL (`http://localhost:3000/mcp`) or a stdio command. Use it to list and call every tool, including bad inputs.
  - Scriptable smoke test: `npx @modelcontextprotocol/inspector --cli --transport http --server-url <url> --method tools/list`, or `npx @modelcontextprotocol/inspector --cli node build/index.js --method tools/list` for stdio. Pin the version in CI.
- **In-memory tests:** the SDK docs' "Test a server" page wires a `Client` to your server in-process, ideal for unit tests of each tool.
- **Claude Code:**
  - Remote: `claude mcp add --transport http acme http://localhost:3000/mcp`
  - stdio: `claude mcp add --transport stdio acme -- node build/index.js` (add `--env KEY=value` before the name for secrets)
  - Then `/mcp` to check the connection or sign in.
- **Tool choice test:** in a fresh session, ask for each job in the user's own words without naming the tool. Check the right tool is chosen with sensible arguments. If not, fix the name and description.
- **One more client** from the brief's targets (Cursor, VS Code, ChatGPT, Claude Desktop). ChatGPT and claude.ai need a public HTTPS URL; use a deploy preview or a tunnel.
- **Auth test:** connect from a clean client, complete sign-in, call a tool, then revoke or expire the token and confirm a clean `401` and re-auth.

## 11. Distribution

### Install snippets (put these in the README)

- **Claude Code:** `claude mcp add --transport http <name> <url>` (remote) or `claude mcp add --transport stdio <name> -- npx -y <package>` (local). Team-shared: `--scope project` writes `.mcp.json`.
- **Claude (web, desktop, mobile):** Customize → Connectors → add a custom connector with the URL (remote; on Team and Enterprise an Owner adds it for the organisation). Local servers: open the `.mcpb` file in Claude Desktop.
- **Cursor:** `.cursor/mcp.json` (project) or `~/.cursor/mcp.json`: `{ "mcpServers": { "<name>": { "url": "<url>" } } }`, or `command`/`args` for stdio.
- **VS Code:** `.vscode/mcp.json`: `{ "servers": { "<name>": { "type": "http", "url": "<url>" } } }` (note the `servers` key).
- **Codex:** `codex mcp add <name> --url <url>` then `codex mcp login <name>` for OAuth; stdio: `codex mcp add <name> -- npx -y <package>`.
- **ChatGPT:** remote HTTPS only. In developer mode (paid plans), create a connector with the URL. Check OpenAI's current docs for the menu path.
- Clients that only speak stdio can reach a remote server through `npx mcp-remote <url>`.

Check each client's docs before publishing snippets; config keys differ and change.

### MCP Registry (the public catalogue many clients read)

1. Install `mcp-publisher` (`brew install mcp-publisher`, or the release binary).
2. `mcp-publisher init` writes a `server.json` template. Set `name` (e.g. `io.github.<user>/<server>`), `description`, `version`, and either `packages` (npm/PyPI/OCI/`mcpb`) or `remotes` (`[{ "type": "streamable-http", "url": "https://…/mcp" }]`).
3. Prove ownership: for npm, add `"mcpName": "<same name>"` to `package.json` and publish the package first. For `.mcpb`, host it on GitHub/GitLab releases with `fileSha256` in `server.json`.
4. `mcp-publisher login github` (namespace `io.github.<user>/*`), or `login dns` for a `com.example/*` namespace.
5. `mcp-publisher validate`, then `mcp-publisher publish`. Automate later with `login github-oidc` in GitHub Actions.

Only the `io.modelcontextprotocol.registry/publisher-provided` key survives in `server.json` `_meta`.

### MCP Bundles (`.mcpb`, local servers)

A zip of the server plus `manifest.json` that installs with one click in Claude Desktop. `npm install -g @anthropic-ai/mcpb`, then `mcpb init` (writes the manifest), `mcpb validate .`, `mcpb pack .`. Declare API keys under `user_config` with `"sensitive": true` and pass them in as `${user_config.<key>}` environment variables. Include a `privacy_policies` array if the server sends data anywhere. Optional: `mcpb sign`.

### Anthropic's connector directory (remote servers)

Submit at claude.ai/directory/manage (any paid Claude plan; Owner on Team/Enterprise). Requirements: public HTTPS URL; every tool has a `title` and `readOnlyHint` or `destructiveHint`; OAuth for user data (CIMD or DCR work by default); documentation URL, privacy policy URL, support contact and icon; a fully populated test account for reviewers; every tool tested in MCP Inspector or as a custom connector. Submissions are scanned and listed as Community connectors; some get human review. The directory no longer accepts local `.mcpb` servers on their own. Ship a local server inside a Claude Code plugin instead.

### Versioning

Semver in the server's `version`, `package.json`, `server.json` and `manifest.json`, kept identical. Never rename tools in a minor release: clients and users' saved prompts depend on them. Keep a `CHANGELOG.md`.

## 12. Patterns to avoid

- One tool per REST endpoint, or 30+ tools. The model picks badly and context fills up.
- Vague descriptions ("Gets data"), missing `.describe()` on inputs, or internal IDs as the only way to name things.
- Code from the 2025 SDK generation: `@modelcontextprotocol/sdk` imports, `server.tool(...)`, session maps keyed by `Mcp-Session-Id`, SSE endpoints, Redis for sessions, Cloudflare `McpAgent` for new servers.
- Keeping user state in server memory between requests. Use handles backed by storage.
- Pushing elicitation or sampling from the server (`elicitInput`, `requestSampling`). Return `inputRequired` instead.
- Adopting deprecated features: Roots, Sampling, the Logging capability, HTTP+SSE, DCR-only auth.
- `console.log` in a stdio server.
- Token passthrough, skipping the audience check, or tokens in query strings.
- Binding a local HTTP server to `0.0.0.0` without Host/Origin validation.
- Unsigned `requestState`, cursors or handles that a client could forge.
- Huge unpaginated responses, raw HTML or full database rows in tool output.
- Throwing bare errors with no hint about how to fix the call.
- Destructive tools without `destructiveHint` and a confirmation step.
- Secrets in `server.json`, `manifest.json`, `.mcp.json` examples or the README.
