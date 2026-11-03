# Editorial log: Chapter 11, Making capabilities discoverable

Writer W3b (continuation of W3). 2026-11-02.

## Pass 1: voice draft
- Plan: the discovery problem (from the agent's side), the limits of discovery files, who reads them today, a map (Table 11.1, Figure 11.1), then the documents in the order an agent meets them: Link header, API catalog, MCP server card, Agent Skills, ARD, OAuth metadata, then the ones not shipped (A2A card, DNS-AID, auth.md, vertical formats), the level ladder (Table 11.2, Figure 11.3), tests, habits, summary.
- All JSON and header examples are real output from the demo (`app.request` at `upto=11`, production origin). The ladder table comes from a real run of the Chapter 2 local checker against servers started at each chapter.
- Voice: first-person judgment where the chapter takes positions (listing MCP in the API catalog, serving Path C plus one mirror, staying at Level 4 instead of publishing an A2A card), tutorial "we" for the build, "Bottomline", "In simple words", "Personally for me", "Please don't".

## Pass 2: substantive edit (professional-writing-editor)
- Fidelity: RFC 8288 is a Proposed Standard, not an Internet Standard. Fixed in prose and Table 11.1.
- Fidelity: Lighthouse reads two discovery documents (llms.txt and ARD) in its Agent Discoverability group, not one. Fixed.
- Fidelity: the 44-site scan facts (eight at Level 4, skill counts of vercel.com, stripe.com, isitagentready.com) now cite the research scan, not the scanner's documentation.
- Fidelity: "some large DNS providers" replaced with the named companies and a footnote, marked UNVERIFIED in validation (search result only).
- Fidelity: the Chapter 18 cross-reference was turned into the author's own recommendation, because Chapter 18 was still being written. Chapter 5 cross-reference trimmed to what Chapter 5 actually says (Guha and NLWeb).
- Fidelity: the Lighthouse environment is stated as "headless Chromium 156" (what the report's user agent says), not a more precise build number.
- Demo fixes found while writing: the ARD entry carried a `capabilities` member that is not an ARD term, replaced with the optional `tags` term. The skill's "NC-XXXXXX" pattern would fail the book-wide placeholder grep, replaced with plain words. Digest output in the chapter updated to the new file.
- Role readability: Note callout for PMs, content and SEO up front, Hands-on callouts before every listing section with a named pickup point, a plain-language reading of the SKILL.md for product and support people, the "keyword research" framing for representative queries.

## Pass 3: voice recheck and fidelity
- No semicolons in prose, no placeholders, no raw HTML, footnotes ch11-1..24 all defined and used, absolute dates only, one "not X, but Y" contrast.
- Every number, name and quote checked against shared/validation/11-making-capabilities-discoverable.md. Listings 11.1-11.5 diffed against the demo files (byte-identical). Tests 20/20 (ch07, ch08, ch11).
