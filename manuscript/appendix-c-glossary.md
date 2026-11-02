# Appendix C: Glossary

Agent-readiness borrows words from accessibility, search, web standards, security and AI, and every one of those communities uses a few of them differently. This glossary gives the meaning each term has in this book, in one or two plain sentences, so a designer, a product manager and a security engineer can read the same chapter and mean the same thing. The chapter in brackets is where the term is taught in depth. Terms in *italics* inside a definition have their own entry.

## A

**A2A (Agent2Agent protocol)**: An open protocol for one AI agent to discover another and hand it a task, with an *agent card* that describes what the agent can do. Version 1.0 was released in March 2026 and the project is part of the *Agentic AI Foundation*. (Chapters 11 and 13)

**Accessibility tree**: The structure a browser builds from the page for assistive technology: every element's *role*, *accessible name* and state. Many browser agents read the page through it, which makes it the cheapest agent interface you have. (Chapter 3)

**Accessible name**: The text that identifies an element in the *accessibility tree*, such as a button's label or a link's text. An icon button without one is invisible to a screen reader and to an agent alike. (Chapter 3)

**Access token**: A short-lived credential that a client sends with each API or MCP request to prove what it is allowed to do. In this book it is an OAuth bearer token issued for one *resource* with specific *scopes*. (Chapter 14)

**ACP (Agentic Commerce Protocol)**: A checkout protocol by OpenAI and Stripe that lets an AI product buy from a merchant while the merchant stays the merchant of record. It is in beta, with dated releases. (Chapter 12)

**Agent**: In this book, software driven by a language model that pursues a goal for a person by reading pages, calling tools or clicking through a site. A *crawler* collects content. An agent tries to get something done. (Chapter 1)

**Agent card**: A JSON document, served at `/.well-known/agent-card.json`, that describes an *A2A* agent: its name, version, skills and how to reach it. (Chapter 11)

**Agent evaluation (eval)**: A repeatable test in which a real model attempts tasks against your site or tools, and you score how often it succeeds. Evals catch the problems deterministic audits cannot, such as a tool description that misleads the model. (Chapters 10 and 18)

**Agentic AI Foundation (AAIF)**: A Linux Foundation home for agent protocols. MCP and A2A both sit there. (Chapter 20)

**Agentic browser**: A web browser with a built-in agent that can act on pages for its user, such as Gemini in Chrome, ChatGPT Atlas or Claude in Chrome. (Chapters 1 and 16)

**Agentic Browsing category**: The Lighthouse report category that audits a page as an agent sees it: the *accessibility tree*, layout stability, *WebMCP* tools, *llms.txt* and the *ARD* manifest. It shows a pass ratio rather than a 0–100 score. (Chapters 2 and 18)

**Agentmap**: A robots.txt line that points to a site's *ARD* manifest. Lighthouse checks it first when it looks for the manifest. (Chapter 11)

**Agent Skills**: Packaged instructions and resources that teach an agent how to do a specific job. A site can list the skills it publishes in an index at `/.well-known/agent-skills/index.json`. (Chapter 11)

**AI crawler**: A *crawler* run by an AI company, for training models, for building a search index, or both. Each has its own *user agent* token, such as GPTBot or ClaudeBot. (Chapter 4)

**AI Mode and AI Overviews**: Google Search's AI features: AI Overviews put a generated summary above the results, and AI Mode is a conversational search experience. Ordinary Googlebot crawling feeds both. (Chapters 1 and 4)

**aipref**: The IETF working group on AI preferences, and the vocabulary it is drafting for saying how content may be used: `train-ai`, `ai-use` and `search`. Its drafts attach those preferences through the *Content-Usage* header and robots.txt. (Chapter 4)

**AP2 (Agent Payments Protocol)**: A protocol for proving that a person authorized a purchase an agent makes, using signed *mandates*. It works as an extension of A2A and UCP and has been donated to the FIDO Alliance. (Chapter 12)

