## Chapter 17: Privacy, consent and the human in the loop

Retrieved dates are the day the source was read for this chapter (research files R1–R4 and the W6/W6b checks).

| # | Claim / API / listing (short) | Status | Source URL | Retrieved | Note |
|---|---|---|---|---|---|
| 1 | GDPR Art. 5(1)(c) minimisation quote; 5(1)(b) purpose limitation; 5(1)(e) storage limitation | VERIFIED | https://gdpr-info.eu/art-5-gdpr/ | 2026-11-02 | R4 §2 #12 |
| 2 | GDPR Art. 25(2) data protection by default, quote | VERIFIED | https://gdpr-info.eu/art-25-gdpr/ | 2026-11-02 | R4 §2 #13 |
| 3 | GDPR Art. 6(1)(b) contract basis, quote; six lawful bases | VERIFIED | https://gdpr-info.eu/art-6-gdpr/ | 2026-11-02 | W6 check |
| 4 | GDPR Art. 22 'the right not to be subject to a decision based solely on automated processing' | VERIFIED | https://gdpr-info.eu/art-22-gdpr/ | 2026-11-02 | R4 §2 #14 |
| 5 | GDPR Art. 15 right of access quote; Art. 20 portability 'structured, commonly used and machine-readable format' | VERIFIED | https://gdpr-info.eu/art-15-gdpr/ ; https://gdpr-info.eu/art-20-gdpr/ | 2026-11-02 | W6 check |
| 6 | Consent conditions: freely given, specific, informed, unambiguous, as easy to withdraw as to give | VERIFIED | https://gdpr-info.eu/art-7-gdpr/ | 2026-11-02 | Art. 4(11) and 7(3); paraphrase |
| 7 | No regulator has agent-specific website rules as of Nov 2026 | OPINION | — | 2026-11-02 | Author's reading of R4 §2; phrased as such |
| 8 | UK ICO Tech Futures report on agentic AI, January 2026, not intended as guidance | VERIFIED | https://www.globalpolicywatch.com/2026/02/ico-shares-early-views-on-agentic-ai-data-protection/ | 2026-11-02 | R4 §2 #15; via summary (ICO page behind a bot challenge), stated in text |
| 9 | AEPD 'Inteligencia Artificial Agéntica desde la perspectiva de Protección de Datos', Feb 2026 | VERIFIED | https://www.aepd.es/areas-de-actuacion/innovacion-y-tecnologia | 2026-11-02 | R4 §2 #16 |
| 10 | AEPD warning on keeping data 'just in case' or to 'optimize performance' (law-firm summary) | VERIFIED | https://www.insideprivacy.com/artificial-intelligence/spanish-supervisory-authority-issues-detailed-guidance-on-agentic-ai-and-gdpr-compliance/ | 2026-11-02 | R4 §2 #11; secondary source named |
| 11 | CookieScript (28 Oct 2026): 'the technical ability to click a consent button does not mean the agent has permission...' | VERIFIED | https://cookie-script.com/guides/ai-agent-readiness-cookie-consent | 2026-11-02 | R4 §2 #18; vendor guidance |
| 12 | No regulator guidance found on agent clicks as valid consent | UNVERIFIED | — | 2026-11-02 | Negative finding; text calls it an open legal question |
| 13 | AI Act Art. 50 applies from 2 Aug 2026: 'Transparency rules (Article 50) start to apply.' | VERIFIED | https://ai-act-service-desk.ec.europa.eu/en/ai-act/timeline/timeline-implementation-eu-ai-act | 2026-11-02 | R4 §2 #5 |
| 14 | Digital Omnibus on AI = Regulation (EU) 2026/1744, in force 27 Jul 2026; high-risk postponed to Dec 2027; Art. 50 date kept; grace to 2 Dec 2026 for marking | UNVERIFIED | https://www.bakerbotts.com/thought-leadership/publications/2026/september/eu-ai-act-article-50-transparency-obligations-go-live | 2026-11-02 | Law-firm summary; regulation number not checked against EUR-Lex, text says so |
| 15 | Art. 50 fines up to EUR 15 million or 3% of worldwide turnover | VERIFIED | https://www.bakerbotts.com/thought-leadership/publications/2026/september/eu-ai-act-article-50-transparency-obligations-go-live | 2026-11-02 | R4 §2 #9 (law-firm summary) |
| 16 | Art. 50(1) quote; 50(2) machine-readable marking; deployer disclosure of deepfakes and public-interest text | VERIFIED | https://artificialintelligenceact.eu/article/50/ | 2026-11-02 | R4 §2 #6, #7, #10 |
| 17 | A site visited by an external agent does not become an AI Act provider/deployer | OPINION | https://artificialintelligenceact.eu/article/50/ | 2026-11-02 | Author's reading; chapter carries the not-legal-advice note |
| 18 | MCP 2026-07-28 MRTR: 'The previous pattern of server-initiated requests is no longer supported. This is a breaking change.' | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/mrtr | 2026-11-02 | Pass 3 recheck |
| 19 | MRTR: servers MUST treat requestState as attacker-controlled input, protect integrity (e.g. HMAC or AEAD), MUST reject state that fails verification | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/mrtr | 2026-11-02 | Pass 3 recheck |
| 20 | Elicitation form and URL modes; MUST NOT use form mode for passwords, API keys, access tokens, payment credentials; MUST use URL mode for such interactions | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/client/elicitation | 2026-11-02 | Pass 3 recheck |
| 21 | URL mode accept 'indicates that the user has consented to the interaction. It does not mean that the interaction is complete.' | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/client/elicitation | 2026-11-02 | Pass 3 recheck |
| 22 | Clients must 'clearly display the target domain/host and gather user consent before navigation'; 'subject to the user's ability to review and decline'; 'may change in future protocol revisions' | VERIFIED | https://modelcontextprotocol.io/specification/2026-07-28/client/elicitation | 2026-11-02 | Pass 3 recheck |
| 23 | TS SDK v2.4.0 exposes inputRequired / elicitUrl / acceptedContent helpers and 'applies no integrity protection by default' to requestState | VERIFIED | npm @modelcontextprotocol/server@2.4.0 type declarations | 2026-11-02 | Pass 3: grep of the installed package |
| 24 | WebMCP draft CG report 27 Oct 2026 has no human-in-the-loop method in its IDL | VERIFIED | https://webmachinelearning.github.io/webmcp/ | 2026-11-02 | R4 §2 #4, WebMCP FACTS |
| 25 | Open PR #204 'Replace requestUserInteraction with requestUserInput', modes interactive/form/url | VERIFIED | https://github.com/webmachinelearning/webmcp/pull/204 | 2026-11-02 | R4 §2 #4 |
| 26 | Chrome secure-tools page (updated 1 Sep 2026): 'the spec draft includes `requestUserInteraction()`' (inconsistent with spec) | VERIFIED | https://developer.chrome.com/docs/ai/webmcp/secure-tools | 2026-11-02 | R4 §2 #17 |
| 27 | consequentialHint lets agent/browser ask before running | VERIFIED | https://developer.chrome.com/docs/ai/webmcp/secure-tools | 2026-11-02 | Same source as Chapter 16 |
| 28 | AP2 signed mandates (Chapter 12) | VERIFIED | see shared/validation/12-agents-that-buy.md | 2026-11-02 | Cross-reference only |
| 29 | Retention periods (30 days raw logs, daily-rotating IP hash) are a proposal | OPINION | — | — | Labelled a proposal in text and in retention.js |
| 30 | Listings 17.2, 17.3, 17.5, 17.7 contiguous excerpts; 17.9 identical; 17.1, 17.4, 17.6, 17.8 captured demo output | VERIFIED | demos/ (local diff) | 2026-11-02 | Pass 3 |
| 31 | Tests: 7/7 with Node 22.23 and 24.22, MCP TS SDK 2.4.0 | VERIFIED | local run | 2026-11-02 | W6b rerun |

## Demos

- `nordlys-cabins/layers/17-consent/` (consent.js, outbox.js, activity.js, retention.js, request-booking.js, index.js)
- `nordlys-cabins/tests/ch17-consent.test.js`: `node --test tests/ch17-consent.test.js` in `nordlys-cabins/` → 7/7 pass (Node 22.23.2 and 24.22.1, `@modelcontextprotocol/server` and `client` 2.4.0, 2 Nov 2026)
- Same dependency note as Chapter 16: the MCP SDK packages are not declared in a package.json of the demos tree.

## Figures

- figure-17-1 (who holds what in an agent booking)
- figure-17-2 (request_booking in three rounds, sequence diagram)
