# Chapter 13: Choosing the right agent interface

This chapter covers

- The eight ways an agent can reach your site, from plain markup to agents clicking through your pages
- Comparing them on cost, reliability, reach, control and maintenance
- Checking what your platform already ships before you build anything
- Decision trees for content sites, booking sites, SaaS applications and online shops
- A staged adoption plan mapped to the isitagentready.com levels and the Lighthouse Agentic Browsing audits

Nordlys Cabins now has more doors for machines than most real sites will ever need. Chapter 7 gave it a public API with an OpenAPI description, Chapter 8 an MCP server, Chapter 9 tools in the page, Chapter 10 tightened the tool definitions, Chapter 11 published the files that let agents find all of that, and Chapter 12 added a commerce layer. Before that, Part 2 made the content readable: semantic markup, structured data, Markdown and llms.txt.

That was on purpose. A book about agent-readiness has to show every layer, and a running example is the cheapest way to show them working together. But your site is not a book. You have a backlog, a budget and a team that already maintains one front end, maybe two. When I talk to web teams about this topic, the first question is almost never "how do I build an MCP server?". It is "which of these do we actually need, and in what order?"

This chapter answers that question. It is the editor's "when to use each layer, and why" chapter, and it closes Part 3. We'll put all eight agent interfaces side by side, rate them on five criteria, and then turn the ratings into decision trees for four common kinds of site. At the end there is a staged plan you can drop into a roadmap, with the exact checks that each stage moves in both graders.

> **Note:** This is a planning chapter, and most of it is written for the whole team. The one hands-on section near the end shows a small decision helper in `chapters/13-choosing-the-right-agent-interface/` of the demos repository. It holds the decision trees from this chapter as data and prints a plan for your type of site.[^ch13-1]

## Eight doors into one site

Let's start with an inventory. In November 2026, an agent that wants something from your site can come in through one of eight doors. Some of them you build, some you configure, and one of them you get whether you want it or not.

1. **Markup.** Semantic HTML, a clean accessibility tree and structured data (Chapters 2, 3 and 5). Every agent that reads or browses your pages uses it, whether it knows the word "agent-ready" or not.
2. **Content formats.** Markdown through content negotiation, llms.txt, feeds and sitemaps (Chapter 6). These serve the same information as your pages, just cheaper to read.
3. **A public API.** HTTP endpoints described with OpenAPI and listed in an API catalog (Chapter 7). The oldest machine door on the web, and still the most portable one.
4. **An MCP server.** Your site's actions as tools on a remote Model Context Protocol server (Chapter 8). Assistants such as Claude, ChatGPT and Copilot Studio connect to it once somebody adds it.
5. **WebMCP tools.** Tools declared in the page itself, on your forms or in JavaScript (Chapter 9). An agent working inside the user's browser calls them in the user's session.
6. **An A2A agent.** An Agent Card at `/.well-known/agent-card.json` and an endpoint that speaks the Agent2Agent protocol. This door only exists if your site runs an agent of its own that other agents can hand work to.
7. **An NLWeb-style endpoint.** A natural-language question endpoint (`/ask`, and the same thing as an MCP tool) answered from your structured data.
8. **Agents clicking.** No door at all, technically. A browsing agent opens your pages, reads them and clicks your buttons the way a person would.

Please note that these are not alternatives in the strict sense. Markup is under everything: a WebMCP form tool is built on the same `<form>` that Chapter 3 made accessible, and an MCP tool calls the same booking service as the API. In our case, all the Nordlys doors end up in the same business rules. That's the most important architectural decision in this whole chapter, and we'll come back to it.

Figure 13.1 puts the eight doors on one line. On the left, the agent does the work of figuring out your site. On the right, your site declares exactly what can be done and how.

![Figure 13.1 — The eight agent interfaces arranged from "the agent figures it out" to "the site declares it". Agents clicking and plain markup need the least from the site team and give it the least control. Content formats, NLWeb-style endpoints, WebMCP tools, a public API, an MCP server and an A2A agent each ask for more work and give back more control over what an agent can do. All of them should call the same domain logic underneath.](images/figure-13-1.png)

The line is not a ranking. A site that only publishes articles has nothing to put on the right side of it, and that's fine. What the line shows is a trade: every step to the right costs you some building and maintenance, and pays you back in control and reliability.

## Five questions to ask of every door

To compare doors that look so different, we need the same questions for each one. Here are the five I use. They are deliberately boring, because they are the questions a product manager or an architect asks about any new interface, agent or not.

**Cost.** What does it take to build the door and to run it? Building includes design work, code, content and review. Running includes hosting, monitoring and the support questions that arrive when something breaks.

**Reliability.** When an agent uses this door, how often does the task actually succeed? A door that works nine times out of ten is not a door for booking cabins. Reliability is mostly about how much the agent has to guess.

**Reach.** Which agents can use the door today, in November 2026? A beautiful interface that no agent product calls is a bet on the future, and bets are fine as long as you know you are making one.

**Control.** What do you decide? Which actions exist, who may call them, with what limits, and where a human must confirm. Low control means the agent decides, and you find out from your logs.

**Maintenance.** What breaks when you change your site, and what breaks when the standard changes? Some doors break silently with every redesign. Others are pinned to a draft that may look different next quarter.

There is a sixth question that I don't put in the table, because it is not a property of the door: does your platform already give it to you? We'll spend a whole section on that one, because it changes the answer more often than any rating.

> **Tip:** Run these five questions as a short workshop with the people who will own the result. Developers tend to rate cost and maintenance well, content and SEO people know reach, and security people will ask about control before anyone else does. Twenty minutes per door is enough.

## Rating the doors

Table 13.1 is my rating of the eight doors on the five questions, for a typical small or medium site. Please treat the ratings as my informed opinion. The paragraphs after the table say why each rating is what it is, with the facts behind it, so you can disagree with me on your own evidence.

Table 13.1 The eight agent interfaces compared (as of November 2026)

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

Let's go through the rows.

### Agents clicking

You get this door for free, and that is both its charm and its problem. Browsing agents such as ChatGPT's agent mode in Atlas, Claude in Chrome, Gemini in Chrome and Copilot in Edge drive a real browser, read the page and click.[^ch13-2] Your site does nothing special for them, so the cost is zero and the reach is every browsing agent there is.

