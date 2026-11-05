# Editorial log: Chapter 7, Designing tools agents can actually use (v2)

- Sources: v1 Chapter 10 (8,953 words) plus v1 Chapter 16 "Threat-modelling Nordlys Cabins" and "Authorization lives in code" (condensed to about 650 words, new section "A first threat model"). Result: 8755 words incl. code and notes.
- Reframed for v2 order: tool design now comes before the API, MCP and WebMCP chapters, so references to them are forward ("which Chapter 8 builds"). The layer note says the demos keep v1 layer numbers.
- Figures kept: 10.1 -> 7.1, 10.2 -> 7.2. Table 10.1 -> 7.1.
- Listings kept: 10.2 -> 7.1, 10.3 -> 7.2, 10.4 -> 7.3, 10.6 -> 7.4, 10.7 -> 7.5, 10.8 -> 7.6. Cut: 10.1 (the "before" availability tool, now described in one sentence) and 10.5 (error code table, described in prose). Two command blocks and the error comparison block kept as in v1.
- Cut: tool-name prefixes and namespacing paragraph, the result size habit (25,000 tokens), the "people read descriptions too" note, the fingerprint idea for retries, the role-by-role list, the mock-model sentence.
- Removed the v1 UNVERIFIED claim about OpenAI's 64-character limit. The names rule now rests only on the verified rows (both APIs refused dots on 2 November 2026, v1 ch10 #11 and #12).
- New section built only from v1 ch16 rows #15, #16, #17, #18, #25 and from the v1 ch10 find_booking listing (owner checks). Policy table (v1 Listing 16.1) left to Chapter 10.
- Footnotes ch07-1 to ch07-16.
- Unverified: none.
