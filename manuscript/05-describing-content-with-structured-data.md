# Chapter 5: Describing your content with structured data

This chapter covers

- What structured data is, and who actually reads it in November 2026
- Modelling a booking site with schema.org: VacationRental, Accommodation, Offer, Review, ReserveAction and the pages around them
- Generating JSON-LD from the same data as the page, and keeping it true to the page
- Checking markup in CI against the real schema.org vocabulary
- What Google says about structured data and AI features, and which rich results are gone
- NLWeb, and the idea of schema.org as a question API for agents

Chapter 4 decided who may come in. This chapter is about what they find when they do.

Look at the Fjellro page of Nordlys Cabins with an agent's eyes. Somewhere in the HTML it says "From NOK 2,200 per night", a bit further down "Friday and Saturday nights cost NOK 2,600", and then "Cleaning, bed linen and towels: NOK 900 per stay". A person reads that in two seconds and knows what a weekend costs. A program has to guess. Which number is the price? Per night or per stay? Is "2,200" two thousand two hundred or two point two? And is "Fjellro" a cabin, a company or a mountain?

Structured data is the site saying it explicitly: this is a vacation rental, it sleeps six, a weekday night costs 2200 Norwegian kroner, a weekend night 2600, and here is the URL where you book it. It is one of the oldest "machine-readable" layers of the web, much older than the current wave of agents, and for exactly that reason it is surrounded by myths. Some say structured data is the secret to appearing in AI answers. Others say it's dead because Google dropped half of its rich results. Both are wrong, and we will look at the evidence for each claim.

By the end of this chapter, every content page of Nordlys Cabins carries a JSON-LD graph generated from the same data as the visible page, a test checks every type and property against the official schema.org vocabulary, and a tiny NLWeb-style endpoint shows what clean structured data makes possible beyond search.

## Structured data in one page

Structured data is a description of the things a page is about, in a vocabulary that machines agree on. On the web that vocabulary is almost always schema.org, a shared vocabulary started by the major search engines in 2011 and developed in the open on GitHub. As of November 2026 the current release is version 30.1, published on 16 September 2026.[^ch05-1] Recent releases are a good reminder that schema.org is alive and keeps growing: 30.1 added vocabulary for the EU Digital Product Passport, and 30.0 added equivalence annotations to GS1, Dublin Core and Open Graph.[^ch05-2]

There are three ways to put schema.org into a page: microdata and RDFa (attributes woven into the HTML elements) and JSON-LD (a separate JSON document in a `<script type="application/ld+json">` element). Google supports all three and says "all 3 formats are equally fine for Google", but recommends JSON-LD "in most cases" because it is the easiest to implement and maintain.[^ch05-3] JSON-LD is also the format that survives transformations best, which matters for agents. For example, Cloudflare's Markdown for Agents strips almost everything except text when it converts a page to Markdown, but it "preserves any `<script type="application/ld+json">` blocks", appending them to the Markdown as a fenced JSON block.[^ch05-4] We use JSON-LD throughout.

