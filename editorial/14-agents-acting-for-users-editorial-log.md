# Editorial log: Chapter 14, Agents acting for users: OAuth and delegated access

Writer: W5. All passes on 2 November 2026. Sources and statuses: shared/validation/14-agents-acting-for-users.md.

## Pass 1: voice draft
- Planned from OUTLINE.md (Ch14 scope) and R3 §2. Built the layer first on top of W3's layer 08 (its `mcpAuth` hook and tool registry), then the command-line agent, then wrote around real output.
- Read the MCP 2026-07-28 authorization pages in full (overview, server discovery, client registration, security considerations), the Streamable HTTP page (Mcp-Name), RFC 9728, the EMA blog post, OpenAI's and Claude's connector docs, auth.md, and datatracker for draft revisions.
- Voice: four-word framing for PMs ("who, to whom, what, until when"), "In simple words" analogy (keys to some rooms), first-person recommendations, tutorial "Let's have a look", "Please note", a recommendation list for architects.

## Pass 2: professional-writing-editor
- Structure: business problem and shortcuts first, roles, then the discovery chain step by step, registration, audience, scopes; Hands-on afterwards with a non-coder skip line; build-vs-buy and enterprise after the code.
- Fidelity: RFC 9728 §3.3 nuance about the root document stated honestly; test renamed after noticing it proved signature integrity, not the audience check; claims about client behaviour limited to what vendor docs say; DCR described as deprecated in MCP while still supported by hosts.
- Demo change during the pass: the agent now rejects metadata whose `resource` differs from the MCP URL (RFC 9728 §3.3).
- Slop: removed six semicolons, no hype words.

## Pass 3: voice recheck and fidelity check
- Each quote rechecked against the saved page text in shared/research/w5/. Footnotes ch14-1, 3, 5 to 22 all defined and used (the main authorization page is one footnote).
- Listings regenerated from files, outputs from real runs (401 header, PRM document, CLI run against port 3000). The AS metadata block is shortened to the relevant fields and says so.
- Words: 7831 (code and output about 13%).