**API catalog**: A list of a site's APIs and their descriptions, served at `/.well-known/api-catalog` as a *linkset* (RFC 9727). It lets a client discover your APIs without reading your documentation. (Chapters 7 and 11)

**API gateway**: A managed service in front of your APIs that handles authentication, quotas and routing. Several gateways, such as Azure API Management and Amazon Bedrock AgentCore Gateway, can now expose an existing REST API as MCP tools. (Chapter 7)

**Arazzo**: An OpenAPI Initiative specification for describing multi-step API workflows, such as "check availability, then book", so a client can follow them in order. (Chapter 7)

**ARD (Agentic Resource Discovery)**: A proposal for one manifest that lists the MCP servers, agents and skills a domain offers, served at `/.well-known/ard.json` in version 0.91. Lighthouse validates it in the `ard-schema` audit. (Chapter 11)

**ARIA (WAI-ARIA)**: The W3C attributes that add roles, names and states to HTML when native elements cannot express them. The first rule of ARIA, use a native element if one exists, applies to agents just as much. (Chapter 3)

**auth.md**: A proposed plain-language file that explains to agents how to authenticate with a site, paired with authorization-server metadata. isitagentready accepts it as one of its Level 5 auth options. (Chapters 11 and 14)

**Authorization server**: The service that signs users in, asks for consent and issues *access tokens*. It describes itself in metadata at `/.well-known/oauth-authorization-server` or `/.well-known/openid-configuration`. (Chapter 14)

## B

**Bot**: Any automated client. In this book "bot" usually means the unwanted kind, such as scrapers and credential stuffers, and the question of Chapter 15 is how to tell them from legitimate *agents*. (Chapter 15)

**Bot management**: The tools at the edge (a CDN, a WAF or your own middleware) that classify, allow, challenge or block automated traffic. (Chapter 15)

## C

**CIMD (Client ID Metadata Document)**: A way for an OAuth client to identify itself by a URL that points to a JSON document about it, instead of registering in advance. The MCP authorization spec recommends it and has deprecated *Dynamic Client Registration*. (Chapter 14)

**Confirmation**: A step where a human approves an action before an agent completes it, such as paying or cancelling a booking. The site, the browser or the agent can ask for it, and the risky ones should never rely on the agent alone. (Chapters 16 and 17)

**Confused deputy**: A program with more authority than the party it acts for, tricked into using that authority for them. An agent with a user's session that follows instructions hidden in a page is the classic case. (Chapter 16)

**Content negotiation**: HTTP's way of serving different representations of the same URL depending on the request headers. In this book it mostly means returning *Markdown* when the client sends `Accept: text/markdown`. (Chapter 6)

**Content Signals**: Cloudflare's robots.txt extension, a `Content-Signal` line that says whether content may be used for search, as AI input or for AI training. isitagentready requires it for Level 2. (Chapter 4)

**Content-Usage**: The HTTP header and robots.txt rule that the IETF *aipref* drafts define for usage preferences. It is a different mechanism from *Content Signals*, with different labels. (Chapter 4)

**Control token**: A robots.txt user-agent name that no crawler fetches under, such as Google-Extended or Applebot-Extended. The vendor reads your rules for it before using content its normal crawlers collected for AI training. (Chapter 4)

**Crawl-to-referral ratio**: How many pages an AI company's crawlers fetch for each visitor its products send back to the site. Cloudflare Radar publishes it per company. (Chapters 1 and 19)

**Crawler**: A program that fetches pages in bulk, following links or a sitemap, to build an index or a dataset. A crawler is governed by robots.txt. (Chapter 4)

**Cumulative Layout Shift (CLS)**: A measure of how much a page's content moves while it loads. Moving content makes an agent click the wrong thing, which is why CLS is part of the Agentic Browsing category. (Chapter 3)

## D

**Declarative tool**: A *WebMCP* tool defined in HTML by adding `toolname` and `tooldescription` to a form, with no JavaScript. (Chapter 9)