Here is the smallest useful example, the kind of thing you see on millions of pages:

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Nordlys Cabins",
  "url": "https://nordlys.example/"
}
```

`@context` says which vocabulary the words come from, `@type` says what kind of thing this is, and the rest are properties of that type. Types form a hierarchy. A `VacationRental` is a `LodgingBusiness`, which is a `LocalBusiness`, which is both an `Organization` and a `Place`, so a vacation rental can use the properties of all of them.[^ch05-5] That hierarchy is also the source of most mistakes, as we will see when the tests run.

Schema.org term pages now show how widely each type is used, in bands "based on monthly aggregations from Google's web index". `VacationRental`, `LodgingBusiness`, `Accommodation` and `ReserveAction` each sit in the band of 10,000 to 100,000 domains, and `LodgingReservation` in the band of 1,000 to 10,000.[^ch05-5] These are bands rather than exact counts. Still, they show that the types we are about to use are mainstream.

## Who reads your structured data in 2026

This is the question that decides how much effort structured data deserves, so let's answer it with sources rather than hopes. Table 5.1 is what I could verify on 2 November 2026.

**Table 5.1** Who reads schema.org JSON-LD, by evidence (November 2026)

| Consumer | What it does with structured data | Evidence |
| --- | --- | --- |
| Google Search | Uses it to understand pages and to show rich results for supported features | Google's own documentation[^ch05-3] |
| Google's AI features (AI Overviews, AI Mode) | Nothing special: "Structured data isn't required for generative AI search, and there's no special schema.org markup you need to add" | Google's AI optimization guide, updated 10 July 2026[^ch05-6] |
| Microsoft Bing and Copilot | Said to help Microsoft's models understand content | A conference statement by Bing's Fabrice Canel (SMX Munich, March 2025), reported by the SEO press, with no Microsoft documentation page[^ch05-7] |
| Cloudflare Markdown for Agents | Keeps JSON-LD in the Markdown it serves to agents | Cloudflare documentation[^ch05-4] |
| NLWeb | Ingests schema.org and RSS, and answers questions with schema.org objects | Microsoft announcement and the project's API docs[^ch05-8] |
| ChatGPT shopping and agentic commerce | Uses product feeds that merchants upload, not page markup | OpenAI's commerce documentation (seen in a search snippet, page not read in full)[^ch05-9] |
| Browsing agents (Claude in Chrome, Gemini in Chrome, Comet and others) | Unknown | No vendor document says these agents read JSON-LD during a task |

The last row is the honest center of this chapter. It is plausible that a browsing agent which reads the DOM also reads a JSON-LD block in it. An agent that hands raw HTML to a model would include the block, and a model that sees a clean `"price": 2200` will probably use it. But I found no vendor documentation that confirms it, so I treat "agents read your JSON-LD" as plausible and unverified, and so should you.

What does that leave? A lot, actually. Structured data is the one place on your site where the facts about your business (what you sell, what it costs, where it is, how people rated it) live in a typed, unambiguous form. Google uses it today. Pipelines that convert pages to Markdown keep it. Tools like NLWeb are built on it. And every layer this book adds later (the Markdown version in Chapter 6, the API in Chapter 7, MCP tools in Chapter 8, WebMCP in Chapter 9) needs the same facts in a typed form. If you generate structured data from your data, you have already done half of the modelling work for all of them.

### What the markup changes for a machine

To make this concrete, let's follow a simple task through the Nordlys site: "Find a cabin for six people in Norway with a fireplace, and tell me what a weekend costs."

Without structured data, a program has the visible text. It finds "Sleeps 6 guests" in a definition list, "From NOK 2,200 per night" a bit further, and "Friday and Saturday nights cost NOK 2,600" in a paragraph under the features. It finds "Fireplace or wood stove" in a list of tags. A capable model will put these together correctly most of the time. But "most of the time" carries the weight here. It has to infer that "From" means a minimum, that the weekend sentence overrides the nightly rate for two nights, that the cleaning fee is per stay and not per night, and that the "6" in "Sleeps 6 guests" is a maximum. Every inference is a chance to be wrong, and the cost of being wrong is a quote that doesn't match the checkout.

With structured data, the same facts arrive labelled. `occupancy.maxValue` is 6. There are two `UnitPriceSpecification` items with `unitText` "night" and names that say which nights, and one `PriceSpecification` for the stay. The amenity is a `LocationFeatureSpecification` with the value `true`. Nothing needs to be guessed, and the same parsing works for every cabin on the site and, in principle, for every rental on the web that uses the same vocabulary.

That doesn't mean an agent must read the markup. It means that when it does, it gets the answer cheaply and correctly, and when a pipeline converts your page into Markdown for a model (Chapter 6 does exactly that for Nordlys), the labelled facts can travel with the text instead of being lost. Table 5.2 compares where each fact lives.

**Table 5.2** Where an agent finds the facts of one cabin

| Fact | In the visible page | In the JSON-LD |
| --- | --- | --- |
| Kind of place | Implied by the words "cabin" and the photo | `@type` VacationRental, `additionalType` Cabin |
| Capacity | "Sleeps 6 guests" | `containsPlace.occupancy.maxValue` 6 |
| Weekday price | "From NOK 2,200 per night" | `price` 2200, `priceCurrency` NOK, `unitText` night |
| Weekend price | A sentence under the features | A second `UnitPriceSpecification` named "Friday and Saturday nights" |
| Cleaning fee | "NOK 900 per stay" | A `PriceSpecification` named "per stay" |
| Rating | Individual reviews, plus the new average line | `aggregateRating` with `ratingValue` and `reviewCount` |
| How to book | A form further down the page | `potentialAction` ReserveAction with a URL template |

Bottomline: sell structured data inside your team as a machine-readable source of truth that several consumers read, not as "Google stars" and not as an AI ranking trick.

## The rich results that are gone

That framing matters because the "stars" argument has become weaker every year. Google has been retiring rich-result features steadily:

- On 12 June 2025 Google announced it would phase out several structured data features in Search, including course info, estimated salary, ClaimReview, learning video, special announcement and vehicle listing. Documentation for most of them was removed on 9 September 2025.[^ch05-10]
- Practice problem and Dataset (in Google Search) rich results were phased out in November 2025.[^ch05-10]
- FAQ rich results stopped appearing in Google Search on 7 May 2026: "This feature will no longer appear in Google Search starting May 7, 2026."[^ch05-10]

And the one feature that sounds made for Nordlys, vacation rental rich results, is not open to everyone. Google's vacation rental documentation says its instructions "are intended for sites that have already connected with a Google Technical Account Manager and have access to the Hotel Center", and it sets requirements such as at least eight photos per listing and coordinates with five decimal places.[^ch05-11] For a small operator with six cabins, that programme is out of reach, and that's fine.

So a team that added FAQ markup purely for the extra lines in search results can remove it now, right? Not so fast. `FAQPage` is still a valid schema.org type, it still describes the page correctly, and Google's guidelines for markup are about truth, not about which features exist this year. The question is simply whether the markup describes visible content. If it does, it costs nothing to keep. Nordlys keeps its `FAQPage`, and the chapter doesn't promise any star or snippet for it.


## Modelling a booking site

Before writing any code, let's decide what Nordlys actually is in schema.org terms. This is the part that needs product and content people in the room, not only developers, because each choice is a statement about the business.

### Choosing the types

Nordlys sells stays in six cabins. Schema.org offers several candidates:

- `LodgingBusiness` is "a lodging business, such as a motel, hotel, or inn".[^ch05-12] It is correct but generic.
- `Hotel`, `Motel`, `Hostel` and `Resort` are more specific subtypes, and none of them fits a single timber cabin in Rondane.
- `VacationRental` is "a kind of lodging business that focuses on renting single properties for limited time".[^ch05-5] That is exactly Nordlys.
- `Accommodation` is the place itself: "a place that can accommodate human beings, e.g. a hotel room, a camping pitch, or a meeting room".[^ch05-12]

The pattern that Google's partner documentation and schema.org both support is a `VacationRental` (the listing, the "business" you book with) whose `containsPlace` is an `Accommodation` (the physical cabin with its beds and bedrooms). The split looks pedantic at first, but it pays off: the rental has the address, check-in times, offers and reviews, and the accommodation has the occupancy, the bedrooms and the amenities. Google's vacation rental documentation suggests `additionalType` values for the listing (such as `Cabin`, `Chalet` or `Cottage`) and for the accommodation (`EntirePlace`, `PrivateRoom` or `SharedRoom`).[^ch05-11] We use both, even though Nordlys is not in Google's partner programme, because they are clear words that any reader of the markup understands.

The other pages need much less thought. The home page describes the company (`Organization`) and the site (`WebSite`). The cabin list is an `ItemList`. Guide articles are `BlogPosting` items, the FAQ page is a `FAQPage` with `Question` and `Answer` pairs, and the two pages that show a breadcrumb (cabin and article) get a `BreadcrumbList` that matches it.

What about events? A northern lights site could easily have guided tours, and `Event` is a well-supported type. Nordlys has no events, so it has no `Event` markup. That sounds obvious when I say it like this, but "add every type that might be relevant" is a surprisingly common approach, and it produces markup that describes a business that doesn't exist. We mark up what is on the page.

### Prices: Offer and makesOffer

The price is the fact agents care about most, and the one with the most traps. Nordlys has three numbers per cabin: a weekday nightly rate, a weekend nightly rate and a cleaning fee per stay. A single `"price": 2200` would be misleading, because a weekend costs more and every stay adds the fee.

Schema.org's answer is an `Offer` with a list of price specifications. A `UnitPriceSpecification` carries a price per unit (we say `"unitText": "night"`), and a plain `PriceSpecification` carries the cleaning fee. Each one has a `name` that repeats the wording of the page: "Sunday to Thursday nights", "Friday and Saturday nights", "Cleaning, bed linen and towels, per stay".

Which property connects the offer to the rental? Many examples on the web use `offers`, and that's the trap. In schema.org, `offers` belongs to things that are offered (a `Product`, a `Service`, an `Event`, a `CreativeWork` and a few others), not to the business that offers them. A business uses `makesOffer`, whose domain is `Organization` and `Person`.[^ch05-13] Because `VacationRental` inherits from `Organization`, `makesOffer` is the right property. A validator that checks domains (we build one later in this chapter) catches this mistake. A quick look at a single example on the web does not.

### Reviews and ratings

Nordlys shows real guest reviews on each cabin page, each with a rating out of five. Those become `Review` items with a `reviewRating`, and a computed `AggregateRating` sits on the rental.

There are two rules here, and both come from one principle. First, only real reviews go into the markup. Google's structured data guidelines say "Don't mark up irrelevant or misleading content, such as fake reviews".[^ch05-14] Second, the aggregate must be something the visitor can see. The original Nordlys page shows individual reviews but no average, so the layer adds one visible line to the page ("Average guest rating 5 out of 5 from 1 review") before it puts `aggregateRating` into the markup. More on that rule in a moment.

### The action: ReserveAction

The last part of the cabin graph is the most interesting one for this book. Schema.org has a whole family of `Action` types, and `potentialAction` lets you say "here is something you can do with this thing". For a rental, the natural action is `ReserveAction`, which "reserves concrete objects (e.g. a table, a hotel) towards a time slot / spatial allocation".[^ch05-12] Its `target` is an `EntryPoint` with a `urlTemplate`:

```
https://nordlys.example/book/fjellro?checkIn={checkIn}&checkOut={checkOut}&guests={guests}
```

And the `result` of the action is a `LodgingReservation`. That type is for actual reservations, "e.g. in confirmation emails or HTML pages with individual confirmations of reservations".[^ch05-15] We don't mark up a listing as a reservation. We only say that reserving produces one.

The URL template is not decoration. The Nordlys booking form really accepts these query parameters and fills in the fields, so the template is a working deep link (a test proves it). An agent that understands it can take a person straight to a prefilled form with the right dates, where the person reviews and confirms.

Now the honest part. I found no consumer in 2026 (not Google, not OpenAI, not Anthropic) that documents reading `ReserveAction` to start a booking. So treat this markup as a clear, cheap statement of intent with no proven consumer, and treat its value beyond semantics as unverified. The real action layers of this book are elsewhere: the WebMCP tools of Chapter 9 and Chapter 10, the MCP server of Chapter 8 and the API of Chapter 7. What `ReserveAction` gives you is a bridge concept. It is the first place where your site says, in a machine-readable way, "this is what you can do here", and every later chapter says the same thing with a stronger contract.

Figure 5.1 shows the whole cabin graph.

![Figure 5.1 The JSON-LD graph of one Nordlys cabin. The VacationRental is the listing you book with, the Accommodation inside it is the physical cabin, and the Offer, Reviews and ReserveAction hang off the listing.](images/figure-5-1.png)

**Figure 5.1** The JSON-LD graph of one Nordlys cabin. The VacationRental is the listing you book with, the Accommodation inside it is the physical cabin, and the Offer, Reviews and ReserveAction hang off the listing.

Table 5.3 sums up the decisions for the whole site.

**Table 5.3** Schema.org types on Nordlys Cabins, and why

| Page | Types | Why this and not something else |
| --- | --- | --- |
| Home | `Organization`, `WebSite` | Describes the company and the site once, other nodes point at the organization with `@id` |
| Cabin list | `ItemList` of `ListItem` | The page is a list of links, nothing more |
| Cabin | `VacationRental` with `containsPlace` `Accommodation`, `makesOffer` `Offer`, `Review`, `AggregateRating`, `ReserveAction`, plus `BreadcrumbList` | A single rentable property, not a hotel. `makesOffer` because the rental is an organization |
| Guide article | `BlogPosting`, `BreadcrumbList` | Dated articles with a visible byline and breadcrumb |
| FAQ | `FAQPage` with `Question` and `Answer` | Still a valid description of the page, even though Google no longer shows FAQ rich results |
| Booking form, booking, account | none | Private or transactional pages, kept out of indexes since Chapter 4 |

### Common modelling mistakes

Before we write code, here are the mistakes I check for first when I review someone's markup. Most of them are invisible in the page and silent in the browser, which is why they survive for years.

- **`offers` on a business.** As described above, a business uses `makesOffer`. `offers` belongs to products, services, events and creative works.
- **Prices as formatted strings.** `"price": "NOK 2,200"` mixes the currency into the value and uses a thousands separator that some parsers read as a decimal point. Use a number (or a plain numeric string) and a separate `priceCurrency` with an ISO 4217 code.
- **Relative URLs.** `"url": "/cabins/fjellro"` is ambiguous once the JSON-LD is copied out of the page (into Markdown, a feed or an index). Always use absolute URLs.
- **Reservations on listings.** `LodgingReservation` describes a reservation that exists, with a guest and dates. It belongs on a confirmation page or in a confirmation email, never on a listing.
- **Two blocks that disagree.** A CMS plugin adds one `Organization`, a theme adds another with a different name or logo, and a developer adds a third by hand. Consumers then have to pick one. Keep one generator per type, and link nodes with `@id` instead of repeating them.
- **Search results marked up as products.** A list page is a list. Mark up the items on their own pages, and give the list an `ItemList` at most.
- **Invented completeness.** Filling every recommended property with placeholder values ("Not specified", 0, empty strings) to satisfy a validator. A missing property is honest. A fake value is not.

The Nordlys demo itself shows the "two blocks" problem in a harmless form. When the demo's example layer (the one that exercises every hook of the layer API) is switched on, cabin pages carry its small demonstration JSON-LD block next to ours. That's why the layer's audit doesn't assume that the first block on the page is the cabin graph. It looks for the `VacationRental` node in all blocks.

## True to the page

There is one rule that matters more than any type choice, and Google states it in plain words: "Don't mark up content that is not visible to readers of the page. For example, if the JSON-LD markup describes a performer, the HTML body must describe that same performer."[^ch05-14] Google's page about AI features repeats the idea that markup should match the visible text.[^ch05-16]

Honestly, I would follow this rule even if no search engine enforced it, for three reasons.

The first is trust. Structured data is a claim your site makes about itself. If the markup says one thing and the page says another, every consumer has to decide which one to believe, and the ones that notice will believe neither.

The second is maintenance. Markup that is written separately from the page drifts. Someone changes a price in the CMS, the page updates, and a hand-written JSON-LD block keeps the old price for months. An agent that reads the block then quotes the wrong price to a guest, and the guest arrives at checkout with the wrong expectation.

The third is security, and it matters more in the agent era than before. A JSON-LD block is text that a model may read. Text that only machines see is exactly the channel that prompt injection uses, whether you put it there or an attacker does. If your rule is "nothing in the markup that isn't on the page", a reviewer can check the markup by looking at the page, and hidden instructions have nowhere to hide. Chapter 16 comes back to injection through content in detail.

The practical consequence for Nordlys was small but instructive. Two facts in the cabin graph were not visible on the original page: the average rating and the coordinates. I had two options: drop them from the markup, or show them on the page. Both are fine. I chose to show them, because they are useful to people too, so the layer adds one line at the end of every cabin page: "Average guest rating 4.5 out of 5 from 2 reviews. Location 69.58° N, 20.21° E." Now every fact in the graph is a fact a visitor can see, and a test checks that it stays that way.

The deeper fix is architectural: generate the markup from the same data as the page. Figure 5.2 shows the shape that this book follows from here on.

![Figure 5.2 One data source, many representations. The page, the JSON-LD, the /ask endpoint in this chapter and the Markdown, API and tools of later chapters all read the same records, and parity tests check that they agree.](images/figure-5-2.png)

**Figure 5.2** One data source, many representations. The page, the JSON-LD, the /ask endpoint in this chapter and the Markdown, API and tools of later chapters all read the same records, and parity tests check that they agree.

If the price in the JSON-LD and the price on the page come from the same field of the same record, they can't drift apart. If they come from two places, they will, sooner or later. In simple words: don't write structured data, generate it.


## Hands-on: the structured-data layer

> **Hands-on.** This section builds layer `05-structured-data` in the Nordlys demo. If you don't write code, read the first paragraph of each listing's explanation and skip to "Checking markup in CI". You will not miss any decision.

The layer lives in `demos/nordlys-cabins/layers/05-structured-data/` and has five files: `graph.js` builds the JSON-LD, `index.js` registers it with the site, `ask.js` is the NLWeb-style endpoint, `schema-check.js` is the vocabulary check, and `vocab-subset.js` regenerates the slice of the schema.org vocabulary the check uses. To run the site up to this chapter:

```
cd demos/nordlys-cabins
npm start -- --upto=5
```

Then open `http://localhost:3000/cabins/fjellro` and view the page source. In the `<head>` you will find one `<script type="application/ld+json">` element.

