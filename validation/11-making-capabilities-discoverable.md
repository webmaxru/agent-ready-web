## Chapter 11: Making capabilities discoverable

| # | Claim / API / listing (short) | Status | Source URL | Retrieved | Note |
|---|---|---|---|---|---|
| 1 | Radar adoption 2 Nov 2026: Link headers 9.7%, API Catalog 0.74%, MCP Server Card 0.61%, Agent Skills 0.59%, ARD 0.29%, OAuth discovery 8.1%, PRM 4.1% of 115,468 scanned domains | VERIFIED | https://radar.cloudflare.com/ai-insights#adoption-of-ai-agent-standards | 2026-11-02 | via FACTS.md headline 3 (R1) |
| 2 | April 2026: MCP Server Cards + API catalogs together on fewer than 15 sites | VERIFIED | https://blog.cloudflare.com/agent-readiness/ | 2026-11-02 | quote "together appear on fewer than 15 sites in the entire dataset" (R3 1.40) |
| 3 | Cloudflare April post calls SEP-1649 server-card.json "a proposal currently in draft" | VERIFIED | https://blog.cloudflare.com/agent-readiness/ | 2026-11-02 | R3 1.39 |
| 4 | isitagentready: 23 checks, level rules L1–L5 quoted verbatim | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | R1 §1 rows 2, 6–10 |
| 5 | mcpServerCard check reads /.well-known/mcp/server-card.json, also server-cards.json and mcp.json, needs name or serverInfo.name | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | R1 §1 check table |
| 6 | agentSkills check: v0.2.0 index, legacy /.well-known/skills/index.json accepted | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | R1 §1 |
| 7 | ard check: manifest via one of several mechanisms, needs specVersion and ≥1 valid entry; fix prompt says "Serve /.well-known/ai-catalog.json at the origin root" | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | R1 §1 table and row 22 (page script) |
| 8 | A2A agent card and AP2 checks are opt-in | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | R1 row 14 |
| 9 | dnsAid checks DNSSEC-validated SVCB/HTTPS under _agents (e.g. _index._agents) | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | R1 §1 |
| 10 | authMd = /auth.md + PRM + agent_auth block; poppy.json informational draft 0.1 | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | R1 §1 |
| 11 | isitagentready.com serves its own card at /.well-known/mcp.json | VERIFIED | https://isitagentready.com/.well-known/mcp.json | 2026-11-02 | R3 1.38 |
| 12 | 44-site scan: nobody at L2/L3/L5, eight at L4; vercel 9 skills, stripe 10 (legacy v0.1.0 path), isitagentready 25 skills | VERIFIED | https://github.com/webmaxru/agent-ready-web-private (analytics/isitagentready-scans-2026-11-02.md) | 2026-11-02 | R1 scan, FACTS headline 5; isitagentready skills count from R1 §1 |
| 13 | Lighthouse Agentic Browsing reads llms.txt and ARD in the Agent Discoverability group | VERIFIED | https://github.com/GoogleChrome/lighthouse/blob/main/core/config/agentic-browsing-config.js | 2026-11-02 | R2 row 6 |
| 14 | Lighthouse ard-schema: discovery order Agentmap → link rel=ard → Link header → /.well-known/ard.json; legacy ai-catalog warning; "Add 2 to 5 representativeQueries to each entry to get a perfect score"; N/A when absent | VERIFIED | https://developer.chrome.com/docs/lighthouse/agentic-browsing/ard | 2026-11-02 | R2 row 3 |
| 15 | Lighthouse 13.6.0 (27 Oct 2026) moved to ARD v0.91 and /.well-known/ard.json | VERIFIED | https://developer.chrome.com/docs/lighthouse/agentic-browsing/ard | 2026-11-02 | FACTS headline 2 |
| 16 | Lighthouse 13.6.0 run on Nordlys upto=11: category 1; agent-accessibility-tree 1, CLS 1, llms-txt 1, ard-schema 1; WebMCP audits N/A (no flag); credits ard 0.91 (f073b1e); HeadlessChrome 156 | VERIFIED | local run (W3), report JSON fetched 2026-11-02T22:19Z | 2026-11-02 | run by writer W3 in this project; JSON was in scratch, now deleted |
| 17 | RFC 8615 reserves /.well-known/ | VERIFIED | https://www.rfc-editor.org/rfc/rfc8615.html | 2026-11-02 |  |
| 18 | IANA well-known registry (26 Oct 2026): api-catalog permanent (RFC 9727), oauth-protected-resource permanent (RFC 9728), agent-card.json permanent (2025-08-01), ucp provisional (2026-10-26), vacation-rental.json provisional (2026-08-19); no ard.json, ai-catalog.json, agent-skills, mcp.json | VERIFIED | https://www.iana.org/assignments/well-known-uris/well-known-uris.xml | 2026-11-02 | fetched and parsed 2 Nov 2026 |
| 19 | RFC 8288 Web Linking, Proposed Standard, October 2017 | VERIFIED | https://www.rfc-editor.org/rfc/rfc8288.html | 2026-11-02 | status from RFC index |
| 20 | alternate, describedby, api-catalog registered link relations; ard and sitemap not registered | VERIFIED | https://www.iana.org/assignments/link-relations/link-relations.xhtml | 2026-11-02 | R2 row 27 |
| 21 | ARD consumer "MUST fetch /.well-known/ard.json, and MUST honour a rel="ard" link"; predecessor ai-catalog.json and rel ai-catalog are a "courtesy" | VERIFIED | https://agenticresourcediscovery.org/spec/ | 2026-11-02 | fetched 2 Nov 2026 |
| 22 | ARD v0.91, Proposal, 26 Aug 2026, authors Junjie Bu (Google), R.V. Guha, Shaun Smith (Hugging Face) | VERIFIED | https://agenticresourcediscovery.org/spec/ | 2026-11-02 |  |
| 23 | ARD mechanisms: well-known, in-page JSON-LD, Agentmap, link tag, DNS (and Link header per Lighthouse) | VERIFIED | https://agenticresourcediscovery.org/spec/ | 2026-11-02 |  |
| 24 | ARD entry: identifier urn:air:<publisher>:[<namespace>:]<agent-name>, displayName, type (media type), exactly one of url or data; optional description, tags, version, updatedAt; representativeQueries expected, missing = warning | VERIFIED | https://agenticresourcediscovery.org/spec/ | 2026-11-02 |  |
| 25 | ARD: other top-level manifest members "transport-defined and ignored by ARD" | VERIFIED | https://agenticresourcediscovery.org/spec/ | 2026-11-02 | justifies specVersion |
| 26 | Media types application/mcp-server-card+json, application/agent-skills+md; "de-facto community standards tracking towards formal registration" | VERIFIED | https://agenticresourcediscovery.org/spec/ | 2026-11-02 |  |
| 27 | Google announced ARD on 17 Jun 2026 (ai-catalog.json at a well-known path) | VERIFIED | https://developers.googleblog.com/announcing-the-agentic-resource-discovery-specification/ | 2026-11-02 | R3 1.41 |
| 28 | RFC 9727: api-catalog well-known and link relation, linkset+json; service-desc "primarily intended for machine consumption" | VERIFIED | https://www.rfc-editor.org/rfc/rfc9727.html | 2026-11-02 | R3 3.6–3.8 |
| 29 | Listing the MCP endpoint in the API catalog | OPINION |  |  | author's judgment, stated as such |
| 30 | SEP-2127: <streamable-http-url>/server-card "recommended location"; domain discovery via AI Catalog; page status Final; primitives and capabilities excluded; supportedProtocolVersions rationale quote; card does not define a server.json superset | VERIFIED | https://modelcontextprotocol.io/seps/2127-mcp-server-cards | 2026-11-02 | fetched 2 Nov 2026 |
| 31 | Extension repo: "Status: Experimental. This work is for prototyping and feedback only" (repo renamed to ext-server-card) | VERIFIED | https://github.com/modelcontextprotocol/ext-server-card | 2026-11-02 | fetched 2 Nov 2026 |
| 32 | MCP Registry "currently in preview" | VERIFIED | https://modelcontextprotocol.io/registry/about | 2026-11-02 | R3 1.33 |
| 33 | MCP Registry uses reverse-DNS server names | UNVERIFIED | https://modelcontextprotocol.io/registry/about | 2026-11-02 | phrased "as far as I can tell" |
| 34 | No mainstream assistant auto-fetches server cards or skills indexes from arbitrary domains without human approval (Nov 2026) | OPINION |  |  | author's search, stated as "I could not find" |
| 35 | Agent Skills spec: SKILL.md front matter name (≤64 chars, lowercase/digits/hyphens) and description (≤1024 chars) required | VERIFIED | https://agentskills.io/specification | 2026-11-02 |  |
| 36 | Agent Skills Discovery RFC: Draft, v0.2.0, published 2026-01-17, updated 2026-03-12; path moved to /.well-known/agent-skills/; $schema; type skill-md or archive; digest = SHA-256 of the artifact | VERIFIED | https://github.com/cloudflare/agent-skills-discovery-rfc | 2026-11-02 |  |
| 37 | $schema host schemas.agentskills.io did not resolve on 2 Nov 2026; isitagentready.com and vercel.com use the same URL | VERIFIED | https://isitagentready.com/.well-known/agent-skills/index.json | 2026-11-02 | DNS failure observed from the box; vercel index fetched too |
| 38 | A2A 1.0.0 released 12 Mar 2026; agent card at /.well-known/agent-card.json | VERIFIED | https://a2a-protocol.org/latest/specification/ | 2026-11-02 | R3 6.1–6.3 |
| 39 | DNS-AID individual draft draft-mozleywilliams-dnsop-dnsaid-02, "not endorsed by the IETF", "no formal standing" | VERIFIED | https://datatracker.ietf.org/doc/draft-mozleywilliams-dnsop-dnsaid/ | 2026-11-02 | fetched 2 Nov 2026 |
| 40 | Infoblox and GoDaddy announced support for DNS-AID-style agent discovery (2026) | UNVERIFIED | https://aboutus.godaddy.net/newsroom/news-releases/press-release-details/2026/Infoblox-and-GoDaddy-Support-Open-Standards-for-AI-Agent-Discovery-Identity-and-Verification-2026-0acKMntvOC/default.aspx | 2026-11-02 | search snippet only, page not opened |
| 41 | auth.md: "An open protocol that lets agents register for services on behalf of users", WorkOS, MIT, agent_auth block | VERIFIED | https://github.com/workos/auth.md | 2026-11-02 | fetched 2 Nov 2026 |
| 42 | VRP vacation-rental.json spec v0.1, Status Draft, published 2026-06-19 (revised 2026-08-20), quote "the origin is a bookable vacation-rental node" | VERIFIED | https://vacationrentalprotocol.com/spec/well-known-uri-v0.1 | 2026-11-02 |  |
| 43 | RFC 9728 PRM, RFC 8414 AS metadata; Chapter 14 adds both | VERIFIED | https://www.rfc-editor.org/rfc/rfc9728.html | 2026-11-02 | R3 §7 |
| 44 | Nordlys levels by chapter: baseline L0, ch3 L1, ch4 L2, ch6 L3, ch7 L4, ch11 L4 (+mcpServerCard, agentSkills, ard), ch14–20 L4 (+oauthDiscovery, oauthProtectedResource) | VERIFIED | local checker demos/chapters/02-your-first-agent-ready-page/agent-ready-check.mjs | 2026-11-02 | run 2 Nov 2026, Node 24.22.1, optIn true |
| 45 | Nordlys Link header after Chapter 11 (4 values) | VERIFIED | demo output | 2026-11-02 | in-process app.request('/') at upto=11 |
| 46 | Skills index digest sha256:9838d68c… | VERIFIED | demo output | 2026-11-02 | production origin https://nordlys.example |
| 47 | MCP SDK packages 2.4.0 | VERIFIED | https://registry.npmjs.org/@modelcontextprotocol%2fserver | 2026-11-02 | R3 1.23 |

