# Appendix B: Files, headers and standards at a glance

This appendix is the reference I wanted on my desk while writing the book. It lists every fixed path, robots.txt line, HTTP header, link relation, markup hook and specification the chapters use. For each one you get the body behind it, its version or draft number, its status on 2 November 2026 and the chapter that teaches it. It also maps each one to the grader checks that read it: the isitagentready.com check ids and the Lighthouse Agentic Browsing audit ids.

Two warnings before the tables. First, status is a moving target. Several entries are individual Internet-Drafts that expire after six months, and two of the discovery paths changed during the months I wrote this book. Every row carries a date for exactly this reason, and Appendix D lists where to check the current state. Second, a well-known path being registered with IANA tells you the name is reserved for that use. It does not tell you that anybody reads it. The adoption figures from Cloudflare Radar in Chapters 1 and 20 are the better guide to that.

## How to read the status column

The tables use one small vocabulary for status, so you can compare rows quickly:

- **RFC (Standards Track)**: a published IETF standard. Stable, and changes only through a new RFC.
- **RFC (Informational)**: published by the IETF but not a standard. Sunset (RFC 8594) is the example in this book.
- **IETF WG draft**: an Internet-Draft adopted by an IETF working group (the file name starts with `draft-ietf-`). On the way to an RFC, but the details can still change, and it expires six months after its date unless a new revision appears.
- **Individual draft**: an Internet-Draft by one or more authors that no working group has adopted (`draft-<author>-…`). A proposal, nothing more.
- **W3C Recommendation / Working Draft**: the W3C equivalents of "standard" and "work in progress".
- **W3C CG report**: published by a W3C Community Group. Community Groups are open to anyone and their reports are not W3C standards. WebMCP and TDMRep both live here.
- **Dated spec**: a specification that publishes numbered or dated releases outside a standards body (MCP, OpenAPI, A2A, UCP, ACP and others). "Current" means the newest release on the date in the row.
- **Vendor proposal**: published by one company, used by that company's tools, with no independent process behind it yet.

For IANA, "permanent" and "provisional" are the two states of a registration in the Well-Known URIs registry. Provisional entries are first-come, first-served and need only a stable reference.[^appB-1]

## Well-known paths

RFC 8615 reserves the `/.well-known/` prefix so that site-wide metadata has a predictable home.[^appB-2] Table B.1 lists every path under that prefix that appears in this book. "Reads it" names the grader checks and the main clients that fetch the path.

Table B.1 Well-known paths

| Path | Purpose | Specification and status | IANA (registry update of 26 Oct 2026) | Graders that read it | Chapter |
|---|---|---|---|---|---|
| `/.well-known/api-catalog` | A linkset that lists your APIs and their descriptions | RFC 9727, Standards Track, June 2025 | Permanent, registered 23 Dec 2024 | isitagentready `apiCatalog` (Level 4) | 7, 11 |
| `/.well-known/oauth-protected-resource` | Protected Resource Metadata: which authorization servers protect this API or MCP server | RFC 9728, Standards Track, April 2025. Required by the MCP authorization spec | Permanent | isitagentready `oauthProtectedResource` (Level 5) | 14 |
| `/.well-known/oauth-protected-resource/mcp` | The same metadata for a resource at the path `/mcp` (RFC 9728 inserts the resource path after the well-known name) | RFC 9728 | Covered by the entry above | Read by MCP clients | 8, 14 |
| `/.well-known/oauth-authorization-server` | Authorization server metadata: endpoints, supported grants, PKCE methods | RFC 8414, Standards Track, June 2018 | Permanent | isitagentready `oauthDiscovery` (Level 5) | 14 |
| `/.well-known/openid-configuration` | OpenID Connect discovery, the OIDC equivalent of the line above | OpenID Connect Discovery 1.0 | Permanent | isitagentready `oauthDiscovery` | 14 |
| `/.well-known/http-message-signatures-directory` | The public keys a bot or agent signs its requests with | Web Bot Auth, `draft-ietf-webbotauth-httpsig-protocol-01`, IETF WG draft, 29 Oct 2026 | Not registered | isitagentready `webBotAuth` (informational, checked for sites that send requests) | 15 |
| `/.well-known/mcp/server-card.json` | An MCP server card describing a server before connection | SEP-1649 draft, superseded by SEP-2127 | Not registered | isitagentready `mcpServerCard` (Level 4) | 11 |
| `/.well-known/mcp/server-cards.json`, `/.well-known/mcp.json` | Alternative card locations in circulation. isitagentready.com serves `mcp.json` itself | De facto, no specification | Not registered | isitagentready `mcpServerCard` accepts both | 11 |
| `/.well-known/ai-catalog.json` | AI Catalog: one domain-level list of MCP servers, agents and skills. Named in SEP-2127 and in the first ARD announcement | SEP-2127 (status contested, see Table B.9). Lighthouse 13.6.0 flags it as a legacy ARD location | Not registered | isitagentready `ard` (its fix prompt points here), Lighthouse `ard-schema` (warning) | 11 |
| `/.well-known/ard.json` | Agentic Resource Discovery manifest | ARD v0.91, Proposal, 26 Aug 2026 | Not registered | Lighthouse `ard-schema`, isitagentready `ard` | 11 |
| `/.well-known/agent-skills/index.json` | An index of Agent Skills a site publishes for agents | Agent Skills Discovery RFC v0.2.0 (vendor proposal). The legacy `/.well-known/skills/index.json` is still accepted by the scanner | Not registered | isitagentready `agentSkills` (Level 4) | 11 |
| `/.well-known/agent-card.json` | A2A Agent Card: name, version, skills and interfaces of an agent | A2A 1.0 (Agentic AI Foundation) | Permanent, registered 1 Aug 2025 | isitagentready `a2aAgentCard` (opt-in, off by default) | 11, 13 |
| `/.well-known/ucp` | UCP business profile: protocol version, services and capabilities | Universal Commerce Protocol, dated spec | Provisional, registered 26 Oct 2026 | isitagentready `ucp` (commerce, scored only on shops) | 12 |
| `/.well-known/acp.json` | ACP discovery document | Agentic Commerce Protocol. The ACP repository says merchant discovery is not yet defined, so treat this path as the scanner's convention | Not registered | isitagentready `acp` (commerce) | 12 |
| `/.well-known/tdmrep.json` | Text-and-data-mining reservation (EU DSM Directive Article 4 opt-out) | TDMRep, W3C CG Final Report, 10 May 2024 | Provisional | None | 4 |
| `/.well-known/poppy.json` | Personal Agent Protocol | Draft 0.1, single proposal | Not registered | isitagentready `personalAgentProtocol` (informational) | 11 |
| `/.well-known/vacation-rental.json` | Vacation Rental Protocol offers signed by the host domain | VRP v0.1, single-maintainer draft, updated 1 Nov 2026 | Provisional, registered 19 Aug 2026 | None | 12 |