### Building the graph from the store

Listing 5.1 is the function that builds the graph of one cabin. Notice that it receives the same `cabin` record that the page template renders, and that every value comes from that record or from the reviews the page also shows. There is not a single literal fact about a cabin in this file.

**Listing 5.1** The cabin graph, built from the same data as the page (`layers/05-structured-data/graph.js`, excerpt)

```js
/** One cabin: a VacationRental that contains one Accommodation. */
export function cabinGraph(page, store, cabin) {
  const features = store.features();
  const reviews = store.reviewsFor(cabin.slug);
  const stars = rating(reviews);
  const rental = {
    '@type': 'VacationRental',
    '@id': id(page, `/cabins/${cabin.slug}`, 'rental'),
    additionalType: 'Cabin',
    identifier: cabin.slug,
    name: cabin.name,
    description: cabin.summary,
    url: abs(page, `/cabins/${cabin.slug}`),
    image: abs(page, cabin.image),
    address: { '@type': 'PostalAddress', addressRegion: cabin.county, addressCountry: 'NO' },
    geo: { '@type': 'GeoCoordinates', latitude: cabin.geo.latitude, longitude: cabin.geo.longitude },
    checkinTime: cabin.checkInTime,
    checkoutTime: cabin.checkOutTime,
    containsPlace: {
      '@type': 'Accommodation',
      additionalType: 'EntirePlace',
      occupancy: { '@type': 'QuantitativeValue', maxValue: cabin.maxGuests },
      numberOfBedrooms: cabin.bedrooms,
      bed: cabin.beds,
      amenityFeature: cabin.features.map((f) => ({ '@type': 'LocationFeatureSpecification', name: features[f] ?? f, value: true })),
    },
    makesOffer: {
      '@type': 'Offer',
      url: abs(page, `/book/${cabin.slug}`),
      priceSpecification: [
        { '@type': 'UnitPriceSpecification', name: 'Sunday to Thursday nights', price: cabin.nightlyRate, priceCurrency: cabin.currency, unitText: 'night' },
        { '@type': 'UnitPriceSpecification', name: 'Friday and Saturday nights', price: cabin.weekendRate, priceCurrency: cabin.currency, unitText: 'night' },
        { '@type': 'PriceSpecification', name: 'Cleaning, bed linen and towels, per stay', price: cabin.cleaningFee, priceCurrency: cabin.currency },
      ],
    },
    potentialAction: {
      '@type': 'ReserveAction',
      target: {
        '@type': 'EntryPoint',
        urlTemplate: `${abs(page, `/book/${cabin.slug}`)}?checkIn={checkIn}&checkOut={checkOut}&guests={guests}`,
        actionPlatform: ['https://schema.org/DesktopWebPlatform', 'https://schema.org/MobileWebPlatform'],
      },
      result: { '@type': 'LodgingReservation' },
    },
    parentOrganization: { '@id': id(page, '/', 'organization') },
  };
  if (stars) {
    rental.aggregateRating = { '@type': 'AggregateRating', ...stars, bestRating: 5, worstRating: 1 };
    rental.review = reviews.map((r) => ({
      '@type': 'Review',
      author: { '@type': 'Person', name: r.author },
      datePublished: r.date,
      reviewBody: r.text,
      reviewRating: { '@type': 'Rating', ratingValue: r.rating, bestRating: 5, worstRating: 1 },
    }));
  }
  const crumbs = {
    '@type': 'BreadcrumbList',
    itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Cabins', item: abs(page, '/cabins') },
      { '@type': 'ListItem', position: 2, name: cabin.name },
    ],
  };
  return { '@context': SCHEMA, '@graph': [rental, crumbs] };
}
```

