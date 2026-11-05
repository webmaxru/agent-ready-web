# Appendix B: Files, headers and standards at a glance

This appendix lists the fixed paths, robots.txt lines, HTTP headers, link relations and grader checks the chapters use, with the status of each on 2 November 2026 and the chapter that teaches it. Appendix D has the places to check what changed since.

A well-known path being registered with IANA tells you the name is reserved for that use. It doesn't tell you that anybody reads it.[^appB-1] The Cloudflare Radar adoption figures in Chapter 1 are the better guide to that.

## Reading a status line

Every specification tells you how settled it is, usually in one line under its title. Learning to read that line takes five minutes and saves weeks. Table B.1 lists the status lines you meet in this book.

Table B.1 Status lines and what they mean for shipping

| What the document says | What it means | Can you ship on it? |
| --- | --- | --- |
| W3C "Draft Community Group Report" | A proposal incubated by a Community Group, with no formal W3C review | Yes, behind feature detection, expecting changes |
| W3C "Working Draft", "Candidate Recommendation" | On the standards track of a Working Group | Yes, with care |
| W3C "Recommendation" | A finished W3C standard | Yes |
| IETF individual Internet-Draft (`draft-name-...`) | One author's or company's proposal, not adopted by any group | Prototype, watch |
| IETF Working Group Internet-Draft (`draft-ietf-wg-...`) | Adopted by a working group, still changing | Yes, if you can update when it changes |
| IETF RFC, Standards Track or Informational | Published and stable, never edited (only replaced) | Yes |
| MCP revision marked "Current" (a date such as `2026-07-28`) | The revision clients and servers should implement now | Yes |
| MCP revision marked "Draft" | The next revision in progress | Prototype |
| Vendor or single-author proposal (llms.txt, Content Signals) | A convention with no standards body behind it | Yes, if it is cheap and harmless |

Two lines in that table are misread all the time. A W3C Community Group report is not a W3C standard, and the document says so itself. The WebMCP report reads: "It is not a W3C Standard nor is it on the W3C Standards Track."[^appB-2] And an Internet-Draft is a work in progress, whatever its number. It expires about six months after it is posted unless a new revision replaces it (the Web Bot Auth draft posted on 29 October 2026 expires on 2 May 2027).[^appB-3] A `-08` is not "almost done". It means the authors revised it eight times.

Browsers add a second, independent status line. A feature in Chrome usually goes from a flag to an origin trial to shipped, and the other engines publish their positions in their standards-positions repositories. On 2 November 2026 WebMCP was in an origin trial in Chrome, while WebKit's position was "oppose" and Mozilla's "neutral".[^appB-4] So "WebMCP works" means "works in Chrome, for sites in the trial, and for developers with the flag". Write the status line next to every spec claim in your own documentation, so a reader a year later knows what to recheck.

## Paths

RFC 8615 reserves the `/.well-known/` prefix so that site-wide metadata has a predictable home.[^appB-5] Table B.2 lists the paths the book uses, under that prefix and outside it. "IANA" is the state in the Well-Known URIs registry (update of 26 October 2026).

Table B.2 Paths