Reliability is where it hurts. The agent has to work out from the page which element is the date picker, what the error message under the form means and whether the booking actually went through. Chapter 2 showed what that looks like on a form with no labels. Chapter 1 also quoted the numbers that make clicking expensive for the agent: on Cloudflare Radar in the week to 2 November 2026, AI bots received HTML 73.2% of the time and Markdown less than 0.1%, and serving Markdown instead of HTML cut the median response to 7.9% of its original size.[^ch13-3] An agent that reads full pages pays for every byte of navigation and cookie banners in tokens and in mistakes.

Control is low: the agent can do anything a person can do on the page, and nothing more specific than that. Maintenance is hidden, which is the worst kind. Every redesign can break an agent's way through your site, and nobody on your team will know until the logs (Chapter 19) or a confused customer tell you.

Bottomline: clicking is the baseline you cannot turn off and should not try to. The rest of this chapter is about how much you add on top of it.

### Markup

Semantic HTML, labels and a well-formed accessibility tree are the cheapest layer in the book, because most of the work is the same work you do for accessibility anyway. Chrome's own toolkit post says agents "rely on the accessibility tree" as their "primary data model".[^ch13-4] Structured data adds machine-readable facts about your entities.

I rate reliability as medium. Good markup makes clicking far more reliable, but the agent still has to plan its way through your pages. Reach is the same as clicking plus every reading agent. Control is low to medium: you decide what the page says and how it is structured. What the agent does with it is up to the agent.

Please note one honest limit on structured data. Google's guidance for its generative AI features, updated 10 July 2026, says that no special schema.org markup is needed for them.[^ch13-5] Structured data is still worth it for rich results and for the agents and pipelines that read it, but it is not a ranking trick, and nobody should sell it to your manager as one.

### Content formats

Markdown through content negotiation, llms.txt and feeds are cheap to add, and on a CDN they can be a switch you flip. For reading tasks they are the most reliable door of all, because the agent gets your words without the page around them. Cloudflare measured its own blog post at 16,180 tokens as HTML and 3,150 as Markdown, an 80% reduction.[^ch13-6]

Reach is growing and uneven. Some retrieval agents send `Accept: text/markdown` first, many don't, and Google says its Search does not use llms.txt or special Markdown files at all. In Google's words, publishing them "will neither harm nor help your site's visibility or rankings in Google Search".[^ch13-5] Adoption numbers tell the same story. Of the 115,468 domains in Cloudflare Radar's agent-readiness dataset on 2 November 2026, 4.3% answered Markdown negotiation.[^ch13-7] So this is a door for the agents and tools that read it. It won't move your search rankings.

Control is medium: you decide what goes into the Markdown version and what the llms.txt file points to, and the robots.txt rules and Content Signals from Chapter 4 travel with it. Maintenance is low as long as the Markdown is generated from the same source as the HTML, which is how Chapter 6 built it.

### A public API

A well-described HTTP API is the most portable action door on the web. Every agent framework can call one, and the big platforms now turn an OpenAPI description into tools for you: Azure API Management can expose REST operations as an MCP server, AWS Bedrock AgentCore Gateway converts OpenAPI into MCP tools, Copilot Studio takes an OpenAPI file directly, and Google's Agent Development Kit generates tools from OpenAPI 3.x.[^ch13-8] Reliability is high, because the operations are explicit and the errors can be precise (Chapter 7 showed problem details and idempotency keys).

Reach deserves a careful sentence. An API is reachable by developers, frameworks and gateways, which is a lot of reach. It is not something a consumer assistant discovers and calls by itself. One of the few consumer paths that did exactly that is closing: OpenAI is retiring Custom GPTs on 11 December 2026, and their OpenAPI-based actions do not carry over to the new MCP-based plugins.[^ch13-9]

Cost is medium if you already have an API, which many booking and SaaS sites do, and high if you don't. Control is high. Maintenance is medium: versions, deprecations and the catalog file from Chapter 7 are real work, but it is work API teams already know how to do.

### An MCP server

A remote MCP server is the door that assistants use. Chapter 8 listed the hosts that connect to one in November 2026: Claude, ChatGPT and Codex, Copilot Studio, VS Code and Gemini Enterprise. Reliability is high for the same reason as with an API, and the tool design craft from Chapter 10 pushes it higher.

Reach comes with a catch that Chapter 8 already named. In every one of those hosts, somebody has to add your server: a user pastes a URL, an admin approves a connector or a developer edits a configuration file. There is no global directory that assistants consult on their own, and the discovery files from Chapter 11 are still settling. Adoption is accordingly small: on 2 November 2026 Radar found an MCP Server Card on 0.61% of the domains it scanned.[^ch13-7]

Control is high: you choose the tools, the annotations, the confirmations and, with Chapter 14, who may call them on whose behalf. Maintenance is medium with a warning attached. The specification changed shape in its 2026-07-28 revision (stateless requests, no sessions), and the TypeScript SDK moved to a new major version. A server written from 2025 tutorials needed real changes this year, and that can happen again.

### WebMCP tools

WebMCP is the door inside the page. A declarative tool is a few attributes on a form you already have, and imperative tools reuse the JavaScript your page already runs, so the cost is low to medium. Reliability is high in a browser that supports it, because the agent calls a function with a schema instead of hunting for buttons. The user's session, cookies and consent come along for free, which no server-side door can offer.

Reach is the honest weak spot. As of November 2026, WebMCP runs in a Chrome origin trial that started in Chrome 149 and is extended to Chrome 162, and Edge has its own origin trial.[^ch13-10] WebKit's standards position is "oppose" and Mozilla's is "neutral".[^ch13-11] Radar counted WebMCP on 1.42% of scanned domains, 1,643 of them, and most of those are online shops whose platform added the tools for them (more on that in a moment).[^ch13-7]

Control is high, because the tools are yours and the page decides when they exist. Maintenance is medium: the specification gained `outputSchema` on 2 November 2026, the very day I am writing this, and it will change again before it is final. My previous book, "Tools, Not Clicks", covers this door in depth at https://webmcp.salnikov.no.

### An A2A agent

