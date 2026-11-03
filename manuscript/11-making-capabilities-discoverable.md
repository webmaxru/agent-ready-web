# Chapter 11: Making capabilities discoverable

This chapter covers

- How an agent learns what your site can do before it sends a single request to a tool
- The signposts a site can publish: `Link` headers, the API catalog, MCP server cards, an Agent Skills index and an ARD manifest
- Why the MCP server card has three competing addresses, and which one Nordlys serves
- The discovery files Nordlys does not publish (A2A agent card, DNS-AID, auth.md), and why
- The isitagentready.com level ladder for Nordlys, chapter by chapter, and the Lighthouse ARD audit

By now Nordlys Cabins has a lot to offer an agent. Chapter 7 gave it a public HTTP API with an OpenAPI description. Chapter 8 put an MCP server next to it, sharing the same booking logic. Chapter 9 registered tools inside the page with WebMCP, and Chapter 10 made all of those tools easier for a model to use correctly. That is a decent set of doors.

There is one awkward problem left. How does an agent find out that the doors exist?

A person who lands on nordlys.example sees a search box and a "Book" button. An agent that knows only the domain sees nothing of the sort. It can fetch the home page and read it (Part 2 made that pleasant), but nothing on the home page says "there is an MCP server at `/mcp`" or "the API is described at `/openapi.json`". Today, in most cases, a human closes that gap by hand: a user pastes a server URL into a chat app, an admin approves a connector, a developer edits a configuration file. Chapter 8 called this out, and it is still true in November 2026.

Discovery files try to close the gap from the site's side. They are small, mostly static documents at predictable addresses that answer three questions for a machine: what can this site do, where are the endpoints, and how do I connect to them? In this chapter we publish all the ones that make sense for a booking site, explain the ones that don't (yet), and measure the result with both graders.

I'll be honest from the start: this is the least settled layer in the whole book. Some of these files are RFCs with years of history. Others are proposals that changed their address twice in 2026. One of them has a status page that says "Final" and a repository that says "Experimental" for the same idea. So this chapter does two jobs. It shows you how to publish discovery files today, and it shows you how to publish them in a way that survives the next rename.

> **Note:** Product managers, content and SEO people, this chapter is closer to your world than it looks. Discovery files are to agents roughly what sitemaps and structured data are to search engines: they don't add features, they make existing features findable. The sections "The discovery problem", "A map of the signposts" and "The ladder, chapter by chapter" are written for the whole team. The code-heavy sections start with a Hands-on callout that says where to pick up again.

## The discovery problem

Let's look at the problem from the agent's side for a moment. Imagine a travel assistant that a user asked to "find me a cabin with a sauna in Lofoten for four people in December". The assistant has a few ways to get there.

It can search the web, land on a Nordlys cabin page and read it. Chapters 4 to 6 made sure that works: the crawler is allowed in, the page carries schema.org data, and a Markdown version is one `Accept` header away. That is enough to *answer* the question. It is not enough to *book*.

It can click through the booking form like a person, as in Chapter 3. That works on a well-built page, and slowly.

Or it can call a tool. Nordlys now offers three kinds: the HTTP API, the MCP server and the WebMCP tools in the page. The first two live at addresses the agent cannot guess, and the third exists only when a browser has the page open. For the API and the MCP server, somebody has to tell the agent where they are.

In simple words, discovery is the step between "I know your domain" and "I know your capabilities". On the classic web, that step was done by humans: a developer read the docs, found the API reference and wrote a client. Agents want to do that step themselves, at run time, for sites nobody configured in advance. And they want to do it cheaply, without crawling a whole site to find one endpoint.

### What a discovery file can and cannot do

A discovery file is a statement by the site about itself. It says "my MCP server is here, it speaks these protocol versions, here is a description of what it is for". That statement is useful, and it is also just a statement. Three limits are worth keeping in mind for the rest of the chapter.

First, a discovery file is advisory. The live interface is the truth. If the server card says the MCP server supports protocol version 2026-07-28 and the server itself disagrees, the server wins. That is why the Nordlys tests (later in this chapter) check that every discovery document agrees with the live endpoint it points to.

Second, a discovery file grants nothing. Publishing an MCP server card does not make the server public, and hiding the card does not make the server private. Access is decided by authentication (Chapter 14) and by your edge (Chapter 15). Please don't treat an unpublished path as a security measure.

Third, somebody has to read the file. A signpost nobody looks at is decoration. So before we build anything, let's check who actually reads these files in November 2026.

### Who reads discovery files today

The honest answer is: scanners first, registries second, agents a distant third.

The most active readers are the graders this book uses. isitagentready.com fetches more than a dozen well-known paths for every scan, and its Level 4 and Level 5 are defined almost entirely by discovery files.[^ch11-1] The Lighthouse Agentic Browsing category reads two discovery documents in its "Agent Discoverability" group, `llms.txt` and the ARD manifest, and audits both.[^ch11-2] Cloudflare Radar runs the same checks as isitagentready across the top 200,000 domains and publishes the adoption numbers weekly.[^ch11-3]

Those numbers are small. In Radar's data dated 2 November 2026 (115,468 successfully scanned domains), `Link` headers with agent-useful relations appear on 9.7% of sites, an API catalog on 0.74%, an MCP server card on 0.61%, an Agent Skills index on 0.59% and an ARD manifest on 0.29%.[^ch11-3] Back in April 2026, when Cloudflare launched the scanner, MCP server cards and API catalogs together appeared on fewer than 15 sites in the whole dataset.[^ch11-4] So the growth is real, from a very low base.

Registries are the second group. The official MCP Registry indexes servers and is, in its own words, "currently in preview".[^ch11-5] Google's ARD proposal is built around registries that crawl manifests and offer search.[^ch11-6] Neither is a place where a small site has to be listed today, but both read the same kind of file we are about to publish.

Agents themselves are the third group, and the thinnest one. I could not find a mainstream assistant that, as of November 2026, automatically fetches an MCP server card or an Agent Skills index from an arbitrary domain and connects to what it finds without a human approving it. Coding agents that load Agent Skills on request come closest. That is not a reason to skip the work. It is a reason to keep it cheap, standard and easy to change.

Bottomline: you publish discovery files today mostly for the graders, the registries and the next generation of clients. That is fine, as long as you spend an afternoon on it and not a quarter.

## A map of the signposts

Before the details, here is the whole map. Figure 11.1 shows every discovery document Nordlys serves at the end of this chapter and what each one points to.

![Figure 11.1 — The discovery map of Nordlys Cabins after Chapter 11. The home page carries a Link header that points to the Markdown version, llms.txt, the API catalog and the ARD manifest. The API catalog lists the REST API and the MCP endpoint. The ARD manifest lists the MCP server card and the booking skill. The Agent Skills index points to the SKILL.md file. OAuth metadata arrives in Chapter 14.](images/figure-11-1.png)