Two paths you may meet in blog posts do not appear in Table B.1 on purpose. `/.well-known/ai.txt` exists only as an individual IETF draft (`draft-car-ai-txt-wellknown-00`, June 2026) that no AI vendor documents reading, and `/.well-known/llms.txt` is not where the llms.txt proposal puts the file (it lives at `/llms.txt` or a subpath, see Table B.2). Chapter 4 discusses the first, Chapter 6 the second.

> **Note:** The MCP server card is the clearest case of churn in this table. On 2 November 2026 three locations were live in the wild, and the SEP-2127 page said "Final" while the extension repository said "Experimental". Nordlys Cabins serves the SEP-2127 location and mirrors the card at the path today's scanner reads. Chapter 11 explains the trade-off.

## Files at fixed paths outside /.well-known

Some of the most important files predate RFC 8615 or chose not to use it. Table B.2 lists them.

Table B.2 Root and fixed-path files

| Path | Purpose | Specification and status | Graders that read it | Chapter |
|---|---|---|---|---|
| `/robots.txt` | Crawl rules per user agent, plus the extension lines in Table B.3 | RFC 9309, Standards Track, September 2022. Rules "are not a form of access authorization" | isitagentready `robotsTxt` (Level 1), `robotsTxtAiRules` and `contentSignals` (Level 2) | 4 |
| `/sitemap.xml` (or any URL named by a `Sitemap:` line) | The list of URLs you want discovered, with `lastmod` | sitemaps.org protocol 0.9. Google caps one file at 50 MB or 50,000 URLs | isitagentready `sitemap` (Level 1) | 6 |
| `/llms.txt` (or a subpath such as `/docs/llms.txt`) | A Markdown index for language models: one H1, an optional summary, lists of links | llms.txt proposal v2 (Jeremy Howard), modified 10 Aug 2026. Not registered anywhere | Lighthouse `llms-txt` (N/A when the file is absent) | 6 |
| `/llms-full.txt` | The whole content as one Markdown file | A widely copied convention. It is not part of the v2 proposal | None | 6 |
| `<page>.md` or `<page>.html.md` | The Markdown twin of an HTML page | llms.txt v2 allows both URL forms | None directly (Markdown negotiation is the graded route) | 6 |
| `/openapi.json` (any path, linked from the API catalog) | Machine-readable description of your HTTP API | OpenAPI 3.2.1 (10 Sep 2026), also 3.1.2 | isitagentready `mpp` reads `x-payment-info` extensions here | 7 |
| `/mcp` (any path) | Streamable HTTP endpoint of an MCP server | MCP 2026-07-28 | Read by MCP hosts, not by the graders | 8 |
| `/mcp/server-card` (relative to the MCP endpoint) | Server card at the location SEP-2127 recommends | SEP-2127 | Not read by isitagentready today | 11 |
| `/auth.md` | Plain-language description of how agents authenticate, paired with an `agent_auth` block in authorization-server metadata | Vendor proposal (WorkOS) | isitagentready `authMd` (one of the Level 5 auth options) | 11, 14 |
| `/feed.xml`, `/atom.xml`, `/feed.json` (any paths) | Content feeds | RSS 2.0.11 (2009), Atom RFC 4287 (2005), JSON Feed 1.1 | None | 6 |

