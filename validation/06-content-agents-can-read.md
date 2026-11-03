## Chapter 6: Content agents can read

| # | Claim / API / listing (short) | Status (VERIFIED / UNVERIFIED / OPINION) | Source URL | Retrieved | Note |
|---|---|---|---|---|---|
| 1 | Radar: content types to AI bots HTML 73.2%, plain text 7%, JSON 5.5%, images 4.7%, Markdown <0.1%; Markdown for Agents median 7.9% of original | VERIFIED | https://radar.cloudflare.com/ai-insights | 2026-11-02 | R1 §3 #20-21 |
| 2 | Cloudflare Markdown for Agents blog 12 Feb 2026: 16,180 vs 3,150 tokens | VERIFIED | https://blog.cloudflare.com/markdown-for-agents/ | 2026-11-02 | R2 §4 #18 |
| 3 | blog.cloudflare.com with Accept md: text/markdown, Vary accept, Content-Signal all yes, Link incl RSS alternate, sitemap, api-catalog | VERIFIED | https://blog.cloudflare.com/markdown-for-agents/ | 2026-11-02 | R2 §4 #21 (headers captured 2 Nov) |
| 4 | Checkly Feb 2026: 3 of 7 agents request markdown (Claude Code 2.1.38, Cursor 2.4.28, OpenCode 1.2.5); Codex, Gemini CLI 0.28.2, Copilot, Windsurf not; 180,573 vs 478 tokens, 615.4 KB vs 2.3 KB | VERIFIED | https://www.checklyhq.com/blog/state-of-ai-agent-content-negotation/ | 2026-11-02 | R2 §4 #23; URL 200 on 2 Nov |
| 5 | RFC 9110 proactive content negotiation, q values, Vary | VERIFIED | https://www.rfc-editor.org/rfc/rfc9110.html | 2026-11-02 | standard |
| 6 | llms.txt v1 3 Sep 2024, v2 modified 10 Aug 2026; H1 'only required section'; blockquote, H2 file lists; subpaths; page.md and page.html.md; dropped llms_txt2ctx and Optional meaning; rel alternate/describedby discovery; AI labs publish for docs | VERIFIED | https://llmstxt.org/ | 2026-11-02 | R2 §4 #6-9 |
| 7 | llms-full.txt is a community convention outside the proposal | VERIFIED | https://llmstxt.org/changes.html | 2026-11-02 | R2 §4 #8 |
| 8 | Cloudflare MfA: Pro/Business, strips nav/header/footer, YAML front matter, JSON-LD fenced block, Vary: Accept, default Content-Signal all yes unless origin sets, drops ETag/Last-Modified | VERIFIED | https://developers.cloudflare.com/fundamentals/reference/markdown-for-agents/ | 2026-11-02 | R2 §4 #18-20 |
| 9 | Vercel Next.js recipe 3 Feb 2026 header rewrite | VERIFIED | https://vercel.com/blog/making-agent-friendly-pages-with-content-negotiation | 2026-11-02 | R2 §4 #22 |
| 10 | Radar adoption: Markdown negotiation 4,924 (4.3%), Link headers 11,252 (9.7%) of 115,468 | VERIFIED | https://radar.cloudflare.com/ai-insights#adoption-of-ai-agent-standards | 2026-11-02 | R1 §3 #5, #9 |
| 11 | 'platforms are behind much of this' (markdown negotiation adoption) | OPINION | https://radar.cloudflare.com/ai-insights#adoption-of-ai-agent-standards | 2026-11-02 | stated as my reading |
| 12 | isitagentready markdownNegotiation pass criteria and fix text 'while HTML remains the default for browsers'; linkHeaders criteria; L3 = L2 + markdown negotiation | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | read 2 Nov |
| 13 | gpt-tokenizer 4.1.0 o200k_base; Nordlys token counts / 1578→743, /cabins/fjellro 2543→486, guide 1312→427, /faq 1866→409 | VERIFIED | https://www.npmjs.com/package/gpt-tokenizer | 2026-11-02 | measured 2 Nov with layers/06-agent-content/token-compare.js |
| 14 | Google AI optimization guide quote 'You don't need to create new machine readable files... Google Search itself doesn't use them'; neither harm nor help | VERIFIED | https://developers.google.com/search/docs/fundamentals/ai-optimization-guide | 2026-11-02 | R2 §4 #5, R1 #18 |
| 15 | Mueller 'FWIW no AI system currently uses llms.txt' (Jun 2025); Illyes July 2025 Google doesn't support | VERIFIED | https://www.seroundtable.com/google-ai-llms-txt-39607.html | 2026-11-02 | as reported; R2 §4 #10-11 |
| 16 | SEJ 20 May 2026: guidance depends on product; Lighthouse 13.3 added Agentic Browsing with llms.txt audit | VERIFIED | https://www.searchenginejournal.com/googles-llms-txt-guidance-depends-on-which-product-you-ask/575431/ | 2026-11-02 | R2 §4 #12 |
| 17 | Ahrefs 15 Jun 2026: 137K sites, 28% publish, 97% zero requests, 19.5% from AI bots | VERIFIED | https://ahrefs.com/blog/llmstxt-study/ | 2026-11-02 | R2 §4 #14 |
| 18 | Rankability 18 Sep 2026: 9.3% top 1k, 8.3% top 10k; SE Ranking 10.13% of ~300K, no correlation | VERIFIED | https://www.rankability.com/blog/llms-txt-adoption/ | 2026-11-02 | R2 §4 #13, #15 |
| 19 | Google Search Central llms.txt added Dec 2025, 404 on 2 Nov 2026; platform.openai.com/llms.txt 404; developers.openai.com/llms.txt 200 | VERIFIED | https://www.seroundtable.com/google-adds-llms-txt-to-search-developer-docs-40533.html | 2026-11-02 | status re-checked 2 Nov |
| 20 | Lighthouse 13.6.0 llms-txt: root only, 4xx N/A, 5xx/429 fail, H1 + link + >=50 chars; regexes quoted | VERIFIED | https://github.com/GoogleChrome/lighthouse/blob/main/core/audits/agentic/llms-txt.js | 2026-11-02 | read in lighthouse@13.6.0 package 2 Nov |
| 21 | Chrome docs: N/A 'as providing the file is optional at the moment' | VERIFIED | https://developer.chrome.com/docs/lighthouse/agentic-browsing/llms-txt | 2026-11-02 | R2 §4 #2 |
| 22 | Real Lighthouse 13.6.0 run on Nordlys home: upto 5 llms-txt N/A, upto 6 pass (weight 1); category score 1 both | VERIFIED | https://github.com/GoogleChrome/lighthouse | 2026-11-02 | run locally 2 Nov (headless Chrome, no WebMCP flag) |
| 23 | Google sitemap limits 50MB/50,000; lastmod 'consistently and verifiably' accurate; ignores priority/changefreq | VERIFIED | https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap | 2026-11-02 | R2 §4 #24 |
| 24 | Atom RFC 4287 Standards Track Dec 2005; RSS 2.0; JSON Feed 1.1; Feedfetcher RSS/Atom for News and WebSub; NLWeb ingests RSS | VERIFIED | https://www.rfc-editor.org/rfc/rfc4287.html | 2026-11-02 | R2 §4 #30; feedfetcher page 200 |
| 25 | RFC 8288 Web Linking | VERIFIED | https://www.rfc-editor.org/rfc/rfc8288.html | 2026-11-02 | standard |
| 26 | IANA link relations include describedby, alternate, api-catalog, service-desc, service-doc; 'sitemap' not registered | VERIFIED | https://www.iana.org/assignments/link-relations/link-relations.xhtml | 2026-11-02 | R2 §4 #27 |
| 27 | Ch7 layer appends api-catalog to home Link header; values from Ch6 survive (tested upto 7) | VERIFIED | https://github.com/webmaxru/agent-ready-web-demos | 2026-11-02 | run 2 Nov |
| 28 | No survey measures whether non-negotiating fetchers follow Link rel=alternate | OPINION | https://llmstxt.org/ | 2026-11-02 | absence of evidence |
| 29 | Listings 6.1, 6.2, 6.4, 6.6 byte-identical with demo files; 6.3 and 6.5 real output excerpts | VERIFIED | https://github.com/webmaxru/agent-ready-web-demos | 2026-11-02 | checked 2 Nov |