Most of these documents live under `/.well-known/`, the path prefix that RFC 8615 reserves for site-wide metadata.[^ch11-7] The idea is simple: if every site puts the same kind of file at the same path, a client needs only the domain. The prefix is managed by IANA, and a name in the registry tells you how settled a file is. As of the registry update of 26 October 2026, `api-catalog` and `oauth-protected-resource` are permanent entries backed by RFCs, `agent-card.json` (A2A) is permanent, and `ucp` is provisional. There are no entries for `ard.json`, `ai-catalog.json`, `agent-skills`, `mcp.json` or `mcp/server-card.json`.[^ch11-8] An unregistered name can still work in practice (`llms.txt` is not registered either), but it is a hint that the name could still move.

Table 11.1 is the same map as a list, with the status of each standard and who reads it. I'll refer back to it throughout the chapter.

Table 11.1 Discovery documents for a booking site, as of November 2026

| Document | Address | Standard and status | Read by | Nordlys |
|---|---|---|---|---|
| Link header | home page response | RFC 8288, Proposed Standard | isitagentready `linkHeaders`, Lighthouse (for `rel="ard"`) | Yes (Chapters 6, 7, 11) |
| API catalog | `/.well-known/api-catalog` | RFC 9727, Standards Track | isitagentready `apiCatalog`, API tooling | Yes (Chapter 7, extended here) |
| MCP server card | `/mcp/server-card` and mirrors | SEP-2127 extension, contested | isitagentready `mcpServerCard`, registries | Yes |
| Agent Skills index | `/.well-known/agent-skills/index.json` | Discovery RFC v0.2.0, draft | isitagentready `agentSkills`, coding agents | Yes |
| ARD manifest | `/.well-known/ard.json` | ARD v0.91, proposal | Lighthouse `ard-schema`, isitagentready `ard` | Yes |
| OAuth metadata | `/.well-known/oauth-protected-resource` and others | RFC 9728, RFC 8414 | MCP clients, isitagentready | Chapter 14 |
| A2A agent card | `/.well-known/agent-card.json` | A2A 1.0 | A2A clients, isitagentready (opt-in) | No |
| DNS-AID | `_agents` DNS records | individual Internet-Draft | isitagentready `dnsAid` | No |
| auth.md | `/auth.md` | vendor proposal | isitagentready `authMd` | No |

Two documents from earlier chapters belong on this map as well. `llms.txt` (Chapter 6) is a signpost for readers, and the `Agentmap:` line in `robots.txt` that Chapter 4 mentioned is one of the ways to point at an ARD manifest. We don't add a new `robots.txt` line here: the `Link` header does the same job with less risk of upsetting other `robots.txt` parsers.

What follows goes through the map in the order an agent would meet it: the `Link` header on the home page, the API catalog, the MCP server card, the Agent Skills index, the ARD manifest, and then the documents Nordlys deliberately leaves out.

## Link headers: the cheapest signpost

A `Link` header is a line in an HTTP response that points to another resource and says how the two relate. It is defined by RFC 8288, "Web Linking", and it has been a Proposed Standard since October 2017.[^ch11-9] You already know its HTML twin, `<link rel="stylesheet" href="...">`. The header form has one big advantage for discovery: it works on any response, including ones that are not HTML, and a client can read it with a cheap `HEAD` request without downloading the page.

Here is the `Link` header of the Nordlys home page after this chapter, exactly as the demo server sends it (one line, wrapped here for print):

```http
Link: <https://nordlys.example/index.md>; rel="alternate"; type="text/markdown",
      <https://nordlys.example/llms.txt>; rel="describedby",
      </.well-known/api-catalog>; rel="api-catalog",
      </.well-known/ard.json>; rel="ard"
```

Four values, added by three chapters. Chapter 6 added the Markdown alternate and `llms.txt`. Chapter 7 added the API catalog. This chapter adds the last one, `rel="ard"`, which points to the ARD manifest. An agent that fetches the home page once now knows where the readable content is, where the APIs are listed and where the agentic resources are described.

The relation names matter. `alternate`, `describedby` and `api-catalog` are registered in the IANA link relations registry. `ard` is not registered as of 2 November 2026, and neither is `sitemap`, although both are used in the wild.[^ch11-10] Lighthouse looks for `rel="ard"` specifically, and the ARD specification says that a consumer "MUST honour a rel="ard" link", so we use it anyway.[^ch11-6] This is a typical trade-off in this chapter: the de facto name is the one the readers look for, and the registry has not caught up yet.

isitagentready's `linkHeaders` check passes when the home page carries RFC 8288 `Link` headers with relations that are useful to agents, and it names `service-desc`, `describedby`, `api-catalog` and `alternate` as examples.[^ch11-1] Nordlys has passed that check since Chapter 6. The `ard` value does not change the check. It is there for the ARD readers.

### Appending, not replacing

There is one engineering detail here that is easy to get wrong, and I have seen it go wrong in real projects with other headers. Several layers of Nordlys contribute a `Link` value to the same response. If any one of them *sets* the header instead of *appending* to it, the earlier values vanish without an error, and a check that passed yesterday fails today.

The Nordlys layer contract lets a layer read the headers that earlier layers produced. Every layer that adds a `Link` value reads the current one first and appends its own after a comma. You will see this at the end of Listing 11.1. The Chapter 11 tests then check that the `api-catalog` value from Chapter 7 is still there after this layer has added `ard`, which is the cheapest possible regression test for this class of bug.

If your site sits behind a CDN or a framework that manages headers, the same rule applies. Find the one place where `Link` is assembled, or make every contributor append. A single `Link` header with comma-separated values and several `Link` headers on the same response mean the same thing in RFC 8288, so either form is fine. Silently dropping values is not.

## The API catalog, now with MCP

Chapter 7 published `/.well-known/api-catalog`, the document RFC 9727 defines for "the discovery of APIs published by a given organisation".[^ch11-11] It is a linkset (`application/linkset+json`): a list of anchors, one per API, each with links to the API's description (`service-desc`), its documentation (`service-doc`), extra metadata (`service-meta`) and a status endpoint (`status`). For the REST API those point to `/openapi.json`, to a Markdown developer page, to the Arazzo workflow and to a health endpoint.

Now Nordlys has a second programmatic interface, the MCP server. Should it be in the API catalog too?

RFC 9727 talks about APIs in general and does not prescribe a description format. An MCP server at `/mcp` is an HTTP endpoint with a machine-readable description of its own (the server card we are about to publish), so I think it fits. Listing it costs one more entry, and it means that a client which only knows the API catalog can still find the MCP server. That is my judgment, not something the RFC or the MCP project asks for, and I haven't seen a client that uses such an entry yet.

> **Hands-on:** Listing 11.1 and the JSON after it show how the Chapter 11 layer adds the MCP endpoint to the existing catalog and appends its `Link` value. If you don't write code, the point is in the previous paragraph: one catalog lists both programmatic doors of the site. Pick up again at "MCP server cards: one idea, three addresses".

**Listing 11.1** `nordlys-cabins/layers/11-discovery/index.js` — extending the API catalog and the Link header (excerpt)

