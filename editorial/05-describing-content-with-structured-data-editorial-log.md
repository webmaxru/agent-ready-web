# Editorial log: Chapter 5, Describing your content with structured data

Writer: W2. All passes on 2 November 2026. Sources and statuses: shared/validation/05-describing-content-with-structured-data.md.

## Pass 1: voice draft
- Planned from OUTLINE.md (Ch5 scope), R2 §3 and §6, R1 §1 (grader checks). Built the layer and tests first (layers/05-structured-data, 6 tests), then wrote around the real files and real output.
- Re-checked primary sources beyond the research: schema.org usage bands on five term pages, the full vocabulary file (domains of makesOffer, offers, provider), Google's intro page (JSON-LD recommendation wording), sd-policies (visibility rule, fake reviews), the vacation rental page (additionalType values, lat/long, BedDetails), jsonld and schema-dts on npm, Lighthouse 13.6.0 source (structured-data manual audit, no ld+json gatherer).
- Voice: "Honestly", "Let's", "In simple words", "Bottomline:", "Please treat", rhetorical questions, first person for judgments only.

## Pass 2: professional-writing-editor (structure, fidelity, slop, role-readability)
- Structure: who-reads-it evidence table before any modelling, so non-coders get the "why" first. Hands-on sections marked, with a pointer where non-coders can skip to.
- Fidelity fixes: usage bands described as "monthly aggregations from Google's web index" (the page's words, not "August 2026"); ClaimReview kept in the June 2025 round but "documentation for most of them" removed on 9 Sep 2025; an unverified claim that "many agents pass ld+json to a model" rewritten as a conditional; a Chapter 3 back-reference about public origins replaced with the reason itself; Google's partner format differences stated (lat/long on the rental, BedDetails, five decimals).
- Code changes found while writing: the vocabulary check caught `provider` on VacationRental (fixed to parentOrganization, told in the text as a first-hand event of this chapter); added `additionalType: Cabin` from Google's suggested values; plural fix in the visible rating line; audit made robust to a second JSON-LD block from the example layer (which is now the "two blocks" teaching point).
- Tables renumbered by order of appearance (5.1 consumers, 5.2 where facts live, 5.3 types, 5.4 graders). One "not X, but Y" removed.

## Pass 3: voice and fidelity recheck
- All five code listings checked as exact substrings of the demo files; Listing 5.3 compared with real output for /cabins/fjellro; the /ask example result (Lyngen Lysthus, score 3) re-run.
- Lint: 0 semicolons in prose, 0 placeholders, 0 em dashes, footnotes ch05-1..26 defined, used and first cited in order, 3 figures exist, one H1.
- Honesty notes kept: no browsing-agent vendor documents reading JSON-LD (plausible, unverified); ReserveAction has no documented consumer; OpenAI feed fact from a snippet; Canel statement is second-hand; NLWeb momentum unclear and spec host failing TLS; graders score nothing here.
