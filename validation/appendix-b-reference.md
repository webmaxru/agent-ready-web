# Validation: Appendix B — Files, headers and standards at a glance

All sources retrieved 2026-11-02 unless noted. Research-file references (R1–R4, section.fact) point to /home/user/tab/work/agent-ready-web/shared/research/, where the verbatim quotes are.

| # | Claim | Source | Retrieved |
|---|---|---|---|
| 1 | IANA well-known registry entries and dates (api-catalog permanent 2024-12-23, oauth-protected-resource, agent-card.json 2025-08-01, tdmrep.json provisional, ucp provisional 2026-10-26, vacation-rental.json provisional 2026-08-19; no llms.txt/ard.json/ai-catalog.json) | https://www.iana.org/assignments/well-known-uris (via R2 fact 4.26; page re-fetched 200 today) | 2026-11-02 |
| 2 | RFC 8615 well-known URIs, May 2019, Proposed Standard | https://www.rfc-editor.org/rfc/rfc8615.json | 2026-11-02 |
| 3 | RFC dates and status for 7763, 8288, 9110, 9457 (Aug 2023), 8631 (Informational, Jul 2019), 6750, 8414, 8707, 7591, 8693, 9449, 9421, 9727, 9728, 9745, 8594 (Informational), 9309, 4287 | https://www.rfc-editor.org/rfc/rfcNNNN.json (each fetched today) | 2026-11-02 |
| 4 | RFC 9309: rules are not access authorization | https://www.rfc-editor.org/rfc/rfc9309.html (R2 5.4) | 2026-11-02 |
| 5 | isitagentready check ids, categories, pass conditions, profiles, level rules; WebMCP does not affect level; A2A/AP2 opt-in | https://isitagentready.com/llms-full.txt + page script (R1 §1) | 2026-11-02 |
| 6 | Lighthouse agentic-browsing: 7 audits, groups, scoring rules, 40-tool warning, llms-txt N/A/fail rules, ard-schema discovery order and legacy ai-catalog warning, fraction display, Chrome 150+ | https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring ; https://github.com/GoogleChrome/lighthouse/releases/tag/v13.6.0 (R1 §5) | 2026-11-02 |
| 7 | Lighthouse 13.6.0 released 2026-10-27 | https://github.com/GoogleChrome/lighthouse/releases/tag/v13.6.0 (R1 §5 fact 16) | 2026-11-02 |
| 8 | Web Bot Auth draft-ietf-webbotauth-httpsig-protocol-01, 29 Oct 2026; replaces two individual drafts of Mar 2026 | https://datatracker.ietf.org/wg/webbotauth/documents/ (R3 5.1, 5.2) | 2026-11-02 |
| 9 | Web Bot Auth: tag MUST be web-bot-auth | https://www.ietf.org/archive/id/draft-ietf-webbotauth-httpsig-protocol-01.txt (read today) | 2026-11-02 |
| 10 | MCP server card paths: SEP-1649 /.well-known/mcp/server-card.json, SEP-2127 <endpoint>/server-card + ai-catalog, isitagentready serves mcp.json; SEP status contradiction | https://modelcontextprotocol.io/seps/2127-mcp-server-cards ; https://blog.cloudflare.com/agent-readiness/ (R3 1.36, 1.39, §8) | 2026-11-02 |
| 11 | ARD v0.91 Proposal 26 Aug 2026, /.well-known/ard.json, not IANA-registered; rel=ard not registered | https://agenticresourcediscovery.org/ ; IANA registries (R2 cross-worker flags) | 2026-11-02 |
| 12 | Agent Skills Discovery RFC v0.2.0, index path and legacy path | https://isitagentready.com/llms-full.txt (R1 §1 fact 24) | 2026-11-02 |
| 13 | A2A 1.0.0 12 Mar 2026, 1.0.1 26 May 2026, AAIF Aug 2026 | https://github.com/a2aproject/A2A/releases ; https://a2a-protocol.org (R3 6.1, 6.2, 6.5) | 2026-11-02 |
| 14 | UCP /.well-known/ucp; Lodging draft dev.ucp.lodging.booking 25 Sep 2026 | https://ucp.dev/specification/overview/ ; https://developers.google.com/hotels/ucp (R3 6.13, 6.16; FACTS R3 #7) | 2026-11-02 |
| 15 | ACP versions to 2026-04-17, beta, merchant discovery not yet defined | https://github.com/agentic-commerce-protocol/agentic-commerce-protocol ; https://www.agenticcommerce.dev/ (R3 6.6, 6.7, 6.9) | 2026-11-02 |
| 16 | AP2 v0.2, extension of A2A/UCP, donated to FIDO | https://ap2-protocol.org/ (R3 6.18, 6.19) | 2026-11-02 |
| 17 | x402 V2 headers PAYMENT-REQUIRED / PAYMENT-SIGNATURE / PAYMENT-RESPONSE; x402 Foundation (Linux Foundation) 2 Apr 2026 | https://docs.x402.org/core-concepts/http-402 ; https://docs.cdp.coinbase.com/x402/support/x402-foundation (R3 5.24, 5.26) | 2026-11-02 |
| 18 | Pay per crawl headers crawler-price / exact / max / charged; closed beta | https://blog.cloudflare.com/introducing-pay-per-crawl/ (R3 5.21; FACTS R3 #7) | 2026-11-02 |
| 19 | TDMRep Final CG Report 10 May 2024, tdmrep.json | https://w3c-cg.github.io/tdm-reservation-protocol/spec/ (R2 5.30) | 2026-11-02 |
| 20 | Content Signals Policy 24 Sep 2025, absent signal conveys no meaning; draft-romm-aipref-contentsignals-00 expired 4 Apr 2026 | https://blog.cloudflare.com/content-signals-policy/ (R1 2.13); Chapter 4 [^ch04-18] | 2026-11-02 |
| 21 | aipref vocab-08 14 Sep 2026, attach-05 19 Aug 2026, Content-Usage header and robots rule, labels train-ai/ai-use/search, vocab not WG consensus | https://datatracker.ietf.org/wg/aipref/documents/ ; https://www.ietf.org/archive/id/draft-ietf-aipref-attach-05.txt (R2 5.21-5.24) | 2026-11-02 |
| 22 | draft-kelley-aipref-training-preference-signal-00 30 Oct 2026; Google intends to support __usage_ai-training in early 2027 | https://datatracker.ietf.org/doc/draft-kelley-aipref-training-preference-signal/ ; Google common crawlers page (R2 5.13, 5.25) | 2026-11-02 |
| 23 | /.well-known/ai.txt individual draft draft-car-ai-txt-wellknown-00 (June 2026), no vendor reads it | Chapter 4 [^ch04-30] and its text | 2026-11-02 |
| 24 | RSL 1.0 published 10 Dec 2025, robots.txt License: line | https://rslstandard.org/rsl (R3 5.29, 5.30) | 2026-11-02 |
| 25 | DNS-AID draft-mozleywilliams-dnsop-dnsaid-02, 27 May 2026, expires 28 Nov 2026 | https://datatracker.ietf.org/doc/draft-mozleywilliams-dnsop-dnsaid/ (R1 fact 31) | 2026-11-02 |
| 26 | Sitemaps protocol; Google 50 MB / 50,000 URLs | https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap (R2 4.24) | 2026-11-02 |
| 27 | llms.txt v2 (modified 10 Aug 2026, v1 3 Sep 2024), describedby/alternate discovery, page.md and page.html.md, llms-full.txt not in v2 | https://llmstxt.org/ (R2 4.6-4.8) | 2026-11-02 |
| 28 | Markdown for Agents adds Content-Signal header unless origin sets one | https://developers.cloudflare.com/fundamentals/reference/markdown-for-agents/ (R2 4.19) | 2026-11-02 |
| 29 | IANA link relations: describedby, alternate, api-catalog, service-desc, service-doc registered; sitemap and ard not | https://www.iana.org/assignments/link-relations (R2 4.27) | 2026-11-02 |
| 30 | Cloudflare responses send rel=sitemap and rel=api-catalog | https://blog.cloudflare.com/markdown-for-agents/ response headers (R2 4.21) | 2026-11-02 |
| 31 | WAI-ARIA 1.2 Rec 6 Jun 2023; 1.3 WD 4 Jun 2026 | https://www.w3.org/TR/wai-aria-1.2/ ; https://www.w3.org/TR/2026/WD-wai-aria-1.3-20260604/ (R2 2.4, 2.5) | 2026-11-02 |
| 32 | WebMCP spec dated 2 Nov 2026, outputSchema PR #254; declarative attributes in Chrome docs not spec; document.modelContext; navigator.modelContext legacy detected; OT; WebKit oppose / Mozilla neutral | https://webmachinelearning.github.io/webmcp/ ; FACTS.md R3 #5; R1 §1 webMcp row | 2026-11-02 |
| 33 | OpenAPI 3.2.0 19 Sep 2025, 3.2.1 10 Sep 2026; Arazzo 1.1.0 17 May 2026 | https://spec.openapis.org/oas/v3.2.1.html ; https://spec.openapis.org/arazzo/latest.html (R3 3.1, 3.2, 3.4) | 2026-11-02 |
| 34 | MCP 2026-07-28 current, previous 2025-11-25; Mcp-Session-Id removed (SEP-2567); Mcp-Method/Mcp-Name headers | https://modelcontextprotocol.io/specification/2026-07-28/changelog (R3 1.1-1.3; FACTS R3 #1) | 2026-11-02 |
| 35 | MCP authorization: OAuth 2.1 draft-13, RFC 9728 required, CIMD SHOULD, DCR deprecated | https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization (R3 2.1, 2.5, 2.14) | 2026-11-02 |
| 36 | OAuth 2.1 latest draft-ietf-oauth-v2-1-17, 31 Oct 2026 | https://datatracker.ietf.org/api/v1/doc/document/draft-ietf-oauth-v2-1/ (fetched today: rev 17, 2026-10-31) | 2026-11-02 |
| 37 | CIMD draft-02 6 Jul 2026; ID-JAG draft-06 31 Oct 2026 | https://datatracker.ietf.org/doc/draft-ietf-oauth-client-id-metadata-document/ ; https://datatracker.ietf.org/doc/draft-ietf-oauth-identity-assertion-authz-grant/ (R3 2.23, 2.24) | 2026-11-02 |
| 38 | DPoP on MCP roadmap Agent Identity WG | https://modelcontextprotocol.io/development/roadmap (R3 1.34) | 2026-11-02 |
| 39 | Idempotency-Key draft-08 22 Oct 2026; RateLimit draft-11 May 2026 expires 24 Nov 2026 | https://www.ietf.org/archive/id/draft-ietf-httpapi-idempotency-key-header-08.txt ; https://www.ietf.org/archive/id/draft-ietf-httpapi-ratelimit-headers-11.txt (R3 3.11, 3.13) | 2026-11-02 |
| 40 | RFC 9745 Deprecation Structured Field Date example; RFC 8594 Sunset HTTP-date | https://www.rfc-editor.org/rfc/rfc9745.html ; https://www.rfc-editor.org/rfc/rfc8594.html (R4 5.7, 5.8) | 2026-11-02 |
| 41 | Visa TAP built on RFC 9421 | https://developer.visa.com/docs/trusted-agent-protocol (R3 5.31) | 2026-11-02 |
| 42 | NLWeb repo, no releases, last push 11 Aug 2026 | https://github.com/nlweb-ai/NLWeb (R2 6.5) | 2026-11-02 |
| 43 | OWASP LLM Top 10 2025; OWASP Agentic Top 10 2026 published 9 Dec 2025, ASI01-ASI10 | https://genai.owasp.org (R4 1.12, 1.13) | 2026-11-02 |
| 44 | VRP v0.1 single-maintainer draft updated 2026-11-01 | https://vacationrentalprotocol.com/spec/well-known-uri-v0.1 (R2 4.28) | 2026-11-02 |
| 45 | auth.md (WorkOS proposal); poppy.json draft 0.1; acp.json, ucp, x402, mpp checks | https://isitagentready.com/llms-full.txt (R1 §1) | 2026-11-02 |
| 46 | Nordlys Cabins serves / skips the listed items | Measured today: demos/chapters/appendix-b-reference/check-reference.mjs against nordlys-cabins with all layers (node 24.22.1), test 2/2 pass | 2026-11-02 |
| 47 | JSON-LD 1.1 W3C Recommendation, July 2020 | https://www.w3.org/TR/json-ld11/ (fetched today: Recommendation 16 July 2020) | 2026-11-02 |
| 48 | OpenID Connect Discovery 1.0 registered openid-configuration | IANA well-known registry (re-fetched today) | 2026-11-02 |
| 49 | MPP launched 18 Mar 2026 by Stripe and Tempo | Chapter 12 [^ch12-23], [^ch12-24] (Stripe docs and blog) | 2026-11-02 |