```javascript
    // 4. The API catalog from Chapter 7 gains an entry for the MCP endpoint.
    ctx.staticFile(
      CATALOG_PATH,
      (c) => {
        const catalog = apiCatalog(origin(c));
        catalog.linkset.push({ anchor: `${origin(c)}/mcp`, 'service-desc': [{ href: `${origin(c)}/mcp/server-card`, type: MCP_CARD_TYPE }] });
        return JSON.stringify(catalog, null, 2);
      },
      { replace: true, contentType: LINKSET_TYPE }
    );

    // 5. The home page links the ARD manifest (rel="ard"), after whatever earlier chapters linked.
    ctx.headers('/', (c) => {
      const earlier = c.res.headers.get('link');
      const ours = '</.well-known/ard.json>; rel="ard"';
      return { link: earlier ? `${earlier}, ${ours}` : ours };
    });
```

The catalog is generated, not hand-written: the layer imports the `apiCatalog()` function from Chapter 7 and pushes one more anchor onto the result. That keeps a single source of truth for the REST API entry. The `replace: true` option tells the layer contract that this layer knowingly replaces the response of a path an earlier layer registered. Without it, the app refuses to start, which is a deliberate guard against two layers quietly fighting over one URL.

The new entry in the served catalog looks like this:

```json
{
  "anchor": "https://nordlys.example/mcp",
  "service-desc": [
    {
      "href": "https://nordlys.example/mcp/server-card",
      "type": "application/mcp-server-card+json"
    }
  ]
}
```

The `service-desc` relation means "a description of the API that is primarily intended for machine consumption", which is exactly what a server card is.[^ch11-11] The media type is the one the ARD specification lists for MCP server cards, and the ARD authors say plainly that these agent media types are "de-facto community standards tracking towards formal registration".[^ch11-6] In other words, nobody has registered `application/mcp-server-card+json` with IANA yet.

## MCP server cards: one idea, three addresses

Of all the discovery files in this chapter, the MCP server card has the most confusing story, so let's take it slowly.

The idea is simple and, I think, good. An MCP server already describes itself when a client talks to it: on the 2026-07-28 revision of the protocol, a client sends `server/discover` and gets back the server's name, version, supported protocol versions and capabilities (Chapter 8 showed the exchange). A server card is a static copy of the *connection* part of that information, published somewhere a client can fetch without speaking MCP at all. With a card, a registry or a client can learn "there is an MCP server here, it is called this, it lives at this URL, it speaks these versions" from a single `GET`.

### What goes in a card, and what stays out

The card format comes from SEP-2127, "MCP Server Cards - HTTP Server Discovery".[^ch11-12] Two of its design choices are worth knowing even if you never write a card by hand.

A card describes how to *connect*, not what the server *does* in detail. The SEP explicitly leaves out the server's primitives (tools, resources, prompts) and its runtime capabilities. Its reasoning is that "capabilities and extensions describe negotiated runtime behavior and can depend on the client, identity, configuration, and deployment state", while `supportedProtocolVersions` "lets a client determine whether it can attempt a connection".[^ch11-12] Personally for me, this is the right call. A tool list in a static file goes stale the day somebody adds a tool, and it would tempt clients to trust the file over the server.

A card is aligned with the MCP Registry's metadata but is not the same document. The Registry's `server.json` also describes locally installable packages and their runtime configuration, and the SEP says the card "does not define a Server superset" of it.[^ch11-12] So if you list your server in the Registry later, you will write a second, related file.

### Three addresses

Now the confusing part. In November 2026, three different addresses for "the MCP server card of this domain" are in circulation. Figure 11.2 lines them up.

![Figure 11.2 — Three addresses for one MCP server card. Path A, /.well-known/mcp/server-card.json, comes from the earlier SEP-1649 draft and is what Cloudflare's scanner looks for. Path B, /.well-known/mcp.json, is what isitagentready.com serves for itself. Path C is SEP-2127: the card lives next to the endpoint at /mcp/server-card and is listed from a domain-level catalog. Nordlys serves C and mirrors it at A.](images/figure-11-2.png)

**Path A: `/.well-known/mcp/server-card.json`.** This is the location from an earlier proposal, SEP-1649, and it is what Cloudflare's scanner looked for at launch: its April 2026 post describes it as "a proposal currently in draft".[^ch11-4] The isitagentready `mcpServerCard` check still reads this path first, and also accepts `server-cards.json` and `mcp.json` under `/.well-known/`, as long as the document has a `name` (or `serverInfo.name`).[^ch11-1]

**Path B: `/.well-known/mcp.json`.** This is what isitagentready.com publishes for its own MCP server.[^ch11-13] It is not in any MCP proposal I could find. It is simply the shortest obvious name, and some sites copy whatever the scanner they test against does.

**Path C: `<mcp-endpoint>/server-card`.** SEP-2127 reserves the path `server-card` under the server's own Streamable HTTP URL "as the recommended location", and moves domain-level discovery to a catalog document (the AI Catalog, which became Google's ARD manifest, more on that below).[^ch11-12] For Nordlys, the endpoint is `https://nordlys.example/mcp`, so the card lives at `https://nordlys.example/mcp/server-card`.

Path C has a property I like a lot. A site can run several MCP servers (say `/mcp` for bookings and `/owners/mcp` for cabin owners), and each card sits next to its own server, while one catalog lists them all. A single well-known file per domain cannot express that cleanly.

> **Still in flux:** As of 2 November 2026, the SEP-2127 page on modelcontextprotocol.io shows the status "Final", while the extension's own repository says "Status: Experimental. This work is for prototyping and feedback only".[^ch11-12][^ch11-14] Both statements were live on the same day. Treat the server card as a useful convention with a likely future, not as a finished standard, and keep the code that produces it small.

### What Nordlys serves, and why

Nordlys serves Path C as the canonical card and mirrors the same document at Path A. It does not serve Path B. My reasoning:

- Path C is where the MCP project itself points, and it is the only one that scales to more than one server per domain.
- Path A is where today's main scanner looks. A mirror costs two lines and keeps the `mcpServerCard` check green.
- Path B adds nothing that Path A does not already give the scanner, and it is not part of any proposal. One mirror is enough.

> **Hands-on:** Listing 11.2 is the code that builds and serves the card. If you skip it, remember the two decisions in it: the card is generated from the site's origin (so it is right on staging and in production), and the same object is served at two addresses. Pick up again at "Checking the card against the server".

**Listing 11.2** `nordlys-cabins/layers/11-discovery/index.js` — the MCP server card at two addresses (excerpt)

```javascript
    // 1. MCP Server Card (MCP Server Card extension, SEP-2127): at <mcp-url>/server-card,
    //    the location the extension reserves, and mirrored at the path today's scanners probe.
    const serverCard = (c) => ({
      $schema: 'https://static.modelcontextprotocol.io/schemas/v1/server-card.schema.json',
      name: `${host(c).split('.').reverse().join('.')}/booking`,
      version: '1.0.0',
      title: 'Nordlys Cabins',
      description: 'Search Nordlys holiday cabins in Norway, check availability and exact prices, and book or cancel a stay.',
      websiteUrl: origin(c),
      repository: { url: 'https://github.com/webmaxru/agent-ready-web-demos', source: 'github', subfolder: 'nordlys-cabins/layers/08-mcp-server' },
      remotes: [{ type: 'streamable-http', url: `${origin(c)}/mcp`, supportedProtocolVersions: ['2025-11-25', '2026-07-28'] }],
    });
    ctx.staticFile('/mcp/server-card', (c) => JSON.stringify(serverCard(c), null, 2), { contentType: MCP_CARD_TYPE });
    ctx.staticFile('/.well-known/mcp/server-card.json', (c) => JSON.stringify(serverCard(c), null, 2));
```

