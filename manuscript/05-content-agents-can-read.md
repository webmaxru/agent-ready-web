# Chapter 5: Content agents can read

This chapter covers

- Structured data with schema.org: who actually reads it in November 2026, and how to model a booking site
- Generating JSON-LD from the same data as the page, and checking it in CI for syntax, vocabulary and parity
- Why HTML is an expensive format for agents, and serving Markdown from the same URL with content negotiation
- llms.txt, sitemaps, feeds and Link headers as the map that leads agents to the content
- How to find out who actually reads all of this on your site

Chapter 4 decided who may come in. This chapter is about what they find when they do, and it has two halves. The first half gives the facts of Nordlys a typed form, structured data. The second half serves the words around those facts in the format agents read most cheaply, Markdown, and draws the map that leads agents to it.

Look at the Fjellro page of Nordlys Cabins with an agent's eyes. Somewhere in the HTML it says "From NOK 2,200 per night", a bit further down "Friday and Saturday nights cost NOK 2,600", and then "Cleaning, bed linen and towels: NOK 900 per stay". A person reads that in two seconds and knows what a weekend costs. A program has to guess. Which number is the price? Per night or per stay? Is "2,200" two thousand two hundred or two point two? And is "Fjellro" a cabin, a company or a mountain?

Structured data is the site saying it explicitly: this is a vacation rental, it sleeps six, a weekday night costs 2200 Norwegian kroner, a weekend night 2600, and here is the URL where you book it. It is one of the oldest "machine-readable" layers of the web, and for exactly that reason it is surrounded by myths. Some say structured data is the secret to appearing in AI answers. Others say it's dead because Google dropped half of its rich results. Both are wrong, and we will look at the evidence for each claim.

## Structured data in one page

Structured data is a description of the things a page is about, in a vocabulary that machines agree on. On the web that vocabulary is almost always schema.org, started by the major search engines in 2011 and developed in the open. As of November 2026 the current release is version 30.1, published on 16 September 2026.[^ch05-1]

There are three ways to put schema.org into a page: microdata and RDFa (attributes woven into the HTML elements) and JSON-LD (a separate JSON document in a `<script type="application/ld+json">` element). Google supports all three and says "all 3 formats are equally fine for Google", but recommends JSON-LD "in most cases" because it is the easiest to implement and maintain.[^ch05-2] JSON-LD is also the format that survives transformations best, which matters for agents. For example, Cloudflare's Markdown for Agents strips almost everything except text when it converts a page to Markdown, but it "preserves any `<script type="application/ld+json">` blocks", appending them to the Markdown as a fenced JSON block.[^ch05-3] We use JSON-LD throughout.

A JSON-LD block has an `@context` that says which vocabulary the words come from, an `@type` that says what kind of thing this is, and properties of that type. Types form a hierarchy. A `VacationRental` is a `LodgingBusiness`, which is a `LocalBusiness`, which is both an `Organization` and a `Place`, so a vacation rental can use the properties of all of them.[^ch05-4] That hierarchy is also the source of most mistakes, as we will see when the tests run.

## Who reads your structured data in 2026

This is the question that decides how much effort structured data deserves, so let's answer it with sources rather than hopes. Table 5.1 is what I could verify on 2 November 2026.

**Table 5.1** Who reads schema.org JSON-LD, by evidence (November 2026)

| Consumer | What it does with structured data | Evidence |
| --- | --- | --- |
| Google Search | Uses it to understand pages and to show rich results for supported features | Google's own documentation[^ch05-2] |
| Google's AI features (AI Overviews, AI Mode) | Nothing special: "Structured data isn't required for generative AI search, and there's no special schema.org markup you need to add" | Google's AI optimization guide, updated 10 July 2026[^ch05-5] |
| Cloudflare Markdown for Agents | Keeps JSON-LD in the Markdown it serves to agents | Cloudflare documentation[^ch05-3] |
| NLWeb | Ingests schema.org and RSS, and answers questions with schema.org objects | Microsoft announcement and the project's API docs[^ch05-6] |
| ChatGPT shopping and agentic commerce | Uses product feeds that merchants upload, not page markup | OpenAI's product feed specification for agentic commerce[^ch05-7] |
| Browsing agents (Claude in Chrome, Gemini in Chrome, Comet and others) | Unknown | No vendor document says these agents read JSON-LD during a task |

The last row is the honest center of this chapter. It is plausible that a browsing agent which reads the DOM also reads a JSON-LD block in it. An agent that hands raw HTML to a model would include the block, and a model that sees a clean `"price": 2200` will probably use it. But I found no vendor documentation that confirms it, so I treat "agents read your JSON-LD" as plausible and unverified, and so should you.

To make this concrete, follow one task through the site: "Find a cabin for six people in Norway with a fireplace, and tell me what a weekend costs."

Without structured data, a program has the visible text. It finds "Sleeps 6 guests" in a definition list, "From NOK 2,200 per night" a bit further, and "Friday and Saturday nights cost NOK 2,600" in a paragraph under the features. It finds "Fireplace or wood stove" in a list of tags. A capable model will put these together correctly most of the time. But "most of the time" carries the weight here. It has to infer that "From" means a minimum, that the weekend sentence overrides the nightly rate for two nights, that the cleaning fee is per stay and not per night, and that the "6" in "Sleeps 6 guests" is a maximum. Every inference is a chance to be wrong, and the cost of being wrong is a quote that doesn't match the checkout.

