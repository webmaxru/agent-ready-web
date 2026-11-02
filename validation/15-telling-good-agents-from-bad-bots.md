## Chapter 15: Telling good agents from bad bots

Validated by writer W5b on 2 November 2026. Sources first from FACTS.md and research R3 §5, R4 §4, R1 §1 and §3, then primary sources fetched directly where noted.

| # | Claim / API / listing (short) | Status (VERIFIED / UNVERIFIED / OPINION) | Source URL | Retrieved | Note |
| --- | --- | --- | --- | --- | --- |
| 1 | UA tokens table lives in Ch4/Ch19; anyone can send any UA | OPINION | https://platform.openai.com/docs/bots | 2026-11-02 | Cross-ref; tokens from FACTS/R4 §4 |
| 2 | Common Crawl: "aware of crawlers falsely identifying themselves as CCBot" | VERIFIED | https://commoncrawl.org/ccbot | 2026-11-02 | R2 §5 row 17 |
| 3 | Browser-built agents carry the person's UA, cookies, address; unsigned cloud browsers look like Chrome | OPINION | https://developers.google.com/crawling/docs/crawlers-fetchers/web-bot-auth | 2026-11-02 | Consistent with Ch19 wording; vendor docs do not state UA behaviour of in-browser agents in full |
| 4 | OpenAI IP files gptbot.json, searchbot.json, chatgpt-user.json, adsbot.json | VERIFIED | https://platform.openai.com/docs/bots | 2026-11-02 | R4 §4 row 1 |
| 5 | Anthropic IPs at https://claude.com/crawling/bots.json; quote "may not work correctly or persistently guarantee an opt-out" | VERIFIED | https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler | 2026-11-02 | R4 §4 row 4; quote as used in Ch4 |
| 6 | Perplexity perplexitybot.json | VERIFIED | https://docs.perplexity.ai/docs/resources/perplexity-crawlers | 2026-11-02 | R4 §4 row 5 |
| 7 | Google publishes five IP files, common-crawlers.json … user-triggered-agents.json | VERIFIED | https://developers.google.com/crawling/docs/crawlers-fetchers/verify-google-requests | 2026-11-02 | R4 §4 row 8 |
| 8 | draft-illyes-webbotauth-jafar-01 proposes one JSON format for IP ranges | VERIFIED | https://datatracker.ietf.org/wg/webbotauth/documents/ | 2026-11-02 | R3 5.5, R4 row 17 |
| 9 | Google: reverse DNS, domain check, forward DNS; quote "Verify that the domain name is either googlebot.com, google.com, or googleusercontent.com" | VERIFIED | https://developers.google.com/crawling/docs/crawlers-fetchers/verify-google-requests | 2026-11-02 | Fetched by W5b 2026-11-02, verbatim |
| 10 | Google-Agent quote "agents hosted on Google infrastructure to navigate the web and perform actions upon user request"; user-triggered-agents.json; fetchers "generally ignore robots.txt rules" | VERIFIED | https://developers.google.com/crawling/docs/crawlers-fetchers/google-user-triggered-fetchers | 2026-11-02 | R4 §4 rows 6–7 |
| 11 | RFC 9421 HTTP Message Signatures, February 2024 | VERIFIED | https://www.rfc-editor.org/rfc/rfc9421 | 2026-11-02 | R3 5.6 |
| 12 | Signature-Input / Signature are Structured Fields dictionaries; multiple labelled signatures | VERIFIED | https://www.rfc-editor.org/rfc/rfc9421 | 2026-11-02 | RFC 9421 §4 |
| 13 | WG draft draft-ietf-webbotauth-httpsig-protocol-01, 29 Oct 2026, Thibault Meunier (Cloudflare), Sandor Major (Google) | VERIFIED | https://www.ietf.org/archive/id/draft-ietf-webbotauth-httpsig-protocol-01.txt | 2026-11-02 | Authors' Addresses read by W5b |
| 14 | Merged earlier architecture and directory drafts | VERIFIED | https://datatracker.ietf.org/wg/webbotauth/documents/ | 2026-11-02 | R3 5.2 |
| 15 | Must cover @authority or @target-uri; created+expires required; "it is RECOMMENDED that expires be no more than 24 hours after created"; keyid = JWK SHA-256 thumbprint (RFC 7638, RFC 8037 A.3); tag web-bot-auth | VERIFIED | https://www.ietf.org/archive/id/draft-ietf-webbotauth-httpsig-protocol-01.txt | 2026-11-02 | §5.2 verbatim |
| 16 | Signature-Agent is a Dictionary of https URLs; members with parameters MUST be ignored; legacy bare-string form still sent | VERIFIED | https://www.ietf.org/archive/id/draft-ietf-webbotauth-httpsig-protocol-01.txt | 2026-11-02 | §5.2.1 |
| 17 | Directory is a JWKS with media type application/http-message-signatures-directory+json at /.well-known/http-message-signatures-directory, HTTPS required | VERIFIED | https://www.ietf.org/archive/id/draft-ietf-webbotauth-httpsig-protocol-01.txt | 2026-11-02 | §5.5.1, §8.1 |
| 18 | Listing 15.1 is real output of signer.mjs against Nordlys (port 3015) | VERIFIED | https://github.com/webmaxru/agent-ready-web-demos | 2026-11-02 | Run by W5b 2026-11-02 22:41 UTC, Node 24.22.1 |
| 19 | Quotes: URL resolution "establishes that the host named in the URL served this key set at fetch time", "all it gives you", "does not say that the operator of that URL is honest…" | VERIFIED | https://www.ietf.org/archive/id/draft-ietf-webbotauth-httpsig-protocol-01.txt | 2026-11-02 | §4.4 verbatim |
| 20 | Cloudflare Direct vs Intermediary quotes, transitive trust, Forwarded (RFC 7239) experiment | VERIFIED | https://developers.cloudflare.com/bots/concepts/bot/signed-agents/ | 2026-11-02 | Fetched by W5b 2026-11-02, verbatim |
| 21 | Authority-only signature verifies "against any method, path, or body sent to that authority until it expires" | VERIFIED | https://www.ietf.org/archive/id/draft-ietf-webbotauth-httpsig-protocol-01.txt | 2026-11-02 | §5.2 |
| 22 | No component covers the body; Content-Digest needed; not required | VERIFIED | https://www.ietf.org/archive/id/draft-ietf-webbotauth-httpsig-protocol-01.txt | 2026-11-02 | §5.2 |
| 23 | "defines no additional nonce requirements"; duplicate-nonce rejection needs shared state | VERIFIED | https://www.ietf.org/archive/id/draft-ietf-webbotauth-httpsig-protocol-01.txt | 2026-11-02 | §5.2.3, App. C.6 |
| 24 | WG charter: end-user authentication, HTTP APIs, agent-to-agent out of scope; milestones Apr 2026 and Aug 2026 passed without IESG submission | VERIFIED | https://datatracker.ietf.org/wg/webbotauth/about/ | 2026-11-02 | R3 5.3–5.4 |
| 25 | OpenAI directory live: 1 Ed25519 key with nbf/exp, signature_agent https://chatgpt.com, purpose ai, Cache-Control no-store, no-transform | VERIFIED | https://chatgpt.com/.well-known/http-message-signatures-directory | 2026-11-02 | Fetched by W5b 2026-11-02 |
| 26 | OpenAI signs ChatGPT agent traffic | VERIFIED | https://chatgpt.com/.well-known/http-message-signatures-directory | 2026-11-02 | R4 §4 row 14 |
| 27 | Google: "A subset of requests made by the Google-Agent are signed with Web Bot Auth"; Signature-Agent g="https://agent.bot.goog"; "We don't sign every request of a particular agent. Be sure that you fall back to the established methods of bot verification." | VERIFIED | https://developers.google.com/crawling/docs/crawlers-fetchers/web-bot-auth | 2026-11-02 | Fetched by W5b 2026-11-02, verbatim |
| 28 | Google directory: 5 Ed25519 keys, short kid values, Cache-Control public, max-age=3600 | VERIFIED | https://agent.bot.goog/.well-known/http-message-signatures-directory | 2026-11-02 | Fetched by W5b 2026-11-02 |
| 29 | Visa TAP: verify RFC 9421 signatures of "Visa-approved AI agents" | VERIFIED | https://developer.visa.com/docs/trusted-agent-protocol | 2026-11-02 | R3 5.31; quote as in Ch12 |
| 30 | TAP and Mastercard Agent Pay "leverage Web Bot Auth as the agent authentication layer" | VERIFIED | https://blog.cloudflare.com/secure-agentic-commerce | 2026-11-02 | R3 5.32; Cloudflare blog 24 Oct 2025 |
| 31 | Cloudflare: signed agents folded into Verified bots 1 Jul 2026; verified via WBA, IP list + stable UA, or reverse DNS | VERIFIED | https://developers.cloudflare.com/bots/concepts/bot/verified-bots/ | 2026-11-02 | R3 5.11–5.12, R4 row 18 |
| 32 | AWS WAF WBA support 21 Nov 2025; verified signed bots allowed by default | VERIFIED | https://aws.amazon.com/about-aws/whats-new/2025/11/aws-waf-web-bot-auth-support/ | 2026-11-02 | R3 5.15 |
| 33 | Vercel: reverse DNS + WBA verification; chatgpt-user and chatgpt-operator classed ai_assistant | VERIFIED | https://vercel.com/docs/bot-management | 2026-11-02 | R4 §4 row 13 |
| 34 | Akamai supports Web Bot Auth | UNVERIFIED | https://www.akamai.com/ | 2026-11-02 | Search snippets only; Akamai blog returned 403 (R3 §5 pitfalls). Text says unverified. |
| 35 | Radar: 118 of 115,468 domains (0.10%) publish a WBA directory, data 2026-11-02 | VERIFIED | https://radar.cloudflare.com/ai-insights#adoption-of-ai-agent-standards | 2026-11-02 | R1 §3 rows 1, 12 |
| 36 | isitagentready webBotAuth check (Bot Access Control) informational: "Failures are shown as neutral and do not affect the score." | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | R1 §1 rows 11, line 33 |
| 37 | Level 5: "Level 4 + 2 of 3: Web Bot Auth, all four integration checks, auth metadata" | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | R1 §1 row 10 |
| 38 | cloudflare/web-bot-auth, Apache-2.0: extension signer, Rust, Workers, Caddy verifier | VERIFIED | https://github.com/cloudflare/web-bot-auth | 2026-11-02 | R3 5.17 |
| 39 | npm web-bot-auth 0.2.0 (2026-08-31) sign/verify, Ed25519 + RSA-PSS; http-message-signatures 1.0.6; README cites -protocol-00 | VERIFIED | https://registry.npmjs.org/web-bot-auth | 2026-11-02 | R3 5.18–5.19 and §5 pitfalls |
| 40 | Cloudflare has a BotBase submission form for its bot directory | VERIFIED | https://developers.cloudflare.com/bots/concepts/bot/signed-agents/ | 2026-11-02 | Fetched 2026-11-02 |
| 41 | Key lookup quote "Key lookup MUST be keyed on the (URL, key) pair, not on the key alone" | VERIFIED | https://www.ietf.org/archive/id/draft-ietf-webbotauth-httpsig-protocol-01.txt | 2026-11-02 | §5.4 verbatim |
| 42 | Unsigned request "does not establish whether the sender is human or automated" | VERIFIED | https://www.ietf.org/archive/id/draft-ietf-webbotauth-httpsig-protocol-01.txt | 2026-11-02 | §6.11 verbatim |
| 43 | SSRF precautions: size, key count, timeout, redirects, private ranges | VERIFIED | https://www.ietf.org/archive/id/draft-ietf-webbotauth-httpsig-protocol-01.txt | 2026-11-02 | §6.7 |
| 44 | Verifier "should not fetch the directory for every request"; use HTTP caching; negative cache ≤ 5 min | VERIFIED | https://www.ietf.org/archive/id/draft-ietf-webbotauth-httpsig-protocol-01.txt | 2026-11-02 | App. C.4, C.5 |
| 45 | Test vectors RFC 9421 B.2.6 and draft App. E.2 reproduced by the layer tests | VERIFIED | https://www.rfc-editor.org/rfc/rfc9421 | 2026-11-02 | ch15 tests 1–4 pass |
| 46 | RateLimit headers: draft-ietf-httpapi-ratelimit-headers-11 (HTTPAPI WG, updated 2026-05-23); RateLimit-Policy "name";q;w and RateLimit "name";r;t syntax | VERIFIED | https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/ | 2026-11-02 | Fetched draft text by W5b; examples §3.2, §4.2 |
| 47 | Listing 15.9 headers are real output (curl against Nordlys, other headers omitted) | VERIFIED | https://github.com/webmaxru/agent-ready-web-demos | 2026-11-02 | Run by W5b 2026-11-02 |
| 48 | Pay per crawl, 1 Jul 2025: 402 + crawler-price; crawler-exact-price / crawler-max-price; crawler-charged; requires WBA | VERIFIED | https://blog.cloudflare.com/introducing-pay-per-crawl/ | 2026-11-02 | R3 5.21–5.22 |
| 49 | Pay per crawl closed beta, Cloudflare merchant of record, docs updated 28 Jul 2026; no public adoption numbers | VERIFIED | https://developers.cloudflare.com/ai-crawl-control/features/pay-per-crawl/what-is-pay-per-crawl/ | 2026-11-02 | R3 5.23 and §5 pitfalls |
| 50 | HTTP reserves 402 for future use; pay per crawl and x402 headers incompatible | VERIFIED | https://www.rfc-editor.org/rfc/rfc9110#name-402-payment-required | 2026-11-02 | R3 §5 pitfalls; RFC 9110 §15.5.3 |
| 51 | RSL (Really Simple Licensing) 1.0 published 2025-12-10; editors list; License: line in robots.txt pointing to XML | VERIFIED | https://rslstandard.org/rsl | 2026-11-02 | R3 5.29–5.30; name checked on rslstandard.org 2026-11-02 |
| 52 | TollBit as a commercial intermediary | UNVERIFIED | https://tollbit.com/ | 2026-11-02 | Named only, terms not checked; text says so |
| 53 | Radar: 16% of responses to AI bots are 403, 2.6% are 429, week to 2026-11-02 | VERIFIED | https://radar.cloudflare.com/ai-insights | 2026-11-02 | R1 §3 row 22 |
| 54 | Lighthouse Agentic Browsing has no bot-identity audit | VERIFIED | https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring | 2026-11-02 | R1 §5 audit list (a11y, CLS, WebMCP, llms.txt, ARD) |
| 55 | WG individual drafts: meunier-webbotauth-registry-04 (27 Oct 2026), crawler best practices, JSON IP ranges, anonymous bot auth | VERIFIED | https://datatracker.ietf.org/wg/webbotauth/documents/ | 2026-11-02 | R3 5.5 |
| 56 | Nordlys policy numbers (300/120/60 per minute), 16-key limit, 64 KB, 5 s, 5 min–24 h cache, 60 s negative cache | OPINION | https://github.com/webmaxru/agent-ready-web-demos | 2026-11-02 | Design choices of the demo, stated as such |
| 57 | Verify, don't sign for typical sites; no pay per crawl for booking sites | OPINION | https://blog.cloudflare.com/agent-readiness/ | 2026-11-02 | Author recommendation, consistent with R3 §5 'What a web team does' |

