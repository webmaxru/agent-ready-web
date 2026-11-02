# Appendix A: Agent-readiness checklist by role

Agent-readiness is team work. The robots.txt line belongs to whoever owns SEO. The accessible name of a button belongs to the designer and the developer together. The OAuth scopes belong to the architect and the product manager. And nobody knows whether any of it worked until analytics looks at the logs. This appendix splits the work of the book into one checklist per role, so each person on a web team can see their part, and where it touches somebody else's.

Every item is one line. "Ch." is the chapter that teaches it. "Grader check" names the check that moves when you do it: an isitagentready.com check id (prefixed "IIAR") or a Lighthouse Agentic Browsing audit id (prefixed "LH"). A dash means no grader measures the item. That's common, and it doesn't make the item any less important. Appendix B, Tables B.8 and B.9, explains each check id.

Start with the one-page list for a small team below. Then give each person their own section.

## Minimum viable agent-readiness

If your team has two weeks, a small budget and no appetite for drafts that may change, do these twelve things. They're all built on settled standards or on files that cost nothing to publish. Together they take a typical site from Level 0 or 1 to Level 3 on isitagentready, and to a clean Lighthouse Agentic Browsing report (apart from the WebMCP audits, which need Chapter 9). The order is the order of the book.

Table A.1 The twelve-item minimum

| # | Item | Ch. | Grader check |
|---|---|---|---|
| 1 | Run both graders on your homepage and one key task page, and save the reports with the date | 2 | All |
| 2 | Fix every failing rule in the accessibility audit on those pages: link names, button names, labels, ARIA validity | 3 | LH `agent-accessibility-tree` |
| 3 | Reserve space for images, ads and late content so nothing moves while the page loads | 3 | LH `cumulative-layout-shift` |
| 4 | Make the key task (book, buy, sign up, contact) work with plain HTML forms, real buttons and server-side validation | 2, 3 | LH `agent-accessibility-tree` |
| 5 | Write a robots.txt that names the AI crawlers and fetchers you have decided about, and blocks private paths | 4 | IIAR `robotsTxt`, `robotsTxtAiRules` |
| 6 | Add a `Content-Signal` line that states your search, AI input and AI training preferences | 4 | IIAR `contentSignals` |
| 7 | Publish a sitemap with honest `lastmod` dates and name it in robots.txt | 6 | IIAR `sitemap` |
| 8 | Add JSON-LD for your main entities (product, place, offer, article, organization) and validate it | 5 | - |
| 9 | Serve Markdown for `Accept: text/markdown`, with `Vary: Accept` | 6 | IIAR `markdownNegotiation` |
| 10 | Send `Link` headers from the homepage to the Markdown alternate and your sitemap or API catalog | 6 | IIAR `linkHeaders` |
| 11 | Publish an llms.txt with an H1, a one-line summary and links to your most useful pages | 6 | LH `llms-txt` |
| 12 | Put both graders in CI and review agent traffic in your logs once a month | 18, 19 | All |

> **Tip:** Items 5, 6 and 7 are often a single setting in your CDN or platform. Before anyone writes code, check what your platform already does (Chapter 13 has a section on exactly that). In my scans for this book, vercel.com shipped Markdown negotiation, an API catalog, OAuth discovery, Agent Skills and an ARD manifest, and still sat at Level 1 for one reason: there was no `Content-Signal` line in its robots.txt.

What the minimum leaves out on purpose: MCP servers, WebMCP tools, OAuth for agents, signatures and commerce protocols. Those are worth doing when agents need to act on your site, not only read it, and they are where Parts 3 and 4 of the book come in. The role checklists below include them.

## Developers

The developer list is the longest, because most layers end in code. I split it into the page (front-end) and the server (back-end and full-stack). On many teams one person does both.

Table A.2 Front-end developer