A few details in this listing deserve a word.

The `name` is a reverse-DNS style identifier, `example.nordlys/booking` for the host `nordlys.example`. The layer computes it from the host, so the staging card and the production card each carry their own domain. As far as I can tell, reverse-DNS names are also how the MCP Registry names servers, so the same name should work for a later Registry listing.

The `remotes` array says how to connect: one Streamable HTTP endpoint at `/mcp` that supports protocol versions 2025-11-25 and 2026-07-28. The Nordlys server answers both eras on the same endpoint (Chapter 8 showed the legacy handshake), so the card lists both.

The `repository` points at the public demos repository and the subfolder with the server code. That is optional, and for a commercial site you would probably leave it out. For a book demo, it lets a reader jump from the card to the source.

The canonical card is served with the media type `application/mcp-server-card+json`. The mirror at the well-known path goes out as plain `application/json`, which is what generic tools expect from a `.json` URL.

### Checking the card against the server

Remember the first limit of discovery files: the live interface is the truth. A server card that says "version 1.0.0, protocols 2025-11-25 and 2026-07-28" while the server reports something else is worse than no card, because a client might trust it and fail in a confusing way.

The first Chapter 11 test enforces this. It fetches the card, then sends a real `server/discover` request to `/mcp`, and checks two things: every protocol version the server reports is listed in the card, and the server's version matches the card's version. It also checks that the mirror at `/.well-known/mcp/server-card.json` is byte-for-byte the same object as the canonical card. If somebody bumps the server version in Chapter 8's code and forgets the card, this test fails.

In a real project I would go one step further and generate the card's `version` from the same constant the server uses. Nordlys keeps them separate on purpose, so the test has something to catch.

## Agent Skills: instructions an agent can load

The server card tells an agent *where* the MCP server is. It does not tell the agent *how to use it well*. For a booking site, that second part matters more than it seems. Chapter 10 spent a whole chapter on it: ask for the dates before searching, show the total before booking, never accept the terms on the user's behalf, retry with the same idempotency key, explain errors instead of retrying blindly. Tool descriptions carry some of that. A procedure that spans several tools does not fit well into any single description.

This is the gap Agent Skills fill. A skill is a folder with a `SKILL.md` file: YAML front matter with a `name` and a `description`, followed by Markdown instructions. The format comes from the Agent Skills specification at agentskills.io, which requires both fields and limits the name to 64 characters (lowercase letters, numbers and hyphens) and the description to 1,024 characters that say "what the skill does and when to use it".[^ch11-15] An agent that supports skills keeps only the names and descriptions in mind and loads the full instructions when a task matches. Coding agents popularised the format, and it fits a website surprisingly well.

### A skill for booking a cabin

Listing 11.3 is the whole skill Nordlys publishes. It is written for an agent, but please read it as a product manager or a support lead would: it is basically the booking policy and the booking flow, in plain language.

**Listing 11.3** `nordlys-cabins/layers/11-discovery/skills/book-a-nordlys-cabin/SKILL.md` — the booking skill

```markdown
---
name: book-a-nordlys-cabin
description: Find, price and book a holiday cabin at Nordlys Cabins (Norway). Use when a user wants to rent a cabin in Rondane, Lyngen, Senja, Lofoten, Hardanger or Femunden, check if a cabin is free, or cancel a Nordlys booking.
---

# Book a Nordlys cabin

Nordlys Cabins rents six holiday cabins in Norway. You can work with it in two
ways. Use whichever your environment supports, they share the same data.

- MCP server: `https://nordlys.example/mcp` (Streamable HTTP). Tools:
  `search_cabins`, `check_availability`, `create_booking`, `cancel_booking`.
- HTTP API: `https://nordlys.example/openapi.json` (OpenAPI 3.1). Operations:
  `searchCabins`, `getCabin`, `checkAvailability`, `createBooking`, `cancelBooking`.

## Steps

1. Ask for what you do not know yet: region or wishes, dates, number of guests.
2. Search. Pass both dates so you only get cabins that are free.
3. Check availability for the cabin the user likes. Tell the user the total price
   in NOK and what it includes (nights and one cleaning fee).
