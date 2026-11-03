# Chapter 12: Agents that buy: commerce and payments

This chapter covers

- Why the moment an agent wants to pay is different from every layer before it
- The commerce protocols of November 2026: UCP and its Lodging draft, ACP, AP2 mandates, the card networks’ agent programmes, x402 and MPP
- What a small booking site should do now, and what it can safely wait for
- Building an agent-safe checkout for Nordlys Cabins: the agent prepares the booking, the guest confirms and pays on the site
- Which isitagentready checks this layer moves, and why Lighthouse does not care

Up to this chapter, everything we added to Nordlys Cabins was about reading and acting. An agent can find the cabins (Chapters 5 and 6), query the API (Chapter 7), call MCP tools (Chapter 8) and use the booking form through WebMCP (Chapter 9). Chapter 10 taught us to put a confirmation in front of anything that costs money. Chapter 11 made all of it discoverable.

One step is left, and it is the step every business actually cares about: the booking turns into money. This is where agent-readiness stops being a technical topic only. Money brings liability (who pays back a wrong booking?), regulation (consumer law, strong customer authentication in Europe, card network rules) and fraud. It also brings a crowd of protocols. In 2025 and 2026 almost every big name in payments and AI published one, and several of them overlap.

In this chapter we sort the crowd. I’ll show you what each protocol standardizes, who is behind it, how far it is and how many sites use it, with the dates. Then we make a decision for a small business like Nordlys, and we build it. The decision, as a spoiler: let agents do the tedious part, keep the decision and the payment with the person and on your own site. The protocol that fits a cabin-rental site best, the Universal Commerce Protocol’s Lodging capability, is still a draft, and our code will say so in every file.

## What changes when an agent wants to pay

Let’s start with the business view, because the protocols only make sense against it.

When a person books a cabin on nordlys.example today, four things happen that nobody writes down. The person sees the final price, with the cleaning fee. The person reads (or at least could read) the cancellation terms. The person types their own card details into a payment page, often with a bank app confirming the payment. And Nordlys is the merchant of record: the company the guest pays, the name on the card statement, the one who handles refunds and complaints.

An agent in the middle can break each of these. It can see a price that changed a minute later. It can skip the terms. It can be asked to handle card numbers it should never touch. And it can be run by a company that decides to become the merchant itself, which is exactly what happened with some of the first shopping experiences in AI assistants. That is why I think about agent commerce as four questions, and every protocol in this chapter answers some of them:

1. **What exactly is being bought?** The cabin, the dates, the guests, the total, the cancellation terms. The agent and the site must agree on one authoritative version of this, with an expiry.
2. **Did the person agree to it?** Not “did the person ask an agent to find a cabin”, but “did the person approve this booking at this price”. This is the hardest question and the one with the most new technology.
3. **Who is paying, and with what?** A card, a wallet, a bank transfer, a stablecoin, and who touches the credentials on the way.
4. **Who is the agent?** Is this request really from the assistant it claims to be, run by a company you can hold to account? That question is big enough for its own chapter (Chapter 15), but card networks build on it, so it shows up here too.

Keep these four questions in mind. When a vendor pitches you an agent commerce integration, ask which of the four it answers and which it leaves to you.

Figure 12.1 places the protocols of this chapter on those four questions.

![Figure 12.1 — Four questions every agent purchase has to answer, and the protocols that answer each of them in November 2026. Filled boxes are the path Nordlys Cabins takes in this book: a booking session in the UCP Lodging shape, the guest confirming on nordlys.example, verified agent signatures (Chapter 15) and the payment provider’s own payment page. Dashed boxes are the options to watch, or to get through your payment provider: ACP, AP2 mandates, the card networks’ agent programmes, and x402 and MPP for pay-per-request.](images/figure-12-1.png)

### How much of this is real today

Before the details, let’s have a look at adoption, so we keep our feet on the ground. Cloudflare Radar scans the top 200,000 domains for agent standards, and on 2 November 2026 it had results for 115,468 of them.[^ch12-1] The Universal Commerce Protocol profile was on 5,429 domains (4.7%). The Agentic Commerce Protocol discovery file was on 32 domains. MPP was on 13, x402 on 7 and AP2 on 4. Radar’s own footnote reminds us that “x402 is only relevant for sites with paid content”, so a low number there is not a failure.[^ch12-1]

Those 5,429 UCP domains are not 5,429 teams that read a spec. Most of them are online shops on one platform. The research for this book found Shopify storefronts serving a `/.well-known/ucp` profile by default, and when I fetched the profiles of two of those stores on 2 November 2026 they declared UCP version 2026-08-25 with shopping checkout capabilities and an MCP endpoint on the store’s `myshopify.com` host.[^ch12-2] Radar’s Ecommerce category tells the same story: UCP on 4,181 of 18,927 e-commerce domains. In the Travel category, which is where Nordlys lives, UCP was on 38 of 6,896 domains.[^ch12-1] Please note: that a platform puts most of these profiles there is my inference from the stores I checked, not a breakdown Radar publishes.

Bottomline: agent commerce in November 2026 is a platform story. If your shop runs on a commerce platform, check what it already publishes before you write a line of code. If you run your own booking engine, like Nordlys, you are early, and the right strategy is to be ready rather than first.

## The protocols, one by one

There are more acronyms in this space than cabins in Lofoten, so I’ll keep each one to the same five facts: who is behind it, what it standardizes, how an agent discovers it, its status in November 2026, and what it means for a small site. Table 12.1 at the end of the section puts all of them side by side.

### UCP: the Universal Commerce Protocol

UCP is an open standard for the whole shopping journey between an AI platform (the agent’s side) and a business. Its site lists co-developers in three groups. Shopping has Google, Shopify, Etsy, Wayfair, Target, Walmart, Amazon, Microsoft, Meta, Salesforce and Stripe. Lodging has Amadeus, Booking.com, Expedia Group, Google, Hilton, Marriott and Trip.com. Food has DoorDash, Google, Square, Toast and Uber Eats.[^ch12-3] The business stays the merchant of record, and the site describes account linking through OAuth 2.0 and payments through AP2 (both come later in this chapter and in Chapter 14).[^ch12-3]

The core idea is a **business profile** at a well-known address, `/.well-known/ucp`. In the specification’s words, platforms “MUST resolve schemas following this sequence”, and the first step is “Discovery: Fetch business profile from /.well-known/ucp”.[^ch12-4] The profile is a JSON document with one required member, `ucp`, which carries:

- `version`: the protocol version, a date such as `2026-08-25` (UCP versions are dates, like MCP’s)
- `services`: which transports the business offers for each service (REST, MCP, A2A or an embedded UI), each with an `endpoint` and a `schema`
- `capabilities`: what the business can do, named in reverse-domain style such as `dev.ucp.shopping.checkout`, each with its own version, spec and schema
- `payment_handlers`: which payment methods the business accepts through the protocol. The specification says the `services` and `payment_handlers` registries “MUST be present even when empty”.[^ch12-4]

A profile may also carry public signing keys in a `keys` array. That array is an RFC 7517 JSON Web Key Set, and the specification points out that the same document can then serve as a Web Bot Auth key source, so the identity work of Chapter 15 and the commerce work of this chapter meet in one file.[^ch12-4]

When an agent and a business talk, both sides compare their profiles and use what they have in common. A capability has to match by name and by version. Extensions (discounts, fulfilment, loyalty points) declare which capability they extend, and the specification defines how the two sides compute the intersection. For a site owner this means one thing: **every entry in your profile is a promise**. A scanner or a platform that reads it will try to use it.

The latest released version on 2 November 2026 was 2026-08-25, tagged in the project’s repository on 25 August 2026.[^ch12-5]

### The Lodging draft: a standard written for booking sites