| Item | Ch. | Grader check |
|---|---|---|
| Use native elements for actions: `button` for actions, `a` with `href` for navigation, never a clickable `div` | 3 | LH `agent-accessibility-tree` |
| Give every form field a visible `label` connected to it, and every icon button an accessible name | 3 | LH `agent-accessibility-tree` |
| Use real `input` types (`date`, `number`, `email`) instead of custom pickers where you can | 2, 3 | LH `agent-accessibility-tree` |
| Render the content and the key task on the server, so it works before and without JavaScript | 2, 6 | - |
| Keep one `h1` per page and a heading outline that matches the content | 3 | LH `agent-accessibility-tree` (`document-title` and related rules) |
| Use a native `dialog` for modals, and move focus into it | 3 | LH `agent-accessibility-tree` (`aria-dialog-name`) |
| Set explicit sizes on images and embeds, and avoid inserting content above what is already visible | 3 | LH `cumulative-layout-shift` |
| Show validation errors as text next to the field, not only as colour | 3 | - |
| Add `toolname` and `tooldescription` to forms that are complete actions, and `toolparamdescription` where a label is not enough | 9 | LH `webmcp-form-coverage`, `webmcp-schema-validity`, IIAR `webMcp` |
| Register imperative WebMCP tools for actions that are not a single form, with an input schema and annotations | 9 | LH `webmcp-registered-tools`, IIAR `webMcp` |
| Keep the number of registered tools per page well under 40 | 9, 10 | LH `webmcp-registered-tools` |
| Unregister tools when the state they depend on goes away (an `AbortSignal` does it) | 9 | - |
| Ship WebMCP behind feature detection or a polyfill, and test the page with WebMCP off | 9 | - |
| Ask for user interaction before a tool completes a risky action | 9, 17 | - |
| Add `link rel="alternate" type="text/markdown"` to pages that have a Markdown twin | 6 | - |
| Keep JSON-LD in sync with the visible content (same price, same availability) | 5 | - |

Table A.3 Back-end and full-stack developer

| Item | Ch. | Grader check |
|---|---|---|
| Serve robots.txt as `text/plain` with status 200, from configuration rather than a hand-edited file | 4 | IIAR `robotsTxt` |
| Generate the sitemap from the same data as the pages | 6 | IIAR `sitemap` |
| Implement Markdown negotiation on `Accept: text/markdown`, return `Content-Type: text/markdown` and `Vary: Accept` | 6 | IIAR `markdownNegotiation` |
| Send `Link` headers with `alternate`, `describedby`, `api-catalog` and (if you publish one) `ard` | 6, 11 | IIAR `linkHeaders` |
| Describe the public API in OpenAPI and serve it | 7 | - |
| Publish `/.well-known/api-catalog` as a linkset that points to the OpenAPI document | 7, 11 | IIAR `apiCatalog` |
| Return errors as problem details (`application/problem+json`) with an actionable `detail` | 7, 10 | - |
| Accept `Idempotency-Key` on every POST that creates or pays for something | 7, 10 | - |
| Send `RateLimit-Policy` and `RateLimit` headers, and `Retry-After` on 429 | 7, 15 | - |
| Put the business logic behind one set of domain functions that the pages, the API, MCP and WebMCP all call | 7, 8, 9 | - |
| Expose site actions as an MCP server on Streamable HTTP, following the 2026-07-28 spec (stateless, no sessions) | 8 | - |
| Read `Mcp-Method` and `Mcp-Name` at the edge for routing, logging and rate limits | 8, 19 | - |
| Publish an MCP server card at the SEP-2127 location, and mirror it where today's scanner looks | 11 | IIAR `mcpServerCard` |
| Publish an Agent Skills index if you have skills to offer | 11 | IIAR `agentSkills` |
| Publish an ARD manifest at `/.well-known/ard.json` and link it | 11 | LH `ard-schema`, IIAR `ard` |
| Serve Protected Resource Metadata for the API and the MCP endpoint, and answer 401 with `WWW-Authenticate: Bearer resource_metadata=…` | 14 | IIAR `oauthProtectedResource` |
| Validate token audience and scopes on every protected call | 14 | - |
| Verify Web Bot Auth signatures in middleware before your bot rules run | 15 | - |
| Send `Deprecation` and `Sunset` headers before you change or remove a tool or endpoint | 20 | - |

## Designers

Designers rarely think of agents as users, but an agent driving a browser meets exactly what the designer drew. Most of this list is good accessibility practice that pays twice.

Table A.4 Designer

| Item | Ch. | Grader check |
|---|---|---|
| Design every interactive element with a visible text label, or specify its accessible name in the hand-off | 3 | LH `agent-accessibility-tree` |
| Prefer native controls over custom widgets. When a custom widget is unavoidable, specify its role and states | 3 | LH `agent-accessibility-tree` |
| Never rely on placeholder text as the only label | 2, 3 | LH `agent-accessibility-tree` |
| Make links in cards and image tiles carry descriptive text (every real site in the Lighthouse runs of Chapter 3 failed this rule) | 2, 3 | LH `agent-accessibility-tree` (`link-name`) |
| Reserve the final space of banners, consent notices and late-loading modules in the layout | 3 | LH `cumulative-layout-shift` |
| Design consent banners that do not block the content an agent came to read | 17 | - |
| Design confirmation screens for risky actions that state exactly what will happen (price, dates, cancellation terms) | 16, 17 | - |
| Show who acted when an agent made a change ("Booked by your assistant on 2 Dec") | 17 | - |
| Keep the order of the visual layout and the source order the same | 3 | - |
| Review the page as the accessibility tree sees it, not only as pixels (Chapter 3 shows how) | 3 | - |