## Lines in robots.txt

RFC 9309 defines only `User-agent`, `Allow` and `Disallow`, and says crawlers should ignore lines they do not understand.[^appB-3] Every agent-era addition in Table B.3 relies on that rule. A crawler that does not know the line simply skips it.

Table B.3 robots.txt lines

| Line | Example | Defined by | Status | Graders | Chapter |
|---|---|---|---|---|---|
| `User-agent`, `Allow`, `Disallow` | `User-agent: GPTBot` then `Disallow: /account/` | RFC 9309 | RFC (Standards Track) | isitagentready `robotsTxt`, `robotsTxtAiRules` (named AI bots, or wildcard rules that apply to all crawlers) | 4 |
| `Sitemap` | `Sitemap: https://nordlys.example/sitemap.xml` | sitemaps.org | Long-standing convention | isitagentready `sitemap` | 6 |
| `Content-Signal` | `Content-Signal: search=yes, ai-input=yes, ai-train=no` | Cloudflare Content Signals Policy, 24 Sep 2025 | Vendor proposal. An absent signal "conveys no meaning". Its IETF individual draft (`draft-romm-aipref-contentsignals-00`) expired in April 2026 | isitagentready `contentSignals` (Level 2) | 4 |
| `Content-Usage` | `Content-Usage: train-ai=n` or path-scoped `Content-Usage: /ai-ok/ train-ai=y` | `draft-ietf-aipref-attach-05` (19 Aug 2026) with the vocabulary in `draft-ietf-aipref-vocab-08` (14 Sep 2026) | IETF WG drafts, both aimed at Proposed Standard | None | 4 |
| `User-Agent: __usage_ai-training` | An ordinary group whose `Disallow` lines express the training preference | `draft-kelley-aipref-training-preference-signal-00` (30 Oct 2026). Google says it intends to support this token in early 2027 | Individual draft | None | 4 |
| `License` | `License: https://nordlys.example/license.xml` | RSL 1.0, published 10 Dec 2025 | Specification of the RSL Collective | None | 4 |
| `Agentmap` | `Agentmap: https://nordlys.example/.well-known/ard.json` | ARD v0.91 | Proposal | Lighthouse `ard-schema` looks here first | 4, 11 |

Be precise about the second row. `Content-Signal` is a robots.txt line in Cloudflare's policy. The IETF drafts in the third row define a separate HTTP header called `Content-Usage` with different labels (`train-ai`, `ai-use`, `search`, each `y` or `n`). Cloudflare's Markdown for Agents also adds a `Content-Signal` response header to the Markdown it generates. That header is Cloudflare's own product behaviour. The policy isitagentready checks is the robots.txt line.[^appB-4]

## HTTP headers

Table B.4 lists the headers in the order a request meets them: what the client sends, what the server answers, and the signatures and payment headers that sit on top. "Dir." says whether the client sends it (Req), the server sends it (Resp) or both.

Table B.4 HTTP headers