A2A, the Agent2Agent protocol, is for one agent handing work to another. Version 1.0.0 shipped on 12 March 2026, and in August 2026 A2A joined the Agentic AI Foundation next to MCP.[^ch13-12] The discovery file is an Agent Card at `/.well-known/agent-card.json`.

The important thing for a site owner is what A2A is not. It is not a way to expose your booking form or your product catalog. Tools and data belong in an API, an MCP server or WebMCP. A2A only makes sense if your site runs an agent of its own with judgment worth delegating to, for example a "Nordlys concierge" that plans a whole trip and talks back with progress. Building and operating such an agent is the most expensive item in Table 13.1 by a wide margin, and reliability is whatever your agent's reliability is.

So for most sites in this book's audience, A2A is a door to know about and to skip. That's also why Nordlys doesn't publish an Agent Card, even though isitagentready.com would reward it with points, as we'll see later in this chapter.

### An NLWeb-style endpoint

NLWeb, which Microsoft announced in May 2025 and which R.V. Guha (the person behind RSS, RDF and schema.org) conceived, lets agents ask a site a question in natural language and get schema.org-shaped JSON back. Every NLWeb instance is also an MCP server.[^ch13-13] The reference implementation ingests the structured data and feeds you already publish into a vector store and answers with a language model.

The idea is elegant, and for a large catalog of articles or recipes it can be a genuinely useful door. But the facts as of November 2026 call for caution. The reference repository has no tagged releases, its last push was on 11 August 2026, and its most recent commits on main were dependency updates. Cloudflare's NLWeb template in AI Search is still in public preview.[^ch13-14] I found no evidence that any major assistant discovers or calls NLWeb endpoints automatically, and no 2026 adoption numbers either. That's why the reach cell in Table 13.1 says "hard to tell". In simple words: if you already run a search index over a large content collection, an NLWeb-style endpoint is a cheap experiment. If you don't, the structured data and Markdown from Part 2 give agents the same content without a model in the middle.

## One set of rules behind every door

Before we turn ratings into decisions, there is one rule that makes every later decision cheaper. Whatever doors you open, they should all call the same business rules. Let's have a look at how Nordlys does it.

The rules of the business (search, prices, availability and the 14-day free cancellation policy) live in one place, the store module of the app. The human booking form calls it. Chapter 7 wrapped it in a booking service that adds what machine clients need on top, stable output shapes and idempotent booking, and both the public API and the MCP tools from Chapter 8 call that service. The small JSON endpoints behind the WebMCP tools of Chapter 9 call the store too, and so does the commerce layer from Chapter 12. So when the cancellation policy changes, it changes in one place, and every door tells every agent the same thing.

Figure 13.2 shows the shape. The doors are thin. Each one translates between a protocol and the shared rules, and adds what only that door can add: a schema for MCP, a form annotation for WebMCP, an OpenAPI description for the API.

![Figure 13.2 — One set of business rules behind every door. The human pages, the public API, the MCP server, the WebMCP tools and the commerce layer of Nordlys Cabins are thin adapters over the same store, partly through the booking service from Chapter 7, so prices, availability and the cancellation policy live in one place. Markup and content formats describe the same data for readers.](images/figure-13-2.png)

This has two consequences for planning:

- **The cost of an extra door is mostly definitions and tests, not logic.** Once the shared rules exist, an MCP server is a list of tool definitions and a few hundred lines of adapter code. The tool design work from Chapter 10 applies to all doors at once, because a model sees every one of them as a name, a description and a schema.
- **The order of doors matters less than where your rules live.** If your business logic is buried in page controllers, the first agent door you open will be expensive, whichever one it is. Pulling the rules into one module that every interface calls is the real first step, and it pays off for your human front end too.

> **Warning:** A door that bypasses the shared rules is where trouble starts. A WebMCP tool that scrapes its own page, or an MCP tool that writes to the database directly, will drift from what the human interface does. Chapter 16 shows how such drift becomes a security problem as well.

## Check what your platform already does

Here is the sixth question from earlier, and the one that most often changes the plan. Before you build any door, find out which ones your platform has already opened for you. The adoption data makes the point better than any argument. Platforms move agent-readiness on the web, individual sites much less.

### Shopify

Shopify is the clearest example in November 2026. On the storefronts we looked at during the research for this book, the platform serves a WebMCP adapter with tools such as `search_catalog`, `add_to_cart` and `proceed_to_checkout`, a Universal Commerce Protocol profile at `/.well-known/ucp`, and OAuth discovery metadata.[^ch13-15] The merchants didn't build any of it.

You can see the effect in Cloudflare Radar. In its e-commerce category on 2 November 2026, WebMCP showed up on 928 of 18,927 domains (about 4.9%) and UCP on 4,181. Across all scanned domains, WebMCP was at 1.42%.[^ch13-7] One platform decision did more for in-page tools than every hand-built WebMCP integration together.

Let's have a look at what that means for the graders. I scanned three Shopify stores (allbirds.com, brooklinen.com and kith.com) with isitagentready.com on 2 November 2026. All three passed robots.txt, sitemap, the AI bot rules check, OAuth discovery, OAuth Protected Resource and UCP. Allbirds also passed Markdown negotiation. And all three sat at Level 1, "Basic Web Presence".[^ch13-16] The reason is one missing line. Level 2 needs Content Signals in robots.txt, and none of the three had it. The scanner's WebMCP check could not finish on any of them ("Browser session timed out"), which is a reminder that a heavy storefront can defeat a headless check even when the tools are there.

So for a Shopify merchant, the agent-readiness plan is mostly configuration and content: robots.txt policy, product data quality, structured data and the accessibility of the theme. The action doors are the platform's job.

### WordPress

WordPress takes a different route: the building blocks ship in core, the agent door is a plugin. WordPress 6.9 (December 2025) introduced the Abilities API, a registry where core, plugins and themes describe what they can do, with input and output schemas.[^ch13-17] The official MCP Adapter, introduced on the WordPress developer blog in February 2026, makes registered abilities available to MCP clients, and you install it as a plugin. Its current version, 0.7.1, was released on 16 October 2026.[^ch13-18]

