## Chapter 4: Who gets in: robots.txt, AI crawlers and content signals

| # | Claim / API / listing (short) | Status (VERIFIED / UNVERIFIED / OPINION) | Source URL | Retrieved | Note |
|---|---|---|---|---|---|
| 1 | Radar crawl purpose 7 days to 2 Nov 2026: Training 41.4%, Training & Search 41.3%, Search 12.3%, User action 3.7%, Undeclared 1.3% | VERIFIED | https://radar.cloudflare.com/ai-insights | 2026-11-02 | R1 §3 #18 |
| 2 | Crawl-to-refer: Perplexity 4.9K:1 (−24.9% week), OpenAI 1.4K:1, Anthropic 540.8:1, Google 4.8:1 | VERIFIED | https://radar.cloudflare.com/ai-insights | 2026-11-02 | R1 §3 #24; text rounds to 4,900/1,400/541/4.8 |
| 3 | 16% of responses to AI bots are 403 | VERIFIED | https://radar.cloudflare.com/ai-insights | 2026-11-02 | R1 §3 #22 |
| 4 | Top 10k: 4,387 robots.txt files; GPTBot disallowed by 708 (509 fully) | VERIFIED | https://radar.cloudflare.com/ai-insights | 2026-11-02 | R1 §3 #25 |
| 5 | Content Signals on 10,279 of 115,468 domains (8.9%) in Nov 2026 snapshot | VERIFIED | https://radar.cloudflare.com/ai-insights#adoption-of-ai-agent-standards | 2026-11-02 | R1 §3 #1, #6 |
| 6 | April 2026: about 4% declared Content Signals | VERIFIED | https://blog.cloudflare.com/agent-readiness/ | 2026-11-02 | R1 §2 #3 |
| 7 | RFC 9309 published Sept 2022, Standards Track; 'not a form of access authorization'; 500 KiB parse minimum; longest match | VERIFIED | https://www.rfc-editor.org/rfc/rfc9309.html | 2026-11-02 | R2 §5 #3-5 |
| 8 | Groups do not inherit: a crawler obeys only the most specific matching group (else *) | VERIFIED | https://www.rfc-editor.org/rfc/rfc9309.html | 2026-11-02 | RFC 9309 §2.2.1; also robots-parser test shows behaviour |
| 9 | Google: 4xx (except 429) = no restrictions; 5xx = stops crawling first 12 h; caches up to 24 h; 500 KiB limit | VERIFIED | https://developers.google.com/search/docs/crawling-indexing/robots/robots_txt | 2026-11-02 | R2 §5 #6; re-read page 2 Nov |
| 10 | Google: sitemap field 'isn't tied to any specific user agent and may be followed by all crawlers' | VERIFIED | https://developers.google.com/search/docs/crawling-indexing/robots/robots_txt | 2026-11-02 | read 2 Nov |
| 11 | Disallowed URL cannot convey noindex; may be indexed without content | OPINION | https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag | 2026-11-02 | standard SEO knowledge, consistent with Google docs |
| 12 | OpenAI: GPTBot training, OAI-SearchBot search, ChatGPT-User 'robots.txt rules may not apply' | VERIFIED | https://platform.openai.com/docs/bots | 2026-11-02 | R2 §5 #7, R4 §4 #2 |
| 13 | Anthropic: ClaudeBot, Claude-User, Claude-SearchBot all honour robots.txt; disabling Claude-User 'prevents our system from retrieving your content in response to a user query'; IP blocking 'may not work correctly or persistently guarantee an opt-out' | VERIFIED | https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler | 2026-11-02 | R2 §5 #9-10 |
| 14 | Perplexity: PerplexityBot search 'not used to crawl content for AI foundation models'; Perplexity-User 'generally ignores robots.txt rules' | VERIFIED | https://docs.perplexity.ai/guides/bots | 2026-11-02 | re-read 2 Nov |
| 15 | Google-Extended is a control token, no crawler; 'does not impact a site's inclusion in Google Search nor is it used as a ranking signal' | VERIFIED | https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers | 2026-11-02 | R2 §5 #12 |
| 16 | Google intends to support __usage_ai-training in early 2027 (page updated 30 Oct 2026), quote | VERIFIED | https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers | 2026-11-02 | R2 §5 #13 |
| 17 | Google user-triggered fetchers incl. Google-Agent 'generally ignore robots.txt rules' | VERIFIED | https://developers.google.com/search/docs/crawling-indexing/google-user-triggered-fetchers | 2026-11-02 | R2 §5 #14 |
| 18 | Applebot-Extended 'does not crawl webpages'; opt-out of training | VERIFIED | https://support.apple.com/en-us/119829 | 2026-11-02 | R2 §5 #15 |
| 19 | Amazon: Amazonbot 'used to improve our products and services' and 'may be used to train Amazon AI models'; respects REP with cached copy up to 30 days; Amzn-SearchBot search not training; Amzn-User 'may not follow all robots.txt directives' | VERIFIED | https://developer.amazon.com/amazonbot | 2026-11-02 | re-read 2 Nov |
| 20 | Common Crawl CCBot; warns of spoofed CCBot UAs | VERIFIED | https://commoncrawl.org/ccbot | 2026-11-02 | R2 §5 #17 |
| 21 | Mistral: MistralAI-Training ('Webmasters can disallow this user agent'), MistralAI-Index (search only), MistralAI-User 'governs which sites these user requests can be made to' | VERIFIED | https://docs.mistral.ai/robots | 2026-11-02 | re-read 2 Nov |
| 22 | Meta-ExternalAgent / Meta-ExternalFetcher purposes | UNVERIFIED | https://developers.facebook.com/documentation/sharing/webmasters/web-crawlers | 2026-11-02 | page returned HTTP 400; snippet only; text says so |
| 23 | Bytespider has no official documentation; community reports non-compliance | UNVERIFIED | https://github.com/ai-robots-txt/ai.robots.txt/issues/108 | 2026-11-02 | phrased as 'community sources report' |
| 24 | www.cloudflare.com/robots.txt lists Anthropic-AI and Claude-Web; blog.cloudflare.com has Content-Signal inside * group | VERIFIED | https://www.cloudflare.com/robots.txt | 2026-11-02 | fetched 2 Nov 2026 |
| 25 | ai.robots.txt repo: list of AI agents to block, robots.txt + server configs (.htaccess, nginx, Caddy, HAProxy, lighttpd) | VERIFIED | https://github.com/ai-robots-txt/ai.robots.txt | 2026-11-02 | GitHub API 2 Nov |
| 26 | Content Signals Policy 24 Sep 2025: search/ai-input/ai-train definitions; absence = no meaning; Art. 4 DSM reservation; CC0 | VERIFIED | https://blog.cloudflare.com/content-signals-policy/ | 2026-11-02 | R1 §2 #13-17, R2 §5 #27-29; comment text read in blog.cloudflare.com/robots.txt |
| 27 | Managed robots.txt on >3.8M domains (Sep 2025), with search=yes, ai-train=no and no ai-input | VERIFIED | https://blog.cloudflare.com/content-signals-policy/ | 2026-11-02 | R2 §5 #28 |
| 28 | draft-romm-aipref-contentsignals-00, 1 Oct 2025, individual, 'Expired & archived', last updated 2026-04-04 | VERIFIED | https://datatracker.ietf.org/doc/draft-romm-aipref-contentsignals/ | 2026-11-02 | read 2 Nov |
| 29 | No vendor page in Table 4.2 mentions Content Signals; no compliance measurement found | OPINION | https://blog.cloudflare.com/content-signals-policy/ | 2026-11-02 | absence of evidence; phrased as 'I found no' |
| 30 | isitagentready L2 = L1 + AI bot rules + Content Signals; robotsTxtAiRules passes on wildcard; contentSignals rule; robotsTxt needs 200/text/plain/User-agent | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | R1 §1 checks table, #7, #12 |
| 31 | Cloudflare Markdown for Agents default Content-Signal ai-train=yes, search=yes, ai-input=yes unless origin sets header | VERIFIED | https://developers.cloudflare.com/fundamentals/reference/markdown-for-agents/ | 2026-11-02 | R2 §4 #19 |
| 32 | Lighthouse 13.6.0 SEO robots-txt audit safelist includes content-signal, not content-usage or agentmap | VERIFIED | https://github.com/GoogleChrome/lighthouse/blob/main/core/audits/seo/robots-txt.js | 2026-11-02 | read in npm lighthouse@13.6.0 package source 2 Nov |
| 33 | Lighthouse agentic-browsing auditRefs: agent-accessibility-tree, webmcp x3, CLS, llms-txt, ard-schema; ARD gatherer reads robots Agentmap | VERIFIED | https://github.com/GoogleChrome/lighthouse/blob/main/core/config/default-config.js | 2026-11-02 | lighthouse@13.6.0 source |
| 34 | aipref WG: vocab-08 (14 Sep 2026), attach-05 (19 Aug 2026), both Proposed Standard targets | VERIFIED | https://datatracker.ietf.org/wg/aipref/documents/ | 2026-11-02 | R2 §5 #21 |
| 35 | vocab-08 labels train-ai, ai-use, search; definitions quoted; 'DO NOT REFLECT CONSENSUS'; search overrides other categories incl. search-only training; example train-ai=y, search=n | VERIFIED | https://www.ietf.org/archive/id/draft-ietf-aipref-vocab-08.txt | 2026-11-02 | read 2 Nov |
| 36 | attach-05 (Illyes, Thomson): Content-Usage header and robots rule; example robots block quoted | VERIFIED | https://www.ietf.org/archive/id/draft-ietf-aipref-attach-05.txt | 2026-11-02 | read 2 Nov, example copied verbatim |
| 37 | draft-kelley-aipref-training-preference-signal-00, K. Kelley (Anthropic), 30 Oct 2026, User-Agent: __usage_ai-training | VERIFIED | https://datatracker.ietf.org/doc/draft-kelley-aipref-training-preference-signal/ | 2026-11-02 | read 2 Nov |
| 38 | No crawler documents reading Content-Usage today | OPINION | https://datatracker.ietf.org/wg/aipref/documents/ | 2026-11-02 | from vendor pages read; Google states intent for 2027 only |
| 39 | DSM Art. 4(3) 'in an appropriate manner, such as machine-readable means' | VERIFIED | https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32019L0790 | 2026-11-02 | EUR-Lex text via search snippet (page served 202 to our client) |
| 40 | AI Act Art. 53(1)(c) copyright policy, 'including through state-of-the-art technologies' | VERIFIED | https://artificialintelligenceact.eu/article/53/ | 2026-11-02 | R2 §5 #32 |
| 41 | GPAI Code of Practice published 10 Jul 2025; copyright chapter commits honouring robots.txt | VERIFIED | https://digital-strategy.ec.europa.eu/en/policies/contents-code-gpai | 2026-11-02 | date verified; robots commitment per secondary summary (R2 §5 #33) |
| 42 | TDMRep: W3C CG report 2024, /.well-known/tdmrep.json, header or meta, tdm-reservation 1, tdm-policy | VERIFIED | https://w3c-cg.github.io/tdm-reservation-protocol/spec/ | 2026-11-02 | R2 §5 #30-31 |
| 43 | noai/noimageai from DeviantArt Nov 2022; no vendor documents honouring | VERIFIED | https://www.deviantart.com/team/journal/UPDATE-All-Deviations-Are-Opted-Out-of-AI-Datasets-934500371 | 2026-11-02 | R2 §5 #34 (non-support inferred from vendor docs) |
| 44 | ai.txt: Spawning generator and draft-car-ai-txt-wellknown-00 (12 Jun 2026) | VERIFIED | https://datatracker.ietf.org/doc/draft-car-ai-txt-wellknown/00/ | 2026-11-02 | R2 §5 #35 |
| 45 | Google nosnippet prevents direct input for AI Overviews/AI Mode; data-nosnippet; X-Robots-Tag | VERIFIED | https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag | 2026-11-02 | R2 §5 #36 |
| 46 | Search Console 'Search generative AI control': test 3 Jun 2026, all sites 31 Aug 2026; quote 'Sites that opt out will not receive traffic or impressions...' | VERIFIED | https://blog.google/products-and-platforms/products/search/new-controls-website-owners/ | 2026-11-02 | R2 §5 #1-2 |
| 47 | Cloudflare AI Crawl Control: allow/block rules per crawler, metrics; referrals paid plans only | VERIFIED | https://developers.cloudflare.com/ai-crawl-control/ | 2026-11-02 | read 2 Nov + R4 §4 #12 |
| 48 | Vercel Bot Management: AI bots managed ruleset (training/search/user-generated fetches), all plans, log or deny; verified bots chatgpt-user/operator as ai_assistant | VERIFIED | https://vercel.com/docs/bot-management | 2026-11-02 | read 2 Nov (last_updated 2026-09-10) + R4 §4 #13 |
| 49 | AWS WAF and Akamai verify signed agents | VERIFIED | https://datatracker.ietf.org/wg/webbotauth/documents/ | 2026-11-02 | FACTS R3 #6 (details in Ch15) |
| 50 | Google lastmod used if 'consistently and verifiably' accurate; ignores priority/changefreq | VERIFIED | https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap | 2026-11-02 | read 2 Nov |
| 51 | robots-parser 3.0.1 (MIT) on npm; Google's robotstxt C++ library open source | VERIFIED | https://www.npmjs.com/package/robots-parser | 2026-11-02 | npm registry + GitHub API 2 Nov |
| 52 | Listing 4.1–4.6 byte-identical to demo files; Listing 4.3 is real output of the demo | VERIFIED | https://github.com/webmaxru/agent-ready-web-demos | 2026-11-02 | diffed 2 Nov |
| 53 | Level 1 → 2 for Nordlys after this layer | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | by documented rules mirrored in the layer audit; real scanner cannot reach localhost (said in text) |

### Demos

- Layer: `nordlys-cabins/layers/04-crawler-controls/` (index.js, policy.js, agents.js, robots.js, sitemap.js)
- Tests: `nordlys-cabins/tests/ch04-crawler-controls.test.js` (7 tests, node:test)
- Command: `node --test tests/ch04-*.test.js` (in nordlys-cabins)
- Result 2026-11-02: 7/7 pass; core tests 29/29 still pass with the layer present
- Versions: Node.js 22.23.2, hono 4.13.16, @hono/node-server 2.1.6, robots-parser 3.0.1 (needs adding as a devDependency of nordlys-cabins, see report)

### Figures

- Figure 4.1 figure-4-1.svg — four purposes, four decisions, where each is written
- Figure 4.2 figure-4-2.svg — from request to enforcement (ask, state, decide, protect)
- Figure 4.3 figure-4-3.svg — which robots.txt group each crawler reads
