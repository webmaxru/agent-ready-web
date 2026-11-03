## Chapter 10: Designing tools agents can actually use

| # | Claim / API / listing (short) | Status | Source URL | Retrieved | Note |
| --- | --- | --- | --- | --- | --- |
| 1 | MCP tools/list carries name, title, description, inputSchema, outputSchema, annotations | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/server/tools | 2026-11-02 | spec page read 2 Nov 2026 |
| 2 | MCP tool names SHOULD be 1-128 chars, letters digits _ - . | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/server/tools | 2026-11-02 | 'Tool names SHOULD be between 1 and 128 characters' |
| 3 | structuredContent SHOULD also be returned as serialized JSON in a TextContent block | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/server/tools | 2026-11-02 | quote in spec |
| 4 | Tool execution errors with isError:true, 'actionable feedback ... self-correct and retry' | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/server/tools | 2026-11-02 | quote in spec |
| 5 | Human in the loop SHOULD be able to deny invocations, annotations untrusted unless trusted server | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/server/tools | 2026-11-02 | R3 1.29 |
| 6 | Annotations post 'Tool Annotations as Risk Vocabulary' by Ola Hungerford, 16 Mar 2026 | VERIFIED | https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/ | 2026-11-02 | page read 2 Nov 2026 |
| 7 | tools/list SHOULD be deterministic order (prompt cache), ttlMs + cacheScope on list results | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/changelog | 2026-11-02 | Key Changes page |
| 8 | Server-minted handles passed back as arguments (2026-07-28 blog) | VERIFIED | https://blog.modelcontextprotocol.io/posts/2026-07-28/ | 2026-11-02 | R3 1.17 |
| 9 | Copilot Studio REST API tools from OpenAPI, AgentCore Gateway OpenAPI->MCP | VERIFIED | https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-extend-action-rest-api ; https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html | 2026-11-02 | R3 3.17, 3.20 |
| 10 | OpenAI function calling: intern test, enums/object structure, combine sequential functions, fewer than 20 'soft suggestion' | VERIFIED | https://developers.openai.com/api/docs/guides/function-calling | 2026-11-02 | quotes read 2 Nov 2026 |
| 11 | OpenAI Chat Completions rejects 'nordlys.search' (pattern ^[a-zA-Z0-9_-]+$) and names > 128 | VERIFIED | local API call via model proxy, 2 Nov 2026 | 2026-11-02 | 400 error text quoted; 65 chars accepted |
| 12 | Anthropic Messages rejects dots, pattern ^[a-zA-Z0-9_-]{1,128}$ | VERIFIED | local API call via model proxy, 2 Nov 2026 | 2026-11-02 | 400 error text quoted |
| 13 | Anthropic 'Writing effective tools for agents' 11 Sep 2025: namespacing, user vs user_id, high signal, UUIDs, 25,000 token limit, actionable errors, metrics | VERIFIED | https://www.anthropic.com/engineering/writing-tools-for-agents | 2026-11-02 | quotes read 2 Nov 2026 |
| 14 | Chrome best practices: execution vs initiation (create-event vs start-event-creation-process), positive language, validate strictly in code loosely in schema, confirmation recompute state, evaluation-driven development | VERIFIED | https://developer.chrome.com/docs/ai/webmcp/best-practices | 2026-11-02 | updated 30 Oct 2026, quotes read 2 Nov 2026 |
| 15 | Chrome build-tools: pin versions | VERIFIED | https://developer.chrome.com/docs/ai/webmcp/build-tools | 2026-11-02 | updated 30 Oct 2026 |
| 16 | RFC 9457 Problem Details | VERIFIED | https://www.rfc-editor.org/rfc/rfc9457.html | 2026-11-02 | R3 3.10 |
| 17 | Idempotency-Key draft-08 dated 22 Oct 2026 | VERIFIED | https://www.ietf.org/archive/id/draft-ietf-httpapi-idempotency-key-header-08.txt | 2026-11-02 | R3 3.11 |
| 18 | Nordlys booking service remembers idempotency keys 24 h, refuses reused key with different input, replays result | VERIFIED | demos nordlys-cabins/layers/07-public-api/service.js | 2026-11-02 | code read |
| 19 | Eval models served as gpt-4.1-mini-2025-04-14, gpt-5.4-mini-2026-03-17, claude-haiku-4-5-20251001, claude-haiku-5-5 | VERIFIED | results/*.md 'models served as' | 2026-11-02 | API-reported model ids |
| 20 | Table 10.1 and Figure 10.2 numbers (before 21/18/24/45, after 55/54/52/55 of 55; per task) | VERIFIED | results/2026-11-02.json (before) and results/2026-11-02-after-final.json (after) | 2026-11-02 | re-scored with final checks |
| 21 | 40 before-episodes hit 404: 10 recovered, 14 estimated, 11 asked, 5 said cabin missing | VERIFIED | results/2026-11-02.json | 2026-11-02 | computed 2 Nov 2026 |
| 22 | Before set: cancel-needs-confirmation 0/20, 11 of 20 cancelled; retry 0/20 | VERIFIED | results/2026-11-02.json | 2026-11-02 | computed |
| 23 | After set: all 20 cancel-needs runs called find_booking only | VERIFIED | results/2026-11-02.json | 2026-11-02 | computed |
| 24 | Idempotency key reused in 19 of 20 main-run after episodes, 1 tried a fresh key first | VERIFIED | results/2026-11-02.json | 2026-11-02 | computed |
| 25 | Iterations: hint 4/5->0/5 (too-many, gpt-5.4-mini), nearMisses 5/5; description sentence 4/5 then 1/5; stayTotal 10/10 | VERIFIED | results/2026-11-02-iteration*.json, -after-v3.json | 2026-11-02 | results/README.md documents versions |
| 26 | Final run: claude-haiku-4-5 set acceptTerms without asking once (book-needs-confirmation 4/5), read 12/03 as Dec 3 twice | VERIFIED | results/2026-11-02-after-final.json | 2026-11-02 | episodes read |
| 27 | Two checks fixed after reading failures, re-scored without model calls | VERIFIED | eval.mjs --rescore, results/README.md | 2026-11-02 | before 23->24, 20->21; after v1 46->50, 54->55 |
| 28 | Lint: before 8 errors 20 warnings, after 0/0; audit '5 tools, 0 errors', 4 warnings on Ch8 tools | VERIFIED | node lint.mjs; tests/ch10-tool-design.test.js | 2026-11-02 | run 2 Nov 2026 |
| 29 | Small models are what most production agents use for tool calls | OPINION | author | 2026-11-02 | framed as reasoning |
| 30 | 'Before' set is a simulation of naive generation, not a product's output | OPINION | author | 2026-11-02 | stated in text and in before.mjs |

## Demos

- Layer: `nordlys-cabins/layers/10-tool-design/` (index.js: MCP tool find_booking + "Tool design" audit; lint.js; README.md). Depends on layers 07 and 08 (imports service.js and registry.js). Adds a fifth MCP tool at upto >= 10.
- Tests: `node --test tests/ch10-tool-design.test.js` (4 pass), together with ch07/ch08/ch09 node tests 25 pass, 2 Nov 2026, copy of the demos tree with layers up to 10 (and the other complete layers).
- Harness: `chapters/10-designing-tools-agents-can-use/` (package.json workspace, no dependencies; backend.mjs imports nordlys-cabins/src/store.js and layers/07 service.js; toolsets/before.mjs, after.mjs; tasks.mjs; models.mjs; agent.mjs; eval.mjs with --rescore; lint.mjs; test/harness.test.mjs 5 pass with a mock model; results/ with README).
- Real-model runs: OpenAI Chat Completions and Anthropic Messages APIs through the box's model proxy, 2 Nov 2026 22:17–22:27 UTC, default temperature, 5 trials (10 for iteration-3). Keys never printed or stored.
- Versions: Node 22.23.2, @modelcontextprotocol/server 2.4.0 / client 2.4.0, zod 4.6.7 (W3's layer 08 deps).

## Figures

- figure-10-1 (MCP, WebMCP and OpenAPI collapse to name/description/JSON Schema)
- figure-10-2 (eval results per model and per task, data from results/2026-11-02.json and -after-final.json)