**Delegated access**: Permission a person grants to an agent to act for them, limited in scope and time and revocable. OAuth is the standard way to grant it. (Chapter 14)

**Deprecation header**: An HTTP response header (RFC 9745) that tells clients an endpoint or tool is deprecated and since when. It pairs with the *Sunset header*. (Chapter 20)

**DNS-AID**: An individual IETF draft for discovering agents through DNS records under an `_agents` label. isitagentready checks it, but it does not count toward any level. (Chapter 11)

**DPoP**: A way to bind an *access token* to a key the client holds (RFC 9449), so a stolen token alone is useless. (Chapter 14)

**Dynamic Client Registration (DCR)**: The OAuth protocol (RFC 7591) by which a client registers itself with an authorization server at run time. MCP deprecated it in favour of *CIMD* in the 2026-07-28 revision. (Chapter 14)

## E

**Elicitation**: An MCP feature in which a server asks the user for more information during a tool call. In the 2026-07-28 spec it is part of *Multi Round-Trip Requests*. (Chapter 17)

**Enterprise-Managed Authorization**: An MCP extension that lets a company's identity provider grant agents access to approved MCP servers at sign-in, without a consent screen per server. It uses *ID-JAG*. (Chapter 14)

**EU AI Act**: The European Union's regulation on AI systems, with obligations that apply in stages. The book touches its transparency and copyright provisions with dates, and none of that is legal advice. (Chapters 4 and 17)

## F

**Fetcher (user-triggered fetcher)**: A client that loads one page because a person just asked an AI product about it, such as ChatGPT-User or Claude-User. Fetchers behave like a visitor more than like a *crawler*, and some ignore robots.txt for that reason. (Chapter 4)

## G

**GDPR**: The EU's General Data Protection Regulation. When an agent acts for a person on your site, the data you collect and log is still personal data under it. (Chapter 17)

**Google-Extended**: A robots.txt control token, not a crawler: Google checks it before using content fetched by its normal crawlers for training and grounding Gemini. It has no effect on Google Search. (Chapter 4)

**Grader**: In this book, one of the two tools that measure agent-readiness: *isitagentready.com* and the Lighthouse *Agentic Browsing category*. (Chapters 1 and 2)

**Grounding**: Giving a model real content to base its answer on, such as a page fetched at the moment of the question. Content Signals call this "AI input". (Chapters 4 and 6)

## H

**Human in the loop**: A design in which a person reviews or approves an agent's step before it takes effect. (Chapter 17)

**HTTP 402 Payment Required**: An HTTP status code reserved for decades and now used by *x402* and by pay per crawl to ask a client to pay before it gets the content. (Chapters 12 and 15)

**HTTP Message Signatures**: The IETF standard (RFC 9421) for signing parts of an HTTP request so the receiver can check who sent it. *Web Bot Auth* builds on it. (Chapter 15)

## I

**ID-JAG (Identity Assertion Authorization Grant)**: An OAuth draft in which a client exchanges an identity assertion from the company's identity provider for an access token to another service. It underpins *Enterprise-Managed Authorization*. (Chapter 14)

**Idempotency key**: A unique value a client sends with a request (in the `Idempotency-Key` header) so a retry of the same request does not do the work twice. It is what stops an agent from booking a cabin twice after a timeout. (Chapters 7 and 10)

**Imperative tool**: A *WebMCP* tool registered from JavaScript with `document.modelContext.registerTool()`, with its own input schema and handler. (Chapter 9)

**Indirect prompt injection**: Instructions hidden in content an agent reads, such as a review, a hidden element or an image, that try to make the agent do something its user did not ask for. It is the defining security problem of agent-facing sites. (Chapter 16)

**Input schema**: The JSON Schema that describes a tool's parameters: names, types, which are required and what each means. Models read it to decide how to call the tool. (Chapter 10)

**isitagentready.com**: Cloudflare's free scanner that checks a site's robots.txt, sitemap, headers, well-known files and in-page tools, and assigns a *level* from 0 to 5. (Chapters 1 and 2)

