# Editorial log: Chapter 16, Security for agent-facing sites

Writers: W6 (pass 1, demo layer, figures), W6b (passes 2 and 3, validation). All passes on 2 November 2026. Sources and statuses: shared/validation/16-security-for-agent-facing-sites.md.

## Pass 1: voice draft (W6)
- Planned from OUTLINE.md (Chapter 16 scope), R4 §1–§3 and the WebMCP FACTS security notes. Built `layers/16-security/` and the standalone hidden-text scanner first, then wrote around real output.
- Voice: first-person judgment ("I find it useful to think of two roles", "I use them as a lens"), "Please note", "In simple words", "Bottomline", rhetorical questions, one author label stated as such ("agent CSRF").

## Pass 2: professional-writing-editor (W6b)
- Structure: problem, what vendors defend, the split of responsibilities (Table 16.1), threat model, then the four building blocks (clean and label, authorization in code, supply chain, logging), then tests and the honest scorecard. Kept as drafted, it reads in the order a security review runs.
- Role-readability: the Hands-on callout gives non-coders the outcome in one sentence and names the pick-up section. Content and SEO people get their own rule ("Do not hide text yourself"), product managers get the planning-meeting sentence on the Rule of Two, designers the confirmation screens.
- Fidelity: vendor attack-success numbers are framed as vendor-internal and not comparable. Secondary sources are named where the primary refused a fetch (OpenAI via Fortune, Meta via Oso).
- Mechanical: zero semicolons in prose, no AI-tell words found, no placeholders, no raw HTML, all 27 footnotes defined and used, both image paths exist, and the banned old account name appears nowhere.
- Changed: Listing 16.1 refreshed, because `policy.js` gained four tools (find_booking, list_my_bookings, cancel_my_booking, check_booking_request) after the draft. The test line now names both Node versions the suite was run on.

## Pass 3: voice recheck and fidelity check (W6b)
- Rechecked on the live pages: MCP -32020 HeaderMismatch and the Mcp-Name rule, -32602 "Unknown tool", "MUST consider tool annotations to be untrusted unless they come from trusted servers", and the OWASP ASI names. All other quotes matched R4's saved text.
- Listings: 16.1 identical to the file, 16.2, 16.4, 16.5 and 16.7 to 16.11 contiguous excerpts, 16.3 identical to a fresh run of `scan-page.mjs`. Listings 16.6 and 16.12 are captured output, consistent with the provenance strings in `untrusted.js`.
- Tests rerun: ch16-security 6/6 (Node 22.23.2 and 24.22.1), scan-page 3/3 (Playwright 1.64.1, Chromium 156.0.8078.4).
- Figures 16.1 and 16.2 inspected as PNG: readable labels, no clipping.
- Words: 9,190 (code and output about 15%).
