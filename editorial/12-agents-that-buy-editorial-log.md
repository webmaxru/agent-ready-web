# Editorial log: Chapter 12, Agents that buy: commerce and payments

Writer: W5. All passes on 2 November 2026. Sources and statuses: shared/validation/12-agents-that-buy.md.

## Pass 1: voice draft
- Planned from OUTLINE.md (Ch12 scope) and the lead's notes in briefs/W5.md, R3 §5–§8, R1 §1 and §3. Built and tested the demo layer first (layers/12-commerce, 9 tests), then wrote the chapter around the real files and real curl output.
- Read primary sources the research marked UNVERIFIED and closed them: the UCP Lodging draft itself (booking index, REST and MCP bindings, cancellation-policy extension) at repository commit 58c7ab9, the UCP overview (profile structure), the ACP repository (versions, /.well-known/acp.json in 2026-04-17), AP2 v0.2 mandate pages, the x402 V2 specification, MPP docs and its IETF draft, Visa TAP, isitagentready's commerce pass criteria.
- Voice: first person for judgment and decisions ("I think about agent commerce as four questions", "I want to be honest about it"), tutorial "let's" in the walkthrough, "you" for the reader, signature phrases ("Let's have a look", "In simple words", "Please note", "Bottomline", "Let's see it in action"), a light aside (acronyms vs cabins in Lofoten), rhetorical questions.

## Pass 2: professional-writing-editor (structure, fidelity, slop, role-readability)
- Structure: business framing (four questions) before any protocol, protocols in one repeated five-fact pattern, one comparison table, a plain decision list for PMs ("Do now / Ask your PSP / Model your data / Join / Wait for / Never do") before the Hands-on section, which tells non-coders where to pick up ("The agent-safe checkout, without any protocol").
- Fidelity fixes: Google's hotel page quote corrected to its exact wording; card-token claim narrowed to Mastercard's own words (search summary, marked); Chrome defences narrowed to what R4 documents; SCA sentence rewritten as general guidance with an EBA source and "ask your PSP"; Instant Checkout pivot kept as press-only.
- Slop: removed a semicolon list, "landscape" heading, one invented-sounding anecdote ("made me rewrite this chapter's plan").
- Demo found a real bug during writing: the checkout POST let form fields override the session's stay. Fixed (form adds who, session decides what) and added a test. The chapter now teaches that rule.

## Pass 3: voice recheck and fidelity check
- Every number, version, header and quote checked against the validation table (61 rows). Totals in the curl output recomputed (3 x 2,200 + 900 = 7,500 NOK = 750000 minor units).
- Listings regenerated from the demo files (byte-identical excerpts). curl outputs re-run after the last code change.
- Lint: no semicolons in prose, no raw HTML, footnotes ch12-1 to ch12-31 all defined and used, figure paths exist, no placeholders, no "vibeprogrammer".
- Words: 8162 (code and command output about 10%).