Now the part that matters most for a booking site. On 24 September 2026 the UCP repository merged a pull request titled “feat: Introduce Lodging Booking Capability and Cancellation Policy Extension” (PR #780), and ucp.dev now shows the banner “Lodging draft specification now available”.[^ch12-5][^ch12-3] The capability is called `dev.ucp.lodging.booking`. Its first lines are a warning I’ll repeat in this chapter more than once:

> **Still in flux:** The Lodging booking capability is in draft. Its own page says that “data models, protocol bindings, and operational flows are under active iteration and may undergo breaking changes as the specification evolves.” In November 2026 it is published only under the `draft` version of the specification site (ucp.dev/draft/...), not in a dated release.[^ch12-6]

Why does it matter so much for us? Because it describes exactly the business of Nordlys Cabins, and it was written with the large travel companies at the table. Google’s page for hotel partners asks them to “adopt UCP to enable agentic actions on Google surfaces such as AI Mode in Google Search”, offers a waitlist, and repeats the line that matters to every booking site: “You remain the Merchant of Record.”[^ch12-7] A trade-press report adds that Google plans to adopt the draft for AI Mode hotel booking.[^ch12-8]

Let’s look at how the draft models a booking. It is built around a **booking session**: a short-lived, server-side object that the platform creates and enriches, and that the business turns into a real reservation at the end. Figure 12.2 shows its states.

![Figure 12.2 — The booking session lifecycle in the UCP Lodging draft. A session starts incomplete, collects stay, guest and payment details, and becomes ready_for_complete, or requires_escalation when a person has to continue on the business’s site through continue_url. Only Complete Booking Session (or the person on the business’s page) creates the reservation. A session can become canceled from any state, including by expiry.](images/figure-12-2.png)

The vocabulary is worth learning, because you will meet it in every UCP integration:

- **`stays`**: one entry per unit you book. A stay binds an `accommodation_type` (the physical thing: a room type, or for Nordlys the whole cabin), a `rate_plan` (the commercial deal: a flexible rate, a non-refundable rate), `stay_dates` (check-in and check-out) and `occupancy` (adults, children, total).
- **`booker` and `guests`**: the person who pays and is responsible for the booking, kept apart from the people who sleep there. The draft is strict about privacy here: guest identifiers are opaque and scoped to one session, and platforms “**MUST NOT** use persistent cross-merchant user tracking identifiers”.[^ch12-6]
- **`totals`**: the authoritative price, as an array of entries such as `subtotal`, `fee`, `tax` and exactly one `total`. Amounts are integers in minor units, so 7,500 Norwegian kroner become `750000`. The draft calls this “strict all-in pricing” and says the guest “is presented with the complete stay liability before booking confirmation”.[^ch12-6]
- **`policies`**: binding terms attached to the session. The cancellation-policy extension adds a `refundability` field with the well-known values `refundable`, `partially_refundable` and `non_refundable`, and a human-readable description.
- **`expires_at`**: how long the quote (and any hold on inventory) stays valid. The business “MAY place a temporary soft hold on inventory”, or MAY check availability again at the end instead.[^ch12-6]
- **`status`**: one of `incomplete`, `requires_escalation`, `ready_for_complete`, `complete_in_progress`, `completed` or `canceled`.
- **`continue_url`**: the address on the business’s own site where a person can pick up the session. A business “MUST provide `continue_url` when returning `status` = `requires_escalation`“.[^ch12-6]

And here is the sentence I built the Nordlys design on. The draft says that the business “does not need to become PCI DSS compliant to accept card payments through this capability”, and then: “Unless the AP2 Mandates extension is supported, the booking must be finalized manually by the user through a trusted UI.”[^ch12-6] In simple words: without cryptographic proof of the person’s consent, a person finishes the booking. The standard itself writes the human into the loop.

The draft offers the same five operations over REST (`POST /booking-sessions`, `GET` and `PUT /booking-sessions/{id}`, `POST /booking-sessions/{id}/complete` and `/cancel`) and as MCP tools (`create_booking_session`, `get_booking_session`, `update_booking_session`, `complete_booking_session` and `cancel_booking_session`).[^ch12-9] So the MCP server from Chapter 8 is a natural home for a UCP binding later.

### ACP: the Agentic Commerce Protocol

ACP is the other big shopping protocol. Its repository states that “the specification is maintained by OpenAI and Stripe and is currently in beta”, under the Apache 2.0 licence.[^ch12-10] It defines checkout sessions between an agent and a seller, product feeds, and a delegated payment flow in which the payment provider gives the agent a token that is limited to one purchase (Stripe calls its version a Shared Payment Token). Like UCP, it keeps the seller as merchant of record.[^ch12-11]

ACP versions are dates too. The repository lists releases from 2025-09-29 to 2026-04-17, and the 2026-04-17 changelog added carts, orders, authentication, an MCP binding and a discovery document at `/.well-known/acp.json`, which agents read “for pre-session capability checks”.[^ch12-10][^ch12-12] The last commit I saw on the main branch was from 17 July 2026.

ACP launched with ChatGPT’s Instant Checkout in September 2025. In March 2026, according to press reports I could not confirm from OpenAI’s own pages, OpenAI pivoted away from Instant Checkout toward retailers’ own apps and checkouts.[^ch12-13] That leaves ACP mainly as a checkout and product-feed API. For a small site it is a “watch” item: if you are invited into an AI platform that uses it, your payment provider will most likely give you the integration.

### AP2: mandates as proof of consent

AP2, the Agent Payments Protocol, answers question two, “did the person agree?”, and only that one. Google announced it on 16 September 2025.[^ch12-14] Its home page now describes it as an open protocol “available as an extension for the open-source Agent2Agent (A2A) protocol and Universal Commerce Protocol” and headlines “AP2 v0.2 Release and FIDO Alliance Donation”.[^ch12-14] I could not find the exact date of the donation on the site.

The central object is a **mandate**: a signed, verifiable digital credential (an SD-JWT) in which a trusted surface records what the person approved. Version 0.2 defines two kinds. A **checkout mandate** authorizes the completion of one checkout. It contains a merchant-signed copy of the checkout and its hash, so the merchant can check that the thing being paid is exactly the thing the person saw. A **payment mandate** authorizes the payment for that checkout and is verified by the credential provider, the network and the merchant’s payment processor. It carries the payee, the amount in minor units, the instrument and optional risk signals.[^ch12-15] Each comes in a “closed” form (this exact checkout) and an “open” form, where the person sets constraints in advance, for example a list of acceptable items, and the agent completes the purchase later within them.[^ch12-15]

In UCP, AP2 is the extension that lets a platform call Complete Booking Session programmatically: the platform submits both mandates to the business’s complete endpoint, the business verifies the checkout mandate and its payment processor verifies the payment mandate.[^ch12-16] Without it, as we saw, a person finishes the booking. Radar found AP2 on 4 domains of the top 200,000.[^ch12-1]

### Visa and Mastercard: agents with a card

The card networks run their own programmes, and both lean on agent identity. Visa’s Trusted Agent Protocol is for “merchants and infrastructure providers who want to securely recognize and transact with Visa-approved AI agents”. A trusted agent “will include a message signature in its request to your server”, built on RFC 9421, and the merchant’s job is to verify it.[^ch12-17] Cloudflare wrote in October 2025 that “both Trusted Agent Protocol and Agent Pay leverage Web Bot Auth as the agent authentication layer”, Agent Pay being Mastercard’s programme.[^ch12-18]

On the payment side, Mastercard describes its framework as a way for merchants to “recognize trusted AI agents and accept secure, tokenized transactions”, so that the agent works with a token instead of the real card number.[^ch12-30] I could not read Mastercard’s developer documentation in full (its pages need JavaScript), so I describe Agent Pay only through the Cloudflare post and Mastercard’s own news page, and I recommend you ask your acquirer for the current requirements. What matters for a site owner: **these programmes reach you through your payment provider and your edge**, not through new pages on your site. The verification part is Chapter 15’s topic, and we’ll build it there.

### Paying per request: HTTP 402, x402 and MPP

The last group answers question three for a different kind of purchase: an agent paying for one API call or one document, a few cents at a time, with no account and no checkout page. Both protocols revive HTTP status code 402 Payment Required, which the HTTP specifications reserved long ago and never defined in detail.

**x402** came out of Coinbase, and Cloudflare and Coinbase announced an x402 Foundation together in September 2025.[^ch12-19] On 2 April 2026 the foundation launched under the Linux Foundation, and by its operational launch on 14 July 2026 it had 40 members, with Adyen, AWS, American Express, Circle, Cloudflare, Coinbase, Fiserv, Google, Mastercard, Shopify, Stripe and Visa among the premier ones.[^ch12-20] Version 2 of the protocol uses three headers, each carrying base64-encoded JSON: `PAYMENT-REQUIRED` from server to client with the 402, `PAYMENT-SIGNATURE` from client to server on the retry, and `PAYMENT-RESPONSE` from server to client with the settlement result.[^ch12-21] The `PAYMENT-REQUIRED` object lists what the server `accepts`: a scheme (such as `exact`), a network in CAIP-2 format (such as `eip155:84532`, the Base Sepolia test network), an amount in atomic units of an asset, and the address to pay.[^ch12-22] In practice that means stablecoins on blockchains today, which is why I call x402 crypto-first.

**MPP**, the Machine Payments Protocol, is the payment industry’s other answer. Stripe’s documentation describes it as “an open protocol that lets agents pay for your APIs and services programmatically without a checkout UI, co-authored by Stripe and Tempo”.[^ch12-23] It launched on 18 March 2026 alongside the Tempo blockchain’s mainnet (Stripe’s announcement and several reports give that date).[^ch12-24] Where x402 invents its own headers, MPP defines a new HTTP authentication scheme called `Payment`: the 402 carries a `WWW-Authenticate: Payment ...` challenge with an id, a realm, a payment method and an encoded request, and the client answers with a credential.[^ch12-25] Its core is an individual Internet-Draft, “The ‘Payment’ HTTP Authentication Scheme” (`draft-httpauth-payment-01`, last updated 9 September 2026), with no working group behind it yet.[^ch12-26] MPP supports cards through Stripe’s Shared Payment Tokens as well as stablecoins, and its own blog announced x402 compatibility in June 2026.[^ch12-23][^ch12-25]

Neither is for Nordlys. A cabin booking is a large, considered purchase with a cancellation policy, not a per-request micropayment. These protocols are for API businesses and for content publishers, and Chapter 15 comes back to them with Cloudflare’s pay per crawl, which uses a 402 of its own. We will still build a 402 response, as a teaching example, so you can see one.

### All of them in one table

Table 12.1 lines up the protocols with the four questions. Read the status column carefully: almost everything here is a draft, a beta or a version 0.x.

Table 12.1 Agent commerce protocols in November 2026

| Protocol | Backed by | Answers | How an agent finds it | Status, Nov 2026 | Radar, 2 Nov 2026 |
|---|---|---|---|---|---|
| UCP | Google, Shopify and co-developers | what, and who pays (with AP2) | `/.well-known/ucp` | 2026-08-25 released, Lodging in draft | 5,429 domains |
| ACP | OpenAI and Stripe | what, who pays | `/.well-known/acp.json` | beta, 2026-04-17 | 32 domains |
| AP2 | Google, donated to FIDO Alliance | did the person agree | extension in A2A Agent Card or UCP profile | v0.2 | 4 domains |
| Visa Trusted Agent Protocol, Mastercard Agent Pay | card networks | who the agent is, who pays | signatures on each request | live programmes | not measured |
| x402 | x402 Foundation (Linux Foundation) | who pays, per request | HTTP 402 with `PAYMENT-REQUIRED` | V2 | 7 domains |
| MPP | Stripe and Tempo | who pays, per request | HTTP 402 with `WWW-Authenticate: Payment` | individual IETF draft | 13 domains |

## What a small booking site should do in November 2026

So, what do we do with all this at Nordlys? I’ll answer the way I would answer a product manager, and then we build it.

**Do now.** Make availability, prices and booking readable and callable, which the earlier chapters already did. Then add a handoff: an agent can prepare a complete booking (cabin, dates, guests, the all-in price, the cancellation terms), and the guest finishes it on your own site. That gives the agent a clear, machine-readable path to “almost done”, and it keeps the four things from the start of this chapter in your hands: the final price, the terms, the payment page and the merchant-of-record role.

**Ask your payment provider.** Agent payments reach a small business through its PSP (payment service provider) and its acquirer, not through a protocol you implement yourself. Ask which agent features they support (delegated tokens such as Stripe’s Shared Payment Tokens, the card networks’ agent programmes), and what changes for strong customer authentication. Nordlys is in Norway, which follows the European payment rules, and I would not assume that an agent flow removes any authentication step. That is a question for your provider, not for a book.

**Model your data so it maps later.** The UCP Lodging draft is a good free design review. Does your booking have one authoritative total with every fee in it? Is the cancellation policy a structured thing, or only a paragraph on the FAQ page? Do you keep the booker separate from the guests? Can a quote expire? Nordlys’s store already returned a full price with the cleaning fee and a cancellation policy object, so the mapping in the next section was mostly renaming.

**Join, don’t build, the big channels.** If Google’s AI Mode matters for your bookings, join the UCP for Lodging waitlist on Google’s partner page.[^ch12-7] If an AI platform invites you to sell through ACP, let your PSP do the integration.

**Wait for.** AP2 mandates (version 0.2, now at FIDO), the Lodging draft’s first dated release, and pay-per-request protocols unless you sell an API or content. None of them pays off for a small site in November 2026.

**Never do.** Let an agent type card numbers into your forms on a person’s behalf, or accept card data through an API or tool that an agent calls. UCP’s whole payment design, ACP’s delegated tokens and AP2’s mandates exist precisely so that raw card details do not pass through the agent.

> **Note:** Publishing `/.well-known/ucp` is a claim, not a decoration. Scanners and platforms read every entry as something they can use. In the next section Nordlys publishes a profile because this book needs to show one, and it marks every draft part so that no production platform negotiates with it by accident. On your own site, publish only what you actually serve.

## Hands-on: the Nordlys commerce layer

> **Hands-on:** This section builds layer `12-commerce` of the demo app: a UCP business profile, booking sessions shaped after the Lodging draft, and the page where the guest confirms. If you don’t read JavaScript, the short version is: an agent asks for a booking and gets back a price, the cancellation terms and a link. The booking exists only after a person opens that link and presses “Confirm and book”. Pick up again at “The agent-safe checkout, without any protocol”.

The layer lives in `nordlys-cabins/layers/12-commerce/` in the demos repository.[^ch12-27] It uses only Node.js (version 22 or later, we ran it on 22.23) and the app’s own Hono 4.13.16 setup, with no new dependencies. Run the app with all layers up to this chapter, `npm start -- --upto=12`, and the new addresses appear in `GET /__layers`.

### The business profile

Listing 12.1 builds the profile. Two version strings do the honest work here. `UCP_VERSION` is the latest released protocol version, 2026-08-25, because the profile structure itself comes from that release. The Lodging service and capability exist only in the draft, which has no release date. So the layer pins them to `DRAFT_VERSION`, the date of the draft commit we built against (31 October 2026), and points `spec` and `schema` at ucp.dev’s `draft` pages. A real platform negotiates only versions it knows, so it will not mistake this for a released capability.

**Listing 12.1** `nordlys-cabins/layers/12-commerce/ucp.js` (excerpt) — the business profile
```js
// The UCP documents Nordlys publishes: the business profile at /.well-known/ucp
// and the booking session object. DRAFT IMPLEMENTATION (see sessions.js).
export const UCP_VERSION = '2026-08-25'; // latest released UCP version
export const DRAFT_VERSION = '2026-10-31'; // the Lodging draft as we built against it
const DRAFT = 'https://ucp.dev/draft';

export function businessProfile(origin) {
  return {
    ucp: {
      version: UCP_VERSION,
      services: {
        'dev.ucp.lodging': [{
          version: DRAFT_VERSION,
          spec: `${DRAFT}/specification/overview/`,
          transport: 'rest',
          schema: `${DRAFT}/services/lodging/rest.openapi.json`,
          endpoint: `${origin}/ucp/v1`,
        }],
      },
      capabilities: {
        'dev.ucp.lodging.booking': [{
          version: DRAFT_VERSION,
          spec: `${DRAFT}/specification/lodging/booking/`,
          schema: `${DRAFT}/schemas/lodging/booking.json`,
        }],
        'dev.ucp.lodging.policy.cancellation': [{
          version: DRAFT_VERSION,
          extends: ['dev.ucp.lodging.booking'],
          spec: `${DRAFT}/specification/lodging/extensions/cancellation-policy/`,
          schema: `${DRAFT}/schemas/lodging/policy_cancellation.json`,
        }],
      },
      payment_handlers: {}, // no payment through agents: the guest pays on our site
    },
  };
}
```

Please note the last line of the profile: `payment_handlers` is an empty object. The specification requires the member, and an empty registry says, in the protocol’s own language, “you can’t pay me through the API”. That is our policy, written where an agent will read it.

The layer serves the profile with `ctx.staticFile()`, so it is a plain JSON file at `/.well-known/ucp`. Here is what the server returns, read with curl from the demo app running with `PUBLIC_ORIGIN=https://nordlys.example`:

```text
$ curl -s -i http://127.0.0.1:4512/.well-known/ucp | head -3
HTTP/1.1 200 OK
content-security-policy: default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'self'; object-src 'none'
content-type: application/json; charset=utf-8
```

### Booking sessions

A session is created with `POST /ucp/v1/booking-sessions`. Listing 12.2 turns the UCP request (property, stays, dates, occupancy) into a call to the same `checkAvailability()` function the booking form uses, so an agent can never get a price that a person would not get. Errors come back as UCP messages: a validation problem is `recoverable` and carries a JSONPath (`path`) to the field the agent should fix, and a cabin that is already booked is the draft’s standard `inventory_exhausted` error with severity `unrecoverable`.

**Listing 12.2** `nordlys-cabins/layers/12-commerce/sessions.js` (excerpt) — opening a booking session
```js
// Booking sessions shaped after the UCP Lodging draft (dev.ucp.lodging.booking).
// DRAFT IMPLEMENTATION: written against the UCP draft at commit 58c7ab9
// (31 Oct 2026). Field names follow that draft and may change before release.
import { randomBytes } from 'node:crypto';

export const SESSION_MINUTES = 15;
const minor = (nok) => nok * 100; // UCP amounts are integers in minor units

const fieldPath = {
  cabin: '$.property.id',
  checkIn: '$.stays[0].stay_dates.start_date',
  checkOut: '$.stays[0].stay_dates.end_date',
  guests: '$.stays[0].occupancy.total',
};

export function createSessions({ store, now }) {
  const sessions = new Map();

  /** Turn a UCP create request into a Nordlys availability check. */
  function open(body, { agent } = {}) {
    const stay = body?.stays?.[0] ?? {};
    const input = {
      cabin: body?.property?.id,
      checkIn: stay.stay_dates?.start_date,
      checkOut: stay.stay_dates?.end_date,
      guests: stay.occupancy?.total,
    };
    const check = store.checkAvailability(input);
    if (check.errors.length || !check.available) {
      const messages = check.errors.map((e) => ({
        type: 'error', code: e.code, path: fieldPath[e.field], content: e.message, severity: 'recoverable',
      }));
      if (!messages.length) messages.push({
        type: 'error', code: 'inventory_exhausted', content: `${check.cabin.name} is not available for those dates.`, severity: 'unrecoverable',
      });
      return { ok: false, messages };
    }
    const session = {
      id: 'bks_' + randomBytes(12).toString('base64url'),
      input, quote: check.quote, cabin: check.cabin, agent,
      booker: body.booker ?? null,
      status: 'requires_escalation',
      expiresAt: new Date(now().getTime() + SESSION_MINUTES * 60_000),
    };
    sessions.set(session.id, session);
    return { ok: true, session };
  }
```

Two design choices are hiding in these lines. The first is that every successful session starts in `requires_escalation`. Nordlys accepts no payment through the protocol, so there is nothing an agent can do to make the session `ready_for_complete`. The second is that the session holds the quote for 15 minutes but holds no inventory. The draft allows both strategies (a soft hold, or checking availability again at the end). For a small site I prefer the second: an agent that opens fifty sessions while comparing cabins should not block fifty stays for real guests.

Let’s see it in action. This is a real exchange with the demo app. The request is the draft’s single-stay example adapted to Fjellro, a cabin in Rondane, for three nights in December, and jq keeps the response to the fields that matter here:

```text
$ curl -s -X POST http://127.0.0.1:4512/ucp/v1/booking-sessions \
    -H 'content-type: application/json' \
    -H 'UCP-Agent: profile="https://platform.example/profile"' \
    -d @stay.json | jq '{id, status, totals, policies, messages, continue_url, expires_at}'
{
  "id": "bks_nO_7coiscPXBcP9k",
  "status": "requires_escalation",
  "totals": [
    { "type": "subtotal", "amount": 660000 },
    { "type": "fee", "display_text": "Cleaning fee", "amount": 90000 },
    { "type": "total", "amount": 750000 }
  ],
  "policies": [
    {
      "type": "dev.ucp.lodging.policy.cancellation",
      "refundability": "refundable",
      "description": {
        "plain": "Free cancellation until 2026-11-23. After that the stay is not refunded."
      },
      "url": "https://nordlys.example/faq"
    }
  ],
  "messages": [
    {
      "type": "error",
      "code": "buyer_confirmation_required",
      "severity": "requires_buyer_review",
      "content": "Nordlys Cabins confirms every booking with the guest. Open continue_url to review the stay and confirm it."
    }
  ],
  "continue_url": "https://nordlys.example/checkout/bks_nO_7coiscPXBcP9k",
  "expires_at": "2026-11-02T21:59:26.682Z"
}
```

(I joined each `totals` entry onto one line to save space. The values are exactly what the server sent.)

Three nights at 2,200 kroner plus the 900 kroner cleaning fee is 7,500 kroner, and in minor units that is `750000`. The message uses the severity `requires_buyer_review`, which the draft defines as “the booking session is **complete** — but policy, regulatory, or entitlement rules require user authorization before completion”.[^ch12-6] That is precisely our situation: the agent gave us everything we need, and we still want the person.

What happens when an agent calls Complete anyway? Nothing new. The route in Listing 12.3 returns the session unchanged, still `requires_escalation`, with the same `continue_url`. An agent that follows the draft knows what to do next: hand the link to the person.

**Listing 12.3** `nordlys-cabins/layers/12-commerce/index.js` (excerpt) — Complete never finalizes
```js
    // Complete never finalises: without AP2 mandates the guest confirms on our site.
    ctx.route('POST', `${base}/:id/complete`, (c) => {
      const s = sessions.get(c.req.param('id'));
      return s ? show(c, s) : notFound(c);
    });
```

### The page behind continue_url

`continue_url` opens a page on Nordlys’s own site. It shows the dates, the number of guests, the total with the cleaning fee and the time the offer expires, and it asks for the guest’s name and email and the acceptance of the terms. Listing 12.4 is the part that runs when the guest presses “Confirm and book”.

**Listing 12.4** `nordlys-cabins/layers/12-commerce/checkout.js` (excerpt) — the guest confirms
```js
  ctx.route('POST', '/checkout/:id', async (c) => {
    const s = sessions.get(c.req.param('id'));
    if (!s || s.status !== 'requires_escalation') return gone(c);
    // The form adds who is booking. What is booked comes only from the session.
    const { name, email, acceptTerms } = await c.req.parseBody();
    const result = store.createBooking({ ...s.input, name, email, acceptTerms }, { member: c.get('member') });
    if (!result.ok) return page(c, 'Review your stay', review(s, { name, email }, result.errors), 422);
    sessions.complete(s.id, result.booking);
    ctx.events.emit('booking.created', result.booking, { via: 'ucp-checkout', agent: s.agent, c });
    return page(c, 'Booking confirmed', html`<h1>Booking confirmed</h1>
      <p>Your booking reference is <strong>${result.booking.ref}</strong>.
      You can <a href="/bookings">find your booking</a> with this reference and your email.</p>`);
  });
```

Look at the comment on the first lines of the handler. The form may add who is booking, and nothing else. The cabin, the dates and the guests come only from the session the agent created and the guest just reviewed, so a tampered form cannot turn a reviewed three-night stay into a different one. The booking itself goes through `store.createBooking()`, the same function the normal booking form uses, which checks availability once more. The layer then marks the session `completed` and emits the app’s `booking.created` event with `via: 'ucp-checkout'` and the agent’s `UCP-Agent` value, so the traffic analysis in Chapter 19 can count bookings that agents prepared.

After that, a `GET` on the session returns `status: "completed"` with a `confirmation` object that carries the booking reference, and the agent can tell the person that the booking is done. Figure 12.3 shows the whole flow.

![Figure 12.3 — The agent-safe checkout for Nordlys Cabins. The agent creates a booking session and receives the all-in price, the cancellation terms and continue_url. Complete returns the same session. The guest opens continue_url on nordlys.example, reviews and confirms, the store creates the booking, and the agent reads the completed session with its confirmation.](images/figure-12-3.png)

In the demo the confirmation page is where the money would move. Nordlys’s demo store takes no payment at all. In production this step is your PSP’s hosted payment page, with whatever authentication your provider and your region require, and the booking is created when the payment succeeds.

### Testing the layer

The tests in `nordlys-cabins/tests/ch12-commerce.test.js` run in-process with `node:test`, no browser needed:

```text
$ node --test tests/ch12-*.test.js 2>&1 | grep -E '^# (tests|pass|fail)'
# tests 9
# pass 9
# fail 0
```

They check the profile, the minor-unit totals, the error messages and their paths, `inventory_exhausted` for booked dates, that Complete never finalizes, that the checkout form cannot change the stay, that a session is `canceled` after 15 minutes (with Node’s mock timers) and that the 402 route from the next section is off by default.

I also validated the JSON the layer produces against the JSON Schemas in the UCP repository at the commit we built against: the profile against the business-profile schema, the sessions against the booking schema with the cancellation-policy extension, and the error response against the error-response schema. The first run failed in three places, and every one of them was a real mistake of mine: a stay’s `totals` needs exactly one `subtotal` and one `total`, a policy `description` is an object with a `plain` member rather than a string, and a `completed` session must carry a booker with a first name, a last name and an email. That is the best argument I know for validating against a draft’s schemas: the prose of a specification is easy to misread, a schema is not. All of the JSON now validates.

## The agent-safe checkout, without any protocol

Strip away UCP’s field names and what we built is a pattern you can apply to any site, with or without a commerce protocol:

1. **The agent asks, the server quotes.** The price, the fees and the terms come from your server, computed by the same code your own pages use. Never let an agent send you a price.
2. **The quote has an identity and an expiry.** A session id, a fixed set of terms and an `expires_at`. If prices or availability change, the agent gets a new quote, never a silently different one. The UCP draft calls this out explicitly: when totals change during a session, the business reports a `totals_changed` warning, and the platform must show it.[^ch12-6]
3. **The decision happens on your page.** The person reviews exactly what the agent prepared, on your domain, in your design, under your terms. That page is also where your PSP’s payment step lives.
4. **The form can add, not change.** Whatever the confirmation page accepts must not alter the quote.
5. **The agent learns the outcome.** A machine-readable status (`completed` plus a confirmation, or `canceled`) so the agent can close the loop with the person.

The same pattern works as an MCP tool or a WebMCP tool that returns a link, as a REST endpoint from Chapter 7, or as a plain deep link to your booking form with the dates filled in. The protocol adds discoverability and a shared vocabulary. It does not add safety, because the safety comes from step 3.

### Can’t a browsing agent just press the button?

Yes, it can, and I want to be honest about it. A browsing agent (Chapter 3) that runs in the person’s own browser can open `continue_url` and click “Confirm and book”. From the server’s point of view it looks exactly like the person doing it. A protocol cannot draw the line between “the person pressed it” and “the person’s agent pressed it” on a web page. Three things still make the design worth it.

First, the browsers already treat sensitive moments as special. Chrome documents defences for its agent such as a second model that vets each action and deterministic confirmations before certain sensitive sites, and every agent vendor writes about prompt injection as an unsolved problem (Chapter 16 has the details and the sources). Second, the payment step is a separate gate. In the European Economic Area, which includes Norway, online card payments generally go through strong customer authentication under the PSD2 rules, and it happens between the cardholder and their bank, often in a banking app.[^ch12-31] How that works when an agent prepared the booking is a question for your PSP, and it is one more reason to keep the payment on your own page. Third, the page shows the person a complete, honest summary at the exact moment they decide, which is the point of the “trusted UI” wording in the draft.

What the site owner owns is making that page impossible to misunderstand: the total with every fee, the dates in words, the cancellation terms, the expiry. Chapter 17 comes back to consent and the human in the loop.

## Hands-on: a 402 for teaching

> **Hands-on:** This short section shows what an x402 “Payment Required” response looks like on the wire. It is off by default in Nordlys and never moves money. Non-coders can skip to “What the graders see”.

Nordlys doesn’t sell content, so a pay-per-request endpoint makes no business sense for it. But a 402 is easier to understand when you see one, so the layer has a teaching route, `/guide/premium/winter-routes`, that exists only when you start the app with `NORDLYS_X402_DEMO=1`. Listing 12.5 is the whole file.

**Listing 12.5** `nordlys-cabins/layers/12-commerce/x402-demo.js` — a teaching 402 response
```js
// TEACHING EXAMPLE ONLY: what an x402 V2 "402 Payment Required" response looks
// like. Nordlys sells cabin stays, not content, so this route is off by default
// (NORDLYS_X402_DEMO=1 turns it on). It never verifies or settles a payment.
const b64 = (obj) => Buffer.from(JSON.stringify(obj)).toString('base64');

export function x402Demo(ctx) {
  ctx.route('GET', '/guide/premium/winter-routes', (c) => {
    const required = {
      x402Version: 2,
      error: 'PAYMENT-SIGNATURE header is required',
      resource: {
        url: ctx.absoluteUrl(c, '/guide/premium/winter-routes'),
        description: 'Winter ski-touring routes near Nordlys cabins (teaching example)',
        mimeType: 'text/markdown',
      },
      accepts: [{
        scheme: 'exact',
        network: 'eip155:84532', // Base Sepolia, a test network: no real money
        amount: '10000', // 0.01 test USDC in atomic units (6 decimals)
        asset: '0x036CbD53842c5426634e7929541eC2318f3dCF7e',
        payTo: '0x0000000000000000000000000000000000000000',
        maxTimeoutSeconds: 60,
        extra: { name: 'USDC', version: '2' },
      }],
    };
    if (c.req.header('payment-signature')) required.error = 'This teaching demo never settles payments';
    c.header('PAYMENT-REQUIRED', b64(required));
    return c.json(required, 402);
  });
}

```

And this is the response, decoded from the `PAYMENT-REQUIRED` header:

```text
$ curl -s -i http://127.0.0.1:4512/guide/premium/winter-routes | head -1
HTTP/1.1 402 Payment Required
$ curl -s http://127.0.0.1:4512/guide/premium/winter-routes -D - -o /dev/null \
    | grep -i payment-required | cut -d' ' -f2 | tr -d '\r' | base64 -d | jq .accepts
[
  {
    "scheme": "exact",
    "network": "eip155:84532",
    "amount": "10000",
    "asset": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
    "payTo": "0x0000000000000000000000000000000000000000",
    "maxTimeoutSeconds": 60,
    "extra": {
      "name": "USDC",
      "version": "2"
    }
  }
]
```

The network and asset are the test-network values from the x402 specification’s own example, and the `payTo` address is all zeros. A real seller would use the x402 SDK’s middleware and a facilitator service that verifies and settles the payment (the x402 documentation points sellers to a test facilitator for exactly that).[^ch12-21] An MPP seller would return a `WWW-Authenticate: Payment` challenge instead.[^ch12-25] Our route does neither. If a client sends a `PAYMENT-SIGNATURE`, it just answers with another 402 that says the demo never settles payments.

## What the graders see

isitagentready.com has a Commerce category with five checks, and their published pass criteria are short:[^ch12-28]

- `ucp`: “/.well-known/ucp exists with protocol_version and services”
- `acp`: “/.well-known/acp.json exists with protocol.name, protocol.version, api_base_url, transports, and capabilities.services”
- `x402`: routes return HTTP 402 with x402 payment headers
- `mpp`: an OpenAPI document at `/openapi.json` with `x-payment-info` extensions on paid operations
- `ap2`: an AP2 extension in the A2A Agent Card (opt-in, off by default)

Cloudflare’s launch post says it checks for UCP and ACP, and the tool scores commerce checks only when it detects that a site sells things. Otherwise they show as neutral.[^ch12-29] None of them moves the isitagentready level (Chapter 11 has the ladder). The wording “protocol_version” in the `ucp` criterion does not match a field name in the specification, where the version lives at `ucp.version`, and real Shopify profiles use `ucp.version` too. I read it as a description, not a field name, and Nordlys follows the specification. I could not scan the local demo with the public tool, so the claim that Nordlys passes `ucp` rests on the published criteria and on the schema validation above, not on a scan.

The Lighthouse Agentic Browsing category has no commerce audit at all in Lighthouse 13.6.0. It looks at the page an agent sees, and for this layer the only page is the confirmation page, which is a plain, labelled form.

Table 12.2 Nordlys after Chapter 12

| Check | Before | After | Why |
|---|---|---|---|
| isitagentready `ucp` | fail or neutral | pass by the published criteria (not scanned) | `/.well-known/ucp` with `ucp.version` and `ucp.services` |
| isitagentready `acp` | fail or neutral | unchanged | Nordlys publishes no ACP document |
| isitagentready `x402` | fail or neutral | unchanged by default | the teaching route is off |
| isitagentready level | unchanged | unchanged | commerce checks do not affect the level |
| Lighthouse Agentic Browsing | unchanged | unchanged | no commerce audits |

## What to watch

> **Still in flux:** Everything in this chapter moves. These are the dates I would put in a team calendar.

- **The UCP Lodging draft’s first dated release.** Watch the specification’s changelog and the `draft` pages on ucp.dev. When it ships, replace `DRAFT_VERSION` with the release date, re-run the schema validation, and only then consider joining a platform.
- **Google’s UCP for Lodging onboarding.** Google’s partner page has a waitlist and says detailed onboarding and specs will follow.[^ch12-7]
- **AP2 at the FIDO Alliance.** If mandates become a FIDO standard and payment providers verify them for you, the “a person finishes the booking” rule can relax for low-risk bookings.
- **ACP’s direction after Instant Checkout.** Its repository is the source of truth, and its beta label tells you how stable to expect it to be.
- **The card networks’ programmes,** through your PSP and acquirer.
- **x402 and MPP,** if you sell an API or content. MPP’s IETF draft is individual for now, x402 is governed by a foundation. Chapter 15 adds pay per crawl.

## Summary

- Agent commerce has to answer four questions: what exactly is bought, did the person agree, who pays with what, and who the agent is. Ask every protocol and every vendor which of the four it answers.
- Adoption in November 2026 is a platform story. Radar found the UCP profile on 4.7% of the top domains it scanned, mostly on online shops, and ACP, MPP, x402 and AP2 on 32, 13, 7 and 4 domains.
- UCP publishes a business profile at `/.well-known/ucp` with dated versions, services, capabilities and payment handlers. Every entry is a promise that scanners and platforms will try to use.
- The UCP Lodging draft (`dev.ucp.lodging.booking`) is the first commerce standard written for booking sites. It models booking sessions with stays, all-in totals in minor units, cancellation policies, expiry and a `continue_url`, and without AP2 mandates it requires a person to finalize the booking.
- ACP (OpenAI and Stripe, beta) and AP2 (mandates, version 0.2, donated to FIDO) cover checkout and proof of consent, the card networks build on Web Bot Auth, and x402 and MPP revive HTTP 402 for pay-per-request.
- For a small site the realistic path is an agent-safe checkout: the server quotes, the quote expires, the person decides and pays on your own page, the form cannot change the quote, and the agent can read the outcome.
- Nordlys’s `12-commerce` layer implements that path in the Lodging draft’s shape, validates against the draft’s schemas, and marks every draft part so no platform negotiates with it by accident.
- isitagentready’s commerce checks are scored only for sites that sell, and they never move the level. Lighthouse has no commerce audit.

[^ch12-1]: “AI Insights: Adoption of AI agent standards”, Cloudflare Radar, https://radar.cloudflare.com/ai-insights#adoption-of-ai-agent-standards, data dated 2 November 2026, including the Ecommerce and Travel domain categories (retrieved November 2026).
[^ch12-2]: Business profiles served at https://www.allbirds.com/.well-known/ucp and https://kith.com/.well-known/ucp, fetched 2 November 2026. Shopify’s default profile was first observed by this book’s research on allbirds.com, brooklinen.com and kith.com (retrieved November 2026).
[^ch12-3]: “Universal Commerce Protocol”, ucp.dev, https://ucp.dev/ (retrieved November 2026).
[^ch12-4]: “Overview”, Universal Commerce Protocol specification, https://ucp.dev/specification/overview/ (retrieved November 2026).
[^ch12-5]: Universal-Commerce-Protocol/ucp, GitHub, https://github.com/Universal-Commerce-Protocol/ucp, release v2026-08-25 and commit c9a1395 “feat: Introduce Lodging Booking Capability and Cancellation Policy Extension (#780)”, 24 September 2026 (retrieved November 2026).
[^ch12-6]: “Booking Capability”, Universal Commerce Protocol specification (draft), https://ucp.dev/draft/specification/lodging/booking/, read at repository commit 58c7ab9 of 31 October 2026 (retrieved November 2026).
[^ch12-7]: “Google Universal Commerce Protocol (UCP) for Lodging”, Google for Developers, https://developers.google.com/hotels/ucp (retrieved November 2026).
[^ch12-8]: “Google Plans To Adopt UCP Draft Spec For AI Mode Hotel Booking”, Search Engine Journal, https://www.searchenginejournal.com/google-plans-to-adopt-ucp-draft-spec-for-ai-mode-hotel-booking/591235/ (retrieved November 2026). Secondary source.
[^ch12-9]: “Booking Capability: REST Binding” and “MCP Binding”, Universal Commerce Protocol specification (draft), https://ucp.dev/draft/specification/lodging/booking/rest/ and https://ucp.dev/draft/specification/lodging/booking/mcp/ (retrieved November 2026).
[^ch12-10]: agentic-commerce-protocol/agentic-commerce-protocol, GitHub, https://github.com/agentic-commerce-protocol/agentic-commerce-protocol (retrieved November 2026).
[^ch12-11]: “Agentic Commerce Protocol”, agenticcommerce.dev, https://www.agenticcommerce.dev/ (retrieved November 2026).
[^ch12-12]: “RFC: Agentic Checkout — Discovery” and changelog 2026-04-17, Agentic Commerce Protocol repository, https://github.com/agentic-commerce-protocol/agentic-commerce-protocol/blob/main/rfcs/rfc.discovery.md (retrieved November 2026).
[^ch12-13]: “OpenAI revamps shopping experience in ChatGPT after Instant Checkout”, CNBC, https://www.cnbc.com/2026/03/24/openai-revamps-shopping-experience-in-chatgpt-after-instant-checkout.html, 24 March 2026, read through a search summary (retrieved November 2026). Secondary source.
[^ch12-14]: “Agent Payments Protocol (AP2)”, ap2-protocol.org, https://ap2-protocol.org/ (retrieved November 2026).
[^ch12-15]: “Checkout Mandate” and “Payment Mandate”, AP2 documentation, https://ap2-protocol.org/ap2/checkout_mandate/ and https://ap2-protocol.org/ap2/payment_mandate/ (retrieved November 2026).
[^ch12-16]: “UCP and AP2”, Universal Commerce Protocol documentation, https://ucp.dev/documentation/ucp-and-ap2/ (retrieved November 2026).
[^ch12-17]: “Getting Started - Trusted Agent Protocol”, Visa Developer, https://developer.visa.com/docs/trusted-agent-protocol (retrieved November 2026).
[^ch12-18]: “Helping AI agents transact with Visa and Mastercard”, The Cloudflare Blog, https://blog.cloudflare.com/secure-agentic-commerce, 24 October 2025 (retrieved November 2026).
[^ch12-19]: “Launching the x402 Foundation with Coinbase”, The Cloudflare Blog, https://blog.cloudflare.com/x402, 23 September 2025, read through a search result (retrieved November 2026).
[^ch12-20]: “Linux Foundation Announces Operational Launch of x402 Foundation”, x402.org, https://x402.org/linux-foundation-announces-operational-launch-of-x402-foundation-to-standardize-internet-native-payments-for-ai-agents-and-applications/, and “x402 Foundation”, Coinbase Developer Documentation, https://docs.cdp.coinbase.com/x402/support/x402-foundation (retrieved November 2026).
[^ch12-21]: “HTTP 402”, x402 documentation, https://docs.x402.org/core-concepts/http-402 (retrieved November 2026).
[^ch12-22]: “x402 Protocol Specification v2”, x402-foundation/x402, GitHub, https://github.com/x402-foundation/x402/blob/main/specs/x402-specification-v2.md, section 5.1 (retrieved November 2026).
[^ch12-23]: “MPP”, Stripe Documentation, https://docs.stripe.com/payments/machine/mpp (retrieved November 2026).
[^ch12-24]: “Introducing the Machine Payments Protocol”, Stripe blog, https://stripe.com/blog/machine-payments-protocol, 18 March 2026, read through a search result and confirmed by Fortune, https://fortune.com/2026/03/18/stripe-tempo-paradigm-mpp-ai-payments-protocol/ (retrieved November 2026).
[^ch12-25]: “HTTP 402” and “Challenges”, MPP documentation, https://mpp.dev/protocol/http-402 and https://mpp.dev/protocol/challenges, and the MPP blog at https://mpp.dev/ (retrieved November 2026).
[^ch12-26]: “The ‘Payment’ HTTP Authentication Scheme”, draft-httpauth-payment-01, IETF Datatracker, https://datatracker.ietf.org/doc/draft-httpauth-payment/ (retrieved November 2026).
[^ch12-27]: Layer `nordlys-cabins/layers/12-commerce/`, webmaxru/agent-ready-web-demos, GitHub, https://github.com/webmaxru/agent-ready-web-demos (retrieved November 2026).
[^ch12-28]: “llms-full.txt”, isitagentready.com, https://isitagentready.com/llms-full.txt, checks 19 to 23 (retrieved November 2026).
[^ch12-29]: “Introducing the Agent Readiness score. Is your site agent-ready?”, The Cloudflare Blog, https://blog.cloudflare.com/agent-readiness/, 17 April 2026, and the isitagentready.com scan API description (retrieved November 2026).
[^ch12-30]: “Agentic token framework: Driving trusted AI transactions”, Mastercard, https://www.mastercard.com/global/en/news-and-trends/stories/2025/agentic-commerce-framework.html, read through a search summary (retrieved November 2026).
[^ch12-31]: “Regulatory Technical Standards on strong customer authentication and secure communication under PSD2”, European Banking Authority, https://www.eba.europa.eu/regulation-and-policy/payment-services-and-electronic-money/regulatory-technical-standards-on-strong-customer-authentication-and-secure-communication-under-psd2 (retrieved November 2026).
