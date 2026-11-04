# Chapter 6: Choosing the right agent interface

This chapter covers

- The eight ways an agent can reach your site, from plain markup to agents clicking through your pages
- Comparing them on cost, reliability, reach, control and maintenance
- Checking what your platform already ships before you build anything
- Decision trees for content sites, booking sites, SaaS applications and online shops
- A staged adoption plan mapped to the isitagentready.com levels and the Lighthouse Agentic Browsing audits, and the doors to leave closed

Part 1 made Nordlys Cabins readable: semantic markup, a clear policy for who gets in, structured data, Markdown and llms.txt. Every agent that comes to read now gets what it needs. Part 2 is about agents that come to act, and before we build a single tool, we have to decide which doors to open at all.

Nordlys will end up with more doors for machines than most real sites will ever need, because a book has to show every layer. Your site is not a book. You have a backlog, a budget and a team that already maintains one front end, maybe two. When I talk to web teams about this topic, the first question is almost never "how do I build an MCP server?". It is "which of these do we actually need, and in what order?"

This chapter answers it, and Chapters 7, 8 and 9 then build the doors that Nordlys chooses here.

> **Note:** This is a planning chapter, and most of it is written for the whole team. The one hands-on section near the end shows a small decision helper in `chapters/13-choosing-the-right-agent-interface/` of the demos repository. It holds the decision trees from this chapter as data and prints a plan for your type of site.[^ch06-1] The demos keep the first edition's folder and layer numbers, and the table in About this book maps them to the chapters of this edition.

## Eight doors into one site

Let's start with an inventory. In November 2026, an agent that wants something from your site can come in through one of eight doors. Some of them you build, some you configure, and one of them you get whether you want it or not.

1. **Markup.** Semantic HTML, a clean accessibility tree and structured data (Chapters 2, 3 and 5). Every agent that reads or browses your pages uses it, whether it knows the word "agent-ready" or not.
2. **Content formats.** Markdown through content negotiation, llms.txt, feeds and sitemaps (Chapter 5). These serve the same information as your pages, just cheaper to read.
3. **A public API.** HTTP endpoints described with OpenAPI and listed in an API catalog (Chapter 8). The oldest machine door on the web, and still the most portable one.
4. **An MCP server.** Your site's actions as tools on a remote Model Context Protocol server (Chapter 8). Assistants such as Claude, ChatGPT and Copilot Studio connect to it once somebody adds it.
5. **WebMCP tools.** Tools declared in the page itself, on your forms or in JavaScript (Chapter 9). An agent working inside the user's browser calls them in the user's session.
6. **An A2A agent.** An Agent Card at `/.well-known/agent-card.json` and an endpoint that speaks the Agent2Agent protocol. This door only exists if your site runs an agent of its own that other agents can hand work to.
7. **An NLWeb-style endpoint.** A natural-language question endpoint (`/ask`, and the same thing as an MCP tool) answered from your structured data.
8. **Agents clicking.** No door at all, technically. A browsing agent opens your pages, reads them and clicks your buttons the way a person would.

Please note that these are not alternatives in the strict sense. Markup is under everything: a WebMCP form tool is built on the same `<form>` that Chapter 3 made accessible, and an MCP tool calls the same booking service as the API. In our case, all the Nordlys doors end up in the same business rules. That's the most important architectural decision in this whole chapter, and we'll come back to it.

Figure 6.1 puts the eight doors on one line. On the left, the agent does the work of figuring out your site. On the right, your site declares exactly what can be done and how.

![Figure 6.1 — The eight agent interfaces arranged from "the agent figures it out" to "the site declares it". Agents clicking and plain markup need the least from the site team and give it the least control. Content formats, NLWeb-style endpoints, WebMCP tools, a public API, an MCP server and an A2A agent each ask for more work and give back more control over what an agent can do. All of them should call the same domain logic underneath.](images/figure-6-1.png)

The line is not a ranking. Every step to the right costs you some building and maintenance, and pays you back in control and reliability.

## Five questions to ask of every door

To compare doors that look so different, I use five deliberately boring questions, the ones a product manager or an architect asks about any new interface:

- **Cost.** What does it take to build the door and to run it, including design, content, review, hosting and support?
- **Reliability.** How often does an agent's task actually succeed through it? That is mostly about how much the agent has to guess.
- **Reach.** Which agents can use it today, in November 2026? A door no agent product calls yet is a bet, and bets are fine as long as you know you are making one.
- **Control.** What do you decide: which actions exist, who may call them, with what limits, and where a human must confirm?
- **Maintenance.** What breaks when you change your site, and what breaks when the standard changes?

A sixth question is not a property of the door: does your platform already give it to you? It changes the answer more often than any rating, so it gets its own section.

## Rating the doors

Table 6.1 is my rating of the eight doors for a typical small or medium site. Please treat the ratings as my informed opinion, and disagree with me on your own evidence.

Table 6.1 The eight agent interfaces compared (as of November 2026)