With structured data, the same facts arrive labelled. `occupancy.maxValue` is 6. There are two `UnitPriceSpecification` items with `unitText` "night" and names that say which nights, and one `PriceSpecification` for the stay. The amenity is a `LocationFeatureSpecification` with the value `true`. Nothing needs to be guessed, and the same parsing works for every cabin on the site and, in principle, for every rental on the web that uses the same vocabulary.

What does that leave? A lot, actually. Structured data is the one place on your site where the facts about your business (what you sell, what it costs, where it is, how people rated it) live in a typed, unambiguous form. Google uses it today. Pipelines that convert pages to Markdown keep it. And every layer this book adds later (the Markdown version in this chapter, the API and MCP tools in Chapter 8, WebMCP in Chapter 9) needs the same facts in a typed form. If you generate structured data from your data, you have already done half of the modelling work for all of them. Sell it inside your team as a machine-readable source of truth that several consumers read, not as "Google stars" and not as an AI ranking trick.

The "stars" argument has become weaker every year anyway. Google phased out several rich-result features in 2025, and FAQ rich results stopped appearing in Google Search on 7 May 2026.[^ch05-8] Vacation rental rich results are open only to sites that work with a Google Technical Account Manager and the Hotel Center,[^ch05-9] which a small operator with six cabins is not. None of that makes the markup wrong. `FAQPage` is still a valid type that describes the page, so Nordlys keeps it and promises no star or snippet for it.

## Modelling a booking site

Before writing any code, let's decide what Nordlys actually is in schema.org terms. This part needs product and content people in the room, not only developers, because each choice is a statement about the business.

**The types.** `LodgingBusiness` is correct but generic, and `Hotel` or `Resort` don't fit a single timber cabin in Rondane. `VacationRental` is "a kind of lodging business that focuses on renting single properties for limited time".[^ch05-4] That is exactly Nordlys. The pattern that Google's partner documentation and schema.org both support is a `VacationRental` (the listing you book with) whose `containsPlace` is an `Accommodation` (the physical cabin with its beds and amenities). The rental has the address, check-in times, offers and reviews, and the accommodation has the occupancy and bedrooms. The home page describes the company (`Organization`) and the site (`WebSite`), guide articles are `BlogPosting` items, the FAQ is a `FAQPage`, and Nordlys has no events, so it has no `Event` markup. We mark up what is on the page.

**The prices.** The price is the fact agents care about most, and the one with the most traps. Nordlys has a weekday nightly rate, a weekend nightly rate and a cleaning fee per stay, so a single `"price": 2200` would be misleading. Schema.org's answer is an `Offer` with a list of price specifications: two `UnitPriceSpecification` items with `"unitText": "night"` and a plain `PriceSpecification` for the fee, each with a `name` that repeats the wording of the page. And the property that connects the offer to the rental is `makesOffer`, not `offers`. In schema.org, `offers` belongs to things that are offered (a `Product`, a `Service`, an `Event`), while a business uses `makesOffer`, whose domain is `Organization` and `Person`.[^ch05-10] A validator that checks domains catches this mistake. A quick look at an example on the web does not.

**The reviews.** Real guest reviews become `Review` items, and a computed `AggregateRating` sits on the rental. Only real reviews go in, because Google says "Don't mark up irrelevant or misleading content, such as fake reviews".[^ch05-11] And the aggregate must be something the visitor can see, a rule we come back to in a moment.

**The action.** For a rental, the natural `potentialAction` is `ReserveAction`, which "reserves concrete objects (e.g. a table, a hotel) towards a time slot / spatial allocation".[^ch05-12] Its `target` is an `EntryPoint` with a `urlTemplate`:

```
https://nordlys.example/book/fjellro?checkIn={checkIn}&checkOut={checkOut}&guests={guests}
```

The template is not decoration. The Nordlys booking form really accepts these query parameters and fills in the fields, so an agent that understands it can take a person straight to a prefilled form where the person reviews and confirms. Treat it as a clear, cheap statement of intent. The real action layers of this book are the API and MCP server in Chapter 8 and the WebMCP tools in Chapter 9. Figure 5.1 shows the whole cabin graph.

![Figure 5.1 — The JSON-LD graph of one Nordlys cabin. The VacationRental is the listing you book with, the Accommodation inside it is the physical cabin, and the Offer, Reviews and ReserveAction hang off the listing.](images/figure-5-1.png)

Before we write code, these are the mistakes I check for first when I review someone's markup: `offers` on a business, prices as formatted strings like `"NOK 2,200"` instead of a number and a separate `priceCurrency`, relative URLs that become ambiguous once the JSON-LD is copied out of the page, a `LodgingReservation` on a listing instead of a confirmation page, two blocks from a plugin and a theme that disagree, and placeholder values that fill every recommended property to satisfy a validator. A missing property is honest. A fake value is not.

## True to the page

There is one rule that matters more than any type choice, and Google states it in plain words: "Don't mark up content that is not visible to readers of the page. For example, if the JSON-LD markup describes a performer, the HTML body must describe that same performer."[^ch05-11] Google's page about AI features repeats the idea that markup should match the visible text.[^ch05-13]

Honestly, I would follow this rule even if no search engine enforced it. Markup that says one thing while the page says another loses every consumer's trust. Markup written separately from the page drifts, and an agent then quotes last season's price to a guest. And a JSON-LD block is text that a model may read, which is exactly the channel prompt injection uses. If your rule is "nothing in the markup that isn't on the page", a reviewer can check the markup by looking at the page, and hidden instructions have nowhere to hide (Chapter 10 comes back to injection through content).

