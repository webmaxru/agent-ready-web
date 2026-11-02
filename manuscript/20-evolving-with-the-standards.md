# Chapter 20: Evolving with the standards

This chapter covers

- How the standards in this book move: W3C groups, IETF drafts, MCP's dated revisions, schema.org releases and the foundations behind them
- Reading a specification's status line before you build on it
- Versioning your own tools and APIs so agents can follow along, with the Deprecation and Sunset header fields
- A watch list, and a small script that tells you when something on it changed
- A four-quarter agent-readiness roadmap, and the web edition of this book as a case study with its measured scores

Three things changed while this book was being written, and each one touched a chapter. In July 2026 the Model Context Protocol released a revision that removed the session handshake from the core protocol. On 1 July 2026 Cloudflare folded signed agents into its Verified bots. And on 2 November 2026, the day I am writing this chapter, the WebMCP specification gained an `outputSchema` for tools, merged in the afternoon and published the same day.[^ch20-1]

None of this is unusual. Almost every layer in this book rests on something that is still moving: a Community Group report, an Internet-Draft, a protocol with dated revisions, a proposal with one author, a grader whose own documentation says it is "still under development and subject to change". I know the feeling from the other side, too. The first edition of my previous book, *Tools, Not Clicks*, was tagged on 15 October 2026, and its second major version followed on 2 November 2026, because WebMCP had moved enough in between to justify it.[^ch20-2]

So the last chapter of this book is not about one more layer. It is about how to keep all the layers working while the ground moves under them: how to read where a standard stands, how each kind of standard evolves, how to version what *you* publish so that agents can follow your changes, how to notice when something changes, and how to plan a year of agent-readiness work for a team. At the end we look at the web edition of this book, which tries to practise what the book teaches, and at where I think all of this is heading.

## Reading a status line

Every specification tells you how settled it is, usually in one line under its title. Learning to read that line takes five minutes and saves weeks. Here are the status lines you meet in this book, and what each one means for a team that wants to ship.

| What the document says | What it means | Can you ship on it? |
| --- | --- | --- |
| W3C "Draft Community Group Report" | a proposal incubated by a community group, with no formal W3C review | yes, behind feature detection, expecting changes |
| W3C "Working Draft", "Candidate Recommendation" | on the standards track of a Working Group | yes, with care up to Candidate Recommendation |
| W3C "Recommendation" | a finished W3C standard | yes |
| IETF "Internet-Draft", individual (`draft-name-...`) | one author's or company's proposal, not adopted by any group | prototype, watch |
| IETF Internet-Draft, Working Group (`draft-ietf-wg-...`) | adopted by an IETF working group, still changing | yes, if you can update when it changes |
| IETF RFC, Standards Track or Informational | published and stable, never edited (only replaced) | yes |
| MCP revision marked "Current" (a date such as `2026-07-28`) | the revision clients and servers should implement now | yes |
| MCP revision marked "Draft" | the next revision in progress | prototype |
| schema.org release number (30.1) | a vocabulary release, almost always additive | yes |
| Single-author proposal (llms.txt) | a convention with no standards body behind it | yes, if it is cheap and harmless |

Two lines in that table deserve a closer look, because people misread them all the time.

A W3C Community Group report is not a W3C standard, and the document says so itself. The status section of the WebMCP report reads: "It is not a W3C Standard nor is it on the W3C Standards Track."[^ch20-3] WebMCP is such a report. That does not make it unusable (Chrome ships it in an origin trial and Shopify deploys it at scale, as Chapter 1 showed), but it means the API can change without the formal process a Recommendation goes through.

An Internet-Draft is a work in progress, whatever its number. An IETF draft expires about six months after it is posted unless a new revision replaces it (the Web Bot Auth draft posted on 29 October 2026 expires on 2 May 2027), and every draft carries the boilerplate that it is a work in progress, not a standard.[^ch20-4] A `-08` is not "almost done". It means the authors revised it eight times.

Browsers add a second kind of status line, and it is independent of the spec's. A feature in Chrome usually goes through three stages: behind a flag (only people who switch it on in `chrome://flags` get it), an origin trial (sites that register get it for their visitors, for a limited range of Chrome versions) and shipped (everyone gets it). Chrome Platform Status shows the stage of every feature, and the other engines publish their positions in their standards-positions repositories. On 2 November 2026 WebMCP was in an origin trial in Chrome, while WebKit's position was "oppose" and Mozilla's "neutral".[^ch20-24] So "WebMCP works" means "works in Chrome, for sites in the trial, and for developers with the flag". That is plenty to build on, as long as the page works without it.

> **Tip:** Write the status line next to every spec claim in your own documentation, the way this book does ("as of November 2026, a Working Group draft"). When someone reads it a year later, they know exactly what to recheck.

## How each standard moves

Each family of standards in this book has its own process, its own speed and its own signals that a change is coming. Figure 20.1 puts them side by side, with a dot where each one stood in November 2026.

![Figure 20.1 — How the standards in this book move, and where each stood in November 2026. W3C reports and IETF drafts move along a track toward a finished standard. MCP publishes dated revisions. schema.org publishes numbered releases.](images/figure-20-1.png)

### W3C: from Community Group to Working Group

At the W3C, new ideas usually start in a Community Group, which anyone may join and which produces reports without formal review. To become a standard, the work has to move into a Working Group with a charter that lists it as a deliverable. From there it follows the Recommendation track: Working Draft, Candidate Recommendation, Proposed Recommendation and finally Recommendation.[^ch20-19]

