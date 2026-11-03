## Chapter 5: Describing your content with structured data

| # | Claim / API / listing (short) | Status (VERIFIED / UNVERIFIED / OPINION) | Source URL | Retrieved | Note |
|---|---|---|---|---|---|
| 1 | schema.org Version 30.1 published 2026-09-16; 30.1 adds EU DPP vocabulary; 30.0 equivalence annotations GS1/DC/OG | VERIFIED | https://schema.org/version/latest | 2026-11-02 | page read 2 Nov; releases page |
| 2 | Google supports JSON-LD, microdata, RDFa; 'all 3 formats are equally fine'; recommends JSON-LD in most cases | VERIFIED | https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data | 2026-11-02 | read 2 Nov |
| 3 | Cloudflare Markdown for Agents preserves ld+json blocks | VERIFIED | https://developers.cloudflare.com/fundamentals/reference/markdown-for-agents/ | 2026-11-02 | R2 §3 #16 |
| 4 | VacationRental hierarchy LodgingBusiness>LocalBusiness>Organization+Place; definition quote | VERIFIED | https://schema.org/VacationRental | 2026-11-02 | vocab file subClassOf + term page |
| 5 | Usage bands: VacationRental, LodgingBusiness, Accommodation, ReserveAction 10K-100K; LodgingReservation 1K-10K; 'monthly aggregations from Google's web index' | VERIFIED | https://schema.org/VacationRental | 2026-11-02 | term pages fetched 2 Nov |
| 6 | Google AI optimization guide: 'Structured data isn't required for generative AI search...' (updated 2026-07-10) | VERIFIED | https://developers.google.com/search/docs/fundamentals/ai-optimization-guide | 2026-11-02 | R2 §3 #13, R1 #19-20 |
| 7 | Canel (Bing) SMX Munich March 2025: schema helps Microsoft LLMs — second-hand | VERIFIED | https://www.seroundtable.com/schema-llms-copilot-bing-microsoft-39093.html | 2026-11-02 | as report; text labels it as conference statement reported by press |
| 8 | OpenAI commerce uses merchant product feeds | UNVERIFIED | https://developers.openai.com/commerce/specs/file-upload/products | 2026-11-02 | snippet; text says page not read in full |
| 9 | No browsing-agent vendor documents reading JSON-LD | OPINION | https://developers.cloudflare.com/fundamentals/reference/markdown-for-agents/ | 2026-11-02 | absence of evidence, stated as such |
| 10 | Google phase-outs: 12 Jun 2025 announcement (course info, estimated salary, ClaimReview, learning video, special announcement, vehicle listing); docs removed 9 Sep 2025; practice problem + Dataset Nov 2025; FAQ ended 7 May 2026 | VERIFIED | https://developers.google.com/search/updates | 2026-11-02 | R2 §3 #10-11 |
| 11 | Google VacationRental docs partner-only (TAM + Hotel Center), >=8 photos, 5 decimals; additionalType suggestions incl. Cabin; containsPlace.additionalType EntirePlace/PrivateRoom/SharedRoom; lat/long on rental, BedDetails | VERIFIED | https://developers.google.com/search/docs/appearance/structured-data/vacation-rental | 2026-11-02 | read 2 Nov |
| 12 | LodgingBusiness, Accommodation, ReserveAction definitions quoted | VERIFIED | https://schema.org/ReserveAction | 2026-11-02 | term pages via R2 §3 #4-6 |
| 13 | makesOffer domain Organization, Person; offers domain AggregateOffer, CreativeWork, EducationalOccupationalProgram, Event, MenuItem, Product, Service, Trip | VERIFIED | https://schema.org/makesOffer | 2026-11-02 | from schemaorg-current-https.jsonld 2 Nov |
| 14 | provider domain: Action, CreativeWork, EducationalOccupationalProgram, FinancialIncentive, Invoice, OfferShippingDetails, ParcelDelivery, Reservation, Service, Trip (not Organization) | VERIFIED | https://schema.org/provider | 2026-11-02 | vocab file; real failure observed in our test 2 Nov |
| 15 | Google sd-policies: 'Don't mark up content that is not visible to readers of the page...' and fake reviews sentence | VERIFIED | https://developers.google.com/search/docs/appearance/structured-data/sd-policies | 2026-11-02 | read 2 Nov |
| 16 | LodgingReservation for actual reservations, confirmation emails/pages | VERIFIED | https://schema.org/LodgingReservation | 2026-11-02 | R2 §3 #7 |
| 17 | Google AI features page: markup should match visible text; no special schema needed | VERIFIED | https://developers.google.com/search/docs/appearance/ai-features | 2026-11-02 | R2 §3 #12 |
| 18 | No consumer documents reading ReserveAction to book | UNVERIFIED | https://schema.org/ReserveAction | 2026-11-02 | absence of evidence (R2 pitfalls) |
| 19 | jsonld npm latest 9.0.0 (2025-11-21) | VERIFIED | https://www.npmjs.com/package/jsonld | 2026-11-02 | npm registry 2 Nov |
| 20 | schema.org vocabulary file ~1.5 MB, 3,256 graph nodes | VERIFIED | https://schema.org/version/latest/schemaorg-current-https.jsonld | 2026-11-02 | downloaded 2 Nov (1,521,575 bytes) |
| 21 | Schema Markup Validator and Rich Results Test; RRT has no public API | VERIFIED | https://validator.schema.org/ | 2026-11-02 | R2 §3 #18 + demo ideas |
| 22 | schema-dts 2.1.0 published 2026-10-02, google/schema-dts | VERIFIED | https://www.npmjs.com/package/schema-dts | 2026-11-02 | npm registry 2 Nov |
| 23 | Google sitemap lastmod 'consistently and verifiably' accurate | VERIFIED | https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap | 2026-11-02 | read 2 Nov (Ch4) |
| 24 | NLWeb: 19 May 2025, Guha, 'Every NLWeb instance is also a Model Context Protocol (MCP) server', collaborators | VERIFIED | https://news.microsoft.com/source/features/company-news/introducing-nlweb-bringing-conversational-interfaces-directly-to-the-web/ | 2026-11-02 | R2 §6 #1-3 |
| 25 | NLWeb REST API /ask and /mcp, args, result fields incl. schema_object | VERIFIED | https://github.com/nlweb-ai/NLWeb/blob/main/docs/nlweb-rest-api.md | 2026-11-02 | R2 §6 #4 |
| 26 | NLWeb repo nlweb-ai/NLWeb ~6.3k stars, no releases, last push 11 Aug 2026, June 2026 commits dependency bumps; README 'NLWeb is to MCP/A2A what HTML is to HTTP' | VERIFIED | https://github.com/nlweb-ai/NLWeb | 2026-11-02 | R2 §6 #5-6 |
| 27 | nlweb.ai/spec TLS hostname mismatch on 2 Nov 2026 | VERIFIED | https://nlweb.ai/spec | 2026-11-02 | R2 §6 #7 |
| 28 | Cloudflare AI Search NLWeb template public preview | VERIFIED | https://developers.cloudflare.com/ai-search/how-to/nlweb/ | 2026-11-02 | R2 §6 #8 |
| 29 | Guha co-author of ARD spec v0.91 | VERIFIED | https://agenticresourcediscovery.org/spec/ | 2026-11-02 | R2 §6 #9 |
| 30 | isitagentready 23 checks, none reads JSON-LD | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | R1 §1 check table |
| 31 | Lighthouse 13.6.0: SEO manual 'structured-data' audit weight 0; no ld+json gatherer in core/gather or core/audits | VERIFIED | https://github.com/GoogleChrome/lighthouse/blob/main/core/config/default-config.js | 2026-11-02 | grep of lighthouse@13.6.0 package source 2 Nov |
| 32 | Listings 5.1, 5.2, 5.4, 5.5, 5.6 byte-identical with demo files; Listing 5.3 is excerpt of real output; /ask 'sauna hot tub' → Lyngen Lysthus score 3 | VERIFIED | https://github.com/webmaxru/agent-ready-web-demos | 2026-11-02 | checked 2 Nov |

### Demos

- Layer: `nordlys-cabins/layers/05-structured-data/` (index.js, graph.js, ask.js, schema-check.js, vocab-subset.js, schemaorg-subset.json)
- Tests: `nordlys-cabins/tests/ch05-structured-data.test.js` (6 tests, node:test)
- Command: `node --test tests/ch05-*.test.js` (in nordlys-cabins); regenerate vocabulary subset: `node layers/05-structured-data/vocab-subset.js` (needs network)
- Result 2026-11-02: 6/6 pass; ch04 7/7 and core 29/29 still pass with layers up to 5
- Versions: Node.js 22.23.2, hono 4.13.16, jsonld 9.0.0 (needs adding as a devDependency of nordlys-cabins), schema.org 30.1 vocabulary

### Figures

- Figure 5.1 figure-5-1.svg — the JSON-LD graph of one cabin
- Figure 5.2 figure-5-2.svg — one data source, many representations, parity tests
- Figure 5.3 figure-5-3.svg — three levels of checking (syntax, vocabulary, parity)
