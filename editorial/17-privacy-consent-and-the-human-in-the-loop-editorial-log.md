# Editorial log: Chapter 17, Privacy, consent and the human in the loop

Writers: W6 (pass 1, demo layer, figures), W6b (passes 2 and 3, validation). All passes on 2 November 2026. Sources and statuses: shared/validation/17-privacy-consent-and-the-human-in-the-loop.md.

## Pass 1: voice draft (W6)
- Planned from OUTLINE.md (Chapter 17 scope) and R4 §2, with R3 for MCP elicitation and the WebMCP FACTS for requestUserInteraction. Built `layers/17-consent/` first (records, outbox, activity page and export, retention, request_booking with multi round-trip requests), then wrote around captured output.
- Voice: the not-legal-advice note said once, first-person recommendations ("I recommend this split", "Here is the split I would propose"), "Let's", "Please note", tables a privacy officer can take to a meeting.

## Pass 2: professional-writing-editor (W6b)
- Structure kept: roles, GDPR principles with a data inventory, the three meanings of consent, cookie banners, the AI Act, the human in the loop per interface, transparency to the guest, retention, a role-by-role split, tests.
- Role-readability: each role has its own paragraph in "What each role takes away", and the human-in-the-loop decision is a table a product manager can own.
- Fidelity: law-firm and secondary summaries are named as such (AEPD, ICO, Digital Omnibus), and the regulation number carries the "not checked against EUR-Lex" caveat. The AI Act scope statement is framed as the author's reading.
- Fixed one logic slip in the WebMCP section: the three options were described as "all three" page confirmations, although the first one (the hint) leaves the asking to the agent. It now says so.
- Mechanical: zero semicolons in prose, no placeholders, no raw HTML, 18 footnotes defined and used, both image paths exist, and the banned old account name appears nowhere.

## Pass 3: voice recheck and fidelity check (W6b)
- Rechecked on the live 2026-07-28 MCP pages: the MRTR breaking-change sentence, the requestState rules (attacker-controlled, HMAC or AEAD, reject on failure), the form-mode and URL-mode MUSTs and the URL-mode accept wording. The SDK helper names (`inputRequired`, `elicitUrl`, `acceptedContent`) and "applies no integrity protection by default" were checked in the installed 2.4.0 package.
- Tool-to-layer mapping in the data inventory checked against the layer folders.
- Listings: 17.9 identical to the file, 17.2, 17.3, 17.5, 17.7 contiguous excerpts. Tests rerun 7/7 on Node 22.23.2 and 24.22.1, and the test line now names both.
- Figures 17.1 and 17.2 inspected as PNG: readable, no clipping.
- Words: 7,740.
