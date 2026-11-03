# Appendix D: Resources and tools

Everything in this appendix was open in my browser while I wrote the book, and every URL was checked on 2 November 2026. The list is grouped by the layers of the book, so you can jump to the part you work on. In each group the specification comes first, then the official documentation, then the tools. Library versions are the latest releases on npm on that date. They will have moved by the time you read this, and that is fine: the point of the versions is to tell you what the book's code was tested with, not what you should install.

This field changes every week. When you want to know whether something in the book is still true, the sources in the last section ("Following the changes") are where I would look first.

## The companion book and the code

- **"Tools, Not Clicks: Building Agent-Ready Websites with WebMCP"**, my previous book, goes deep on one layer of this one: in-page tools with WebMCP, from the first tool to production. Its free web edition is at https://webmcp.salnikov.no.
- **The demos repository** for this book, with Nordlys Cabins, one layer per chapter, the standalone chapter demos and their tests: https://github.com/webmaxru/agent-ready-web-demos. The README explains how to run the site as it stands after any chapter (`npm start -- --upto=N`).
- **The WebMCP agent skill** I maintain, for coding agents that build WebMCP tools: https://github.com/webmaxru/ai-native-dev.

## Measuring agent-readiness

- **isitagentready.com**, Cloudflare's scanner, with levels 0 to 5: https://isitagentready.com. The full list of checks and the level rules, written for agents but very readable for people, is at https://isitagentready.com/llms-full.txt. It also has an API and an MCP server, described there.
- **"Introducing the Agent Readiness score"**, the Cloudflare blog post that explains why the scanner exists and what it checks: https://blog.cloudflare.com/agent-readiness/.
- **Lighthouse Agentic Browsing scoring**, the documentation for the category and each audit: https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring.
- **Lighthouse source and releases**, where the audit ids, thresholds and changes per version live: https://github.com/GoogleChrome/lighthouse. npm package `lighthouse` 13.6.0. Run the category with `npx lighthouse <url> --only-categories=agentic-browsing` in Chrome 150 or later.
- **PageSpeed Insights**, which runs the Agentic Browsing category without installing anything (since Lighthouse 13.4.1): https://pagespeed.web.dev.
- **Chrome's developer toolkit for agent-ready websites**, the post that ties the Lighthouse category, DevTools and WebMCP together: https://developer.chrome.com/blog/agent-ready-toolkit.
- **Cloudflare Radar AI Insights**, the public dataset on AI crawler traffic, crawl-to-referral ratios and adoption of agent standards across the top domains: https://radar.cloudflare.com/ai-insights. It blocks scripted requests, so open it in a browser. Every figure on it is a snapshot, so quote it with the date.

## Access: robots.txt, crawlers and usage preferences (Chapter 4)

- **RFC 9309, Robots Exclusion Protocol**: https://www.rfc-editor.org/rfc/rfc9309.html.
- **Google's common crawlers**, including Google-Extended and the planned support for the aipref training token: https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers.
- **OpenAI's crawler overview** (GPTBot, OAI-SearchBot, ChatGPT-User): https://developers.openai.com/api/docs/bots. Anthropic, Perplexity, Apple, Amazon, Meta and Mistral document theirs too, and Chapter 4 cites each page.
- **Content Signals**, Cloudflare's robots.txt policy text and generator: https://contentsignals.org.
- **IETF AI Preferences (aipref) working group documents**, with the current vocabulary and attachment drafts: https://datatracker.ietf.org/wg/aipref/documents/.
- **TDM Reservation Protocol (TDMRep)**: https://w3c-cg.github.io/tdm-reservation-protocol/spec/.
- **RSL (Really Simple Licensing)**: https://rslstandard.org.
- Library: `robots-parser` 3.0.1, a small robots.txt parser for Node.js, used by the Chapter 4 tests.

## Perception: semantic HTML and the accessibility tree (Chapters 2 and 3)

- **WAI-ARIA 1.2**, the Recommendation: https://www.w3.org/TR/wai-aria-1.2/.
- **ARIA Authoring Practices Guide**, with tested patterns for every widget you might be tempted to build yourself: https://www.w3.org/WAI/ARIA/apg/.
- **axe-core**, the accessibility engine behind the `agent-accessibility-tree` audit: https://github.com/dequelabs/axe-core. npm `axe-core` 4.14.0 and `@axe-core/playwright` 4.14.0.
- **Playwright**, for driving a real browser and reading the accessibility tree in tests: https://playwright.dev. npm `playwright` and `@playwright/test` 1.64.1. The book's measurements used the Chromium 156.0.8078.4 build bundled with it.

## Content: structured data, Markdown, llms.txt and sitemaps (Chapters 5 and 6)

