## Chapter 7: APIs agents can use

Writer W3, 2026-11-02. Every claim, number, name, status and date in the chapter, with its source.

| # | Claim / API / listing (short) | Status | Source URL | Retrieved | Note |
|---|---|---|---|---|---|
| 1 | OpenAI lists 11 Dec 2026 as scheduled retirement of Custom GPTs; Custom Actions do not transfer to MCP-based plugins | VERIFIED (date via search snippet + secondary) | https://help.openai.com/en/articles/20001519-custom-gpt-retirement-and-migration-faq ; https://adtmag.com/articles/2026/09/28/openai-custom-gpt-retirement-puts-integrations-on-the-migration-checklist.aspx | 2026-11-02 | OpenAI page 403 on fetch; text phrased cautiously ('check the date'). R3 3.15/3.16 |
| 2 | Azure API Management exposes REST operations as MCP tools | VERIFIED | https://learn.microsoft.com/en-us/azure/api-management/export-rest-mcp-server | 2026-11-02 | page title 'Expose REST API as MCP server'; R3 3.19 |
| 3 | Amazon Bedrock AgentCore Gateway takes OpenAPI, Smithy, Lambda as tool inputs, serves MCP | VERIFIED | https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html | 2026-11-02 | R3 3.20 |
| 4 | Copilot Studio REST API tools from OpenAPI, converted to v2, preview | VERIFIED | https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-extend-action-rest-api | 2026-11-02 | title says (preview); R3 3.17 |
| 5 | Google ADK OpenAPIToolset generates tools from OpenAPI 3.x | VERIFIED | https://adk.dev/tools-custom/openapi-tools/ | 2026-11-02 | R3 3.18 |
| 6 | OpenAPI 3.2.0 dated 19 Sep 2025, 3.2.1 dated 10 Sep 2026; 3.2 adds hierarchical tags, QUERY method, streaming | VERIFIED | https://spec.openapis.org/oas/v3.2.0.html ; https://spec.openapis.org/oas/v3.2.1.html ; https://www.openapis.org/blog/2025/09/23/announcing-openapi-v3-2 | 2026-11-02 | R3 3.1-3.3 |
| 7 | OpenAPI 3.1.2 exists and is what Nordlys uses | VERIFIED | https://spec.openapis.org/oas/v3.1.2.html | 2026-11-02 | demo openapi.js 'openapi: 3.1.2' |
| 8 | 3.1 is the safer target in Nov 2026 (uneven 3.2 tool support) | OPINION | R3 §3 pitfalls | 2026-11-02 | no survey found, said so in text |
| 9 | @scalar/openapi-parser 0.29.19 validates the description; $ref + required sibling rejected | VERIFIED | https://registry.npmjs.org/@scalar/openapi-parser | 2026-11-02 | run locally in test 'the OpenAPI document is valid' |
| 10 | RFC 9457 problem details, application/problem+json, members type/title/status/detail/instance, extensions allowed; obsoletes RFC 7807 | VERIFIED | https://www.rfc-editor.org/rfc/rfc9457.html | 2026-11-02 | R3 3.10 |
| 11 | RFC 9457 example shows an errors array (with detail and pointer) | VERIFIED | https://www.rfc-editor.org/rfc/rfc9457.html | 2026-11-02 | Section 3 example |
| 12 | IANA HTTP Problem Types registry exists; quota-exceeded registered via the RateLimit draft | VERIFIED | https://www.iana.org/assignments/http-problem-types ; https://www.ietf.org/archive/id/draft-ietf-httpapi-ratelimit-headers-11.txt | 2026-11-02 | type URI https://iana.org/assignments/http-problem-types#quota-exceeded and violated-policies from the draft |
| 13 | Idempotency-Key draft-08, October 2026, expires 25 Apr 2027; sf-string; 400 missing, 422 reuse with different payload, 409 still processing; fingerprint optional | VERIFIED | https://www.ietf.org/archive/id/draft-ietf-httpapi-idempotency-key-header-08.txt | 2026-11-02 | read 2026-11-02; R3 3.11/3.12 |
| 14 | Stripe uses Idempotency-Key header | VERIFIED | https://docs.stripe.com/api/idempotent_requests | 2026-11-02 |  |
| 15 | RateLimit headers draft-11 (May 2026, expires 24 Nov 2026): RateLimit-Policy q/w, RateLimit r/t | VERIFIED | https://www.ietf.org/archive/id/draft-ietf-httpapi-ratelimit-headers-11.txt | 2026-11-02 | R3 3.13/3.14 |
| 16 | Older RateLimit drafts used separate headers such as RateLimit-Remaining | VERIFIED | https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/ | 2026-11-02 | history of the draft |
| 17 | Arazzo 1.1.0 dated 17 May 2026, adds AsyncAPI support | VERIFIED | https://spec.openapis.org/arazzo/v1.1.0.html | 2026-11-02 | R3 3.4 |
| 18 | Few agent platforms read Arazzo as of Nov 2026; progressive discovery on MCP roadmap | OPINION / VERIFIED (roadmap) | https://modelcontextprotocol.io/development/roadmap | 2026-11-02 | adoption is an author judgment |
| 19 | RFC 9727 (June 2025): api-catalog well-known URI + link relation; MUST be Linkset application/linkset+json with profile; HEAD returns Link rel=api-catalog; examples use service-desc/service-doc/service-meta/status | VERIFIED | https://www.rfc-editor.org/rfc/rfc9727.html | 2026-11-02 | R3 3.6-3.8 |
| 20 | Linkset format RFC 9264; service-desc etc. from RFC 8631 | VERIFIED | https://www.rfc-editor.org/rfc/rfc9264.html ; https://www.rfc-editor.org/rfc/rfc8631.html | 2026-11-02 |  |
| 21 | Radar: API Catalog on 0.74% of 115,468 scanned domains of top 200k, data dated 2026-11-02 | VERIFIED | https://radar.cloudflare.com/ai-insights#adoption-of-ai-agent-standards | 2026-11-02 | FACTS.md headline 3 |
| 22 | isitagentready apiCatalog check: linkset+json with linkset array; linkHeaders looks for agent-useful rels incl. api-catalog | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | R1 check table |
| 23 | isitagentready Level 4 = Level 3 + 1 of MCP Server Card, A2A Agent Card, Agent Skills, API Catalog | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | R1 row 9 |
| 24 | Lighthouse Agentic browsing does not audit APIs | VERIFIED | R1 Lighthouse section | 2026-11-02 | category = a11y subset, CLS, WebMCP, llms.txt |
| 25 | RFC 9745 Deprecation header (March 2025); RFC 8594 Sunset header | VERIFIED | https://www.rfc-editor.org/rfc/rfc9745.html ; https://www.rfc-editor.org/rfc/rfc8594.html | 2026-11-02 | read 2026-11-02 |
| 26 | Real exchanges: availability Fjellro 2-5 Dec 2026, 4 guests = 7000 + 900 = 7900 NOK; Lyngen Lysthus = 10700 + 1200 = 11900; too_many_guests 422; min_nights 422; booking 201/200 replay/422 reuse; cancel 404 wrong email/200 refund 7900/409 already-cancelled; 429 with quota 2; HEAD catalog | VERIFIED | demo run, /tmp scripts against nordlys-cabins upto=7 | 2026-11-02 | 2026-12-02 is a Wednesday; booking refs are random |
| 27 | Free cancellation ends 14 days before check-in (18 Nov for 2 Dec) | VERIFIED | demos nordlys-cabins/src (store.cancellationPolicy) | 2026-11-02 |  |
| 28 | Listings 7.1-7.6 byte-identical to demo files | VERIFIED | demos nordlys-cabins/layers/07-public-api/{openapi,api,service,arazzo,catalog,index}.js | 2026-11-02 | checked by script |

### Demos

- Layer: `nordlys-cabins/layers/07-public-api/` (index.js, api.js, service.js, problems.js, ratelimit.js, openapi.js, arazzo.js, catalog.js).
- Tests: `nordlys-cabins/tests/ch07-public-api.test.js`, 8 tests, `node --test tests/ch07-*.test.js` → 8/8 pass (2026-11-02, Node v22.23.2, hono from the app's package.json). The validity test uses `@scalar/openapi-parser` 0.29.19 when installed and skips otherwise (dev dependency requested from the lead).
- No new runtime dependency.

### Figures

- figure-7-1: the Nordlys API layer, catalog, description files, shared booking service (figures/src/figure-7-1.svg)
- figure-7-2: an OpenAPI operation becoming a tool (figures/src/figure-7-2.svg)
- figure-7-3: retry with the same Idempotency-Key, sequence (figures/src/figure-7-3.svg)
