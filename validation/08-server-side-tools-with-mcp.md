## Chapter 8: Server-side tools with the Model Context Protocol

Writer W3, 2026-11-02. Every claim, number, name, status and date in the chapter, with its source.

| # | Claim / API / listing (short) | Status | Source URL | Retrieved | Note |
|---|---|---|---|---|---|
| 1 | MCP created by Anthropic Nov 2024; donated to Agentic AI Foundation (LF directed fund, co-founded by Anthropic, Block, OpenAI) on 9 Dec 2025 | VERIFIED | https://blog.modelcontextprotocol.io/posts/2025-12-09-mcp-joins-agentic-ai-foundation/ | 2026-11-02 | R3 1.20 |
| 2 | Tier 1 SDKs TypeScript, Python, Go, C#; 'close to half-a-billion downloads a month' (maintainer-reported) | VERIFIED (self-reported number) | https://blog.modelcontextprotocol.io/posts/2026-07-28/ | 2026-11-02 | R3 1.18/1.19; flagged as project's own number |
| 3 | Host/client/server roles; tools, resources, prompts; JSON-RPC 2.0; Streamable HTTP | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28 | 2026-11-02 |  |
| 4 | Claude custom connectors (remote MCP) on all plans, Free limited to one | VERIFIED | https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp | 2026-11-02 | R3 1.42 |
| 5 | OpenAI docs titled 'Plugin development for ChatGPT and Codex'; MCP example installs v1 SDK; instructions: most important details in first 512 characters | VERIFIED | https://developers.openai.com/apps-sdk ; https://developers.openai.com/apps-sdk/build/mcp-server | 2026-11-02 | R3 1.43/1.44 |
| 6 | Copilot Studio MCP onboarding wizard | VERIFIED | https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-extend-action-mcp | 2026-11-02 | R3 1.46 |
| 7 | VS Code adds MCP servers; docs describe portable .mcp.json with mcpServers and label .vscode/mcp.json destinations deprecated | VERIFIED | https://code.visualstudio.com/docs/copilot/customization/mcp-servers | 2026-11-02 | read 2026-11-02 |
| 8 | Gemini Enterprise custom MCP connection Pre-GA, admin configured, updated 15 Sep 2026 | VERIFIED | https://support.google.com/g/answer/17106276 | 2026-11-02 | R3 1.45 |
| 9 | Current spec revision 2026-07-28; previous 2025-11-25 | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/changelog | 2026-11-02 | R3 1.1/1.2 |
| 10 | Removed initialize handshake and Mcp-Session-Id; per-request _meta; server/discover mandatory; Mcp-Method/Mcp-Name headers; ttlMs/cacheScope; deterministic tools/list; MRTR input_required; SSE resumability removed; Roots/Sampling/Logging and HTTP+SSE deprecated, 12-month window; Tasks moved to extension | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/changelog | 2026-11-02 | R3 1.3-1.15 |
| 11 | 'any request can land on any instance behind a plain round-robin load balancer'; cross-call state via handles passed as arguments | VERIFIED | https://blog.modelcontextprotocol.io/posts/2026-07-28/ | 2026-11-02 | R3 1.16/1.17 |
| 12 | subscriptions/listen replaces GET stream and resources/subscribe | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/changelog | 2026-11-02 | R3 1.6 |
| 13 | Real server/discover response (supportedVersions, capabilities, instructions, resultType, ttlMs 0, cacheScope private, serverInfo) | VERIFIED | demo: curl against npm start --upto=8, 2026-11-02 | 2026-11-02 |  |
| 14 | Missing _meta → -32602 'Invalid params … missing the required per-request envelope key(s): _meta'; header/body mismatch → -32020 | VERIFIED | demo run (curl and SDK), 2026-11-02 | 2026-11-02 |  |
| 15 | TS SDK v2: split packages server/client + Node/Express/Hono/Fastify adapters; ESM-only; Node 20+; Bun, Deno; Standard Schema incl. Zod v4 | VERIFIED | https://blog.modelcontextprotocol.io/posts/sdk-betas-2026-07-28/ | 2026-11-02 | R3 1.22 |
| 16 | @modelcontextprotocol/server 2.4.0 (2026-10-23), client 2.4.0, zod 4.6.7, v1 sdk 1.32.2 | VERIFIED | https://registry.npmjs.org/@modelcontextprotocol%2fserver ; https://registry.npmjs.org/zod ; https://registry.npmjs.org/@modelcontextprotocol%2fsdk | 2026-11-02 | npm registry read 2026-11-02 |
| 17 | createMcpHandler returns handler with fetch(Request)→Response; factory per request; handler 'validates no Host header, no Origin header, and no token' | VERIFIED | https://ts.sdk.modelcontextprotocol.io/v2/serving/http | 2026-11-02 | R3 1.25/1.26; used in demo |
| 18 | originValidationResponse helper exists in @modelcontextprotocol/server; cross-origin request → 403 -32000 'Invalid Origin: evil.example' | VERIFIED | demo run 2026-11-02 | 2026-11-02 |  |
| 19 | Codemod: npx @modelcontextprotocol/codemod@beta v1-to-v2 . | VERIFIED | https://blog.modelcontextprotocol.io/posts/sdk-betas-2026-07-28/ | 2026-11-02 | R3 1.27 |
| 20 | Tool names SHOULD be 1-128 chars, restricted charset | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/server/tools | 2026-11-02 | R3 1.28 |
| 21 | inputSchema/outputSchema may use any JSON Schema 2020-12 keyword | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/changelog | 2026-11-02 | R3 1.12 |
| 22 | Server validates structuredContent against outputSchema (SDK v2) | VERIFIED | demo experiment 2026-11-02 | 2026-11-02 | wrong type → isError 'Output validation error: Invalid structured content' |
| 23 | Roadmap: tools/call returning content and structuredContent 'has confused server and client authors'; progressive discovery | VERIFIED | https://modelcontextprotocol.io/development/roadmap | 2026-11-02 | R3 1.35 |
| 24 | Annotations since 2025-03-26: title, readOnlyHint, destructiveHint, idempotentHint, openWorldHint; hints not enforcement | VERIFIED | https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/ | 2026-11-02 | R3 1.30 |
| 25 | Clients MUST treat annotations as untrusted unless server trusted; 'there SHOULD always be a human in the loop…' | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/server/tools | 2026-11-02 | R3 1.29 |
| 26 | MCP Apps first official extension Jan 2026, built on MCP-UI and OpenAI Apps SDK; Claude, Goose, VS Code Insiders, ChatGPT | VERIFIED | https://blog.modelcontextprotocol.io/posts/2026-01-26-mcp-apps/ | 2026-11-02 | R3 1.31 |
| 27 | Cloudflare Agents createMcpHandler takes SDK v2 server factory | VERIFIED (snippet) | https://developers.cloudflare.com/agents/model-context-protocol/apis/handler-api/ | 2026-11-02 | R3 1.48 |
| 28 | Vercel mcp-handler 2.3.0 in Next.js App Router | VERIFIED (snippet + npm) | https://vercel.com/docs/mcp/deploy-mcp-servers-to-vercel | 2026-11-02 | R3 1.49 |
| 29 | Azure Functions self-hosted remote MCP (public preview); AWS AgentCore Runtime deploys MCP servers | VERIFIED | https://learn.microsoft.com/en-us/azure/azure-functions/self-hosted-mcp-servers ; https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-mcp.html | 2026-11-02 | titles read 2026-11-02 |
| 30 | MCP Inspector 2.13.0 (2026-10-28), Node >=22.19, web UI default, --cli, --tui; CLI tools/list and tools/call worked; --strict exit 0 | VERIFIED | https://registry.npmjs.org/@modelcontextprotocol%2finspector ; local run 2026-11-02 | 2026-11-02 | Node v22.23.2 |
| 31 | Legacy 2025-11-25 initialize answered from same endpoint (SSE event) | VERIFIED | demo curl 2026-11-02 + test | 2026-11-02 | SDK default |
| 32 | isitagentready does not test MCP tools; mcpServerCard checks discovery file; Lighthouse has no MCP audit | VERIFIED | https://isitagentready.com/llms-full.txt ; R1 | 2026-11-02 | R1 check table |
| 33 | Nordlys instructions 309 characters | VERIFIED | demo server.js | 2026-11-02 |  |
| 34 | Chapters 14, 16, 17 register MCP tools via the registry; 14 sets mcpAuth with member | VERIFIED | demos layers 14-oauth, 16-security, 17-consent (read 2026-11-02) | 2026-11-02 | other writers' layers |
| 35 | Listings 8.1-8.6 byte-identical | VERIFIED | demos nordlys-cabins/layers/08-mcp-server/*, tests/ch08-mcp-server.test.js | 2026-11-02 | script check |

### Demos

- Layer: `nordlys-cabins/layers/08-mcp-server/` (index.js, server.js, registry.js, tools.js, README.md).
- Tests: `nordlys-cabins/tests/ch08-mcp-server.test.js`, 7 tests, `node --test tests/ch08-*.test.js` → 7/7 pass (2026-11-02, Node v22.23.2, @modelcontextprotocol/server 2.4.0, @modelcontextprotocol/client 2.4.0, zod 4.6.7).
- Dependencies requested from the lead for the root package.json: `@modelcontextprotocol/server` 2.4.0 and `zod` 4.6.7 (dependencies), `@modelcontextprotocol/client` 2.4.0 (devDependency).
- MCP Inspector 2.13.0 CLI run by hand against `npm start -- --upto=8` (tools/list, tools/call, --strict).

### Figures

- figure-8-1: the Nordlys MCP server, host to booking service (figures/src/figure-8-1.svg)
- figure-8-2: the registry across Chapters 8, 14, 16, 17 and the extra.auth seam (figures/src/figure-8-2.svg)