| Door | Cost to build and run | Reliability for tasks | Reach today | Control for the site | Maintenance |
|---|---|---|---|---|---|
| Agents clicking | None to build | Low | Every browsing agent | Low | Hidden: every redesign |
| Markup | Low (mostly existing work) | Medium | Every reading and browsing agent | Low to medium | Low |
| Content formats | Low | High for reading | Growing, uneven | Medium | Low |
| Public API | Medium | High | Frameworks, gateways, developer agents | High | Medium |
| MCP server | Medium | High | Assistants, once someone adds it | High | Medium, the spec moves |
| WebMCP tools | Low to medium | High in supporting browsers | Chrome and Edge origin trials | High | Medium, the spec moves |
| A2A agent | High | Depends on your agent | Agent platforms | High | High |
| NLWeb-style endpoint | Medium | Medium | Hard to tell | Medium | Medium |

### Agents clicking

You get this door for free, and that is both its charm and its problem. Browsing agents drive a real browser, read the page and click. Your site does nothing special for them, so the cost is zero and the reach is every browsing agent there is. Reliability is where it hurts: the agent has to work out which element is the date picker and whether the booking actually went through (Chapter 2 showed a form with no labels). It is also expensive for the agent: on Cloudflare Radar in the week to 2 November 2026, AI bots received HTML 73.2% of the time and Markdown less than 0.1%, and serving Markdown instead of HTML cut the median response to 7.9% of its original size.[^ch06-2]

Control is low, and maintenance is hidden, which is the worst kind. Every redesign can break an agent's way through your site, and nobody on your team will know until the logs (Chapter 12) or a confused customer tell you. Bottomline: clicking is the baseline you cannot turn off and should not try to. The rest of this chapter is about how much you add on top of it.

### Markup and content formats

Semantic HTML, labels and a well-formed accessibility tree are the cheapest layer in the book, because most of the work is the same work you do for accessibility anyway. Chrome's own toolkit post says agents "rely on the accessibility tree" as their "primary data model".[^ch06-3] Good markup makes clicking far more reliable, but the agent still has to plan its way through your pages, so I rate reliability as medium. Please note one honest limit on structured data: Google's guidance for its generative AI features, updated 10 July 2026, says that no special schema.org markup is needed for them.[^ch06-4] It is not a ranking trick, and nobody should sell it to your manager as one.

Markdown, llms.txt and feeds are cheap to add, and for reading tasks they are the most reliable door of all. Reach is growing and uneven. Some retrieval agents send `Accept: text/markdown` first, many don't, and Google says publishing llms.txt or special Markdown files "will neither harm nor help your site's visibility or rankings in Google Search".[^ch06-4] Of the 115,468 domains in Cloudflare Radar's agent-readiness dataset on 2 November 2026, 4.3% answered Markdown negotiation.[^ch06-5] Maintenance is low as long as the Markdown is generated from the same source as the HTML, which is how Chapter 5 built it.

### A public API

A well-described HTTP API is the most portable action door on the web. Every agent framework can call one, and the big platforms now turn an OpenAPI description into tools for you: Azure API Management can expose REST operations as an MCP server, AWS Bedrock AgentCore Gateway converts OpenAPI into MCP tools, Copilot Studio takes an OpenAPI file directly, and Google's Agent Development Kit generates tools from OpenAPI 3.x.[^ch06-6] Reliability is high, because the operations are explicit and the errors can be precise (Chapter 8 shows problem details and idempotency keys).

Reach deserves a careful sentence. An API is reachable by developers, frameworks and gateways, which is a lot of reach. It is not something a consumer assistant discovers and calls by itself. One of the few consumer paths that did exactly that is closing: OpenAI is retiring Custom GPTs on 11 December 2026, and their OpenAPI-based actions do not carry over to the new MCP-based plugins.[^ch06-7]

Cost is medium if you already have an API, which many booking and SaaS sites do, and high if you don't. Control is high. Maintenance is medium: versions, deprecations and an API catalog file (Chapter 8) are real work, but it is work API teams already know how to do.

### An MCP server

A remote MCP server is the door that assistants use. In November 2026 the hosts that connect to one include Claude, ChatGPT and Codex, Copilot Studio, VS Code and Gemini Enterprise. Reliability is high for the same reason as with an API, and the tool design craft of Chapter 7 pushes it higher.

Reach comes with a catch. In every one of those hosts, somebody has to add your server: a user pastes a URL, an admin approves a connector or a developer edits a configuration file. There is no global directory that assistants consult on their own, and the discovery files of Chapter 8 are still settling. Adoption is accordingly small: on 2 November 2026 Radar found an MCP Server Card on 0.61% of the domains it scanned.[^ch06-5]

Control is high. Maintenance is medium with a warning attached: the specification changed shape in its 2026-07-28 revision (stateless requests, no sessions), the TypeScript SDK moved to a new major version, and a server written from 2025 tutorials needed real changes this year.

### WebMCP tools

WebMCP is the door inside the page. A declarative tool is a few attributes on a form you already have, and imperative tools reuse the JavaScript your page already runs, so the cost is low to medium. Reliability is high in a browser that supports it, and the user's session, cookies and consent come along for free, which no server-side door can offer. Control is high, because the page decides when the tools exist.

Reach is the honest weak spot. As of November 2026, WebMCP runs in a Chrome origin trial that started in Chrome 149 and is extended to Chrome 162, and Edge has its own origin trial.[^ch06-8] WebKit's standards position is "oppose" and Mozilla's is "neutral".[^ch06-9] Radar counted WebMCP on 1.42% of scanned domains, 1,643 of them, and most of those are online shops whose platform added the tools for them.[^ch06-5] Maintenance is medium, because the draft will change again before it is final. Chapter 9 has the details.