A few details are worth a second look:

- Every main node has an `@id`, a URL with a fragment such as `https://nordlys.example/cabins/fjellro#rental`. Other nodes can then point at it instead of repeating it. The rental says its `parentOrganization` is `{"@id": "https://nordlys.example/#organization"}`, which is the organization described once on the home page.
- All URLs are absolute and built from the page URL, which the demo derives from its configured public origin. That matters behind proxies and on preview deployments, where the host the server sees is not the host the world sees.
- Prices are numbers, not strings like "NOK 2,200". Formatting is the page's job. The markup carries the value and the currency separately.
- The aggregate rating is computed only when there are reviews. A cabin with no reviews gets no rating at all, instead of a "0 out of 5" that would be both wrong and harmful.

### Registering the graph

Listing 5.2 shows how the layer attaches a graph to each page kind and adds the visible line for the rating and the location.

**Listing 5.2** One graph per page kind, and one visible line (`layers/05-structured-data/index.js`, excerpt)

```js
    // 1. One JSON-LD graph per page kind, injected into <head> by the core.
    //    The head hook writes <script type="application/ld+json">, a data block
    //    the CSP does not treat as script, with "<" escaped.
    ctx.head((page) => ({ jsonLd: homeGraph(page) }), { kinds: 'home' });
    ctx.head((page) => ({ jsonLd: cabinListGraph(page, page.data.results ?? store.cabins()) }), { kinds: 'cabin-list' });
    ctx.head((page) => (page.data.cabin ? { jsonLd: cabinGraph(page, store, page.data.cabin) } : null), { kinds: 'cabin' });
    ctx.head((page) => (page.data.article ? { jsonLd: articleGraph(page, page.data.article) } : null), { kinds: 'article' });
    ctx.head((page) => ({ jsonLd: faqGraph(page, store.faq()) }), { kinds: 'faq' });

    // 2. Markup must match the page: show what the markup says about rating and location.
    ctx.slot('cabin-detail-end', (page) => {
      const cabin = page.data.cabin;
      const stars = rating(store.reviewsFor(cabin.slug));
      return html`<p class="cabin-meta">${stars ? `Average guest rating ${stars.ratingValue} out of 5 from ${stars.reviewCount} ${stars.reviewCount === 1 ? 'review' : 'reviews'}. ` : ''}Location ${cabin.geo.latitude}° N, ${cabin.geo.longitude}° E.</p>`;
    });
```

