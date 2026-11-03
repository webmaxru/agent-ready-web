# Editorial log: Chapter 9, In-page tools with WebMCP

Writer: W4. Date: 2 November 2026. Sources: shared/FACTS.md, shared/research/R3-action-identity.md §4, /home/user/tab/work/webmcp-book/shared/FACTS.md (validated 2 Nov 2026), R1 §4–§5, and my own tests (Chrome for Testing 156.0.8078.4, Playwright 1.64.1, Lighthouse 13.6.0).

## Pass 1: voice draft
- Built the demo layer first (layers/09-webmcp, 18 tests), then drafted against the listings that actually ran.
- Voice: first person for judgment and the discoveries made while testing ("I tried that first, and it taught me something"), tutorial "we" in walkthroughs, "you" for the reader. Signature phrases used sparingly: "Let's start with", "Let's have a look", "In simple words", "Please note", "Bottomline". Parenthetical asides kept. No ":)" in this chapter.
- Author facts used only from AUTHOR-FACTS.md: member of the W3C WebML CG, co-author of two Chrome WebMCP pages (best-practices and build-tools), author of "Tools, Not Clicks".

## Pass 2: professional-writing-editor (structure, fidelity, slop, role-readability)
- Structure: why → status → two styles → declarative (hands-on) → imperative (hands-on) → lifecycle (hands-on) → detection/polyfills → testing (hands-on) → measuring → roles → summary. Every code-heavy section opens with a Hands-on callout that names where non-coders resume.
- Fidelity changes: Shopify claim narrowed from "storefronts ship by default" to "the three storefronts our scan looked at register the same adapter", plus the single W3C comment presented as a quote, not a measurement. isitagentready pass for Nordlys stated as reasoning (no public scan of a local server possible). The "JSON-LD as answer" finding is labelled an observation of one browser version, with the Chrome docs date and a test that fails when it changes.
- Design change found while writing: start_booking originally navigated after answering. A CDP test showed the agent received an empty result (navigation beat the answer). Rewrote the tool to show a notice with a link instead, updated the test and the text ("prepare, don't commit").
- Same for the search form respondWith: navigating right after resolve lost the answer, so the page now updates the result list in place. Both races are explained in the text.
- Slop check: no "delve/landscape/robust/seamless/unlock", no "Here's the thing", no semicolons in prose, em dashes 13 in ~9,300 words, one "not X, but Y" form. Removed symmetric section endings.
- Role-readability: added "What each role takes from this chapter". Designer content (pseudo-classes, note wording) and content-writer content (descriptions as microcopy) placed in the non-code prose.

## Pass 3: voice recheck + fidelity check against the validation table
- Every number, date, API name and URL checked against shared/validation/09-in-page-tools-with-webmcp.md. Listings checked byte-for-byte against the demo files (9 listings, all match).
- Dates written absolutely. "Today" only where it means 2 November 2026 and is stated as such.
- Lighthouse table matches the raw JSON of my runs (2 Nov 2026).
