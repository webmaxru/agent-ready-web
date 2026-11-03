## Chapter 19: Measuring agent traffic and outcomes

| # | Claim / API / listing (short) | Status | Source URL | Retrieved | Note |
| --- | --- | --- | --- | --- | --- |
| 1 | Seven labels; training/search/user-fetch distinction | OPINION | shared/research/R4-trust-ops.md §4 |  |  |
| 2 | OpenAI: ChatGPT-User 'robots.txt rules may not apply' | VERIFIED | https://platform.openai.com/docs/bots | 2026-11-02 | verbatim |
| 3 | Google user-triggered fetchers 'generally ignore robots.txt rules' | VERIFIED | https://developers.google.com/crawling/docs/crawlers-fetchers/google-user-triggered-fetchers | 2026-11-02 | verbatim |
| 4 | OpenAI tokens GPTBot, OAI-SearchBot, ChatGPT-User, OAI-AdsBot and IP JSON URLs | VERIFIED | https://platform.openai.com/docs/bots | 2026-11-02 | R4 §4 fact 1 |
| 5 | Anthropic ClaudeBot, Claude-SearchBot, Claude-User; bots.json | VERIFIED | https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler | 2026-11-02 | R4 fact 4 |
| 6 | Perplexity PerplexityBot + Perplexity-User, both IP JSON URLs | VERIFIED | https://docs.perplexity.ai/docs/resources/perplexity-crawlers | 2026-11-02 | read this session: perplexity-user.json listed |
| 7 | Google-Agent UA token and user-triggered-agents.json | VERIFIED | https://developers.google.com/crawling/docs/crawlers-fetchers/google-user-triggered-fetchers | 2026-11-02 | UA string read this session |
| 8 | Googlebot common-crawlers.json + reverse DNS names crawl-***.googlebot.com, geo-crawl-***.geo.googlebot.com, google.com / gae.googleusercontent.com | VERIFIED | https://developers.google.com/crawling/docs/crawlers-fetchers/verify-google-requests | 2026-11-02 | R4 fact 8 |
| 9 | bingbot range file at bing.com/toolbox/bingbot.json | VERIFIED (file) / UNVERIFIED (docs page) | https://www.bing.com/toolbox/bingbot.json | 2026-11-02 | file fetched; Bing Webmaster help page is script-rendered, not read |
| 10 | GPTBot/1.4, OAI-SearchBot/1.4, 'version may change'; robots.txt marker in UA | VERIFIED | https://platform.openai.com/docs/bots | 2026-11-02 | R4 fact 3 |
| 11 | Nine range files: creationTime 2 Nov 2026 (Google) back to Jan 2026 (OAI-SearchBot), Bing Jan 2024; ChatGPT-User 235 prefixes, Anthropic 14 | VERIFIED | demos chapters/19-measuring-agent-traffic/ip-ranges/2026-11-02/SOURCES.md | 2026-11-02 | fetched by me |
| 12 | Anthropic: IP blocking 'may not work correctly or persistently guarantee an opt-out' | VERIFIED | https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler | 2026-11-02 | R4 fact 4 |
| 13 | Web Bot Auth = RFC 9421 signatures + Signature-Agent | VERIFIED | https://www.ietf.org/archive/id/draft-ietf-webbotauth-httpsig-protocol-01.txt | 2026-11-02 | R3 5.1 |
| 14 | OpenAI key directory at chatgpt.com/.well-known/http-message-signatures-directory | VERIFIED | https://chatgpt.com/.well-known/http-message-signatures-directory | 2026-11-02 | fetched 200 this session |
| 15 | Google experiments with agent.bot.goog; 'We don't sign every request' | VERIFIED | https://developers.google.com/crawling/docs/crawlers-fetchers/web-bot-auth | 2026-11-02 | R3 5.9/5.10 |
| 16 | Combined log format has no signature field | VERIFIED | demo test 'the report on the synthetic week adds up' | 2026-11-02 | design fact of the format |
| 17 | Claude in Chrome, Gemini in Chrome, Copilot in Edge run in the person's browser; requests carry the person's UA/cookies/IP | OPINION (inference from product docs) | ch01 footnote 8 sources | 2026-11-02 | phrased 'as far as their documentation shows' |
| 18 | Referrer-Policy strict-origin-when-cross-origin sent by Nordlys | VERIFIED | demos nordlys-cabins/LAYERS.md (base headers) | 2026-11-02 |  |
| 19 | utm_source=chatgpt.com added by ChatGPT | UNVERIFIED | https://www.tryprofound.com/articles/get-your-product-discovered-in-chatgpt-shopping | 2026-11-02 | secondary source; not found in OpenAI docs; text says so |
| 20 | GA4 AI Assistant channel; AI Overviews/AI Mode count as Organic Search | VERIFIED | https://support.google.com/analytics/answer/9756891 | 2026-11-02 | R4 fact 11 |
| 21 | Crawl-to-refer definition (Jul 2025) | VERIFIED | https://blog.cloudflare.com/ai-search-crawl-refer-ratio-on-radar | 2026-11-02 | R4 fact 9; title read this session |
| 22 | Jul 2025 ratios: Anthropic 38,065.7:1 (286,930.1 Jan), OpenAI 1,091.4:1, Perplexity 194.8:1, Microsoft 40.7:1 | VERIFIED | https://blog.cloudflare.com/crawlers-click-ai-bots-training | 2026-11-02 | R4 fact 10 |
| 23 | Radar week to 2 Nov 2026: Perplexity 4.9K:1 (-24.9%), OpenAI 1.4K:1 (-24%), Anthropic 540.8:1 (+8.4%), Google 4.8:1 | VERIFIED | https://radar.cloudflare.com/ai-insights | 2026-11-02 | R1 §3 fact 24 (rendered page read by R1) |
| 24 | Radar client types: non-AI bot 54.4%, human 35.5%, AI bot 6%, mixed 4.1% | VERIFIED | https://radar.cloudflare.com/ai-insights | 2026-11-02 | R1 fact 23 |
| 25 | Radar crawl purpose: training 41.4, training&search 41.3, search 12.3, user action 3.7, undeclared 1.3 | VERIFIED | https://radar.cloudflare.com/ai-insights | 2026-11-02 | R1 fact 18 |
| 26 | Radar status to AI bots: 200 59.6, 403 16, 404 7.5, 301 5.9, 429 2.6 | VERIFIED | https://radar.cloudflare.com/ai-insights | 2026-11-02 | R1 fact 22 |
| 27 | Radar content types HTML 73.2%, Markdown <0.1% | VERIFIED | https://radar.cloudflare.com/ai-insights | 2026-11-02 | R1 fact 20 |
| 28 | Radar API needs token; adoption data weekly on Mondays | VERIFIED | https://developers.cloudflare.com/changelog/post/2026-04-17-radar-ai-insights-updates/ | 2026-11-02 | R1 facts 27-28 |
| 29 | Cloudflare AI Crawl Control metrics; referrals paid plans only | VERIFIED | https://developers.cloudflare.com/ai-crawl-control/features/analyze-ai-traffic/ | 2026-11-02 | R4 fact 12 |
| 30 | Cloudflare: signed agents folded into Verified bots 1 Jul 2026, Direct vs Intermediary | VERIFIED | https://developers.cloudflare.com/bots/concepts/bot/verified-bots/ | 2026-11-02 | R3 5.11 |
| 31 | Vercel AI bots ruleset (training/search/user-initiated), verified bots directory, chatgpt-user/chatgpt-operator ai_assistant, rDNS + Web Bot Auth | VERIFIED | https://vercel.com/docs/bot-management | 2026-11-02 | R4 fact 13 |
| 32 | AWS WAF Web Bot Auth 21 Nov 2025, verified WBA bots allowed by default; CloudFront + regional | VERIFIED | https://aws.amazon.com/about-aws/whats-new/2025/11/aws-waf-web-bot-auth-support/ | 2026-11-02 | R3 5.15/5.16 |
| 33 | OpenAI robots changes ~24 h for search; Perplexity up to 24 h | VERIFIED | https://platform.openai.com/docs/bots ; https://docs.perplexity.ai/docs/resources/perplexity-crawlers | 2026-11-02 | R4 facts 2, 5 |
| 34 | MCP 2026-07-28 requires Mcp-Method and Mcp-Name on Streamable HTTP POST (SEP-2243) | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/changelog | 2026-11-02 | read this session |
| 35 | nginx log_format escape=json, $http_<name>, $sent_http_content_type | VERIFIED | https://nginx.org/en/docs/http/ngx_http_log_module.html | 2026-11-02 | standard nginx variables; config not run on this box |
| 36 | GDPR: IP addresses in logs are personal data (pointer to Ch17) | OPINION / see Ch17 | Chapter 17 validation | 2026-11-02 | not legal advice |
| 37 | KPI table | OPINION | R4 §4 'Proposed KPIs' | 2026-11-02 | labelled as proposals |
| 38 | Listing 19.1 agents.json lines 1-20 | VERIFIED | demos chapters/19-measuring-agent-traffic/agents.json | 2026-11-02 | byte-identical excerpt |
| 39 | Listing 19.2 classify.mjs lines 21-55 | VERIFIED | demos chapters/19-measuring-agent-traffic/lib/classify.mjs | 2026-11-02 | byte-identical excerpt |
| 40 | Listing 19.3 report output | VERIFIED | output of node report.mjs fixtures/synthetic-access.jsonl (Node 22.23.2) | 2026-11-02 | synthetic data, labelled |
| 41 | Listing 19.4 layer index.js lines 36-63 | VERIFIED | demos nordlys-cabins/layers/19-agent-analytics/index.js | 2026-11-02 | byte-identical excerpt |
| 42 | jq output of training topPaths | VERIFIED | run on the synthetic log | 2026-11-02 | real output |

### Demos

- `chapters/19-measuring-agent-traffic/` (no dependencies): `node --test "test/*.test.mjs"` → 9 pass, 0 fail (Node 22.23.2, 2026-11-02). Synthetic log: `node make-synthetic-log.mjs` (2,000 requests, invented mix, labelled synthetic). IP range files fetched 2026-11-02.
- `nordlys-cabins/layers/19-agent-analytics/` + `tests/ch19-agent-analytics.test.js`: `node --test tests/ch19-agent-analytics.test.js` → 7 pass, 0 fail, with and without layer 15 (W5's 15-bot-identity copied in). hono 4.13.16, @hono/node-server 2.1.6.

### Figures

- figure-19-1 (evidence ladder), figure-19-3 (pipeline of layers 15 and 19), figure-19-2 (Radar crawl-to-refer, log scale, week to 2 Nov 2026).