4. Before booking, confirm cabin, dates, guests, total and the lead guest's name
   and email. Ask the user to accept the booking terms (https://nordlys.example/faq).
   Never accept the terms on the user's behalf.
5. Book with a new idempotency key (a UUID). If the call times out, retry with the
   same key: you get the same booking back, not a second one.
6. Give the user the booking reference (it starts with `NC-`) and the free-cancellation date.

## Rules

- Dates are YYYY-MM-DD in Europe/Oslo. Check-in is 16:00, check-out 11:00.
- Friday and Saturday nights cost more. The cleaning fee is added once per stay.
- Free cancellation ends 14 days before check-in. Cancelling cannot be undone:
  always ask first.
- Errors carry a stable `code` (for example `min_nights`, `too_many_guests`,
  `not_available`). Explain the problem to the user and suggest a fix instead of
  retrying blindly.
```

A few choices here are deliberate.

The description names the regions. An agent decides whether to load a skill from its description alone, and "a user wants to rent a cabin in Lofoten" should match. Vague descriptions ("helps with bookings") are as bad for skills as they are for tools.

The skill names both doors, the MCP server and the HTTP API, with their exact tool and operation names. An agent in an environment without MCP support can still follow the steps with plain HTTP calls.

The rules repeat facts that also live in the tool descriptions and the API errors (check-in times, the cleaning fee, the cancellation window). That duplication is on purpose: the skill is read before any tool is called, so it lets the agent ask the right questions up front instead of discovering the rules one error at a time.

And step 4 says, in so many words, "Never accept the terms on the user's behalf." That sentence is the same safety rule Chapter 10 enforced in the schema and Chapter 16 comes back to. A skill is a good place to state it, and a bad place to *rely* on it: an agent may ignore instructions, so the server still refuses a booking without an explicit `acceptTerms: true`.

> **Warning:** A skill is text that an agent will follow. That makes it a prompt-injection surface in both directions. Your own skill must never contain anything you would not want an agent to execute, and an agent should treat a skill from an unknown site with the same suspicion as any other page content. Chapter 16 covers prompt injection in detail. For Nordlys, the skill contains no scripts and no links outside the site.

### The discovery index

A `SKILL.md` on a web server is just a file. To make it findable, Nordlys publishes an index at `/.well-known/agent-skills/index.json`, following the "Agent Skills Discovery via Well-Known URIs" RFC. That document is a draft maintained by Cloudflare: version 0.2.0, first published on 17 January 2026 and updated on 12 March 2026.[^ch11-16] Version 0.2.0 moved the path from `/.well-known/skills/` to `/.well-known/agent-skills/`, replaced a `version` field with a `$schema` URI, and switched to a flat model where each entry has a `type` (`skill-md` or `archive`), a `url` and a `digest`, the SHA-256 of that single artifact.[^ch11-16]

> **Hands-on:** Listing 11.4 serves the skill and its index. The interesting line is the digest, which lets an agent check that the file it downloaded is the one the index describes. Pick up again at "Who publishes skills".

**Listing 11.4** `nordlys-cabins/layers/11-discovery/index.js` — the Agent Skills index (excerpt)

```javascript
    // 2. Agent Skills Discovery (v0.2.0): an index with name, type, description, url and a SHA-256 digest.
    ctx.staticFile(`/.well-known/agent-skills/${SKILL}/SKILL.md`, (c) => skillBody(c));
    ctx.staticFile('/.well-known/agent-skills/index.json', (c) =>
      JSON.stringify(
        {
          $schema: 'https://schemas.agentskills.io/discovery/0.2.0/schema.json',
          skills: [
            {
              name: SKILL,
              type: 'skill-md',
              description: 'Find, price and book a holiday cabin at Nordlys Cabins (Norway), or cancel a booking.',
              url: `/.well-known/agent-skills/${SKILL}/SKILL.md`,
              digest: digest(skillBody(c)),
            },
          ],
        },
        null,
        2
      )
    );
```

The skill file names the production host, `https://nordlys.example`. The layer rewrites it to the origin the request came in on, so a copy served from staging points at staging. The digest is computed from the rewritten text, which is exactly what a client downloads, so it always matches. The second Chapter 11 test downloads the file from the URL in the index, hashes it and compares.

Here is the index as the server sends it (the digest is real output for the production origin):

```json
{
  "$schema": "https://schemas.agentskills.io/discovery/0.2.0/schema.json",
  "skills": [
    {
      "name": "book-a-nordlys-cabin",
      "type": "skill-md",
      "description": "Find, price and book a holiday cabin at Nordlys Cabins (Norway), or cancel a booking.",
      "url": "/.well-known/agent-skills/book-a-nordlys-cabin/SKILL.md",
      "digest": "sha256:9838d68c08fdcb727a2999984cf9f1733ff867fb0c3e0c64ff7566dc46ef5529"
    }
  ]
}
```

One small surprise: on 2 November 2026 the `$schema` URL did not resolve from my machine (the host name had no DNS record). isitagentready.com and vercel.com use the same URL in their own indexes, so treat it as an identifier that names the format version, not as a schema you can download today.

### Who publishes skills

isitagentready's `agentSkills` check passes when the index exists in the v0.2.0 format, and it still accepts the legacy `/.well-known/skills/index.json` path.[^ch11-1] In the scan of 44 sites that our research did on 2 November 2026, vercel.com published 9 skills and stripe.com 10 (still on the legacy v0.1.0 path), and isitagentready.com itself publishes 25: one for scanning a site and one fix skill per check.[^ch11-17] Those are developer-tool companies publishing skills for developers' coding agents. A booking site publishing a skill for travel agents is newer ground, and I think it is one of the more promising ideas in this chapter, because it carries policy and procedure, the things tool schemas are worst at.

## ARD: one manifest to describe them all

So far we have a card for the MCP server, an index for the skill and a catalog for the APIs. Three files, three formats, three paths. An agent (or a registry) that wants to know "what agentic resources does nordlys.example have?" would have to know all three conventions.

The Agentic Resource Discovery specification, ARD for short, tries to give that question one answer. Google announced it on 17 June 2026 as a way for a provider to host a catalog file on its own domain listing its MCP servers, A2A agents and other tools.[^ch11-18] The current text is version 0.91, status "Proposal", dated 26 August 2026, by Junjie Bu (Google), R.V. Guha and Shaun Smith (Hugging Face).[^ch11-6] Chapter 5 met Guha as the creator of NLWeb, so the people behind ARD have been working on machine-readable web content for a long time.

### How ARD is found

ARD describes several ways to publish its entries: a manifest at `/.well-known/ard.json`, an `Agentmap:` directive in `robots.txt`, an HTML `<link rel="ard">`, a `Link` header, DNS service records, and JSON-LD embedded in pages.[^ch11-6] For a consumer, the specification is strict about two of them: it "MUST fetch /.well-known/ard.json, and MUST honour a rel="ard" link".[^ch11-6]

The name has a history you will bump into. ARD's predecessor used the path `/.well-known/ai-catalog.json` and the link relation `ai-catalog` (that is the "AI Catalog" SEP-2127 refers to). The specification allows consumers to consult the old names as "a courtesy to resources published before this revision".[^ch11-6] Lighthouse 13.6.0, released on 27 October 2026, moved to ARD v0.91 and `/.well-known/ard.json` and warns when it finds the legacy `ai-catalog` location.[^ch11-2] isitagentready.com, on the same day, still told sites to "Serve /.well-known/ai-catalog.json at the origin root" in its fix prompt, while its check accepts a manifest found through several mechanisms.[^ch11-1] So the two graders disagree about the address, and the specification sides with Lighthouse.

### What goes in an entry

An ARD manifest is a JSON document with an `entries` array. Each entry must carry an `identifier` (a domain-anchored URN of the form `urn:air:<publisher>:[<namespace>:]<agent-name>`), a `displayName`, a `type` given as a media type, and exactly one of `url` (a reference to the artifact) or `data` (the artifact inline).[^ch11-6] Optional descriptive terms include `description`, `tags`, `version` and `updatedAt`. And then there is the term that makes ARD different from a plain list: `representativeQueries`, example requests the resource is good for. The specification expects every ARD entry to carry them, and conformance tooling flags a missing or thin list as a warning rather than a failure.[^ch11-6] The Lighthouse documentation is more direct: "Add 2 to 5 representativeQueries to each entry to get a perfect score."[^ch11-2]

Representative queries are an interesting design choice. They move tool selection out of the model's context window and into a search index: a registry can match a user's request against your example queries before any model reads your descriptions. For a site owner, this is a familiar job. It is keyword research, just phrased as things people ask an assistant.

> **Hands-on:** Listing 11.5 builds the Nordlys manifest. If you skip the code, look at the representative queries in it: they are the part a content or SEO person should write. Pick up again at "Two graders, one manifest".

**Listing 11.5** `nordlys-cabins/layers/11-discovery/index.js` — the ARD manifest (excerpt)

```javascript
    // 3. ARD manifest (Agentic Resource Discovery v0.91) at /.well-known/ard.json.
    ctx.staticFile('/.well-known/ard.json', (c) =>
      JSON.stringify(
        {
          specVersion: '1.0',
          entries: [
            {
              identifier: `urn:air:${host(c)}:mcp:booking`,
              displayName: 'Nordlys Cabins booking',
              type: MCP_CARD_TYPE,
              url: `${origin(c)}/mcp/server-card`,
              description: 'MCP server for searching, pricing, booking and cancelling Nordlys holiday cabins in Norway.',
              tags: ['travel', 'lodging', 'booking', 'norway'],
              representativeQueries: [
                'find a cabin with a sauna in Lofoten for four people',
                'is the Fjellro cabin free from 2 to 5 December',
                'book a mountain cabin in Norway for a long weekend',
              ],
            },
            {
              identifier: `urn:air:${host(c)}:skill:${SKILL}`,
              displayName: 'Book a Nordlys cabin',
              type: 'application/agent-skills+md',
              url: `${origin(c)}/.well-known/agent-skills/${SKILL}/SKILL.md`,
              description: 'Step-by-step instructions for an agent that books a Nordlys cabin through the MCP server or the HTTP API.',
              representativeQueries: [
                'how do I book a Nordlys cabin for a customer',
                'cancel a Nordlys Cabins booking',
              ],
            },
          ],
        },
        null,
        2
      )
    );
```

The manifest has two entries. The first describes the MCP server by pointing at its server card (type `application/mcp-server-card+json`). The second describes the booking skill as `application/agent-skills+md`, one of the media types the specification lists for skills.[^ch11-6] I did not add an entry for the REST API: ARD is aimed at agentic resources, and the API is already listed in the API catalog, which the `Link` header points to. You could add it with the OpenAPI media type, and if registries start indexing APIs through ARD I would.

There are three representative queries for the server and two for the skill, inside the 2 to 5 range Lighthouse asks for. I wrote them the way a traveller would type them, with real Nordlys cabin names and regions. The `tags` are ARD's optional descriptive term. ARD identifiers are URNs on the publisher's domain, so the staging manifest has staging identifiers. That is correct: they are different publishers as far as a registry is concerned.

The top-level `specVersion: '1.0'` needs an explanation. isitagentready's `ard` check requires a `specVersion` member, while ARD itself defines only the `entries` array and says that "any other top-level members are transport-defined and ignored by ARD".[^ch11-1][^ch11-6] So the member satisfies one grader and is harmless to the other.

### Two graders, one manifest

I wanted to be sure the manifest passes the stricter reader, so we ran Lighthouse 13.6.0 against the demo server with all layers up to this chapter (headless Chromium 156, 2 November 2026). Lighthouse bundles a port of the ARD conformance suite (it reports "ard 0.91 (f073b1e)"), and the `ard-schema` audit passed with a score of 1. In that run, the Agentic Browsing category scored 1 overall: `agent-accessibility-tree`, `cumulative-layout-shift`, `llms-txt` and `ard-schema` all passed, and the three WebMCP audits were not applicable because that run did not enable Chrome's WebMCP testing flag. Chapter 18 shows how to run the full category with the flag in CI.

Before this chapter, `ard-schema` was simply not applicable for Nordlys. A missing ARD manifest is "N/A", not a failure, in Lighthouse, so the category score did not punish us for not having one. What the manifest adds is one more passing audit and, more importantly, a description that registries following ARD can index.

On the isitagentready side, our local checker (the one from Chapter 2, which reimplements the documented checks) reports `ard` as passing with the manifest at `/.well-known/ard.json` linked from the home page. I did not serve a copy at `ai-catalog.json`. The specification treats the old name as a courtesy for consumers, not as a duty for publishers, and a second copy is one more file that can drift. If a client you care about only reads `ai-catalog.json`, a mirror is a two-line change in Listing 11.5.

## OAuth metadata is discovery too

One more family of documents belongs to discovery, although it arrives in Chapter 14. An MCP client that wants to call a protected Nordlys tool on a user's behalf needs to know which authorization server to talk to and which scopes exist. It learns that from OAuth Protected Resource Metadata at `/.well-known/oauth-protected-resource` (RFC 9728) and from the authorization server's own metadata (RFC 8414 or OpenID Connect discovery).[^ch11-19] isitagentready counts these as "auth metadata", one of the three ingredients of its Level 5.[^ch11-1]

Radar puts OAuth discovery on 8.1% of top domains and Protected Resource Metadata on 4.1% as of 2 November 2026, far ahead of server cards and skills.[^ch11-3] Much of that comes from platforms (identity providers and e-commerce platforms publish these files by default), which is a pattern you will see again in Chapter 13: check what your platform already does before you build. For Nordlys, Chapter 14 adds both documents when it puts OAuth in front of the booking tools, and they show up on the ladder below.

## The ones I did not ship

A discovery chapter could easily turn into a list of every file anyone has proposed. isitagentready alone checks 23 things.[^ch11-1] Here are the ones Nordlys leaves out, and why. Each is a reasonable "watch" item, and none is something a small booking site needs in November 2026.

### A2A agent card

A2A (Agent2Agent) is the protocol for one agent to hand work to another agent. Version 1.0.0 shipped on 12 March 2026, and its agent card at `/.well-known/agent-card.json` is a permanent IANA well-known name, the most settled of all the agent discovery files.[^ch11-20][^ch11-8]

So why not publish one? Because an agent card describes an *agent*, something that takes a task, reasons about it and returns a result. Nordlys has tools and data, not an agent. A card that pretends a booking API is an agent would be misleading, and any A2A client that tried to send it a task would get nowhere. If Nordlys one day runs a "concierge" agent that other agents can delegate trip planning to, that agent gets a card, kept separate from the MCP server. Chapter 13 discusses when A2A is the right interface.

There is a scoring consequence, and I want to be upfront about it. isitagentready's Level 5 asks for two of three things: Web Bot Auth, *all four* integration checks (MCP server card, A2A agent card, Agent Skills, API catalog), or auth metadata.[^ch11-1] Without an A2A card, Nordlys can only reach Level 5 through Web Bot Auth plus auth metadata. Web Bot Auth is for sites that *run* bots and sign their requests (Chapter 15 explains why Nordlys verifies signatures instead of making them). So Nordlys stays at Level 4, by choice. The A2A check is even opt-in, off by default in the scanner's own profile, which tells you how its authors weigh it.[^ch11-1] I would rather explain a Level 4 than publish an agent card for an agent that does not exist.

### DNS-AID

DNS for AI Discovery (DNS-AID) publishes agents in DNS: service binding records (SVCB) under an `_agents` label, so a client can discover agents with a DNS query instead of an HTTP request. isitagentready checks for DNSSEC-validated records under names like `_index._agents.example.com`.[^ch11-1] The specification is an individual Internet-Draft, `draft-mozleywilliams-dnsop-dnsaid-02`, which the IETF datatracker labels as "not endorsed by the IETF" with "no formal standing in the IETF standards process", the standard wording for any individual draft.[^ch11-21] Infoblox and GoDaddy announced support for the approach in 2026.[^ch11-22] For Nordlys, it would mean DNSSEC plus new record types to discover the same server card the `Link` header already points to. Watch it, don't ship it.

### auth.md

auth.md is a proposal from WorkOS: "an open protocol that lets agents register for services on behalf of users", discoverable through a Markdown file at your domain plus an `agent_auth` block in the authorization server metadata (MIT licensed).[^ch11-23] isitagentready checks for it as one of the three kinds of auth metadata.[^ch11-1] It addresses a real problem (an agent signing a user up for a service), but it is one vendor's proposal, and Nordlys does not let agents create accounts. Chapter 14 covers delegated access with standard OAuth instead.

### Vertical formats

One more item is worth a sentence because it is specific to our running example. In August 2026, IANA provisionally registered a well-known name `vacation-rental.json` for the "Vacation Rental Protocol", whose specification (version 0.1, status "Draft") describes a site-wide document that tells a client "the origin is a bookable vacation-rental node and how to interact with it".[^ch11-24][^ch11-8] I have not evaluated it beyond reading the specification page, and I found no grader or client that reads it. Chapter 12 looks at the commerce standards with real momentum (UCP has a lodging draft backed by Google). Industry-specific discovery files like this one may matter later, so a booking site should keep an eye on its own vertical.

The scanner also reports a few informational checks that do not affect the level, such as the Personal Agent Protocol file `poppy.json` (draft 0.1).[^ch11-1] Nordlys ignores them, and so can you.

## The ladder, chapter by chapter

Now let's put the whole book's work on one chart. isitagentready's levels are cumulative, and their rules are short enough to quote: Level 1 "Pass 2 of 3: robots.txt, sitemap, link headers", Level 2 adds "both: AI bot rules and Content Signals in robots.txt", Level 3 adds "markdown content negotiation", Level 4 adds "1 of 4: MCP Server Card, A2A Agent Card, Agent Skills, API Catalog", and Level 5 adds "2 of 3: Web Bot Auth, all four integration checks, auth metadata".[^ch11-1]

We ran the local checker from Chapter 2 against the Nordlys demo server with the layers switched on up to each chapter (`npm start -- --upto=N`, Node.js 24.22.1, 2 November 2026). Table 11.2 shows the result, and Figure 11.3 draws it as a staircase.

Table 11.2 Nordlys Cabins on the isitagentready.com level rules, by chapter (local checker, 2 November 2026)

| Layers up to | Level | Checks that pass (selection) | What the next level asks for |
|---|---|---|---|
| Baseline (no layers) | 0 Not Ready | none | robots.txt, sitemap, link headers (2 of 3) |
| Chapter 3 | 1 Basic Web Presence | robotsTxt, sitemap, robotsTxtAiRules | contentSignals |
| Chapter 4 | 2 Bot-Aware | + contentSignals | markdownNegotiation |
| Chapter 6 | 3 Agent-Readable | + linkHeaders, markdownNegotiation | one integration check |
| Chapter 7 | 4 Agent-Integrated | + apiCatalog | 2 of 3 for Level 5 |
| Chapter 11 | 4 Agent-Integrated | + mcpServerCard, agentSkills, ard (webMcp since Chapter 9) | 2 of 3 for Level 5 |
| Chapter 14 to 20 | 4 Agent-Integrated | + oauthDiscovery, oauthProtectedResource | webBotAuth or a2aAgentCard |

![Figure 11.3 — The Nordlys Cabins level ladder. Each step is a chapter: Chapter 3 reaches Level 1, Chapter 4 Level 2, Chapter 6 Level 3 and Chapter 7 Level 4. Chapter 11 adds three discovery checks without changing the level, and Chapter 14 adds auth metadata. Level 5 would need either Web Bot Auth or an A2A agent card on top, which Nordlys deliberately does not publish.](images/figure-11-3.png)

Two things stand out.

First, this chapter does not move the level at all. Nordlys reached Level 4 with one file in Chapter 7, the API catalog, because Level 4 needs only one of the four integration checks. Everything in this chapter is invisible to the level and visible to the per-check report: `mcpServerCard`, `agentSkills` and `ard` turn from fail to pass. That is why I recommend tracking checks, not levels, in CI (Chapter 18 builds that part). A level is a step function, and most real progress happens between the steps.

Second, the last step is out of reach on purpose. With auth metadata from Chapter 14, Nordlys has one of the three Level 5 ingredients. The other two are Web Bot Auth (for sites that run signing bots) and an A2A agent card (for sites that run agents). Neither describes Nordlys. Our research scan of 44 sites on 2 November 2026 found nobody at Level 5 and only eight sites at Level 4, mostly developer platforms.[^ch11-17] A small booking site at Level 4 is in very good company.

In my opinion, this is the right way to read the ladder. It is Cloudflare's view of priorities, written as rules, and it is useful as a checklist. It is not a target to hit at any cost. When a level asks for a file that would describe something your site does not do, the honest answer is to stay one level lower and say why.

## Testing the discovery layer

> **Hands-on:** This section lists the Chapter 11 tests and how to run them. If you don't write code, the summary is: every discovery document is checked against the thing it describes, so the files cannot quietly drift away from the site. Pick up again at "Keeping discovery honest".

The layer comes with five tests in `nordlys-cabins/tests/ch11-discovery.test.js`, using Node's built-in test runner:

1. The MCP server card is served at `/mcp/server-card` with the card media type, the mirror at `/.well-known/mcp/server-card.json` is identical, and the card agrees with a live `server/discover` call about versions.
2. The Agent Skills index uses the v0.2.0 `$schema`, each entry has exactly `name`, `type`, `description`, `url` and `digest`, and the digest is the SHA-256 of the file at that URL.
3. The ARD manifest has at least two entries, each with a `urn:air:nordlys.example:` identifier, a display name, a type, a URL (and no inline `data`) and 2 to 5 representative queries, and the home page `Link` header carries `rel="ard"` next to the `api-catalog` value from Chapter 7.
4. The API catalog lists the REST API and the MCP endpoint, in that order, and the layer's own audit passes.
5. The local agent-readiness checker from Chapter 2, run against a real server on a free port, reports `apiCatalog`, `mcpServerCard`, `agentSkills` and `ard` as passing.

To run them, install the demos once and run the chapter's tests (Node.js 24 or newer, as the repository's `engines` field says):