WebMCP is incubated in the Web Machine Learning Community Group (I am a member of that group, so I watch this process closely). Two charter discussions on GitHub show where it may go next. The proposed new charter of the Web Machine Learning Working Group, open since 9 June 2026, proposes to work on WebMCP "as a tentative deliverable". And since 28 September 2026 a separate proposal for an Agentic Web Working Group charter is open for review.[^ch20-5] Neither had concluded on 2 November 2026, so WebMCP was still a Community Group report on that day.

> **Still in flux:** Everything this book says about WebMCP's API is as of the Draft Community Group Report dated 2 November 2026 and Chrome's origin trial (Chrome 149 to 162). Check the report's date before you copy code from any chapter, including this one.

Meanwhile, the browser side moves on its own clock. Chrome runs WebMCP as an origin trial from Chrome 149 to Chrome 162, which means that a site needs a trial token (renewed when Chrome asks) to enable it for its visitors, and that the feature has a planned end unless Chrome ships it.[^ch20-6] For a team, the practical consequences are simple: feature-detect `document.modelContext` (Chapter 9 does), keep the token's renewal in someone's calendar, and read the spec's changes before each Chrome release you care about.

### IETF: drafts, working groups and RFCs

At the IETF, anyone can publish an Internet-Draft. A working group can adopt it, which renames it to `draft-ietf-<group>-...`, and revise it until it has consensus. Then it goes through working group last call, review by the IESG, and finally becomes an RFC with a number that never changes.

Two working groups matter most for this book. The Web Bot Auth working group adopted one document, `draft-ietf-webbotauth-httpsig-protocol`, whose revision `-01` is dated 29 October 2026. Its charter had milestones for April and August 2026 to send the specifications to the IESG, and both dates passed without that happening.[^ch20-7] The AI Preferences working group (aipref) has a vocabulary draft at `-08` and a draft for attaching preferences to robots.txt and HTTP at `-05`, both intended as Proposed Standards and both still drafts in November 2026.[^ch20-8] The Content Signals vocabulary that Chapter 4 used is a separate, individual draft (`draft-romm-aipref-contentsignals`), written by Cloudflare and not adopted by the working group.[^ch20-9]

Missed milestones are normal at the IETF, and I would not read anything dramatic into them. What I take from it is a rule: never plan a launch around a predicted RFC date. Build on the draft if it helps you, keep the code that touches it small, and watch the datatracker.

Some drafts are already in your code without you noticing. Chapter 15 sent rate-limit information to agents, and the header fields for that come from another IETF draft, `draft-ietf-httpapi-ratelimit-headers`. Its revision `-11` from May 2026 defines `RateLimit-Policy` and `RateLimit` as structured fields, and it expires on 24 November 2026 unless a new revision appears.[^ch20-25] That is typical: a draft at revision eleven, used by many APIs, still not an RFC. If you emit those headers, put the draft on your watch list. When it changes, your headers may need to change with it.

The good news is that several things this book relies on are already finished RFCs: HTTP Message Signatures (RFC 9421), OAuth 2.0 Protected Resource Metadata (RFC 9728), the API catalog well-known URI (RFC 9727), and the two header fields we use later in this chapter, Deprecation (RFC 9745) and Sunset (RFC 8594).[^ch20-10]

### MCP: dated revisions and SEPs

MCP names its versions after dates. A version string such as `2026-07-28` marks the last backwards-incompatible change, and each revision is labelled Draft, Current or Final. On 2 November 2026 the current revision was `2026-07-28`, and the earlier ones were `2025-11-25`, `2025-06-18` and `2025-03-26`.[^ch20-11] Since the July revision, every request declares its protocol version in its `_meta` field under `io.modelcontextprotocol/protocolVersion`, so a server can accept or reject versions per request instead of per session.

Changes arrive as SEPs (Specification Enhancement Proposals), each with a number and a discussion on GitHub. The headers we logged in Chapter 19 (`Mcp-Method` and `Mcp-Name`) came from SEP-2243, the stateless core from SEP-2575, the deprecation of Roots, Sampling and Logging from SEP-2577.[^ch20-12] Reading the SEPs that are in progress is the best early warning you will get.

The July revision also brought something every API owner should copy: a formal deprecation policy with a minimum window of twelve months. Under it, the legacy HTTP+SSE transport, Roots, Sampling and Logging are deprecated, and Dynamic Client Registration is deprecated in favour of Client ID Metadata Documents (Chapter 14 already uses the new way).[^ch20-13]

Governance changed too. In December 2025 Anthropic donated MCP to the Agentic AI Foundation, a directed fund under the Linux Foundation co-founded by Anthropic, Block and OpenAI, and in August 2026 the A2A protocol joined the same foundation.[^ch20-14]

### schema.org: numbered releases

schema.org publishes numbered releases with a short note for each. Version 29.4 came out on 8 December 2025, 30.0 on 19 March 2026 and 30.1 on 16 September 2026 (it added vocabulary for discovering EU Digital Product Passports and for common e-commerce product data).[^ch20-15] Releases are almost always additive, so a vocabulary you used last year keeps working. If you want to know exactly which release a search engine or validator works with, `https://schema.org/version/latest` shows the current one, and each release has its own permanent URL, which is handy in a bug report. The risk with structured data is rarely schema.org itself. It is what search engines and agents choose to read, which changes without a release note. Chapter 5 covered that.

### Proposals with one author or one company

A good part of the agent-ready web runs on proposals that have no standards body at all, and it is fine to use them as long as you know that.