| Header | Dir. | What it carries in this book | Specification and status | Chapter |
|---|---|---|---|---|
| `Accept: text/markdown` | Req | The agent asks for the Markdown version of a page | `text/markdown` is RFC 7763. The negotiation is ordinary HTTP (RFC 9110) | 6 |
| `Content-Type: text/markdown` | Resp | The server answers with Markdown. isitagentready `markdownNegotiation` passes when the homepage does this for `Accept: text/markdown` | RFC 7763, RFC 9110 | 6 |
| `Vary: Accept` | Resp | Tells caches that the response depends on `Accept`, so HTML and Markdown are never mixed up | RFC 9110 | 6 |
| `Link` | Resp | Points to related resources: API catalog, sitemap, Markdown alternate, llms.txt, ARD manifest (see Table B.5). isitagentready `linkHeaders` (Level 1) reads it on the homepage | RFC 8288, Standards Track | 6, 11 |
| `X-Robots-Tag` | Resp | Indexing directives for non-HTML files, such as `noindex` on generated Markdown | Google and other search engines' documentation, no RFC | 4, 6 |
| `Content-Usage` | Resp | aipref usage preferences for this response | `draft-ietf-aipref-attach-05`, IETF WG draft | 4 |
| `Content-Signal` | Resp | Cloudflare Markdown for Agents adds `ai-train=yes, search=yes, ai-input=yes` unless the origin sends its own | Cloudflare product behaviour | 4, 6 |
| `User-Agent` | Req | The name a crawler or agent claims. A claim, not proof | RFC 9110 | 4, 15, 19 |
| `Signature-Input` | Req | Which components a request signature covers, with `keyid`, `created`, `expires` and the `tag` value `web-bot-auth` that Web Bot Auth requires | RFC 9421 (February 2024) plus the Web Bot Auth draft | 15 |
| `Signature` | Req | The signature itself | RFC 9421 | 15 |
| `Signature-Agent` | Req | Where to fetch the signer's key directory (for example `https://chatgpt.com`) | Web Bot Auth, `draft-ietf-webbotauth-httpsig-protocol-01` | 15, 19 |
| `Authorization: Bearer …` | Req | An OAuth access token on API and MCP calls | RFC 6750 | 14 |
| `WWW-Authenticate: Bearer resource_metadata="…", scope="…"` | Resp | A 401 that tells an MCP client where the Protected Resource Metadata lives and which scope it needs | RFC 6750 with the `resource_metadata` parameter of RFC 9728 | 14 |
| `DPoP` | Req | A proof that the client holds the key a token is bound to | RFC 9449. Listed on the MCP roadmap's Agent Identity work, not required by MCP 2026-07-28 | 14 |
| `Mcp-Method`, `Mcp-Name` | Req | The JSON-RPC method and the tool, resource or prompt name, copied into headers so gateways and logs can route and filter without parsing the body | MCP 2026-07-28 | 8, 16, 19 |
| `Mcp-Session-Id` | Both | Session id of the 2025 MCP transport | Removed in MCP 2026-07-28 (SEP-2567). Legacy | 8 |
| `Idempotency-Key` | Req | A client-chosen key that makes a retried POST safe, so an agent retrying a booking does not book twice | `draft-ietf-httpapi-idempotency-key-header-08` (22 Oct 2026), IETF WG draft | 7, 10 |
| `RateLimit-Policy`, `RateLimit` | Resp | The quota policy and the remaining quota as structured fields | `draft-ietf-httpapi-ratelimit-headers-11` (May 2026), IETF WG draft | 7, 15 |
| `Retry-After` | Resp | How long to wait after a 429 or 503 | RFC 9110 | 7, 15 |
| `Content-Type: application/problem+json` | Resp | Machine-readable error body with `type`, `title`, `status` and `detail` | RFC 9457 (obsoletes RFC 7807) | 7, 10 |
| `Deprecation` | Resp | When an endpoint or tool was or will be deprecated, as a Structured Field Date (`Deprecation: @1688169599`) | RFC 9745, Standards Track, March 2025 | 7, 8, 20 |
| `Sunset` | Resp | When the resource will stop responding, as an HTTP-date | RFC 8594, Informational, May 2019 | 7, 20 |
| `ETag`, `If-Match` | Both | Detects stale state, so an agent cannot overwrite a booking someone else changed | RFC 9110 | 10 |
| `PAYMENT-REQUIRED`, `PAYMENT-SIGNATURE`, `PAYMENT-RESPONSE` | Resp, Req, Resp | x402 V2 payment requirement, payment and settlement, each base64-encoded JSON | x402 V2 (x402 Foundation, Linux Foundation) | 12, 15 |
| `crawler-price`, `crawler-exact-price`, `crawler-max-price`, `crawler-charged` | Both | Cloudflare pay per crawl price quote, offer and charge | Cloudflare product, closed beta | 15 |

> **Tip:** When you test any row of Table B.4, use `curl -sI` for response headers and add `-H 'Accept: text/markdown'` for the negotiation rows. The three graders in this book all start from the same raw responses, so if `curl` does not show the header, no grader will either.

## Link relations

The `Link` header (and the HTML `link` element) carries a relation type. Only registered relation types are safe to rely on, but agents read a few that are not registered yet.[^appB-5]

Table B.5 Link relations

| Relation | Points to | Registered with IANA (2 Nov 2026) | Used by | Chapter |
|---|---|---|---|---|
| `api-catalog` | `/.well-known/api-catalog` | Yes, RFC 9727 | isitagentready `linkHeaders` | 6, 7, 11 |
| `service-desc` | A machine-readable API description such as `openapi.json` | Yes, RFC 8631 (Informational, July 2019) | isitagentready `linkHeaders`, API tooling | 6, 7 |
| `service-doc` | Human-readable API documentation | Yes, RFC 8631 | API tooling | 7 |
| `describedby` | A resource that describes this one. llms.txt v2 uses it for the covering llms.txt | Yes | isitagentready `linkHeaders`, llms.txt readers | 6 |
| `alternate` with `type="text/markdown"` | The Markdown twin of the page | Yes (`alternate`) | isitagentready `linkHeaders`, llms.txt v2 | 6 |
| `sitemap` | The sitemap | No, though Cloudflare's own responses send it | isitagentready `linkHeaders` | 6 |
| `ard` | The ARD manifest | No | Lighthouse `ard-schema` (as a `link` element or a `Link` header) | 11 |
| `deprecation`, `sunset` | A human-readable deprecation or sunset policy | Yes, RFC 9745 and RFC 8594 | API clients | 20 |

## Markup hooks in HTML

