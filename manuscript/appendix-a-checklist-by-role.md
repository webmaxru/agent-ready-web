# Appendix A: Agent-readiness checklist by role

Agent-readiness is team work. The robots.txt line belongs to whoever owns SEO, the accessible name of a button to the designer and the developer together, and nobody knows whether any of it worked until analytics looks at the logs. This appendix splits the work of the book into one short checklist per role.

"Ch." is the chapter that teaches an item. "Grader check" names the check that moves when you do it: an isitagentready.com check id (prefixed "IIAR") or a Lighthouse Agentic Browsing audit id (prefixed "LH"). A dash means no grader measures the item, which doesn't make it less important. Appendix B explains each check id.

## Minimum viable agent-readiness

If your team has two weeks and no appetite for drafts that may change, do these twelve things. Together they take a typical site from Level 0 or 1 to Level 3 on isitagentready, and to a clean Lighthouse Agentic Browsing report (apart from the WebMCP audits, which need Chapter 9).

Table A.1 The twelve-item minimum

| # | Item | Ch. | Grader check |
|---|---|---|---|
| 1 | Run both graders on your homepage and one key task page, and save the reports with the date | 2 | All |
| 2 | Fix every failing rule in the accessibility audit on those pages: link names, button names, labels, ARIA validity | 3 | LH `agent-accessibility-tree` |
| 3 | Reserve space for images, ads and late content so nothing moves while the page loads | 3 | LH `cumulative-layout-shift` |
| 4 | Make the key task (book, buy, sign up, contact) work with plain HTML forms, real buttons and server-side validation | 2, 3 | LH `agent-accessibility-tree` |
| 5 | Write a robots.txt that names the AI crawlers and fetchers you have decided about, and blocks private paths | 4 | IIAR `robotsTxt`, `robotsTxtAiRules` |
| 6 | Add a `Content-Signal` line that states your search, AI input and AI training preferences | 4 | IIAR `contentSignals` |
| 7 | Publish a sitemap with honest `lastmod` dates and name it in robots.txt | 5 | IIAR `sitemap` |
| 8 | Add JSON-LD for your main entities (product, place, offer, article, organization) and validate it | 5 | - |
| 9 | Serve Markdown for `Accept: text/markdown`, with `Vary: Accept` | 5 | IIAR `markdownNegotiation` |
| 10 | Send `Link` headers from the homepage to the Markdown alternate and your sitemap or API catalog | 5 | IIAR `linkHeaders` |
| 11 | Publish an llms.txt with an H1, a one-line summary and links to your most useful pages | 5 | LH `llms-txt` |
| 12 | Put both graders in CI and review agent traffic in your logs once a month | 12 | All |

> **Tip:** Items 5, 6 and 7 are often a single setting in your CDN or platform (Chapter 6). In my scans on 2 November 2026, vercel.com shipped Markdown negotiation, an API catalog, OAuth discovery, Agent Skills and an ARD manifest, and still sat at Level 1 because its robots.txt had no `Content-Signal` line.

The minimum leaves out MCP servers, WebMCP tools, OAuth, signatures and commerce, which matter when agents act on your site. The role lists below include them.

## Developers

Front end:

- Use native elements and connected labels, render the key task on the server, and keep the layout stable (Ch. 3, LH `agent-accessibility-tree`, `cumulative-layout-shift`).
- Make complete-action forms declarative WebMCP tools and register imperative tools for the rest, behind feature detection (Ch. 9, LH `webmcp-*`, IIAR `webMcp`).

Back end and full stack:

- Describe the API in OpenAPI, publish an API catalog, return problem details and accept `Idempotency-Key` on every POST that creates something (Ch. 8, IIAR `apiCatalog`).
- Expose site actions as a stateless MCP server on the 2026-07-28 specification (Ch. 8).
- Publish an MCP server card, an Agent Skills index and an ARD manifest generated from one configuration (Ch. 8, IIAR `mcpServerCard`, `agentSkills`, `ard`, LH `ard-schema`).
- Serve Protected Resource Metadata, answer 401 with `WWW-Authenticate`, and validate token audience and scopes on every protected call (Ch. 11, IIAR `oauthProtectedResource`).

