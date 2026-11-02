## Chapter 18: Testing agent-readiness

Retrieved dates are the day the source was read for this chapter (research files R1–R4 and the W6/W6b checks).

| # | Claim / API / listing (short) | Status | Source URL | Retrieved | Note |
|---|---|---|---|---|---|
| 1 | Lighthouse 13.6.0 (npm, published 2026-10-27) ships an 'agentic-browsing' category in its default config with 7 audits, each weight 1, displayed as a fraction: agent-accessibility- | VERIFIED | https://unpkg.com/lighthouse@13.6.0/core/config/default-config.js | 2026-11-02 | R4 §3 #1 |
| 2 | Lighthouse CLI 13.6.0 accepts --only-categories=agentic-browsing (listed among available categories). | VERIFIED | https://unpkg.com/lighthouse@13.6.0/cli/cli-flags.js | 2026-11-02 | R4 §3 #2 |
| 3 | Chrome docs: Agentic Browsing category is experimental, requires Chrome 150+, WebMCP audits require the WebMCP origin trial; no 0–100 weighted score — a fractional pass ratio plus  | VERIFIED | https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring | 2026-11-02 | R4 §3 #4 |
| 4 | Chrome docs: Lighthouse watches WebMCP tool registration through the CDP WebMCP domain; imperative (JS) registration timing can make results fluctuate between runs; audits are dete | VERIFIED | https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring | 2026-11-02 | R4 §3 #5 |
| 5 | Chrome blog 'A developer toolkit to make your website agent-ready' (Kasper Kulikowski, Michael Hablich, Jun 22 2026): Lighthouse Agentic browsing category available from M150; 'inf | VERIFIED | https://developer.chrome.com/blog/agent-ready-toolkit | 2026-11-02 | R4 §3 #6 |
| 6 | Chrome DevTools for Agents (chrome-devtools-mcp) can invoke a lighthouse_audit tool on the active tab and trigger WebMCP tools with flags --autoConnect --categoryExperimentalWebmcp | VERIFIED | https://developer.chrome.com/blog/agent-ready-toolkit | 2026-11-02 | R4 §3 #7 |
| 7 | npm package @playwright/mcp latest version 0.0.84 (published 2026-10-31). | VERIFIED | https://www.npmjs.com/package/@playwright/mcp | 2026-11-02 | R4 §3 #9 |
| 8 | npm package chrome-devtools-mcp latest version 1.12.0 (published 2026-10-22). | VERIFIED | https://www.npmjs.com/package/chrome-devtools-mcp | 2026-11-02 | R4 §3 #10 |
| 9 | npm package @modelcontextprotocol/inspector latest version 2.13.0 (published 2026-10-28). | VERIFIED | https://www.npmjs.com/package/@modelcontextprotocol/inspector | 2026-11-02 | R4 §3 #11 |
| 10 | npm package promptfoo latest version 0.125.1 (published 2026-10-25). | VERIFIED | https://www.npmjs.com/package/promptfoo | 2026-11-02 | R4 §3 #12 |
| 11 | npm package @lhci/cli latest version 0.15.1 (published 2025-06-25). | VERIFIED | https://www.npmjs.com/package/@lhci/cli | 2026-11-02 | R4 §3 #13 |
| 12 | npm package lighthouse latest version 13.6.0 (published 2026-10-27). | VERIFIED | https://www.npmjs.com/package/lighthouse | 2026-11-02 | R4 §3 #14 |
| 13 | npm package playwright latest version 1.64.1 (published 2026-10-14). | VERIFIED | https://www.npmjs.com/package/playwright | 2026-11-02 | R4 §3 #15 |
| 14 | npm package @playwright/test latest version 1.64.1 (published 2026-10-14). | VERIFIED | https://www.npmjs.com/package/@playwright/test | 2026-11-02 | R4 §3 #16 |
| 15 | npm package robots-parser latest version 3.0.1 (published 2023-02-21). | VERIFIED | https://www.npmjs.com/package/robots-parser | 2026-11-02 | R4 §3 #17 |
| 16 | npm package structured-data-testing-tool latest version 4.5.0 (published 2020-03-11). | VERIFIED | https://www.npmjs.com/package/structured-data-testing-tool | 2026-11-02 | R4 §3 #18 |
| 17 | npm package evalite latest version 0.19.0 (published 2025-11-06). | VERIFIED | https://www.npmjs.com/package/evalite | 2026-11-02 | R4 §3 #23 |
| 18 | npm package braintrust latest version 3.42.0 (published 2026-10-29). | VERIFIED | https://www.npmjs.com/package/braintrust | 2026-11-02 | R4 §3 #25 |
| 19 | npm package langsmith latest version 0.11.7 (published 2026-11-02). | VERIFIED | https://www.npmjs.com/package/langsmith | 2026-11-02 | R4 §3 #26 |
| 20 | Pitfall: @lhci/cli 0.15.1 (latest, June 2025) depends on lighthouse 12.6.1, which predates the agentic-browsing category; run lighthouse@13.6.0 directly (or verify LHCI's bundled v | VERIFIED | https://registry.npmjs.org/@lhci/cli/0.15.1 | 2026-11-02 | R4 §3 #33 |
| 21 | Playwright MCP (microsoft/playwright-mcp) drives the browser through 'structured accessibility snapshots, bypassing the need for screenshots'; browser_snapshot tool; optional --cap | VERIFIED | https://github.com/microsoft/playwright-mcp | 2026-11-02 | R4 §3 #34 |
| 22 | promptfoo Browser Provider uses Playwright to run scripted steps (navigate/type/click/extract) as an eval target; supports Chromium, Firefox, WebKit; headless by default. | VERIFIED | https://www.promptfoo.dev/docs/providers/browser/ | 2026-11-02 | R4 §3 #36 |
| 23 | promptfoo has an OWASP Agentic red-team preset (owasp:agentic, per-risk plugins e.g. owasp:agentic:asi01) incl. indirect-prompt-injection plugin. | VERIFIED | https://www.promptfoo.dev/docs/red-team/owasp-agentic-ai/ | 2026-11-02 | R4 §3 #37 |
| 24 | Schema.org Markup Validator (validator.schema.org) validates Schema.org structured data embedded in pages; Google's Rich Results Test checks Google eligibility. No official public  | VERIFIED | https://github.com/schemaorg/schemaorg/discussions/3261 | 2026-11-02 | R4 §3 #39 |
| 25 | Model Context Tool Inspector (Chrome Web Store id gbpdfapgefenggkahomfgkhfehlcenpd, by François Beaufort): inspect, monitor, execute WebMCP tools manually or with Gemini; needs 'We | VERIFIED | https://chromewebstore.google.com/detail/gbpdfapgefenggkahomfgkhfehlcenpd | 2026-11-02 | R4 §3 #40 |
| 26 | @adobe/structured-data-validator 1.7.0 (npm, 2026-02-25): JS library validating structured data against Schema.org and Google Rich Results requirements — usable in CI. | VERIFIED | https://www.npmjs.com/package/@adobe/structured-data-validator | 2026-11-02 | R4 §3 #41 |
| 27 | Pitfall: structured-data-testing-tool (npm) last published 2020-03-11 (v4.5.0) — stale. | VERIFIED | https://www.npmjs.com/package/structured-data-testing-tool | 2026-11-02 | R4 §3 #42 |
| 28 | MCP Inspector (@modelcontextprotocol/inspector 2.13.0, 'Deterministic testing tools for MCP servers'): web UI by default, --cli and --tui modes, plus an mcpdo binary; stores OAuth  | VERIFIED | https://github.com/modelcontextprotocol/inspector | 2026-11-02 | R4 §3 #43 |
| 29 | llms.txt spec is now 'v2' (author Jeremy Howard; published 3 Sep 2024, modified 10 Aug 2026): files at /llms.txt or any subpath (e.g. /docs/llms.txt), most specific applies; H1 is  | VERIFIED | https://llmstxt.org/ | 2026-11-02 | R4 §3 #44 |
| 30 | Chrome WebMCP best practices recommend evaluation-driven development: define the problem as an API contract, a baseline and ideal result, and how output is judged (code checks and  | VERIFIED | https://developer.chrome.com/docs/ai/webmcp/best-practices | 2026-11-02 | R4 §3 #45 |
| 31 | Category added in Lighthouse 13.2.0 (1 May 2026), 13.5.0 added ard-schema, 13.6.0 (27 Oct 2026) moved ARD to v0.91 and fails llms-txt on HTTP 429; 'still under development and subject to change' | VERIFIED | https://github.com/GoogleChrome/lighthouse/releases | 2026-11-02 | R1 §5 |
| 32 | 'does not have a weighted average score from 0 to 100'; fraction display; JSON category score is the mean of applicable audits | VERIFIED | https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring | 2026-11-02 | R1 §5; mean confirmed by our own /cabins run (6.5 of 7 shown as 0.92) |
| 33 | 'informational and unbenchmarked'; available from M150 | VERIFIED | https://developer.chrome.com/blog/agent-ready-toolkit | 2026-11-02 | R1 §4 |
| 34 | DevTools Lighthouse panel in Chrome 150+ shows the category | UNVERIFIED | https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring | 2026-11-02 | Docs say so; only the CLI was run. Text says 'according to Chrome's documentation' |
| 35 | Lighthouse 13.6.0 llms-txt audit checks H1, links and minimum length | VERIFIED | lighthouse@13.6.0 core/audits/agentic/llms-txt.js (installed package) | 2026-11-02 | Read in the installed source |
| 36 | isitagentready.com: JSON API POST /api/scan; MCP server at /mcp with scan_site | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | R1 §1 |
| 37 | RFC 9309: most specific group, longest match, allow on tie | VERIFIED | https://www.rfc-editor.org/rfc/rfc9309 | 2026-11-02 | Implemented and unit-tested in robots-llms.mjs |
| 38 | Playwright toMatchAriaSnapshot compares the accessibility tree with a YAML template | VERIFIED | https://playwright.dev/docs/aria-snapshots | 2026-11-02 | Fetched in pass 3; test passes |
| 39 | WebMCP tools on the home page via document.modelContext.getTools() with --enable-features=WebMCPTesting in Chromium 156.0.8078.4 | VERIFIED | local run | 2026-11-02 | agent-paths.spec.js test 3 passes |
| 40 | MCP Inspector 2.13.0 --cli tools/list and tools/call against Nordlys; tool_is_error line | VERIFIED | local run (npx @modelcontextprotocol/inspector@2.13.0) | 2026-11-02 | Listing 18.10 is the real output |
| 41 | /cabins webmcp-schema-validity 0.5: warning 'Add a description to make this form more accessible for AI agents' on the fireplace checkbox | VERIFIED | local Lighthouse 13.6.0 run | 2026-11-02 | Cause not determined; reported to the Chapter 9 layer owner (lead) |
| 42 | Nordlys: level 4 Agent-Integrated; authMd and personalAgentProtocol fail; Lighthouse 1 / 0.92 / 1 / 1 for /, /cabins, /cabins/fjellro, /book/fjellro | VERIFIED | local runs | 2026-11-02 | Listings 18.5, 18.8 |
| 43 | Regression demo: --upto=6 gives level 3 and 7 regressed checks | VERIFIED | local run | 2026-11-02 | Listing 18.2 |
| 44 | Four pages x three Lighthouse runs took a little over two minutes | VERIFIED | local run | 2026-11-02 | About 136 s measured |
| 45 | Injection eval table (120 episodes) and quoted answers | VERIFIED | demos results/2026-11-02-injection.json | 2026-11-02 | Models as reported by the APIs; default temperature |
| 46 | Episode median 3.4 s, ~4,200 input and ~330 output tokens | VERIFIED | results/2026-11-02-injection.json | 2026-11-02 | Computed from usage fields |
| 47 | Rule of three: zero events in N trials gives a 95% upper bound of about 3/N | VERIFIED | https://en.wikipedia.org/wiki/Rule_of_three_(statistics) | 2026-11-02 | Standard result |
| 48 | OWASP ASI09 Human-Agent Trust Exploitation | VERIFIED | https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/ | 2026-11-02 | Rechecked for Chapter 16 |
| 49 | A test that can block a merge must be deterministic; budgets as a ratchet; role ownership table | OPINION | — | — | Author's practice |
| 50 | Workflow never run on GitHub Actions; every step run locally | VERIFIED | local runs | 2026-11-02 | Stated in text; YAML parses (PyYAML) |

## Demos

- `chapters/18-testing-agent-readiness/` (scripts/, baselines/, e2e/, evals/injection-eval.mjs, test/, workflow/agent-readiness.yml, results/2026-11-02-injection.{json,md})
- Unit tests: `node --test test/*.test.mjs` → 9/9 pass (Node 24.22.1)
- `node scripts/readiness.mjs http://127.0.0.1:4318` → level 4, no regressions. `structured-data.mjs` → 5 pages, no problems. `robots-llms.mjs` → 11/11 ok
- `CHROME_PATH=… node scripts/lighthouse-agentic.mjs http://127.0.0.1:4318` → all 4 pages within budget (Lighthouse 13.6.0, Chromium 156.0.8078.4, median of 3)
- `NORDLYS_URL=http://127.0.0.1:4318 npx playwright test` → 4/4 pass in 1.6 s (Playwright 1.64.1)
- `node evals/injection-eval.mjs --models=gpt-4.1-mini,gpt-5.4-mini,claude-haiku-4-5,claude-haiku-5-5 --runs=10` → table in the chapter (exit code 0)
- Not run: the workflow on GitHub's servers. `npm ci` there needs a lockfile in sync with the workspaces (it was not on 2 Nov 2026) and the MCP SDK declared as a dependency.

## Figures

- figure-18-1 (four layers of agent-readiness tests)
- figure-18-3 (the Nordlys workflow: steps, baselines, failure conditions)
- figure-18-2 (injection eval results, real data)