| Path | Purpose | Specification, status, IANA | Ch. |
|---|---|---|---|
| `/robots.txt` | Crawl rules per user agent | RFC 9309, Standards Track. Rules "are not a form of access authorization" | 4 |
| `/sitemap.xml` | The URLs you want discovered, with `lastmod` | sitemaps.org 0.9. Google caps a file at 50 MB or 50,000 URLs | 5 |
| `/llms.txt` | A Markdown index for language models | llms.txt proposal v2, 10 Aug 2026. Not registered | 5 |
| `/.well-known/api-catalog` | A linkset of your APIs and their descriptions | RFC 9727. Permanent | 8 |
| `/openapi.json` (any path) | Machine-readable API description | OpenAPI 3.2.1, 10 Sep 2026 | 8 |
| `/mcp` (any path) | Streamable HTTP endpoint of an MCP server | MCP 2026-07-28 | 8 |
| `/.well-known/mcp/server-card.json` | MCP server card, the path today's scanner reads | SEP-1649, superseded by SEP-2127, which puts the card at `<endpoint>/server-card`. Not registered | 8 |
| `/.well-known/ard.json` | Agentic Resource Discovery manifest | ARD v0.91, Proposal, 26 Aug 2026. Not registered | 8 |
| `/.well-known/ai-catalog.json` | AI Catalog, named in SEP-2127 | Status contested. Lighthouse 13.6.0 flags it as a legacy ARD location | 8 |
| `/.well-known/agent-skills/index.json` | An index of Agent Skills | Agent Skills Discovery RFC v0.2.0, vendor proposal. Not registered | 8 |
| `/.well-known/agent-card.json` | A2A Agent Card | A2A 1.0. Permanent, registered 1 Aug 2025 | 6 |
| `/auth.md` | How agents authenticate, in plain language | Vendor proposal (WorkOS) | 8, 11 |
| `/.well-known/oauth-protected-resource` | Which authorization servers protect this API or MCP server | RFC 9728, required by MCP authorization. Permanent | 11 |
| `/.well-known/oauth-authorization-server`, `/.well-known/openid-configuration` | Authorization-server metadata | RFC 8414, OpenID Connect Discovery 1.0. Permanent | 11 |
| `/.well-known/http-message-signatures-directory` | The public keys a bot signs its requests with | Web Bot Auth, `draft-ietf-webbotauth-httpsig-protocol-01`, IETF WG draft. Not registered | 4 |
| `/.well-known/ucp` | UCP business profile | Universal Commerce Protocol, dated spec. Provisional, 26 Oct 2026 | 11 |
| `/.well-known/acp.json` | ACP discovery document | The scanner's convention. ACP says merchant discovery is not yet defined | 11 |

`/llms-full.txt` is a convention outside the llms.txt v2 proposal. TDMRep's `/.well-known/tdmrep.json` is in Appendix C.

## Lines in robots.txt and HTTP headers

RFC 9309 defines only `User-agent`, `Allow` and `Disallow`, and says crawlers should ignore lines they don't understand.[^appB-6] Every agent-era addition relies on that rule. `Sitemap` is a long-standing convention. `Content-Signal` (for example `search=yes, ai-input=yes, ai-train=no`) is Cloudflare's Content Signals Policy of 24 September 2025, and an absent signal "conveys no meaning". `Content-Usage` comes from the IETF aipref drafts (`draft-ietf-aipref-attach-05` with the vocabulary in `draft-ietf-aipref-vocab-08`). An ordinary group for `User-Agent: __usage_ai-training` is an individual draft of 30 October 2026, which Google says it intends to support in early 2027. All of these are taught in Chapter 4. The RSL `License:` line belongs to Appendix C.[^appB-7]

Table B.3 HTTP headers ("Req" the client sends, "Resp" the server sends)

| Header | Dir. | What it carries | Specification and status | Ch. |
|---|---|---|---|---|
| `Accept: text/markdown`, `Vary: Accept` | Req, Resp | Markdown negotiation, kept apart in caches | RFC 7763, RFC 9110 | 5 |
| `Link` | Resp | Related resources (Table B.4) | RFC 8288 | 5, 8 |
| `X-Robots-Tag` | Resp | Indexing directives for non-HTML files | Search engines' documentation, no RFC | 4 |
| `Content-Signal`, `Content-Usage` | Resp | AI usage preferences for this response | Vendor proposal, IETF WG draft | 4 |
| `User-Agent` | Req | The name a crawler claims. A claim, not proof | RFC 9110 | 4 |
| `Signature-Input`, `Signature`, `Signature-Agent` | Req | A signed request and where the signer's keys live. Web Bot Auth requires the tag `web-bot-auth` | RFC 9421, Web Bot Auth draft-01 | 4 |
| `Authorization: Bearer`, `WWW-Authenticate` | Req, Resp | An OAuth token, and a 401 that points to the Protected Resource Metadata | RFC 6750, RFC 9728 | 11 |
| `Mcp-Method`, `Mcp-Name` | Req | The JSON-RPC method and tool name, for gateways and logs | MCP 2026-07-28 | 8, 12 |
| `Mcp-Session-Id` | Both | Session id of the 2025 transport | Removed in MCP 2026-07-28 (SEP-2567) | 8 |
| `Idempotency-Key` | Req | Makes a retried POST safe | `draft-ietf-httpapi-idempotency-key-header-08`, 22 Oct 2026 | 7, 8 |
| `RateLimit-Policy`, `RateLimit`, `Retry-After` | Resp | Quota policy, remaining quota, how long to wait | `draft-ietf-httpapi-ratelimit-headers-11` (expires 24 Nov 2026), RFC 9110 | 8 |
| `Content-Type: application/problem+json` | Resp | Machine-readable errors | RFC 9457 | 7, 8 |
| `Deprecation`, `Sunset` | Resp | When an endpoint or tool was deprecated, and when it stops responding | RFC 9745 (Structured Field Date), RFC 8594 (Informational, HTTP-date) | 8 |