## J

**JSON-LD**: The format for embedding *structured data* in a page as JSON inside a `script` element. It is the format search engines recommend for *schema.org* markup. (Chapter 5)

## L

**Least privilege**: Giving every tool, token and agent only the permissions its task needs. It limits the damage when something goes wrong. (Chapter 16)

**Level (isitagentready level)**: The 0–5 rating isitagentready assigns: Not Ready, Basic Web Presence, Bot-Aware, Agent-Readable, Agent-Integrated and Agent-Native. Each level requires all the checks of the one below it. (Chapters 1 and 13)

**Lighthouse**: Google's open-source auditing tool, built into Chrome DevTools and run from the command line or CI. Its *Agentic Browsing category* is one of the book's two graders. (Chapters 2 and 18)

**Link header**: An HTTP response header (RFC 8288) that points from a page to related resources with a *link relation*, such as the API catalog or a Markdown version. isitagentready counts it toward Level 1. (Chapter 6)

**Link relation**: The `rel` value that says how a linked resource relates to the current one, such as `alternate`, `describedby` or `api-catalog`. (Chapter 6)

**Linkset**: A JSON format for a set of links (`application/linkset+json`), used by the *API catalog*. (Chapter 7)

**llms.txt**: A proposed Markdown file at `/llms.txt` that gives language models a short summary of a site and a list of links to its most useful content. Google says it does not affect Google Search. Lighthouse audits its shape when it exists. (Chapter 6)

**llms-full.txt**: A common convention for publishing a site's full content as one Markdown file. It is not part of the llms.txt v2 proposal. (Chapter 6)

## M

**Mandate**: In *AP2*, a signed statement of what a person authorized an agent to buy, such as a cart or a spending limit. (Chapter 12)

**Markdown for Agents**: Cloudflare's feature that converts HTML to Markdown at the edge for clients that ask for it. (Chapter 6)

**Markdown negotiation**: Returning a Markdown version of a page when the client sends `Accept: text/markdown`, with `Vary: Accept` so caches keep the versions apart. isitagentready requires it for Level 3. (Chapter 6)

**MCP client and MCP host**: The host is the AI application a person uses, such as an assistant or an IDE. The client is the part of it that talks to one MCP server. (Chapter 8)

**MCP Inspector**: The MCP project's developer tool for connecting to a server, listing its tools and calling them by hand or in CI. (Chapters 8 and 18)

**MCP (Model Context Protocol)**: An open protocol that lets AI applications connect to tools, resources and prompts on a server. A site runs an *MCP server* so agents can call its actions directly. The current spec revision is dated 2026-07-28. (Chapter 8)

**MCP server**: A service that exposes tools, resources and prompts over MCP. For a site owner it is a server-side interface for agents, next to your API. (Chapter 8)

**MCP server card**: A JSON description of an MCP server that a client can read before it connects. Its location is not settled yet, and three paths are in use. (Chapter 11)

**Merchant of record**: The party legally responsible for a sale, including taxes and refunds. UCP and ACP both keep the business as the merchant of record when an agent buys. (Chapter 12)

**MPP (Machine Payments Protocol)**: An open protocol by Stripe and Tempo, launched in March 2026, that lets agents pay for APIs and services over HTTP 402 without a checkout page. (Chapter 12)

**Multi Round-Trip Requests (MRTR)**: The mechanism in MCP 2026-07-28 by which a tool call can pause to ask the client for input or confirmation and then continue. It replaces server-initiated sampling and elicitation. (Chapters 8 and 17)

## N

**NLWeb**: An open-source project, started at Microsoft, that adds a natural-language `/ask` endpoint and an MCP endpoint to a site, built on its schema.org data and feeds. (Chapters 5 and 13)

**noindex**: A directive, in a robots meta tag or the `X-Robots-Tag` header, that keeps a URL out of search indexes. It is useful for generated Markdown twins you do not want to compete with your HTML pages. (Chapters 4 and 6)

## O

