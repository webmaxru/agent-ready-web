# Appendix D: Glossary and resources

This appendix gives the meaning each term has in this book, in one plain sentence or two, and then the places I'd look first when you want to go deeper or check what changed. The chapter in brackets is where a term is taught. Every URL was checked on 2 November 2026.

## Glossary

**A2A (Agent2Agent protocol)**: An open protocol for one AI agent to discover another and hand it a task, described by an *agent card* at `/.well-known/agent-card.json`. (Chapter 6)

**Accessibility tree**: The structure a browser builds from the page for assistive technology: every element's role, *accessible name* and state. Many browser agents read the page through it. (Chapter 3)

**Accessible name**: The text that identifies an element in the *accessibility tree*, such as a button's label. An icon button without one is invisible to a screen reader and to an agent alike. (Chapter 3)

**Agent**: Software driven by a language model that pursues a goal for a person by reading pages, calling tools or clicking through a site. A *crawler* collects content. An agent tries to get something done. (Chapter 1)

**Agent Skills**: Packaged instructions that teach an agent a specific job. A site lists the skills it publishes at `/.well-known/agent-skills/index.json`. (Chapter 8)

**Agentic Browsing category**: The Lighthouse category that audits a page as an agent sees it: the *accessibility tree*, layout stability, *WebMCP* tools, *llms.txt* and the *ARD* manifest. (Chapters 2 and 12)

**API catalog**: A list of a site's APIs and their descriptions at `/.well-known/api-catalog` (RFC 9727). (Chapter 8)

**ARD (Agentic Resource Discovery)**: A proposal for one manifest that lists the MCP servers, agents and skills a domain offers, at `/.well-known/ard.json`. (Chapter 8)

**Content negotiation**: Serving different representations of one URL depending on request headers, mostly Markdown for `Accept: text/markdown`. (Chapter 5)

**Content Signals**: Cloudflare's robots.txt extension, a `Content-Signal` line that says whether content may be used for search, as AI input or for AI training. (Chapter 4)

**Crawler**: A program that fetches pages in bulk to build an index or a dataset. It is governed by robots.txt. (Chapter 4)

**Cumulative Layout Shift (CLS)**: How much a page's content moves while it loads. Moving content makes an agent click the wrong thing. (Chapter 3)

**Declarative tool**: A *WebMCP* tool defined in HTML by adding `toolname` and `tooldescription` to a form. (Chapter 9)

**Delegated access**: Permission a person grants an agent to act for them, limited in scope and time and revocable. OAuth is the standard way to grant it. (Chapter 11)

**Fetcher (user-triggered fetcher)**: A client that loads one page because a person just asked an AI product about it, such as ChatGPT-User. (Chapter 4)

**Grader**: One of the two tools that measure agent-readiness in this book: *isitagentready.com* and the Lighthouse *Agentic Browsing category*. (Chapters 1 and 2)

**Human in the loop**: A design in which a person reviews or approves an agent's step before it takes effect. (Chapters 9 and 11)

**Imperative tool**: A *WebMCP* tool registered from JavaScript with `document.modelContext.registerTool()`. (Chapter 9)

**Indirect prompt injection**: Instructions hidden in content an agent reads, such as a review, that try to make the agent do something its user didn't ask for. (Chapters 7 and 10)

**Input schema**: The JSON Schema that describes a *tool*'s parameters. Models read it to decide how to call the tool. (Chapter 7)

**isitagentready.com**: Cloudflare's free scanner that checks a site's robots.txt, sitemap, headers, well-known files and in-page tools, and assigns a level from 0 to 5. (Chapters 1 and 2)

**JSON-LD**: The format for embedding schema.org structured data in a page as JSON inside a `script` element. (Chapter 5)

**llms.txt**: A proposed Markdown file at `/llms.txt` that gives language models a short summary of a site and links to its most useful content. (Chapter 5)

**MCP (Model Context Protocol)**: An open protocol that lets AI applications connect to tools, resources and prompts on a server. The current revision is dated 2026-07-28. (Chapter 8)

**MCP host, client and server**: The host is the AI application a person uses, the client is the part of it that talks to one server, and the server exposes the tools. (Chapter 8)