llms.txt is a proposal by Jeremy Howard, first published on 3 September 2024. Its "v2" page was last modified on 10 August 2026.[^ch20-16] Content Signals is Cloudflare's vocabulary. The isitagentready.com levels are Cloudflare's opinion of what matters first (WebMCP, for example, does not affect the level at all). The Lighthouse Agentic Browsing category was added in Lighthouse 13.2.0 in May 2026 and describes itself as "still under development and subject to change".[^ch20-17] And the discovery files of Chapter 11 are openly contested: the MCP server card has at least three proposed locations.

This is not a reason to avoid them. It is a reason to keep each one cheap to change. A generated llms.txt (Chapter 6) costs nothing to regenerate in a new format. A hand-written one in twelve places costs a sprint.

### Foundations

Several protocols in this book now live in foundations: MCP and A2A in the Agentic AI Foundation, x402 in the x402 Foundation (launched under the Linux Foundation on 2 April 2026), OpenAPI and Arazzo in the OpenAPI Initiative (also under the Linux Foundation), and AP2, according to its own site, was donated to the FIDO Alliance.[^ch20-18] A foundation gives a protocol neutral ownership, a trademark policy and a place for competitors to meet. It does not make the protocol stable. MCP's biggest breaking change came seven months after it joined a foundation. So I treat "joined a foundation" as good news for the long term and as no information at all about next quarter.

## Versioning what you publish

So far we looked at standards that other people change. The more important half of this chapter is about what *you* change. Every tool, API, Markdown file and discovery document you published in this book is an interface, and agents learned to use it. When you change it, an agent that worked yesterday may fail today, quietly, in front of a customer.

People adapt to a redesigned page in a few seconds. Agents do not adapt that way. An agent that has a tool description cached, or a developer's integration built against your API, keeps calling the old shape until something tells it otherwise. So the rule for an agent-ready site is the one good API teams have followed for years, applied to every agent-facing surface: change by adding, announce before removing, and give machines the same warning you give people.

### Additive first

Most changes do not need to break anything. Here is how I sort them for tools (MCP or WebMCP) and API operations:

| Change | Safe? | Why |
| --- | --- | --- |
| Add a new tool or operation | safe | agents that do not know it keep working |
| Add an optional input parameter with a sensible default | safe | old calls are still valid |
| Add a field to the output | usually safe | strict clients that reject unknown fields may break |
| Improve a description | safe in theory, test it | the description is the agent's documentation, so a better one changes behaviour (rerun the Chapter 18 evals) |
| Rename a tool, parameter or field | breaking | old calls fail |
| Make an optional parameter required | breaking | old calls fail validation |
| Change the meaning or unit of a field (price with VAT instead of without) | breaking, and silent | the worst kind, because nothing fails |
| Remove a tool or operation | breaking | announce it first |

Two rows in that table surprise people. A description is part of the interface. Chapter 10 showed how much a tool description changes what an agent does, so editing one is a behaviour change even when the schema stays the same. And the silent change, a field that keeps its name but changes its meaning, is the one I fear most, because no test that checks shapes will catch it. If the meaning changes, change the name.

### When you must break

Sometimes you have to break things. Then run the old and the new side by side for a while, and let the name carry the version. For tools, that means a new tool name (`create_booking_v2`, or better, a name that says what is different) next to the old one. For HTTP APIs, it means a new path (`/api/v2/...`) or a media type version, whichever your API already uses. In both cases the old version keeps working until a date you announce, and your evals from Chapter 18 run against both until the old one is gone.

Please note that an MCP or WebMCP tool list is read by a model, not by a developer. Two tools that do almost the same thing confuse it. So keep the overlap short, mark the old tool in its description ("Deprecated: use `quote_stay` instead. Stops working on 3 May 2027."), and remove it on the date you said.

### Deprecation and Sunset: warnings machines can read

For HTTP, there is a standard way to say "this is going away", and it has two parts. The Deprecation header field (RFC 9745, published in March 2025) says that a resource is deprecated and since when, as a Structured Field Date: an `@` followed by a Unix timestamp. The Sunset header field (RFC 8594, from 2019) says when the resource is expected to stop responding, as an HTTP date. Both can link to more information with a `Link` header: `rel="deprecation"` for a page that explains the change and `rel="successor-version"` for what to use instead.[^ch20-10] [^ch20-20]

Why bother, when you can write a blog post? Because agents and integrations do not read your blog. A header on every response is read by every client, every time, and a well-built client can log a warning, alert its developer or switch to the successor on its own.

> **Hands-on:** The rest of this section adds the `20-versioning` layer to Nordlys Cabins and a small client-side check. If you do not write code, look at Figure 20.2 for the timeline and continue with "A watch list".

Nordlys Cabins has a good candidate for retirement. Before the public API of Chapter 7 existed, the old front end used private JSON endpoints under `/_app/`. We never documented them, but anything that watched the old front end's network traffic could find them, and a few integrations did. Now we want them gone, with six months' notice. Listing 20.1 is the layer.

**Listing 20.1** `nordlys-cabins/layers/20-versioning/index.js` (excerpt) — headers, 410 Gone and the changelog link