**OAuth 2.1**: The consolidated revision of OAuth 2.0 that the MCP authorization spec builds on, with PKCE required for every client. It is still an IETF draft. (Chapter 14)

**OpenAPI**: The standard format for describing an HTTP API's endpoints, parameters and responses. Many agent platforms and gateways turn an OpenAPI description into tools. The current release is 3.2.1. (Chapter 7)

**Origin trial**: A Chrome programme that lets a site use an experimental feature in production for a limited time by registering for a token. WebMCP is in one. (Chapter 9)

**Output schema**: The JSON Schema that describes what a tool returns. MCP has it, and WebMCP added `outputSchema` to its draft on 2 November 2026. (Chapters 9 and 10)

## P

**Pay per crawl**: Cloudflare's closed-beta feature that charges AI crawlers per request, using HTTP 402 and price headers. (Chapter 15)

**PKCE**: An OAuth extension that protects the authorization code from interception. OAuth 2.1 and MCP require it. (Chapter 14)

**Playwright**: An open-source library for driving real browsers from code. The book uses it to read the accessibility tree, walk the booking flow and test every browser-facing layer. (Chapters 2, 3 and 18)

**Polyfill**: Code that provides a browser API in browsers that lack it. WebMCP polyfills let you ship tools today and keep them when native support arrives. (Chapter 9)

**Problem details**: A standard JSON format for API errors (RFC 9457) with fields such as `type`, `title`, `status` and `detail`. Clear errors let an agent recover instead of guessing. (Chapters 7 and 10)

**Prompt injection**: Text that tries to override a model's instructions. See *indirect prompt injection* for the form that reaches agents through your content. (Chapter 16)

**Protected Resource Metadata (PRM)**: A JSON document (RFC 9728) at `/.well-known/oauth-protected-resource` that tells a client which authorization servers protect an API or MCP server and which scopes it supports. MCP requires it. (Chapter 14)

## R

**RAG (retrieval-augmented generation)**: Answering a question by first retrieving relevant content and then giving it to a model as context. Most AI answer engines work this way, which is why the content they fetch matters. (Chapters 4 and 6)

**Rate limit**: A cap on how many requests a client can make in a window. The IETF RateLimit draft defines `RateLimit-Policy` and `RateLimit` headers so clients can see the cap instead of hitting it. (Chapters 7 and 15)

**Resource indicator**: An OAuth parameter (RFC 8707) that names the API or MCP server a token is meant for, so the token cannot be replayed against another service. (Chapter 14)

**Reverse DNS verification**: Checking that a crawler's IP address resolves to the operator's domain and back, to confirm that a request claiming to be Googlebot really came from Google. (Chapter 15)

**Rich results**: Search results with extra features, such as prices, ratings or availability, that Google builds from structured data. Google's Rich Results Test checks whether a page qualifies. (Chapter 5)

**robots.txt**: The file at the site root that tells crawlers which paths they may fetch (RFC 9309). It is a request, not access control. (Chapter 4)

**Role**: The kind of element in the *accessibility tree*, such as button, link, heading or dialog. Agents decide what they can do with an element from its role. (Chapter 3)

**RSL (Really Simple Licensing)**: A standard for publishing machine-readable licence terms for content, referenced from robots.txt with a `License` line. (Chapter 4)

## S

**schema.org**: The shared vocabulary for *structured data*, maintained by the major search engines and a community. Nordlys Cabins uses types such as `VacationRental`, `Accommodation` and `LodgingBusiness`. (Chapter 5)

**Scope**: A named permission in OAuth, such as reading bookings or creating them. A good scope design lets a person grant an agent exactly what a task needs. (Chapter 14)

**Semantic HTML**: Using HTML elements for what they mean (headings, lists, buttons, labels, landmarks) rather than generic containers styled to look right. It is the zero-cost baseline of agent-readiness. (Chapters 2 and 3)

**SEP (Specification Enhancement Proposal)**: The MCP project's process for proposing a change to the spec, numbered like SEP-2127. (Chapters 8 and 11)

