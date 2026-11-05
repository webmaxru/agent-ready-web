## Chapter 1: The agent-ready web

v2 writer (Part 1), 2026-11-04. Rows carried from the first edition with status, source and retrieval date unchanged. The last column names the v1 row.

| # | Claim / API / listing (short) | Status | Source URL | Retrieved | Note | v1 row |
|---|---|---|---|---|---|---|
| 1 | 13 of 13 booking steps on the clean page, 0 on the legacy page (Chapter 2 experiment) | VERIFIED | demos: chapters/02-your-first-agent-ready-page/booking-walk.mjs, run locally | 2026-11-02 | Chromium 156.0.8078.4, Playwright 1.64.1; tests/ch02-first-page.spec.js | v1 ch1 #1 |
| 2 | Training crawlers GPTBot, ClaudeBot, Amazonbot, CCBot | VERIFIED | https://platform.openai.com/docs/bots ; https://support.anthropic.com/en/articles/8896518 ; https://developer.amazon.com/amazonbot ; https://commoncrawl.org/ccbot | 2026-11-02 | R2 §5 rows 7, 9, 16, 17 | v1 ch1 #2 |
| 3 | Google-Extended is a control token, does not affect Search | VERIFIED | https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers | 2026-11-02 | R2 §5 row 12 | v1 ch1 #3 |
| 4 | Applebot-Extended is a control token for Apple model training | VERIFIED | https://support.apple.com/en-us/119829 | 2026-11-02 | R2 §5 row 15 | v1 ch1 #4 |
| 5 | Crawl purpose: training 41.4%, training and search 41.3%, search 12.3%, user action 3.7%, undeclared 1.3% | VERIFIED | https://radar.cloudflare.com/ai-insights | 2026-11-02 | R1 §3 row 18, 7 days to 2026-11-02 | v1 ch1 #5 |
| 6 | Search crawlers OAI-SearchBot, Claude-SearchBot, PerplexityBot, Googlebot feeds AI Overviews/AI Mode | VERIFIED | https://platform.openai.com/docs/bots ; https://docs.perplexity.ai/guides/bots ; https://developers.google.com/search/docs/appearance/ai-features | 2026-11-02 | R2 §5 | v1 ch1 #6 |
| 7 | Crawl-to-refer: Perplexity 4.9K:1, OpenAI 1.4K:1, Anthropic 540.8:1, Google 4.8:1; Perplexity moved -24.9% in a week | VERIFIED | https://radar.cloudflare.com/ai-insights | 2026-11-02 | R1 §3 row 24 | v1 ch1 #7 |
| 8 | User agents ChatGPT-User, Claude-User, Perplexity-User, Google-Agent; Google-Agent quote | VERIFIED | https://developers.google.com/search/docs/crawling-indexing/google-user-triggered-fetchers | 2026-11-02 | R2 §1 row 22 | v1 ch1 #9 |
| 9 | OpenAI: ChatGPT-User 'robots.txt rules may not apply' | VERIFIED | https://platform.openai.com/docs/bots.md | 2026-11-02 | verbatim | v1 ch1 #10 |
| 10 | Perplexity-User 'generally ignores robots.txt rules' | VERIFIED | https://docs.perplexity.ai/guides/bots | 2026-11-02 | verbatim | v1 ch1 #11 |
| 11 | Google user-triggered fetchers 'generally ignore robots.txt rules' | VERIFIED | https://developers.google.com/search/docs/crawling-indexing/google-user-triggered-fetchers | 2026-11-02 | R4 §4 digest | v1 ch1 #12 |
| 12 | Anthropic: all three bots incl. Claude-User honour robots.txt | VERIFIED | https://support.anthropic.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler | 2026-11-02 | help article dated 7 Apr 2026 | v1 ch1 #13 |
| 13 | Browsing agent products: ChatGPT agent mode, Claude in Chrome, Gemini in Chrome auto browse, Edge Browse with Copilot, Comet, Opera Neon | VERIFIED | https://support.claude.com/en/articles/12012173 ; https://blog.google/products-and-platforms/products/chrome/gemini-3-auto-browse/ ; https://support.microsoft.com/en-us/edge/copilot/browse-with-copilot | 2026-11-02 | R2 §1; Comet and Neon shipping per R2 (product pages) | v1 ch1 #14 |
| 14 | Developer stacks: Playwright MCP, Stagehand, browser-use, computer-use APIs | VERIFIED | https://github.com/microsoft/playwright-mcp ; https://github.com/browserbase/stagehand ; https://platform.openai.com/docs/guides/tools-computer-use | 2026-11-02 | R2 §1 rows 19, 24, 25 | v1 ch1 #15 |
| 15 | web.dev: three ways agents view a site (screenshots, raw HTML, accessibility tree), combined | VERIFIED | https://web.dev/articles/ai-agent-site-ux | 2026-11-02 | R2 §1 row 27 | v1 ch1 #16 |
| 16 | Chrome: accessibility tree is agents' 'primary data model' | VERIFIED | https://developer.chrome.com/blog/agent-ready-toolkit | 2026-11-02 | verbatim | v1 ch1 #17 |
| 17 | HTML requests by client type: non-AI bot 54.4%, human 35.5%, AI bot 6%, mixed 4.1% | VERIFIED | https://radar.cloudflare.com/ai-insights | 2026-11-02 | R1 §3 row 23 | v1 ch1 #19 |
| 18 | Content types to AI bots: HTML 73.2%, text 7%, JSON 5.5%, images 4.7%, Markdown <0.1% | VERIFIED | https://radar.cloudflare.com/ai-insights | 2026-11-02 | R1 §3 row 20 | v1 ch1 #21 |
| 19 | Response status to AI bots: 200 59.6%, 403 16%, 404 7.5%, 301 5.9%, 429 2.6% | VERIFIED | https://radar.cloudflare.com/ai-insights | 2026-11-02 | R1 §3 row 22 | v1 ch1 #22 |
| 20 | Markdown median size 7.9% of HTML | VERIFIED | https://radar.cloudflare.com/ai-insights | 2026-11-02 | R1 §3 row 21 | v1 ch1 #23 |
| 21 | Chrome toolkit post 22 June 2026; two stages searching vs using; 'SEO principles still apply' | VERIFIED | https://developer.chrome.com/blog/agent-ready-toolkit | 2026-11-02 | R1 §4 rows 1-2 | v1 ch1 #24 |
| 22 | Google guide updated 10 Jul 2026: llms.txt/Markdown/special schema not used; 'will neither harm nor help' | VERIFIED | https://developers.google.com/search/docs/fundamentals/ai-optimization-guide | 2026-11-02 | R1 §4 rows 17-20 | v1 ch1 #25 |
| 23 | robots.txt is RFC 9309 (2022) | VERIFIED | https://www.rfc-editor.org/rfc/rfc9309 | 2026-11-02 | R2 §5 | v1 ch1 #26 |
| 24 | isitagentready launched 17 Apr 2026, post title | VERIFIED | https://blog.cloudflare.com/agent-readiness/ | 2026-11-02 | h1 read on page | v1 ch1 #27 |
| 25 | isitagentready: headless browser for WebMCP, statuses pass/fail/neutral/unableToCheck, levels 0-5 | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | read in full | v1 ch1 #28 |
| 26 | 23 checks in 5 categories (list) | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | read in full | v1 ch1 #29 |
| 27 | Level rules L0-L5 (Table 1.2) | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | verbatim | v1 ch1 #30 |
| 28 | Lighthouse agentic category added 13.2.0 (1 May 2026), default config 13.3.0 | VERIFIED | https://github.com/GoogleChrome/lighthouse/releases/tag/v13.2.0 ; /v13.3.0 | 2026-11-02 | R1 §5 rows 12-13 | v1 ch1 #33 |
| 29 | Category needs Chrome 150+ | VERIFIED | https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring | 2026-11-02 |  | v1 ch1 #34 |
| 30 | Seven audits in Lighthouse 13.6.0 (ids and meaning); 33 axe rules; warns above 40 tools | VERIFIED | Lighthouse 13.6.0 source core/config/agentic-browsing-config.js ; core/audits/agentic/* | 2026-11-02 | R1 §5 | v1 ch1 #35 |
| 31 | No 0-100 score, fraction; 'informational and unbenchmarked' | VERIFIED | https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring ; https://developer.chrome.com/blog/agent-ready-toolkit | 2026-11-02 |  | v1 ch1 #36 |
| 32 | WebMCP audits need origin trial or testing flag | VERIFIED | https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring | 2026-11-02 |  | v1 ch1 #37 |
| 33 | 'still under development and subject to change' | VERIFIED | Lighthouse 13.6.0 agentic-browsing-config.js | 2026-11-02 | verbatim | v1 ch1 #38 |
| 34 | 44-site scan: no site at L2/L3/L5, 36 at L0/L1, 8 at L4 (named) | VERIFIED | private/analytics/isitagentready-scans-2026-11-02.md | 2026-11-02 | 5 more refused | v1 ch1 #39 |
| 35 | vercel.com features and still L1 because no Content Signals | VERIFIED | private/analytics/isitagentready-scans-2026-11-02.json | 2026-11-02 | R1 headline 5 | v1 ch1 #40 |
| 36 | Content Signals is an individual IETF draft (draft-romm-aipref-contentsignals), not a WG document | VERIFIED | https://datatracker.ietf.org/doc/draft-romm-aipref-contentsignals/ | 2026-11-02 | R1 §1 pitfalls | v1 ch1 #42 |
| 37 | Agent subset leaves out colour contrast | VERIFIED | Lighthouse agent-accessibility-tree.js TARGET_RULES | 2026-11-02 | R2 §2 row 2 | v1 ch1 #44 |
| 38 | Lighthouse 13.6.0 (27 Oct 2026) moved ARD to /.well-known/ard.json, ai-catalog.json legacy; isitagentready prompt says ai-catalog.json | VERIFIED | https://github.com/GoogleChrome/lighthouse/releases/tag/v13.6.0 ; https://isitagentready.com/llms-full.txt | 2026-11-02 | both read | v1 ch1 #45 |
| 39 | Radar adoption table (Table 1.3), 115,468 domains, 2 Nov 2026 | VERIFIED | https://radar.cloudflare.com/ai-insights#adoption-of-ai-agent-standards | 2026-11-02 | R1 §3 rows 1-13 | v1 ch1 #46 |
| 40 | April 2026: robots.txt 78%, Content Signals 4%, Markdown 3.9%, <15 sites with server cards + API catalogs | VERIFIED | https://blog.cloudflare.com/agent-readiness/ | 2026-11-02 | R1 §2 rows 2-5 | v1 ch1 #47 |
| 41 | Shopify storefronts: WebMCP adapter with 12 tools, /.well-known/ucp, OAuth metadata by default (allbirds, brooklinen, kith) | VERIFIED | scans for this book (private/analytics) | 2026-11-02 | observation on 3 stores, generalised by Radar category data | v1 ch1 #48 |
| 42 | Ilya Grigorik (Shopify): 'Shopify deploys WebMCP across millions of storefronts' | VERIFIED | https://github.com/w3c/strategy/issues/576 | 2026-11-02 | via webmcp-book FACTS.md §1.9; a single comment, presented as a quote | v1 ch1 #50 |
| 43 | Cloudflare benchmark: Kimi-k2.5 via OpenCode, 31% fewer tokens, 66% faster | VERIFIED | https://blog.cloudflare.com/agent-readiness/ | 2026-11-02 | quote checked on page today | v1 ch1 #53 |
| 44 | No public independent study of agent conversion for agent-ready sites | OPINION | research files R1-R4 found none | 2026-11-02 | absence not proven, phrased as 'no public, independent study' known to the author | v1 ch1 #55 |
| 45 | UCP Lodging draft 25 Sep 2026; co-developers Amadeus, Booking.com, Expedia Group, Google, Hilton, Marriott, Trip.com | VERIFIED | https://ucp.dev/ | 2026-11-02 | R3 §6 row 6.12 | v1 ch1 #56 |
| 46 | Nordlys Cabins: six cabins, Fjellro (Rondane, 6 guests, fireplace, ski-in), Reine Rorbu (Lofoten, 2) | VERIFIED | demos nordlys-cabins/data/cabins.json | 2026-11-02 |  | v1 ch1 #58 |
| 47 | Nordlys: Hono on Node 24, in-memory data, two front ends, layer system, --upto flag, /__layers | VERIFIED | demos nordlys-cabins/package.json, LAYERS.md | 2026-11-02 | hono 4.13.16, engines node >=24 | v1 ch1 #59 |
| 48 | Tools, Not Clicks web edition free at https://webmcp.salnikov.no | VERIFIED | SPEC.md | 2026-11-02 |  | v1 ch1 #61 |
| 49 | Lighthouse fails/changes in every minor release since May 2026 | VERIFIED | https://github.com/GoogleChrome/lighthouse/releases | 2026-11-02 | 13.2-13.6 each changed the category | v1 ch1 #62 |
| 50 | isitagentready level rules L1–L5, quoted verbatim | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | R1 §1 'Levels (verbatim rules)' | v1 ch13 #30 |
| 51 | WebMCP does not affect the isitagentready level | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | R1 §1 pitfalls | v1 ch13 #31 |
| 52 | Lighthouse agentic audit ids: agent-accessibility-tree, cumulative-layout-shift, llms-txt, webmcp-registered-tools, webmcp-form-coverage, webmcp-schema-validity, ard-schema (Lighthouse 13.6.0) | VERIFIED | https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring ; https://github.com/GoogleChrome/lighthouse/blob/main/core/config/agentic-browsing-config.js | 2026-11-02 | R1 §5 | v1 ch13 #32 |
| 53 | Nordlys after Chapter 14: Level 4 plus one Level 5 ingredient (auth metadata), by published criteria, not scanned; no A2A card; no own signatures directory | VERIFIED | demos: layers/11-discovery/index.js (no agent-card), layers/15-bot-identity/README.md ('never signs anything itself'); Chapter 14 Table 14.1 | 2026-11-02 | nordlys.example is not publicly scannable | v1 ch13 #35 |