`ctx.head()` is the demo's hook for adding things to `<head>`. When a hook returns `{ jsonLd }`, the core writes a `<script type="application/ld+json">` element and escapes `<` inside the JSON, so a review text that contains `</script>` can't break out of the block. The Nordlys Content Security Policy blocks inline scripts, and that's fine, because a JSON-LD block is a data block, not a script. The browser never executes it.

Let's have a look at what the cabin page now carries. Listing 5.3 is an excerpt of the real output for Fjellro (the full graph also has the description, the image, the amenities, the three price specifications, the review and the breadcrumb).

**Listing 5.3** The start of the JSON-LD on `/cabins/fjellro` (output, excerpt)

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

If you compare this with the Google vacation rental example, you will notice small differences. Google's partner format puts `latitude` and `longitude` directly on the rental and describes beds with a `BedDetails` type, and it asks for at least five decimals in the coordinates.[^ch05-11] Nordlys uses plain schema.org (`geo` with `GeoCoordinates`, a text `bed`) because it's not in the partner programme, and its demo data has two decimals. If you are a partner, follow Google's page to the letter. If you aren't, plain schema.org is the more portable choice.

## Checking markup in CI

Structured data has an unpleasant property: when it's wrong, nothing breaks. The page renders, the tests that click through the booking flow pass, and the mistake sits there until somebody opens a validator, which may be never. So let's make the build check it, at three levels. Figure 5.3 shows them.

![Figure 5.3 Three levels of checking. Syntax (does it parse and expand?), vocabulary (does every type and property exist, and does each property belong to its type?) and parity (does the markup say what the page says?).](images/figure-5-3.png)

**Figure 5.3** Three levels of checking. Syntax (does it parse and expand?), vocabulary (does every type and property exist, and does each property belong to its type?) and parity (does the markup say what the page says?).

### Level 1: syntax

The first level is cheap. The test fetches every content page, extracts the `ld+json` blocks and parses them with `JSON.parse`. Then it expands each block with the `jsonld` package (version 9.0.0, the JavaScript implementation of the JSON-LD processing algorithms) to make sure it is valid JSON-LD, not only valid JSON.[^ch05-17] Expanding normally downloads the schema.org context from the network. Tests should not depend on the network, so the test gives `jsonld` a tiny document loader that answers `https://schema.org` with a local stand-in context. This stand-in maps every term to the schema.org namespace, which is exactly what level 2 then checks properly.

### Level 2: vocabulary

The second level is where real mistakes show up. JSON-LD happily accepts any property name, so `"makesoffer"` (lowercase) or `"offers"` on a business expand without a complaint. To catch those, we need the vocabulary itself.

Schema.org publishes the whole vocabulary as one JSON-LD file (`schemaorg-current-https.jsonld`, about 1.5 MB and a little over 3,000 terms in version 30.1).[^ch05-18] `vocab-subset.js` renders the Nordlys pages, collects every type and property they use, and copies from the official file two facts for each: the superclasses of every type (`rdfs:subClassOf`) and the allowed domains of every property (`schema:domainIncludes`). The result is a small JSON file with 25 types and 52 properties that lives next to the layer and is regenerated when the markup changes. Listing 5.4 is the check that uses it.

**Listing 5.4** A domain check against the official vocabulary (`layers/05-structured-data/schema-check.js`)

```js
// A small schema.org vocabulary check: is every type known, and is every
// property allowed on the type it is used with (domainIncludes, with
// inheritance)? It reads a subset of the official vocabulary that
// vocab-subset.js extracts from https://schema.org/version/latest/.

/** Walk a JSON-LD value and call visit(type, property) for every typed node. */
export function walk(value, visit) {
  if (Array.isArray(value)) return value.forEach((v) => walk(v, visit));
  if (!value || typeof value !== 'object') return;
  const types = [].concat(value['@type'] ?? []);
  for (const [key, child] of Object.entries(value)) {
    if (key.startsWith('@')) {
      if (key === '@graph') walk(child, visit);
      continue;
    }
    for (const t of types) visit(t, key);
    walk(child, visit);
  }
  for (const t of types) visit(t, null);
}

export function checkVocabulary(jsonld, vocab) {
  const problems = [];
  const ancestors = (t) => [t, ...(vocab.classes[t] ?? [])];
  walk(jsonld, (type, prop) => {
    if (!vocab.classes[type]) return problems.push(`unknown type ${type}`);
    if (prop === null) return;
    const domains = vocab.properties[prop];
    if (!domains) return problems.push(`unknown property ${prop}`);
    if (!ancestors(type).some((t) => domains.includes(t))) problems.push(`${prop} is not a property of ${type}`);
  });
  return [...new Set(problems)];
}
```

The logic is short: a property is allowed on a type if one of its declared domains is the type itself or one of its ancestors. `makesOffer` is allowed on `VacationRental` because its domain includes `Organization`, and `Organization` is an ancestor of `VacationRental`.

I can tell you that this check is worth having from first-hand experience with this very chapter. My first version of the cabin graph pointed from the rental to the company with `provider`, which looks perfectly reasonable. The vocabulary check failed with "provider is not a property of VacationRental". It's right: in schema.org, `provider` belongs to things like services, reservations and creative works, not to businesses. The fix was `parentOrganization`, which belongs to `Organization`. No visual review would have caught it, and Google's own tools would only have flagged it if I had pasted that exact page into them.

### Level 3: parity

The third level checks the promise from the "True to the page" section. Listing 5.5 is the test that does it.

**Listing 5.5** The markup says what the page says (`tests/ch05-structured-data.test.js`, excerpt)

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

Run all the chapter's tests like this:

```
node --test tests/ch05-*.test.js
```

On 2 November 2026, all six tests passed on Node.js 22.23.2 with `jsonld` 9.0.0. The layer also registers a `structured-data` audit, so `GET /__audit` reports whether the JSON-LD parses on five key pages and whether the cabin price matches the page.

> **Try it yourself.** Three small exercises for this layer. First, add a `floorSize` to the accommodation and run the tests: the vocabulary check fails until you regenerate the subset with `node layers/05-structured-data/vocab-subset.js`, which is the intended workflow for every new property. Second, change the weekend rate of one cabin in `data/cabins.json` in a scratch copy and confirm that the page, the JSON-LD and the `/ask` answer all change together. Third, put `offers` on the rental in a scratch copy and read the error the check gives you.

### Manual tools

Automated checks don't replace the two official validators, they complement them. The Schema Markup Validator (validator.schema.org) checks generic schema.org markup, and Google's Rich Results Test (search.google.com/test/rich-results) checks only the features Google supports.[^ch05-19] The Rich Results Test has no public API, so it stays a manual step for pages where you expect a Google feature. If your project is in TypeScript, the `schema-dts` package (version 2.1.0, maintained by Google) gives you type definitions for the whole vocabulary, which catches many of the same mistakes at compile time.[^ch05-20]

### Structured data in a CMS or framework

Nordlys generates its markup in a few small functions because it is a small server-rendered app. Most real sites are built on a CMS, a commerce platform or a front-end framework, and the same principles apply with different mechanics.

In a CMS, the question to ask is where the markup comes from. Often it's a plugin, a theme and some hand-written snippets at the same time, which is the perfect recipe for the "two blocks that disagree" mistake. Pick one owner per type (for example, the SEO plugin owns `Organization` and `BreadcrumbList`, and your product templates own `Product`), turn off the rest, and check a page of each template with the Schema Markup Validator after every plugin update.

In a commerce platform, product markup usually comes with the platform. Check that it uses the price the customer actually pays (including the currency of the storefront), that it reflects stock, and that it doesn't mark up reviews from a third-party widget that the page loads with JavaScript after the markup was rendered.

In a front-end framework with server rendering, generate the JSON-LD on the server from the same props that render the page, and make sure it's in the initial HTML. Markup that only appears after client-side JavaScript runs may be seen by Google's renderer, but many other consumers (including the Markdown converters of Chapter 6 and simple fetchers used by agents) only see the first response.

In every case, the three-level check from this chapter works the same: fetch the rendered HTML, extract the blocks, check syntax, vocabulary and parity. The test doesn't care which system produced the markup.


## Keeping markup honest over time

Generating markup from data solves drift between the markup and the page. It doesn't solve drift between the page and reality, and some properties are more sensitive to that than others. Here are the ones I would watch on any site.

**Dates.** `datePublished` and `dateModified` are easy to fake and tempting to bump, because fresh content looks better. Nordlys sets `dateModified` to the published date because its articles carry no update date, and it shows the same date in the byline. If you add an "updated" field later, set it when the content really changes, not when a template changes or a build runs. Chapter 4 made the same argument for `lastmod` in the sitemap, and Google's sitemap documentation says it uses `lastmod` only when it is "consistently and verifiably" accurate.[^ch05-21] Consumers that learn your dates are noise will ignore them.

**Prices and availability.** The Nordlys prices change rarely, so the markup always matches. A site with dynamic pricing has a harder problem: the page may show a price computed for the visitor's dates, while the markup can only state a general rate. The rule stays the same. Mark up what the page states generally ("from NOK 2,200 per night"), and leave date-specific quotes to the interactive layers (the availability form, the API of Chapter 7 and the tools of Chapter 9), where a price can be computed for a real request.

**Reviews.** A review that's been removed from the page must also leave the markup, and an aggregate must be recomputed when reviews change. Generation from data handles both. Hand-maintained markup almost never does.

**Images.** Point `image` at images that exist and that show the actual property. A listing that uses stock photos in its markup tells every consumer something false about the cabin.

**Caching.** If your HTML is cached at a CDN for hours, the markup inside it is cached too. That's usually fine, but it means a price change appears in the markup no sooner than on the page, and you can't fix stale structured data separately from stale HTML. One more reason to keep them in one response.

## What to mark up first

Nordlys is a booking site, so its priorities were obvious. For other sites, here is a short ordering that I find holds up. It's an opinion, not a measurement, so adapt it.

1. **The thing you sell or publish.** For a shop, that is `Product` with `Offer` (and if you sell through ChatGPT or Google Shopping, a product feed as well, because those programmes read feeds, not page markup). For a publisher, `Article` or `NewsArticle` with a real author and real dates. For a local business, the right `LocalBusiness` subtype with address, opening hours and contact.
2. **The facts people compare.** Prices, ratings, opening hours, sizes, capacities. These are exactly the facts an agent extracts when it compares your offer with three others.
3. **Navigation context.** `BreadcrumbList` and `ItemList` help any consumer understand where a page sits in the site.
4. **Actions.** `potentialAction` with a working URL template. Cheap to add when the deep link exists, of unproven value today, and a good first draft of the tools you will build later in this book.
5. **Everything else.** Only when it describes something visible and useful.

Notice what's not on the list: markup for features that no longer exist, markup for content you don't have, and markup whose only purpose is to influence an AI system. The last one is a trap in both directions. It doesn't work in Google (by Google's own statement), and if it worked anywhere it would be indistinguishable from manipulation.

## NLWeb: schema.org as a question API

There is one more reason to care about clean structured data, and it comes from the person who started schema.org.

On 19 May 2025, at Build, Microsoft announced NLWeb, an open project conceived by R.V. Guha, the creator of RSS, RDF and schema.org, who had just joined Microsoft as CVP and Technical Fellow.[^ch05-8] The idea is simple and, honestly, elegant. A site already publishes schema.org markup and RSS feeds. NLWeb ingests that data into a vector store and lets anyone ask the site questions in natural language, answering in JSON using schema.org. And "every NLWeb instance is also a Model Context Protocol (MCP) server", so agents can use the same endpoint as tools.[^ch05-8] The project's README puts it boldly: "NLWeb is to MCP/A2A what HTML is to HTTP."[^ch05-22]

The documented REST API has two endpoints, `/ask` and `/mcp`, with the same arguments: a required `query`, and optional `site`, `prev` (previous queries), `decontextualized_query`, `streaming`, `query_id` and `mode` (`list`, `summarize` or `generate`). Each result carries `url`, `name`, `site`, `score`, a `description` and the item's `schema_object`, which is the schema.org data of that item.[^ch05-23] Launch collaborators included Eventbrite, Shopify, Tripadvisor, O'Reilly Media and others.[^ch05-8]