**MCP server card**: A JSON description of an MCP server that a client reads before it connects. Its location isn't settled yet. (Chapter 8)

**Origin trial**: A Chrome programme that lets a site use an experimental feature in production for a limited time with a token. WebMCP is in one. (Chapter 9)

**Pay per crawl**, **RSL**, **TDMRep**, **x402**: Ways to charge for or license content and requests. See Appendix C.

**Protected Resource Metadata (PRM)**: A document (RFC 9728) at `/.well-known/oauth-protected-resource` that tells a client which authorization servers protect an API or MCP server. MCP requires it. (Chapter 11)

**Scope**: A named permission in OAuth, such as reading bookings or creating them. (Chapter 11)

**Stateless MCP**: The shape of the 2026-07-28 MCP spec: no handshake and no session id, so any request can go to any server instance. (Chapter 8)

**Step-up authentication**: Asking a user to authenticate again, or more strongly, before a risky action. (Chapter 11)

**Tool**: A named action an agent can call, with a description, an *input schema* and a result. (Chapter 7)

**Tool annotations**: Hints on a tool, such as whether it only reads data. Clients use them to decide when to ask for confirmation. (Chapters 7 and 9)

**Tool poisoning**: Hiding malicious instructions in a tool's description or metadata. (Chapter 10)

**User agent**: The name a client gives itself in the `User-Agent` header. A claim anyone can copy. (Chapter 4)

**Web Bot Auth**: The IETF work on signing bot and agent requests with HTTP Message Signatures, so a site can verify who sent them. (Chapter 4)

**WebMCP**: A proposed browser standard that lets a page register *tools* for agents in the browser, from JavaScript or by annotating forms. (Chapter 9)

**Well-known URI**: A path under `/.well-known/` reserved for site-wide metadata (RFC 8615). (Chapter 8, Appendix B)

## Resources

The book and its code:

- "Tools, Not Clicks", my book on WebMCP, free on the web: https://webmcp.salnikov.no
- The demos repository with Nordlys Cabins, one layer per chapter: https://github.com/webmaxru/agent-ready-web-demos

Measuring:

- isitagentready.com and its full check list: https://isitagentready.com/llms-full.txt
- Lighthouse Agentic Browsing scoring: https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring
- Cloudflare Radar AI Insights (quote every figure with its date): https://radar.cloudflare.com/ai-insights

Specifications and documentation:

- RFC 9309, Robots Exclusion Protocol: https://www.rfc-editor.org/rfc/rfc9309.html
- WAI-ARIA Authoring Practices Guide: https://www.w3.org/WAI/ARIA/apg/
- schema.org and the Schema Markup Validator: https://validator.schema.org
- llms.txt: https://llmstxt.org
- OpenAPI 3.2.1: https://spec.openapis.org/oas/v3.2.1.html
- Model Context Protocol: https://modelcontextprotocol.io/specification/latest
- WebMCP: https://webmachinelearning.github.io/webmcp/ and Chrome's documentation at https://developer.chrome.com/docs/ai/webmcp
- MCP authorization: https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization
- Web Bot Auth working group: https://datatracker.ietf.org/wg/webbotauth/documents/
- OWASP LLM Prompt Injection Prevention Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html
- Universal Commerce Protocol: https://ucp.dev

Tools:

- Playwright, for driving a real browser and reading the accessibility tree: https://playwright.dev
- axe-core, the engine behind the accessibility audit: https://github.com/dequelabs/axe-core
- MCP Inspector, for calling your server's tools by hand and in CI: https://github.com/modelcontextprotocol/inspector

Following the changes:

- IETF Datatracker, for every Internet-Draft in Appendix B and the aipref, webbotauth, oauth and httpapi working groups
- The MCP changelog and SEPs, the WebMCP repository (https://github.com/webmachinelearning/webmcp) and the Agentic AI Foundation (https://aaif.io)
- Lighthouse release notes and the isitagentready check list, both of which changed several times during 2026
- The IANA Well-Known URIs registry: https://www.iana.org/assignments/well-known-uris

The graders tell you what is present, the validators tell you whether it is correct, and only logs and evals tell you whether agents succeed. Put the grader versions next to every score you report.