### Demos

- Layer: `nordlys-cabins/layers/06-agent-content/` (index.js, negotiate.js, markdown.js, llms.js, feed.js, token-compare.js); imports POLICY and contentSignal from layer 04
- Tests: `nordlys-cabins/tests/ch06-agent-content.test.js` (7 tests, node:test)
- Command: `node --test tests/ch06-*.test.js`; token comparison: `npm install --no-save gpt-tokenizer@4.1.0 && node layers/06-agent-content/token-compare.js`
- Result 2026-11-02: 7/7 pass; all unit tests with layers 00, 02, 03, 04, 05, 06 together: 60/60 pass; with layer 07 added, /developers.md and the home Link header (api-catalog appended) still work
- Lighthouse 13.6.0 Agentic Browsing on the home page: llms-txt N/A (upto 5) → pass (upto 6), category 100 both
- Versions: Node.js 22.23.2, hono 4.13.16, gpt-tokenizer 4.1.0 (optional, not a dependency)

### Figures

- Figure 6.1 figure-6-1.svg — one URL, two representations (negotiation, .md, Vary)
- Figure 6.2 figure-6-2.svg — tokens per page, HTML vs Markdown (measured)
- Figure 6.3 figure-6-3.svg — how agents find the content (robots, sitemap, llms.txt, Link, feed)