```js
  register(app, ctx) {
    ctx.staticFile('/changes.md', CHANGES, { contentType: 'text/markdown; charset=utf-8' });

    ctx.headers(
      (c) => c.req.path.startsWith('/_app/'),
      (c) => {
        const found = SUCCESSORS.map(([re, to]) => [re.exec(c.req.path), to]).find(([m]) => m);
        return deprecationHeaders({
          deprecated: DEPRECATED,
          sunset: SUNSET,
          policy: ctx.absoluteUrl(c, '/changes.md'),
          successor: found ? ctx.absoluteUrl(c, found[1](found[0])) : undefined,
        });
      },
    );

    // After the sunset date the old endpoints answer 410 Gone and name the successor.
    ctx.beforeAuth(async (c, next) => {
      if (!c.req.path.startsWith('/_app/') || ctx.store.today() < SUNSET.slice(0, 10)) return next();
      return c.json({ error: 'gone', detail: `Retired on ${SUNSET.slice(0, 10)}. See /changes.md.` }, 410);
    });

    // Point llms.txt (Chapter 6) at the changelog, if that layer is on. Root files are
    // served before ctx.middleware() runs, so this wraps them from ctx.beforeAuth().
    ctx.beforeAuth(async (c, next) => {
      await next();
      if (c.req.path !== '/llms.txt' || c.res.status !== 200) return;
      const body = await c.res.text();
      const line = `\n## Changes\n\n- [Agent interface changes](${ctx.absoluteUrl(c, '/changes.md')}): deprecations and sunset dates\n`;
      c.res = new Response(body.includes('/changes.md') ? body : body.trimEnd() + '\n' + line, c.res);
    });
