## Chapter 2: Your first agent-ready page

Writer W1, 2026-11-02. Every claim, number, name, status and date in the chapter, with its source.

| # | Claim / API / listing (short) | Status | Source URL | Retrieved | Note |
|---|---|---|---|---|---|
| 1 | Legacy widget markup (div controls, read-only inputs with placeholders, no form) | VERIFIED | DOM captured with Playwright from nordlys-cabins legacy variant | 2026-11-02 | public/js/legacy.js, src/views/layout.js |
| 2 | Legacy content injected after 400 ms | VERIFIED | nordlys-cabins/src/config.js legacyDelayMs default 400 | 2026-11-02 |  |
| 3 | Versions: Chromium 156.0.8078.4, Playwright 1.64.1, Lighthouse 13.6.0 | VERIFIED | local runs | 2026-11-02 |  |
| 4 | isitagentready API: POST /api/scan, response level/levelName/nextLevel/checks | VERIFIED | https://isitagentready.com/llms-full.txt ; stored scan JSON | 2026-11-02 | camelCase keys as returned |
| 5 | salnikov.no Level 1, next contentSignals; robotsTxt/sitemap/AI rules pass; linkHeaders, markdown, contentSignals fail; messages quoted | VERIFIED | private/analytics/isitagentready-scans-2026-11-02.json | 2026-11-02 | scannedAt 2026-11-02T20:59:58Z |
| 6 | MCP server at https://isitagentready.com/mcp with scan_site | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 |  |
| 7 | Checker agrees on level for six public sites; known differences webMcp (vercel), commerce (allbirds), a2a | VERIFIED | local comparison run vs stored real scans | 2026-11-02 | see demos README |
| 8 | Baseline checker output (Level 0, next robotsTxt, sitemap, linkHeaders) | VERIFIED | agent-ready-check.mjs run on legacy --upto=0 | 2026-11-02 | port changed to 3000 in print |
| 9 | Level 1 needs 2 of 3 basics | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | and computeLevel |
| 10 | Lighthouse agentic category since 13.2.0, needs Chrome 150+, WebMCP audits need OT or flag | VERIFIED | https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring ; release notes | 2026-11-02 |  |
| 11 | Baseline Lighthouse: a11y tree pass, CLS 0.116 fail, form coverage N/A, 1 of 2 | VERIFIED | private/analytics/w1-measurements-2026-11-02/lighthouse/legacy0-fjellro.json (local run) | 2026-11-02 | category score 0.93 |
| 12 | CLS good threshold 0.1 | VERIFIED | https://web.dev/articles/cls | 2026-11-02 | standard Core Web Vitals threshold |
| 13 | 33 axe rules, check quality of exposed elements | VERIFIED | Lighthouse 13.6.0 agent-accessibility-tree.js | 2026-11-02 | R2 §2 |
| 14 | axe label rule accepts placeholder | VERIFIED | https://dequeuniversity.com/rules/axe/4.10/label ; observed: audit passed on legacy page | 2026-11-02 | pass observed in our run |
| 15 | Playwright aria snapshot: legacy textbox 'Check-in' from placeholder; fill fails 'element is not editable' | VERIFIED | local Playwright 1.64.1 run | 2026-11-02 | verbatim |
| 16 | getByLabel does not match placeholder | VERIFIED | observed count 0 in local run ; https://playwright.dev/docs/locators#locate-by-label | 2026-11-02 |  |
| 17 | Walk results 0/13 legacy, 13/13 clean and clean+layer02, legacy+layer02 0/13 at Level 1 | VERIFIED | booking-walk.mjs local runs | 2026-11-02 |  |
| 18 | Chrome: accessibility tree is agents' primary data model | VERIFIED | https://developer.chrome.com/blog/agent-ready-toolkit | 2026-11-02 |  |
| 19 | Anthropic reference quote | VERIFIED | https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool | 2026-11-02 | verbatim |
| 20 | First rule of ARIA use quote | VERIFIED | https://www.w3.org/TR/using-aria/ | 2026-11-02 | read today, section 2.1 |
| 21 | Clean page Lighthouse: 2 of 2, CLS 0, form coverage informative '1 form missing annotations' | VERIFIED | private/analytics/w1-measurements-2026-11-02/lighthouse/clean0-fjellro.json | 2026-11-02 |  |
| 22 | Clean + layer 02: 4 of 4, form coverage and schema validity pass | VERIFIED | private/analytics/w1-measurements-2026-11-02/lighthouse/clean2-fjellro.json | 2026-11-02 |  |
| 23 | robotsTxtAiRules passes on wildcard groups | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 |  |
| 24 | Sitemap protocol requires absolute URLs | VERIFIED | https://www.sitemaps.org/protocol.html | 2026-11-02 | loc must begin with the protocol |
| 25 | WebMCP is a WebML CG draft report | VERIFIED | https://webmachinelearning.github.io/webmcp/ | 2026-11-02 |  |
| 26 | Declarative attributes toolname, tooldescription, toolparamdescription, toolautosubmit; label fallback | VERIFIED | https://developer.chrome.com/docs/ai/webmcp/declarative-api (updated 25 Sep 2026) | 2026-11-02 | read today |
| 27 | Declarative API moved to explainer in Oct 2026, still in Chrome OT | VERIFIED | https://github.com/webmachinelearning/webmcp/blob/main/declarative-api-explainer.md ; Tools, Not Clicks App. C (commit 8 Oct 2026) | 2026-11-02 | explainer read today |
| 28 | Chrome-generated schema JSON | VERIFIED | document.modelContext.getTools() local run, Chromium 156 with WebMCPTesting | 2026-11-02 | verbatim |
| 29 | executeTool(tool, object) works; NOK 7,900 for 9 to 12 Dec, 2 guests | VERIFIED | tests/ch02-first-page.spec.js (passes) | 2026-11-02 |  |
| 30 | Model Context Tool Inspector extension, needs testing flag | VERIFIED | https://github.com/beaufortfrancois/model-context-tool-inspector | 2026-11-02 | FACTS.md |
| 31 | 'WebMCP for testing' flag in chrome://flags | VERIFIED | shared/FACTS.md (testing section) | 2026-11-02 |  |
| 32 | No browser exposes WebMCP by default; OT Chrome 149 to 162 | VERIFIED | https://chromestatus.com/feature/5117755740913664 | 2026-11-02 |  |
| 33 | Layer file 78 lines | VERIFIED | wc -l layers/02-first-steps/index.js | 2026-11-02 |  |
| 34 | Lighthouse changed category every minor release 13.2 to 13.6 | VERIFIED | https://github.com/GoogleChrome/lighthouse/releases | 2026-11-02 |  |
| 35 | Shopify storefronts pass some server-side checks by default | VERIFIED | scans for this book (allbirds, brooklinen, kith) | 2026-11-02 | see Chapter 1 validation |

### Demos

| Demo | Command | Result on 2 Nov 2026 |
|---|---|---|
| Layer 02 unit tests | `node --test tests/ch02-first-steps.test.js` | 7 of 7 pass |
| Layer 02 browser tests | `npx playwright test tests/ch02-first-page.spec.js` | 4 of 4 pass |
| Core suite with layer 02 | `npm test -w nordlys-cabins` | 36 unit + 9 e2e pass |
| Local checker | `node chapters/02-your-first-agent-ready-page/agent-ready-check.mjs <url>` | L0 legacy, L0 clean, L1 clean+02, L1 legacy+02 |
| Booking walk | `node chapters/02-your-first-agent-ready-page/booking-walk.mjs <origin>` | 0/13, 13/13, 13/13, 0/13 |
| Lighthouse 13.6.0 | `--only-categories=agentic-browsing` with WebMCPTesting | 1/2, 2/2, 4/4 |

Listings 2.1 to 2.5 are byte-identical excerpts of the demo files (checked with a script).

### Figures

- figure-2-1: the measure / change one layer / measure again loop with three instruments
- figure-2-2: declarative form attributes mapped to the generated tool schema