Please note the difference to Shopify. Nothing is exposed until a site owner installs the adapter and decides which abilities to publish. That's more work, and also more control, which is exactly the trade from Table 13.1. A WordPress site that wants an MCP door should start there before writing a server by hand.

### Cloudflare and the other edges

If your site sits behind Cloudflare, several Part 2 layers are zone settings. A managed robots.txt with a Content Signals line has been available since September 2025, and Cloudflare said at the time that it was already enabled on more than 3.8 million domains.[^ch13-19] Markdown for Agents, the content negotiation from Chapter 6, is a beta feature at no extra cost on the Pro, Business and Enterprise plans.[^ch13-6] Your llms.txt, of course, is still yours to write, because only you know which pages matter.

Bot verification is the other edge feature worth checking. Cloudflare folded signed agents into its verified bots program on 1 July 2026, and AWS WAF added Web Bot Auth support in November 2025.[^ch13-20] If your CDN or WAF verifies signed agents, Chapter 15's work becomes a policy decision instead of code.

### API gateways

If you already run an API behind Azure API Management or plan to use AWS Bedrock AgentCore Gateway, an MCP door may be a configuration step on top of the OpenAPI description you already have.[^ch13-8] The tool design advice from Chapter 10 still applies, because the generated tool names and descriptions come straight from your `operationId` and `summary` fields. Chapter 10's eval showed what happens when they are left as they are.

> **Tip:** Ask your platform vendors four short questions before planning any build: Do you serve Markdown to agents? Do you publish any agent tools (WebMCP or MCP) for my site, and can I switch them off? What do you put in my robots.txt and `/.well-known/`? Do you verify signed bots and agents? Write the answers into your plan, with the date, because they change.

## Decision trees for four kinds of site

Now let's turn the ratings into decisions. Figure 13.3 is the general tree. It asks four questions in order: what your platform already gives you, whether agents need to act on your site or only read it, whether the action needs the user's session in the browser, and whether you run an agent of your own.

