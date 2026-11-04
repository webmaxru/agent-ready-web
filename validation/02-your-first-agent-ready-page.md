## Chapter 2: Your first agent-ready page

v2 writer (Part 1), 2026-11-04. Rows carried from the first edition with status, source and retrieval date unchanged. The last column names the v1 row.

| # | Claim / API / listing (short) | Status | Source URL | Retrieved | Note | v1 row |
|---|---|---|---|---|---|---|
| 1 | Legacy widget markup (div controls, read-only inputs with placeholders, no form) | VERIFIED | DOM captured with Playwright from nordlys-cabins legacy variant | 2026-11-02 | public/js/legacy.js, src/views/layout.js | v1 ch2 #1 |
| 2 | Legacy content injected after 400 ms | VERIFIED | nordlys-cabins/src/config.js legacyDelayMs default 400 | 2026-11-02 |  | v1 ch2 #2 |
| 3 | Versions: Chromium 156.0.8078.4, Playwright 1.64.1, Lighthouse 13.6.0 | VERIFIED | local runs | 2026-11-02 |  | v1 ch2 #3 |
| 4 | isitagentready API: POST /api/scan, response level/levelName/nextLevel/checks | VERIFIED | https://isitagentready.com/llms-full.txt ; stored scan JSON | 2026-11-02 | camelCase keys as returned | v1 ch2 #4 |
| 5 | salnikov.no Level 1, next contentSignals; robotsTxt/sitemap/AI rules pass; linkHeaders, markdown, contentSignals fail; messages quoted | VERIFIED | private/analytics/isitagentready-scans-2026-11-02.json | 2026-11-02 | scannedAt 2026-11-02T20:59:58Z | v1 ch2 #5 |
| 6 | MCP server at https://isitagentready.com/mcp with scan_site | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 |  | v1 ch2 #6 |
| 7 | Checker agrees on level for six public sites; known differences webMcp (vercel), commerce (allbirds), a2a | VERIFIED | local comparison run vs stored real scans | 2026-11-02 | see demos README | v1 ch2 #7 |
| 8 | Baseline checker output (Level 0, next robotsTxt, sitemap, linkHeaders) | VERIFIED | agent-ready-check.mjs run on legacy --upto=0 | 2026-11-02 | port changed to 3000 in print | v1 ch2 #8 |
| 9 | Level 1 needs 2 of 3 basics | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | and computeLevel | v1 ch2 #9 |
| 10 | Lighthouse agentic category since 13.2.0, needs Chrome 150+, WebMCP audits need OT or flag | VERIFIED | https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring ; release notes | 2026-11-02 |  | v1 ch2 #10 |
| 11 | Baseline Lighthouse: a11y tree pass, CLS 0.116 fail, form coverage N/A, 1 of 2 | VERIFIED | private/analytics/w1-measurements-2026-11-02/lighthouse/legacy0-fjellro.json (local run) | 2026-11-02 | category score 0.93 | v1 ch2 #11 |
| 12 | CLS good threshold 0.1 | VERIFIED | https://web.dev/articles/cls | 2026-11-02 | standard Core Web Vitals threshold | v1 ch2 #12 |
| 13 | 33 axe rules, check quality of exposed elements | VERIFIED | Lighthouse 13.6.0 agent-accessibility-tree.js | 2026-11-02 | R2 §2 | v1 ch2 #13 |
| 14 | axe label rule accepts placeholder | VERIFIED | https://dequeuniversity.com/rules/axe/4.10/label ; observed: audit passed on legacy page | 2026-11-02 | pass observed in our run | v1 ch2 #14 |
| 15 | Playwright aria snapshot: legacy textbox 'Check-in' from placeholder; fill fails 'element is not editable' | VERIFIED | local Playwright 1.64.1 run | 2026-11-02 | verbatim | v1 ch2 #15 |
| 16 | getByLabel does not match placeholder | VERIFIED | observed count 0 in local run ; https://playwright.dev/docs/locators#locate-by-label | 2026-11-02 |  | v1 ch2 #16 |
| 17 | Walk results 0/13 legacy, 13/13 clean and clean+layer02, legacy+layer02 0/13 at Level 1 | VERIFIED | booking-walk.mjs local runs | 2026-11-02 |  | v1 ch2 #17 |
| 18 | Chrome: accessibility tree is agents' primary data model | VERIFIED | https://developer.chrome.com/blog/agent-ready-toolkit | 2026-11-02 |  | v1 ch2 #18 |
| 19 | Anthropic reference quote | VERIFIED | https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool | 2026-11-02 | verbatim | v1 ch2 #19 |
| 20 | First rule of ARIA use quote | VERIFIED | https://www.w3.org/TR/using-aria/ | 2026-11-02 | read today, section 2.1 | v1 ch2 #20 |
| 21 | Clean page Lighthouse: 2 of 2, CLS 0, form coverage informative '1 form missing annotations' | VERIFIED | private/analytics/w1-measurements-2026-11-02/lighthouse/clean0-fjellro.json | 2026-11-02 |  | v1 ch2 #21 |
| 22 | Clean + layer 02: 4 of 4, form coverage and schema validity pass | VERIFIED | private/analytics/w1-measurements-2026-11-02/lighthouse/clean2-fjellro.json | 2026-11-02 |  | v1 ch2 #22 |
| 23 | robotsTxtAiRules passes on wildcard groups | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 |  | v1 ch2 #23 |
| 24 | Sitemap protocol requires absolute URLs | VERIFIED | https://www.sitemaps.org/protocol.html | 2026-11-02 | loc must begin with the protocol | v1 ch2 #24 |
| 25 | WebMCP is a WebML CG draft report | VERIFIED | https://webmachinelearning.github.io/webmcp/ | 2026-11-02 |  | v1 ch2 #25 |
| 26 | Declarative attributes toolname, tooldescription, toolparamdescription, toolautosubmit; label fallback | VERIFIED | https://developer.chrome.com/docs/ai/webmcp/declarative-api (updated 25 Sep 2026) | 2026-11-02 | read today | v1 ch2 #26 |
| 27 | Declarative API moved to explainer in Oct 2026, still in Chrome OT | VERIFIED | https://github.com/webmachinelearning/webmcp/blob/main/declarative-api-explainer.md ; Tools, Not Clicks App. C (commit 8 Oct 2026) | 2026-11-02 | explainer read today | v1 ch2 #27 |
| 28 | Chrome-generated schema JSON | VERIFIED | document.modelContext.getTools() local run, Chromium 156 with WebMCPTesting | 2026-11-02 | verbatim | v1 ch2 #28 |
| 29 | executeTool(tool, object) works; NOK 7,900 for 9 to 12 Dec, 2 guests | VERIFIED | tests/ch02-first-page.spec.js (passes) | 2026-11-02 |  | v1 ch2 #29 |
| 30 | Model Context Tool Inspector extension, needs testing flag | VERIFIED | https://github.com/beaufortfrancois/model-context-tool-inspector | 2026-11-02 | FACTS.md | v1 ch2 #30 |
| 31 | 'WebMCP for testing' flag in chrome://flags | VERIFIED | shared/FACTS.md (testing section) | 2026-11-02 |  | v1 ch2 #31 |
| 32 | No browser exposes WebMCP by default; OT Chrome 149 to 162 | VERIFIED | https://chromestatus.com/feature/5117755740913664 | 2026-11-02 |  | v1 ch2 #32 |
| 33 | Layer file 78 lines | VERIFIED | wc -l layers/02-first-steps/index.js | 2026-11-02 |  | v1 ch2 #33 |
| 34 | Lighthouse changed category every minor release 13.2 to 13.6 | VERIFIED | https://github.com/GoogleChrome/lighthouse/releases | 2026-11-02 |  | v1 ch2 #34 |
| 35 | Shopify storefronts pass some server-side checks by default | VERIFIED | scans for this book (allbirds, brooklinen, kith) | 2026-11-02 | see Chapter 1 validation | v1 ch2 #35 |
| 36 | Seven labels; training/search/user-fetch distinction | OPINION | shared/research/R4-trust-ops.md §4 |  |  | v1 ch19 #1 |
| 37 | Combined log format has no signature field | VERIFIED | demo test 'the report on the synthetic week adds up' | 2026-11-02 | design fact of the format | v1 ch19 #16 |
| 38 | Listing 19.3 report output | VERIFIED | output of node report.mjs fixtures/synthetic-access.jsonl (Node 22.23.2) | 2026-11-02 | synthetic data, labelled | v1 ch19 #40 |
| 39 | Synthetic week: 2,000 requests, 26 Oct to 1 Nov 2026, invented visitors incl. fake GPTBot from a documentation range and a signed ChatGPT agent; 76 spoofed GPTBot, 55 signed-agent requests | VERIFIED | v1 ch19 "The report" text and Listing 19.3 (make-synthetic-log.mjs, report.mjs) | 2026-11-02 | carried from v1 ch19 prose, which sits under v1 ch19 #40 | v1 ch19 #40 |