## Content and SEO

Content and SEO people own the first layer agents meet: who is allowed in, and what they find when they arrive.

Table A.5 Content and SEO

| Item | Ch. | Grader check |
|---|---|---|
| Decide, with legal and the business, which AI crawlers and fetchers you allow, for which paths, and write it down | 4 | - |
| Turn that decision into robots.txt groups for named user agents | 4 | IIAR `robotsTxtAiRules` |
| Add `Content-Signal` lines that match the decision | 4 | IIAR `contentSignals` |
| Follow the IETF aipref drafts (`Content-Usage`) and the training-preference token, and add them when they settle | 4, 20 | - |
| Remember that robots.txt is a request, not a lock. Pair it with bot management for paths that matter | 4, 15 | - |
| Keep the sitemap complete and its `lastmod` dates accurate | 6 | IIAR `sitemap` |
| Write llms.txt by hand: an H1, one honest sentence about the site, links to the pages that answer real questions | 6 | LH `llms-txt` |
| Check that the Markdown version of each important page reads well on its own (no navigation noise, no missing tables) | 6 | IIAR `markdownNegotiation` |
| Mark up the main entities with schema.org JSON-LD and validate it with the Schema Markup Validator or Google's rich results test | 5 | - |
| Write descriptions that state facts plainly (capacity, price, policies), because agents quote them | 5, 6 | - |
| Moderate user content (reviews, comments) for hidden instructions as well as spam | 16 | - |
| Do not expect llms.txt or Markdown to change Google Search rankings. Google says they do not | 6 | - |
| Track AI referrals and crawl-to-referral ratios as content KPIs | 19 | - |

## Product managers

The product manager decides which tasks agents should be able to do, and which they should not, and owns the trade-off between reach and control.

Table A.6 Product manager