## Demos

- Layer `nordlys-cabins/layers/15-bot-identity/`: index.js, identity.js, verify.js, httpsig.js, directory.js, rdns.js, ratelimit.js, README.md. No dependencies (node:crypto, node:dns).
- Standalone: `chapters/15-signing-agent/` (signer.mjs, package.json, README.md), no dependencies.
- Tests: `nordlys-cabins/tests/ch15-bot-identity.test.js`, 13 tests (RFC 9421 B.2.6 and draft E.2 vectors, tampering, directory URL rules, in-app labels, per-class buckets, RateLimit headers, reverse/forward DNS with a fake resolver, member parameters, key-count limit, negative cache, key exp). `node --test tests/ch15-bot-identity.test.js` → 13 pass, 0 fail (2 Nov 2026, Node 24.22.1, hono 4.13.16, @hono/node-server 2.1.6). Also re-run: ch19-agent-analytics 7/7 (consumes layer 15's label).
- Manual run: server `--upto=15` with NORDLYS_WBA_TRUST=http://127.0.0.1:8977, NORDLYS_WBA_ALLOW_HTTP=1, NORDLYS_WBA_DEBUG=1, then signer.mjs → `200 OK  x-nordlys-bot-identity: verified-agent http://127.0.0.1:8977` (Listing 15.1). curl with a ChatGPT-User UA to /ucp/v1/booking-sessions/bks_missing → 404 with RateLimit headers (Listing 15.9).
- Listings 15.2–15.8 are generated from the files (full files or contiguous excerpts marked "excerpt"), byte-identical.

## Figures

- figure-15-1: three questions about one automated request (software, operator, person) — figures/src/figure-15-1.svg
- figure-15-2: anatomy of a Web Bot Auth check (four steps, two outcomes) — figures/src/figure-15-2.svg
- figure-15-3: the Nordlys bot identity layer, labels to rate-limit buckets and RateLimit headers — figures/src/figure-15-3.svg