The payment headers of x402 and pay per crawl are in Appendix C.

Every tool, API and discovery file you publish is an interface somebody depends on. Announce a removal with `Deprecation` and `Sunset`, and record which draft of each standard you implemented, and when.[^appB-8]

Table B.4 Link relations

| Relation | Points to | Registered with IANA | Ch. |
|---|---|---|---|
| `api-catalog` | `/.well-known/api-catalog` | Yes, RFC 9727 | 8 |
| `service-desc`, `service-doc` | API description, API documentation | Yes, RFC 8631 | 8 |
| `describedby` | A describing resource, such as the covering llms.txt | Yes | 5 |
| `alternate` with `type="text/markdown"` | The Markdown twin of the page | Yes | 5 |
| `sitemap` | The sitemap | No, though Cloudflare's responses send it | 5 |
| `ard` | The ARD manifest | No | 8 |
| `deprecation`, `sunset` | A deprecation or sunset policy | Yes | 8 |

## Grader check index

Start from a check id in a report and find what it reads and where the book teaches it.[^appB-9]

Table B.5 isitagentready.com checks (2 November 2026)

| Check id | What passes | Level | Ch. |
|---|---|---|---|
| `robotsTxt`, `sitemap`, `linkHeaders` | robots.txt with a `User-agent`, a valid sitemap, agent-useful `Link` headers on the homepage | L1 (2 of 3) | 4, 5 |
| `robotsTxtAiRules`, `contentSignals` | Named AI bots or wildcard rules, and a `Content-Signal` line | L2 (both) | 4 |
| `markdownNegotiation` | `Accept: text/markdown` on the homepage returns Markdown | L3 | 5 |
| `mcpServerCard`, `agentSkills`, `apiCatalog`, `a2aAgentCard` | A server card, a skills index, an API catalog, or an agent card (opt-in) | L4 (1 of 4) | 6, 8 |
| `oauthDiscovery`, `oauthProtectedResource`, `authMd`, `webBotAuth` | Authorization metadata, `/auth.md`, or a key directory (informational) | L5 | 4, 8, 11 |
| `webMcp`, `ard`, `dnsAid` | Tools on the page, an ARD manifest, DNS records under `_agents` | None | 8, 9 |
| `ucp`, `acp`, `x402`, `mpp`, `ap2` | Commerce documents and payment routes | Not scored (shops only) | 11, App. C |

Table B.6 Lighthouse 13.6.0 Agentic Browsing audits (27 October 2026)

| Audit id | Scoring | Ch. |
|---|---|---|
| `agent-accessibility-tree` | Binary. Fails if any of 33 axe rules fails | 3 |
| `cumulative-layout-shift` | The standard CLS metric | 3 |
| `webmcp-form-coverage` | Informative. Lists forms without `toolname` and `tooldescription` | 9 |
| `webmcp-registered-tools` | Informative. Lists tools, warns above 40 | 9 |
| `webmcp-schema-validity` | 0 on errors, 0.5 on warnings only, 1 when clean | 9 |
| `llms-txt` | N/A when absent. Fails without an H1, a Markdown link or 50 characters | 5 |
| `ard-schema` | Validates the ARD manifest, warns on legacy `ai-catalog` locations, N/A when absent | 8 |

The category has no 0 to 100 score. It needs Chrome 150 or later, and the WebMCP audits need the origin trial or the testing flag.[^appB-10]

## Agent commerce protocols

Table B.7 lines up the commerce protocols that Chapter 11 discusses. Almost everything here is a draft, a beta or a version 0.x. The Radar column counts domains among the 115,468 that Cloudflare Radar scanned.[^appB-11]

Table B.7 Agent commerce protocols in November 2026

| Protocol | Backed by | Answers | How an agent finds it | Status | Radar, 2 Nov 2026 |
|---|---|---|---|---|---|
| UCP | Google, Shopify and co-developers | What, and who pays (with AP2) | `/.well-known/ucp` | 2026-08-25 released, Lodging in draft | 5,429 domains |
| ACP | OpenAI and Stripe | What, who pays | `/.well-known/acp.json` | Beta, 2026-04-17 | 32 domains |
| AP2 | Google, donated to FIDO Alliance | Did the person agree | Extension in an A2A Agent Card or UCP profile | v0.2 | 4 domains |
| Visa Trusted Agent Protocol, Mastercard Agent Pay | Card networks | Who the agent is, who pays | Signatures on each request | Live programmes | Not measured |
| x402 | x402 Foundation (Linux Foundation) | Who pays, per request | HTTP 402 with `PAYMENT-REQUIRED` | V2 | 7 domains |
| MPP | Stripe and Tempo | Who pays, per request | HTTP 402 with `WWW-Authenticate: Payment` | Individual IETF draft | 13 domains |