The practical consequence for Nordlys was small but instructive. Two facts in the cabin graph were not visible on the original page: the average rating and the coordinates. I had two options: drop them from the markup, or show them on the page. Both are fine. I chose to show them, because they are useful to people too, so the layer adds one line at the end of every cabin page: "Average guest rating 4.5 out of 5 from 2 reviews. Location 69.58° N, 20.21° E." Now every fact in the graph is a fact a visitor can see, and a test checks that it stays that way.

The deeper fix is architectural. If the price in the JSON-LD and the price on the page come from the same field of the same record, they can't drift apart. If they come from two places, they will, sooner or later. In simple words: don't write structured data, generate it.

## Hands-on: the structured-data layer

> **Hands-on.** This section builds layer `05-structured-data` in the Nordlys demo. If you don't write code, read the explanations and skip to "Checking markup in CI". You will not miss any decision.

The layer lives in `demos/nordlys-cabins/layers/05-structured-data/`. `graph.js` builds the JSON-LD for each page kind from the same records the page templates render (there is not a single literal fact about a cabin in that file), `index.js` registers it, and `schema-check.js` is the vocabulary check we meet in a moment. To run the site up to this chapter:

```
cd demos/nordlys-cabins
npm start -- --upto=5
```

Every main node has an `@id`, a URL with a fragment such as `https://nordlys.example/cabins/fjellro#rental`, so other nodes can point at it instead of repeating it. All URLs are absolute and built from the configured public origin. Prices are numbers, and formatting is the page's job. A cabin with no reviews gets no rating at all, instead of a "0 out of 5" that would be both wrong and harmful. When a layer hook returns `{ jsonLd }`, the core writes a `<script type="application/ld+json">` element and escapes `<` inside the JSON, so a review text that contains `</script>` can't break out of the block. Listing 5.1 is the start of the real output for Fjellro.

**Listing 5.1** The start of the JSON-LD on `/cabins/fjellro` (output, excerpt)

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "VacationRental",
      "@id": "https://nordlys.example/cabins/fjellro#rental",
      "additionalType": "Cabin",
      "identifier": "fjellro",
      "name": "Fjellro",
      "url": "https://nordlys.example/cabins/fjellro",
      "address": { "@type": "PostalAddress", "addressRegion": "Innlandet", "addressCountry": "NO" },
      "geo": { "@type": "GeoCoordinates", "latitude": 61.87, "longitude": 9.77 },
      "checkinTime": "16:00",
      "checkoutTime": "11:00",
      "containsPlace": {
        "@type": "Accommodation",
        "additionalType": "EntirePlace",
        "occupancy": { "@type": "QuantitativeValue", "maxValue": 6 },
        "numberOfBedrooms": 3,
        "bed": "2 double beds, 2 single beds",
        ...
      },
      "makesOffer": { "@type": "Offer", "priceSpecification": [ ... ] },
      "potentialAction": { "@type": "ReserveAction", ... },
      "aggregateRating": { "@type": "AggregateRating", "ratingValue": 5, "reviewCount": 1, ... }
    },
    { "@type": "BreadcrumbList", ... }
  ]
}
```

## Checking markup in CI

Structured data has an unpleasant property: when it's wrong, nothing breaks. The page renders, the booking tests pass, and the mistake sits there until somebody opens a validator, which may be never. So let's make the build check it, at three levels (Figure 5.2).

![Figure 5.2 — Three levels of checking. Syntax (does it parse and expand?), vocabulary (does every type and property exist, and does each property belong to its type?) and parity (does the markup say what the page says?).](images/figure-5-2.png)

**Level 1: syntax.** The test fetches every content page, extracts the `ld+json` blocks, parses them and expands each one with the `jsonld` package (version 9.0.0) to make sure it is valid JSON-LD, not only valid JSON.[^ch05-14] A tiny local document loader answers for `https://schema.org`, so the test doesn't depend on the network.

**Level 2: vocabulary.** JSON-LD happily accepts any property name, so `"makesoffer"` (lowercase) or `"offers"` on a business expand without a complaint. Schema.org publishes the whole vocabulary as one JSON-LD file, a little over 3,000 terms in version 30.1.[^ch05-15] The layer copies from it the superclasses of every type and the allowed domains of every property it uses (25 types and 52 properties), and a short check asks: is one of this property's declared domains the type itself or one of its ancestors?

I can tell you that this check is worth having from first-hand experience with this very chapter. My first version of the cabin graph pointed from the rental to the company with `provider`, which looks perfectly reasonable. The vocabulary check failed with "provider is not a property of VacationRental". It's right: in schema.org, `provider` belongs to things like services, reservations and creative works, not to businesses. The fix was `parentOrganization`, which belongs to `Organization`. No visual review would have caught it, and Google's own tools would only have flagged it if I had pasted that exact page into them.

**Level 3: parity.** The last level checks the promise from "True to the page" (Listing 5.2).

**Listing 5.2** The markup says what the page says (`tests/ch05-structured-data.test.js`, excerpt)

```js
test('the markup says what the page says', async () => {
  const { app, store } = await buildApp({ upto: 5, publicOrigin: ORIGIN });
  const cabin = store.getCabin('fjellro');
  const { html, data } = await blocks('/cabins/fjellro', app);
  const rental = data[0]['@graph'].find((n) => n['@type'] === 'VacationRental');
  const [weekday, weekend, cleaning] = rental.makesOffer.priceSpecification;
  for (const amount of [weekday.price, weekend.price, cleaning.price]) {
    assert.ok(html.includes(`NOK ${new Intl.NumberFormat('en-GB').format(amount)}`), `price ${amount} is visible`);
  }
  assert.equal(weekday.price, cabin.nightlyRate);
  const reviews = store.reviewsFor('fjellro');
  assert.equal(rental.review.length, reviews.length);
  assert.ok(html.includes(`Average guest rating ${rental.aggregateRating.ratingValue} out of 5`));
  assert.ok(html.includes(`${cabin.geo.latitude}° N`));
  assert.equal(rental.potentialAction.target.urlTemplate,
    `${ORIGIN}/book/fjellro?checkIn={checkIn}&checkOut={checkOut}&guests={guests}`);
});
```

