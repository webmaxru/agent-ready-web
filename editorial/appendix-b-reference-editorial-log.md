# Editorial log: Appendix B

- Pass 1 (draft): 10 tables (well-known paths, root files, robots.txt lines, HTTP headers, link relations, markup hooks, DNS, isitagentready checks, Lighthouse audits, standards master list) + status vocabulary + what Nordlys serves.
- Fact re-checks during pass 1: all RFC dates and statuses re-fetched from rfc-editor.org JSON (corrected RFC 9457 to Aug 2023); OAuth 2.1 latest draft is -17 (31 Oct 2026), noted that MCP cites -13; Web Bot Auth `tag` value `web-bot-auth` read in draft-01.
- Pass 2 (edit): split long sentences, made the Content-Signal vs Content-Usage distinction explicit, removed one semicolon.
- Reconciliation with chapters: Chapter 4 cites an individual draft for /.well-known/ai.txt and the expired draft-romm Content Signals draft, so the ai.txt sentence and the Content-Signal rows were corrected; auth.md mapped to Chapters 11 and 14 after Chapter 11 landed.
- "What Nordlys serves" rewritten from a measured run of the new checker (chapters/appendix-b-reference) against Nordlys with all layers, instead of from the plan.
- Pass 3 (voice): first person kept for "the reference I wanted on my desk"; reference tables left neutral on purpose.
