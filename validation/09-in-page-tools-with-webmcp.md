## Chapter 9: In-page tools with WebMCP

| # | Claim / API / listing (short) | Status | Source URL | Retrieved | Note |
| --- | --- | --- | --- | --- | --- |
| 1 | WebMCP spec: Draft Community Group Report dated 2 Nov 2026, W3C WebML CG, not a W3C standard | VERIFIED | https://webmachinelearning.github.io/webmcp/ | 2026-11-02 | R3 4.1 |
| 2 | Four editors: Walderman, Dallstream (Microsoft), Sagar, Farolino (Google) | VERIFIED | https://webmachinelearning.github.io/webmcp/ | 2026-11-02 | R3 4.2 |
| 3 | API: document.modelContext with registerTool/getTools/executeTool, events toolchange/toolactivated/toolcancel | VERIFIED | https://webmachinelearning.github.io/webmcp/#idl-index | 2026-11-02 | webmcp FACTS §1.2, probe §3 |
| 4 | outputSchema added by PR #254, merged 2 Nov 2026 13:10 UTC | VERIFIED | https://github.com/webmachinelearning/webmcp/pull/254 | 2026-11-02 | R3 4.3 |
| 5 | Declarative API not in spec text, removed by PR #338 (8 Oct 2026), documented by Chrome | VERIFIED | https://github.com/webmachinelearning/webmcp/pull/338 | 2026-11-02 | webmcp FACTS §1.1 |
| 6 | Chrome flag chrome://flags/#enable-webmcp-testing, equivalent --enable-features=WebMCPTesting | VERIFIED | https://developer.chrome.com/docs/ai/webmcp | 2026-11-02 | webmcp FACTS §1.7, probe; my tests use the switch |
| 7 | Origin trial from Chrome 149, extended to 162 (extension 28 Sep 2026) | VERIFIED | https://chromestatus.com/feature/5117755740913664 | 2026-11-02 | webmcp FACTS §1.7 |
| 8 | Edge origin trial expiry 30 Mar 2027 | VERIFIED | https://developer.microsoft.com/microsoft-edge/origin-trials/trials/0b76fe60-b266-458e-a285-04e375c0c31a | 2026-11-02 | webmcp FACTS §1.7 |
| 9 | WebKit oppose (#670, closed 11 Jun 2026) | VERIFIED | https://github.com/WebKit/standards-positions/issues/670 | 2026-11-02 | webmcp FACTS §1.9 |
| 10 | Mozilla neutral (#1412), refreshed position announced, not published | VERIFIED | https://github.com/mozilla/standards-positions/issues/1412 | 2026-11-02 | webmcp FACTS §1.9 |
| 11 | TAG review #1238 open, early comment 26 Oct 2026 (agent-only functionality, JSON Schema, rename to 'Tools') | VERIFIED | https://github.com/w3ctag/design-reviews/issues/1238#issuecomment-6410471845 | 2026-11-02 | webmcp FACTS §2 item 4 |
| 12 | Agentic Web WG charter in refinement after TPAC 2026 | VERIFIED | https://github.com/w3c/strategy/issues/576 | 2026-11-02 | webmcp FACTS §1.9 |
| 13 | Chrome 156 stable 20 Oct 2026, 157 stable 3 Nov 2026 | VERIFIED | https://chromiumdash.appspot.com/fetch_releases?channel=Stable&platform=Windows | 2026-11-02 | webmcp FACTS §1.7 |
| 14 | Tests run on Chrome for Testing 156.0.8078.4 via Playwright 1.64.1 | VERIFIED | local: navigator.userAgent HeadlessChrome/156.0.8078.4; demos package.json | 2026-11-02 | my probe 2 Nov 2026 |
| 15 | Radar: WebMCP on 1.42% of 115,468 scanned domains (1,643); e-commerce 928 of 18,927 (~4.9%) | VERIFIED | https://radar.cloudflare.com/ai-insights#adoption-of-ai-agent-standards | 2026-11-02 | FACTS headline 3 and 4, data dated 2026-11-02 |
| 16 | Shopify storefronts (allbirds, brooklinen, kith) register WebMCP adapter with search_catalog, add_to_cart, proceed_to_checkout | VERIFIED | https://www.allbirds.com (R1 scan) | 2026-11-02 | FACTS headline 4; 3 stores observed, not all Shopify |
| 17 | Shopify comment 'deploys WebMCP across millions of storefronts' on W3C charter thread | VERIFIED | https://github.com/w3c/strategy/issues/576 | 2026-11-02 | single comment, presented as quote |
| 18 | compare-mcp quote: WebMCP 'connects agents to your web page — a proposed browser standard...' | VERIFIED | https://developer.chrome.com/docs/ai/webmcp/compare-mcp | 2026-11-02 | webmcp FACTS §2 item 5, page updated 27 Oct 2026 |
| 19 | best-practices: share the application service, register tools all at once (roll back), explicit commit points | VERIFIED | https://developer.chrome.com/docs/ai/webmcp/best-practices | 2026-11-02 | webmcp FACTS §2 item 2, updated 30 Oct 2026, byline includes Maxim Salnikov |
| 20 | build-tools: enforcement in application logic 'beyond readOnlyHint or untrustedContentHint', pin versions | VERIFIED | https://developer.chrome.com/docs/ai/webmcp/build-tools | 2026-11-02 | webmcp FACTS §2 item 3, updated 30 Oct 2026, byline includes Maxim Salnikov |
| 21 | Duplicate tool name with declarative form -> InvalidStateError 'Duplicate tool name' in Chromium 156 | VERIFIED | local probe, Chrome for Testing 156.0.8078.4 | 2026-11-02 | my probe 2 Nov 2026 |
| 22 | Declarative schema: select -> anyOf/const/title + enum, number min/max -> minimum/maximum/multipleOf, date -> format date + appended format sentence | VERIFIED | local probe + https://developer.chrome.com/docs/ai/webmcp/declarative-api | 2026-11-02 | schema printed in chapter is real output, shortened |
| 23 | toolparamdescription else label (else aria-description) | VERIFIED | https://developer.chrome.com/docs/ai/webmcp/declarative-api | 2026-11-02 | webmcp FACTS §1.5 |
| 24 | Chrome 156 ignores toolparamdescription on a checkbox group (features array has no description) | VERIFIED | local probe (getTools inputSchema keys type, items, uniqueItems) | 2026-11-02 | observation, one browser version |
| 25 | :tool-form-active and :tool-submit-active pseudo-classes | VERIFIED | https://developer.chrome.com/docs/ai/webmcp/declarative-api | 2026-11-02 | webmcp FACTS §1.5; test asserts :tool-form-active |
| 26 | SubmitEvent.agentInvoked and respondWith(promise) after preventDefault() | VERIFIED | https://developer.chrome.com/docs/ai/webmcp/declarative-api | 2026-11-02 | page read 2 Nov 2026 |
| 27 | Navigating right after respondWith resolves loses the answer, agent gets the next page instead | VERIFIED | local test, Chromium 156 | 2026-11-02 | observation; my debug runs 2 Nov 2026 |
| 28 | A declarative tool that navigates (no respondWith) completes with the next page's JSON-LD array | VERIFIED | local test ch09-webmcp.spec.js; Chrome docs silent (declarative page, updated 25 Sep 2026) | 2026-11-02 | observation, undocumented, labelled as such |
| 29 | Chrome docs: toolautosubmit triggers 'submission and a navigation' | VERIFIED | https://developer.chrome.com/docs/ai/webmcp/declarative-api | 2026-11-02 | page read 2 Nov 2026 |
| 30 | Thrown error in execute -> executeTool rejects UnknownError, message lost (Chromium 156), spec says specific DOMExceptions (PR #339) | VERIFIED | https://github.com/webmachinelearning/webmcp/pull/339 + probe | 2026-11-02 | webmcp FACTS §3 |
| 31 | executeTool resolves a string, objects serialised as JSON, getTools alphabetical | VERIFIED | local probe | 2026-11-02 | webmcp FACTS §3 and my tests |
| 32 | Chromium 156 accepts outputSchema at registerTool but getTools does not return it | VERIFIED | local probe + test 'accepts outputSchema but does not report it' | 2026-11-02 | my probe 2 Nov 2026 |
| 33 | Four annotations readOnlyHint, consequentialHint, untrustedContentHint, debugging, all default false | VERIFIED | https://webmachinelearning.github.io/webmcp/ | 2026-11-02 | R3 4.6 |
| 34 | debugging annotation available from Chrome 156 | VERIFIED | https://developer.chrome.com/docs/ai/webmcp/imperative-api | 2026-11-02 | webmcp FACTS §1.7 |
| 35 | No unregisterTool(), unregister by aborting the AbortSignal | VERIFIED | https://webmachinelearning.github.io/webmcp/ | 2026-11-02 | webmcp FACTS §1.2 |
| 36 | Since Chrome 153 unregister without cancelling in-flight calls | VERIFIED | https://developer.chrome.com/docs/ai/webmcp/imperative-api | 2026-11-02 | webmcp FACTS §1.7 |
| 37 | toolchange fires per registration and unregistration | VERIFIED | local probe | 2026-11-02 | webmcp FACTS §3 |
| 38 | Chrome for Testing 149 + flag exposes navigator.modelContext, 156 only document.modelContext | VERIFIED | local probe | 2026-11-02 | webmcp FACTS §3 |
| 39 | isitagentready webMcp check accepts document.modelContext.registerTool, legacy navigator.modelContext, or toolname+tooldescription forms | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | R1 §1 check 15 |
| 40 | isitagentready level ignores WebMCP | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | R1 §1 levels |
| 41 | isitagentready headless check can time out on heavy pages, late registration missed | VERIFIED | R1 §1 pitfalls | 2026-11-02 | research observation |
| 42 | Nordlys passes isitagentready webMcp from Chapter 2 | OPINION | reasoning from the check definition | 2026-11-02 | not scanned (local server) |
| 43 | Polyfill webmachinelearning/webmcp-polyfill Apache-2.0, created Aug 2026 | VERIFIED | https://github.com/webmachinelearning/webmcp-polyfill | 2026-11-02 | R3 4.16 |
| 44 | @mcp-b/webmcp-polyfill 6.0.3 temporary, 'will eventually be removed' | VERIFIED | https://registry.npmjs.org/@mcp-b%2fwebmcp-polyfill | 2026-11-02 | R3 4.17; npm view 6.0.3 on 2 Nov 2026 |
| 45 | @mcp-b/global 6.0.3 MIT, transports, auto-detects native | VERIFIED | https://registry.npmjs.org/@mcp-b%2fglobal | 2026-11-02 | R3 4.19; npm view 6.0.3 (modified 2026-10-14) |
| 46 | Frameworks: React use-webmcp-tool/useWebMCP, Vue @vueuse/core useWebMCP, Angular Signal Forms, webmcp-types | VERIFIED | https://developer.chrome.com/docs/ai/webmcp/imperative-api | 2026-11-02 | webmcp FACTS §1.8 |
| 47 | Cross-origin: allow="tools", exposedTo, fromOrigins (PR #326, 27 Oct 2026) | VERIFIED | https://github.com/webmachinelearning/webmcp/pull/326 | 2026-11-02 | webmcp FACTS §1.6 |
| 48 | DevTools Application panel WebMCP pane | VERIFIED | https://developer.chrome.com/docs/devtools/application/webmcp | 2026-11-02 | webmcp FACTS §1.8 |
| 49 | chrome-devtools-mcp 1.12.0 (22 Oct 2026), list_webmcp_tools/execute_webmcp_tool with --categoryExperimentalWebmcp | VERIFIED | https://developer.chrome.com/blog/agent-ready-toolkit | 2026-11-02 | R1 §4 facts 10, 13; webmcp FACTS §1.8 |
| 50 | CDP WebMCP domain WebMCP.enable / invokeTool / toolResponded | VERIFIED | local tests (ch09-webmcp.spec.js) | 2026-11-02 | experimental domain |
| 51 | Lighthouse 13.6.0 released 27 Oct 2026, agentic-browsing 7 audits | VERIFIED | https://github.com/GoogleChrome/lighthouse/releases/tag/v13.6.0 | 2026-11-02 | R1 §5 |
| 52 | webmcp-registered-tools informative, warns > 40 tools | VERIFIED | Lighthouse 13.6.0 source | 2026-11-02 | R1 §5 |
| 53 | webmcp-form-coverage informative when failing, passes when all covered | VERIFIED | Lighthouse 13.6.0 source + my runs | 2026-11-02 | R1 §5 |
| 54 | webmcp-schema-validity: errors 0, warnings 0.5; issues come from Chrome (CDP) | VERIFIED | Lighthouse 13.6.0 core/audits/webmcp-schema-validity.js | 2026-11-02 | read 2 Nov 2026 |
| 55 | WebMCP audits need Chrome 150+ and OT or flag, late registration may be missed | VERIFIED | https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring | 2026-11-02 | R1 §5 facts |
| 56 | Nordlys Lighthouse table (before/after) | VERIFIED | my runs 2 Nov 2026, Lighthouse 13.6.0, Chrome for Testing 156, --enable-features=WebMCPTesting | 2026-11-02 | raw JSON kept in /tmp during the run |
| 57 | start_booking navigation race (agent got empty output with 50 ms delayed navigation) | VERIFIED | local CDP test, 5 of 5 runs | 2026-11-02 | observation |
| 58 | Login form deliberately not a tool | OPINION | author's design decision | 2026-11-02 | see Chapter 14 |
| 59 | Recommendation: skip polyfill for public sites | OPINION | author | 2026-11-02 | reasoned in text |

## Demos

- Layer: `nordlys-cabins/layers/09-webmcp/` (index.js, public/tools.js, public/forms.js, public/webmcp.css). No new dependencies.
- Tests: `node --test tests/ch09-webmcp.test.js` (7 pass) and `npx playwright test tests/ch09-` (11 pass: ch09-webmcp.spec.js 10 with `--enable-features=WebMCPTesting`, ch09-webmcp-off.spec.js 1 without). Run 2 Nov 2026 in a copy of the demos tree with all complete layers up to 9 enabled.
- Versions: Node 22.23.2 (engines says >=24, tests pass on 22), @playwright/test 1.64.1, Chrome for Testing 156.0.8078.4 (chromium-1248), hono 4.13.16, @hono/node-server 2.1.6. Lighthouse 13.6.0 for the scores table.
- Listings 9.1–9.9 are byte-identical excerpts of the files above (checked by script).

## Figures

- figure-9-1 (three doors: API, MCP server, WebMCP in the guest's browser)
- figure-9-2 (sequence: agent prepares, guest commits, book_cabin)
- figure-9-3 (tool map per page: script vs form)