x402 and MPP charge per request, which is the subject of Appendix C.

## What Nordlys Cabins serves

With every layer switched on, Nordlys serves most of the rows above. It deliberately skips the rest: no signature directory (it sends no bot traffic), no A2A card (it runs no agent), no ACP document (UCP is its commerce profile), no x402 routes (it sells stays, not requests), no `llms-full.txt` and nothing at the legacy `ai-catalog.json` location.[^appB-12]

> **Hands-on:** `node chapters/appendix-b-reference/check-reference.mjs http://127.0.0.1:3000` in the demos repository requests every path and header from these tables and prints which ones a site serves. A "yes" means the file exists, not that its content is right.

[^appB-1]: IANA, "Well-Known URIs" registry, last updated 26 October 2026, https://www.iana.org/assignments/well-known-uris/well-known-uris.xhtml (retrieved November 2026). Registration states and dates in Table B.2 come from this registry.
[^appB-2]: Web Machine Learning Community Group, "WebMCP", Draft Community Group Report, 2 November 2026, https://webmachinelearning.github.io/webmcp/ (retrieved 2 November 2026).
[^appB-3]: draft-ietf-webbotauth-httpsig-protocol-01, "Status of This Memo", https://www.ietf.org/archive/id/draft-ietf-webbotauth-httpsig-protocol-01.txt (retrieved November 2026).
[^appB-4]: Chrome Platform Status, https://chromestatus.com/feature/5117755740913664, WebKit standards positions issue 670, https://github.com/WebKit/standards-positions/issues/670, and Mozilla standards positions issue 1412, https://github.com/mozilla/standards-positions/issues/1412 (retrieved November 2026).
[^appB-5]: M. Nottingham, "Well-Known Uniform Resource Identifiers (URIs)", RFC 8615, https://www.rfc-editor.org/rfc/rfc8615.html (retrieved November 2026).
[^appB-6]: M. Koster, G. Illyes, H. Zeller, L. Sassman, "Robots Exclusion Protocol", RFC 9309, https://www.rfc-editor.org/rfc/rfc9309.html (retrieved November 2026).
[^appB-7]: Cloudflare, "Content Signals Policy", https://blog.cloudflare.com/content-signals-policy/, and "Markdown for Agents", https://developers.cloudflare.com/fundamentals/reference/markdown-for-agents/. IETF, draft-ietf-aipref-attach-05, https://www.ietf.org/archive/id/draft-ietf-aipref-attach-05.txt, and draft-ietf-aipref-vocab-08, https://www.ietf.org/archive/id/draft-ietf-aipref-vocab-08.txt (all retrieved November 2026).
[^appB-8]: "Key changes", Model Context Protocol specification 2026-07-28, https://modelcontextprotocol.io/specification/2026-07-28/changelog, RFC 9745, https://www.rfc-editor.org/rfc/rfc9745.html, and RFC 8594, https://www.rfc-editor.org/rfc/rfc8594.html (retrieved November 2026).
[^appB-9]: Cloudflare, isitagentready.com documentation for agents, https://isitagentready.com/llms-full.txt, and the blog post "Introducing the Agent Readiness score", https://blog.cloudflare.com/agent-readiness/ (both retrieved November 2026).
[^appB-10]: Chrome for Developers, "Agentic browsing scoring", https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring, and the Lighthouse v13.6.0 release notes and source, https://github.com/GoogleChrome/lighthouse/releases/tag/v13.6.0 (both retrieved November 2026).
[^appB-11]: “AI Insights: Adoption of AI agent standards”, Cloudflare Radar, https://radar.cloudflare.com/ai-insights#adoption-of-ai-agent-standards, data dated 2 November 2026, including the Ecommerce and Travel domain categories (retrieved November 2026).
[^appB-12]: Measured with the demos repository's `chapters/appendix-b-reference/check-reference.mjs` against Nordlys Cabins with all layers switched on, 2 November 2026.
