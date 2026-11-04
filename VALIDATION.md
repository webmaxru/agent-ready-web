# Validation report — Agent-Ready Websites in Action

This file records how the book was checked against the specifications, documentation and tools it describes. Each chapter gets one table: every factual statement, number, quote, listing and status claim, the source it was checked against (URL and retrieval date), and the outcome (confirmed, corrected in the text, or marked unverified). The tables are added as the chapters are written and checked.

## Second edition (v2.0.0, draft of 4 November 2026)

The second edition condenses the 20 chapters of v1.0.0 into 12. No claim was added without a row: every kept number, date, version, quote and URL carries its v1 row (the "v1 row" column names it, for example `v1 ch15 #12`), with the v1 status, source and retrieval date unchanged. Rows for v1 passages that were cut stay in the tables for traceability. New rows exist for the section "Two ways to buy" in Chapter 11, reused from the verified validation of *Tools, Not Clicks* v2.1.0 (UCP specification 2026-08-25, Shopify's Checkout WebMCP documentation and three live `/.well-known/ucp` fetches, all on 4 November 2026), and for linking text that rests on existing rows (marked as such). The v1 tables stay on the `v1.0.0` tag.

| Table | Rows | Verified | Unverified | Opinion |
| --- | --- | --- | --- | --- |
| `validation/01-the-agent-ready-web.md` | 53 | 52 | 0 | 1 |
| `validation/02-your-first-agent-ready-page.md` | 39 | 38 | 0 | 1 |
| `validation/03-how-agents-see-a-page.md` | 43 | 40 | 0 | 2 |
| `validation/04-who-gets-in.md` | 87 | 79 | 1 | 7 |
| `validation/05-content-agents-can-read.md` | 44 | 40 | 2 | 2 |
| `validation/06-choosing-the-right-agent-interface.md` | 40 | 36 | 1 | 3 |
| `validation/07-designing-tools-agents-can-use.md` | 35 | 32 | 0 | 3 |
| `validation/08-server-side-tools-and-discovery.md` | 93 | 89 | 0 | 4 |
| `validation/09-in-page-tools-with-webmcp.md` | 56 | 52 | 0 | 4 |
| `validation/10-security-for-agent-facing-sites.md` | 36 | 34 | 0 | 2 |
| `validation/11-agents-acting-for-users.md` | 139 | 128 | 3 | 8 |
| `validation/12-testing-and-measuring-in-production.md` | 132 | 122 | 2 | 8 |
| `validation/appendix-a-checklist-by-role.md` | 11 | 0 | 0 | 0 |
| `validation/appendix-b-reference.md` | 54 | 22 | 0 | 0 |
| `validation/appendix-c-pay-per-crawl-and-licensing.md` | 30 | 27 | 1 | 2 |
| `validation/appendix-d-glossary-and-resources.md` | 28 | 0 | 0 | 0 |

Rows marked UNVERIFIED are hedged in the text where the text still uses them. Appendix A, B and D rows marked "as in v1" point to the chapter rows they summarise.

## Sources

The primary sources, as named in the author's brief of 2 November 2026:

- isitagentready.com, its checks and its agent skills: <https://isitagentready.com/>
- Cloudflare's agent-readiness post: <https://blog.cloudflare.com/agent-readiness/>
- Cloudflare Radar, adoption of AI agent standards: <https://radar.cloudflare.com/ai-insights#adoption-of-ai-agent-standards>
- Chrome's agent-ready toolkit: <https://developer.chrome.com/blog/agent-ready-toolkit>
- Lighthouse Agentic browsing scoring: <https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring>

The specifications and documentation behind each layer (HTML and ARIA, schema.org, llms.txt, robots.txt and Content Signals, the Model Context Protocol, WebMCP, OAuth, Web Bot Auth, ARD, Agent Skills and the others) are listed in each chapter's table with the version or date that was read.

## How a chapter is checked

1. Every claim about a standard is compared with the current text of the standard or its editor's draft, and the draft date is recorded.
2. Every number (adoption figures, scores, version numbers) is traced to the page that publishes it, with the retrieval date. A number without a source is removed or marked unverified in the text.
3. Every listing is byte-identical to a file in [webmaxru/agent-ready-web-demos](https://github.com/webmaxru/agent-ready-web-demos), whose tests run in that repository's CI, or is marked as an excerpt.
4. Every scanner result shown in the book (isitagentready.com, Lighthouse) is re-run on the demo it describes, and the tool version is recorded.
5. The web edition is checked with the same tools: see [AGENT-READY.md](AGENT-READY.md).

## Unverified

Items that could not be checked are listed here with the chapter they appear in, and are marked as unverified in the text.

## Chapter tables

One section per manuscript file, in `Book.txt` order.


## Per-chapter tables (v1.0.0, checked 2 November 2026)

| File | Table | Rows | Verified | Unverified | Opinion |
| --- | --- | --- | --- | --- | --- |
| [front-matter.md](validation/front-matter.md) | Front matter (preface, about this book, about the author) | 14 | 13 | 0 | 1 |
| [01-the-agent-ready-web.md](validation/01-the-agent-ready-web.md) | Chapter 1: The agent-ready web | 62 | 61 | 0 | 1 |
| [02-your-first-agent-ready-page.md](validation/02-your-first-agent-ready-page.md) | Chapter 2: Your first agent-ready page | 42 | 35 | 0 | 0 |
| [03-how-agents-see-a-page.md](validation/03-how-agents-see-a-page.md) | Chapter 3: How agents see a page | 45 | 37 | 1 | 2 |
| [04-who-gets-in.md](validation/04-who-gets-in.md) | Chapter 4: Who gets in: robots.txt, AI crawlers and content signals | 53 | 48 | 2 | 3 |
| [05-describing-content-with-structured-data.md](validation/05-describing-content-with-structured-data.md) | Chapter 5: Describing your content with structured data | 32 | 29 | 2 | 1 |
| [06-content-agents-can-read.md](validation/06-content-agents-can-read.md) | Chapter 6: Content agents can read | 29 | 27 | 0 | 2 |
| [07-apis-agents-can-use.md](validation/07-apis-agents-can-use.md) | Chapter 7: APIs agents can use | 28 | 26 | 0 | 2 |
| [08-server-side-tools-with-mcp.md](validation/08-server-side-tools-with-mcp.md) | Chapter 8: Server-side tools with the Model Context Protocol | 35 | 35 | 0 | 0 |
| [09-in-page-tools-with-webmcp.md](validation/09-in-page-tools-with-webmcp.md) | Chapter 9: In-page tools with WebMCP | 59 | 56 | 0 | 3 |
| [10-designing-tools-agents-can-use.md](validation/10-designing-tools-agents-can-use.md) | Chapter 10: Designing tools agents can actually use | 30 | 28 | 0 | 2 |
| [11-making-capabilities-discoverable.md](validation/11-making-capabilities-discoverable.md) | Chapter 11: Making capabilities discoverable | 47 | 43 | 2 | 2 |
| [12-agents-that-buy.md](validation/12-agents-that-buy.md) | Chapter 12: Agents that buy: commerce and payments | 61 | 58 | 2 | 2 |
| [13-choosing-the-right-agent-interface.md](validation/13-choosing-the-right-agent-interface.md) | Chapter 13: Choosing the right agent interface | 43 | 39 | 1 | 3 |
| [14-agents-acting-for-users.md](validation/14-agents-acting-for-users.md) | Chapter 14: Agents acting for users: OAuth and delegated access | 39 | 37 | 0 | 2 |
| [15-telling-good-agents-from-bad-bots.md](validation/15-telling-good-agents-from-bad-bots.md) | Chapter 15: Telling good agents from bad bots | 57 | 51 | 2 | 4 |
| [16-security-for-agent-facing-sites.md](validation/16-security-for-agent-facing-sites.md) | Chapter 16: Security for agent-facing sites | 36 | 34 | 0 | 2 |
| [17-privacy-consent-and-the-human-in-the-loop.md](validation/17-privacy-consent-and-the-human-in-the-loop.md) | Chapter 17: Privacy, consent and the human in the loop | 31 | 26 | 2 | 3 |
| [18-testing-agent-readiness.md](validation/18-testing-agent-readiness.md) | Chapter 18: Testing agent-readiness | 50 | 48 | 1 | 1 |
| [19-measuring-agent-traffic.md](validation/19-measuring-agent-traffic.md) | Chapter 19: Measuring agent traffic and outcomes | 42 | 37 | 2 | 4 |
| [20-evolving-with-the-standards.md](validation/20-evolving-with-the-standards.md) | Chapter 20: Evolving with the standards | 40 | 37 | 1 | 3 |
| [appendix-a-checklist-by-role.md](validation/appendix-a-checklist-by-role.md) | Validation: Appendix A — Agent-readiness checklist by role | 12 | 0 | 0 | 0 |
| [appendix-b-reference.md](validation/appendix-b-reference.md) | Validation: Appendix B — Files, headers and standards at a glance | 49 | 0 | 0 | 0 |
| [appendix-c-glossary.md](validation/appendix-c-glossary.md) | Validation: Appendix C — Glossary | 21 | 0 | 0 | 0 |
| [appendix-d-resources.md](validation/appendix-d-resources.md) | Validation: Appendix D — Resources and tools | 72 | 0 | 0 | 0 |
| **Total** | | **1029** | **805** | **18** | **43** |

Every UNVERIFIED row is also phrased cautiously in the chapter text. Row counts include the demo and figure rows at the end of each table.