It checks that every price in the markup appears on the page in the page's own format, that the weekday price equals the price in the store, that the number of reviews matches, that the average rating and the coordinates are visible, and that the `ReserveAction` template points at the right URL. A neighbouring test fills the template with real dates and requests the URL to prove that the booking form opens prefilled.

On 2 November 2026, all six tests passed on Node.js 22.23.2 with `jsonld` 9.0.0. Automated checks complement the two official validators, the Schema Markup Validator and Google's Rich Results Test, which has no public API and stays a manual step.[^ch05-16] And whatever produces your markup (a CMS plugin, a commerce platform, a framework), the same three checks work on the rendered HTML. In a framework with server rendering, generate the JSON-LD on the server from the same props that render the page, so it is in the first response that fetchers and Markdown converters see.

Generation also does not solve drift between the page and reality. Keep `datePublished` and `dateModified` honest, because consumers that learn your dates are noise will ignore them, and Google uses a sitemap's `lastmod` only when it is "consistently and verifiably" accurate.[^ch05-17] Mark up the general rate the page states, and leave date-specific quotes to the interactive layers of Part 2. And when a review leaves the page, it leaves the markup.

## Why HTML is expensive to read

Now for the words around the facts: cabin descriptions, guide articles, FAQ answers. People read them in a browser, with a header, a menu, a footer and a stylesheet that turns a dozen nested elements into one clean paragraph. An agent reads the same page as a long string of markup, and it pays for every character of it, in tokens, in time and in the chance that it picks the wrong thing out of the noise.

Cloudflare Radar reports which content types its network serves to AI bots. In the seven days to 2 November 2026, AI bots received HTML 73.2% of the time, plain text 7%, JSON 5.5%, images 4.7% and Markdown less than 0.1%.[^ch05-18] So almost everything an AI crawler or fetcher reads is HTML, built for browsers. The same dashboard shows what Markdown changes: for responses converted by Cloudflare's Markdown for Agents feature, the median Markdown response is 7.9% of the original size.[^ch05-18] That's more than twelve times smaller.

Individual measurements tell the same story with more drama. Cloudflare's Markdown for Agents announcement measured its own blog post at 16,180 tokens as HTML and 3,150 as Markdown,[^ch05-19] and Checkly measured one documentation page at 180,573 tokens as HTML and 478 as Markdown.[^ch05-20] Size matters for cost and speed (agent tools often cut a long page off at some limit), for accuracy (a "you may also like" box competes with the price you need) and for room in the context window when an agent compares four cabins.

## Serving Markdown

There are three common ways to give agents Markdown, and they combine well. *Content negotiation* serves Markdown at the normal URL when the client sends `Accept: text/markdown`, which is the HTTP way and what isitagentready checks. *Separate `.md` URLs* such as `/cabins/fjellro.md` work for clients that can't set headers and are easy to link from llms.txt. *Edge conversion* lets a CDN convert HTML on the way out, with no code changes. Cloudflare's Markdown for Agents strips navigation, keeps JSON-LD and sets `Vary: Accept`.[^ch05-21] Nordlys does the first two in the application, from data, and doesn't depend on the third.

> **Warning:** When the origin response has no `content-signal` header, Markdown for Agents adds a default `Content-Signal: ai-train=yes, search=yes, ai-input=yes`.[^ch05-21] If you decided in Chapter 4 that your answer to training is "no", an edge feature can quietly attach the opposite answer to every Markdown response. Send your own `Content-Signal` header from the origin, and the CDN keeps it. Nordlys does exactly that.

Negotiation only helps if clients ask. In February 2026, Checkly tested seven coding agents, and three of them requested Markdown: Claude Code (2.1.38), Cursor (2.4.28) and OpenCode (1.2.5). OpenAI Codex, Gemini CLI (0.28.2), GitHub Copilot and Windsurf did not.[^ch05-20] These are coding agents fetching documentation, and browsing agents that drive a real browser never send the header at all. So Markdown serves one important group well, the agents that fetch pages over plain HTTP, and does nothing for the others. That's fine. Each layer in this book serves some agents, and none serves all of them. On the server side, Radar's November 2026 scan found Markdown negotiation on 4.3% of 115,468 top domains.[^ch05-22]

## Content negotiation done right

Content negotiation is easy to get almost right, and the "almost" is where caches serve Markdown to browsers. These are the rules Nordlys follows:

- **Only an explicit request gets Markdown.** A browser's `*/*` technically accepts Markdown too, but no browser wants it. Nordlys serves Markdown only when the client names `text/markdown` with a quality at least as high as HTML, and HTML stays the default, as isitagentready's own fix text says.[^ch05-23]
- **`Vary: Accept` on both versions.** Otherwise a shared cache can store the Markdown and serve it to the next browser, or the other way round.[^ch05-24]
- **One canonical URL.** The Markdown response carries `rel="canonical"` to the page, and the HTML links back with `rel="alternate"; type="text/markdown"`.
- **The same facts in both.** Markdown that omits navigation is fine. Markdown with different prices or extra claims is cloaking, and we test it like the JSON-LD.
- **Public pages only.** A member's "My bookings" stays HTML, and `.md` responses are built from a fresh internal request without cookies, so no session data can end up in a cached Markdown file.
- **Your own content signal**, generated from the same policy object as robots.txt in Chapter 4.

