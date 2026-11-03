# Editorial log: Chapter 13, Choosing the right agent interface

Writer: W4b (continuation of W4), 2 November 2026. Sources: shared/FACTS.md, research R1 §1, §4, §5 and cross-cutting, R2 §1, §6, R3 §1, §3, §6, the WebMCP FACTS, my own isitagentready.com scans (allbirds.com, brooklinen.com, kith.com) and GitHub API reads (WordPress/mcp-adapter). Neighbour chapters read by headings and their "What the graders see" sections: 1, 2, 6, 7, 8, 9, 10, 12, 14. Chapter 11 did not exist yet when this chapter was written, so it is referenced only for its outline scope (discovery files, the level ladder).

## Pass 1: voice draft

- Structure: eight doors, five questions, Table 13.1 with one subsection per door, the shared-rules section (Figure 13.2), platform check (Shopify, WordPress, CDNs, API gateways), four site-type decision trees (Figure 13.3), Nordlys walked through the tree, the staged plan (Table 13.2) and where Nordlys stops, the hands-on decision helper, what not to build, revisiting, roles, Summary.
- Voice per PROFILE.md and SPEC: first person for judgment, "Let's have a look", "Please note", "In simple words", "Bottomline", "of course", one ":)", rhetorical framing kept low. No invented anecdotes: the only first-person events are my scans and reading of the demos.
- Demo first: the W4 decision helper existed (6 tests). Fixed data errors before quoting it (Link headers belong to Chapter 6, Shopify covers the API side too, Cloudflare plan list), added the content-site "Also do" line and one test (7 pass), fixed the README test command.

## Pass 2: professional-writing-editor

- Fidelity: the first draft said every Nordlys door calls "the booking service". The code says otherwise: the store holds the rules, the Chapter 7 service wraps it for API and MCP, WebMCP endpoints and commerce call the store. Rewrote the section, its title ("One set of rules behind every door") and the Figure 13.2 caption to match the code.
- Removed a claim that the WordPress MCP Adapter 0.7.1 release notes mention the 2026-07-28 MCP revision (not in the v0.7.1 notes). Removed Perplexity Comet from the browsing-agent list (no primary source in the research).
- Shopify: my scans contradicted a generalisation (Markdown negotiation passed only on allbirds.com), so the text says so per store. The WebMCP adapter claim stays attributed to the research observation, because the scanner's WebMCP check timed out on all three stores, which the text reports.
- Cut 9 of 14 ", not X" contrasts. Dropped a fourth figure (a ladder that repeated Table 13.2), keeping three. Moved "Walking the tree with Nordlys" next to the decision trees so the Hands-on callout's "continue with What not to build" is true.
- Role check: every section before the hands-on reads without code. The Hands-on callout names the section to continue with.

## Pass 3: voice + fidelity

- Every number, date, version and quoted phrase checked against shared/validation/13-choosing-the-right-agent-interface.md (43 rows). Footnote titles re-checked against the live page titles on 2 November 2026 (9 corrected). Radar and help.openai.com answer our direct fetch with a bot challenge or 403, so those rows rely on R1 and R3.
- Overstatement fixed: "the Shopify stores pass almost everything except this one line" became "have everything Level 2 asks for except this one line".
- Self-checks: no placeholders, no semicolons in prose, no raw HTML, 25 footnotes all prefixed ch13- and all used, 3 images exist, Listings 13.1 and 13.2 byte-identical excerpts of plan.mjs, Listing 13.3 is real program output, no forbidden account name.