## Designers

- Give every interactive element a visible text label, or specify its accessible name in the hand-off, and never rely on placeholder text alone (Ch. 3, LH `agent-accessibility-tree`).
- Make links in cards and image tiles carry descriptive text. Every real site in the Lighthouse runs of Chapter 3 failed this rule (Ch. 3, LH `link-name`).
- Reserve the final space of banners, consent notices and late-loading modules (Ch. 3, LH `cumulative-layout-shift`).
- Design the moment an agent works on a form, and confirmation screens that state exactly what will happen (Ch. 9 and 11).

## Content and SEO

- Decide with legal which AI crawlers you allow where, and write matching robots.txt groups and `Content-Signal` lines (Ch. 4, IIAR `robotsTxtAiRules`, `contentSignals`).
- Keep the sitemap complete, write llms.txt by hand, and check that the Markdown version of each important page reads well on its own (Ch. 5, IIAR `sitemap`, LH `llms-txt`).
- Don't expect llms.txt or Markdown to change Google Search rankings. Google says they don't (Ch. 5).

## Product managers

- List the three to five tasks a person might delegate to an agent on your site, choose the door for each with the decision trees, and check what your platform already ships (Ch. 6).
- Decide which actions need a human confirmation every time, and whether agents may buy at all (Ch. 11).
- Write goals as named checks and user outcomes, not grader levels, and record which checks don't apply to your site and why (Ch. 1, 6 and 12).
- Add agent tasks to the definition of done, and put the standards watch list in the quarterly plan (Ch. 12).

## Architects

- Keep one source of truth for actions that every interface calls, and document where each layer runs: origin, edge or platform (Ch. 6 and 8).
- Design delegated-access scopes around user tasks, use an existing identity provider and require resource indicators (Ch. 11, IIAR `oauthDiscovery`).
- Define a versioning policy for tools and APIs, and keep a record of which draft of each standard you implemented, and when (Ch. 12, Appendix B).

## QA

- Run Lighthouse with `--only-categories=agentic-browsing` in CI on the key templates, with the WebMCP testing flag or a trial token (Ch. 12, all LH audits).
- Complete the key tasks in Playwright through roles and names, test MCP servers with MCP Inspector, and run a small agent eval with real models per release (Ch. 7, 8 and 12).
- Test with WebMCP off, JavaScript off and Markdown requested (Ch. 9 and 12).

## Security

- Threat-model the agent interfaces with the OWASP LLM and Agentic Top 10 lists, and treat all user content as possible indirect prompt injection (Ch. 7 and 10).
- Enforce authorization and confirmations in code, and give each tool the least privilege it needs (Ch. 7, 10 and 11).
- Verify bot identity with signatures, published IP ranges or reverse DNS, never with the user agent alone. Verify Web Bot Auth, but don't publish a signature directory unless your site sends bot traffic (Ch. 4, IIAR `webBotAuth`).
- Log tool calls with `Mcp-Method`, `Mcp-Name`, the client identity and the outcome, without personal data you don't need (Ch. 10 and 12).

## Analytics

- Classify server-log traffic into humans, search crawlers, AI crawlers, user-triggered fetchers and browser agents, and confirm identity before you report a bot by name (Ch. 2, 4 and 12).
- Track AI referrals as their own channel, with crawl-to-referral ratios per AI company (Ch. 12).
- Count agent task outcomes (tool calls, completed bookings, failed attempts, declined confirmations) and report per-check grader results next to them (Ch. 12).

## Using the checklists

Give every item an owner's name and a date, not just a role. Then re-run the graders after each batch and write down which checks moved. When a check doesn't move, the platform or the CDN usually overrides what you changed, which is what the CI checks of Chapter 12 catch.