### Demos

- Layer: `nordlys-cabins/layers/11-discovery/index.js`, `nordlys-cabins/layers/11-discovery/skills/book-a-nordlys-cabin/SKILL.md`
- Listings: 11.1 (index.js excerpt, server card), 11.2 (SKILL.md whole), 11.3 (index.js excerpt, skills index), 11.4 (index.js excerpt, ARD), 11.5 (index.js excerpt, catalog and Link) — all byte-identical contiguous excerpts, checked by script on 2 Nov 2026.
- Test: `cd nordlys-cabins && node --test tests/ch11-discovery.test.js` — 5/5 pass; with ch07 and ch08: 20/20 pass (Node.js 24.22.1, @modelcontextprotocol/server 2.4.0, @modelcontextprotocol/client 2.4.0, zod 4.6.7, hono 4.13.16, @scalar/openapi-parser 0.29.19 for the optional ch07 check).
- Changes by W3b on 2 Nov 2026: ARD entry term `capabilities` (not an ARD term) replaced by the standard optional term `tags`; SKILL.md step 6 no longer uses the "NC-XXXXXX" pattern (it tripped the placeholder grep).
- Ladder: a throwaway script ran `startServer({ upto })` + `runChecks(url, { optIn: true })` for upto 0,3,4,5,6,7,8,10,11,12,14,15,20.

### Figures

- figure-11-1 (discovery map), figure-11-2 (three server card addresses), figure-11-3 (level ladder by chapter): SVG in book/figures/src, rendered with figures/render.py, inspected.