Where does NLWeb stand in November 2026? Let's look at the facts:

- The repository moved to `nlweb-ai/NLWeb` and has about 6.3k stars, but no tagged releases. The last push was on 11 August 2026, and the latest commits on the main branch (June 2026) are dependency updates.[^ch05-22]
- The specification link in the README (`nlweb.ai/spec`) failed TLS verification when I tried it on 2 November 2026 (certificate hostname mismatch), so I couldn't read the spec text that day.
- Cloudflare offers an "NLWeb Website" template in AI Search that deploys `/ask` and `/mcp` on a Worker, still labelled as a public preview.[^ch05-24]
- I found no 2026 adoption numbers, and no evidence that ChatGPT, Claude, Gemini or Copilot discover or call NLWeb endpoints on their own.
- Guha is now listed as a co-author of the Agentic Resource Discovery (ARD) specification, which Chapter 11 covers.[^ch05-25] In my reading, the discovery problem NLWeb left open is being taken up there.

So NLWeb is an influential idea with unclear momentum, not a standard to adopt by default. But the idea itself teaches something important, and Nordlys can show it in thirty lines without any model at all.

### Hands-on: an NLWeb-shaped /ask for Nordlys

Listing 5.6 is a deliberately naive question endpoint. It ranks cabins by how many words of the query appear in the cabin's name, region, summary and features, and it answers in the NLWeb result shape. The interesting line is the one that builds `schema_object`: it calls the same `cabinGraph()` function that produces the page's JSON-LD.

**Listing 5.6** A question endpoint that answers with schema.org objects (`layers/05-structured-data/ask.js`)

```js
import { cabinGraph } from './graph.js';

// An NLWeb-shaped question endpoint without a model: it ranks cabins by the
// words of the query and answers with each cabin's own schema.org object.
// It shows the idea behind NLWeb (Chapter 5): clean structured data is
// already most of a query API.
const words = (s) => String(s ?? '').toLowerCase().match(/[\p{L}\p{N}]+/gu) ?? [];

export function ask(store, origin, query) {
  const terms = new Set(words(query).filter((t) => t.length > 2));
  const features = store.features();
  const results = store.cabins().map((cabin) => {
    const text = new Set(words([cabin.name, cabin.region, cabin.county, cabin.summary, ...cabin.features.map((f) => features[f])].join(' ')));
    const score = [...terms].filter((t) => text.has(t)).length;
    const page = { url: `${origin}/cabins/${cabin.slug}` };
    const rental = cabinGraph(page, store, cabin)['@graph'][0];
    return { url: page.url, name: cabin.name, site: origin, score, description: cabin.summary, schema_object: rental };
  });
  return results.filter((r) => r.score > 0).sort((a, b) => b.score - a.score);
}
```

The layer mounts it at `GET /ask`. Let's ask it something:

```
curl "http://localhost:3000/ask?query=sauna+hot+tub"
```

The first result is Lyngen Lysthus with a score of 3, and its `schema_object` is exactly the `VacationRental` node from the cabin page, with its offers, its rating, its `ReserveAction` and all. A test asserts that equality, so the answer an agent gets from `/ask` can never disagree with the markup on the page.

What this demo shows is the point of the whole chapter in a nutshell. Once your facts are clean, typed and generated from one source, a question API is mostly a ranking problem. NLWeb adds a vector store and a model for the ranking and the summaries. Chapter 8 adds an MCP server with typed tools. Chapter 7 adds a real API with an OpenAPI description. All of them get easier when the modelling work of this chapter is done, and all of them can reuse the same functions.

One warning, if you go further than this toy: an endpoint that runs a language model over indexed content is a new attack surface. Indexed user content (reviews, comments) can carry prompt injection, and every query costs you money. Keep the indexed content curated, rate-limit the endpoint and read Chapter 16 before putting a model behind `/ask` in production.

## One model, many layers

Before we look at the graders, let me connect this chapter to the rest of the book, because the modelling you just did is reused far more often than the JSON-LD block itself.

The Markdown version of each page in Chapter 6 is rendered from the same page data, and it can carry the JSON-LD along, the way Cloudflare's converter does. The public API in Chapter 7 describes a cabin with a JSON Schema in its OpenAPI document. The fields of that schema (capacity, bedrooms, nightly rate, currency, check-in time) are the same facts we just typed, and naming them consistently across the markup and the API saves every client from building a translation table. The MCP server in Chapter 8 returns cabins from its tools, and nothing stops a tool result from including the schema.org object as well, exactly as NLWeb does. The WebMCP tools in Chapter 9 turn the availability and booking forms into callable functions, which is the strong, testable version of what `ReserveAction` only describes. And the commerce chapter (Chapter 12) needs prices, currencies and fees modelled precisely enough that an agent can show a person the final amount before anything is charged.

In other words, the questions you answered in this chapter (what is the thing, what does it cost and in which unit, who rated it, what can you do with it) are the questions every machine interface asks. Answering them once, in one place in your code, is the real deliverable. JSON-LD is one serialization of the answer.

There is also a lesson here for teams that are tempted to skip straight to the shiny layers. An MCP server or a set of WebMCP tools built on top of inconsistent data will expose the inconsistency faster and more visibly than any search engine ever did, because an agent acts on the data immediately. A weekend price that is wrong in the markup is an annoyance. The same wrong price in a booking tool is a support ticket and, possibly, a refund. Clean, typed, single-source facts are the foundation for everything that follows, and this chapter is where Nordlys lays them.

## What the graders see

Here is a slightly awkward fact for a chapter in a book about agent readiness: neither of the two graders this book tracks gives you any points for structured data. Table 5.4 shows it.

**Table 5.4** Structured data in the two graders (November 2026)

| Grader | Structured data check | Effect of this chapter |
| --- | --- | --- |
| isitagentready.com | None of its 23 documented checks reads JSON-LD[^ch05-26] | Level unchanged (Level 2 since Chapter 4) |
| Lighthouse 13.6.0, Agentic Browsing | No audit in the category reads JSON-LD, and the source has no gatherer for `ld+json` | Unchanged |
| Lighthouse 13.6.0, SEO | A manual `structured-data` audit with weight 0 that tells you to use the validators | Listed as a manual check, no score change |

Should that worry you? I don't think so. Graders measure what is easy to measure and new. Structured data is neither new nor easy to grade (whether markup is true to the page needs a person or a test like ours). The reasons to do it are the ones in Table 5.1: Google uses it, agent-facing Markdown keeps it, NLWeb-style tools are built on it, and every later layer of this book reuses the modelling. Please treat a grader as a checklist of things that are cheap to verify, not as a definition of agent readiness.

## Checklist by role