- **schema.org**, the vocabulary: https://schema.org.
- **Schema Markup Validator**, which checks any schema.org markup against the vocabulary: https://validator.schema.org.
- **Google Rich Results Test**, which checks the subset Google uses for search features: https://search.google.com/test/rich-results.
- **JSON-LD Playground**, for seeing how a JSON-LD block expands: https://json-ld.org/playground/.
- Libraries: `schema-dts` 2.1.0 (TypeScript types for schema.org) and `jsonld` 9.0.0 (JSON-LD processing).
- **llms.txt**, the proposal (now v2): https://llmstxt.org.
- **Sitemaps protocol**: https://www.sitemaps.org/protocol.html.
- **Cloudflare Markdown for Agents**, an edge implementation of Markdown negotiation worth reading even if you implement it yourself: https://developers.cloudflare.com/fundamentals/reference/markdown-for-agents/.
- Library: `turndown` 7.2.4, the HTML-to-Markdown converter used in Chapter 6.
- **NLWeb**, the open-source natural-language endpoint built on schema.org and feeds: https://github.com/nlweb-ai/NLWeb.

## Action: APIs, MCP and WebMCP (Chapters 7 to 10)

- **OpenAPI Specification 3.2.1**: https://spec.openapis.org/oas/v3.2.1.html.
- **Arazzo**, for describing multi-step API workflows: https://spec.openapis.org/arazzo/latest.html.
- **RFC 9727, api-catalog**: https://www.rfc-editor.org/rfc/rfc9727.html.
- **RFC 9457, Problem Details for HTTP APIs**: https://www.rfc-editor.org/rfc/rfc9457.html.
- **Model Context Protocol specification**, current revision 2026-07-28: https://modelcontextprotocol.io/specification/latest.
- **MCP TypeScript SDK**: https://github.com/modelcontextprotocol/typescript-sdk. The book uses the v2 line, npm `@modelcontextprotocol/server` 2.4.0. The older monolithic package `@modelcontextprotocol/sdk` (1.32.2) is the v1 line that many tutorials still show.
- **MCP Inspector**, for calling your server's tools by hand and in CI: https://github.com/modelcontextprotocol/inspector. npm `@modelcontextprotocol/inspector` 2.13.0.
- **WebMCP specification** (W3C Web Machine Learning Community Group draft): https://webmachinelearning.github.io/webmcp/, with the explainer and issues at https://github.com/webmachinelearning/webmcp.
- **Chrome's WebMCP documentation**, including the declarative form attributes and the origin trial: https://developer.chrome.com/docs/ai/webmcp.
- WebMCP polyfill packages used in Chapter 9: `@mcp-b/webmcp-polyfill` and `@mcp-b/global`, both 6.0.3.
- Library: `zod` 4.6.7, used for tool input schemas in the demos. The demo server runs on `hono` 4.13.16. `express` 5.3.0 works the same way if that is your stack.

## Discovery (Chapter 11)

- **IANA Well-Known URIs registry**, the place to check whether a path is registered: https://www.iana.org/assignments/well-known-uris.
- **IANA Link Relations registry**: https://www.iana.org/assignments/link-relations.
- **MCP Server Cards, SEP-2127**: https://modelcontextprotocol.io/seps/2127-mcp-server-cards.
- **Agentic Resource Discovery (ARD) specification**: https://agenticresourcediscovery.org.
- **A2A specification**: https://a2a-protocol.org/latest/specification/.

## Commerce (Chapter 12)

- **Universal Commerce Protocol (UCP)**: https://ucp.dev, and Google's page on UCP for hotel booking in AI Mode: https://developers.google.com/hotels/ucp.
- **Agentic Commerce Protocol (ACP)**: https://www.agenticcommerce.dev.
- **AP2, Agent Payments Protocol**: https://ap2-protocol.org.
- **x402**: https://docs.x402.org. Seller middleware such as `@x402/express` 2.29.0.
- **Visa Trusted Agent Protocol**: https://developer.visa.com/docs/trusted-agent-protocol.

## Trust: delegated access and agent identity (Chapters 14 and 15)

- **MCP authorization**, the section of the spec every MCP server with user data must follow: https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization.
- **RFC 9728, OAuth 2.0 Protected Resource Metadata**: https://www.rfc-editor.org/rfc/rfc9728.html.
- **OAuth 2.1 draft**: https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/.
- **Client ID Metadata Document draft**: https://datatracker.ietf.org/doc/draft-ietf-oauth-client-id-metadata-document/.
- **IETF Web Bot Auth working group documents**: https://datatracker.ietf.org/wg/webbotauth/documents/.
- **RFC 9421, HTTP Message Signatures**: https://www.rfc-editor.org/rfc/rfc9421.html. npm `http-message-signatures` 1.0.6 for verifying them in Node.js.
- **Cloudflare verified bots**, including the Direct and Intermediary labels: https://developers.cloudflare.com/bots/concepts/bot/verified-bots/.
- **Cloudflare pay per crawl**: https://blog.cloudflare.com/introducing-pay-per-crawl/.