These are attributes and elements in the page itself. They matter to browser agents and to the Lighthouse category, not to the server-side scanner (with one exception, the declarative WebMCP form, which isitagentready also detects).

Table B.6 Markup hooks

| Hook | Purpose | Specification and status | Graders | Chapter |
|---|---|---|---|---|
| Semantic elements, accessible names, `label` | The accessibility tree that browser agents read | HTML Living Standard, WAI-ARIA 1.2 (W3C Recommendation, 6 June 2023). ARIA 1.3 is a Working Draft (4 June 2026) | Lighthouse `agent-accessibility-tree` (33 axe rules) | 2, 3 |
| `script type="application/ld+json"` | schema.org structured data as JSON-LD | schema.org vocabulary, JSON-LD 1.1 (W3C Recommendation) | None in either grader. Google's rich results test reads it | 5 |
| `link rel="alternate" type="text/markdown"` | Markdown twin, as in Table B.5 | llms.txt v2 | isitagentready `linkHeaders` reads only headers | 6 |
| `form` with `toolname` and `tooldescription` | A declarative WebMCP tool | Chrome documentation. Not in the WebMCP specification text as of 2 Nov 2026 | Lighthouse `webmcp-form-coverage`, `webmcp-schema-validity`, `webmcp-registered-tools`. isitagentready `webMcp` | 9 |
| `toolparamdescription` on a form field | Describes one parameter of a declarative tool | Chrome documentation | Lighthouse `webmcp-schema-validity` (warning when an optional named field has neither this nor a `label`) | 9 |
| `document.modelContext.registerTool()` | An imperative WebMCP tool registered from JavaScript | WebMCP, W3C Web Machine Learning CG draft dated 2 Nov 2026. The older `navigator.modelContext` is still detected | Lighthouse `webmcp-registered-tools` (warns above 40 tools), isitagentready `webMcp` | 9 |
| `link rel="ard"` | ARD manifest | ARD v0.91 | Lighthouse `ard-schema` | 11 |

## DNS records

One check in the book lives outside HTTP entirely.

Table B.7 DNS records

| Record | Purpose | Specification and status | Graders | Chapter |
|---|---|---|---|---|
| SVCB or HTTPS records under `_agents`, for example `_index._agents.example.com` | Agent discovery through DNS, validated with DNSSEC | DNS-AID, `draft-mozleywilliams-dnsop-dnsaid-02` (27 May 2026, expires 28 Nov 2026), individual draft | isitagentready `dnsAid` (Discoverability category, not required for any level) | 11 |

## Grader check index

Tables B.8 and B.9 work in the other direction. Start from a check id in a report and find what it reads and where the book teaches it.

Table B.8 isitagentready.com checks (as published on 2 November 2026)

| Category | Check id | What passes | Level it counts toward | Chapter |
|---|---|---|---|---|
| Discoverability | `robotsTxt` | `/robots.txt` returns 200 as `text/plain` with at least one `User-agent` | L1 (2 of 3) | 4 |
| Discoverability | `sitemap` | Valid `/sitemap.xml`, or a `Sitemap` line in robots.txt | L1 (2 of 3) | 6 |
| Discoverability | `linkHeaders` | Homepage sends `Link` headers with agent-useful relations | L1 (2 of 3) | 6 |
| Discoverability | `dnsAid` | DNSSEC-validated SVCB/HTTPS records under `_agents` | None | 11 |
| Content accessibility | `markdownNegotiation` | `Accept: text/markdown` on the homepage returns `Content-Type: text/markdown` | L3 | 6 |
| Bot access control | `robotsTxtAiRules` | Named AI bots, or wildcard rules that apply to all crawlers | L2 | 4 |
| Bot access control | `contentSignals` | A `Content-Signal` line with `ai-train`, `search` or `ai-input` | L2 | 4 |
| Bot access control | `webBotAuth` | A valid key directory at `/.well-known/http-message-signatures-directory` (informational, a fail shows as neutral) | L5 (one of 2 of 3) | 15 |
| Discovery | `mcpServerCard` | Server card at one of the paths in Table B.1 with a name | L4 (1 of 4) | 11 |
| Discovery | `a2aAgentCard` | Agent card with `name`, `version` and `supportedInterfaces` (opt-in) | L4 (1 of 4) | 11 |
| Discovery | `agentSkills` | `/.well-known/agent-skills/index.json` | L4 (1 of 4) | 11 |
| Discovery | `apiCatalog` | `/.well-known/api-catalog` as a linkset | L4 (1 of 4) | 7, 11 |
| Discovery | `webMcp` | The page registers tools imperatively or declares a tool form | None. WebMCP does not affect the level | 9 |
| Discovery | `oauthDiscovery` | Authorization-server or OpenID metadata | L5 (auth option) | 14 |
| Discovery | `oauthProtectedResource` | Protected Resource Metadata with `resource` and `authorization_servers` | L5 (auth option) | 14 |
| Discovery | `authMd` | `/auth.md` with PRM and an `agent_auth` block | L5 (auth option) | 11, 14 |
| Discovery | `ard` | An ARD manifest through one of four mechanisms | None | 11 |
| Discovery | `personalAgentProtocol` | `/.well-known/poppy.json` (informational) | None | 11 |
| Commerce | `x402` | Routes return 402 with x402 payment headers | Not scored (shops only) | 12 |
| Commerce | `mpp` | `/openapi.json` with `x-payment-info` extensions | Not scored | 12 |
| Commerce | `ucp` | `/.well-known/ucp` with `protocol_version` and `services` | Not scored | 12 |
| Commerce | `acp` | `/.well-known/acp.json` with the required fields | Not scored | 12 |
| Commerce | `ap2` | AP2 extension in the A2A Agent Card (opt-in) | Not scored | 12 |

