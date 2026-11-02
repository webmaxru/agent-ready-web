# Validation report — The Agent-Ready Web

This file records how the book was checked against the specifications, documentation and tools it describes. Each chapter gets one table: every factual statement, number, quote, listing and status claim, the source it was checked against (URL and retrieval date), and the outcome (confirmed, corrected in the text, or marked unverified). The tables are added as the chapters are written and checked.

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