## Security and privacy (Chapters 16 and 17)

- **OWASP Top 10 for LLM Applications**: https://genai.owasp.org/llm-top-10/.
- **OWASP LLM Prompt Injection Prevention Cheat Sheet**, a practical list of where injected instructions come from and what to do: https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html.
- **promptfoo's OWASP Agentic red-team preset**, for testing your own agent-facing endpoints against the OWASP agentic risks: https://www.promptfoo.dev/docs/red-team/owasp-agentic-ai/.
- **EU AI Act Service Desk**, the European Commission's site with the official timeline of obligations: https://ai-act-service-desk.ec.europa.eu.

## Testing and measuring (Chapters 18 and 19)

- **Playwright MCP**, which gives any MCP client a browser that works from accessibility snapshots. Chapter 18 uses it to explore a failing test the way an accessibility-tree agent sees the page: https://github.com/microsoft/playwright-mcp. npm `@playwright/mcp` 0.0.84.
- **Chrome DevTools MCP** (DevTools for agents), including the `lighthouse_audit` tool: https://github.com/ChromeDevTools/chrome-devtools-mcp. npm `chrome-devtools-mcp` 1.12.0.
- **Model Context Tool Inspector**, a Chrome extension that lists and calls the WebMCP tools a page registers: https://chromewebstore.google.com/detail/gbpdfapgefenggkahomfgkhfehlcenpd.
- **Lighthouse**, **isitagentready.com** and **Cloudflare Radar**, as listed under "Measuring agent-readiness" above.

## Versioning (Chapter 20)

- **RFC 9745, the Deprecation header**: https://www.rfc-editor.org/rfc/rfc9745.html.
- **RFC 8594, the Sunset header**: https://www.rfc-editor.org/rfc/rfc8594.html.

## Which instrument answers which question

The tools above overlap, and teams waste time running the wrong one. Table D.1 is the shortcut I use.

Table D.1 Questions and the instrument that answers them

| Question | Instrument | Chapter |
|---|---|---|
| Which agent-related files and headers does my site serve? | isitagentready.com, or the Appendix B checker in the demos repository | 2, Appendix B |
| Can an agent in a browser understand and operate this page? | Lighthouse Agentic Browsing category | 2, 3, 18 |
| Which element exactly breaks the accessibility tree? | axe-core through Playwright, or the Lighthouse report details | 3 |
| Is my structured data valid, and does it match what Google uses? | Schema Markup Validator, then the Rich Results Test | 5 |
| Do my MCP tools list and run correctly? | MCP Inspector | 8, 18 |
| Do real models call my tools correctly? | A small agent eval (Chapter 10's eval harness) | 10, 18 |
| Which bots and agents actually visit, and what do they do? | Your server logs, classified (Chapter 19's tool), with Radar for context | 19 |
| Is a request really from the agent it claims to be? | Signature verification with an RFC 9421 library, or your CDN's verified-bot data | 15 |
| Has a standard I depend on changed? | The sources under "Following the changes" below | 20 |

The pattern behind the table: the graders tell you what is present, the validators tell you whether it is correct, and only logs and evals tell you whether agents succeed. A site needs all three kinds of answer, and no single tool gives more than one.

## Following the changes

These are the places where the standards in this book actually move. A monthly look at them is enough for most teams, and Chapter 20 turns them into a watch list with an owner per item.

- **IETF Datatracker**: every Internet-Draft in Appendix B has a page there with its revision history and expiry date. The working group pages for aipref, webbotauth, oauth and httpapi are the ones to follow.
- **The MCP specification changelog and SEPs**, linked from https://modelcontextprotocol.io/specification/latest.
- **The WebMCP repository and the Web Machine Learning Community Group**: https://github.com/webmachinelearning/webmcp and https://www.w3.org/community/webmachinelearning/. I am a member of the Community Group, and its issues are where the API is decided.
- **The Agentic AI Foundation**, home of MCP and A2A: https://aaif.io.
- **Lighthouse release notes** in the repository above: each version can add, change or regroup audits in the Agentic Browsing category, which is still marked as under development.
- **The isitagentready.com check list** at its llms-full.txt, which changed several times during 2026.
- **The IANA registries** above: a new well-known registration is often the first public sign that a proposal is getting serious.

> **Tip:** Put the two grader versions (Lighthouse release and the date of your isitagentready scan) next to every score you report. A score without the grader version is a number nobody can reproduce a month later.
