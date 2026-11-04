## Chapter 9: In-page tools with WebMCP

Carried from the v1 validation tables (validated 2026-11-02) for the v2 condensation, 2026-11-04. Status, source URL and retrieved date are unchanged from v1.

| # | Claim / API / listing (short) | Status | Source URL | Retrieved | Note | v1 row |
|---|---|---|---|---|---|---|
| 1 | WebMCP spec: Draft Community Group Report dated 2 Nov 2026, W3C WebML CG, not a W3C standard | VERIFIED | https://webmachinelearning.github.io/webmcp/ | 2026-11-02 | R3 4.1 | v1 ch9 #1 |
| 2 | Four editors: Walderman, Dallstream (Microsoft), Sagar, Farolino (Google) | VERIFIED | https://webmachinelearning.github.io/webmcp/ | 2026-11-02 | R3 4.2 | v1 ch9 #2 |
| 3 | API: document.modelContext with registerTool/getTools/executeTool, events toolchange/toolactivated/toolcancel | VERIFIED | https://webmachinelearning.github.io/webmcp/#idl-index | 2026-11-02 | webmcp FACTS §1.2, probe §3 | v1 ch9 #3 |
| 4 | outputSchema added by PR #254, merged 2 Nov 2026 13:10 UTC | VERIFIED | https://github.com/webmachinelearning/webmcp/pull/254 | 2026-11-02 | R3 4.3 | v1 ch9 #4 |
| 5 | Declarative API not in spec text, removed by PR #338 (8 Oct 2026), documented by Chrome | VERIFIED | https://github.com/webmachinelearning/webmcp/pull/338 | 2026-11-02 | webmcp FACTS §1.1 | v1 ch9 #5 |
| 6 | Chrome flag chrome://flags/#enable-webmcp-testing, equivalent --enable-features=WebMCPTesting | VERIFIED | https://developer.chrome.com/docs/ai/webmcp | 2026-11-02 | webmcp FACTS §1.7, probe; my tests use the switch | v1 ch9 #6 |
| 7 | Origin trial from Chrome 149, extended to 162 (extension 28 Sep 2026) | VERIFIED | https://chromestatus.com/feature/5117755740913664 | 2026-11-02 | webmcp FACTS §1.7 | v1 ch9 #7 |
| 8 | Edge origin trial expiry 30 Mar 2027 | VERIFIED | https://developer.microsoft.com/microsoft-edge/origin-trials/trials/0b76fe60-b266-458e-a285-04e375c0c31a | 2026-11-02 | webmcp FACTS §1.7 | v1 ch9 #8 |
| 9 | WebKit oppose (#670, closed 11 Jun 2026) | VERIFIED | https://github.com/WebKit/standards-positions/issues/670 | 2026-11-02 | webmcp FACTS §1.9 | v1 ch9 #9 |
| 10 | Mozilla neutral (#1412), refreshed position announced, not published | VERIFIED | https://github.com/mozilla/standards-positions/issues/1412 | 2026-11-02 | webmcp FACTS §1.9 | v1 ch9 #10 |
| 11 | TAG review #1238 open, early comment 26 Oct 2026 (agent-only functionality, JSON Schema, rename to 'Tools') | VERIFIED | https://github.com/w3ctag/design-reviews/issues/1238#issuecomment-6410471845 | 2026-11-02 | webmcp FACTS §2 item 4 | v1 ch9 #11 |
| 12 | Agentic Web WG charter in refinement after TPAC 2026 | VERIFIED | https://github.com/w3c/strategy/issues/576 | 2026-11-02 | webmcp FACTS §1.9 | v1 ch9 #12 |
| 13 | Chrome 156 stable 20 Oct 2026, 157 stable 3 Nov 2026 | VERIFIED | https://chromiumdash.appspot.com/fetch_releases?channel=Stable&platform=Windows | 2026-11-02 | webmcp FACTS §1.7 | v1 ch9 #13 |
| 14 | Tests run on Chrome for Testing 156.0.8078.4 via Playwright 1.64.1 | VERIFIED | local: navigator.userAgent HeadlessChrome/156.0.8078.4; demos package.json | 2026-11-02 | my probe 2 Nov 2026 | v1 ch9 #14 |
| 15 | Radar: WebMCP on 1.42% of 115,468 scanned domains (1,643); e-commerce 928 of 18,927 (~4.9%) | VERIFIED | https://radar.cloudflare.com/ai-insights#adoption-of-ai-agent-standards | 2026-11-02 | FACTS headline 3 and 4, data dated 2026-11-02 | v1 ch9 #15 |
| 16 | Shopify storefronts (allbirds, brooklinen, kith) register WebMCP adapter with search_catalog, add_to_cart, proceed_to_checkout | VERIFIED | https://www.allbirds.com (R1 scan) | 2026-11-02 | FACTS headline 4; 3 stores observed, not all Shopify | v1 ch9 #16 |
| 17 | Shopify comment 'deploys WebMCP across millions of storefronts' on W3C charter thread | VERIFIED | https://github.com/w3c/strategy/issues/576 | 2026-11-02 | single comment, presented as quote | v1 ch9 #17 |
| 18 | compare-mcp quote: WebMCP 'connects agents to your web page — a proposed browser standard...' | VERIFIED | https://developer.chrome.com/docs/ai/webmcp/compare-mcp | 2026-11-02 | webmcp FACTS §2 item 5, page updated 27 Oct 2026 | v1 ch9 #18 |
| 19 | best-practices: share the application service, register tools all at once (roll back), explicit commit points | VERIFIED | https://developer.chrome.com/docs/ai/webmcp/best-practices | 2026-11-02 | webmcp FACTS §2 item 2, updated 30 Oct 2026, byline includes Maxim Salnikov | v1 ch9 #19 |
| 20 | build-tools: enforcement in application logic 'beyond readOnlyHint or untrustedContentHint', pin versions | VERIFIED | https://developer.chrome.com/docs/ai/webmcp/build-tools | 2026-11-02 | webmcp FACTS §2 item 3, updated 30 Oct 2026, byline includes Maxim Salnikov | v1 ch9 #20 |
| 21 | Duplicate tool name with declarative form -> InvalidStateError 'Duplicate tool name' in Chromium 156 | VERIFIED | local probe, Chrome for Testing 156.0.8078.4 | 2026-11-02 | my probe 2 Nov 2026 | v1 ch9 #21 |
| 22 | Declarative schema: select -> anyOf/const/title + enum, number min/max -> minimum/maximum/multipleOf, date -> format date + appended format sentence | VERIFIED | local probe + https://developer.chrome.com/docs/ai/webmcp/declarative-api | 2026-11-02 | schema printed in chapter is real output, shortened | v1 ch9 #22 |
| 23 | toolparamdescription else label (else aria-description) | VERIFIED | https://developer.chrome.com/docs/ai/webmcp/declarative-api | 2026-11-02 | webmcp FACTS §1.5 | v1 ch9 #23 |
| 24 | Chrome 156 ignores toolparamdescription on a checkbox group (features array has no description) | VERIFIED | local probe (getTools inputSchema keys type, items, uniqueItems) | 2026-11-02 | observation, one browser version | v1 ch9 #24 |
| 25 | :tool-form-active and :tool-submit-active pseudo-classes | VERIFIED | https://developer.chrome.com/docs/ai/webmcp/declarative-api | 2026-11-02 | webmcp FACTS §1.5; test asserts :tool-form-active | v1 ch9 #25 |
| 26 | SubmitEvent.agentInvoked and respondWith(promise) after preventDefault() | VERIFIED | https://developer.chrome.com/docs/ai/webmcp/declarative-api | 2026-11-02 | page read 2 Nov 2026 | v1 ch9 #26 |
| 27 | Navigating right after respondWith resolves loses the answer, agent gets the next page instead | VERIFIED | local test, Chromium 156 | 2026-11-02 | observation; my debug runs 2 Nov 2026 | v1 ch9 #27 |
| 28 | A declarative tool that navigates (no respondWith) completes with the next page's JSON-LD array | VERIFIED | local test ch09-webmcp.spec.js; Chrome docs silent (declarative page, updated 25 Sep 2026) | 2026-11-02 | observation, undocumented, labelled as such | v1 ch9 #28 |
| 29 | Chrome docs: toolautosubmit triggers 'submission and a navigation' | VERIFIED | https://developer.chrome.com/docs/ai/webmcp/declarative-api | 2026-11-02 | page read 2 Nov 2026 | v1 ch9 #29 |
| 30 | Thrown error in execute -> executeTool rejects UnknownError, message lost (Chromium 156), spec says specific DOMExceptions (PR #339) | VERIFIED | https://github.com/webmachinelearning/webmcp/pull/339 + probe | 2026-11-02 | webmcp FACTS §3 | v1 ch9 #30 |
| 31 | executeTool resolves a string, objects serialised as JSON, getTools alphabetical | VERIFIED | local probe | 2026-11-02 | webmcp FACTS §3 and my tests | v1 ch9 #31 |
| 32 | Chromium 156 accepts outputSchema at registerTool but getTools does not return it | VERIFIED | local probe + test 'accepts outputSchema but does not report it' | 2026-11-02 | my probe 2 Nov 2026 | v1 ch9 #32 |
| 33 | Four annotations readOnlyHint, consequentialHint, untrustedContentHint, debugging, all default false | VERIFIED | https://webmachinelearning.github.io/webmcp/ | 2026-11-02 | R3 4.6 | v1 ch9 #33 |
| 34 | debugging annotation available from Chrome 156 | VERIFIED | https://developer.chrome.com/docs/ai/webmcp/imperative-api | 2026-11-02 | webmcp FACTS §1.7 | v1 ch9 #34 |
| 35 | No unregisterTool(), unregister by aborting the AbortSignal | VERIFIED | https://webmachinelearning.github.io/webmcp/ | 2026-11-02 | webmcp FACTS §1.2 | v1 ch9 #35 |
| 36 | toolchange fires per registration and unregistration | VERIFIED | local probe | 2026-11-02 | webmcp FACTS §3 | v1 ch9 #37 |
| 37 | Chrome for Testing 149 + flag exposes navigator.modelContext, 156 only document.modelContext | VERIFIED | local probe | 2026-11-02 | webmcp FACTS §3 | v1 ch9 #38 |
| 38 | isitagentready webMcp check accepts document.modelContext.registerTool, legacy navigator.modelContext, or toolname+tooldescription forms | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | R1 §1 check 15 | v1 ch9 #39 |
| 39 | isitagentready level ignores WebMCP | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | R1 §1 levels | v1 ch9 #40 |
| 40 | isitagentready headless check can time out on heavy pages, late registration missed | VERIFIED | R1 §1 pitfalls | 2026-11-02 | research observation | v1 ch9 #41 |
| 41 | Nordlys passes isitagentready webMcp from Chapter 2 | OPINION | reasoning from the check definition | 2026-11-02 | not scanned (local server) | v1 ch9 #42 |
| 42 | Polyfill webmachinelearning/webmcp-polyfill Apache-2.0, created Aug 2026 | VERIFIED | https://github.com/webmachinelearning/webmcp-polyfill | 2026-11-02 | R3 4.16 | v1 ch9 #43 |
| 43 | Frameworks: React use-webmcp-tool/useWebMCP, Vue @vueuse/core useWebMCP, Angular Signal Forms, webmcp-types | VERIFIED | https://developer.chrome.com/docs/ai/webmcp/imperative-api | 2026-11-02 | webmcp FACTS §1.8 | v1 ch9 #46 |
| 44 | DevTools Application panel WebMCP pane | VERIFIED | https://developer.chrome.com/docs/devtools/application/webmcp | 2026-11-02 | webmcp FACTS §1.8 | v1 ch9 #48 |
| 45 | CDP WebMCP domain WebMCP.enable / invokeTool / toolResponded | VERIFIED | local tests (ch09-webmcp.spec.js) | 2026-11-02 | experimental domain | v1 ch9 #50 |
| 46 | Lighthouse 13.6.0 released 27 Oct 2026, agentic-browsing 7 audits | VERIFIED | https://github.com/GoogleChrome/lighthouse/releases/tag/v13.6.0 | 2026-11-02 | R1 §5 | v1 ch9 #51 |
| 47 | webmcp-registered-tools informative, warns > 40 tools | VERIFIED | Lighthouse 13.6.0 source | 2026-11-02 | R1 §5 | v1 ch9 #52 |
| 48 | webmcp-form-coverage informative when failing, passes when all covered | VERIFIED | Lighthouse 13.6.0 source + my runs | 2026-11-02 | R1 §5 | v1 ch9 #53 |
| 49 | webmcp-schema-validity: errors 0, warnings 0.5; issues come from Chrome (CDP) | VERIFIED | Lighthouse 13.6.0 core/audits/webmcp-schema-validity.js | 2026-11-02 | read 2 Nov 2026 | v1 ch9 #54 |
| 50 | WebMCP audits need Chrome 150+ and OT or flag, late registration may be missed | VERIFIED | https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring | 2026-11-02 | R1 §5 facts | v1 ch9 #55 |
| 51 | Nordlys Lighthouse table (before/after) | VERIFIED | my runs 2 Nov 2026, Lighthouse 13.6.0, Chrome for Testing 156, --enable-features=WebMCPTesting | 2026-11-02 | raw JSON kept in /tmp during the run | v1 ch9 #56 |
| 52 | start_booking navigation race (agent got empty output with 50 ms delayed navigation) | VERIFIED | local CDP test, 5 of 5 runs | 2026-11-02 | observation | v1 ch9 #57 |
| 53 | Login form deliberately not a tool | OPINION | author's design decision | 2026-11-02 | see Chapter 11 | v1 ch9 #58 |
| 54 | Recommendation: skip polyfill for public sites | OPINION | author | 2026-11-02 | reasoned in text | v1 ch9 #59 |
| 55 | WebMCP does not affect the isitagentready level | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | R1 §1 pitfalls | v1 ch13 #31 |
| 56 | Recommended orders per site type, the three-release plan for Nordlys, 'what not to build' | OPINION | — | 2026-11-02 | author's judgment | v1 ch13 #41 |