![Figure 5.3 — One URL, two representations. A browser and an agent request the same URL and get HTML or Markdown depending on the Accept header. Both responses carry Vary: Accept, so a shared cache keeps them apart, and .md URLs map to the same Markdown.](images/figure-5-3.png)

How do agents find the Markdown? A coding agent that sends `Accept: text/markdown` gets it directly from the normal URL, about 400 tokens for the FAQ instead of almost 1,900. A fetcher that doesn't negotiate can follow the `Link` header or the `<link>` element to the `.md` URL, if its authors made it do so, and I found no survey that measures that. An assistant that starts from the site rather than a page can read `/llms.txt` and get the whole catalogue in one short file. And a browsing agent that drives a real browser never asks for Markdown at all, so for it the work of Chapter 3 and the tools of Chapter 9 matter. The layers of this chapter don't replace good HTML. They add a cheaper, cleaner path for the clients that can use one.

## Hands-on: the agent-content layer

> **Hands-on.** This section builds layer `05-agent-content` in the Nordlys demo, the second of this chapter's two layers after `05-structured-data`. If you don't write code, read the explanations after the listing and continue with "Measuring the savings".

The layer lives in `demos/nordlys-cabins/layers/05-agent-content/`: `negotiate.js` decides who gets Markdown, `markdown.js` renders the Markdown views, `index.js` wires everything into the site, `llms.js` builds llms.txt, `feed.js` builds the Atom feed of the guide, and `token-compare.js` measures the savings. Start the site with all layers up to this chapter:

```
cd demos/nordlys-cabins
npm start -- --upto=5
```

Listing 5.3 is the whole negotiation logic. It parses the `Accept` header into media ranges with their quality values and compares Markdown with HTML.

**Listing 5.3** Choosing Markdown only when the client asks for it (`layers/05-agent-content/negotiate.js`)

```js
// Content negotiation for Markdown (RFC 9110, section 12.5.1).
// A client gets Markdown only when it asks for text/markdown explicitly and
// ranks it at least as high as HTML. Browsers never do, so they keep HTML.

/** Parse an Accept header into [{ type, q }]. */
export function parseAccept(header = '') {
  return header
    .split(',')
    .map((part) => {
      const [range, ...params] = part.trim().split(';').map((s) => s.trim());
      const q = params.find((p) => p.toLowerCase().startsWith('q='));
      return { type: range.toLowerCase(), q: q ? Number(q.slice(2)) : 1 };
    })
    .filter((r) => r.type && !Number.isNaN(r.q));
}

/** The q value the header gives a media type, using the most specific range. */
function qualityOf(ranges, type, { wildcards = true } = {}) {
  const [major] = type.split('/');
  const exact = ranges.find((r) => r.type === type);
  if (exact) return exact.q;
  if (!wildcards) return 0;
  const partial = ranges.find((r) => r.type === `${major}/*`);
  if (partial) return partial.q;
  const any = ranges.find((r) => r.type === '*/*');
  return any ? any.q : 0;
}

export function prefersMarkdown(accept) {
  const ranges = parseAccept(accept);
  const md = qualityOf(ranges, 'text/markdown', { wildcards: false });
  const html = qualityOf(ranges, 'text/html');
  return md > 0 && md >= html;
}
```

Notice the asymmetry in `prefersMarkdown()`. For Markdown, wildcards don't count (`{ wildcards: false }`), so `*/*` never selects it. For HTML, they do, so a browser's `*/*;q=0.8` still counts as an HTML preference. That one detail is what keeps browsers safe.

A middleware runs after the core has rendered the page. If the page has a Markdown view and the client prefers Markdown, it replaces the HTML response with Markdown rendered from the same page object. Otherwise it adds `Vary: Accept` and the Link header to the HTML. A separate handler serves `.md` URLs by asking the app for the same page with `Accept: text/markdown` and no cookies, and returns a real 404 when the answer isn't Markdown, so `/account/bookings.md` can never return anything.

Two design choices are worth copying. First, the Markdown is rendered from data with a small template per page kind, not converted from HTML. It never contains navigation or a cookie banner, it can state as one line what the HTML spreads over a definition list and a sentence ("Sunday to Thursday nights: NOK 2,200 per night"), and it is testable against the store. Second, it is written for a reader with no screen: one H1 and a real heading hierarchy, facts as short labelled lines, units and periods in every price, ISO dates, absolute URLs, and a line that says what the agent can do next ("Book (a person confirms in the form): …"). For caches, the safe setup is a cache key with one bit, "Markdown or not", computed with the same rule as the negotiation, and the HTML and Markdown of one URL must never share an `ETag`. The layer's tests pin the negotiation down with real header values, check that every `.md` URL returns exactly the negotiated Markdown, and compare its prices and capacity with the store.

> **Try it yourself.** Three experiments with the running demo. First, compare `curl -H "Accept: text/markdown" http://localhost:3000/faq` with `curl http://localhost:3000/faq.md`. They should be identical. Second, send `curl -H "Accept: text/html, text/markdown;q=0.5" http://localhost:3000/` and confirm that you get HTML. Third, add a seventh cabin to a scratch copy of `data/cabins.json` and watch it appear in the home page, the Markdown, the JSON-LD and llms.txt, with no other change.

## Measuring the savings

The layer includes a small script that requests four pages in both formats and counts tokens with `gpt-tokenizer` (version 4.1.0, `o200k_base` encoding) if it is installed, or estimates four characters per token if not.[^ch05-25]