| Item | Ch. | Grader check |
|---|---|---|
| List the three to five tasks a person might delegate to an agent on your site, and rank them by value | 1, 13 | - |
| For each task, decide the interface: markup only, API, MCP, WebMCP or "let agents click" (Chapter 13's decision trees) | 13 | - |
| Decide which actions need a human confirmation every time, and which never do | 16, 17 | - |
| Check what your platform (CMS, shop system, CDN) already ships before funding custom work | 13 | - |
| Decide your position on AI training, AI answers and search, with legal, and give it to Content and SEO | 4 | IIAR `contentSignals` |
| Decide whether agents may buy, and through which protocol, before anyone builds checkout tools | 12 | IIAR `ucp`, `acp`, `x402` (not scored) |
| Write agent-readiness goals as user outcomes (completed agent bookings, fewer failed attempts), not grader levels | 1, 19 | - |
| Pick which grader checks are irrelevant for your site and record why, so nobody chases points | 1, 13 | - |
| Put a review of the standards watch list in the quarterly plan | 20 | - |
| Add agent tasks to the definition of done for new features | 18 | - |

## Architects

The architect keeps the layers consistent with each other and with the rest of the platform.

Table A.7 Architect

| Item | Ch. | Grader check |
|---|---|---|
| Keep one source of truth for actions: domain functions that every interface (pages, API, MCP, WebMCP) calls | 7, 8, 9 | - |
| Choose where each layer runs: origin, CDN edge or platform feature, and document it | 4, 6, 13 | - |
| Design the scopes for delegated access around user tasks, not around endpoints | 14 | - |
| Use an existing identity provider as the authorization server, with metadata at a well-known path | 14 | IIAR `oauthDiscovery` |
| Support CIMD for MCP clients, keep pre-registration for known partners and avoid new reliance on DCR | 14 | - |
| Require resource indicators and check token audience in every resource server | 14 | - |
| Plan for enterprise customers who will ask for Enterprise-Managed Authorization (ID-JAG) | 14 | - |
| Make the MCP server stateless, so it scales behind a load balancer like the rest of the API | 8 | - |
| Decide which discovery documents you publish, and keep them generated from one configuration | 11 | IIAR `apiCatalog`, `mcpServerCard`, `agentSkills`, LH `ard-schema` |
| Define a versioning policy for tools and APIs, including deprecation and sunset dates | 20 | - |
| Keep a record of which draft of each standard you implemented, and when | 20 | - |
| Evaluate A2A only if you run an agent of your own that others should call | 11, 13 | IIAR `a2aAgentCard` (opt-in) |

## QA

QA turns agent-readiness from a launch project into a property of every release.

Table A.8 QA

| Item | Ch. | Grader check |
|---|---|---|
| Run Lighthouse with `--only-categories=agentic-browsing` in CI on the key templates, in Chrome 150 or later | 18 | All LH audits |
| Run the WebMCP audits with the testing flag or an origin trial token, otherwise they show N/A | 18 | LH `webmcp-*` |
| Call the isitagentready API (or a local re-implementation) on staging after each deploy | 18 | All IIAR checks |
| Add Playwright tests that complete the key tasks through the accessibility tree (roles and names, not CSS selectors) | 18 | - |
| Test MCP servers with MCP Inspector, and assert tool lists and schemas in CI | 18 | - |
| Run a small agent eval with real models on the key tasks, and track the success rate per release | 10, 18 | - |
| Set regression budgets: no new accessibility failures, no new CLS, no tool schema errors | 18 | LH `agent-accessibility-tree`, `cumulative-layout-shift`, `webmcp-schema-validity` |
| Test with WebMCP off, JavaScript off and Markdown requested, as well as the default | 6, 9, 18 | - |
| Re-run the graders when a grader itself changes version, and note the version in the report | 18, 20 | - |

## Security

Security owns the layer where agent-readiness can go wrong in ways that matter: content that hijacks agents, tools that do too much, and bots pretending to be agents.

Table A.9 Security

| Item | Ch. | Grader check |
|---|---|---|
| Threat-model the agent interfaces with the OWASP LLM and Agentic Top 10 lists as prompts | 16 | - |
| Treat every piece of user-generated content as possible indirect prompt injection | 16 | - |
| Require confirmation outside the agent's control for payments, cancellations and changes to personal data | 16, 17 | - |
| Give each tool the least privilege it needs, and separate read-only tools from tools that change state | 10, 16 | - |
| Pin tool descriptions in review, and treat a changed description like a changed permission | 16 | - |
| Keep a strict Content-Security-Policy so injected scripts cannot register tools | 9, 16 | - |
| Verify bot identity with signatures, published IP ranges or reverse DNS, never with the user agent alone | 15 | - |
| Verify Web Bot Auth signatures, but do not publish a signature directory unless your site sends bot traffic | 15 | IIAR `webBotAuth` (informational) |
| Rate-limit per verified identity and per token, not only per IP address | 15 | - |
| Log tool calls with `Mcp-Method`, `Mcp-Name`, the client identity and the outcome, without logging personal data you do not need | 16, 17, 19 | - |
| Review OAuth consent screens and scopes for over-broad grants | 14 | - |

## Analytics

Analytics answers the question everybody else will ask: did any of this change anything?

Table A.10 Analytics

| Item | Ch. | Grader check |
|---|---|---|
| Classify server-log traffic into humans, search crawlers, AI crawlers, user-triggered fetchers and browser agents | 19 | - |
| Use signatures and published IP ranges to confirm identity before you report a bot by name | 15, 19 | - |
| Track referrals from AI products as their own channel | 19 | - |
| Compute crawl-to-referral ratios per AI company for your site, and compare them with Cloudflare Radar's | 19 | - |
| Count agent task outcomes: tool calls, completed bookings, failed attempts, confirmations declined | 19 | - |
| Report per-check grader results over time, next to the outcome metrics | 1, 19 | All |
| Give each role one KPI it owns (Chapter 19 suggests one per role) | 19 | - |
| Date every adoption or traffic figure you share, because these numbers change weekly | 1, 19 | - |

## Using the checklists

Two habits make these lists work. First, give every item an owner's name and a date, not just a role. A checklist with "Design" in the owner column is a checklist nobody does. Second, re-run the graders after each batch of items and write down which checks moved. When a check does not move, that is information too: it usually means the platform or the CDN overrides what you changed, which is exactly the kind of thing Chapter 18 teaches you to catch in CI.

The book's own web edition is the worked example. Chapter 20's case study lists what it publishes and how it scored with both graders on 2 November 2026.