### An A2A agent

A2A, the Agent2Agent protocol, is for one agent handing work to another. Version 1.0.0 shipped on 12 March 2026, and in August 2026 A2A joined the Agentic AI Foundation next to MCP.[^ch06-10] The discovery file is an Agent Card at `/.well-known/agent-card.json`.

A2A is not a way to expose your booking form or your product catalog. It only makes sense if your site runs an agent of its own with judgment worth delegating to, and building and operating such an agent is the most expensive item in Table 6.1 by a wide margin.

### An NLWeb-style endpoint

NLWeb, which Microsoft announced in May 2025 and which R.V. Guha (the person behind RSS, RDF and schema.org) conceived, lets agents ask a site a question in natural language and get schema.org-shaped JSON back. Every NLWeb instance is also an MCP server.[^ch06-11] The reference implementation ingests the structured data and feeds you already publish into a vector store and answers with a language model.

The idea is elegant, but the reference repository has no tagged releases, its last push was on 11 August 2026, and Cloudflare's NLWeb template in AI Search is still in public preview.[^ch06-12] I found no evidence that any major assistant discovers or calls NLWeb endpoints automatically, and no 2026 adoption numbers either, hence "hard to tell" in Table 6.1. If you already run a search index over a large content collection, an NLWeb-style endpoint is a cheap experiment. If you don't, structured data and Markdown give agents the same content without a model in the middle.

## One set of rules behind every door

Before we turn ratings into decisions, there is one rule that makes every later decision cheaper: whatever doors you open, they should all call the same business rules. The rules of the business (search, prices, availability and the 14-day free cancellation policy) live in one place, the store module of the app. The human booking form calls it. Chapter 8 wraps it in a booking service that adds what machine clients need on top, stable output shapes and idempotent booking, and both the public API and the MCP tools call that service. The small JSON endpoints behind the WebMCP tools of Chapter 9 call the store too, and so does the commerce layer of Chapter 11. So when the cancellation policy changes, it changes in one place, and every door tells every agent the same thing.

Figure 6.2 shows the shape. The doors are thin. Each one translates between a protocol and the shared rules, and adds what only that door can add: a schema for MCP, a form annotation for WebMCP, an OpenAPI description for the API.

![Figure 6.2 — One set of business rules behind every door. The human pages, the public API, the MCP server, the WebMCP tools and the commerce layer of Nordlys Cabins are thin adapters over the same store, partly through the booking service from Chapter 8, so prices, availability and the cancellation policy live in one place. Markup and content formats describe the same data for readers.](images/figure-6-2.png)

For planning, this means two things. The cost of an extra door is mostly definitions and tests, not logic, and the tool design work of Chapter 7 applies to every door at once. And the order of doors matters less than where your rules live: if your business logic is buried in page controllers, the first agent door you open will be expensive, whichever one it is. Pulling the rules into one module is the real first step, and it pays off for your human front end too.

> **Warning:** A door that bypasses the shared rules is where trouble starts. A WebMCP tool that scrapes its own page, or an MCP tool that writes to the database directly, will drift from what the human interface does, and Chapter 10 shows how such drift becomes a security problem.

## Check what your platform already does

Here is the sixth question from earlier, and the one that most often changes the plan. Before you build any door, find out which ones your platform has already opened for you. The adoption data makes the point better than any argument. Platforms move agent-readiness on the web, individual sites much less.

### Shopify

Shopify is the clearest example in November 2026. On the storefronts we looked at during the research for this book, the platform serves a WebMCP adapter with tools such as `search_catalog`, `add_to_cart` and `proceed_to_checkout`, a Universal Commerce Protocol profile at `/.well-known/ucp`, and OAuth discovery metadata.[^ch06-13] The merchants didn't build any of it.

You can see the effect in Cloudflare Radar. In its e-commerce category on 2 November 2026, WebMCP showed up on 928 of 18,927 domains (about 4.9%) and UCP on 4,181. Across all scanned domains, WebMCP was at 1.42%.[^ch06-5] One platform decision did more for in-page tools than every hand-built WebMCP integration together.

Let's have a look at what that means for the graders. I scanned three Shopify stores (allbirds.com, brooklinen.com and kith.com) with isitagentready.com on 2 November 2026. All three passed robots.txt, sitemap, the AI bot rules check, OAuth discovery, OAuth Protected Resource and UCP. Allbirds also passed Markdown negotiation. And all three sat at Level 1, "Basic Web Presence".[^ch06-14] The reason is one missing line. Level 2 needs Content Signals in robots.txt, and none of the three had it. The scanner's WebMCP check could not finish on any of them ("Browser session timed out"), which is a reminder that a heavy storefront can defeat a headless check even when the tools are there.

So for a Shopify merchant, the plan is mostly configuration and content: robots.txt policy, product data quality, structured data and the accessibility of the theme. The action doors are the platform's job.

### WordPress

WordPress 6.9 (December 2025) introduced the Abilities API, a registry where core, plugins and themes describe what they can do, with input and output schemas.[^ch06-15] The official MCP Adapter makes registered abilities available to MCP clients, and you install it as a plugin. Its current version, 0.7.1, was released on 16 October 2026.[^ch06-16] Nothing is exposed until a site owner installs it, which is more work than on Shopify and also more control.

### Edges and API gateways

