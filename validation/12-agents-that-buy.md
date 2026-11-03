## Chapter 12: Agents that buy: commerce and payments

Retrieved dates are the day the source was read for this chapter.

| # | Claim / API / listing (short) | Status | Source URL | Retrieved | Note |
|---|---|---|---|---|---|
| 1 | Radar adoption snapshot: 115,468 of top 200,000 domains | VERIFIED | https://radar.cloudflare.com/ai-insights#adoption-of-ai-agent-standards | 2026-11-02 | via R1 §3 facts 1 |
| 2 | UCP 5,429 domains (4.7%); ACP 32; MPP 13; x402 7; AP2 4 | VERIFIED | https://radar.cloudflare.com/ai-insights#adoption-of-ai-agent-standards | 2026-11-02 | R1 §3 facts 8, 13 |
| 3 | Radar footnote 'x402 is only relevant for sites with paid content' | VERIFIED | https://radar.cloudflare.com/ai-insights#adoption-of-ai-agent-standards | 2026-11-02 | R1 §3 fact 14, verbatim |
| 4 | Ecommerce: UCP 4,181 of 18,927 domains; Travel: UCP 38 of 6,896 | VERIFIED | https://radar.cloudflare.com/ai-insights?domainCategory=Ecommerce / Travel | 2026-11-02 | R1 §3 facts 15, 16 |
| 5 | Shopify storefronts serve /.well-known/ucp by default | VERIFIED (inference from stores checked) | https://www.allbirds.com/.well-known/ucp ; https://kith.com/.well-known/ucp | 2026-11-02 | fetched by W5: version 2026-08-25, dev.ucp.shopping MCP endpoint on myshopify.com; R1 headline 4. Attribution to the platform is inference, said so in text |
| 6 | UCP co-developers (shopping, lodging, food lists) | VERIFIED | https://ucp.dev/ | 2026-11-02 | R3 6.12 |
| 7 | UCP: business stays merchant of record; OAuth 2.0 account linking; AP2 payments | VERIFIED | https://ucp.dev/ | 2026-11-02 | R3 6.11 |
| 8 | Resolution flow step 1 'Discovery: Fetch business profile from /.well-known/ucp'; 'MUST resolve schemas following this sequence' | VERIFIED | https://ucp.dev/specification/overview/ | 2026-11-02 | read by W5, saved shared/research/w5/ucp-overview.txt |
| 9 | Profile members ucp.version, services, capabilities, payment_handlers; services and payment_handlers 'MUST be present even when empty' | VERIFIED | https://ucp.dev/specification/overview/ | 2026-11-02 | Profile Structure section |
| 10 | Profile keys[] is RFC 7517 JWK Set, reusable as Web Bot Auth key source | VERIFIED | https://ucp.dev/specification/overview/ | 2026-11-02 | Profile Structure section |
| 11 | UCP version format is a date (YYYY-MM-DD) | VERIFIED | https://github.com/Universal-Commerce-Protocol/ucp/blob/main/source/schemas/ucp.json | 2026-11-02 | pattern ^\d{4}-\d{2}-\d{2}$ |
| 12 | Latest released version 2026-08-25 (tag v2026-08-25, 25 Aug 2026) | VERIFIED | https://github.com/Universal-Commerce-Protocol/ucp/releases | 2026-11-02 | GitHub releases API |
| 13 | Lodging capability added by commit c9a1395 'feat: Introduce Lodging Booking Capability and Cancellation Policy Extension (#780)', 24 Sep 2026 | VERIFIED | https://github.com/Universal-Commerce-Protocol/ucp/pull/780 | 2026-11-02 | git log on main; FACTS/R3 give 25 Sep (announcement); text says 24 Sep (commit date) |
| 14 | ucp.dev banner 'Lodging draft specification now available' | VERIFIED | https://ucp.dev/ | 2026-11-02 | R3 6.14 |
| 15 | Lodging page draft warning quote 'data models, protocol bindings, and operational flows are under active iteration and may undergo breaking changes as the specification evolves' | VERIFIED | https://ucp.dev/draft/specification/lodging/booking/ | 2026-11-02 | docs/specification/lodging/booking/index.md at commit 58c7ab9 |
| 16 | Lodging published only under /draft/ (latest/ and unversioned paths 404) | VERIFIED | https://ucp.dev/draft/specification/lodging/booking/ | 2026-11-02 | HTTP 200 for /draft/, 404 for /latest/ and /specification/lodging/booking/ |
| 17 | Google page quote 'adopt UCP to enable agentic actions on Google surfaces such as AI Mode in Google Search'; waitlist; 'You remain the Merchant of Record.' | VERIFIED | https://developers.google.com/hotels/ucp | 2026-11-02 | page text read by W5 |
| 18 | Google plans to adopt draft for AI Mode hotel booking | VERIFIED (secondary) | https://www.searchenginejournal.com/google-plans-to-adopt-ucp-draft-spec-for-ai-mode-hotel-booking/591235/ | 2026-11-02 | R3 6.15; secondary source, flagged in footnote |
| 19 | Booking session concepts: stays (accommodation_type, rate_plan, stay_dates, occupancy), booker vs guests, totals, policies, expires_at, status values, continue_url | VERIFIED | https://ucp.dev/draft/specification/lodging/booking/ | 2026-11-02 | index.md Key Concepts, Status Values, Continue URL |
| 20 | guest ids: Platforms 'MUST NOT use persistent cross-merchant user tracking identifiers' | VERIFIED | https://ucp.dev/draft/specification/lodging/booking/ | 2026-11-02 | verbatim |
| 21 | 'strict all-in pricing'; guest 'is presented with the complete stay liability before booking confirmation' | VERIFIED | https://ucp.dev/draft/specification/lodging/booking/ | 2026-11-02 | Pricing Scope, verbatim |
| 22 | Amounts are integers in minor units (7,500 NOK = 750000) | VERIFIED | https://ucp.dev/draft/specification/lodging/booking/rest/ | 2026-11-02 | REST examples (amount 363000 USD minor units); AP2 payment mandate also 'integer minor units per ISO 4217' |
| 23 | cancellation-policy extension refundability values refundable/partially_refundable/non_refundable | VERIFIED | https://ucp.dev/draft/specification/lodging/extensions/cancellation-policy/ | 2026-11-02 | cancellation-policy.md + schema policy_cancellation.json |
| 24 | Business 'MAY place a temporary soft hold on inventory' or verify at completion | VERIFIED | https://ucp.dev/draft/specification/lodging/booking/ | 2026-11-02 | Session Expiry & Inventory Management |
| 25 | Business 'MUST provide continue_url when returning status = requires_escalation' | VERIFIED | https://ucp.dev/draft/specification/lodging/booking/ | 2026-11-02 | Continue URL > Availability |
| 26 | 'does not need to become PCI DSS compliant'; 'Unless the AP2 Mandates extension is supported, the booking must be finalized manually by the user through a trusted UI.' | VERIFIED | https://ucp.dev/draft/specification/lodging/booking/ | 2026-11-02 | Overview, verbatim |
| 27 | REST operations POST /booking-sessions, GET/PUT /{id}, POST /{id}/complete, /cancel; MCP tools create/get/update/complete/cancel_booking_session | VERIFIED | https://ucp.dev/draft/specification/lodging/booking/rest/ ; .../mcp/ | 2026-11-02 | rest.md and mcp.md |
| 28 | requires_buyer_review definition quote | VERIFIED | https://ucp.dev/draft/specification/lodging/booking/ | 2026-11-02 | Error Handling, verbatim |
| 29 | totals_changed warning, platform must show it | VERIFIED | https://ucp.dev/draft/specification/lodging/booking/ | 2026-11-02 | Totals Changes |
| 30 | inventory_exhausted standard error, severity unrecoverable in example | VERIFIED | https://ucp.dev/draft/specification/lodging/booking/rest/ | 2026-11-02 | Standard Errors table + REST error example |
| 31 | ACP 'maintained by OpenAI and Stripe and is currently in beta', Apache 2.0 | VERIFIED | https://github.com/agentic-commerce-protocol/agentic-commerce-protocol | 2026-11-02 | README + R3 6.6 |
| 32 | ACP versions 2025-09-29 … 2026-04-17; 2026-04-17 adds carts, orders, auth, MCP, /.well-known/acp.json 'for pre-session capability checks' | VERIFIED | https://github.com/agentic-commerce-protocol/agentic-commerce-protocol/tree/main/changelog | 2026-11-02 | spec/ folders; changelog/2026-04-17.md line 198 |
| 33 | ACP last commit on main 17 Jul 2026 | VERIFIED | https://github.com/agentic-commerce-protocol/agentic-commerce-protocol/commits/main | 2026-11-02 | shallow clone: 7fdd78d Fri Jul 17 2026 |
| 34 | ACP merchant of record kept; Stripe Shared Payment Token as first PSP | VERIFIED | https://www.agenticcommerce.dev/ | 2026-11-02 | R3 6.8 |
| 35 | ACP launched with Instant Checkout Sep 2025 | VERIFIED | https://www.agenticcommerce.dev/ | 2026-11-02 | R3 §6 current state |
| 36 | OpenAI pivoted away from Instant Checkout (Mar 2026) | UNVERIFIED (secondary) | https://www.cnbc.com/2026/03/24/openai-revamps-shopping-experience-in-chatgpt-after-instant-checkout.html | 2026-11-02 | search snippet only; phrased 'according to press reports I could not confirm' |
| 37 | AP2 announced 16 Sep 2025; extension for A2A and UCP; 'AP2 v0.2 Release and FIDO Alliance Donation' | VERIFIED | https://ap2-protocol.org/ | 2026-11-02 | home page; donation date UNVERIFIED (said so) |
| 38 | AP2 v0.2 checkout mandate (merchant-signed checkout_jwt + checkout_hash) and payment mandate (payee, payment_amount minor units, instrument, risk_data); open/closed forms | VERIFIED | https://ap2-protocol.org/ap2/checkout_mandate/ ; https://ap2-protocol.org/ap2/payment_mandate/ | 2026-11-02 | read by W5 |
| 39 | UCP+AP2: platform submits both mandates to /complete; business verifies checkout mandate, processor verifies payment mandate | VERIFIED | https://ucp.dev/documentation/ucp-and-ap2/ | 2026-11-02 | read by W5 |
| 40 | Visa TAP quotes: 'merchants and infrastructure providers who want to securely recognize and transact with Visa-approved AI agents'; 'will include a message signature in its request to your server'; RFC 9421 | VERIFIED | https://developer.visa.com/docs/trusted-agent-protocol | 2026-11-02 | read by W5 |
| 41 | 'Both Trusted Agent Protocol and Agent Pay leverage Web Bot Auth as the agent authentication layer' (24 Oct 2025) | VERIFIED | https://blog.cloudflare.com/secure-agentic-commerce | 2026-11-02 | R3 5.32 |
| 42 | Mastercard: 'recognize trusted AI agents and accept secure, tokenized transactions' | VERIFIED (search summary) | https://www.mastercard.com/global/en/news-and-trends/stories/2025/agentic-commerce-framework.html | 2026-11-02 | search snippet; developer docs need JS (not read) |
| 43 | x402 Foundation announced by Cloudflare + Coinbase, 23 Sep 2025 | VERIFIED (search result) | https://blog.cloudflare.com/x402 | 2026-11-02 | R3 5.28 / R1 #22 |
| 44 | x402 Foundation under Linux Foundation 2 Apr 2026; operational launch 14 Jul 2026 with 40 members; premier members list | VERIFIED | https://docs.cdp.coinbase.com/x402/support/x402-foundation ; https://x402.org/linux-foundation-announces-operational-launch-of-x402-foundation-to-standardize-internet-native-payments-for-ai-agents-and-applications/ | 2026-11-02 | R3 5.26, 5.27 |
| 45 | x402 V2 headers PAYMENT-REQUIRED / PAYMENT-SIGNATURE / PAYMENT-RESPONSE, base64 JSON | VERIFIED | https://docs.x402.org/core-concepts/http-402 | 2026-11-02 | read by W5 |
| 46 | PaymentRequired fields x402Version, error, resource, accepts[scheme, network CAIP-2, amount, asset, payTo, maxTimeoutSeconds, extra]; example network eip155:84532 and asset 0x036C…CF7e | VERIFIED | https://github.com/x402-foundation/x402/blob/main/specs/x402-specification-v2.md | 2026-11-02 | §5.1, commit 5220ceb (2 Nov 2026) |
| 47 | x402 test facilitator for sellers | VERIFIED | https://docs.x402.org/getting-started/quickstart-for-sellers | 2026-11-02 | R3 5.25 |
| 48 | MPP 'an open protocol that lets agents pay for your APIs and services programmatically without a checkout UI, co-authored by Stripe and Tempo' | VERIFIED | https://docs.stripe.com/payments/machine/mpp | 2026-11-02 | read by W5 |
| 49 | MPP launched 18 Mar 2026 with Tempo mainnet | VERIFIED (search result + press) | https://stripe.com/blog/machine-payments-protocol ; https://fortune.com/2026/03/18/stripe-tempo-paradigm-mpp-ai-payments-protocol/ | 2026-11-02 | search snippets |
| 50 | MPP uses WWW-Authenticate: Payment challenge (id, realm, method, intent, request) | VERIFIED | https://mpp.dev/protocol/http-402 ; https://mpp.dev/protocol/challenges | 2026-11-02 | read by W5 |
| 51 | draft-httpauth-payment-01, last updated 2026-09-09, no stream | VERIFIED | https://datatracker.ietf.org/doc/draft-httpauth-payment/ | 2026-11-02 | datatracker page |
| 52 | MPP supports cards via SPTs and stablecoins; x402 support blog June 2026 | VERIFIED | https://docs.stripe.com/payments/machine/mpp ; https://mpp.dev/ | 2026-11-02 | 'EVM and x402 support June 8, 2026' |
| 53 | isitagentready commerce pass criteria (ucp, acp, x402, mpp, ap2 opt-in) | VERIFIED | https://isitagentready.com/llms-full.txt | 2026-11-02 | checks 19-23 read by W5 |
| 54 | Commerce checks scored only for sites with e-commerce signals, otherwise neutral; do not affect level | VERIFIED | https://isitagentready.com/llms-full.txt ; https://blog.cloudflare.com/agent-readiness/ | 2026-11-02 | R1 profiles/levels; 'We also check for Universal Commerce Protocol and Agentic Commerce Protocol' |
| 55 | Lighthouse 13.6.0 Agentic Browsing has no commerce audit | VERIFIED | https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring | 2026-11-02 | seven audits listed in FACTS R4 §3 |
| 56 | Chrome agent defences: second model vets actions, deterministic confirmations before sensitive sites | VERIFIED | see R4 §1 (Chrome security blog 8 Dec 2025) | 2026-11-02 | FACTS R4 §1; details deferred to Chapter 16 |
| 57 | SCA under PSD2 for online card payments in the EEA (Norway in EEA) | OPINION / general knowledge | https://www.eba.europa.eu/regulation-and-policy/payment-services-and-electronic-money/regulatory-technical-standards-on-strong-customer-authentication-and-secure-communication-under-psd2 | 2026-11-02 | phrased 'generally', with 'a question for your PSP' |
| 58 | Nordlys demo: Fjellro 7–10 Dec 2026 = 3 x 2,200 + 900 = 7,500 NOK | VERIFIED | demos run | 2026-11-02 | store.quotePrice; curl output in shared/research/w5/ch12-curl-outputs.txt |
| 59 | Nordlys layer outputs validate against UCP draft JSON Schemas at commit 58c7ab9 (profile, booking with cancellation policy, error_response) | VERIFIED | https://github.com/Universal-Commerce-Protocol/ucp/tree/58c7ab92dcf80b3b1fc756d577b0552ec1cd503a/source/schemas | 2026-11-02 | python jsonschema 4.26.0, Draft 2020-12; first run found 3 errors (stay totals, description object, completed booker), fixed |
| 60 | isitagentready ucp criterion wording 'protocol_version' vs spec ucp.version | OPINION | https://isitagentready.com/llms-full.txt | 2026-11-02 | interpretation stated in text; Nordlys not scanned by the public tool (localhost) |
| 61 | Node.js 22.23 used to run the demo; Hono 4.13.16 | VERIFIED | demos/nordlys-cabins/package.json; node --version | 2026-11-02 |  |