![Figure 13.3 — The decision tree. Start with markup and content formats for every site, then check what the platform ships. If agents only need to read, stop after content formats. If they need to act, add an API, then WebMCP when the action belongs to the user's browser session and an MCP server when assistants should reach it without a browser. Add an A2A agent only if you run an agent of your own. Agents clicking remain possible on every path.](images/figure-13-3.png)

The tree shows the usual order, and your site type can swap two steps, as the online shop below does. It is general on purpose. Real sites cluster into a few types, and for each type the same answers come up again and again. Here are four, with what I would build, what I would consider later and what I would skip. They are also the data behind the decision helper in the hands-on section.

### A content site

Publishers, documentation sites, blogs and most marketing sites belong here. Agents come to read: training crawlers, search and answer engines, and user-triggered fetchers that pull one page because somebody asked about it.

- **Build:** markup and content formats. Semantic HTML and structured data, a robots.txt that states your policy (Chapter 4), Markdown through content negotiation and an llms.txt that links to your important pages (Chapter 6).
- **Consider later:** an NLWeb-style endpoint if you have a large archive and already run a search index over it, and an MCP server if your content is something people want to query from an assistant (documentation sites are the strongest case).
- **Skip:** WebMCP, because there are few actions to offer, and A2A, because there is no agent of yours to talk to.
- **Also do:** verify signed agents and crawlers at your edge (Chapter 15). No grader counts this, but it is how the policy you wrote in robots.txt actually gets enforced.

A content site can reach Level 3 on isitagentready.com without a single tool, and that is a good place to stop. In my scan of 44 well-known sites on 2 November 2026, none of them sat at Level 2 or Level 3 at all, so a content site at Level 3 would be ahead of most of the web.[^ch13-21]

### A booking site

This is Nordlys, and also restaurants, clinics, salons, tours and any site where a guest picks a time slot and commits. Agents come to read and to act, and the action has consequences: money, a reservation, a personal schedule.

- **Build:** markup, content formats, a public API, WebMCP tools, an MCP server, in that order. The API and its shared rules come first because every other action door depends on them. WebMCP comes before MCP for a public booking flow because the guest's own browser session, consent and confirmation come along with it (Chapter 9). The MCP server follows for assistants that should check availability or look up a booking without a browser.
- **Consider later:** an A2A agent, if you ever build a concierge worth delegating to. And the commerce standards from Chapter 12, especially the UCP Lodging draft from 25 September 2026, which is written for exactly this kind of business.[^ch13-22]
- **Skip:** an NLWeb-style endpoint. Nordlys has six cabins. A natural-language search over six items is not worth an endpoint, and `search_cabins` already does the job.

Booking sites need the trust layers of Part 4 more than any other type, because the actions are real. Chapter 14's delegated access and Chapter 16's confirmations are not optional extras here.

### A SaaS application

Here the product is behind a login, and the users are customers who want their assistant to work with their data in your product: create a ticket, pull a report, update a record.

- **Build:** markup for the public pages, a public API, an MCP server, then WebMCP. Most SaaS products already have an API, so the first real step is usually the MCP server with OAuth (Chapters 8 and 14). WebMCP comes after it for workflows that happen inside the product's UI with the user watching.
- **Consider later:** A2A if your product has its own agent (many SaaS products do by now), and content formats for your documentation and help center.
- **Skip:** an NLWeb-style endpoint. Your users ask your product, not your marketing pages.

For SaaS, the MCP server is the door that matters most, because the assistants your customers already use at work are MCP hosts. Copilot Studio, Claude and ChatGPT were all on the Chapter 8 list.

### An online shop

Shops have the most crowded field of standards (Chapter 12) and the strongest platform effect.

- **Build:** markup, content formats, WebMCP tools and an API, unless your platform provides them. Product data quality is part of the markup here: names, prices, availability and variants that a machine can read without guessing.
- **Consider later:** an MCP server and an A2A agent, and the commerce protocols once your payment provider supports them.
- **Skip:** nothing on principle, but check the platform list first. On Shopify, the WebMCP tools, the commerce profile and the OAuth metadata already exist, so your own work is the markup, the content and the robots.txt policy.

Please note how the order differs from the booking site. A shop puts WebMCP before an API because a cart and a checkout live in the browser session, and because, as the Radar numbers show, that is where the platforms went first.

## Walking the tree with Nordlys

Let's put the tree to work on our own example, question by question, and see where the book's choices and the tree's answers differ. They do differ in a few places, and that's useful.

**What does the platform give us?** Nothing. Nordlys is a custom application on a small Node.js server, so every door is ours to build. A real cabin-rental business of this size would often sit on a booking platform or a channel manager instead, and the first step would be to ask that vendor the four platform questions. For the book, building everything by hand was the point.

**Do agents need to act, or only to read?** Both. Guests ask an assistant about cabins with a sauna near the fjord, which is reading, and then they want to check dates and book, which is acting. So Nordlys goes past the content stage.

**Does the action belong in the user's browser session?** For a guest who is already on the site, yes. The booking form, the guest's sign-in and the final confirmation all live in the page, so WebMCP is the natural door for them. Chapter 9 kept the final step in the guest's hands on purpose: the agent prepares the booking, the guest commits it.

**Should assistants reach the site without a browser?** Also yes, for the questions that don't need a session: search, availability and exact prices, and later, with Chapter 14, a member's own bookings. That's the MCP server, and the public API under it serves frameworks and gateways that prefer plain HTTP.

**Do we run an agent of our own?** No. So no A2A, and no Agent Card, even though it would earn an integration point.

Where the book went further than the tree recommends is NLWeb (we didn't build it, and the tree agrees) and the commerce layer of Chapter 12. With six cabins and a payment page of its own, Nordlys would, in real life, wait for the UCP Lodging draft to settle and for its payment provider to support it. The book built a UCP-style profile to show the shape, and Chapter 12 says plainly what is demonstration and what is production advice.

If I had to plan Nordlys for a real owner with a small budget, I would cut it into three releases:

1. **First month.** Accessible forms and pages, robots.txt with AI user-agent rules and Content Signals, a sitemap, structured data for the cabins, Markdown negotiation and an llms.txt. This is Stages 1 to 3, mostly content and configuration, and it takes the site to Level 3.
2. **Second month.** The shared booking rules pulled into one module, declarative WebMCP on the search and booking forms, and an API catalog for the public API. Level 4, and the three Lighthouse WebMCP audits have something to check.
3. **Later, on evidence.** The MCP server and OAuth for members, once the logs from Chapter 19 show assistants actually asking about cabins.

Please note what's missing from that list: nothing in it requires a standard that is still a draft to be final, apart from WebMCP, which degrades gracefully to the plain form in every browser that doesn't support it. That's the property I look for in a first release.

## A staged adoption plan

Decision trees tell you which doors to open. A roadmap also needs an order and a way to know that each step worked. Table 13.2 is the plan I recommend, in five stages. Each stage names the chapters that build it and what the two graders see when it is done. The isitagentready.com level rules are quoted from the scanner's own documentation, and the Lighthouse audit ids are from Lighthouse 13.6.0.[^ch13-23][^ch13-24]

Table 13.2 A staged adoption plan mapped to the graders (as of November 2026)

| Stage | Work | Chapters | isitagentready.com | Lighthouse Agentic Browsing |
|---|---|---|---|---|
| 1. Be readable and reachable | Semantic HTML, labels, a clean accessibility tree, robots.txt, sitemap, Link headers | 2, 3, 4, 6 | Level 1: "Pass 2 of 3: robots.txt, sitemap, link headers" | `agent-accessibility-tree`, `cumulative-layout-shift` |
| 2. Say what agents may do | AI user-agent rules and Content Signals in robots.txt, structured data | 4, 5 | Level 2: "Level 1 + both: AI bot rules and Content Signals in robots.txt" | none |
| 3. Serve content cheaply | Markdown through content negotiation, llms.txt | 6 | Level 3: "Level 2 + markdown content negotiation" | `llms-txt` |
| 4. Offer actions | API and API catalog, MCP server and server card, WebMCP tools, tool design, discovery files | 7 to 11 | Level 4: "Level 3 + 1 of 4: MCP Server Card, A2A Agent Card, Agent Skills, API Catalog" | `webmcp-registered-tools`, `webmcp-form-coverage`, `webmcp-schema-validity`, `ard-schema` |
| 5. Know who acts, and for whom | OAuth metadata and delegated access, bot verification, commerce where it fits | 12, 14, 15 | Level 5: "Level 4 + 2 of 3: Web Bot Auth, all four integration checks, auth metadata" | none |

A few things in this table deserve a comment, because the graders are tools with opinions, and you should know the opinions before you plan around them.

**WebMCP does not change the level.** isitagentready.com has a `webMcp` check, but it is not part of any level rule. A site with perfect in-page tools and nothing else stays where it was. Lighthouse is the grader that sees WebMCP, with three audits. That's why Stage 4 lists WebMCP under Lighthouse only. Chapter 9 measured exactly this on Nordlys.

**Level 2 is one vendor's vocabulary.** Content Signals is a robots.txt extension authored at Cloudflare, published as an individual IETF draft. The IETF working group on AI preferences has drafts of its own.[^ch13-25] Making it a gate for Level 2 is a choice the scanner made. The Shopify stores from earlier have everything Level 2 asks for except this one line, so they stay at Level 1. I still recommend adding Content Signals, because the line states your policy in a form that agents can read. Just don't let anyone on your team believe that Level 1 means "not agent-ready" when the actual gap is one line in robots.txt.

**Level 4 needs only one of four files.** A single API catalog at `/.well-known/api-catalog` is enough, and Chapter 7 showed that this one file moved Nordlys from Level 3 to Level 4. That's good news for planning: Stage 4 can start with whichever door your site type needs, and the level follows.

**Level 5 rewards things a small site may not need.** It asks for two of three: Web Bot Auth, all four integration files, or auth metadata. For Web Bot Auth, the scanner looks for your own signatures directory, which only makes sense if your site sends bot traffic. "All four" includes an A2A Agent Card. So a site that verifies bots instead of signing (Chapter 15's advice) and runs no agent of its own can reach only one of the three ingredients.

That last point is where Nordlys stops, and I think it's the right place.

### Where Nordlys stops

By the published criteria, Nordlys after Chapter 14 is at Level 4 with one of the three Level 5 ingredients: the OAuth discovery and Protected Resource Metadata files. I write "by the published criteria" because the demo site lives on `nordlys.example`, which the public scanner cannot reach, so these results come from comparing our files with the documented rules. Chapter 18 shows how to run the same checks against a local server in CI.

To reach Level 5, Nordlys would have to publish an A2A Agent Card for an agent it doesn't have, or publish a key directory for bot traffic it doesn't send. Both would be points without purpose. I'd rather explain to a manager why we stopped at Level 4 than maintain two files that describe nothing real :)

On the Lighthouse side, Chapter 9 already showed the useful lesson: every Nordlys page scored a full fraction before the WebMCP layer existed, because missing form coverage is informative and doesn't count. A full score is not the goal. The audit details are.

> **Tip:** Write your target into the plan as checks, not as a level or a score. "Pass `contentSignals`, `markdownNegotiation` and `apiCatalog`, and keep `agent-accessibility-tree` green on the booking pages" is a goal a team can own. "Reach Level 4" is a goal a team can game.

## Hands-on: the decision helper

> **Hands-on:** This section shows a small Node.js script that holds this chapter's decision trees and staged plan as data and prints a plan for one site. If you don't write code, the printed plan in Listing 13.3 is the part to read, and you can continue with "What not to build".

The helper lives in `chapters/13-choosing-the-right-agent-interface/` of the demos repository. It has no dependencies and runs on Node.js 22 or newer. The point of keeping a decision framework as code is simple: when a grader changes its rules or your platform ships a new feature, you edit one data file, run the tests and print the new plan, instead of rewriting a slide deck.

Listing 13.1 is the part of the data that describes the four site types. Each entry says what to build in priority order, what to consider, what to skip and why, and at which stage of the plan this type of site can stop.

**Listing 13.1** `chapters/13-choosing-the-right-agent-interface/plan.mjs` (excerpt) — the four site types as data

```js
export const SITE_TYPES = {
  content: {
    label: 'Content site (publisher, docs, blog)',
    build: ['markup', 'content'],
    consider: ['nlweb', 'mcp'],
    skip: { webmcp: 'few actions to offer', a2a: 'no agent of your own to talk to' },
    stop: 'content',
    also: ['Verify signed agents and crawlers at your edge (Chapter 15). No grader counts it, but it is how the policy from Stage 2 gets enforced.'],
  },
  booking: {
    label: 'Booking site (rentals, restaurants, appointments)',
    build: ['markup', 'content', 'api', 'webmcp', 'mcp'],
    consider: ['a2a'],
    skip: { nlweb: 'a search box over six cabins is not worth an endpoint' },
    stop: 'trust',
  },
  saas: {
    label: 'SaaS application',
    build: ['markup', 'api', 'mcp', 'webmcp'],
    consider: ['a2a', 'content'],
    skip: { nlweb: 'your users ask your product, not your marketing pages' },
    stop: 'trust',
  },
  ecommerce: {
    label: 'E-commerce shop',
    build: ['markup', 'content', 'webmcp', 'api'],
    consider: ['mcp', 'a2a'],
    skip: {},
    stop: 'trust',
  },
};
```

The platforms get the same treatment. A platform entry says which interfaces it already covers, so the helper can move them from "build" to "configure". Listing 13.2 is the function that combines the two.

**Listing 13.2** `chapters/13-choosing-the-right-agent-interface/plan.mjs` (excerpt) — a plan is the stages up to the site type's stop, minus what the platform gives

```js
export function plan({ type, platform = 'custom', hasApi = false }) {
  const site = SITE_TYPES[type];
  if (!site) throw new Error(`Unknown site type "${type}". Use one of: ${Object.keys(SITE_TYPES).join(', ')}`);
  const given = PLATFORMS[platform] ?? PLATFORMS.custom;
  const last = STAGES.findIndex((s) => s.id === site.stop);
  const stages = STAGES.slice(0, last + 1).map((s) => ({
    ...s,
    interfaces: s.interfaces.filter((i) => site.build.includes(i) || site.consider.includes(i)),
  }));
  return {
    site: site.label,
    platformGives: given.gives,
    platformNote: given.note,
    build: site.build.filter((i) => !(hasApi && i === 'api') && !(given.covers ?? []).includes(i)).map((i) => INTERFACES[i]),
    configure: site.build.filter((i) => (given.covers ?? []).includes(i)).map((i) => INTERFACES[i]),
    consider: site.consider.map((i) => INTERFACES[i]),
    skip: Object.entries(site.skip).map(([i, why]) => `${INTERFACES[i]}: ${why}`),
    also: site.also ?? [],
    stages: stages.filter((s) => s.interfaces.length || s.id === 'basics' || s.id === 'policy' || s.id === 'trust'),
  };
}
```

Let's see it in action for a Shopify shop. Listing 13.3 is the real output of `node decide.mjs --type ecommerce --platform shopify`.

**Listing 13.3** The printed plan for an online shop on Shopify

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

Run it for your own site type with `node decide.mjs --type booking`, `--type content` or `--type saas`, add `--platform wordpress` or `--platform cloudflare`, and add `--has-api` if you already have a public API. The tests (`node --test` in the folder, 7 tests) check the rules that matter: a content site stops after content formats and skips WebMCP, a Shopify shop is told what the platform already ships, an existing API is not built again, and the stages follow the isitagentready.com levels in order.

> **Note:** The helper encodes my opinions from this chapter, dated November 2026. Fork it and change the data to your own judgment. That's the whole idea.

## What not to build

A decision framework is just as much about the doors you leave closed. Here are the ones I see teams open too early, with the reason to wait.

**An MCP server for a brochure site.** If your site has nothing to do except read, the Markdown version and llms.txt give agents everything an MCP server would, at a fraction of the cost. "Every site needs an MCP server" is one of the most overhyped claims of 2026. Transactional sites (bookings, shops, SaaS) need one, most content sites don't.

**An A2A Agent Card without an agent.** It earns an integration point on isitagentready.com and describes nothing. Publish one when you have an agent that other agents should talk to, and not before.

**An NLWeb endpoint over a small catalog.** A model and a vector store in front of six cabins add latency, cost and a new place for mistakes. A typed `search_cabins` tool answers better.

**Commerce protocols before your payment provider supports them.** Chapter 12 went through ACP, UCP, AP2, x402 and the card network programs. For a small site, the realistic path in November 2026 is an agent-safe checkout with human confirmation on your own payment page, and watching the drafts.

**Long-tail checks for the points.** isitagentready.com documents 23 checks, among them DNS-AID records, an `auth.md` file and a Personal Agent Protocol file. Their adoption is close to zero, and several of them reference proposals that may change. They belong on a watch list (Chapter 20).

**A wall against clicking agents.** It is tempting to block every browsing agent until the "proper" doors are ready. Please don't do it by default. Chapter 4 separates training crawlers, search crawlers and agents acting for a user, and the last group is often a customer trying to book. Block by purpose and by verified identity (Chapter 15), not by fear.

Each of these is a "not now", not a "never". The point is to spend your next sprint where the evidence is.

## Revisiting the decision

The ratings in Table 13.1 have a date on them for a reason. Three things should make you open this chapter's plan again.

**Your own traffic changes.** Chapter 19 shows how to classify agent traffic in your logs and how to measure what each class does on your site. If user-triggered agents start to show up in your booking funnel, the case for WebMCP and an MCP server gets stronger. If almost everything is training crawlers, your robots.txt policy matters more than any tool.

**A standard changes status.** WebMCP leaving its origin trial, a browser vendor changing its position, the MCP discovery files settling, UCP Lodging becoming final. Chapter 20 is about following those changes without chasing every draft.

**Your platform ships something.** The Shopify example shows how fast a platform can make a hand-built door redundant. Ask the four platform questions from earlier again at least twice a year.

I'd put a short review of the plan into the same calendar slot as your accessibility review. The two share half their evidence anyway, since the accessibility tree is the agent's view of the page.

## What each role takes from this chapter

- **Product managers:** choose the doors from your site type and your platform, write the targets as named checks, and keep a "not now" list with reasons. Table 13.2 is your roadmap skeleton.
- **Architects:** keep the business rules in one module and make every door a thin adapter (Figure 13.2). Decide which doors your platform covers before you design any.
- **Developers:** start with the shared rules and one door. The API or WebMCP form tools are usually the cheapest first action door, and Chapter 10's tool design work carries over to every door you add.
- **Designers:** markup and forms come first on every path in Figure 13.3, so the accessible form you design is the agent's form too.
- **Content and SEO people:** you own Stages 2 and 3, the robots.txt policy, Content Signals, the Markdown versions and llms.txt. Be honest internally about what they do and don't do for Google Search.
- **Security people:** look at control in Table 13.1, and read Part 4 before any write action is exposed.
- **QA and analytics:** turn the target checks into CI tests (Chapter 18) and watch which agent classes actually use each door (Chapter 19).

## Summary

- An agent can reach a site through eight doors: markup, content formats, a public API, an MCP server, WebMCP tools, an A2A agent, an NLWeb-style endpoint, or simply by clicking through the pages. Clicking is the baseline you always have.
- Compare the doors on cost, reliability, reach, control and maintenance. Each step from "the agent figures it out" to "the site declares it" costs more to build and gives more control and reliability.
- Reach is the honest weak spot of the newer doors in November 2026. WebMCP runs in origin trials, MCP servers have to be added by somebody, and NLWeb shows little activity. An API is portable, but consumer assistants don't call one on their own.
- Put every door on top of the same business rules. Then an extra door is mostly definitions and tests, and every agent hears the same prices and policies.
- Check what your platform already does before building. Shopify serves WebMCP tools, a UCP profile and OAuth metadata, WordPress has the Abilities API and an MCP Adapter plugin, and CDNs offer managed robots.txt, Markdown and bot verification.
- Content sites can stop after content formats. Booking sites need an API, WebMCP and MCP, plus the trust layers. SaaS applications lead with an MCP server and OAuth. Shops lean on their platform for in-page tools and commerce.
- Plan in five stages that map to the isitagentready.com levels and the Lighthouse Agentic Browsing audits, and know the graders' opinions: WebMCP doesn't change the level, Level 2 hinges on one Cloudflare-authored robots.txt line, and Level 5 rewards files a small site may not need.
- Write targets as named checks, keep a "not now" list, and revisit the plan when your traffic, the standards or your platform change.

[^ch13-1]: The decision helper `chapters/13-choosing-the-right-agent-interface/` (`plan.mjs`, `decide.mjs`, `test/plan.test.mjs`), webmaxru/agent-ready-web-demos, GitHub, https://github.com/webmaxru/agent-ready-web-demos (retrieved November 2026).
[^ch13-2]: "Introducing ChatGPT Atlas", Simon Willison's Weblog, https://simonwillison.net/2025/Oct/21/introducing-chatgpt-atlas/, "Get started with Claude in Chrome", Claude Help Center, https://support.claude.com/en/articles/12012173-get-started-with-claude-in-chrome, "Chrome gets new Gemini 3 features, including auto browse", Google blog, https://blog.google/products-and-platforms/products/chrome/gemini-3-auto-browse/, and "Browse with Copilot", Microsoft Support, https://support.microsoft.com/en-us/edge/copilot/browse-with-copilot (retrieved November 2026). Product names change often, so treat the list as a snapshot.
[^ch13-3]: "AI Insights", Cloudflare Radar, https://radar.cloudflare.com/ai-insights (retrieved November 2026). Traffic widgets for the 7 days to 2 November 2026: content type served to AI bots and the Markdown for Agents median response size.
[^ch13-4]: "A developer toolkit to make your website agent-ready", Kasper Kulikowski and Michael Hablich, Chrome for Developers, 22 June 2026, https://developer.chrome.com/blog/agent-ready-toolkit (retrieved November 2026).
[^ch13-5]: "Google's Guide to Optimizing for Generative AI Features on Google Search", Google Search Central, last updated 10 July 2026, https://developers.google.com/search/docs/fundamentals/ai-optimization-guide (retrieved November 2026).
[^ch13-6]: "Introducing Markdown for Agents", The Cloudflare Blog, 12 February 2026, https://blog.cloudflare.com/markdown-for-agents/ (retrieved November 2026). The post gives the 16,180 and 3,150 token counts and the plan availability.
[^ch13-7]: "Adoption of AI agent standards", Cloudflare Radar AI Insights, data dated 2 November 2026, 115,468 of the top 200,000 domains scanned, https://radar.cloudflare.com/ai-insights#adoption-of-ai-agent-standards (retrieved November 2026). The e-commerce numbers use the same page filtered to the Ecommerce domain category.
[^ch13-8]: "Expose REST API as MCP server", Azure API Management, Microsoft Learn, https://learn.microsoft.com/en-us/azure/api-management/export-rest-mcp-server, "Amazon Bedrock AgentCore Gateway: A secure AI gateway for agents, tools, and models", AWS documentation, https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html, "Extend your agent with tools from a REST API (preview)", Microsoft Copilot Studio documentation, https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-extend-action-rest-api, and "OpenAPI tools", Agent Development Kit, https://adk.dev/tools-custom/openapi-tools/ (retrieved November 2026).
[^ch13-9]: "Custom GPT retirement and migration FAQ", OpenAI Help Center, https://help.openai.com/en/articles/20001519-custom-gpt-retirement-and-migration-faq (retrieved November 2026).
[^ch13-10]: "WebMCP", Chrome Platform Status, feature 5117755740913664 (origin trial from Chrome 149, extended to Chrome 162), https://chromestatus.com/feature/5117755740913664, and the WebMCP trial on the Microsoft Edge origin trials page, https://developer.microsoft.com/microsoft-edge/origin-trials/trials/0b76fe60-b266-458e-a285-04e375c0c31a (retrieved November 2026).
[^ch13-11]: WebKit standards positions issue 670, https://github.com/WebKit/standards-positions/issues/670, and Mozilla standards positions issue 1412, https://github.com/mozilla/standards-positions/issues/1412 (retrieved November 2026). Mozilla has said a refreshed position is coming, and it was not published as of 2 November 2026.
[^ch13-12]: A2A releases, GitHub, https://github.com/a2aproject/A2A/releases, and "A New Chapter for A2A: Joining the Agentic AI Foundation", A2A project blog, 27 August 2026, https://a2a-protocol.org/latest/blog/2026/08/27/a-new-chapter-for-a2a-joining-the-agentic-ai-foundation/ (retrieved November 2026).
[^ch13-13]: "Introducing NLWeb: Bringing conversational interfaces directly to the web", Microsoft Source, 19 May 2025, https://news.microsoft.com/source/features/company-news/introducing-nlweb-bringing-conversational-interfaces-directly-to-the-web/ (retrieved November 2026).
[^ch13-14]: nlweb-ai/NLWeb repository, GitHub, https://github.com/nlweb-ai/NLWeb, and "NLWeb", Cloudflare AI Search documentation, https://developers.cloudflare.com/ai-search/how-to/nlweb/ (retrieved November 2026). Repository activity read through the GitHub API on 2 November 2026.
[^ch13-15]: The research for this book, 2 November 2026: the storefronts allbirds.com, brooklinen.com and kith.com, their `/.well-known/ucp` files and OAuth metadata, and the WebMCP tools their pages register. The full scan table is in the book's research notes. Shopify can change any of this at any time.
[^ch13-16]: isitagentready.com scan API (`POST https://isitagentready.com/api/scan`), scans of https://www.allbirds.com, https://www.brooklinen.com and https://kith.com run by the author on 2 November 2026, https://isitagentready.com (retrieved November 2026).
[^ch13-17]: "Abilities API in WordPress 6.9", Make WordPress Core, 10 November 2025, https://make.wordpress.org/core/2025/11/10/abilities-api-in-wordpress-6-9/ (retrieved November 2026).
[^ch13-18]: "From Abilities to AI Agents: Introducing the WordPress MCP Adapter", WordPress Developer Blog, February 2026, https://developer.wordpress.org/news/2026/02/from-abilities-to-ai-agents-introducing-the-wordpress-mcp-adapter/, and release v0.7.1 of WordPress/mcp-adapter, 16 October 2026, https://github.com/WordPress/mcp-adapter/releases/tag/v0.7.1 (retrieved November 2026).
[^ch13-19]: "Giving users choice with Cloudflare's new Content Signals Policy", The Cloudflare Blog, 24 September 2025, https://blog.cloudflare.com/content-signals-policy/ (retrieved November 2026).
[^ch13-20]: "Verified bots", Cloudflare documentation, https://developers.cloudflare.com/bots/concepts/bot/verified-bots/, and "AWS WAF announces Web Bot Auth support", AWS What's New, 21 November 2025, https://aws.amazon.com/about-aws/whats-new/2025/11/aws-waf-web-bot-auth-support/ (retrieved November 2026).
[^ch13-21]: Scans of 44 sites with isitagentready.com by the author on 2 November 2026 (5 more sites refused the scanner). Results: 8 sites at Level 4, 30 at Level 1, 6 at Level 0, none at Levels 2, 3 or 5. The full table is in the book's research notes.
[^ch13-22]: Universal Commerce Protocol, https://ucp.dev/, and "Google plans to adopt UCP draft spec for AI Mode hotel booking", Search Engine Journal, https://www.searchenginejournal.com/google-plans-to-adopt-ucp-draft-spec-for-ai-mode-hotel-booking/591235/ (retrieved November 2026). Chapter 12 covers the Lodging draft in detail.
[^ch13-23]: isitagentready.com documentation for agents, https://isitagentready.com/llms-full.txt (retrieved November 2026). The level rules are quoted verbatim.
[^ch13-24]: "Lighthouse agentic browsing scoring", Chrome for Developers, https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring, and the category configuration in Lighthouse 13.6.0, https://github.com/GoogleChrome/lighthouse/blob/main/core/config/agentic-browsing-config.js (retrieved November 2026).
[^ch13-25]: "Vocabulary For Expressing Content Signals", Internet-Draft draft-romm-aipref-contentsignals-00, IETF Datatracker, https://datatracker.ietf.org/doc/draft-romm-aipref-contentsignals/ (retrieved November 2026). The IETF AIPREF working group's own drafts are draft-ietf-aipref-vocab and draft-ietf-aipref-attach (Chapter 4).