The level rules, quoted from the scanner's own documentation: Level 1 needs two of robots.txt, sitemap and Link headers. Level 2 adds both AI bot rules and Content Signals. Level 3 adds Markdown negotiation. Level 4 adds one of the four integration checks (MCP Server Card, A2A Agent Card, Agent Skills, API Catalog). Level 5 adds two of three: Web Bot Auth, all four integration checks, or auth metadata.[^appB-6]

Table B.9 Lighthouse Agentic Browsing audits (Lighthouse 13.6.0, 27 October 2026)

| Audit id | Group | Scoring | Reads | Chapter |
|---|---|---|---|---|
| `agent-accessibility-tree` | Agent Accessibility | Binary. Fails if any of 33 axe rules fails (link names, button names, labels, ARIA validity and so on) | The DOM and accessibility tree | 3 |
| `cumulative-layout-shift` | (stability) | The standard CLS metric | Layout shifts during load | 3 |
| `webmcp-form-coverage` | WebMCP | Informative. Lists forms without both `toolname` and `tooldescription` | Forms | 9 |
| `webmcp-registered-tools` | WebMCP | Informative. Lists tools, warns above 40 | WebMCP registrations through the CDP `WebMCP` domain | 9 |
| `webmcp-schema-validity` | WebMCP | 0 on errors, 0.5 on warnings only, 1 when clean | Declarative tool attributes and field names | 9 |
| `llms-txt` | Agent Discoverability | N/A on 4xx except 429. Fails without an H1, without a Markdown link or under 50 characters | `/llms.txt` | 6 |
| `ard-schema` | Agent Discoverability | Validates the ARD manifest, warns on legacy `ai-catalog` locations, N/A when absent | `Agentmap`, `link rel="ard"`, `Link` header, `/.well-known/ard.json` (in that order) | 11 |

The category has no 0–100 score. Lighthouse shows the share of scored audits that pass, and the JSON report holds the mean of the scored, non-N/A audits. It needs Chrome 150 or later, and the WebMCP audits need the WebMCP origin trial or the `WebMCPTesting` feature flag.[^appB-7]

## Standards and specifications

Table B.10 is the master list. "Body" is who publishes it. "Version or draft" and "Date" are the newest I could read on 2 November 2026.

Table B.10 Standards and specifications