```
npm install --no-save gpt-tokenizer@4.1.0
node layers/05-agent-content/token-compare.js
```

Table 5.2 is the output from 2 November 2026.

**Table 5.2** HTML and Markdown sizes of four Nordlys pages, in tokens (o200k_base)

| Page | HTML | Markdown | Saved |
| --- | --- | --- | --- |
| `/` | 1,578 | 743 | 53% |
| `/cabins/fjellro` | 2,543 | 486 | 81% |
| `/guide/northern-lights-from-a-cabin` | 1,312 | 427 | 67% |
| `/faq` | 1,866 | 409 | 78% |

The home page saves the least because its Markdown lists all six cabins and all five articles, while the HTML shows three of each. And the absolute numbers are small because Nordlys is small and its HTML is lean. The ratio is what transfers to your site, and on most production sites, with scripts, menus and tracking, the HTML side will be several times larger.

## llms.txt

Now for the most debated file in this book. llms.txt is a proposal by Jeremy Howard, first published on 3 September 2024, with version 2 published on 10 August 2026.[^ch05-26] It is a Markdown file at `/llms.txt` that works as a curated table of contents of your site for language models: an H1 with the name of the site (the only required section), a blockquote summary, optional details and H2 sections of links in the form `[name](url): notes`. Version 2 lets a file live under any path and cover the URLs below it, accepts both `page.md` and `page.html.md`, and adds discovery through `rel="alternate"; type="text/markdown"` and `rel="describedby"` links.[^ch05-27] `llms-full.txt`, the whole site in one file, is a community convention, not part of the proposal.

Who reads it? Let's collect the facts. Google Search doesn't: "You don't need to create new machine readable files, AI text files, markup, or Markdown to appear in Google Search (including its generative AI capabilities), as Google Search itself doesn't use them."[^ch05-28] Google Chrome checks it, with an `llms-txt` audit in Lighthouse's Agentic Browsing category.[^ch05-29] Ahrefs analysed logs of 137,000 sites in June 2026 and found that 28% publish llms.txt and that 97% of those files received zero requests in the period.[^ch05-30] Rankability found a file on 9.3% of the top 1,000 domains (18 September 2026), measured by an SEO vendor with its own method.[^ch05-31] And OpenAI, Anthropic and Gemini publish llms.txt files for their developer documentation,[^ch05-26] because coding agents and documentation tools are where the format is used most.

Honestly, I think both camps overstate their case. llms.txt is not a ranking factor, and nobody should promise traffic from it. It's also not useless. It costs an hour, coding agents use files like it, and it gives any agent a short, curated map of your site in the format it reads best. Publish one as cheap hygiene, never dump the whole sitemap into it, and don't expect anything from Google Search. A large site can publish a short root file that links to section files curated by the teams that own them.

The Lighthouse 13.6.0 audit fetches `/llms.txt` at the origin root only. A 4xx response makes it "not applicable", a 5xx or 429 fails it, and a file that loads passes when it has an H1, at least one Markdown link and at least 50 characters.[^ch05-32] So a file with an H1 and a summary but no links, which the proposal allows, fails the audit. Include links. They are the whole point of a table of contents.

The Nordlys layer generates `/llms.txt` from the store, so it can never list a cabin or an article that doesn't exist (Listing 5.4).

**Listing 5.4** The Nordlys llms.txt (`GET /llms.txt`, output, excerpt)

```markdown
# Nordlys Cabins

> Six holiday cabins in Norway that you can book directly, from a rorbu in Lofoten to a forest hut by lake Femunden. Prices are in NOK, and cancellation is free up to 14 days before check-in. (Nordlys Cabins is a fictional demo site.)

Every public page is also available as Markdown: request it with `Accept: text/markdown`, or add `.md` to the path. A booking is always confirmed by a person in the booking form.

## Cabins

- [Fjellro](https://nordlys.example/cabins/fjellro.md): Rondane, sleeps 6, from NOK 2,200 per night.
- [Lyngen Lysthus](https://nordlys.example/cabins/lyngen-lysthus.md): Lyngen, sleeps 4, from NOK 3,400 per night.
...

## Booking and policies

- [Frequently asked questions](https://nordlys.example/faq.md): check-in and check-out times, what is included, cancellation, pets.
...

## Optional

- [Sitemap](https://nordlys.example/sitemap.xml): every public page with real modification dates for articles.
- [Guide feed](https://nordlys.example/guide/feed.xml): new articles as an Atom feed.
- [robots.txt](https://nordlys.example/robots.txt): crawler rules and content signals.
```

The summary says what the site is in one sentence, including that it's a demo, so no model mistakes it for a real business. Every cabin line repeats the three facts that matter most for choosing (region, capacity, price), so an agent can shortlist without opening six pages, and all links are absolute `.md` URLs. A test checks the file against the Lighthouse rules and requests every link in it, expecting a 200. A table of contents with broken links is worse than none, and this is the cheapest test you will ever write against that.

## Sitemaps, feeds and Link headers

llms.txt is a curated map. Sitemaps and feeds are complete maps. The sitemap from Chapter 4 lists every public page and sets `lastmod` only where Nordlys knows a real date, because Google uses it only when it is accurate and ignores `priority` and `changefreq`.[^ch05-33] An agent that keeps a local copy of your content can use a true `lastmod` to refresh only what changed. A feed answers "what's new?" without crawling, so the layer publishes an Atom feed of the guide at `/guide/feed.xml`.