If your site sits behind Cloudflare, several Part 1 layers are zone settings. A managed robots.txt with a Content Signals line has been available since September 2025, and Cloudflare said at the time that it was already enabled on more than 3.8 million domains.[^ch06-17] Markdown for Agents is a beta feature at no extra cost on the Pro, Business and Enterprise plans.[^ch06-18] Cloudflare folded signed agents into its verified bots program on 1 July 2026, and AWS WAF added Web Bot Auth support in November 2025.[^ch06-19] If your edge verifies signed agents, the verification work of Chapter 4 becomes a policy decision instead of code.

If you already run an API behind Azure API Management or plan to use AWS Bedrock AgentCore Gateway, an MCP door may be a configuration step on top of the OpenAPI description you already have.[^ch06-6] The tool design advice from Chapter 7 still applies, because the generated tool names and descriptions come straight from your `operationId` and `summary` fields, and Chapter 7's eval shows what happens when they are left as they are.

> **Tip:** Ask your platform vendors four short questions before planning any build: Do you serve Markdown to agents? Do you publish any agent tools (WebMCP or MCP) for my site, and can I switch them off? What do you put in my robots.txt and `/.well-known/`? Do you verify signed bots and agents? Write the answers into your plan, with the date, because they change.

## Decision trees for four kinds of site

Now let's turn the ratings into decisions. Figure 6.3 is the general tree. It asks four questions in order: what your platform already gives you, whether agents need to act on your site or only read it, whether the action needs the user's session in the browser, and whether you run an agent of your own.