```bash
npm install
cd nordlys-cabins
node --test tests/ch11-discovery.test.js
```

On 2 November 2026 all five passed, together with the Chapter 7 and Chapter 8 tests they depend on (20 tests in total, with `@modelcontextprotocol/server` and `@modelcontextprotocol/client` 2.4.0).

The fifth test is the closest thing to running the real scanner offline. If you deploy the demo somewhere public, you can also run isitagentready.com itself against it (the web page, or its documented `POST /api/scan` endpoint) and compare.

## Keeping discovery honest

Discovery files have a failure mode that APIs don't: when they go wrong, nothing breaks loudly. A stale server card, a skill that still describes last year's cancellation policy, a manifest whose URL returns 404 after a redesign. Clients just quietly stop using your site, or use it wrongly. A few habits keep that from happening.

**Generate, don't hand-write.** Every Nordlys discovery document is built from the request origin and from data the site already has: the catalog from Chapter 7's function, the card from the host, the digest from the served file. Hand-written JSON in a `public/.well-known/` folder is how sites end up advertising staging URLs in production.

**Test the agreement, not just the presence.** A check that the file exists is what the graders do. Your own tests can do better: compare the card to `server/discover`, the digest to the file, the catalog to the routes. That is what the five tests above do.

**Keep one canonical copy and few mirrors.** Nordlys has exactly one mirror (the server card at the scanner's path). Every extra copy is a future inconsistency. When a standard settles, delete the mirror.

**Write down why each file exists.** This chapter's Table 11.1 is a decent template for your own docs: document, address, standard and status, who reads it, and whether you publish it. When the next rename comes (and in this layer it will), that table tells you what to change and what to ignore.

**Re-check the status twice a year.** Several documents in this chapter changed address or status between April and November 2026. Chapter 20 turns this into a routine for all the standards in the book.

## Summary

- Discovery files tell an agent what a site can do and where its endpoints are, before any tool is called. In November 2026 they are read mostly by graders and registries, and only a little by agents, so keep them cheap and standard.
- The `Link` header on the home page is the cheapest signpost. Nordlys now points to its Markdown version, `llms.txt`, the API catalog and the ARD manifest from one header. Every layer must append to it, never replace it.
- The API catalog (RFC 9727) can list the MCP endpoint next to the REST API, with the server card as its machine-readable description.
- The MCP server card has three competing addresses. Nordlys serves the SEP-2127 location `/mcp/server-card` and mirrors it at `/.well-known/mcp/server-card.json` for today's scanner. The SEP page says "Final" while the extension repository says "Experimental".
- An Agent Skills index (`/.well-known/agent-skills/index.json`, draft v0.2.0) publishes a `SKILL.md` with the booking procedure and policy, with a SHA-256 digest so clients can verify the file.
- ARD v0.91 (a proposal) lists agentic resources in one manifest at `/.well-known/ard.json`, found through `rel="ard"`. Lighthouse validates it and asks for 2 to 5 representative queries per entry. isitagentready's fix prompt still names the older `ai-catalog.json`.
- Nordlys does not publish an A2A agent card, DNS-AID records or auth.md, because each would describe something the site does not do or add a second path to the same information.
- On isitagentready's rules, Nordlys reached Level 4 in Chapter 7 and stays there. This chapter turns three discovery checks green without moving the level, and Level 5 would require files Nordlys deliberately does not publish.
- Test discovery documents against the live interfaces they describe, so they cannot drift without a failing test.

[^ch11-1]: "Is Your Site Agent-Ready? (llms-full.txt)," isitagentready.com, Cloudflare, https://isitagentready.com/llms-full.txt (retrieved November 2026).
[^ch11-2]: "ARD manifest is valid," Lighthouse documentation, Chrome for Developers, https://developer.chrome.com/docs/lighthouse/agentic-browsing/ard (retrieved November 2026).
[^ch11-3]: "AI Insights: Adoption of AI agent standards," Cloudflare Radar, https://radar.cloudflare.com/ai-insights#adoption-of-ai-agent-standards (data dated 2 November 2026, retrieved November 2026).
[^ch11-4]: André Jesus and Vance Morrison, "Introducing the Agent Readiness score. Is your site agent-ready?," The Cloudflare Blog, 17 April 2026, https://blog.cloudflare.com/agent-readiness/ (retrieved November 2026).
[^ch11-5]: "About the MCP Registry," Model Context Protocol, https://modelcontextprotocol.io/registry/about (retrieved November 2026).
[^ch11-6]: Junjie Bu, R.V. Guha and Shaun Smith, "Agentic Resource Discovery Specification," version 0.91 (Proposal), 26 August 2026, https://agenticresourcediscovery.org/spec/ (retrieved November 2026).
[^ch11-7]: M. Nottingham, "Well-Known Uniform Resource Identifiers (URIs)," RFC 8615, IETF, https://www.rfc-editor.org/rfc/rfc8615.html (retrieved November 2026).
[^ch11-8]: "Well-Known URIs," IANA registry (last updated 26 October 2026), https://www.iana.org/assignments/well-known-uris/well-known-uris.xhtml (retrieved November 2026).
[^ch11-9]: M. Nottingham, "Web Linking," RFC 8288, IETF, https://www.rfc-editor.org/rfc/rfc8288.html (retrieved November 2026).
[^ch11-10]: "Link Relations," IANA registry, https://www.iana.org/assignments/link-relations/link-relations.xhtml (retrieved November 2026).
[^ch11-11]: K. Smith, "api-catalog: A Well-Known URI and Link Relation to Help Discovery of APIs," RFC 9727, IETF, https://www.rfc-editor.org/rfc/rfc9727.html (retrieved November 2026).
[^ch11-12]: "SEP-2127: MCP Server Cards - HTTP Server Discovery," Model Context Protocol, https://modelcontextprotocol.io/seps/2127-mcp-server-cards (retrieved November 2026).
[^ch11-13]: "mcp.json," isitagentready.com, https://isitagentready.com/.well-known/mcp.json (retrieved November 2026).
[^ch11-14]: "MCP Server Cards (Experimental Extension)," GitHub, https://github.com/modelcontextprotocol/ext-server-card (retrieved November 2026).
[^ch11-15]: "Specification," Agent Skills, https://agentskills.io/specification (retrieved November 2026).
[^ch11-16]: "Agent Skills Discovery via Well-Known URIs," version 0.2.0 (Draft), Cloudflare on GitHub, https://github.com/cloudflare/agent-skills-discovery-rfc (retrieved November 2026).
[^ch11-17]: "Is Your Site Agent-Ready?," isitagentready.com, Cloudflare, https://isitagentready.com/ (scans of 44 sites run on 2 November 2026 while researching this book, results in the author's research notes) (retrieved November 2026).
[^ch11-18]: "Announcing the Agentic Resource Discovery specification," Google Developers Blog, 17 June 2026, https://developers.googleblog.com/announcing-the-agentic-resource-discovery-specification/ (retrieved November 2026).
[^ch11-19]: M.B. Jones, P. Hunt and A. Parecki, "OAuth 2.0 Protected Resource Metadata," RFC 9728, IETF, https://www.rfc-editor.org/rfc/rfc9728.html (retrieved November 2026).
[^ch11-20]: "Agent2Agent (A2A) Protocol Specification," version 1.0, A2A Project, https://a2a-protocol.org/latest/specification/ (retrieved November 2026).
[^ch11-21]: "DNS for AI Discovery," draft-mozleywilliams-dnsop-dnsaid-02, IETF Datatracker, https://datatracker.ietf.org/doc/draft-mozleywilliams-dnsop-dnsaid/ (retrieved November 2026).
[^ch11-22]: "Infoblox and GoDaddy Support Open Standards for AI Agent Discovery, Identity and Verification," GoDaddy newsroom, 2026, https://aboutus.godaddy.net/newsroom/news-releases/press-release-details/2026/Infoblox-and-GoDaddy-Support-Open-Standards-for-AI-Agent-Discovery-Identity-and-Verification-2026-0acKMntvOC/default.aspx (retrieved November 2026).
[^ch11-23]: "auth.md: An open protocol that lets agents register for services on behalf of users," WorkOS on GitHub, https://github.com/workos/auth.md (retrieved November 2026).
[^ch11-24]: "VRP Well-Known URI: vacation-rental.json, Specification v0.1," Vacation Rental Protocol, https://vacationrentalprotocol.com/spec/well-known-uri-v0.1 (retrieved November 2026).
