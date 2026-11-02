# Chapter 1: The agent-ready web

This chapter covers

- Who and what visits a website in November 2026, from training crawlers to agents that book a stay for a person
- Chrome's two stages of the agentic web: agents searching the web and agents using it
- Agent-readiness as six layers: access, perception, content, capabilities, trust and operations
- The two graders that define "agent-ready" today, what each one measures and why they disagree
- Nordlys Cabins, the running example, and a reading path for every role on a web team

Open the access logs of almost any public website and read them for ten minutes. Most of the lines are not people. Some are search engine crawlers that have visited for twenty years. Some are newer crawlers that collect text to train language models. Some are fetchers that grab one page because a person, somewhere, just asked an assistant a question about it. And a growing share look exactly like a person using Chrome, because they are a browser (driven by a model on the person's behalf) that reads the page, types into the form and presses the button.

Each of these visitors wants something different from your site. Each of them sees your site differently. And each of them can leave with the right answer, the wrong answer or no answer at all, depending on decisions your team made long before anyone said "agent" in a planning meeting.

This book is about those decisions. It answers one question: *how do I make my site work for AI agents?* In this first chapter we look at who visits a site today and how much, what "agent-ready" means when you take it apart, and how two very different tools from Cloudflare and Google turned that phrase into something you can measure. Then I introduce Nordlys Cabins, the small booking site we make agent-ready layer by layer through the rest of the book, and show which chapters matter most for your role.

## A booking nobody watched

Let's start with a scene that is completely ordinary in late 2026. A person planning a winter trip opens their browser's assistant and types: "Find a cabin in Rondane for three people from the 2nd to the 5th of December, check it is free and book it for me." Then they go back to whatever they were doing — coffee, a meeting, the kids.

The assistant opens a search result for a small cabin-rental site. What happens next depends on how that site is built.

On one version of the site, the agent finds a page whose structure tells it everything. There is a heading with the cabin's name, a form labelled "Check availability" with fields called "Check-in", "Check-out" and "Guests", and a button that says what it does. The agent fills three fields, presses the button, reads "Fjellro is available from Wed, 2 Dec 2026 to Sat, 5 Dec 2026" from a status message and follows a link called "Book these dates". If the page also declares that form as a tool, the agent does not even need to find the fields: it calls `check_availability` with three values and gets the answer.

On the other version, which looks identical to a person with a mouse, the agent finds a page made of `<div>` elements. The date fields have no labels, only grey placeholder text. The date picker is a custom calendar that opens when you click a read-only box. The "Check" button is a styled `<div>` with a click handler. The content itself arrives half a second after the page loads, which moves everything down just as the agent is about to click. An agent that reads the page's structure finds almost nothing it can name. An agent that works from screenshots can probably get through it — slowly, with many model calls and some luck.

I bet your team has a page like the second version somewhere. Most of us do.

In Chapter 2 we build exactly this experiment and run it. A small script that finds controls only by their role and name (the way agents that read the accessibility tree do) completes all 13 steps of the booking on the first version and zero steps on the second. Nobody changed the business logic. Same server, same prices, same calendar. The only difference is how the front end was written.

Please note: in this scene nobody from the cabin company was watching. No sales person saw the failed booking, no analytics dashboard showed an abandoned form with a reason, no customer wrote an angry email. The agent tried, failed and moved on to a competitor whose site worked. That is the quiet part of the agentic web, and the reason I think every web team needs a plan for it.

## Who visits your site now

"AI agent" is used for many different things, and the differences matter for a site owner. Each kind of visitor identifies itself differently — or not at all — follows different rules and wants a different kind of content. So before we talk about readiness, let's sort the visitors. I find five groups useful, ordered from "reads your content in bulk" to "acts on your site for one person right now" (Figure 1.1).

![Figure 1.1 — Five kinds of automated visitor, ordered from reading in bulk to acting for one person. Training crawlers and search crawlers read many pages ahead of time. User-triggered fetchers read one page because a person asked. Browsing agents read and click in a real browser. Tool-calling agents skip the clicking and call declared tools or APIs.](images/figure-1-1.png)

### Training crawlers

Training crawlers download pages to build the datasets that language models learn from. OpenAI's GPTBot, Anthropic's ClaudeBot, Amazon's Amazonbot and Common Crawl's CCBot are well-documented examples. Some vendors also publish *control tokens* with no crawler of their own: Google-Extended tells Google whether content may be used for Gemini training and grounding (it does not affect Google Search), and Applebot-Extended does the same for Apple's models.[^ch01-1]

What these crawlers want is volume. They never book anything, and the value they give back to a site is indirect at best. They are also the biggest group by far. On Cloudflare's network, in the seven days to 2 November 2026, 41.4% of AI crawling was declared as training only and another 41.3% as training and search combined.[^ch01-2]

### Search and answer engines

The second group fetches pages so that an AI product can cite them in answers: OpenAI's OAI-SearchBot for ChatGPT search, Anthropic's Claude-SearchBot, PerplexityBot, and of course Googlebot, whose ordinary Search crawling also feeds AI Overviews and AI Mode.[^ch01-1] This group behaves much like classic search crawlers and reads robots.txt like them. The difference is what happens to your content afterwards — and that is where the arguments start. A classic search result sends a person to your page. An AI answer may give the person what they needed without a click, with your page as a citation (or not).

Cloudflare tracks this exchange as a *crawl-to-refer ratio*: how many pages a platform crawls for every visit it sends back. In the week to 2 November 2026, Radar showed about 4,900 crawls per referral for Perplexity, about 1,400 for OpenAI, 540.8 for Anthropic and 4.8 for Google.[^ch01-2] These numbers swing a lot from week to week (Perplexity's ratio moved by almost 25% in that single week), and when Cloudflare first published the metric in June 2025 the range ran from 70,900:1 for Anthropic down to 0.1:1 for Mistral.[^ch01-3] I would not build a business case on one week of them. But the order of magnitude tells you something: for most AI platforms, the crawling is far bigger than the traffic it brings.

### User-triggered fetchers

The third group is easy to miss in logs and very important for this book. When a person asks ChatGPT, Claude, Perplexity or Gemini about a specific page ("what are the cancellation terms on this cabin site?"), the assistant fetches that page right then, for that person. These fetchers have their own user agents: ChatGPT-User, Claude-User, Perplexity-User, and Google's family of user-triggered fetchers, which includes Google-Agent for "agents hosted on Google infrastructure to navigate the web and perform actions upon user request".[^ch01-4]

Here the vendors start to differ in a way every site owner should know. OpenAI writes about ChatGPT-User that "because these actions are initiated by a user, robots.txt rules may not apply."[^ch01-5] Perplexity says its user fetcher "generally ignores robots.txt rules",[^ch01-6] and Google says its user-triggered fetchers "generally ignore robots.txt rules" too.[^ch01-4] Anthropic is the documented exception: its help centre says all three of its bots, Claude-User included, honour robots.txt.[^ch01-7] In simple words, robots.txt is a reliable way to talk to the crawlers in the first two groups, and an unreliable way to talk to this one. Chapter 4 goes through the rules per vendor, and Chapter 15 shows how to identify these visitors properly.

### Browsing agents that read and click

The fourth group drives a real browser. ChatGPT's agent mode, Claude in Chrome, Gemini in Chrome's auto browse, Microsoft Edge's "Browse with Copilot", Perplexity Comet and Opera Neon are the consumer products. Developers build the same thing with Playwright MCP, Stagehand, browser-use and the computer-use APIs that OpenAI, Anthropic and Google offer.[^ch01-8]

These agents use your site the way a person does: they look at the page, decide what to do, then click, type or scroll, and look again. Chrome's documentation calls this *actuation*. What they "look at" differs per product. web.dev's guide to agent-friendly websites says agents view a site in three ways: screenshots, raw HTML and the accessibility tree, and that modern agents combine them.[^ch01-9] Chrome's agent-ready toolkit post goes further and calls the accessibility tree the agents' "primary data model".[^ch01-10] Anthropic's browser tool documentation tells developers to prefer references from the accessibility tree over pixel coordinates, because "a reference survives layout shifts and reflows that make pixel coordinates fragile."[^ch01-11]

Two practical consequences follow. First, most browsing agents arrive with an ordinary browser user agent, because they *are* an ordinary browser. You will not see "Claude in Chrome" in your logs. Second, how well they do on your site depends mostly on things web teams already know from accessibility work: real buttons and links, labelled form fields, stable layouts. Chapter 3 is about exactly that.

### Agents that call tools

The fifth group skips the clicking altogether. Instead of operating your user interface, the agent calls a function your site declares: an operation in a documented HTTP API, a tool on a Model Context Protocol (MCP) server, or a tool the page itself registers in the browser with WebMCP. The agent sends structured input ("check-in 2026-12-02, check-out 2026-12-05, 3 guests") and gets structured output back.

This is the most reliable way for an agent to get a job done, and the one that needs the most deliberate work from the site. It is also the newest. Part 3 of this book (Chapters 7 to 13) covers each interface, how to design tools that models call correctly, how agents discover them, and how to choose between them.

### What the traffic looks like

How big is all this? The best public numbers come from Cloudflare Radar, which sees a large share of the web's traffic. Table 1.1 collects the figures I use in this book, all for the seven days to 2 November 2026.[^ch01-2]

| Measure (Cloudflare Radar, 7 days to 2 Nov 2026) | Value |
|---|---|
| HTML requests by client type | non-AI bots 54.4%, humans 35.5%, AI bots 6%, mixed purpose 4.1% |
| AI crawling by declared purpose | training 41.4%, training and search 41.3%, search 12.3%, user action 3.7%, undeclared 1.3% |
| Top AI bots by HTTP traffic | Googlebot 25%, ClaudeBot 12.2%, Meta-ExternalAgent 9.1%, Applebot 8.7%, Bingbot 7.6% |
| Content types served to AI bots | HTML 73.2%, plain text 7%, JSON 5.5%, images 4.7%, Markdown under 0.1% |
| Response status to AI bots | 200 for 59.6%, 403 for 16%, 404 for 7.5%, 301 for 5.9%, 429 for 2.6% |
| Crawls per referral | Perplexity about 4,900, OpenAI about 1,400, Anthropic 540.8, Google 4.8 |

Some lines in that table deserve a second look. Only 3.7% of AI crawling is declared as "user action", the group that books cabins. That is small today, and it is the group with the highest value per request, because behind each request is a person with a task. Sixteen percent of responses to AI bots are already 403 Forbidden, which tells you that many sites have made a decision about AI access (often at the CDN, often without the content team knowing). And Markdown, the format that agents read most cheaply, is served in under 0.1% of responses, although Radar's own measurement shows that a Markdown version of a page is, at the median, 7.9% of the size of the HTML. We come back to all three in Part 2.

> **Note:** Radar sees what Cloudflare sees: traffic on its network and the domains its scanner visits. It is the largest public dataset of its kind, not a census of the whole web. When this book quotes Radar, it gives the date, and so should you. These figures change every week.

## Searching the web and using the web

The Chrome team offers a simple way to organise all of this. In its post "A developer toolkit to make your website agent-ready" (22 June 2026), it splits the agentic web into two stages: agents *searching* the web and agents *using* the web.[^ch01-10]

When agents search, they read. They find your pages, extract what they need and fold it into an answer or a plan. Training crawlers, search crawlers and user-triggered fetchers live mostly in this stage. The Chrome post says that for this stage "the principles for Search Engine Optimization (SEO) still apply", and Google's own Search documentation is very direct about what that means for Google. Its guide to optimising for generative AI features (last updated 10 July 2026) says Google Search does not use llms.txt files, Markdown versions of pages or special schema.org markup for its AI features, and that adding them "will neither harm nor help your site's visibility or rankings in Google Search".[^ch01-12]

When agents use the web, they act. They fill forms, compare options, add things to carts, book, cancel and sign in. Browsing agents and tool-calling agents live in this stage, and here classic SEO has little to say. A page can rank first for "cabin Rondane December" and still be impossible for an agent to book. Chrome's toolkit focuses on this second stage, and so does most of this book.

I like this split because it stops two common mistakes. The first mistake is treating agent-readiness as a new kind of SEO, a list of files to add so that some AI product "ranks" you. Some of the work does help agents find and read you, and Part 2 covers it honestly, including where Google says it makes no difference. The second mistake is the opposite one: thinking agents are only about chatbots answering questions, so a site with good content has nothing to do. The moment an agent tries to *do* something on your site, a different set of properties matters, and most of them are about how the site is built.

> **Tip:** When someone on your team asks "should we do X for AI?", ask back: "for agents searching, or for agents using?" The answer usually tells you who owns the work. Searching is content, SEO and access policy. Using is front-end, API and product.

## What "agent-ready" means

Let's try a definition. A site is *agent-ready* when automated visitors can find it, are allowed in on terms the site chose, can perceive and read it accurately, can complete its key tasks reliably, and can be trusted, measured and kept working as the standards change.

That is a long sentence, and that is the point. "Agent-ready" is not one feature. It is a stack of properties, each one owned by different people on a web team, each one with its own standards and its own tools. When I started to sort the material for this book, six layers fell out of it naturally. They build on each other from the bottom up (Figure 1.2), and every chapter of the book belongs to one of them.

![Figure 1.2 — The six layers of agent-readiness and the chapters that build each one. Access decides who gets in. Perception makes the page understandable as structure. Content makes information cheap to read. Capabilities let agents act through declared interfaces. Trust covers identity, delegation, security and consent. Operations keeps it all measured, tested and current.](images/figure-1-2.png)

### Access: who gets in

The bottom layer is the decision about which automated visitors may use your site and for what. Its tools are old and new: robots.txt (an IETF standard since RFC 9309 in 2022), user-agent groups for each AI crawler, Content Signals that say whether content may be used for search, AI input or AI training, the IETF AI Preferences drafts, and the controls your CDN offers. Access is a business decision before it is a technical one. Blocking all AI training crawlers is a reasonable policy. So is welcoming them. Blocking the user-triggered fetcher that would have booked a cabin for a paying customer is usually a mistake, and it happens by accident more often than on purpose. Chapter 4 covers this layer.

### Perception: can the agent understand the page

The second layer is about the page as an agent perceives it. For browsing agents that means the accessibility tree first, the DOM second and screenshots as the expensive fallback. Semantic HTML, accessible names, labelled form controls, real dialogs and stable layouts make the page legible as structure. This is the layer where agent-readiness and accessibility for people are almost the same work, which I consider the best news in this whole book. Chapters 2 and 3 build it.

### Content: can the agent read it cheaply and correctly

The third layer is about the information on your pages, in formats machines read well. Structured data with schema.org says what a page is about in an unambiguous vocabulary. Markdown versions of pages, served through content negotiation or at predictable URLs, cut the tokens an agent spends. llms.txt offers a curated map of the site. Sitemaps and Link headers point to everything else. Chapters 5 and 6 cover this layer, with honest data on who actually reads what.

### Capabilities: can the agent act

The fourth layer lets agents do things through declared interfaces instead of guessing at buttons. A well-designed HTTP API with an OpenAPI description, an MCP server beside it, WebMCP tools in the page, discovery files that tell an agent what exists before it clicks, and, for sites that sell, the commerce protocols that are starting to appear. This is the largest layer and the one that changes fastest. Chapters 7 to 13 cover it, ending with a decision framework for choosing between the interfaces.

### Trust: should anyone let the agent act

The fifth layer makes acting safe. When an agent acts for a person, the site needs delegated, scoped and revocable access (OAuth). When an automated visitor claims to be a well-known agent, the site needs a way to check it (Web Bot Auth and HTTP message signatures). When an agent reads your content, your content can try to hijack it, so security now includes prompt injection through reviews and comments. And when an agent books something for a person, consent and the human in the loop stop being abstract. Chapters 14 to 17 cover this layer.

### Operations: does it keep working

The top layer is the boring one — and it decides whether all the others survive the next release. Testing agent-readiness in CI, measuring agent traffic and outcomes in logs and analytics, and evolving with standards that change every few months. Chapters 18 to 20 cover it.

### Why layers

Why not just a checklist? Because the layers explain *order* and *ownership*. You cannot usefully declare tools on a page whose forms are unreadable, because both the agent and your own tool descriptions depend on the same labels. A beautiful MCP server does not help if your CDN answers the agent with 403. And each layer has an owner: access is a content and legal conversation, perception belongs to designers and front-end developers, capabilities to API and product teams, trust to security, operations to QA and analytics. When a manager asks "are we agent-ready?", the honest answer is a short sentence per layer, not a yes or no.

Of course the layers leak into each other. Structured data (content) also helps discovery (capabilities). Bot identity (trust) is how you enforce access decisions. I keep those connections visible in the chapters. But as a map, six layers has worked well for me, and it is the map the rest of the book follows.

## Two graders, two definitions

For most of the web's history, "is my site ready for X?" had a familiar answer: run the audit. Lighthouse for performance, axe for accessibility, the Rich Results Test for structured data. In 2026 agent-readiness got its audits too. Two of them matter more than all the others, because they come from the companies that run much of the infrastructure agents travel through: Cloudflare and Google. They are free, they are well documented, and they measure very different things.

### isitagentready.com

Cloudflare launched isitagentready.com on 17 April 2026, during its Agents Week, with the blog post "Introducing the Agent Readiness score. Is your site agent-ready?"[^ch01-13] You give it a URL. Cloudflare's servers fetch a set of well-known paths and headers from your site, query DNS, and load the page in a headless browser to look for WebMCP tools. The result is a status per check (pass, fail, neutral or unable to check), evidence for each one, and a *level* from 0 to 5.

As of November 2026 the scanner documents 23 checks in five categories:[^ch01-14]

- *Discoverability*: robots.txt, a sitemap, Link response headers with agent-useful relations, and DNS records for AI discovery (DNS-AID).
- *Content accessibility*: Markdown content negotiation (`Accept: text/markdown` on the homepage returns Markdown).
- *Bot access control*: AI bot rules in robots.txt, Content Signals in robots.txt, and a Web Bot Auth key directory (informational).
- *Discovery*: an MCP Server Card, an A2A Agent Card, an Agent Skills index, WebMCP tools, an API catalog, OAuth discovery metadata, OAuth Protected Resource Metadata, Auth.md, an Agentic Resource Discovery (ARD) manifest and the Personal Agent Protocol (informational).
- *Commerce*: x402, MPP, UCP, ACP and AP2, scored only when the scanner detects that the site sells something.

The levels are a ladder (Table 1.2). Each level requires the one below it.

| Level | Name | Requirement (as documented on 2 Nov 2026) |
|---|---|---|
| 0 | Not Ready | does not meet Level 1 |
| 1 | Basic Web Presence | 2 of 3: robots.txt, sitemap, Link headers |
| 2 | Bot-Aware | Level 1, plus both AI bot rules and Content Signals in robots.txt |
| 3 | Agent-Readable | Level 2, plus Markdown content negotiation |
| 4 | Agent-Integrated | Level 3, plus 1 of 4: MCP Server Card, A2A Agent Card, Agent Skills, API Catalog |
| 5 | Agent-Native | Level 4, plus 2 of 3: Web Bot Auth, all four integration checks, auth metadata |

The tool is agent-ready itself, which I appreciate. It has a JSON API (`POST https://isitagentready.com/api/scan`), an MCP server with a single `scan_site` tool, and for each failing check it offers a prompt you can hand to a coding agent. The same checks power an "Agent readiness" tab in Cloudflare's URL Scanner and the adoption data on Radar.

What isitagentready measures, in simple words, is *what your server publishes*: files at known paths and headers on known responses. It is a fast, objective way to answer "have we told agents what we offer, in the formats they look for?"

### Lighthouse Agentic Browsing

Google added an "Agentic Browsing" category to Lighthouse in version 13.2.0 (1 May 2026) and put it in the default configuration in 13.3.0 a week later.[^ch01-15] It needs Chrome 150 or later. In Lighthouse 13.6.0, the current release in November 2026, the category has seven audits:[^ch01-16]

- `agent-accessibility-tree`: the accessibility tree is well formed. It fails if any of 33 axe-core rules fails (button and link names, form labels, valid ARIA and similar).
- `webmcp-form-coverage`: lists forms that do not declare a WebMCP tool.
- `webmcp-registered-tools`: lists the WebMCP tools the page registers and warns above 40.
- `webmcp-schema-validity`: checks that declared tools have valid names, descriptions and parameters.
- `cumulative-layout-shift`: the familiar Core Web Vitals metric, because layout shifts make agents click the wrong thing.
- `llms-txt`: if the site has an llms.txt, it should have a heading, at least one link and some content.
- `ard-schema`: if the site publishes an ARD manifest, it should be valid.

The category does not produce a 0 to 100 score. The report shows a fraction of passed audits, and Chrome's documentation calls it "informational and unbenchmarked". The WebMCP audits only see tools when Chrome runs with the WebMCP origin trial or its testing flag. And the category's own description in the Lighthouse source says it is "still under development and subject to change".

What Lighthouse measures is *the page as an agent perceives it*: its accessibility tree, its stability, the tools it declares. It is the right tool for a front-end developer who wants to know whether a template change broke something for agents.

### Why they disagree

Put the two graders side by side and they hardly overlap (Figure 1.3). isitagentready looks at the server and never reads your accessibility tree. Lighthouse looks at one page and never checks your robots.txt for AI rules or your MCP server card. Only two things appear in both: WebMCP (which isitagentready detects but does not count towards the level) and ARD (which they look for at different paths).

![Figure 1.3 — What the two graders check, mapped onto the six layers. isitagentready.com reads files and headers the server publishes (access, content formats, discovery, commerce). Lighthouse Agentic Browsing loads one page and checks perception, stability and in-page tools. WebMCP and ARD are the only overlaps.](images/figure-1-3.png)

When the research for this book scanned 44 well-known sites with isitagentready on 2 November 2026 (five more refused the scanner), nobody sat at Level 2, 3 or 5. Sites were either at Level 0 or 1 (36 of them) or at Level 4 (8).[^ch01-17] The Level 4 group was Cloudflare's own properties, isitagentready.com itself, docs.stripe.com, supabase.com, netlify.com and modelcontextprotocol.io. vercel.com is the interesting case. It serves Markdown negotiation, an API catalog, OAuth discovery, an Agent Skills index, an ARD manifest and four WebMCP tools, and it is still at Level 1, because its robots.txt has no Content Signals line and Level 2 requires one.

The same day, Lighthouse runs on developer.chrome.com, vercel.com and isitagentready.com all failed `agent-accessibility-tree`, each time on the same axe rule: "Links must have discernible text" (an image link or a card link without an accessible name).[^ch01-17] isitagentready.com also failed Lighthouse's `llms-txt` audit, with the message "File does not appear to contain any links." So Cloudflare's agent-readiness tool fails Google's agent-readiness audit, and Google's own developer site fails it too. I find that comforting, to be honest — it shows how new all of this is.

There are three reasons for the disagreement, and they are worth understanding before you put either score in a quarterly report.

They ask different questions. isitagentready asks "has this site published the things agents look for?" Lighthouse asks "can an agent make sense of this page?" Both are fair questions. Neither covers the whole stack.

They encode opinions. A level is somebody's view of priority. isitagentready's ladder makes Content Signals (a robots.txt extension that Cloudflare authored and that is an individual IETF draft, not a working group document) a hard gate for Level 2, while WebMCP does not count at all. Its "AI bot rules" check passes for a robots.txt that has only a wildcard `User-agent: *` group, so it says nothing about whether you made a decision about AI crawlers. Lighthouse, in turn, checks 33 accessibility rules that agents need and leaves out the ones they do not (colour contrast, for example), which makes it a floor for agents and not an accessibility audit for people.

They move. Lighthouse changed the category in every minor release since May 2026. Version 13.6.0 (27 October 2026) moved the ARD manifest to `/.well-known/ard.json` and now warns that `/.well-known/ai-catalog.json` is a legacy location, while isitagentready's fix prompt still tells sites to publish `ai-catalog.json`. A site that follows one grader's advice today can get a warning from the other one tomorrow.

> **Warning:** Do not put "reach Level 4" or "pass all agentic audits" in your roadmap as a goal in itself. Use the checks as instruments. Report per-check changes, decide which checks are irrelevant for your site (commerce protocols on a documentation site, for example) and say so explicitly, so nobody chases points.

### How this book uses the graders

This book treats the two graders as complementary instruments, and it uses them in every chapter that adds a layer. Each of those chapters ends its hands-on part by re-running both: isitagentready (or, for a site on `localhost`, a local re-implementation of its documented checks that we write in Chapter 2) and Lighthouse's Agentic Browsing category. Each says which check ids moved. Chapter 18 turns the same measurements into CI, and Chapter 20 applies the whole ladder to this book's own web edition.

The habit I want you to take from this book is the one in Chapter 2: measure, change one layer, measure again. A score you cannot explain is useless. A per-check change you caused is information.

## Where the web is in November 2026

How many sites have done any of this? Again Radar has the best public answer. Since April 2026 its "Adoption of AI agent standards" widget reports, every week, how many of the top 200,000 domains pass each isitagentready check. The snapshot of 2 November 2026 covers 115,468 domains that were scanned successfully (Table 1.3).[^ch01-18]

| Check (Radar, 115,468 domains, 2 Nov 2026) | Domains passing | Share |
|---|---|---|
| robots.txt | 98,741 | 85.5% |
| AI rules in robots.txt (wildcards count) | 95,630 | 82.8% |
| Sitemap | 81,594 | 70.7% |
| Link headers | 11,252 | 9.7% |
| Content Signals | 10,279 | 8.9% |
| OAuth discovery | 9,323 | 8.1% |
| Universal Commerce Protocol (UCP) | 5,429 | 4.7% |
| Markdown negotiation | 4,924 | 4.3% |
| OAuth Protected Resource | 4,775 | 4.1% |
| WebMCP | 1,643 | 1.42% |
| API catalog | 852 | 0.74% |
| MCP Server Card | 699 | 0.61% |
| Agent Skills | 687 | 0.59% |
| ARD | 331 | 0.29% |
| Web Bot Auth | 118 | 0.10% |
| x402 | 7 | under 0.01% |

The basics are everywhere, the agent-specific parts are rare, and there is a cliff right after the files most sites published years ago for search engines. Compare with Cloudflare's first measurement in April 2026, which found robots.txt on 78% of sites, Content Signals on 4%, Markdown negotiation on 3.9%, and MCP Server Cards together with API catalogs on fewer than 15 sites in the whole dataset.[^ch01-13] The two measurements were not made in exactly the same way (the April dataset was filtered differently), so compare them with care. Still, in about seven months Content Signals more than doubled and the discovery files went from a handful of domains to hundreds. Small numbers, moving fast. That is exactly the moment when the cost of getting ahead is low.

### Platforms move the needle

Look at UCP and WebMCP in that table. The Universal Commerce Protocol is on 4.7% of the top domains and WebMCP on 1.42%, far more than most of the discovery files. Did thousands of shop owners read the specs over the summer? Of course not. Their platform did it for them. When the book's research scanned Shopify storefronts (allbirds.com, brooklinen.com and kith.com) on 2 November 2026, each one shipped a WebMCP adapter with 12 tools such as `search_catalog`, `add_to_cart` and `proceed_to_checkout`, a UCP profile at `/.well-known/ucp` and OAuth metadata, all by default.[^ch01-17] Radar's e-commerce category shows the same picture: WebMCP on 928 of 18,927 e-commerce domains and UCP on 4,181.[^ch01-18] Ilya Grigorik of Shopify put it plainly in the W3C discussion about a future Agentic Web Working Group: "Shopify deploys WebMCP across millions of storefronts."[^ch01-19]

Cloudflare works the same way for its customers. When it announced its Content Signals Policy in September 2025, its managed robots.txt feature was already serving over 3.8 million domains, and turning on Content Signals for them was a setting.[^ch01-20] Its Markdown for Agents feature converts HTML to Markdown at the edge for zones that enable it.

That gives us the first practical rule of this book: *check what your platform already does before you build anything*. If your shop runs on a platform that publishes UCP and WebMCP tools, your job is to know what they say about you, test them and fill the gaps, not to write your own. If your CDN can add Content Signals or serve Markdown, the decision is about policy, and the implementation is a toggle. Chapter 13 turns this into a staged plan per site type.

### Does it pay off?

Fair question, and I want to answer it carefully, because this is where agent-readiness marketing gets loud. As of November 2026 there is no public, independent study that shows how many bookings or sales agents bring to sites that are agent-ready compared to sites that are not. Anyone who quotes you such a conversion number should be asked for the source.

What we do have is evidence about cost and reliability, which is where the business case starts. When Cloudflare reworked its own developer documentation for agents (Markdown versions of every page, llms.txt files per section, cleaner structure), it ran a benchmark: an agent (Kimi-k2.5 in OpenCode) answering very specific technical questions from Cloudflare's documentation "consumed 31% fewer tokens and arrived at the correct answer 66% faster than the average site that is not refined for agents."[^ch01-13] Its Markdown for Agents announcement measured one blog post at 16,180 tokens as HTML and 3,150 as Markdown, a reduction of about 80%.[^ch01-21] Fewer tokens and fewer steps mean an agent is cheaper to run on your site and less likely to give up or get it wrong. For a site that wants agents to complete tasks, that is the metric that matters first.

And then there is the experiment in Chapter 2, which you can run yourself in ten minutes: the same booking, 13 of 13 steps on a semantic page, zero on a `<div>` page. Bottomline: today the honest business case is "agents can complete our key tasks, cheaply and reliably, and we can see them do it". Revenue attribution comes later, and Chapter 19 shows how to start collecting the data for it.

### Why now

Every few years the web gets a new kind of client that sites have to learn to serve. Search crawlers in the late 1990s. Mobile browsers around 2010. Installable, offline-capable web apps a few years later (the topic I spent a big part of my community life on, as a long-time progressive web app speaker and writer). Each time, the sites that understood the new client early got an advantage that lasted longer than anyone expected, and the sites that waited paid more later to catch up under pressure.

Agents are that new client now. Let's have a look at why late 2026 is a good moment to start. First, the measurement exists, so you can see where you are in an afternoon. Second, the standards are young but real: robots.txt and accessibility are mature, structured data and OAuth are mature, and MCP, WebMCP, Web Bot Auth and the commerce protocols are moving through standards bodies and shipping in products. And third, the big platforms are clearly committing. Chrome ships an agentic Lighthouse category and a WebMCP origin trial. UCP published a draft for lodging bookings on 25 September 2026, co-developed by companies such as Amadeus, Booking.com, Expedia Group, Google, Hilton, Marriott and Trip.com.[^ch01-22] For a booking site like the one in this book, that is a signal hard to ignore.

## Meet Nordlys Cabins

A book about making sites agent-ready needs a site. Ours is *Nordlys Cabins* (nordlys.example), a small, fictional company that rents six cabins in Norway, from Fjellro in Rondane, a timber mountain cabin for six with a fireplace and ski-in access, to Reine Rorbu, a fisherman's cabin for two in Lofoten. "Nordlys" is Norwegian for the northern lights. Living in Oslo, I could not resist :)

I chose a booking site on purpose, and the more research went into this book, the better the choice looked. A booking site has everything the book needs: public content that agents read (cabins, a travel guide, an FAQ), a search with filters, an availability check with dates, a booking form with personal data, a confirmation with a reference number, member accounts with "my bookings", a cancellation flow with money attached, and reviews written by other people. It is small enough to understand completely, and real enough that every layer has something to change. And, as we saw above, the lodging industry now has its own draft commerce standard.

The site is a small Node.js application (Hono on Node 24, with data in memory) in the book's public demos repository, webmaxru/agent-ready-web-demos, folder `nordlys-cabins/`. Two things about it matter before Chapter 2.

### Two front ends

Nordlys Cabins has two front ends over the same business logic. The *clean* front end is what I would write today: semantic HTML, native form controls with labels, real links and buttons, landmarks, server-rendered content that works without JavaScript. The *legacy* front end is what many real booking sites still ship, built on purpose to be hostile to agents and assistive technology: clickable `<div>` elements instead of links and buttons, a custom date picker behind a read-only input, placeholder-only fields, icon buttons without names, a "modal" without dialog semantics, and content that JavaScript injects late.

Both front ends work for a sighted person with a mouse. You can book a cabin through either of them. That is exactly why the legacy one is useful: it is the kind of site that passes every manual test a busy team runs, and still fails the visitors this book is about.

### One layer per chapter

The second thing is the layer system. Every chapter that changes the site adds one folder, `nordlys-cabins/layers/NN-slug/`, which plugs robots.txt files, headers, head tags, page scripts, routes and middleware into the app through a small set of hooks, without touching the shared application code. You start the site "as it is after Chapter N" with one flag. So you can always compare before and after, and so can the graders.

> **Hands-on:** If you want to run the site now, you need Node.js 24 or later and Git. The commands below start the clean site with every layer, then the legacy baseline that Chapter 2 begins with. If you do not run code, skip to "Reading paths for every role". Nothing later in this chapter depends on it.

```sh
git clone https://github.com/webmaxru/agent-ready-web-demos.git
cd agent-ready-web-demos
npm install
npm start                                   # clean front end, every layer, http://127.0.0.1:3000
npm start -- --upto=6                       # the site as it is after Chapter 6
npm run start:baseline -w nordlys-cabins    # legacy front end, no layers: the Chapter 2 baseline
```

`GET /__layers` on a running site lists which layers are on and what each one registered, which is handy when a grader result surprises you.

Through the book Nordlys Cabins climbs both graders. In Chapter 2 it gets a robots.txt, a sitemap and its first declared tool. In Part 2 it gets AI crawler rules, Content Signals, structured data, Markdown versions of its pages and an llms.txt. In Part 3 it gets a public API, an MCP server, WebMCP tools, discovery files and an agent-safe checkout. Part 4 adds delegated access for "my bookings", signature verification for bots, a threat model and consent flows. Part 5 tests and measures it all. At every step you can see which checks moved and why.

## Reading paths for every role

Agent-readiness is a whole-team job, and this book is written for the whole team. Every chapter starts with plain-language sections that explain what the layer is, why it matters and what it costs. Sections with code begin with a "Hands-on" note that tells you what the code achieves and where to pick up again if you skip it. You do not need to write JavaScript to get value from any chapter. If you do write JavaScript or TypeScript, the hands-on sections and the demos repository are where you will spend most of your time.

Still, not everyone needs every chapter in the same depth. Table 1.4 is my suggestion for a first read per role. Read your row first, skim the rest, and use Appendix A (a checklist per role) when you are ready to act.

| Role | Read first | Then | Skim |
|---|---|---|---|
| Front-end developer | 2, 3, 9, 10 | 6, 11, 13, 16, 18 | 4, 12, 19 |
| Full-stack or back-end developer | 2, 7, 8, 10 | 11, 12, 13, 14, 15, 16, 18 | 3, 5 |
| Designer (UX, UI, design system) | 2, 3 | 10, 13, 17 | 9, 16 |
| Content, SEO or marketing | 1, 4, 5, 6 | 11, 19, 20 | 3, 12 |
| Product manager | 1, 2, 13 | 4, 12, 17, 19, 20 | 7 to 11 |
| Architect or tech lead | 1, 13, 7, 8 | 11, 14, 15, 16, 20 | everything else |
| QA and test engineer | 2, 3, 18 | 10, 13, 16 | 19 |
| Security engineer | 15, 16, 14 | 4, 8, 9, 17 | 12 |
| Analytics and growth | 1, 19 | 4, 6, 13, 20 | 15 |

Two chapters are worth everyone's time. Chapter 2 is short on theory and shows the whole loop (measure, fix, measure again) on one page, so it gives a team a shared picture in an hour. Chapter 13, "Choosing the right agent interface", is where the team decides what to build, and it goes better when people from more than one row of that table are in the room.

## What this book is and is not

A few promises, so you know what to expect.

The book is vendor-agnostic. It teaches the standard first and then shows the products that implement it, with at least two options wherever vendors compete. You will see Cloudflare, Google, Microsoft, OpenAI, Anthropic, Vercel, AWS, Shopify and others by name, because they ship the things a web team actually uses.

The book is written from the site owner's point of view. It is not about building agents. When it shows agent code (a browsing script, an MCP client, an eval), it is there to test your site.

The book is honest about evidence. Agent-readiness attracts a lot of marketing. Every number in this book comes with its source and date, every standard with its status (Recommendation, RFC, draft, proposal or vendor document), and when a vendor says a technique does nothing for its product (as Google does for llms.txt and Google Search), I say so, even when the technique still helps elsewhere. Boxes marked "Still in flux" warn you where things are likely to change after November 2026.

The book is not an SEO book, although Part 2 overlaps with SEO, and it is not a WebMCP book. WebMCP is one layer here, with one chapter. If you want the whole story of in-page tools, my previous book, "Tools, Not Clicks: Building Agent-Ready Websites with WebMCP", covers it in depth, and its web edition is free at https://webmcp.salnikov.no.

And the book is not legal advice. Chapters 4, 16 and 17 touch copyright reservations, data protection and the EU AI Act with dates and sources, and they point you to the people in your organisation who should make those calls.

## Summary

- Automated visitors fall into five groups with different needs and rules: training crawlers, search and answer crawlers, user-triggered fetchers, browsing agents that read and click, and agents that call tools. User-triggered fetchers and browsing agents act for one person right now, and several vendors say robots.txt may not apply to them.
- Cloudflare Radar (seven days to 2 November 2026) shows AI bots at 6% of HTML requests plus 4.1% mixed purpose, 82.7% of AI crawling declared as training or training plus search, Markdown in under 0.1% of responses to AI bots and 16% of those responses refused with 403.
- Chrome splits the agentic web into agents searching it, where SEO principles still apply, and agents using it, where the structure of your pages and interfaces decides whether a task succeeds.
- Agent-readiness is a stack of six layers: access, perception, content, capabilities, trust and operations. Each has its own standards, tools and owners, and the book follows that order.
- isitagentready.com checks what your server publishes (23 checks, Levels 0 to 5). Lighthouse's Agentic Browsing category checks the page as an agent perceives it (seven audits, shown as a fraction). They barely overlap, encode different opinions, change often and even fail each other's tools. Use both as instruments and report per-check changes.
- Adoption is low and uneven: robots.txt on 85.5% of the top domains, Content Signals on 8.9%, Markdown negotiation on 4.3%, WebMCP on 1.42% and MCP Server Cards on 0.61% (Radar, 2 November 2026). Platforms such as Shopify and Cloudflare move these numbers far more than individual sites, so check what your platform already does first.
- Nordlys Cabins, a fictional cabin-rental site with a clean and a deliberately agent-hostile legacy front end, becomes agent-ready one layer per chapter, and every step is measured with both graders.

[^ch01-1]: Vendor documentation of AI crawlers: OpenAI, "Overview of OpenAI Crawlers", https://platform.openai.com/docs/bots, Google, "Google's common crawlers", https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers, Apple, "About Applebot", https://support.apple.com/en-us/119829, Amazon, "Amazon Web Search crawlers", https://developer.amazon.com/amazonbot, and Common Crawl, "CCBot", https://commoncrawl.org/ccbot (all retrieved November 2026).
[^ch01-2]: Cloudflare Radar, "AI Insights", https://radar.cloudflare.com/ai-insights, traffic widgets for the seven days from 26 October to 2 November 2026 (retrieved November 2026).
[^ch01-3]: Cloudflare blog, "The crawl before the fall… of referrals: understanding AI's impact on content providers", https://blog.cloudflare.com/ai-search-crawl-refer-ratio-on-radar/ (retrieved November 2026).
[^ch01-4]: Google for Developers, "Google User-Triggered Fetchers", https://developers.google.com/search/docs/crawling-indexing/google-user-triggered-fetchers (retrieved November 2026).
[^ch01-5]: OpenAI, "Overview of OpenAI Crawlers", https://platform.openai.com/docs/bots (retrieved November 2026).
[^ch01-6]: Perplexity, "Perplexity Crawlers", https://docs.perplexity.ai/guides/bots (retrieved November 2026).
[^ch01-7]: Claude Help Center, "Does Anthropic crawl data from the web, and how can site owners block the crawler?", https://support.anthropic.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler (retrieved November 2026).
[^ch01-8]: Product documentation: Claude Help Center, "Get started with Claude in Chrome", https://support.claude.com/en/articles/12012173-get-started-with-claude-in-chrome, Google, "The new era of browsing: Putting Gemini to work in Chrome", https://blog.google/products-and-platforms/products/chrome/gemini-3-auto-browse/, Microsoft Support, "Browse with Copilot", https://support.microsoft.com/en-us/edge/copilot/browse-with-copilot, and Microsoft, "Playwright MCP server", https://github.com/microsoft/playwright-mcp (all retrieved November 2026).
[^ch01-9]: web.dev, "Build agent-friendly websites", https://web.dev/articles/ai-agent-site-ux (retrieved November 2026).
[^ch01-10]: Chrome for Developers, "A developer toolkit to make your website agent-ready", 22 June 2026, https://developer.chrome.com/blog/agent-ready-toolkit (retrieved November 2026).
[^ch01-11]: Claude Docs, "Browser use tool", https://platform.claude.com/docs/en/agents-and-tools/tool-use/browser-use-tool (retrieved November 2026).
[^ch01-12]: Google Search Central, "Google's Guide to Optimizing for Generative AI Features on Google Search", https://developers.google.com/search/docs/fundamentals/ai-optimization-guide (retrieved November 2026).
[^ch01-13]: Cloudflare blog, "Introducing the Agent Readiness score. Is your site agent-ready?", 17 April 2026, https://blog.cloudflare.com/agent-readiness/ (retrieved November 2026).
[^ch01-14]: isitagentready.com, "Is Your Site Agent-Ready? Full Documentation", https://isitagentready.com/llms-full.txt (retrieved November 2026).
[^ch01-15]: GoogleChrome/lighthouse on GitHub, release notes for v13.2.0, v13.3.0 and v13.6.0, https://github.com/GoogleChrome/lighthouse/releases (retrieved November 2026).
[^ch01-16]: Chrome for Developers, "Lighthouse agentic browsing scoring", https://developer.chrome.com/docs/lighthouse/agentic-browsing/scoring, and the Lighthouse 13.6.0 source, core/config/agentic-browsing-config.js, https://github.com/GoogleChrome/lighthouse (retrieved November 2026).
[^ch01-17]: Scans made for this book on 2 November 2026: 49 sites submitted to https://isitagentready.com/api/scan (44 answered), and Lighthouse 13.6.0 runs of the Agentic Browsing category in Chromium 156 with the WebMCP testing flag.
[^ch01-18]: Cloudflare Radar, "AI Insights: Adoption of AI agent standards", https://radar.cloudflare.com/ai-insights#adoption-of-ai-agent-standards, snapshot of 2 November 2026, including the Ecommerce domain category (retrieved November 2026).
[^ch01-19]: Comment by Ilya Grigorik on the W3C Agentic Web Working Group charter discussion, https://github.com/w3c/strategy/issues/576 (retrieved November 2026).
[^ch01-20]: Cloudflare blog, "Giving users choice with Cloudflare's new Content Signals Policy", 24 September 2025, https://blog.cloudflare.com/content-signals-policy/ (retrieved November 2026).
[^ch01-21]: Cloudflare blog, "Introducing Markdown for Agents", 12 February 2026, https://blog.cloudflare.com/markdown-for-agents/ (retrieved November 2026).
[^ch01-22]: Universal Commerce Protocol, https://ucp.dev/, Lodging section and co-developer list (retrieved November 2026).