The last piece connects everything. Web Linking (RFC 8288) defines the HTTP `Link` header,[^ch05-34] and it works without parsing HTML at all: a `HEAD` request to any page tells a client where the Markdown version and the llms.txt are. After this chapter, every public Nordlys page sends a header like this one:

```
Link: <https://nordlys.example/cabins/fjellro.md>; rel="alternate"; type="text/markdown",
      <https://nordlys.example/llms.txt>; rel="describedby"
Vary: Accept
```

Both relation types are registered in the IANA link relations registry.[^ch05-35] Chapter 8 appends an `api-catalog` link to the same header, and announcing what a site offers is its topic.

## Who actually reads it on your site

Everything in this chapter is cheap to build, and the question "is anyone using it?" is cheap to answer. You only need to log two things that most access logs drop by default: the `Accept` header of each request, and whether the request was for a `.md` URL or `/llms.txt`. Group them by user agent, and after a few weeks you know which agents ask for Markdown, how often they read llms.txt and whether the numbers grow.

Expect small numbers at first. Most llms.txt files in Ahrefs' sample received no requests at all, and Radar shows Markdown as less than 0.1% of what AI bots receive. That's a reason to measure, not a reason to stop. These formats cost almost nothing once they are generated from data, and the agents that use them get a much better result. Chapter 12 builds the log analysis that includes these signals.

## What the graders see

Here is a slightly awkward fact for a book about agent readiness: neither grader gives any points for structured data. None of isitagentready's 23 documented checks reads JSON-LD,[^ch05-36] and no audit in Lighthouse's Agentic Browsing category reads it either. Graders measure what is easy to measure and new, and whether markup is true to the page needs a test like ours. Markdown is a different story (Table 5.3).

isitagentready's Level 3, "Agent-Readable", is "Level 2 + markdown content negotiation", and the check passes when "requesting the homepage with `Accept: text/markdown` returns a response with `Content-Type: text/markdown`".[^ch05-23] The same layer makes `linkHeaders` pass. As in Chapter 4, the real scanner can't reach `localhost`, so the layer's audit mirrors the documented pass rules. In Lighthouse 13.6.0, the `llms-txt` audit went from "not applicable" to pass, and the category score was 100 both times, because a not-applicable audit is left out of the score.

**Table 5.3** The graders after this chapter (Nordlys, November 2026)

| Grader | Check | Before | After |
| --- | --- | --- | --- |
| isitagentready | `markdownNegotiation` | fail | pass |
| isitagentready | `linkHeaders` | fail | pass |
| isitagentready | Level | 2, Bot-Aware | 3, Agent-Readable |
| Lighthouse 13.6.0 Agentic Browsing | `llms-txt` | not applicable | pass |
| Lighthouse 13.6.0 Agentic Browsing | Category score | 100 | 100 |

Please don't read the level as a measure of how readable the site has become. The level moved because of one response header on one URL. The useful work of this chapter is everything around that header: Markdown on every public page, the same facts as the HTML, `Vary` for caches, an honest content signal, an llms.txt whose links all work, and tests that keep all of it true.

## Summary

- Structured data is a typed source of truth about your business. Google uses it, Markdown converters keep it, and every later layer reuses the modelling, but no vendor documents that browsing agents read JSON-LD, and Google's AI features need no special markup.
- Model what the business really is: a `VacationRental` containing an `Accommodation`, an `Offer` with `makesOffer` and price specifications per unit, real reviews and a `ReserveAction` that points at a working deep link.
- Mark up only what is visible, and generate the markup from the same data as the page. Check it in CI at three levels: syntax, vocabulary against the real schema.org file, and parity with the page.
- HTML is expensive for agents: Radar shows AI bots receive HTML 73.2% of the time and Markdown under 0.1%, while a Markdown version is at the median 7.9% of the size. On Nordlys, Markdown saved 53% to 81% of tokens.
- Serve Markdown only on an explicit `Accept: text/markdown`, with `Vary: Accept` on both versions, a canonical link, the same facts, public pages only and your own `Content-Signal` header.
- llms.txt is cheap hygiene, not a ranking factor. Google Search doesn't use it, Lighthouse checks it, and most files get few requests. Generate it from data and test every link.
- Sitemaps with honest `lastmod`, a feed and Link headers complete the map. Log the `Accept` header and `.md` and llms.txt requests to see who actually reads it.
- Markdown negotiation moves Nordlys from Level 2 to Level 3. Structured data moves no grader at all.