```

The layer does three things. It adds the three header fields to every response under `/_app/`, with a successor link that points to the matching public API path. After the sunset date it answers 410 Gone, which tells clients that the resource is gone on purpose, not missing by mistake. And it serves `/changes.md`, a short Markdown changelog of every change to the site's agent interfaces, linked from llms.txt (Chapter 6) so agents can find it. The headers themselves come from a small helper, shown in Listing 20.2.

**Listing 20.2** `chapters/20-evolving-with-the-standards/lib/deprecation.mjs` (excerpt) — building the header fields

```js
export function deprecationHeaders({ deprecated, sunset, policy, successor }) {
  const headers = { deprecation: `@${toEpoch(deprecated)}` }; // RFC 9745: a Structured Field Date
  if (sunset) headers.sunset = new Date(sunset).toUTCString(); // RFC 8594: an HTTP-date
  const links = [];
  if (policy) links.push(`<${policy}>; rel="deprecation"; type="text/markdown"`);
  if (successor) links.push(`<${successor}>; rel="successor-version"`);
  if (links.length) headers.link = links.join(', ');
  return headers;
}
```

This is what an old endpoint sends now (output of a request against the demo app):

```http
HTTP/1.1 200
content-type: application/json
deprecation: @1793577600
sunset: Mon, 03 May 2027 00:00:00 GMT
link: <https://nordlys.example/changes.md>; rel="deprecation"; type="text/markdown", <https://nordlys.example/api/v1/cabins/fjellro>; rel="successor-version"
```

The timestamp `1793577600` is midnight UTC on 2 November 2026. Figure 20.2 shows the timeline from deprecation to sunset.

![Figure 20.2 — Retiring an interface that agents use. From the deprecation date, the old endpoint keeps working and says it is going away. On the sunset date it answers 410 Gone. A client that checks the headers on 10 November 2026 knows it has 174 days left.](images/figure-20-2.png)

On the other side of the wire, a careful client (or an agent framework, or your own integration tests) reads the fields. Listing 20.3 is the check from the same helper module.

**Listing 20.3** `chapters/20-evolving-with-the-standards/lib/deprecation.mjs` (excerpt) — reading them on the client

```js
/** What a careful client (or agent) does with a response: notice, and know the deadline. */
export function checkDeprecation(response, now = new Date()) {
  const deprecated = parseDeprecation(response.headers.get('deprecation'));
  const sunset = parseSunset(response.headers.get('sunset'));
  if (!deprecated && !sunset) return null;
  const links = parseLinks(response.headers.get('link'));
  return {
    deprecated: deprecated ? deprecated <= now : false,
    deprecatedSince: deprecated?.toISOString() ?? null,
    sunset: sunset?.toISOString() ?? null,
    daysLeft: sunset ? Math.ceil((sunset - now) / 86_400_000) : null,
    policy: links.deprecation ?? null,
    successor: links['successor-version'] ?? null,
  };
}
```

Run against the old endpoint as if it were 10 November 2026, it returns:

```text
{
  deprecated: true,
  deprecatedSince: '2026-11-02T00:00:00.000Z',
  sunset: '2027-05-03T00:00:00.000Z',
  daysLeft: 174,
  policy: 'https://nordlys.example/changes.md',
  successor: 'https://nordlys.example/api/v1/cabins/fjellro'
}
```

I like to put exactly this check into the integration tests of anything that calls a third-party API: a test that fails (or warns) when any response carries a `Deprecation` header turns other people's announcements into your to-do list automatically.

The tests in `tests/ch20-versioning.test.js` (five tests) check the headers and successor links, the changelog and its link from llms.txt, that public routes carry no deprecation headers, the 174 days on 10 November 2026, and the 410 after the sunset date (the demo's clock can be moved with `--now`). The standalone folder `chapters/20-evolving-with-the-standards/` has six more tests for the helper itself.

### Your MCP server and the protocol's revisions

The same thinking applies to the protocol underneath your tools. An MCP server that only speaks the newest revision cuts off every client that has not upgraded yet. Since the July 2026 revision, the client sends its protocol version with every request, so a server can serve several revisions side by side and decide per request. My rule of thumb is to support the current revision and the one before it, and to drop the older one when the client libraries your users depend on have moved on. The MCP deprecation policy's minimum window of twelve months is a good yardstick for your own changes too.[^ch20-13]

For WebMCP the moving part is the browser API itself. The `outputSchema` added on 2 November 2026 is a good example: an addition, so existing tools keep working, and a site can add output schemas when Chrome supports them. Feature detection, not version checks, is the tool for that job (Chapter 9).

### When a standard you used is replaced

Sometimes the change is not yours at all: the standard you built on replaces one of its own parts. This book has several examples. MCP deprecated its original HTTP+SSE transport in favour of Streamable HTTP, and Dynamic Client Registration in favour of Client ID Metadata Documents. WebMCP moved its entry point from `navigator.modelContext` to `document.modelContext`, and isitagentready.com still detects the old one as "legacy".[^ch20-22] Chapter 11 showed three competing locations for an MCP server card.

I handle all of these with the same four steps:

1. **Support both.** Accept the old and the new way at the same time (a server that answers on both transports, a page script that checks both entry points, discovery files at every location that a client you care about reads).
2. **Prefer the new.** Point everything you control (your docs, your llms.txt, your own clients) at the new way, so new integrations start there.
3. **Measure the old.** Log how often the old way is still used. The classifier from Chapter 19 and a counter per transport or path are enough.
4. **Remove on evidence.** Drop the old way when the logs say almost nobody uses it, or when the standard's deprecation window ends, whichever is later, and write it in your changelog.

It is not glamorous. It does turn a spec change into a planned task instead of a production incident.

## Keeping what agents know about you fresh

There is one more thing that changes over time, and it is easy to forget: what AI products already know about your site. An answer in a chat product may be based on a page that a crawler read weeks ago. You cannot push a correction into a model or an index. What you can do is make it easy for crawlers to notice changes and cheap for them to fetch them again.

Most of this is ordinary web hygiene that pays off twice. Accurate `lastmod` values in the sitemap tell crawlers which pages changed. `Last-Modified` and `ETag` headers let them revalidate a page without downloading it. A dated changelog in Markdown, linked from llms.txt, tells agents what changed in your *interfaces*. And a feed (the web edition of this book publishes one for its releases) lets anyone who watches you get changes without polling every page.

Two details are specific to agents. First, policy changes take time to reach the crawlers. OpenAI says a robots.txt change takes about 24 hours to affect its search results, and Perplexity says up to 24 hours.[^ch20-23] So when you change your Content Signals or crawler rules, note the date and check the logs (Chapter 19) a few days later, not the same afternoon. Second, user-triggered fetchers read the page at the moment a person asks, so for them your current page is the answer. That is one more reason to keep the pages agents fetch most (the "most-fetched pages" KPI from Chapter 19) accurate. Prices, opening times and cancellation rules on those pages matter more than the rest of the site.

## A watch list

You cannot read every mailing list. But you can know, once a month, whether anything you depend on has a new version. That is what a watch list is for: one row per standard, where to look and what you saw last time. This is the one I used for this book, as of 2 November 2026.

| Standard | Where to watch | Status on 2 November 2026 |
| --- | --- | --- |
| MCP | the versioning page and open SEPs on GitHub | current revision `2026-07-28` |
| WebMCP | the Community Group report, the W3C strategy issues (#560, #576), Chrome origin-trial pages | draft report dated 2 November 2026, origin trial Chrome 149 to 162 |
| Web Bot Auth | IETF datatracker, webbotauth working group | `draft-ietf-webbotauth-httpsig-protocol-01`, 29 October 2026 |
| AI preferences | IETF datatracker, aipref working group | vocabulary `-08`, attachment `-05` |
| schema.org | release notes | 30.1, 16 September 2026 |
| llms.txt | the proposal's site | v2 page modified 10 August 2026 |
| Lighthouse | npm and the release notes | 13.6.0 |
| isitagentready.com | its llms-full.txt, which lists the checks and levels | 23 checks |

The first seven rows have a version string that a program can read, so I wrote a small script that does it. `standards-watch.mjs` reads `watchlist.json` (where each entry says which page to fetch and how to find the version in it: a JSON field, a pattern in the page text or a pattern in the HTML), compares each value with `watch-state.json`, prints the result and exits with code 1 when anything changed, so a scheduled CI job turns red. Listing 20.4 shows how it reads a value.

**Listing 20.4** `chapters/20-evolving-with-the-standards/standards-watch.mjs` (excerpt) — reading one version string

```js
/** Read the version string of one entry from a fetched body. */
export function extract(entry, body) {
  if (entry.type === 'json') {
    const json = JSON.parse(body);
    const values = entry.fields.map((f) => json[f]);
    if (values.some((v) => v === undefined)) throw new Error(`missing field in ${entry.url}`);
    return values.join(' / ');
  }
  // 'html' patterns run on the markup (for dates kept in attributes), 'text' on the visible text
  const m = new RegExp(entry.pattern).exec(entry.type === 'html' ? body : textOf(body));
  if (!m) throw new Error(`pattern not found in ${entry.url}`);
  return m.slice(1).join(' / ');
}
```

This is the output on 2 November 2026, the day I stored the state:

```text
same     Model Context Protocol, current revision: 2026-07-28
same     WebMCP, W3C Community Group draft report: 2026-11-02
same     Web Bot Auth, IETF draft-ietf-webbotauth-httpsig-protocol: 01 / 2026-10-29 10:32:27
same     AI preferences vocabulary, IETF draft-ietf-aipref-vocab: 08 / 2026-09-14 06:18:02
same     AI preferences in robots.txt and HTTP, IETF draft-ietf-aipref-attach: 05 / 2026-08-19 04:25:16
same     schema.org, latest release: 30.1 / 2026-09-16
same     llms.txt proposal, last modified: August 10, 2026
same     Lighthouse (Agentic Browsing category), npm latest: 13.6.0
```

When you run it, some lines will probably say `changed`. That is the point. Read what changed, update the affected part of your site (and, if you are me, of your book), then run `node standards-watch.mjs --update` to store today's values. A monthly schedule is enough for most teams. Patterns in web pages break when the page is redesigned, and the script reports that as an error rather than guessing, which is what you want from a watcher.

To run it on a schedule, a CI job once a month is enough. On GitHub Actions, for example, a workflow with a `schedule` trigger (`cron: '0 6 1 * *'`, the first day of each month at 06:00 UTC) that checks out the repository and runs `node standards-watch.mjs` in this folder fails whenever something changed, and the failed run is your reminder. Keep the job separate from the build, so a moved standard never blocks a release.

The watcher only tells you *that* something moved. Deciding whether it matters is still a person's job, and I suggest you make it someone's named job. On a small team that is one developer for one hour a month. On a large one, the architect who owns the agent interfaces.

## An agent-readiness roadmap for your team

After nineteen chapters of techniques, the honest question from a team is: in which order? Nobody does all of this in one sprint, and you should not try. Figure 20.3 is the roadmap I would propose to a team that starts from an ordinary, well-built website. It runs over four quarters and maps every step to the chapters that cover it and to what the two graders will show.

![Figure 20.3 — A four-quarter agent-readiness roadmap. Measurement starts in the first quarter and never stops. Access and perception come first, then content, then capabilities and trust. The bottom band shows what isitagentready.com and the Lighthouse Agentic Browsing category reflect at each stage.](images/figure-20-3.png)

**Quarter 1: measure, decide, fix the basics.** Run both graders on your key pages and write the scores down (Chapter 2). Classify a month of logs (Chapter 19), so you know who visits before you change anything. Decide your policy per kind of crawler and write it into robots.txt with Content Signals (Chapter 4). Fix the accessibility tree of your most important flows (Chapter 3). Start the content work too: structured data and Markdown versions of your key pages (Chapters 5 and 6). These steps are cheap, and they are what isitagentready.com's first three levels and the first Lighthouse audits (the accessibility tree, layout stability and llms.txt) check. Level 3 needs Markdown content negotiation, so it depends on your hosting.

**Quarter 2: finish the content, start on capabilities.** Complete the structured data, Markdown and llms.txt across the site, and begin the capability work: a documented API, an MCP server or WebMCP tools, designed as Chapter 10 describes. One discovery file (an MCP server card, an Agent Skills index or an API catalog) is what isitagentready.com's Level 4 asks for. If WebMCP is part of your plan, the Lighthouse WebMCP audits come into play in this quarter.

**Quarter 3: capabilities and trust.** Finish the capabilities, make them discoverable (Chapter 11) and add commerce if you sell (Chapter 12). This is the step that changes your product, so pick one channel first. In parallel, start on trust: authorization for agents acting on behalf of people (Chapter 14) and bot identity (Chapter 15). Level 5 of isitagentready.com checks some of exactly these: Web Bot Auth and authorization metadata.

**Quarter 4: trust, measurement and evolution.** Security and privacy (Chapters 16 and 17), the KPIs from Chapter 19, evals and grader checks in CI (Chapter 18), and the habits of this chapter: a deprecation policy, a changelog, a watch list. From now on both graders run in CI, so nothing you built regresses unnoticed.

Two remarks about this plan. First, the graders are a progress bar, not the goal. isitagentready.com's levels are cumulative, so a site can pass most of the advanced checks and still show a low level because it skipped one early check (you will see that in the case study below). Use the individual checks, not the level, to plan. Second, the roadmap is for a site that wants agents to *act*. A content site that only wants to be read correctly can stop after the content work and spend the rest of the year on measurement and content quality. That is a perfectly good outcome.

Each role has a natural place in this plan. Designers and front-end developers own the accessibility work and the declarative WebMCP forms. Content and SEO own the crawler policy and the content work. Developers and architects own the capabilities. Security owns most of the trust work. Product owns the KPIs from Chapter 19, which are what tell you whether to continue in year two, and QA owns the CI that keeps it all green.

## Case study: the web edition of this book

A book that teaches agent-readiness should be agent-ready itself, so the web edition of this book is built to follow its own advice. It is a static site, generated from the same Markdown files as the printed book, which makes it a good test of how far a site without a server can go. Here is what it does and how it measured on 2 November 2026, before its first public deployment.[^ch20-21]

**What it publishes.** Semantic HTML with landmarks and a real search form. A Markdown version of every page at `<page>.md`, announced with `rel="alternate"` and a `Link` header. An llms.txt with one link per chapter, and the whole book as one Markdown file. A robots.txt that names AI crawlers by purpose and carries the Content Signal `search=yes, ai-input=yes, ai-train=no`. A sitemap with `lastmod`, an Atom feed of releases, schema.org `Book` and `Chapter` data, an Agent Skill that tells an agent how to read and cite the book (with a discovery index), and an ARD manifest. And three WebMCP tools: `search_book` (the search form, made into a declarative tool), `list_chapters` and `get_chapter`, both read-only.

**How it scored in Lighthouse.** With Lighthouse 13.6.0, the Agentic Browsing category, Chrome for Testing 156 and the WebMCP testing flag, against a local server that applies the production headers, six page types (home, chapter, part, about, release history and search results) all scored 1.00. The search results page first scored 0.95, because the results arrived after load and pushed the footer down (a layout shift of 0.164). Reserving the space fixed it. That small fix is a good example of why I like having a grader in CI: the problem was invisible to me and obvious to the audit.

**What isitagentready.com should see.** A live scan needs a deployed site, so on 2 November 2026 the book's checks were "expected" results against the local server: robots.txt, sitemap, Link headers, AI bot rules, Content Signals, Agent Skills and ARD all in place. One check is deliberately skipped: Markdown content negotiation. The site is hosted on Azure Static Web Apps, whose static routes cannot vary the response by the `Accept` header. Doing it would need a function or a proxy in front of every page, and I decided the `.md` URLs were enough. Because the levels are cumulative and Level 3 requires negotiation, I expect the site to stop at Level 2, "Bot-Aware", even though it passes Agent Skills and ARD, two checks from higher levels. I find that a useful lesson about levels, and I prefer to report it honestly than to add a proxy for a badge.

For comparison, the site of my previous book, *Tools, Not Clicks*, scored Level 1 ("Basic Web Presence") on the same day. It passed robots.txt and sitemap and failed the rest. That book is about WebMCP, and WebMCP does not count toward the level at all.

**What it taught me.** Three lessons from building it carry over to any site. The first is that generating everything from one source makes agent-readiness almost free to maintain. The llms.txt, the Markdown pages, the structured data and the WebMCP tools of the web edition all come from the same manuscript files and one settings file, so a new chapter shows up everywhere without anyone touching the agent files. The second is that hosting decides more than you expect. I could do everything a static host allows, and the one gap (negotiation by `Accept` header) comes from the platform, not from a lack of effort. When you choose hosting for a new site, add "can it vary a response by request header?" to the list of questions. The third is that the graders disagree, and that is fine. Lighthouse gives the site full marks and isitagentready.com will probably give it Level 2, because they measure different things: one looks at what a browser agent experiences on the page, the other at what a site publishes for agents in general. Reading both, check by check, told me much more than either score alone.

**What is left.** The WebMCP tools need the origin-trial token for real visitors (the testing flag is only for developers), the live scan needs the first deployment, and the Markdown negotiation stays a known gap. All three are in the book's own changelog, which is, of course, on the watch list.

## Where this is heading

I want to end the book with a few observations about direction. These are opinions, and I mark them as such.

The first is that platforms will do more of the work. Chapter 1 showed WebMCP and UCP spreading through e-commerce because Shopify turned them on, not because shop owners read the specs. I expect the same for structured data, Markdown versions, discovery files and probably bot verification: they become settings in your CMS, CDN or hosting, and the craft moves to choosing good defaults and checking that they work. That makes measurement (Chapter 19) and testing (Chapter 18) more important, not less.

The second is that identity becomes normal. Signed agent requests are still the exception in November 2026, but Cloudflare, AWS and Vercel already verify them, OpenAI signs its agent traffic and Google experiments with it. Once most serious agents sign, "who is this?" stops being guesswork, and the interesting questions move to "what may it do for whom?", which is Chapter 14's territory.

The third is that the boundary between "a website" and "a tool" keeps blurring. A page with WebMCP tools is both. An API with an MCP server is both. I do not think the web page goes away. People still want to look before they book a cabin in the mountains. But the same site increasingly has two front doors, and the teams that do well treat both as products.

And the last one is less an opinion than a request. Most of the standards in this book are still open for comments: the WebMCP repository, the MCP SEPs, the IETF working groups. They are better when people who build real sites take part. If something in this book did not work for your site, that is useful information for the people writing these specs, and I hope you send it to them.

## Summary

- Almost every layer of the agent-ready web is still moving. Read the status line of every spec before you build on it, and write it next to your own claims.
- A W3C Community Group report (WebMCP) is not a W3C standard. A Working Group draft at the IETF is not an RFC. Never plan a launch around a predicted publication date.
- MCP publishes dated revisions, labelled Draft, Current or Final, with a deprecation policy of at least twelve months. Since July 2026 each request carries its protocol version.
- schema.org releases are numbered and almost always additive. Single-author proposals and graders (llms.txt, Content Signals, isitagentready levels, the Lighthouse category) are fine to use, as long as each is cheap to change.
- Foundations give protocols neutral ownership, not stability.
- Change your own agent interfaces by adding. When you must break, run old and new side by side, put the version in the name, and announce the removal.
- The Deprecation (RFC 9745) and Sunset (RFC 8594) header fields, with `rel="deprecation"` and `rel="successor-version"` links, warn every client on every response. After the sunset, answer 410 Gone.
- A watch list and a monthly script tell you when something you depend on changed. Deciding what it means is a named person's job.
- A four-quarter roadmap: measure and set policy, then content, then capabilities, then trust and evolution. Use the graders as a progress bar, not as the goal.

[^ch20-1]: Model Context Protocol, "Key Changes" for revision 2026-07-28, https://modelcontextprotocol.io/specification/2026-07-28/changelog, Cloudflare Docs, "Verified bots", https://developers.cloudflare.com/bots/concepts/bot/verified-bots/, and the WebMCP repository, pull request 254, https://github.com/webmachinelearning/webmcp/pull/254 (all retrieved November 2026).
[^ch20-2]: Release history of *Tools, Not Clicks*, https://github.com/webmaxru/webmcp-book (tag v1.0.0 on 15 October 2026, release v2.0.0 on 2 November 2026).
[^ch20-3]: Web Machine Learning Community Group, "WebMCP", Draft Community Group Report, 2 November 2026, https://webmachinelearning.github.io/webmcp/ (retrieved 2 November 2026).
[^ch20-4]: draft-ietf-webbotauth-httpsig-protocol-01, "Status of This Memo", https://www.ietf.org/archive/id/draft-ietf-webbotauth-httpsig-protocol-01.txt (retrieved November 2026).
[^ch20-5]: W3C strategy issues "[wg/webmachinelearning] Web Machine Learning Group Charter", https://github.com/w3c/strategy/issues/560, and "[wg/agenticweb] Agentic Web Group Charter", https://github.com/w3c/strategy/issues/576 (both open on 2 November 2026).
[^ch20-6]: Chrome for Developers, WebMCP origin trial announcement, 9 June 2026, https://developer.chrome.com/blog/ai-webmcp-origin-trial, and Chrome Platform Status, https://chromestatus.com/feature/5117755740913664 (retrieved November 2026).
[^ch20-7]: IETF Datatracker, "draft-ietf-webbotauth-httpsig-protocol", https://datatracker.ietf.org/doc/draft-ietf-webbotauth-httpsig-protocol/, and the Web Bot Auth working group's charter and milestones, https://datatracker.ietf.org/wg/webbotauth/about/ (retrieved November 2026).
[^ch20-8]: IETF Datatracker, "draft-ietf-aipref-vocab", https://datatracker.ietf.org/doc/draft-ietf-aipref-vocab/, and "draft-ietf-aipref-attach", https://datatracker.ietf.org/doc/draft-ietf-aipref-attach/ (retrieved November 2026).
[^ch20-9]: IETF Datatracker, "draft-romm-aipref-contentsignals", https://datatracker.ietf.org/doc/draft-romm-aipref-contentsignals/ (retrieved November 2026).
[^ch20-10]: RFC 9421, https://www.rfc-editor.org/rfc/rfc9421, RFC 9728, https://www.rfc-editor.org/rfc/rfc9728, RFC 9727, https://www.rfc-editor.org/rfc/rfc9727, RFC 9745, "The Deprecation HTTP Response Header Field", https://www.rfc-editor.org/rfc/rfc9745, and RFC 8594, "The Sunset HTTP Header Field", https://www.rfc-editor.org/rfc/rfc8594.
[^ch20-11]: Model Context Protocol, "Versioning", https://modelcontextprotocol.io/specification/versioning (retrieved 2 November 2026).
[^ch20-12]: Model Context Protocol, "Key Changes" for revision 2026-07-28, https://modelcontextprotocol.io/specification/2026-07-28/changelog (retrieved November 2026).
[^ch20-13]: Same as above, and the Model Context Protocol deprecation policy linked from it (retrieved November 2026).
[^ch20-14]: Linux Foundation, announcement of the Agentic AI Foundation, 9 December 2025, https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation, and A2A Protocol blog, "A new chapter for A2A: joining the Agentic AI Foundation", 27 August 2026, https://a2a-protocol.org/latest/blog/2026/08/27/a-new-chapter-for-a2a-joining-the-agentic-ai-foundation/ (retrieved November 2026).
[^ch20-15]: schema.org, "Releases", https://schema.org/docs/releases.html (retrieved 2 November 2026).
[^ch20-16]: llms.txt, https://llmstxt.org/ (retrieved November 2026).
[^ch20-17]: Lighthouse source, core/config/agentic-browsing-config.js, and release notes for v13.2.0, https://github.com/GoogleChrome/lighthouse/releases (retrieved November 2026).
[^ch20-18]: Coinbase Developer Documentation, "x402 Foundation", https://docs.cdp.coinbase.com/x402/support/x402-foundation, OpenAPI Initiative, https://www.openapis.org/, and AP2, "AP2 v0.2 Release and FIDO Alliance Donation" on https://ap2-protocol.org/ (all retrieved November 2026). The date of the AP2 donation is UNVERIFIED.
[^ch20-19]: W3C, "W3C Process Document", https://www.w3.org/policies/process/ (retrieved November 2026).
[^ch20-20]: RFC 5829, "Link Relation Types for Simple Version Navigation between Web Resources" (defines `successor-version`), https://www.rfc-editor.org/rfc/rfc5829.
[^ch20-21]: Measurements made for this book on 2 November 2026 and documented in the book repository's AGENT-READY.md.
[^ch20-22]: isitagentready.com, check list in https://isitagentready.com/llms-full.txt (retrieved 2 November 2026), and the WebMCP report (see note 3).
[^ch20-23]: OpenAI, "Overview of OpenAI Crawlers", https://platform.openai.com/docs/bots, and Perplexity, "Perplexity Crawlers", https://docs.perplexity.ai/docs/resources/perplexity-crawlers (both retrieved November 2026).
[^ch20-24]: Chrome Platform Status, https://chromestatus.com/feature/5117755740913664, WebKit standards positions issue 670, https://github.com/WebKit/standards-positions/issues/670, and Mozilla standards positions issue 1412, https://github.com/mozilla/standards-positions/issues/1412 (retrieved November 2026).
[^ch20-25]: draft-ietf-httpapi-ratelimit-headers-11, https://www.ietf.org/archive/id/draft-ietf-httpapi-ratelimit-headers-11.txt (retrieved November 2026).