## Demos

- Layer `nordlys-cabins/layers/12-commerce/`: index.js, sessions.js, ucp.js, checkout.js, x402-demo.js, README.md
- Tests: `nordlys-cabins/tests/ch12-commerce.test.js` (node:test, 9 tests). Command `node --test tests/ch12-*.test.js` → 9 pass, 0 fail (2 Nov 2026, Node 22.23.2, hono 4.13.16, @hono/node-server 2.1.6).
- Schema validation (not in repo, no new dependency): responses dumped from the app validated with python jsonschema 4.26.0 against /source/schemas of Universal-Commerce-Protocol/ucp at commit 58c7ab9 → profile, create, completed, error: 0 errors.
- Listings 12.1–12.5 are byte-identical contiguous excerpts of the files above (generated from the files). curl outputs are real runs against `node server.js` with NOW=2026-11-10, PUBLIC_ORIGIN=https://nordlys.example, NORDLYS_X402_DEMO=1 (the totals entries in the session output are joined onto one line each, disclosed in the text).
- Re-run by W5b on 2 Nov 2026 with Node 24.22.1 (the demos require Node >= 24): `node --test tests/ch12-commerce.test.js` → 9 pass, 0 fail.

## Figures

- figure-12-1: the four questions and the commerce protocols (Nordlys path filled)
- figure-12-2: UCP Lodging booking session status lifecycle (from the draft's own state diagram)
- figure-12-3: sequence of the Nordlys agent-safe checkout
