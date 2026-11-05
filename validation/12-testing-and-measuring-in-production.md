## Chapter 12: Testing and measuring in production

v2.0.0 draft, lead task 257dd4d0, 2026-11-04. Rows carried unchanged from the v1 validation tables named in the last column (status, source and retrieval date as validated in v1). Rows for v1 passages cut from this chapter are kept for traceability. 

| # | Claim / API / listing (short) | Status | Source URL | Retrieved | Note | v1 row |
|---|---|---|---|---|---|---|
| 1 | Lighthouse 13.6.0 (npm, published 2026-10-27) ships an 'agentic-browsing' category in its default config with 7 audits, each weight 1, displayed as a fraction: agent-accessibility- | VERIFIED | https://unpkg.com/lighthouse@13.6.0/core/config/default-config.js | 2026-11-02 | R4 §3 #1 | v1 ch18 #1 |
| 2 | Lighthouse CLI 13.6.0 accepts --only-categories=agentic-browsing (listed among available categories). | VERIFIED | https://unpkg.com/lighthouse@13.6.0/cli/cli-flags.js | 2026-11-02 | R4 §3 #2 | v1 ch18 #2 |
| 3 | Chrome docs: Agentic Browsing category is experimental, requires Chrome 150+, WebMCP audits require the WebMCP origin trial; no 0–100 weighted score — a fractional pass ratio plus | VERIFIED | https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring | 2026-11-02 | R4 §3 #4 | v1 ch18 #3 |
| 4 | Chrome docs: Lighthouse watches WebMCP tool registration through the CDP WebMCP domain; imperative (JS) registration timing can make results fluctuate between runs; audits are dete | VERIFIED | https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring | 2026-11-02 | R4 §3 #5 | v1 ch18 #4 |
| 5 | Chrome blog 'A developer toolkit to make your website agent-ready' (Kasper Kulikowski, Michael Hablich, Jun 22 2026): Lighthouse Agentic browsing category available from M150; 'inf | VERIFIED | https://developer.chrome.com/blog/agent-ready-toolkit | 2026-11-02 | R4 §3 #6 | v1 ch18 #5 |
| 6 | Chrome DevTools for Agents (chrome-devtools-mcp) can invoke a lighthouse_audit tool on the active tab and trigger WebMCP tools with flags --autoConnect --categoryExperimentalWebmcp | VERIFIED | https://developer.chrome.com/blog/agent-ready-toolkit | 2026-11-02 | R4 §3 #7 | v1 ch18 #6 |
| 7 | npm package @playwright/mcp latest version 0.0.84 (published 2026-10-31). | VERIFIED | https://www.npmjs.com/package/@playwright/mcp | 2026-11-02 | R4 §3 #9 | v1 ch18 #7 |
| 8 | npm package chrome-devtools-mcp latest version 1.12.0 (published 2026-10-22). | VERIFIED | https://www.npmjs.com/package/chrome-devtools-mcp | 2026-11-02 | R4 §3 #10 | v1 ch18 #8 |
| 9 | npm package @modelcontextprotocol/inspector latest version 2.13.0 (published 2026-10-28). | VERIFIED | https://www.npmjs.com/package/@modelcontextprotocol/inspector | 2026-11-02 | R4 §3 #11 | v1 ch18 #9 |
| 10 | npm package promptfoo latest version 0.125.1 (published 2026-10-25). | VERIFIED | https://www.npmjs.com/package/promptfoo | 2026-11-02 | R4 §3 #12 | v1 ch18 #10 |
| 11 | npm package @lhci/cli latest version 0.15.1 (published 2025-06-25). | VERIFIED | https://www.npmjs.com/package/@lhci/cli | 2026-11-02 | R4 §3 #13 | v1 ch18 #11 |
| 12 | npm package lighthouse latest version 13.6.0 (published 2026-10-27). | VERIFIED | https://www.npmjs.com/package/lighthouse | 2026-11-02 | R4 §3 #14 | v1 ch18 #12 |
| 13 | npm package playwright latest version 1.64.1 (published 2026-10-14). | VERIFIED | https://www.npmjs.com/package/playwright | 2026-11-02 | R4 §3 #15 | v1 ch18 #13 |
| 14 | npm package @playwright/test latest version 1.64.1 (published 2026-10-14). | VERIFIED | https://www.npmjs.com/package/@playwright/test | 2026-11-02 | R4 §3 #16 | v1 ch18 #14 |
| 15 | npm package robots-parser latest version 3.0.1 (published 2023-02-21). | VERIFIED | https://www.npmjs.com/package/robots-parser | 2026-11-02 | R4 §3 #17 | v1 ch18 #15 |
| 16 | npm package structured-data-testing-tool latest version 4.5.0 (published 2020-03-11). | VERIFIED | https://www.npmjs.com/package/structured-data-testing-tool | 2026-11-02 | R4 §3 #18 | v1 ch18 #16 |
| 17 | npm package evalite latest version 0.19.0 (published 2025-11-06). | VERIFIED | https://www.npmjs.com/package/evalite | 2026-11-02 | R4 §3 #23 | v1 ch18 #17 |
| 18 | npm package braintrust latest version 3.42.0 (published 2026-10-29). | VERIFIED | https://www.npmjs.com/package/braintrust | 2026-11-02 | R4 §3 #25 | v1 ch18 #18 |
| 19 | npm package langsmith latest version 0.11.7 (published 2026-11-02). | VERIFIED | https://www.npmjs.com/package/langsmith | 2026-11-02 | R4 §3 #26 | v1 ch18 #19 |
| 20 | Pitfall: @lhci/cli 0.15.1 (latest, June 2025) depends on lighthouse 12.6.1, which predates the agentic-browsing category; run lighthouse@13.6.0 directly (or verify LHCI's bundled v | VERIFIED | https://registry.npmjs.org/@lhci/cli/0.15.1 | 2026-11-02 | R4 §3 #33 | v1 ch18 #20 |
| 21 | Playwright MCP (microsoft/playwright-mcp) drives the browser through 'structured accessibility snapshots, bypassing the need for screenshots'; browser_snapshot tool; optional --cap | VERIFIED | https://github.com/microsoft/playwright-mcp | 2026-11-02 | R4 §3 #34 | v1 ch18 #21 |
| 22 | promptfoo Browser Provider uses Playwright to run scripted steps (navigate/type/click/extract) as an eval target; supports Chromium, Firefox, WebKit; headless by default. | VERIFIED | https://www.promptfoo.dev/docs/providers/browser/ | 2026-11-02 | R4 §3 #36 | v1 ch18 #22 |
| 23 | promptfoo has an OWASP Agentic red-team preset (owasp:agentic, per-risk plugins e.g. owasp:agentic:asi01) incl. indirect-prompt-injection plugin. | VERIFIED | https://www.promptfoo.dev/docs/red-team/owasp-agentic-ai/ | 2026-11-02 | R4 §3 #37 | v1 ch18 #23 |
| 24 | Schema.org Markup Validator (validator.schema.org) validates Schema.org structured data embedded in pages; Google's Rich Results Test checks Google eligibility. No official public | VERIFIED | https://github.com/schemaorg/schemaorg/discussions/3261 | 2026-11-02 | R4 §3 #39 | v1 ch18 #24 |
| 25 | Model Context Tool Inspector (Chrome Web Store id gbpdfapgefenggkahomfgkhfehlcenpd, by François Beaufort): inspect, monitor, execute WebMCP tools manually or with Gemini; needs 'We | VERIFIED | https://chromewebstore.google.com/detail/gbpdfapgefenggkahomfgkhfehlcenpd | 2026-11-02 | R4 §3 #40 | v1 ch18 #25 |
| 26 | @adobe/structured-data-validator 1.7.0 (npm, 2026-02-25): JS library validating structured data against Schema.org and Google Rich Results requirements — usable in CI. | VERIFIED | https://www.npmjs.com/package/@adobe/structured-data-validator | 2026-11-02 | R4 §3 #41 | v1 ch18 #26 |
| 27 | Pitfall: structured-data-testing-tool (npm) last published 2020-03-11 (v4.5.0) — stale. | VERIFIED | https://www.npmjs.com/package/structured-data-testing-tool | 2026-11-02 | R4 §3 #42 | v1 ch18 #27 |
| 28 | MCP Inspector (@modelcontextprotocol/inspector 2.13.0, 'Deterministic testing tools for MCP servers'): web UI by default, --cli and --tui modes, plus an mcpdo binary; stores OAuth | VERIFIED | https://github.com/modelcontextprotocol/inspector | 2026-11-02 | R4 §3 #43 | v1 ch18 #28 |
| 29 | llms.txt spec is now 'v2' (author Jeremy Howard; published 3 Sep 2024, modified 10 Aug 2026): files at /llms.txt or any subpath (e.g. /docs/llms.txt), most specific applies; H1 is | VERIFIED | https://llmstxt.org/ | 2026-11-02 | R4 §3 #44 | v1 ch18 #29 |
| 30 | Chrome WebMCP best practices recommend evaluation-driven development: define the problem as an API contract, a baseline and ideal result, and how output is judged (code checks and | VERIFIED | https://developer.chrome.com/docs/ai/webmcp/best-practices | 2026-11-02 | R4 §3 #45 | v1 ch18 #30 |
| 31 | Category added in Lighthouse 13.2.0 (1 May 2026), 13.5.0 added ard-schema, 13.6.0 (27 Oct 2026) moved ARD to v0.91 and fails llms-txt on HTTP 429; 'still under development and subject to change' | VERIFIED | https://github.com/GoogleChrome/lighthouse/releases | 2026-11-02 | R1 §5 | v1 ch18 #31 |
| 32 | 'does not have a weighted average score from 0 to 100'; fraction display; JSON category score is the mean of applicable audits | VERIFIED | https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring | 2026-11-02 | R1 §5; mean confirmed by our own /cabins run (6.5 of 7 shown as 0.92) | v1 ch18 #32 |
| 33 | 'informational and unbenchmarked'; available from M150 | VERIFIED | https://developer.chrome.com/blog/agent-ready-toolkit | 2026-11-02 | R1 §4 | v1 ch18 #33 |
| 35 | Lighthouse 13.6.0 llms-txt audit checks H1, links and minimum length | VERIFIED | lighthouse@13.6.0 core/audits/agentic/llms-txt.js (installed package) | 2026-11-02 | Read in the installed source | v1 ch18 #35 |
| 36 | isitagentready.com: JSON API POST /api/scan; MCP server at /mcp with scan_site | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | R1 §1 | v1 ch18 #36 |
| 37 | RFC 9309: most specific group, longest match, allow on tie | VERIFIED | https://www.rfc-editor.org/rfc/rfc9309 | 2026-11-02 | Implemented and unit-tested in robots-llms.mjs | v1 ch18 #37 |
| 38 | Playwright toMatchAriaSnapshot compares the accessibility tree with a YAML template | VERIFIED | https://playwright.dev/docs/aria-snapshots | 2026-11-02 | Fetched in pass 3; test passes | v1 ch18 #38 |
| 39 | WebMCP tools on the home page via document.modelContext.getTools() with --enable-features=WebMCPTesting in Chromium 156.0.8078.4 | VERIFIED | local run | 2026-11-02 | agent-paths.spec.js test 3 passes | v1 ch18 #39 |
| 40 | MCP Inspector 2.13.0 --cli tools/list and tools/call against Nordlys; tool_is_error line | VERIFIED | local run (npx @modelcontextprotocol/inspector@2.13.0) | 2026-11-02 | Listing 18.10 is the real output | v1 ch18 #40 |
| 41 | /cabins webmcp-schema-validity 0.5: warning 'Add a description to make this form more accessible for AI agents' on the fireplace checkbox | VERIFIED | local Lighthouse 13.6.0 run | 2026-11-02 | Cause not determined; reported to the Chapter 9 layer owner (lead) | v1 ch18 #41 |
| 42 | Nordlys: level 4 Agent-Integrated; authMd and personalAgentProtocol fail; Lighthouse 1 / 0.92 / 1 / 1 for /, /cabins, /cabins/fjellro, /book/fjellro | VERIFIED | local runs | 2026-11-02 | Listings 18.5, 18.8 | v1 ch18 #42 |
| 43 | Regression demo: --upto=6 gives level 3 and 7 regressed checks | VERIFIED | local run | 2026-11-02 | Listing 18.2 | v1 ch18 #43 |
| 44 | Four pages x three Lighthouse runs took a little over two minutes | VERIFIED | local run | 2026-11-02 | About 136 s measured | v1 ch18 #44 |
| 45 | Injection eval table (120 episodes) and quoted answers | VERIFIED | demos results/2026-11-02-injection.json | 2026-11-02 | Models as reported by the APIs; default temperature | v1 ch18 #45 |
| 46 | Episode median 3.4 s, ~4,200 input and ~330 output tokens | VERIFIED | results/2026-11-02-injection.json | 2026-11-02 | Computed from usage fields | v1 ch18 #46 |
| 47 | Rule of three: zero events in N trials gives a 95% upper bound of about 3/N | VERIFIED | https://en.wikipedia.org/wiki/Rule_of_three_(statistics) | 2026-11-02 | Standard result | v1 ch18 #47 |
| 48 | OWASP ASI09 Human-Agent Trust Exploitation | VERIFIED | https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/ | 2026-11-02 | Rechecked for Chapter 16 | v1 ch18 #48 |
| 49 | A test that can block a merge must be deterministic; budgets as a ratchet; role ownership table | OPINION | — | — | Author's practice | v1 ch18 #49 |
| 50 | Workflow never run on GitHub Actions; every step run locally | VERIFIED | local runs | 2026-11-02 | Stated in text; YAML parses (PyYAML) | v1 ch18 #50 |
| 51 | Seven labels; training/search/user-fetch distinction | OPINION | shared/research/R4-trust-ops.md §4 |  |  | v1 ch19 #1 |
| 52 | OpenAI: ChatGPT-User 'robots.txt rules may not apply' | VERIFIED | https://platform.openai.com/docs/bots | 2026-11-02 | verbatim | v1 ch19 #2 |
| 53 | Google user-triggered fetchers 'generally ignore robots.txt rules' | VERIFIED | https://developers.google.com/crawling/docs/crawlers-fetchers/google-user-triggered-fetchers | 2026-11-02 | verbatim | v1 ch19 #3 |
| 54 | OpenAI tokens GPTBot, OAI-SearchBot, ChatGPT-User, OAI-AdsBot and IP JSON URLs | VERIFIED | https://platform.openai.com/docs/bots | 2026-11-02 | R4 §4 fact 1 | v1 ch19 #4 |
| 55 | Anthropic ClaudeBot, Claude-SearchBot, Claude-User; bots.json | VERIFIED | https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler | 2026-11-02 | R4 fact 4 | v1 ch19 #5 |
| 56 | Perplexity PerplexityBot + Perplexity-User, both IP JSON URLs | VERIFIED | https://docs.perplexity.ai/docs/resources/perplexity-crawlers | 2026-11-02 | read this session: perplexity-user.json listed | v1 ch19 #6 |
| 57 | Google-Agent UA token and user-triggered-agents.json | VERIFIED | https://developers.google.com/crawling/docs/crawlers-fetchers/google-user-triggered-fetchers | 2026-11-02 | UA string read this session | v1 ch19 #7 |
| 58 | Googlebot common-crawlers.json + reverse DNS names crawl-***.googlebot.com, geo-crawl-***.geo.googlebot.com, google.com / gae.googleusercontent.com | VERIFIED | https://developers.google.com/crawling/docs/crawlers-fetchers/verify-google-requests | 2026-11-02 | R4 fact 8 | v1 ch19 #8 |
| 59 | bingbot range file at bing.com/toolbox/bingbot.json | VERIFIED (file) | https://www.bing.com/toolbox/bingbot.json | 2026-11-02 | the range file was read; the text cites only the file, not a Bing help page | v1 ch19 #9 |
| 60 | GPTBot/1.4, OAI-SearchBot/1.4, 'version may change'; robots.txt marker in UA | VERIFIED | https://platform.openai.com/docs/bots | 2026-11-02 | R4 fact 3 | v1 ch19 #10 |
| 61 | Nine range files: creationTime 2 Nov 2026 (Google) back to Jan 2026 (OAI-SearchBot), Bing Jan 2024; ChatGPT-User 235 prefixes, Anthropic 14 | VERIFIED | demos chapters/19-measuring-agent-traffic/ip-ranges/2026-11-02/SOURCES.md | 2026-11-02 | fetched by me | v1 ch19 #11 |
| 62 | Anthropic: IP blocking 'may not work correctly or persistently guarantee an opt-out' | VERIFIED | https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler | 2026-11-02 | R4 fact 4 | v1 ch19 #12 |
| 63 | Web Bot Auth = RFC 9421 signatures + Signature-Agent | VERIFIED | https://www.ietf.org/archive/id/draft-ietf-webbotauth-httpsig-protocol-01.txt | 2026-11-02 | R3 5.1 | v1 ch19 #13 |
| 64 | OpenAI key directory at chatgpt.com/.well-known/http-message-signatures-directory | VERIFIED | https://chatgpt.com/.well-known/http-message-signatures-directory | 2026-11-02 | fetched 200 this session | v1 ch19 #14 |
| 65 | Google experiments with agent.bot.goog; 'We don't sign every request' | VERIFIED | https://developers.google.com/crawling/docs/crawlers-fetchers/web-bot-auth | 2026-11-02 | R3 5.9/5.10 | v1 ch19 #15 |
| 66 | Combined log format has no signature field | VERIFIED | demo test 'the report on the synthetic week adds up' | 2026-11-02 | design fact of the format | v1 ch19 #16 |
| 67 | Claude in Chrome, Gemini in Chrome, Copilot in Edge run in the person's browser; requests carry the person's UA/cookies/IP | OPINION (inference from product docs) | ch01 footnote 8 sources | 2026-11-02 | phrased 'as far as their documentation shows' | v1 ch19 #17 |
| 68 | Referrer-Policy strict-origin-when-cross-origin sent by Nordlys | VERIFIED | demos nordlys-cabins/LAYERS.md (base headers) | 2026-11-02 |  | v1 ch19 #18 |
| 70 | GA4 AI Assistant channel; AI Overviews/AI Mode count as Organic Search | VERIFIED | https://support.google.com/analytics/answer/9756891 | 2026-11-02 | R4 fact 11 | v1 ch19 #20 |
| 71 | Crawl-to-refer definition (Jul 2025) | VERIFIED | https://blog.cloudflare.com/ai-search-crawl-refer-ratio-on-radar | 2026-11-02 | R4 fact 9; title read this session | v1 ch19 #21 |
| 72 | Jul 2025 ratios: Anthropic 38,065.7:1 (286,930.1 Jan), OpenAI 1,091.4:1, Perplexity 194.8:1, Microsoft 40.7:1 | VERIFIED | https://blog.cloudflare.com/crawlers-click-ai-bots-training | 2026-11-02 | R4 fact 10 | v1 ch19 #22 |
| 73 | Radar week to 2 Nov 2026: Perplexity 4.9K:1 (-24.9%), OpenAI 1.4K:1 (-24%), Anthropic 540.8:1 (+8.4%), Google 4.8:1 | VERIFIED | https://radar.cloudflare.com/ai-insights | 2026-11-02 | R1 §3 fact 24 (rendered page read by R1) | v1 ch19 #23 |
| 74 | Radar client types: non-AI bot 54.4%, human 35.5%, AI bot 6%, mixed 4.1% | VERIFIED | https://radar.cloudflare.com/ai-insights | 2026-11-02 | R1 fact 23 | v1 ch19 #24 |
| 75 | Radar crawl purpose: training 41.4, training&search 41.3, search 12.3, user action 3.7, undeclared 1.3 | VERIFIED | https://radar.cloudflare.com/ai-insights | 2026-11-02 | R1 fact 18 | v1 ch19 #25 |
| 76 | Radar status to AI bots: 200 59.6, 403 16, 404 7.5, 301 5.9, 429 2.6 | VERIFIED | https://radar.cloudflare.com/ai-insights | 2026-11-02 | R1 fact 22 | v1 ch19 #26 |
| 77 | Radar content types HTML 73.2%, Markdown <0.1% | VERIFIED | https://radar.cloudflare.com/ai-insights | 2026-11-02 | R1 fact 20 | v1 ch19 #27 |
| 78 | Radar API needs token; adoption data weekly on Mondays | VERIFIED | https://developers.cloudflare.com/changelog/post/2026-04-17-radar-ai-insights-updates/ | 2026-11-02 | R1 facts 27-28 | v1 ch19 #28 |
| 79 | Cloudflare AI Crawl Control metrics; referrals paid plans only | VERIFIED | https://developers.cloudflare.com/ai-crawl-control/features/analyze-ai-traffic/ | 2026-11-02 | R4 fact 12 | v1 ch19 #29 |
| 80 | Cloudflare: signed agents folded into Verified bots 1 Jul 2026, Direct vs Intermediary | VERIFIED | https://developers.cloudflare.com/bots/concepts/bot/verified-bots/ | 2026-11-02 | R3 5.11 | v1 ch19 #30 |
| 81 | Vercel AI bots ruleset (training/search/user-initiated), verified bots directory, chatgpt-user/chatgpt-operator ai_assistant, rDNS + Web Bot Auth | VERIFIED | https://vercel.com/docs/bot-management | 2026-11-02 | R4 fact 13 | v1 ch19 #31 |
| 82 | AWS WAF Web Bot Auth 21 Nov 2025, verified WBA bots allowed by default; CloudFront + regional | VERIFIED | https://aws.amazon.com/about-aws/whats-new/2025/11/aws-waf-web-bot-auth-support/ | 2026-11-02 | R3 5.15/5.16 | v1 ch19 #32 |
| 83 | OpenAI robots changes ~24 h for search; Perplexity up to 24 h | VERIFIED | https://platform.openai.com/docs/bots ; https://docs.perplexity.ai/docs/resources/perplexity-crawlers | 2026-11-02 | R4 facts 2, 5 | v1 ch19 #33 |
| 84 | MCP 2026-07-28 requires Mcp-Method and Mcp-Name on Streamable HTTP POST (SEP-2243) | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/changelog | 2026-11-02 | read this session | v1 ch19 #34 |
| 85 | nginx log_format escape=json, $http_<name>, $sent_http_content_type | VERIFIED | https://nginx.org/en/docs/http/ngx_http_log_module.html | 2026-11-02 | standard nginx variables; config not run on this box | v1 ch19 #35 |
| 86 | GDPR: IP addresses in logs are personal data (pointer to Ch17) | OPINION / see Ch17 | Chapter 17 validation | 2026-11-02 | not legal advice | v1 ch19 #36 |
| 87 | KPI table | OPINION | R4 §4 'Proposed KPIs' | 2026-11-02 | labelled as proposals | v1 ch19 #37 |
| 88 | Listing 19.1 agents.json lines 1-20 | VERIFIED | demos chapters/19-measuring-agent-traffic/agents.json | 2026-11-02 | byte-identical excerpt | v1 ch19 #38 |
| 89 | Listing 19.2 classify.mjs lines 21-55 | VERIFIED | demos chapters/19-measuring-agent-traffic/lib/classify.mjs | 2026-11-02 | byte-identical excerpt | v1 ch19 #39 |
| 90 | Listing 19.3 report output | VERIFIED | output of node report.mjs fixtures/synthetic-access.jsonl (Node 22.23.2) | 2026-11-02 | synthetic data, labelled | v1 ch19 #40 |
| 91 | Listing 19.4 layer index.js lines 36-63 | VERIFIED | demos nordlys-cabins/layers/19-agent-analytics/index.js | 2026-11-02 | byte-identical excerpt | v1 ch19 #41 |
| 92 | jq output of training topPaths | VERIFIED | run on the synthetic log | 2026-11-02 | real output | v1 ch19 #42 |
| 93 | MCP 2026-07-28 removed session handshake (stateless core) | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/changelog | 2026-11-02 | FACTS §MCP; SEP-2575 | v1 ch20 #1 |
| 94 | Cloudflare folded signed agents into Verified bots 1 Jul 2026 | VERIFIED | https://developers.cloudflare.com/bots/concepts/bot/verified-bots/ | 2026-11-02 | R3 5.11 | v1 ch20 #2 |
| 95 | WebMCP outputSchema merged 2 Nov 2026 (PR #254), report dated 2 Nov 2026 | VERIFIED | https://github.com/webmachinelearning/webmcp/pull/254 | 2026-11-02 | R3 §4 | v1 ch20 #3 |
| 96 | Lighthouse category 'still under development and subject to change'; added v13.2.0 May 2026 | VERIFIED | https://github.com/GoogleChrome/lighthouse (agentic-browsing-config.js, releases) | 2026-11-02 | R1 §5 | v1 ch20 #4 |
| 97 | Tools, Not Clicks v1.0.0 tag 15 Oct 2026; v2.0.0 release 2 Nov 2026 | VERIFIED | https://github.com/webmaxru/webmcp-book | 2026-11-02 | GitHub API: tag commit date, release published_at | v1 ch20 #5 |
| 98 | WebMCP status: 'It is not a W3C Standard nor is it on the W3C Standards Track.' | VERIFIED | https://webmachinelearning.github.io/webmcp/ | 2026-11-02 | verbatim | v1 ch20 #6 |
| 99 | Internet-Drafts valid max six months; webbotauth -01 expires 2 May 2027; 'work in progress' | VERIFIED | https://www.ietf.org/archive/id/draft-ietf-webbotauth-httpsig-protocol-01.txt | 2026-11-02 | verbatim boilerplate | v1 ch20 #7 |
| 100 | Browser stages flag / origin trial / shipped | VERIFIED | https://chromestatus.com/feature/5117755740913664 | 2026-11-02 | general Chrome process | v1 ch20 #8 |
| 101 | WebKit position oppose, Mozilla neutral on WebMCP | VERIFIED | https://github.com/WebKit/standards-positions/issues/670 ; https://github.com/mozilla/standards-positions/issues/1412 | 2026-11-02 | labels read via GitHub API | v1 ch20 #9 |
| 102 | W3C Rec track WD→CR→PR→REC; CG → WG with charter | VERIFIED | https://www.w3.org/policies/process/ | 2026-11-02 |  | v1 ch20 #10 |
| 103 | Strategy #560 WebML WG charter proposes WebMCP as 'tentative deliverable', open since 9 Jun 2026 | VERIFIED | https://github.com/w3c/strategy/issues/560 | 2026-11-02 | verbatim | v1 ch20 #11 |
| 104 | Strategy #576 Agentic Web WG charter, new WG, open since 28 Sep 2026 | VERIFIED | https://github.com/w3c/strategy/issues/576 | 2026-11-02 | GitHub API | v1 ch20 #12 |
| 105 | Origin trial Chrome 149–162, announced 9 Jun 2026 | VERIFIED | https://developer.chrome.com/blog/ai-webmcp-origin-trial | 2026-11-02 | R3 4.11 | v1 ch20 #13 |
| 106 | webbotauth -01 29 Oct 2026; milestones Apr/Aug 2026 passed | VERIFIED | https://datatracker.ietf.org/wg/webbotauth/about/ | 2026-11-02 | R3 §5 | v1 ch20 #14 |
| 107 | aipref vocab -08 / attach -05, Proposed Standard intent | VERIFIED | https://datatracker.ietf.org/doc/draft-ietf-aipref-vocab/ | 2026-11-02 | datatracker JSON via watch script | v1 ch20 #15 |
| 108 | Content Signals = individual draft draft-romm-aipref-contentsignals | VERIFIED | https://datatracker.ietf.org/doc/draft-romm-aipref-contentsignals/ | 2026-11-02 | R1 | v1 ch20 #16 |
| 109 | RateLimit headers draft-11 May 2026, expires 24 Nov 2026 | VERIFIED | https://www.ietf.org/archive/id/draft-ietf-httpapi-ratelimit-headers-11.txt | 2026-11-02 | R3 3.13 | v1 ch20 #17 |
| 110 | RFC 9421, 9728, 9727, 9745 (Mar 2025), 8594 (2019), 5829 successor-version | VERIFIED | https://www.rfc-editor.org/ | 2026-11-02 |  | v1 ch20 #18 |
| 111 | MCP versions dated; Draft/Current/Final; current 2026-07-28; previous 2025-11-25, 2025-06-18, 2025-03-26; _meta protocolVersion | VERIFIED | https://modelcontextprotocol.io/specification/versioning | 2026-11-02 | FACTS / R3 §1 | v1 ch20 #19 |
| 112 | SEP-2243 headers, SEP-2575 stateless, SEP-2577 deprecations | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/changelog | 2026-11-02 | R3 §1 table | v1 ch20 #20 |
| 113 | MCP deprecation policy ≥12 months; HTTP+SSE, Roots, Sampling, Logging deprecated; DCR → CIMD | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/changelog | 2026-11-02 | FACTS | v1 ch20 #21 |
| 114 | AAIF 9 Dec 2025 (Anthropic, Block, OpenAI); A2A joined Aug 2026 | VERIFIED | https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation ; https://a2a-protocol.org/latest/blog/2026/08/27/a-new-chapter-for-a2a-joining-the-agentic-ai-foundation/ | 2026-11-02 | R3 6.5 (A2A blog from snippet) | v1 ch20 #22 |
| 115 | schema.org 29.4 (8 Dec 2025), 30.0 (19 Mar 2026), 30.1 (16 Sep 2026, EU DPP + eCommerce) | VERIFIED | https://schema.org/docs/releases.html | 2026-11-02 | read this session | v1 ch20 #23 |
| 116 | schema.org/version/latest and per-release URLs | VERIFIED | https://schema.org/version/30.1/ | 2026-11-02 |  | v1 ch20 #24 |
| 117 | llms.txt by Jeremy Howard, 3 Sep 2024; v2 modified 10 Aug 2026 | VERIFIED | https://llmstxt.org/ | 2026-11-02 | R2 | v1 ch20 #25 |
| 118 | isitagentready levels cumulative; WebMCP doesn't affect level; L3 needs Markdown negotiation | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | R1 §1 | v1 ch20 #26 |
| 119 | isitagentready detects legacy navigator.modelContext | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | R1 §1 check table | v1 ch20 #27 |
| 120 | x402 Foundation under LF 2 Apr 2026 | VERIFIED | https://docs.cdp.coinbase.com/x402/support/x402-foundation | 2026-11-02 | R3 5.26 | v1 ch20 #28 |
| 121 | AP2 donated to FIDO Alliance (v0.2) | VERIFIED | https://ap2-protocol.org/ | 2026-11-05 | home page re-read 2026-11-05: lists "AP2 v0.2 Release and FIDO Alliance Donation" and "Agent Payments Protocol Announcement (9/16/2025)"; the text gives no donation date | v1 ch20 #29 |
| 122 | 'MCP's biggest breaking change came seven months after it joined a foundation' (Dec 2025 → Jul 2026) | OPINION (date arithmetic) |  | 2026-11-02 |  | v1 ch20 #30 |
| 123 | OpenAI ~24 h, Perplexity up to 24 h for robots.txt changes | VERIFIED | https://platform.openai.com/docs/bots ; https://docs.perplexity.ai/docs/resources/perplexity-crawlers | 2026-11-02 | R4 | v1 ch20 #31 |
| 124 | Book web edition: what it publishes, Lighthouse 13.6.0 1.00 on six page types, search page 0.95 / CLS 0.164 fixed | VERIFIED | book/AGENT-READY.md (local run 2 Nov 2026, Chrome for Testing 156.0.8078.4) | 2026-11-02 | measured by the site build worker | v1 ch20 #32 |
| 125 | Book web edition expected isitagentready Level 2 | OPINION (derived) | book/AGENT-READY.md + level rules | 2026-11-02 | labelled 'I expect'; live scan after first deploy | v1 ch20 #33 |
| 126 | webmcp.salnikov.no Level 1 on 2 Nov 2026 | VERIFIED | https://isitagentready.com/api/scan | 2026-11-02 | AGENT-READY.md | v1 ch20 #34 |
| 127 | Azure Static Web Apps static routes can't vary by Accept | VERIFIED (as documented in AGENT-READY.md) | book/AGENT-READY.md | 2026-11-02 |  | v1 ch20 #35 |
| 128 | Change-safety table, four-step migration, roadmap, 'Where this is heading' | OPINION | R4 §5 | 2026-11-02 | labelled as opinion | v1 ch20 #36 |
| 129 | Listing 20.1 layer index.js lines 37-67 | VERIFIED | demos nordlys-cabins/layers/20-versioning/index.js | 2026-11-02 | byte-identical | v1 ch20 #37 |
| 130 | Listing 20.2 deprecation.mjs 13-21; Listing 20.3 deprecation.mjs 47-61 | VERIFIED | demos chapters/20-evolving-with-the-standards/lib/deprecation.mjs | 2026-11-02 | byte-identical | v1 ch20 #38 |
| 131 | Listing 20.4 standards-watch.mjs 18-30 | VERIFIED | demos chapters/20-evolving-with-the-standards/standards-watch.mjs | 2026-11-02 | byte-identical | v1 ch20 #39 |
| 132 | HTTP header output, checkDeprecation output (174 days), watch output | VERIFIED | real output, Node 22.23.2, 2 Nov 2026 | 2026-11-02 | colour codes stripped | v1 ch20 #40 |

### Figures

- Figure 12.1 (v1 Figure 18.1)
- Figure 12.2 (v1 Figure 18.2)
- Figure 12.3 (v1 Figure 18.3)
- Figure 12.4 (v1 Figure 19.1)
- Figure 12.5 (v1 Figure 19.3)
- Figure 12.6 (v1 Figure 20.3)

### Listings

- Listing 12.1 (v1 Listing 18.1)
- Listing 12.2 (v1 Listing 18.2)
- Listing 12.3 (v1 Listing 18.7)
- Listing 12.4 (v1 Listing 19.2)
- Listing 12.5 (v1 Listing 19.3)