[^ch05-1]: "Schema.org Version 30.1," Schema.org, https://schema.org/version/latest (published 16 September 2026, retrieved November 2026).
[^ch05-2]: "Introduction to structured data markup in Google Search," Google Search Central, https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data (retrieved November 2026).
[^ch05-3]: "Markdown for Agents," Cloudflare Docs, https://developers.cloudflare.com/fundamentals/reference/markdown-for-agents/ (retrieved November 2026).
[^ch05-4]: "VacationRental," Schema.org, https://schema.org/VacationRental. Usage bands for LodgingBusiness, Accommodation, ReserveAction and LodgingReservation are on their term pages (retrieved November 2026).
[^ch05-5]: "AI optimization guide," Google Search Central, https://developers.google.com/search/docs/fundamentals/ai-optimization-guide (last updated 10 July 2026, retrieved November 2026).
[^ch05-6]: "Introducing NLWeb: Bringing conversational interfaces directly to the web," Microsoft Source, 19 May 2025, https://news.microsoft.com/source/features/company-news/introducing-nlweb-bringing-conversational-interfaces-directly-to-the-web/ (retrieved November 2026).
[^ch05-7]: "Product feed specification," OpenAI for developers, https://developers.openai.com/commerce/specs/file-upload/products (retrieved 5 November 2026).
[^ch05-8]: "Latest Google Search documentation updates," Google Search Central, https://developers.google.com/search/updates (entries of 12 June 2025, 9 September 2025, November 2025 and 8 May 2026, retrieved November 2026).
[^ch05-9]: "Vacation rental (VacationRental) structured data," Google Search Central, https://developers.google.com/search/docs/appearance/structured-data/vacation-rental (updated 8 September 2026, retrieved November 2026).
[^ch05-10]: "makesOffer," Schema.org, https://schema.org/makesOffer, and "offers," https://schema.org/offers (retrieved November 2026).
[^ch05-11]: "General structured data guidelines," Google Search Central, https://developers.google.com/search/docs/appearance/structured-data/sd-policies (retrieved November 2026).
[^ch05-12]: Schema.org term pages: https://schema.org/LodgingBusiness, https://schema.org/Accommodation and https://schema.org/ReserveAction (retrieved November 2026).
[^ch05-13]: "AI features and your website," Google Search Central, https://developers.google.com/search/docs/appearance/ai-features (retrieved November 2026).
[^ch05-14]: "jsonld," npm, https://www.npmjs.com/package/jsonld (version 9.0.0, retrieved November 2026).
[^ch05-15]: The vocabulary file is https://schema.org/version/latest/schemaorg-current-https.jsonld (1.5 MB on 2 November 2026, retrieved November 2026).
[^ch05-16]: Schema Markup Validator, https://validator.schema.org/, and Rich Results Test, https://search.google.com/test/rich-results (both retrieved November 2026).
[^ch05-17]: "Build and submit a sitemap," Google Search Central, https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap (retrieved November 2026).
[^ch05-18]: "AI Insights," Cloudflare Radar, https://radar.cloudflare.com/ai-insights (content types served to AI bots and Markdown for Agents response sizes, 7 days to 2 November 2026, retrieved November 2026).
[^ch05-19]: "Introducing Markdown for Agents," The Cloudflare Blog, 12 February 2026, https://blog.cloudflare.com/markdown-for-agents/ (response headers checked 2 November 2026, retrieved November 2026).
[^ch05-20]: "The state of AI agent content negotiation," Checkly blog, February 2026, https://www.checklyhq.com/blog/state-of-ai-agent-content-negotation/ (retrieved November 2026).
[^ch05-21]: "Markdown for Agents," Cloudflare Docs, https://developers.cloudflare.com/fundamentals/reference/markdown-for-agents/ (updated 9 October 2026, retrieved November 2026).
[^ch05-22]: "Adoption of AI agent standards," Cloudflare Radar, https://radar.cloudflare.com/ai-insights#adoption-of-ai-agent-standards (115,468 domains scanned, data dated 2 November 2026, retrieved November 2026).
[^ch05-23]: "isitagentready.com full reference," Cloudflare, https://isitagentready.com/llms-full.txt (checks markdownNegotiation and linkHeaders, level definitions, retrieved November 2026).
[^ch05-24]: R. Fielding, M. Nottingham, J. Reschke, "RFC 9110: HTTP Semantics," section 12, Content Negotiation, June 2022, https://www.rfc-editor.org/rfc/rfc9110.html#name-content-negotiation (retrieved November 2026).
[^ch05-25]: "gpt-tokenizer," npm, https://www.npmjs.com/package/gpt-tokenizer (version 4.1.0, retrieved November 2026).
[^ch05-26]: J. Howard, "The /llms.txt file," version 2, https://llmstxt.org/ (modified 10 August 2026, retrieved November 2026).
[^ch05-27]: "Changes in version 2," llmstxt.org, https://llmstxt.org/changes.html (retrieved November 2026).
[^ch05-28]: "AI optimization guide," Google Search Central, https://developers.google.com/search/docs/fundamentals/ai-optimization-guide (last updated 10 July 2026, retrieved November 2026).
[^ch05-29]: "Google's llms.txt guidance depends on which product you ask," Search Engine Journal, 20 May 2026, https://www.searchenginejournal.com/googles-llms-txt-guidance-depends-on-which-product-you-ask/575431/ (retrieved November 2026).
[^ch05-30]: "llms.txt study," Ahrefs blog, 15 June 2026, https://ahrefs.com/blog/llmstxt-study/ (retrieved November 2026).
[^ch05-31]: "llms.txt adoption," Rankability, checked 18 September 2026, https://www.rankability.com/blog/llms-txt-adoption/, and "LLMs.txt," SE Ranking blog, https://seranking.com/blog/llms-txt/ (both retrieved November 2026).
[^ch05-32]: Lighthouse 13.6.0, `core/audits/agentic/llms-txt.js`, https://github.com/GoogleChrome/lighthouse/blob/main/core/audits/agentic/llms-txt.js, and "llms.txt," Chrome for Developers, https://developer.chrome.com/docs/lighthouse/agentic-browsing/llms-txt (both retrieved November 2026).
[^ch05-33]: "Build and submit a sitemap," Google Search Central, https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap (retrieved November 2026).
[^ch05-34]: M. Nottingham, "RFC 8288: Web Linking," October 2017, https://www.rfc-editor.org/rfc/rfc8288.html (retrieved November 2026).
[^ch05-35]: "Link Relations," IANA, https://www.iana.org/assignments/link-relations/link-relations.xhtml (checked 2 November 2026, retrieved November 2026).
[^ch05-36]: "isitagentready.com full reference," Cloudflare, https://isitagentready.com/llms-full.txt (retrieved November 2026).