![Figure 6.3 — The decision tree. Start with markup and content formats for every site, then check what the platform ships. If agents only need to read, stop after content formats. If they need to act, add an API, then WebMCP when the action belongs to the user's browser session and an MCP server when assistants should reach it without a browser. Add an A2A agent only if you run an agent of your own. Agents clicking remain possible on every path.](images/figure-6-3.png)

The tree shows the usual order, and your site type can swap two steps, as the online shop below does. Real sites cluster into a few types, and for each type the same answers come up again and again. Here are four, which are also the data behind the decision helper in the hands-on section.

### A content site

Publishers, documentation sites, blogs and most marketing sites belong here. Agents come to read: training crawlers, search and answer engines, and user-triggered fetchers that pull one page because somebody asked about it.

- **Build:** markup and content formats. Semantic HTML and structured data, a robots.txt that states your policy (Chapter 4), Markdown through content negotiation and an llms.txt that links to your important pages (Chapter 5).
- **Consider later:** an NLWeb-style endpoint if you have a large archive and already run a search index over it, and an MCP server if your content is something people want to query from an assistant (documentation sites are the strongest case).
- **Skip:** WebMCP, because there are few actions to offer, and A2A, because there is no agent of yours to talk to.

A content site can reach Level 3 on isitagentready.com without a single tool, and that is a good place to stop. In my scan of 44 well-known sites on 2 November 2026, none of them sat at Level 2 or Level 3 at all, so a content site at Level 3 would be ahead of most of the web.[^ch06-20]

### A booking site

This is Nordlys, and also restaurants, clinics, salons, tours and any site where a guest picks a time slot and commits. Agents come to read and to act, and the action has consequences: money, a reservation, a personal schedule.

- **Build:** markup, content formats, a public API, WebMCP tools, an MCP server, in that order. The API and its shared rules come first because every other action door depends on them. WebMCP comes before MCP for a public booking flow because the guest's own session, consent and confirmation come along with it.
- **Consider later:** an A2A agent, if you ever build a concierge worth delegating to. And the commerce standards of Chapter 11, especially the UCP Lodging draft from 25 September 2026, which is written for exactly this kind of business.[^ch06-21]
- **Skip:** an NLWeb-style endpoint. Nordlys has six cabins. A natural-language search over six items is not worth an endpoint, and `search_cabins` already does the job.

Booking sites need the trust layers of Part 3 more than any other type, because the actions are real. Delegated access and confirmations (Chapters 10 and 11) are not optional extras here.

### A SaaS application

Here the product is behind a login, and the users are customers who want their assistant to work with their data in your product: create a ticket, pull a report, update a record.

- **Build:** markup for the public pages, a public API, an MCP server, then WebMCP. Most SaaS products already have an API, so the first real step is usually the MCP server with OAuth (Chapters 8 and 11). WebMCP comes after it for workflows that happen inside the product's UI with the user watching.
- **Consider later:** A2A if your product has its own agent (many SaaS products do by now), and content formats for your documentation and help center.
- **Skip:** an NLWeb-style endpoint. Your users ask your product, not your marketing pages.

For SaaS, the MCP server is the door that matters most, because the assistants your customers already use at work are MCP hosts.

### An online shop

Shops have the most crowded field of standards (Appendix B) and the strongest platform effect.

- **Build:** markup, content formats, WebMCP tools and an API, unless your platform provides them. Product data quality is part of the markup here: names, prices, availability and variants that a machine can read without guessing.
- **Consider later:** an MCP server and an A2A agent, and the commerce protocols once your payment provider supports them.
- **Skip:** nothing on principle, but check the platform list first. On Shopify, the WebMCP tools, the commerce profile and the OAuth metadata already exist, so your own work is the markup, the content and the robots.txt policy.

Please note how the order differs from the booking site. A shop puts WebMCP before an API because a cart and a checkout live in the browser session, and because, as the Radar numbers show, that is where the platforms went first.

## Walking the tree with Nordlys

Let's put the tree to work on our own example. This is the decision that the rest of Part 2 builds on.

**What does the platform give us?** Nothing. Nordlys is a custom application on a small Node.js server, so every door is ours to build. A real cabin-rental business of this size would often sit on a booking platform, and the first step would be to ask that vendor the four platform questions.

**Do agents need to act, or only to read?** Both. Guests ask an assistant about cabins with a sauna near the fjord, which is reading, and then they want to check dates and book, which is acting. So Nordlys goes past the content stage.

**Does the action belong in the user's browser session?** For a guest who is already on the site, yes. The booking form, the guest's sign-in and the final confirmation all live in the page, so WebMCP is the natural door for them. Chapter 9 keeps the final step in the guest's hands on purpose: the agent prepares the booking, the guest commits it.

**Should assistants reach the site without a browser?** Also yes, for the questions that don't need a session: search, availability and exact prices, and later, with Chapter 11, a member's own bookings. That's the MCP server, and the public API under it serves frameworks and gateways that prefer plain HTTP. Chapter 8 builds both.

**Do we run an agent of our own?** No. So no A2A, and no Agent Card, even though it would earn an integration point.

If I had to plan Nordlys for a real owner with a small budget, I would cut it into three releases:

1. **First month.** Accessible forms and pages, robots.txt with AI user-agent rules and Content Signals, a sitemap, structured data for the cabins, Markdown negotiation and an llms.txt. This is Stages 1 to 3, mostly content and configuration, and it takes the site to Level 3.
2. **Second month.** The shared booking rules pulled into one module, declarative WebMCP on the search and booking forms, and an API catalog for the public API. Level 4, and the three Lighthouse WebMCP audits have something to check.
3. **Later, on evidence.** The MCP server and OAuth for members, once the logs (Chapter 12) show assistants actually asking about cabins.

### The door Nordlys declines

Two doors stay closed for Nordlys, and they stay closed for good reasons. The NLWeb-style endpoint is the easy one: six cabins and a typed `search_cabins` tool leave nothing for a model and a vector store to improve. The A2A Agent Card is the more interesting one, because a grader would reward it.

isitagentready.com counts an A2A Agent Card as one of the four integration files, and "all four" is one of the three ingredients of Level 5. Publishing a card would describe an agent that Nordlys doesn't have. So Nordlys declines the door, accepts the missing point and writes down why. We'll see in the next section exactly where that leaves the site on the levels, and I think it's the right place to stop.

## A staged adoption plan

Decision trees tell you which doors to open. A roadmap also needs an order and a way to know that each step worked. Table 6.2 is the plan I recommend, in five stages. Each stage names the chapters that build it and what the two graders see when it is done. The isitagentready.com level rules are quoted from the scanner's own documentation, and the Lighthouse audit ids are from Lighthouse 13.6.0.[^ch06-22][^ch06-23]

Table 6.2 A staged adoption plan mapped to the graders (as of November 2026)

| Stage | Work | Chapters | isitagentready.com | Lighthouse Agentic Browsing |
|---|---|---|---|---|
| 1. Be readable and reachable | Semantic HTML, labels, a clean accessibility tree, robots.txt, sitemap, Link headers | 2, 3, 4, 5 | Level 1: "Pass 2 of 3: robots.txt, sitemap, link headers" | `agent-accessibility-tree`, `cumulative-layout-shift` |
| 2. Say what agents may do | AI user-agent rules and Content Signals in robots.txt, structured data | 4, 5 | Level 2: "Level 1 + both: AI bot rules and Content Signals in robots.txt" | none |
| 3. Serve content cheaply | Markdown through content negotiation, llms.txt | 5 | Level 3: "Level 2 + markdown content negotiation" | `llms-txt` |
| 4. Offer actions | API and API catalog, MCP server and server card, WebMCP tools, tool design, discovery files | 7, 8, 9 | Level 4: "Level 3 + 1 of 4: MCP Server Card, A2A Agent Card, Agent Skills, API Catalog" | `webmcp-registered-tools`, `webmcp-form-coverage`, `webmcp-schema-validity`, `ard-schema` |
| 5. Know who acts, and for whom | OAuth metadata and delegated access, bot verification, commerce where it fits | 4, 11 | Level 5: "Level 4 + 2 of 3: Web Bot Auth, all four integration checks, auth metadata" | none |

A few things in this table deserve a comment, because the graders are tools with opinions, and you should know the opinions before you plan around them.

**WebMCP does not change the level.** isitagentready.com has a `webMcp` check, but it is not part of any level rule. A site with perfect in-page tools and nothing else stays where it was. Lighthouse is the grader that sees WebMCP, with three audits. That's why Stage 4 lists WebMCP under Lighthouse only, and Chapter 9 measures exactly this on Nordlys.

**Level 2 is one vendor's vocabulary.** Content Signals is a robots.txt extension authored at Cloudflare, published as an individual IETF draft, and the IETF working group on AI preferences has drafts of its own.[^ch06-24] The Shopify stores from earlier have everything Level 2 asks for except this one line. I still recommend adding it, because it states your policy in a form agents can read. Just don't let anyone believe that Level 1 means "not agent-ready" when the actual gap is one line in robots.txt.

**Level 4 needs only one of four files.** A single API catalog at `/.well-known/api-catalog` is enough, and in Chapter 8 that one file moves Nordlys from Level 3 to Level 4. That's good news for planning: Stage 4 can start with whichever door your site type needs, and the level follows.

**Level 5 rewards things a small site may not need.** It asks for two of three: Web Bot Auth, all four integration files, or auth metadata. For Web Bot Auth, the scanner looks for your own signatures directory, which only makes sense if your site sends bot traffic. "All four" includes an A2A Agent Card. So a site that verifies bots instead of signing (the advice of Chapter 4) and runs no agent of its own can reach only one of the three ingredients.

### Where Nordlys stops

By the published criteria, Nordlys with the delegated access of Chapter 11 is at Level 4 with one of the three Level 5 ingredients: the OAuth discovery and Protected Resource Metadata files. I write "by the published criteria" because the demo site lives on `nordlys.example`, which the public scanner cannot reach, so these results come from comparing our files with the documented rules. Chapter 12 shows how to run the same checks against a local server in CI.

To reach Level 5, Nordlys would have to publish an A2A Agent Card for an agent it doesn't have, or publish a key directory for bot traffic it doesn't send. Both would be points without purpose. I'd rather explain to a manager why we stopped at Level 4 than maintain two files that describe nothing real :)

> **Tip:** Write your target into the plan as checks, not as a level or a score. "Pass `contentSignals`, `markdownNegotiation` and `apiCatalog`, and keep `agent-accessibility-tree` green on the booking pages" is a goal a team can own. "Reach Level 4" is a goal a team can game.

## Hands-on: the decision helper

> **Hands-on:** This section shows a small Node.js script that holds this chapter's decision trees and staged plan as data and prints a plan for one site. If you don't write code, the printed plan in Listing 6.1 is the part to read, and you can continue with "What not to build".

The helper lives in `chapters/13-choosing-the-right-agent-interface/` of the demos repository. It has no dependencies and runs on Node.js 22 or newer. When a grader changes its rules or your platform ships a new feature, you edit one data file and print the new plan, instead of rewriting a slide deck.

The data file describes the four site types from this chapter (what to build in priority order, what to consider, what to skip and why, and at which stage each type can stop) and the platforms (which interfaces each one already covers, so the helper moves them from "build" to "configure"). Listing 6.1 is the real output of `node decide.mjs --type ecommerce --platform shopify`.

**Listing 6.1** The printed plan for an online shop on Shopify

```text
E-commerce shop on shopify

Your platform already gives you (observed on allbirds.com, brooklinen.com and kith.com, 2 Nov 2026):
  - a WebMCP adapter (search_catalog, add_to_cart, proceed_to_checkout and more)
  - a UCP commerce profile at /.well-known/ucp that points agents at the platform's checkout services
  - OAuth discovery and protected resource metadata

Configure on the platform instead of building:
  - WebMCP tools in the page
  - Public API (OpenAPI, or your platform's own API)

Build, in this order:
  1. Markup: semantic HTML, accessibility tree, structured data
  2. Content formats: Markdown negotiation, llms.txt, feeds

Consider later:
  - MCP server
  - A2A agent card and endpoint

Stages and what the graders see:
  Stage 1: be readable and reachable
    isitagentready: Level 1 (2 of 3: robots.txt, sitemap, Link headers)
    Lighthouse: agent-accessibility-tree, cumulative-layout-shift
  Stage 2: say what agents may do
    isitagentready: Level 2 (Level 1 + AI bot rules and Content Signals)
  Stage 3: serve content agents can use cheaply
    isitagentready: Level 3 (Level 2 + Markdown negotiation)
    Lighthouse: llms-txt
  Stage 4: offer actions
    isitagentready: Level 4 (Level 3 + 1 of: MCP Server Card, A2A Agent Card, Agent Skills, API Catalog)
    Lighthouse: webmcp-registered-tools, webmcp-form-coverage, webmcp-schema-validity, ard-schema
  Stage 5: know who is acting, and for whom
    isitagentready: Level 5 (Level 4 + 2 of: Web Bot Auth, all four integration checks, auth metadata)
```

The plan says what we found earlier in this chapter, in a form a team can paste into a ticket. The WebMCP tools and the API side are configuration on Shopify, the build list shrinks to markup and content, and the stages still run all the way to Stage 5 because a shop takes payments.

Run it for your own site type with `--type booking`, `--type content` or `--type saas`, add `--platform wordpress` or `--platform cloudflare`, and `--has-api` if you already have a public API. The 7 tests (`node --test` in the folder) check the rules that matter, for example that a content site stops after content formats.

## What not to build

A decision framework is just as much about the doors you leave closed. Here are the ones I see teams open too early.

**An MCP server for a brochure site.** If your site has nothing to do except read, Markdown and llms.txt give agents everything an MCP server would, at a fraction of the cost. "Every site needs an MCP server" is one of the most overhyped claims of 2026.

**An A2A Agent Card without an agent.** It earns an integration point on isitagentready.com and describes nothing. Publish one when you have an agent that other agents should talk to, and not before.

**Commerce protocols before your payment provider supports them.** Appendix B lists ACP, UCP, AP2, x402 and the card network programs with their status. For a small site, the realistic path in November 2026 is an agent-safe checkout with human confirmation on your own payment page (Chapter 11), and watching the drafts.

**Long-tail checks for the points.** isitagentready.com documents 23 checks, among them DNS-AID records, an `auth.md` file and a Personal Agent Protocol file. Their adoption is close to zero, and several of them reference proposals that may change. They belong on a watch list (Chapter 12).

**A wall against clicking agents.** It is tempting to block every browsing agent until the "proper" doors are ready. Please don't do it by default. Chapter 4 separates training crawlers, search crawlers and agents acting for a user, and the last group is often a customer trying to book. Block by purpose and by verified identity, not by fear.

Each of these is a "not now", not a "never". We'll come back to this decision once more at the end of Chapter 9, when Nordlys has its API, its MCP server and its in-page tools, and look at what should make you open the plan again.

## Summary

- An agent can reach a site through eight doors: markup, content formats, a public API, an MCP server, WebMCP tools, an A2A agent, an NLWeb-style endpoint, or simply by clicking through the pages. Clicking is the baseline you always have.
- Compare the doors on cost, reliability, reach, control and maintenance. Each step from "the agent figures it out" to "the site declares it" costs more to build and gives more control and reliability.
- Reach is the honest weak spot of the newer doors in November 2026. WebMCP runs in origin trials, MCP servers have to be added by somebody, and NLWeb shows little activity. An API is portable, but consumer assistants don't call one on their own.
- Put every door on top of the same business rules. Then an extra door is mostly definitions and tests, and every agent hears the same prices and policies.
- Check what your platform already does before building. Shopify serves WebMCP tools, a UCP profile and OAuth metadata, WordPress has the Abilities API and an MCP Adapter plugin, and CDNs offer managed robots.txt, Markdown and bot verification.
- Content sites can stop after content formats. Booking sites need an API, WebMCP and MCP, plus the trust layers. SaaS applications lead with an MCP server and OAuth. Shops lean on their platform for in-page tools and commerce.
- Plan in five stages that map to the isitagentready.com levels and the Lighthouse Agentic Browsing audits, and know the graders' opinions: WebMCP doesn't change the level, Level 2 hinges on one Cloudflare-authored robots.txt line, and Level 5 rewards files a small site may not need.
- Write targets as named checks, keep a "not now" list, and revisit the plan when your traffic, the standards or your platform change.

- Put every door on top of the same business rules. Then an extra door is mostly definitions and tests, and every agent hears the same prices and policies.
- Check what your platform already does before building. Shopify serves WebMCP tools, a UCP profile and OAuth metadata, WordPress has the Abilities API and an MCP Adapter plugin, and CDNs offer managed robots.txt, Markdown and bot verification.
- Content sites can stop after content formats. Booking sites need an API, WebMCP and MCP, plus the trust layers. SaaS applications lead with an MCP server and OAuth. Shops lean on their platform for in-page tools and commerce.
- Plan in five stages that map to the isitagentready.com levels and the Lighthouse Agentic Browsing audits, and know the graders' opinions: WebMCP doesn't change the level, Level 2 hinges on one Cloudflare-authored robots.txt line, and Level 5 rewards files a small site may not need.
- Nordlys declines the A2A door and stops at Level 4 with one Level 5 ingredient. Write targets as named checks and keep a "not now" list with reasons.

[^ch06-1]: The decision helper `chapters/13-choosing-the-right-agent-interface/` (`plan.mjs`, `decide.mjs`, `test/plan.test.mjs`), webmaxru/agent-ready-web-demos, GitHub, https://github.com/webmaxru/agent-ready-web-demos (retrieved November 2026).
[^ch06-2]: "AI Insights", Cloudflare Radar, https://radar.cloudflare.com/ai-insights (retrieved November 2026). Traffic widgets for the 7 days to 2 November 2026: content type served to AI bots and the Markdown for Agents median response size.
[^ch06-3]: "A developer toolkit to make your website agent-ready", Kasper Kulikowski and Michael Hablich, Chrome for Developers, 22 June 2026, https://developer.chrome.com/blog/agent-ready-toolkit (retrieved November 2026).
[^ch06-4]: "Google's Guide to Optimizing for Generative AI Features on Google Search", Google Search Central, last updated 10 July 2026, https://developers.google.com/search/docs/fundamentals/ai-optimization-guide (retrieved November 2026).
[^ch06-5]: "Adoption of AI agent standards", Cloudflare Radar AI Insights, data dated 2 November 2026, 115,468 of the top 200,000 domains scanned, https://radar.cloudflare.com/ai-insights#adoption-of-ai-agent-standards (retrieved November 2026). The e-commerce numbers use the same page filtered to the Ecommerce domain category.
[^ch06-6]: "Expose REST API as MCP server", Azure API Management, Microsoft Learn, https://learn.microsoft.com/en-us/azure/api-management/export-rest-mcp-server, "Amazon Bedrock AgentCore Gateway: A secure AI gateway for agents, tools, and models", AWS documentation, https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html, "Extend your agent with tools from a REST API (preview)", Microsoft Copilot Studio documentation, https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-extend-action-rest-api, and "OpenAPI tools", Agent Development Kit, https://adk.dev/tools-custom/openapi-tools/ (retrieved November 2026).
[^ch06-7]: "Custom GPT retirement and migration FAQ", OpenAI Help Center, https://help.openai.com/en/articles/20001519-custom-gpt-retirement-and-migration-faq (retrieved November 2026).
[^ch06-8]: "WebMCP", Chrome Platform Status, feature 5117755740913664 (origin trial from Chrome 149, extended to Chrome 162), https://chromestatus.com/feature/5117755740913664, and the WebMCP trial on the Microsoft Edge origin trials page, https://developer.microsoft.com/microsoft-edge/origin-trials/trials/0b76fe60-b266-458e-a285-04e375c0c31a (retrieved November 2026).
[^ch06-9]: WebKit standards positions issue 670, https://github.com/WebKit/standards-positions/issues/670, and Mozilla standards positions issue 1412, https://github.com/mozilla/standards-positions/issues/1412 (retrieved November 2026). Mozilla has said a refreshed position is coming, and it was not published as of 2 November 2026.
[^ch06-10]: A2A releases, GitHub, https://github.com/a2aproject/A2A/releases, and "A New Chapter for A2A: Joining the Agentic AI Foundation", A2A project blog, 27 August 2026, https://a2a-protocol.org/latest/blog/2026/08/27/a-new-chapter-for-a2a-joining-the-agentic-ai-foundation/ (retrieved November 2026).
[^ch06-11]: "Introducing NLWeb: Bringing conversational interfaces directly to the web", Microsoft Source, 19 May 2025, https://news.microsoft.com/source/features/company-news/introducing-nlweb-bringing-conversational-interfaces-directly-to-the-web/ (retrieved November 2026).
[^ch06-12]: nlweb-ai/NLWeb repository, GitHub, https://github.com/nlweb-ai/NLWeb, and "NLWeb", Cloudflare AI Search documentation, https://developers.cloudflare.com/ai-search/how-to/nlweb/ (retrieved November 2026). Repository activity read through the GitHub API on 2 November 2026.
[^ch06-13]: The research for this book, 2 November 2026: the storefronts allbirds.com, brooklinen.com and kith.com, their `/.well-known/ucp` files and OAuth metadata, and the WebMCP tools their pages register. The full scan table is in the book's research notes. Shopify can change any of this at any time.
[^ch06-14]: isitagentready.com scan API (`POST https://isitagentready.com/api/scan`), scans of https://www.allbirds.com, https://www.brooklinen.com and https://kith.com run by the author on 2 November 2026, https://isitagentready.com (retrieved November 2026).
[^ch06-15]: "Abilities API in WordPress 6.9", Make WordPress Core, 10 November 2025, https://make.wordpress.org/core/2025/11/10/abilities-api-in-wordpress-6-9/ (retrieved November 2026).
[^ch06-16]: "From Abilities to AI Agents: Introducing the WordPress MCP Adapter", WordPress Developer Blog, February 2026, https://developer.wordpress.org/news/2026/02/from-abilities-to-ai-agents-introducing-the-wordpress-mcp-adapter/, and release v0.7.1 of WordPress/mcp-adapter, 16 October 2026, https://github.com/WordPress/mcp-adapter/releases/tag/v0.7.1 (retrieved November 2026).
[^ch06-17]: "Giving users choice with Cloudflare's new Content Signals Policy", The Cloudflare Blog, 24 September 2025, https://blog.cloudflare.com/content-signals-policy/ (retrieved November 2026).
[^ch06-18]: "Introducing Markdown for Agents", The Cloudflare Blog, 12 February 2026, https://blog.cloudflare.com/markdown-for-agents/ (retrieved November 2026). The post gives the 16,180 and 3,150 token counts and the plan availability.
[^ch06-19]: "Verified bots", Cloudflare documentation, https://developers.cloudflare.com/bots/concepts/bot/verified-bots/, and "AWS WAF announces Web Bot Auth support", AWS What's New, 21 November 2025, https://aws.amazon.com/about-aws/whats-new/2025/11/aws-waf-web-bot-auth-support/ (retrieved November 2026).
[^ch06-20]: Scans of 44 sites with isitagentready.com by the author on 2 November 2026 (5 more sites refused the scanner). Results: 8 sites at Level 4, 30 at Level 1, 6 at Level 0, none at Levels 2, 3 or 5. The full table is in the book's research notes.
[^ch06-21]: Universal Commerce Protocol, https://ucp.dev/, and "Google plans to adopt UCP draft spec for AI Mode hotel booking", Search Engine Journal, https://www.searchenginejournal.com/google-plans-to-adopt-ucp-draft-spec-for-ai-mode-hotel-booking/591235/ (retrieved November 2026). Appendix B lists the Lodging draft with its status.
[^ch06-22]: isitagentready.com documentation for agents, https://isitagentready.com/llms-full.txt (retrieved November 2026). The level rules are quoted verbatim.
[^ch06-23]: "Lighthouse agentic browsing scoring", Chrome for Developers, https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring, and the category configuration in Lighthouse 13.6.0, https://github.com/GoogleChrome/lighthouse/blob/main/core/config/agentic-browsing-config.js (retrieved November 2026).
[^ch06-24]: "Vocabulary For Expressing Content Signals", Internet-Draft draft-romm-aipref-contentsignals-00, IETF Datatracker, https://datatracker.ietf.org/doc/draft-romm-aipref-contentsignals/ (retrieved November 2026). The IETF AIPREF working group's own drafts are draft-ietf-aipref-vocab and draft-ietf-aipref-attach (Chapter 4).
