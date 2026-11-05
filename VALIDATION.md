# Validation report — Agent-Ready Websites in Action

This file records how the book was checked against the specifications, documentation and tools it describes. Each chapter gets one table: every factual statement, number, quote, listing and status claim, the source it was checked against (URL and retrieval date), and the outcome (confirmed, corrected in the text, or marked unverified). The tables are added as the chapters are written and checked.

## Version 2.0.0 (checked 2 to 5 November 2026)

Every number, date, version, quote and URL in the book has a row in its chapter's table, with the source and retrieval date. The "v1 row" column names the row a claim was first checked under at tag `v1.0.0` of this repository, for traceability. Claims that could not be verified were removed from the text together with their rows and footnotes, so no row in these tables is UNVERIFIED. Rows marked OPINION are the author's judgment, recommendations or the results of the author's own searches, and the text says so where it uses them.

| Table | Rows | Verified | Unverified | Opinion |
| --- | --- | --- | --- | --- |
| `validation/01-the-agent-ready-web.md` | 53 | 52 | 0 | 1 |
| `validation/02-your-first-agent-ready-page.md` | 39 | 38 | 0 | 1 |
| `validation/03-how-agents-see-a-page.md` | 43 | 40 | 0 | 2 |
| `validation/04-who-gets-in.md` | 86 | 79 | 0 | 7 |
| `validation/05-content-agents-can-read.md` | 42 | 40 | 0 | 2 |
| `validation/06-choosing-the-right-agent-interface.md` | 39 | 36 | 0 | 3 |
| `validation/07-designing-tools-agents-can-use.md` | 35 | 32 | 0 | 3 |
| `validation/08-server-side-tools-and-discovery.md` | 93 | 89 | 0 | 4 |
| `validation/09-in-page-tools-with-webmcp.md` | 56 | 52 | 0 | 4 |
| `validation/10-security-for-agent-facing-sites.md` | 36 | 34 | 0 | 2 |
| `validation/11-agents-acting-for-users.md` | 135 | 128 | 0 | 7 |
| `validation/12-testing-and-measuring-in-production.md` | 130 | 122 | 0 | 8 |
| `validation/appendix-a-checklist-by-role.md` | 11 | 0 | 0 | 0 |
| `validation/appendix-b-reference.md` | 54 | 22 | 0 | 0 |
| `validation/appendix-c-pay-per-crawl-and-licensing.md` | 30 | 28 | 0 | 2 |
| `validation/appendix-d-glossary-and-resources.md` | 28 | 0 | 0 | 0 |
| **Total** | **910** | **792** | **0** | **46** |

Appendix A, B and D rows marked "as in v1" point to the chapter rows they summarise.

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

None. A claim that could not be checked against a primary source was removed from the book.

## Chapter tables

One section per manuscript file, in `Book.txt` order.