**server/discover**: The MCP method a server must implement in the 2026-07-28 revision to advertise its protocol versions, capabilities and identity, replacing the old connection handshake. (Chapter 8)

**Sitemap**: An XML file that lists a site's URLs with their last-modified dates. isitagentready counts it toward Level 1. (Chapter 6)

**Stateless MCP**: The shape of the 2026-07-28 MCP spec: no connection handshake and no session id, so each request carries what the server needs and can go to any server instance. (Chapter 8)

**Step-up authentication**: Asking a user to authenticate again, or with a stronger method, before a risky action. (Chapter 14)

**Streamable HTTP**: MCP's HTTP transport. The client sends JSON-RPC messages with POST to one endpoint, and the server answers with JSON or a stream. (Chapter 8)

**Structured data**: Machine-readable facts about a page's content, such as a cabin's price, location and rating, embedded as *JSON-LD*. (Chapter 5)

**Sunset header**: An HTTP response header (RFC 8594) that says when a resource will stop working. (Chapter 20)

## T

**TDMRep**: A W3C Community Group protocol for reserving text-and-data-mining rights under EU law, with a file at `/.well-known/tdmrep.json` or HTTP headers. (Chapter 4)

**Threat model**: A structured list of what can go wrong, who might cause it and what you do about it. Chapter 16 builds one for Nordlys Cabins. (Chapter 16)

**Token audience**: The service a token is issued for. A server must reject tokens whose audience is not itself. (Chapter 14)

**Tool**: A named action an agent can call, with a description, an *input schema* and a result. Tools exist in MCP servers, in WebMCP pages and as API operations. (Chapter 10)

**Tool annotations**: Hints attached to a tool, such as whether it only reads data or whether it is destructive. Clients can use them to decide when to ask for *confirmation*. (Chapters 9 and 10)

**Tool poisoning**: Hiding malicious instructions in a tool's description or metadata so an agent that reads it misbehaves. A *rug pull* is the variant where a trusted tool changes after approval. (Chapter 16)

**Trusted Agent Protocol**: Visa's programme for merchants to recognize Visa-approved AI agents by checking the HTTP message signatures on their requests. (Chapters 12 and 15)

## U

**UCP (Universal Commerce Protocol)**: A commerce protocol from Google, Shopify and co-developers, with a business profile at `/.well-known/ucp` and capabilities for checkout, orders and, in draft, lodging bookings. (Chapter 12)

**User agent**: The name a client gives itself in the `User-Agent` header, such as GPTBot. It is a claim anyone can copy, which is why Chapter 15 adds verification. (Chapters 4 and 15)

## V

**Vary header**: An HTTP header that lists which request headers change the response. `Vary: Accept` keeps a cache from serving Markdown to a browser. (Chapter 6)

**Verified bot**: A bot whose identity a bot-management service has confirmed, by IP ranges, reverse DNS or signatures. Cloudflare labels verified bots as Direct or Intermediary. (Chapter 15)

**Versioning**: Changing tools and APIs without breaking the agents that use them: new names or versions for breaking changes, deprecation notices and a sunset date. (Chapter 20)

## W

**Web Bot Auth**: The IETF work on signing bot and agent requests with *HTTP Message Signatures*, so a site can verify who sent them. Its keys are published at `/.well-known/http-message-signatures-directory`. (Chapter 15)

**WebMCP**: A proposed browser standard that lets a page register *tools* for agents in the browser, either from JavaScript or by annotating forms. It is a W3C Community Group draft with an origin trial in Chrome. (Chapter 9)

**Well-known URI**: A path under `/.well-known/` reserved for site-wide metadata (RFC 8615), registered with IANA. (Chapters 11 and Appendix B)

## X

**x402**: An open protocol for paying per request over HTTP. The server answers 402 with payment requirements, the client pays and retries with a payment header. It is run by the x402 Foundation under the Linux Foundation. (Chapters 12 and 15)