- **Product manager.** Decide which facts about your offer must be machine-readable (price, capacity, rating, location, how to book) and make "markup matches the page" a release criterion. Don't promise rich results, and don't promise AI visibility.
- **Content and SEO.** Own the type choices and the wording of names and descriptions. Remove markup for retired features only if it no longer describes the page. Keep dates honest.
- **Developer.** Generate JSON-LD from the same data as the page, use `@id` to link nodes, keep values typed (numbers, ISO dates, absolute URLs) and add the three-level check to CI.
- **Designer.** If the markup needs a fact that the page doesn't show (an average rating, a location), design a place for it on the page instead of hiding it in markup.
- **QA.** Run the Schema Markup Validator on one page of each template per release, and the Rich Results Test where you expect a Google feature.
- **Security.** Treat JSON-LD as content a model may read. Nothing in it that isn't visible, and user-generated text (reviews) escaped and moderated like everywhere else.
- **Legal and trust.** Reviews and ratings in markup must be real and complete. Selective or invented ratings are a consumer-protection problem, not only a search guideline problem.

## Summary

- Structured data is a typed description of what a page is about, almost always schema.org in JSON-LD. The current schema.org release is 30.1 (16 September 2026).
- Google uses structured data for rich results and to understand pages, but says it is not required for its AI features and that no special markup is needed. FAQ rich results ended on 7 May 2026, and vacation rental rich results are partner-only.
- No browsing-agent vendor documents reading JSON-LD during a task. Treat it as plausible and unverified, and value structured data as a machine-readable source of truth for several consumers.
- For a booking site, model the listing as a `VacationRental` that contains an `Accommodation`, attach prices with `makesOffer` and specific price specifications, add real reviews and a computed rating, and use `ReserveAction` with a working URL template as a bridge to later action layers.
- Mark up only what is visible. If the markup needs a fact the page lacks, show it on the page or leave it out.
- Generate markup from the same data as the page, and check it in CI at three levels: syntax, vocabulary (domains against the official schema.org file) and parity with the page.
- NLWeb shows the idea of schema.org as a question API. The project has unclear momentum in 2026, but the idea makes the case for clean structured data beyond search.
- Neither isitagentready nor Lighthouse's agentic category scores structured data. Do it for the consumers, not for the graders.

[^ch05-1]: "Schema.org Version 30.1," Schema.org, https://schema.org/version/latest (published 16 September 2026, retrieved November 2026).
[^ch05-2]: "Schema.org releases," Schema.org, https://schema.org/docs/releases.html (retrieved November 2026).
[^ch05-3]: "Introduction to structured data markup in Google Search," Google Search Central, https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data (retrieved November 2026).
[^ch05-4]: "Markdown for Agents," Cloudflare Docs, https://developers.cloudflare.com/fundamentals/reference/markdown-for-agents/ (retrieved November 2026).
[^ch05-5]: "VacationRental," Schema.org, https://schema.org/VacationRental. Usage bands for LodgingBusiness, Accommodation, ReserveAction and LodgingReservation are on their term pages (retrieved November 2026).
[^ch05-6]: "AI optimization guide," Google Search Central, https://developers.google.com/search/docs/fundamentals/ai-optimization-guide (last updated 10 July 2026, retrieved November 2026).
[^ch05-7]: B. Schwartz, "Microsoft Bing: Schema markup helps Copilot LLMs understand content," Search Engine Roundtable, March 2025, https://www.seroundtable.com/schema-llms-copilot-bing-microsoft-39093.html (a report of a conference talk, retrieved November 2026).
[^ch05-8]: "Introducing NLWeb: Bringing conversational interfaces directly to the web," Microsoft Source, 19 May 2025, https://news.microsoft.com/source/features/company-news/introducing-nlweb-bringing-conversational-interfaces-directly-to-the-web/ (retrieved November 2026).
[^ch05-9]: "Product feed specification," OpenAI for developers, https://developers.openai.com/commerce/specs/file-upload/products (seen as a search result, the page was not read in full, retrieved November 2026).
[^ch05-10]: "Latest Google Search documentation updates," Google Search Central, https://developers.google.com/search/updates (entries of 12 June 2025, 9 September 2025, November 2025 and 8 May 2026, retrieved November 2026).
[^ch05-11]: "Vacation rental (VacationRental) structured data," Google Search Central, https://developers.google.com/search/docs/appearance/structured-data/vacation-rental (updated 8 September 2026, retrieved November 2026).
[^ch05-12]: Schema.org term pages: https://schema.org/LodgingBusiness, https://schema.org/Accommodation and https://schema.org/ReserveAction (retrieved November 2026).
[^ch05-13]: "makesOffer," Schema.org, https://schema.org/makesOffer, and "offers," https://schema.org/offers (retrieved November 2026).
[^ch05-14]: "General structured data guidelines," Google Search Central, https://developers.google.com/search/docs/appearance/structured-data/sd-policies (retrieved November 2026).
[^ch05-15]: "LodgingReservation," Schema.org, https://schema.org/LodgingReservation (retrieved November 2026).
[^ch05-16]: "AI features and your website," Google Search Central, https://developers.google.com/search/docs/appearance/ai-features (retrieved November 2026).
[^ch05-17]: "jsonld," npm, https://www.npmjs.com/package/jsonld (version 9.0.0, retrieved November 2026).
[^ch05-18]: The vocabulary file is https://schema.org/version/latest/schemaorg-current-https.jsonld (1.5 MB on 2 November 2026, retrieved November 2026).
[^ch05-19]: Schema Markup Validator, https://validator.schema.org/, and Rich Results Test, https://search.google.com/test/rich-results (both retrieved November 2026).
[^ch05-20]: "schema-dts," npm, https://www.npmjs.com/package/schema-dts (version 2.1.0, published 2 October 2026, source at https://github.com/google/schema-dts, retrieved November 2026).
[^ch05-21]: "Build and submit a sitemap," Google Search Central, https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap (retrieved November 2026).
[^ch05-22]: NLWeb repository, GitHub, https://github.com/nlweb-ai/NLWeb (retrieved November 2026).
[^ch05-23]: "NLWeb REST API," NLWeb repository, https://github.com/nlweb-ai/NLWeb/blob/main/docs/nlweb-rest-api.md (retrieved November 2026).
[^ch05-24]: "NLWeb," Cloudflare AI Search docs, https://developers.cloudflare.com/ai-search/how-to/nlweb/ (updated 10 July 2026, retrieved November 2026).
[^ch05-25]: "Agentic Resource Discovery specification," version 0.91, https://agenticresourcediscovery.org/spec/ (retrieved November 2026).
[^ch05-26]: "isitagentready.com full reference," Cloudflare, https://isitagentready.com/llms-full.txt (retrieved November 2026).
