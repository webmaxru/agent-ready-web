# Editorial log: Chapter 15, Telling good agents from bad bots

Writer: W5b (continuation of W5), 2 November 2026. Demo layer and tests were built and run before the text, so every listing is code that ran.

## Pass 1: voice draft

- Scope from OUTLINE.md: operator identity for bots and agents. Kept out of scope on purpose and pointed to neighbours: the user agent table and robots policy (Chapter 4), log classification and crawl-to-refer (Chapter 19), x402 and MPP (Chapter 12), user delegation with OAuth (Chapter 14), confirmations and injection (Chapter 16).
- Structure: three questions (software, operator, person), the user agent as a claim, network evidence (IP ranges, reverse+forward DNS), Web Bot Auth (RFC 9421 basics, the draft-01 profile, what a signature proves and what it does not, still-in-flux callout), who signs today, verify-don't-sign decision, hands-on layer (labels, verifier, directory client, DNS, rate limits, wiring, signing test agent), pay per crawl / 402 / RSL, graders, checklist per role, what to watch, Summary.
- Voice from PROFILE.md: first person for judgement ("I'll be honest from the start", "Personally for me"), tutorial "let's", "Please note", "In simple words", "Bottomline", rhetorical questions, short lines between longer ones. No invented anecdotes or numbers: the Nordlys traffic description is generic and every figure comes from Radar, vendor docs or my own runs.
- Demo changes made while drafting (layer 15 existed from W5 but lacked parts of the brief): RateLimit/RateLimit-Policy headers (new ratelimit.js), optional reverse-then-forward DNS for Google claims (new rdns.js, because Chapter 19 already says "Chapter 15 does it in middleware"), a `verified-network` label, draft-01 hardening (ignore Signature-Agent members with parameters, 16-key limit, negative cache, key nbf/exp), layer README. Five new tests (13 total).

## Pass 2: professional-writing-editor (structure, fidelity, slop, role-readability)

- Structure: one idea per section, frequent subheads, a policy table before the code so PMs and security people get the decisions without reading JavaScript. The Hands-on callout tells non-coders where to resume.
- Fidelity: every quote re-read against the fetched draft text (sections 4.4, 5.2, 5.2.1, 5.2.3, 5.4, 6.7, 6.11, App. C.4/C.5), Google's Web Bot Auth guide and Cloudflare's signed-agents page. Live directories of chatgpt.com and agent.bot.goog fetched on 2 Nov 2026 for the key counts, kid style and Cache-Control values used in the text. Removed Microsoft from the IP-file sentence (not in this chapter's sources). Corrected "the hook Chapter 7's layer contract provides" to the demo app's layer contract.
- Slop and tells: removed a triple "not … not … not" in the Summary, two bold "X, not Y" headings in the limits list, a "not an X but" closing line. No "delve/robust/seamless/landscape". "leverage" and "navigate" appear only inside verbatim quotes.
- Role-readability: security (SSRF, replay, Intermediary), PM (what a verified agent gets), legal/commercial (pay per crawl, RSL), analytics (labels in logs), QA (test cases) each have a paragraph and a checklist line.
- Unverified items phrased cautiously in the text: Akamai support (search results only), TollBit (named only).

## Pass 3: voice recheck and fidelity check

- Read against PROFILE.md rates: contractions present, several "Let's", one "In simple words", one "Personally for me", one "Bottomline", two spaced em dashes added as spoken pauses, ", not" contrasts cut from 8 to 4. No semicolons in prose (checked by script). No ":)" used.
- Fidelity: every number, header name, draft number, date and URL checked against shared/validation/15-telling-good-agents-from-bad-bots.md (57 rows). Listings regenerated from the files and diffed.
- Self-checks: zero placeholders, zero semicolons in prose, no raw HTML, footnotes ch15-1 to ch15-27 all defined and used, three figure PNGs exist and were inspected, no forbidden author name anywhere.
