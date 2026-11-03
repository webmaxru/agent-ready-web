# Validation: Appendix A — Agent-readiness checklist by role

All sources retrieved 2026-11-02 unless noted. Research-file references (R1–R4, section.fact) point to /home/user/tab/work/agent-ready-web/shared/research/, where the verbatim quotes are.

| # | Claim | Source | Retrieved |
|---|---|---|---|
| 1 | Twelve-item minimum: items map to checks robotsTxt, robotsTxtAiRules, contentSignals, sitemap, markdownNegotiation, linkHeaders (L1–L3) and LH agent-accessibility-tree, cumulative-layout-shift, llms-txt | https://isitagentready.com/llms-full.txt ; https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring (R1 §1, §5) | 2026-11-02 |
| 2 | Level rules quoted (L1 2 of 3 … L3 markdown negotiation) | https://isitagentready.com/llms-full.txt (R1 §1) | 2026-11-02 |
| 3 | vercel.com ships Markdown negotiation, API catalog, OAuth discovery, Agent Skills, ARD and is L1 only because Content Signals missing | R1 headline 5 / FACTS.md headline 5 (scan 2026-11-02; private/analytics/isitagentready-scans-2026-11-02) | 2026-11-02 |
| 4 | Every real site in the Lighthouse runs failed link-name | R1 §5 local runs; Chapter 3 text ('discernible text') | 2026-11-02 |
| 5 | LH webmcp-registered-tools warns above 40 | https://developer.chrome.com/docs/lighthouse/agentic-browsing/registered-webmcp-tools (R1 §5 fact 7) | 2026-11-02 |
| 6 | WebMCP audits need Chrome 150+ and OT or testing flag; N/A otherwise | https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring (R1 §5) | 2026-11-02 |
| 7 | Google: llms.txt and Markdown neither help nor hurt Search | FACTS.md headline 7 (Google Search guidance updated 2026-07-10) | 2026-11-02 |
| 8 | MCP 2026-07-28 stateless; Mcp-Method/Mcp-Name | https://modelcontextprotocol.io/specification/2026-07-28/changelog (R3 1.1–1.5) | 2026-11-02 |
| 9 | CIMD recommended, DCR deprecated, resource indicators required | https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization (R3 2.5, 2.10, 2.14) | 2026-11-02 |
| 10 | Web Bot Auth: verify, don't sign; directory only checked for sites that send requests | https://blog.cloudflare.com/agent-readiness/ (R3 5.20; FACTS R3 #6) | 2026-11-02 |
| 11 | Schema Markup Validator / Rich Results Test usage | Chapter 5; https://validator.schema.org ; https://search.google.com/test/rich-results (both 200 today) | 2026-11-02 |
| 12 | Every other item: taught in the chapter named in its row | Chapters 2–20 as drafted on 2026-11-02 (cross-checked by grep for each term) | 2026-11-02 |