| Standard | Body | Version or draft | Date | Status | Chapter |
|---|---|---|---|---|---|
| Robots Exclusion Protocol | IETF | RFC 9309 | Sep 2022 | RFC (Standards Track) | 4 |
| Well-Known URIs | IETF | RFC 8615 | May 2019 | RFC (Standards Track) | 11 |
| Web Linking | IETF | RFC 8288 | Oct 2017 | RFC (Standards Track) | 6, 11 |
| HTTP Semantics | IETF | RFC 9110 | Jun 2022 | RFC (Standards Track) | 6, 7 |
| `text/markdown` media type | IETF | RFC 7763 | Mar 2016 | RFC (Informational) | 6 |
| api-catalog | IETF | RFC 9727 | Jun 2025 | RFC (Standards Track) | 7, 11 |
| Problem Details for HTTP APIs | IETF | RFC 9457 | Aug 2023 | RFC (Standards Track) | 7 |
| Idempotency-Key header | IETF httpapi WG | draft-08 | 22 Oct 2026 | IETF WG draft | 7, 10 |
| RateLimit header fields | IETF httpapi WG | draft-11 | May 2026 | IETF WG draft (expires 24 Nov 2026) | 7, 15 |
| Deprecation header | IETF | RFC 9745 | Mar 2025 | RFC (Standards Track) | 20 |
| Sunset header | IETF | RFC 8594 | May 2019 | RFC (Informational) | 20 |
| OAuth 2.1 | IETF OAuth WG | draft-ietf-oauth-v2-1-17 (MCP 2026-07-28 cites draft-13) | 31 Oct 2026 | IETF WG draft | 14 |
| Bearer Token Usage | IETF | RFC 6750 | Oct 2012 | RFC (Standards Track) | 14 |
| Authorization Server Metadata | IETF | RFC 8414 | Jun 2018 | RFC (Standards Track) | 14 |
| Resource Indicators | IETF | RFC 8707 | Feb 2020 | RFC (Standards Track) | 14 |
| Protected Resource Metadata | IETF | RFC 9728 | Apr 2025 | RFC (Standards Track) | 14 |
| Dynamic Client Registration | IETF | RFC 7591 | Jul 2015 | RFC, deprecated for MCP clients in MCP 2026-07-28 | 14 |
| Client ID Metadata Document (CIMD) | IETF OAuth WG | draft-ietf-oauth-client-id-metadata-document-02 | 6 Jul 2026 | IETF WG draft | 14 |
| Identity Assertion Authorization Grant (ID-JAG) | IETF OAuth WG | draft-ietf-oauth-identity-assertion-authz-grant-06 | 31 Oct 2026 | IETF WG draft | 14 |
| Token Exchange | IETF | RFC 8693 | Jan 2020 | RFC (Standards Track) | 14 |
| DPoP | IETF | RFC 9449 | Sep 2023 | RFC (Standards Track) | 14 |
| HTTP Message Signatures | IETF | RFC 9421 | Feb 2024 | RFC (Standards Track) | 15 |
| Web Bot Auth | IETF webbotauth WG | draft-ietf-webbotauth-httpsig-protocol-01 | 29 Oct 2026 | IETF WG draft (replaces two individual drafts of March 2026) | 15 |
| AI Preferences vocabulary | IETF aipref WG | draft-ietf-aipref-vocab-08 | 14 Sep 2026 | IETF WG draft. The draft itself says it does not reflect WG consensus | 4 |
| AI Preferences attachment | IETF aipref WG | draft-ietf-aipref-attach-05 | 19 Aug 2026 | IETF WG draft | 4 |
| Training preference signal | IETF (individual) | draft-kelley-aipref-training-preference-signal-00 | 30 Oct 2026 | Individual draft | 4 |
| DNS-AID | IETF (individual) | draft-mozleywilliams-dnsop-dnsaid-02 | 27 May 2026 | Individual draft | 11 |
| Content Signals Policy | Cloudflare | First version (IETF individual draft `draft-romm-aipref-contentsignals-00` expired 4 Apr 2026) | 24 Sep 2025 | Vendor proposal | 4 |
| TDM Reservation Protocol (TDMRep) | W3C CG | Final CG Report | 10 May 2024 | W3C CG report | 4 |
| RSL (Really Simple Licensing) | RSL Collective | 1.0 | 10 Dec 2025 | Published specification | 4, 15 |
| Sitemaps | sitemaps.org | 0.9 | (long-standing) | Convention backed by the major search engines | 6 |
| llms.txt | Individual (Jeremy Howard) | v2 | 10 Aug 2026 (v1: 3 Sep 2024) | Proposal | 6 |
| schema.org | schema.org community | Current release on schema.org | (continuous) | Community vocabulary | 5 |
| JSON-LD | W3C | 1.1 | Jul 2020 | W3C Recommendation | 5 |
| WAI-ARIA | W3C | 1.2 (1.3 in progress) | 6 Jun 2023 (1.3 WD: 4 Jun 2026) | W3C Recommendation (1.3: Working Draft) | 3 |
| OpenAPI | OpenAPI Initiative | 3.2.1 (3.2.0: 19 Sep 2025) | 10 Sep 2026 | Dated spec | 7 |
| Arazzo | OpenAPI Initiative | 1.1.0 | 17 May 2026 | Dated spec | 7 |
| Model Context Protocol | Agentic AI Foundation (Linux Foundation) | 2026-07-28 (previous: 2025-11-25) | 28 Jul 2026 | Dated spec | 8 |
| MCP Server Cards | MCP project | SEP-2127 (earlier SEP-1649) | 2026 | Contested: "Final" on the SEP page, "Experimental" in the extension repository | 11 |
| WebMCP | W3C Web Machine Learning CG | Draft dated 2 Nov 2026 (adds `outputSchema`) | 2 Nov 2026 | W3C CG draft. Chrome origin trial. WebKit opposes, Mozilla neutral | 9 |
| Agentic Resource Discovery (ARD) | Authors from Google and Hugging Face | v0.91 | 26 Aug 2026 | Proposal | 11 |
| Agent Skills Discovery | Vendor proposal | v0.2.0 | 2026 | Vendor proposal | 11 |
| A2A (Agent2Agent) | Agentic AI Foundation | 1.0.1 (1.0.0: 12 Mar 2026) | 26 May 2026 | Dated spec | 11, 13 |
| NLWeb | Open source project (started at Microsoft) | No tagged releases | Last push 11 Aug 2026 | Open source project | 5, 13 |
| Universal Commerce Protocol (UCP) | Google, Shopify and co-developers | Dated releases. Lodging capability `dev.ucp.lodging.booking` in draft | Lodging draft 25 Sep 2026 | Dated spec (Lodging: draft) | 12 |
| Agentic Commerce Protocol (ACP) | OpenAI and Stripe | 2026-04-17 | 17 Apr 2026 | Beta | 12 |
| AP2 (Agent Payments Protocol) | Donated to the FIDO Alliance | v0.2 | 2026 | Extension of A2A and UCP | 12 |
| x402 | x402 Foundation (Linux Foundation) | V2 | Foundation since 2 Apr 2026 | Dated spec | 12, 15 |
| MPP (Machine Payments Protocol) | Stripe and Tempo | Launched 18 Mar 2026 | 18 Mar 2026 | Vendor-led open protocol | 12 |
| Visa Trusted Agent Protocol | Visa | Developer documentation | 2026 | Vendor programme built on RFC 9421 | 12, 15 |
| OWASP Top 10 for LLM Applications | OWASP | 2025 | 2025 | Community guidance | 16 |
| OWASP Top 10 for Agentic Applications | OWASP GenAI Security Project | 2026 (ASI01–ASI10) | 9 Dec 2025 | Community guidance | 16 |

> **Warning:** Do not copy a draft number from Table B.10 into code comments as if it were a version that will stay valid. Write the date you implemented against and the draft you read, for example "Web Bot Auth, draft-ietf-webbotauth-httpsig-protocol-01, checked 2 Nov 2026". Chapter 20 turns that habit into a watch list.

## What Nordlys Cabins serves

Finally, the short version for the running example. With every layer switched on, Nordlys Cabins serves robots.txt with named groups for AI crawlers and user-triggered fetchers, with a `Content-Signal` line in each group. It also serves a sitemap, llms.txt, Markdown versions of its pages through `Accept: text/markdown` with `Vary: Accept`, and `Link` headers on the homepage with the `api-catalog`, `alternate`, `describedby` and `ard` relations. Its API under `/api/v1` has an OpenAPI description, `RateLimit-Policy` and `RateLimit` headers and problem details for errors. Its MCP endpoint answers `tools/list` for public tools, with Protected Resource Metadata and authorization-server metadata for the member tools. It publishes a server card at the SEP-2127 location and at the path today's scanner reads, an Agent Skills index, an ARD manifest and a UCP profile.

It deliberately skips the rest. There is no signature directory (Nordlys sends no bot traffic of its own), no A2A card (it runs no agent), no ACP document (UCP is the commerce profile it chose), no x402 routes (it sells stays, not requests), no `llms-full.txt` and no file at the legacy `ai-catalog.json` location. Each "no" is explained in the chapter named in the tables, and your team can make each one the same way.

> **Hands-on:** The demos repository has a small script that requests every path, robots.txt line and header from these tables and prints which ones a site serves: `node chapters/appendix-b-reference/check-reference.mjs http://127.0.0.1:3000` against a local Nordlys, or any public origin of your own. Its test (`npm test -w chapters/appendix-b-reference`) starts Nordlys with every layer and checks the two paragraphs above. A "yes" from the script means the file or header exists. It does not mean the content is right, and that is what the graders and Chapters 4 to 15 are for.

[^appB-1]: IANA, "Well-Known URIs" registry, last updated 26 October 2026, https://www.iana.org/assignments/well-known-uris/well-known-uris.xhtml (retrieved November 2026). Registration states and dates in Table B.1 come from this registry.
[^appB-2]: M. Nottingham, "Well-Known Uniform Resource Identifiers (URIs)", RFC 8615, https://www.rfc-editor.org/rfc/rfc8615.html (retrieved November 2026).
[^appB-3]: M. Koster, G. Illyes, H. Zeller, L. Sassman, "Robots Exclusion Protocol", RFC 9309, https://www.rfc-editor.org/rfc/rfc9309.html (retrieved November 2026).
[^appB-4]: Cloudflare, "Content Signals Policy", https://blog.cloudflare.com/content-signals-policy/, and "Markdown for Agents", https://developers.cloudflare.com/fundamentals/reference/markdown-for-agents/. IETF, draft-ietf-aipref-attach-05, https://www.ietf.org/archive/id/draft-ietf-aipref-attach-05.txt, and draft-ietf-aipref-vocab-08, https://www.ietf.org/archive/id/draft-ietf-aipref-vocab-08.txt (all retrieved November 2026).
[^appB-5]: IANA, "Link Relations" registry, https://www.iana.org/assignments/link-relations/link-relations.xhtml (retrieved November 2026).
[^appB-6]: Cloudflare, isitagentready.com documentation for agents, https://isitagentready.com/llms-full.txt, and the blog post "Introducing the Agent Readiness score", https://blog.cloudflare.com/agent-readiness/ (both retrieved November 2026).
[^appB-7]: Chrome for Developers, "Agentic browsing scoring", https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring, and the Lighthouse v13.6.0 release notes and source, https://github.com/GoogleChrome/lighthouse/releases/tag/v13.6.0 (both retrieved November 2026).
