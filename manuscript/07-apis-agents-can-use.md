# Chapter 7: APIs agents can use

This chapter covers

- When a plain HTTP API is all an agent needs, and when it is not enough
- Describing an API so a model picks the right operation: OpenAPI 3.1, operation ids and descriptions
- Errors, retries and limits that agents can act on: problem details, idempotency keys, pagination and RateLimit headers
- Arazzo workflows and the API catalog at `/.well-known/api-catalog`
- How agent platforms consume OpenAPI in November 2026, from Copilot Studio to gateways that turn REST into MCP
- Building the Nordlys public API and checking it with real tools

Part 2 was about being found and read. An agent that can read every cabin page on Nordlys Cabins still cannot book anything. To book, it has to fill in a form like a person (Chapter 3 showed how fragile that is), or it needs a door built for software. Part 3 is about those doors, and this chapter opens with the oldest one we have: a plain HTTP API.

Why start with something so unfashionable? Because most of the newer agent interfaces stand on top of it. The MCP server we build in Chapter 8 calls the same functions as this API. The gateways from Microsoft and AWS that turn existing services into MCP tools read OpenAPI files. Google's agent toolkit and Microsoft Copilot Studio still take an OpenAPI description directly. And an API is the only interface in this part of the book that every programming language, every agent framework and every developer on your team already knows how to call.

There is a catch, of course. An API that is fine for a developer who reads the docs once and writes a client can be quite hostile to a model that reads the description at run time and improvises. A vague operation name, an error that says only "Bad Request", a POST that books twice when the network hiccups: a human developer works around these. An agent repeats them at machine speed.

So this chapter is about the small, mostly boring design decisions that make an API safe for an agent to call. We build the Nordlys public API layer by layer: five operations, an OpenAPI 3.1 description, problem details for every error, an `Idempotency-Key` on bookings, RateLimit headers, an Arazzo workflow and an API catalog that tells any client where all of this lives. At the end, the isitagentready.com `apiCatalog` check passes, and the `linkHeaders` check has one more good reason to pass.

> **Note:** Product managers and architects, the first two sections are for you. They answer "do we need an API for agents, and what does it cost us?" The code sections are marked with a Hands-on callout, and the prose around each listing says in plain words what the code achieves.

## When a plain API is enough

Let's start with the decision, not the code. A team that wants agents to do things on its site has, in November 2026, roughly four kinds of interface to choose from:

- the human interface itself (agents simply click, as in Chapter 3),
- a plain HTTP API described with OpenAPI,
- an MCP server (Chapter 8),
- tools registered inside the page with WebMCP (Chapter 9).

Chapter 13 compares all of them properly. Here I want to answer a narrower question: when is a plain API enough?

In my experience, a plain API is enough when three things are true. First, the agent runs somewhere a developer configured it: an agent framework in your partner's backend, a Copilot Studio agent in a customer's company, a script someone wrote with an LLM in the loop. Somebody made a decision to integrate with you and pointed the agent at your OpenAPI file. Second, the task is a short sequence of well-defined operations (search, check, book) rather than an open conversation. Third, authentication is either not needed (public data) or handled by that developer, with an API key or an OAuth client they registered.

A booking site like Nordlys fits this quite well for one audience: travel agencies, trip planners and corporate travel tools that want to show Nordlys cabins next to hotels. For them, a clean public API is the right product, and an MCP server would add nothing they need.

A plain API is not enough when the agent was not configured for you. A person using a general assistant (Claude, ChatGPT, Copilot, Gemini) does not paste your OpenAPI URL anywhere. Those assistants connect to MCP servers, or they use a browser. That is the job of Chapters 8 and 9.

### What an API costs you

Product managers usually ask me the next question right away: what does it cost? The honest answer is that the code is the cheap part. In the Nordlys demo, the routes are under a hundred lines, because they call domain functions the website already had. The real costs sit around the code:

- **A contract you keep.** Once an agent platform imports your description, every rename breaks somebody you have never met. You need versioning rules (we come back to them later in this chapter).
- **Documentation that stays true.** The OpenAPI file is documentation that machines act on. A stale description is worse than none, because agents believe it.
- **Abuse handling.** A public API is an invitation to scrapers as well as to good agents. You need limits, monitoring and a way to tell callers apart (Chapter 15).
- **Support.** Somebody has to answer when a partner's agent books the wrong dates. Problem details with stable codes make those conversations much shorter.

None of this is special to agents. It is the normal cost of a public API. What agents change is the audience: you no longer design only for developers who read your guide, but also for models that read your description at run time and act on it without asking anyone.

Bottomline: the API is the foundation, not the whole house. Build it well, because everything else in Part 3 calls into the same logic.

### What changed for OpenAPI and agents in 2026

You may remember the first wave of "ChatGPT reads your OpenAPI file" in 2023 and 2024: Custom GPTs with Actions, where you pasted an OpenAPI description and the model called your API. Please treat that advice as history. OpenAI's help center lists 11 December 2026 as the scheduled retirement of Custom GPTs, and the trade press reports that Custom Actions do not carry over to the plugins that replace them, which are built on MCP.[^ch07-1] I could only read the OpenAI page as a search result (the page itself refused my requests), so check the date before you plan around it.

At the same time, OpenAPI became more important in a different role: as the input to gateways. Two examples, one from each big cloud:

- Azure API Management can expose operations of an existing REST API as tools on a remote MCP server, without changing the API.[^ch07-2]
- Amazon Bedrock AgentCore Gateway accepts OpenAPI, Smithy and Lambda functions as tool sources and serves them to agents over MCP.[^ch07-3]

And some agent platforms still read OpenAPI directly. Microsoft Copilot Studio creates REST API tools from an OpenAPI file (a preview feature that converts the description to OpenAPI v2 internally), and Google's Agent Development Kit has an `OpenAPIToolset` that generates callable tools from any OpenAPI 3.x description.[^ch07-4]

What does this mean for you? Whatever path an agent takes to your service, there is a good chance that a machine reads your OpenAPI description and turns each operation into something a model chooses from. Every `operationId`, `summary` and `description` becomes part of a prompt. That is the main idea of this chapter, and we come back to it again and again.

## The Nordlys API at a glance

Before we look at any design rule, let's see what we are building. The Nordlys public API has five operations under `/api/v1`, plus a health endpoint. Each one maps to a question a guest (or an agent acting for a guest) actually asks:

| Operation | HTTP | What it answers |
|---|---|---|
| `searchCabins` | `GET /api/v1/cabins` | Which cabins fit my group, region, dates and wishes? |
| `getCabin` | `GET /api/v1/cabins/{slug}` | Tell me everything about this cabin. |
| `checkAvailability` | `GET /api/v1/cabins/{slug}/availability` | Is it free for these dates, and what is the total? |
| `createBooking` | `POST /api/v1/bookings` | Book it for this person. |
| `cancelBooking` | `POST /api/v1/bookings/{ref}/cancel` | Cancel my booking. |

Around these sit the files that describe them: `/openapi.json`, an Arazzo workflow at `/api/v1/booking.arazzo.json`, a short Markdown page for developers at `/developers.md`, one page per error type under `/problems/`, and the API catalog at `/.well-known/api-catalog`. Figure 7.1 shows how they fit together.

![Figure 7.1 — The Nordlys API layer. Five operations share one booking service with the MCP server of Chapter 8. Around them, the description files point at each other, and the API catalog is the entry point that a client finds from the home page's Link header.](images/figure-7-1.png)

Please note the box in the middle of the figure: the booking service. It is a thin module that wraps the shared domain functions of the demo app (search, availability, booking) and adds what an API needs on top, such as idempotency. The HTTP routes call it. In Chapter 8, the MCP tools call the very same module. There is exactly one place where a booking is created, whatever door the request came through.

> **Tip:** If your site already has an internal API for its own front end, start from that. The front end and agents often need the same operations, and one code path is easier to secure, test and log than two.

### Why OpenAPI 3.1 and not 3.2

The OpenAPI Initiative published OpenAPI 3.2.0 on 19 September 2025 and a patch, 3.2.1, on 10 September 2026.[^ch07-5] Version 3.2 adds useful things, among them hierarchical tags, the HTTP `QUERY` method and better support for streaming responses. So why does Nordlys use 3.1?

Because of the consumers. The whole point of this description is that other tools read it, and in November 2026 tool support for 3.2 is uneven. Copilot Studio converts whatever it gets to v2. Google's ADK documentation says "v3.x" without listing 3.2 features. The validator I used for this chapter handles 3.1 fully. I did not find any survey of 3.2 support across agent platforms, so this is my judgment rather than a measured fact: 3.1 is the safer target today, and nothing in the Nordlys API needs a 3.2 feature. The demo uses the latest 3.1 patch, 3.1.2.

When your gateway and your agent platforms document 3.2 support, switching is mostly a version string and a few optional improvements. That is a nice property of the 3.x line.
### Try it yourself

> **Hands-on:** A short terminal session against the demo app. If you don't use a terminal, the two responses below show what an agent gets back, and you can continue with "Describing operations so a model chooses well".

Start the demo with the layers up to this chapter and ask for a cabin with a sauna for four people, from 2 to 5 December 2026:

```bash
cd nordlys-cabins
npm install
npm start -- --upto=7 --port=4710
curl -s "http://localhost:4710/api/v1/cabins?features=sauna&guests=4&checkIn=2026-12-02&checkOut=2026-12-05"
```

The answer has one cabin, Lyngen Lysthus, with its rates and a link to its page (I shortened the JSON a bit):

```json
{"data":[{"slug":"lyngen-lysthus","name":"Lyngen Lysthus","region":"Lyngen","maxGuests":4,"features":["sauna","hot-tub","wifi","aurora-view"],"nightlyRate":3400,"weekendRate":3900,"cleaningFee":1200,"currency":"NOK","minNights":3,"page":"/cabins/lyngen-lysthus"}],"total":1,"links":{"self":"/api/v1/cabins"}}
```

Now ask for the exact price with `curl -s "http://localhost:4710/api/v1/cabins/lyngen-lysthus/availability?checkIn=2026-12-02&checkOut=2026-12-05&guests=4"`:

```json
{"cabin":"lyngen-lysthus","checkIn":"2026-12-02","checkOut":"2026-12-05","guests":4,"available":true,"conflicts":[],"quote":{"currency":"NOK","nights":3,"accommodation":10700,"cleaningFee":1200,"total":11900}}
```

Two weekday nights at 3,400 NOK, one Friday night at 3,900 NOK and the cleaning fee: 11,900 NOK. Nothing here needs a model to understand. That is the point. An agent gets numbers it can repeat to a person without inventing anything.

## Describing operations so a model chooses well

> **Hands-on:** This section shows the OpenAPI description of the booking operation and explains each part a model reads. If you don't write code, the idea is simple: every name and sentence in the API description is read by a model that has to choose an operation and fill in its fields, so we write them for that reader. Pick up again at "Errors an agent can act on" if you want to skip the listing.

Let's have a look at what a model actually sees when a platform imports an OpenAPI file. Copilot Studio, ADK and the MCP gateways all do roughly the same thing: each operation becomes a tool, the `operationId` (or a cleaned-up version of it) becomes the tool name, the `summary` and `description` become the tool description, and the parameters and request body become the tool's input schema. The model never sees your nice developer portal. It sees these strings, side by side with the tools of every other service the agent is connected to.

![Figure 7.2 — How an imported OpenAPI operation becomes a tool. The operationId becomes the tool name, the summary and description become the tool description, and the parameters and request body become one input schema. Everything on the right side is what the model reads when it decides what to call.](images/figure-7-2.png)

That gives us a few rules, and I apply all of them in the Nordlys description:

- **An `operationId` on every operation, written as a verb and a noun.** `createBooking` is a good tool name. `postApiV1Bookings` (what some generators produce when the id is missing) is not.
- **A `summary` that says what the operation does, in one line.** This is often the only text shown in a list of tools.
- **A `description` that says when to use it, what to do before it, and what not to do.** This is the place for instructions such as "only call this after the user confirmed the price".
- **Enumerations instead of free text** wherever the set of values is known. Nordlys generates the list of regions and features from its data, so a model cannot invent a region that does not exist.
- **Descriptions on every non-obvious field,** with the format and an example.

Listing 7.1 shows the booking operation as Nordlys describes it.

**Listing 7.1** `nordlys-cabins/layers/07-public-api/openapi.js` — the createBooking operation (excerpt)

```js
      '/bookings': {
        post: {
          operationId: 'createBooking',
          tags: ['bookings'],
          summary: 'Book a cabin for the lead guest',
          description:
            'Only call this after the user has confirmed the cabin, the dates and the price from checkAvailability. ' +
            'Send a new Idempotency-Key (a UUID) for every new booking, and the same key again if you retry after a timeout: ' +
            'a retry with the same key and body returns the original booking with status 200 instead of booking twice.',
          parameters: [{ $ref: '#/components/parameters/IdempotencyKey' }],
          requestBody: {
            required: true,
            content: { 'application/json': { schema: { $ref: '#/components/schemas/BookingRequest' } } },
          },
          responses: {
            201: { description: 'The booking was created.', headers: rateHeaders, content: { 'application/json': { schema: { $ref: '#/components/schemas/Booking' } } } },
            200: { description: 'A retry of an earlier request with the same Idempotency-Key. The body is the original booking.', content: { 'application/json': { schema: { $ref: '#/components/schemas/Booking' } } } },
            400: problemRef('The Idempotency-Key header is missing.'),
            409: problemRef('The cabin was taken for those dates, or a request with this Idempotency-Key is still running.'),
            422: problemRef('A field is invalid, or the Idempotency-Key was already used for a different request.'),
            429: tooMany,
          },
        },
      },
```

A few details deserve a comment.

The `description` is written for a model as much as for a developer: "Only call this after the user has confirmed the cabin, the dates and the price from checkAvailability." This sentence does real work. When a platform turns operations into tools, the model sees the description of each tool it might call, while a general "about this API" text may never reach the prompt at all. So the instruction belongs on the risky operation itself. (Chapter 10 shows how to test whether models actually follow such instructions.)

Every response the operation can return is listed, including the errors, and each error response says when it happens. An agent that gets a 409 can look up what 409 means for this operation: the cabin was taken, or a request with the same key is still running. That is the difference between an agent that retries blindly and one that does the right thing.

The request body schema (not shown in the excerpt, it lives under `components`) marks `acceptTerms` with `const: true` and the description "The user accepted the booking terms at /faq. Never set this without asking." A schema cannot force a model to ask the user. What it can do is make the honest path the only valid one and say clearly what is expected. The server checks the value too, of course.

> **Warning:** Do not put secrets, internal notes or anything you would not show a stranger into an OpenAPI description. Agents copy descriptions into prompts and logs, and some platforms show them to end users. The description is public documentation.

### Validate the description in CI

An OpenAPI file that is invalid fails silently in many tools: the import shows fewer operations, or a parameter disappears. So the Chapter 7 tests load `/openapi.json` from the app and validate it with `@scalar/openapi-parser` (version 0.29.19 when I wrote this).[^ch07-6] The validator is a development dependency, and the test skips itself with a clear message when it is not installed. The validator caught one real mistake while I built the layer: I had combined a `$ref` to a shared parameter with an extra `required: true` next to it, which OpenAPI 3.1 does not allow for parameter references. The fix was to inline those parameters.

The test also checks that every operation has an `operationId`, a `summary` and a `description`. That is a tiny check, but it protects the most important thing in the file from the next person who adds an endpoint in a hurry.

## Errors an agent can act on

Picture this. An agent asks for Fjellro, a mountain cabin in Rondane, for twelve guests. Fjellro sleeps six. The API answers `400 Bad Request` with the body `{"error":"invalid"}`. What does the agent do now? It guesses. It might try again with the same input, it might tell the user that the site is broken, or it might try a different cabin without saying why.

A good error message for an agent has the same parts as a good error message for a person: what went wrong, where, and what to do about it. There is a standard for exactly this. RFC 9457, "Problem Details for HTTP APIs" (it replaced RFC 7807 in 2023), defines a JSON object with the media type `application/problem+json` and five standard members: `type` (a URI that identifies the kind of problem), `title`, `status`, `detail` and `instance`.[^ch07-7] You may add your own members, called extensions.

Here is the real response from the Nordlys API to that request (I removed the rate-limit headers, which we discuss later):

```http
HTTP/1.1 422 Unprocessable Content
Content-Type: application/problem+json

{
  "type": "https://nordlys.example/problems/invalid-request",
  "title": "The request has invalid fields",
  "status": 422,
  "detail": "Fjellro sleeps up to 6 guests.",
  "instance": "/api/v1/cabins/fjellro/availability",
  "errors": [
    {
      "field": "guests",
      "code": "too_many_guests",
      "detail": "Fjellro sleeps up to 6 guests."
    }
  ]
}
```

What makes this usable for an agent?

- **The status code is honest.** 422 means "I understood the request, but the content is wrong." 404 means the cabin does not exist, 409 means a conflict with the current state (already booked, already cancelled). Agents and their frameworks branch on the status before they read anything else.
- **The `type` is stable and resolves.** `https://nordlys.example/problems/invalid-request` is a real page. Nordlys serves a short Markdown explanation for every problem type, so an agent (or a developer) that has never seen this error can fetch the URI and learn what it means.
- **The `errors` extension lists every field problem** with a machine-readable `code` and a human-readable `detail`. The code is what an agent branches on (`too_many_guests` means "suggest a bigger cabin or split the group"). The detail is what it can say to the person.
- **The detail is a sentence a person can read.** "Fjellro sleeps up to 6 guests." works when an assistant passes it on word for word.

Nordlys defines nine problem types. Here they are with their status codes, because choosing the status code is the part teams most often argue about:

| Problem type | Status | When |
|---|---|---|
| `invalid-request` | 422 | One or more fields are invalid (dates, guests, email, terms) |
| `unknown-cabin` | 404 | No cabin with that slug |
| `not-available` | 409 | The cabin is taken for some of those nights |
| `not-found` | 404 | No booking matches that reference and email |
| `already-cancelled` | 409 | The booking was cancelled before |
| `stay-started` | 409 | The stay has started, it can no longer be cancelled online |
| `idempotency-key-missing` | 400 | A booking request without an `Idempotency-Key` |
| `idempotency-key-reused` | 422 | The key was used before for a different request |
| `idempotency-key-in-flight` | 409 | A request with this key is still being processed |

The `errors` array with `field`, `code` and `detail` is my own extension. RFC 9457 shows a very similar shape in one of its examples, but it does not standardize it, so document it in your OpenAPI description (Nordlys has a `Problem` schema under `components`).

> **Tip:** IANA keeps a registry of HTTP problem types that are shared between APIs.[^ch07-8] Before you invent a type for a common situation, look there first. We use one registered type in the next section, for rate limits.

### The same errors through every door

There is one more design decision hidden here. The booking service returns errors as plain data, `{ field, code, message }`, and each door renders them in its own format. The HTTP API turns them into problem details. The MCP tools of Chapter 8 turn them into a tool result marked as an error, with text like `guests: Fjellro sleeps up to 6 guests. (too_many_guests)`. The codes are identical. When you read your logs later, or write the tool evaluations of Chapter 10, a `too_many_guests` is a `too_many_guests` wherever it came from.
## Retries without double bookings

> **Hands-on:** After the explanation of idempotency keys, this section shows the booking route and the shared booking service. If you don't write code, read up to the first listing and then jump to the real exchange near the end of the section: it shows a retry returning the same booking instead of a second one. The next section is "Cancelling is a different kind of operation".

Networks fail. An agent sends `POST /api/v1/bookings`, the connection drops after the server created the booking but before the response arrived, and the agent sees a timeout. What now? If it retries, the guest may get two bookings and two charges. If it gives up, the guest may think nothing was booked and book somewhere else, while Nordlys holds a cabin for them.

People solve this by looking at their email. Agents need a protocol. The common answer is an idempotency key: the client generates a unique value for each logical operation (a UUID is typical) and sends it in a header. If the server sees the same key again with the same request, it does not repeat the operation. It returns the result of the first attempt.

Payment APIs have done this for years, and the IETF HTTPAPI working group is standardizing the header. The current version as I write this is draft-ietf-httpapi-idempotency-key-header-08 from October 2026.[^ch07-9] It defines the `Idempotency-Key` request header as a Structured Field string, so the value is quoted:

```http
Idempotency-Key: "8e03978e-40d5-43e8-bc93-6894a57f9324"
```

> **Still in flux:** `Idempotency-Key` is an Internet-Draft, not an RFC, as of November 2026. The idea is stable and widely deployed (Stripe and many other payment APIs use the same header name).[^ch07-10] Details such as the error codes for reused keys may still change. Nordlys follows draft 08 and accepts the value with or without quotes, because many clients send it bare.

The draft also describes how a server should behave in the tricky cases, and Nordlys follows that guidance:

- **No key on an operation that requires one:** 400 Bad Request.
- **The same key with a different request body:** 422, because that is almost certainly a client bug. The server recognizes "the same request" by a fingerprint, a hash of the significant fields.
- **The same key while the first request is still running:** 409 Conflict. The client should wait and retry.
- **The same key with the same body after success:** the original response again.

Figure 7.3 shows the case that matters most, a timeout followed by a retry.

![Figure 7.3 — A retry with the same Idempotency-Key. The first request books the cabin, but the response is lost. The agent retries with the same key, and the server returns the stored booking with status 200 instead of booking a second time.](images/figure-7-3.png)

Listing 7.2 shows the HTTP side. It is short on purpose: the route reads the header and the body, hands both to the booking service, and translates the answer.

**Listing 7.2** `nordlys-cabins/layers/07-public-api/api.js` — the booking route (excerpt)

```js
  // POST /api/v1/bookings  (requires an Idempotency-Key header)
  ctx.route('POST', '/api/v1/bookings', async (c) => {
    const input = await c.req.json().catch(() => null);
    if (!input || typeof input !== 'object' || Array.isArray(input))
      return problem(c, ctx, 'invalid-request', { detail: 'Send the booking as a JSON object.' });
    const key = c.req.header('idempotency-key')?.replace(/^"|"$/g, '');
    const r = service.createBooking(input, { idempotencyKey: key, via: 'api', member: c.get('member'), c });
    if (!r.ok) return problemFromErrors(c, ctx, r.errors);
    return c.json(r.value, r.replayed ? 200 : 201);
  });
```

Please note the last line. A first, successful booking returns 201 Created. A replay returns 200 OK with the same body. The OpenAPI description says exactly this, so an agent can tell "I booked it now" from "you already booked it with this key".

The interesting part lives in the booking service, which the MCP tools share. Listing 7.3 is its `createBooking` function.

**Listing 7.3** `nordlys-cabins/layers/07-public-api/service.js` — idempotent booking in the shared service (excerpt)

```js
  function createBooking(input, { idempotencyKey, via, member = null, c = null } = {}) {
    if (!idempotencyKey) return fail('idempotency_key_missing', 'idempotencyKey', 'Send an idempotency key (a fresh UUID) with every booking request.');
    const now = Date.now();
    for (const [k, v] of keys) if (v.expires < now) keys.delete(k);
    const fingerprint = fingerprintOf(input);
    const seen = keys.get(idempotencyKey);
    if (seen) {
      if (seen.fingerprint !== fingerprint)
        return fail('idempotency_key_reused', 'idempotencyKey', 'This idempotency key was already used for a different booking request. Use a new key.');
      if (!seen.done) return fail('idempotency_key_in_flight', 'idempotencyKey', 'A request with this idempotency key is still being processed. Retry in a moment.');
      return { ...seen.result, replayed: true };
    }
    keys.set(idempotencyKey, { fingerprint, done: false, expires: now + IDEMPOTENCY_TTL_MS });
    const r = store.createBooking({ ...input, acceptTerms: input.acceptTerms === true }, { member });
    const result = r.ok ? { ok: true, value: publicBooking(r.booking) } : { ok: false, errors: r.errors };
    if (r.ok) {
      keys.set(idempotencyKey, { fingerprint, done: true, result, expires: now + IDEMPOTENCY_TTL_MS });
      ctx.events.emit('booking.created', r.booking, { via, c });
    } else {
      keys.delete(idempotencyKey); // a rejected request may be corrected and sent again with the same key
    }
    return result;
  }
```

Let's walk through it. The service drops expired keys (Nordlys remembers them for 24 hours), computes the fingerprint of the input and looks the key up. A known key with a different fingerprint is refused. A known key whose first request has not finished yet is refused with "still being processed". A known, finished key returns the stored result with a `replayed` flag. Only an unknown key reaches `store.createBooking`, and the key is recorded *before* the booking is attempted, so two parallel requests with the same key cannot both get through.

One decision is worth discussing with your team: what happens to the key when the booking fails? Nordlys deletes it, so the client can fix the input (say, a typo in the email) and send it again with the same key. The draft leaves room for both approaches. Personally for me, forgiving a corrected retry is friendlier to agents, which often fix one field at a time.

> **Warning:** This demo keeps idempotency keys in memory, which works for one server process. With several instances behind a load balancer, the keys must live in shared storage (Redis, a database table with a unique constraint, or your platform's key-value store), or a retry that lands on another instance books twice.

Here is the real exchange from the demo. The first request books, the replay returns the same booking, and a second attempt that reuses the key for three guests instead of four is refused:

```http
POST /api/v1/bookings
Idempotency-Key: "8e03978e-40d5-43e8-bc93-6894a57f9324"

HTTP 201
{"ref":"NC-MHFD9D","status":"confirmed","cabin":"fjellro","checkIn":"2026-12-02","checkOut":"2026-12-05","guests":4,"name":"Kari Nordmann","total":7900,"currency":"NOK","freeCancellationUntil":"2026-11-18","page":"/bookings/NC-MHFD9D"}

POST /api/v1/bookings   (same key, same body)

HTTP 200
{"ref":"NC-MHFD9D", ... the same booking ...}

POST /api/v1/bookings   (same key, "guests": 3)

HTTP 422
{"type":"https://nordlys.example/problems/idempotency-key-reused", ...}
```

The booking reference is random, so yours will differ. The total is not: three nights in Fjellro from 2 to 5 December 2026 cost 7,000 NOK plus a 900 NOK cleaning fee, and free cancellation ends on 18 November, 14 days before check-in.

### Cancelling is a different kind of operation

Booking creates something, so it needs a key to stay safe on retries. Cancelling destroys something, so it needs a different kind of care: proof of ownership and a clear answer when there is nothing left to do.

`POST /api/v1/bookings/{ref}/cancel` takes the email address the booking was made with. A wrong email gets the same answer as a wrong reference (`404`, `not-found`), so nobody can probe which references exist. A correct one cancels and reports the refund:

```json
{"ref":"NC-RJJPT4","status":"cancelled","cabin":"fjellro","checkIn":"2026-12-02","checkOut":"2026-12-05","guests":4,"name":"Kari Nordmann","total":7900,"currency":"NOK","freeCancellationUntil":"2026-11-18","refund":7900,"page":"/bookings/NC-RJJPT4"}
```

And a second cancel of the same booking returns `409` with the type `already-cancelled`. That is idempotent in the sense that matters (the state does not change, nothing is refunded twice), and the agent learns that the job was already done, which is useful when a retry follows a timeout.

The OpenAPI description of `cancelBooking` starts with "Cancelling cannot be undone. Ask the user to confirm first." I would like to tell you that every agent respects such sentences. They do not, and that is why Chapters 10 and 17 talk about confirmations that do not depend on the model's good manners. Still, the sentence costs nothing, and it is the first line of defense.

## Lists that end, and limits that explain themselves

Two more habits make an API pleasant for agents: pagination that a model cannot get wrong, and rate limits that say what they are.

### Pagination with opaque cursors

Nordlys has six cabins, so pagination is a bit theatrical here. A real site has hundreds of listings, and an agent that asks for "all cabins" should not get a 4 MB response that eats its context window. So `searchCabins` returns at most 20 items (10 by default) and a `links.next` URL when there is more:

```json
{"data":[ ... two cabins ... ],"total":6,"links":{"self":"/api/v1/cabins","next":"/api/v1/cabins?guests=2&limit=2&cursor=eyJvIjoyfQ"}}
```

Three small choices help a model here. The response carries `total`, so the agent knows how much is left without fetching everything. The `next` link is complete, with all filters included, so the agent follows it as is instead of building a URL. And the cursor is opaque (base64url-encoded JSON, to be precise), and the OpenAPI description says "Opaque cursor from links.next. Do not build it yourself." Models love to "help" by computing `page=2` or `offset=10` themselves. An opaque cursor removes the temptation, and an invalid one returns a problem detail with the code `invalid_cursor`.

### RateLimit headers

Every API needs limits, and agents hit them more often than people because they are fast and they parallelize. A 429 Too Many Requests with no explanation leads to the worst behavior: immediate retries, which make the overload worse.

The IETF HTTPAPI working group has a draft for this too: draft-ietf-httpapi-ratelimit-headers-11 (May 2026) defines two response header fields.[^ch07-11] `RateLimit-Policy` describes the quota (`q`, the number of requests, and `w`, the window in seconds), and `RateLimit` says how much of it is left (`r`, remaining) and when it resets (`t`, seconds). Both are Structured Fields with a named policy. Here is what Nordlys sends on an ordinary request:

```http
RateLimit-Policy: "default";q=60;w=60
RateLimit: "default";r=57;t=60
```

When the quota is used up, Nordlys answers with 429, a `Retry-After` header and a problem detail of the registered type `quota-exceeded`. Here is the real response with the quota set to two requests per minute (the layer reads the quota from the `NORDLYS_API_QUOTA` environment variable, which makes this easy to test):

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/problem+json
Retry-After: 60
RateLimit-Policy: "default";q=2;w=60
RateLimit: "default";r=0;t=60

{
  "type": "https://iana.org/assignments/http-problem-types#quota-exceeded",
  "title": "Request cannot be satisfied as assigned quota has been exceeded",
  "status": 429,
  "detail": "This client used its 2 requests for the current 60-second window. Retry after 60 seconds.",
  "violated-policies": [
    "default"
  ]
}
```

The `type` URI, the `title` and the `violated-policies` member come from the draft, which registers this problem type with IANA.

> **Still in flux:** The RateLimit draft has changed its syntax more than once since 2020 (older versions used three separate headers such as `RateLimit-Remaining`). Draft 11 expires on 24 November 2026, so a newer version may exist when you read this. Generate the headers in one small function, as Nordlys does, so a change is a one-line fix.

The limiter itself is about thirty lines, a fixed window per client, keyed by the first address in `X-Forwarded-For`. It runs in the layer's `beforeAuth` hook for every path under `/api/`. I will not pretend this is how you should limit a production API: real sites limit at the edge (a CDN or an API gateway), with smarter algorithms, and Chapter 15 talks about telling good agents from bad bots. The point of the demo is the contract, the headers and the problem detail, which stays the same wherever the limit is enforced.
## Workflows with Arazzo

> **Hands-on:** One listing with the last step of a workflow file. If you don't write code, the idea fits in a sentence: Arazzo writes the order of API calls down, so neither a developer nor a model has to guess it. Pick up again at "The API catalog: one well-known starting point".

An OpenAPI description lists operations. It does not say in which order to call them, or how the output of one feeds the input of the next. A human developer reads that from the guide. A model has to infer it, and it often infers well, but "often" is not a word I like next to "booking".

Arazzo is the OpenAPI Initiative's answer: a separate document that describes workflows as sequences of steps over one or more OpenAPI descriptions, with inputs, success criteria and outputs for each step. Version 1.1.0 is dated 17 May 2026 (its headline addition is support for AsyncAPI-based steps).[^ch07-12] The Nordlys workflow `bookCabin` has three steps: search, check availability, book. Listing 7.4 shows the last one.

**Listing 7.4** `nordlys-cabins/layers/07-public-api/arazzo.js` — the booking step of the bookCabin workflow (excerpt)

```js
            stepId: 'book',
            operationId: 'createBooking',
            parameters: [{ name: 'Idempotency-Key', in: 'header', value: '$inputs.idempotencyKey' }],
            requestBody: {
              contentType: 'application/json',
              payload: {
                cabin: '$steps.search.outputs.slug',
                checkIn: '$inputs.checkIn',
                checkOut: '$inputs.checkOut',
                guests: '$inputs.guests',
                name: '$inputs.name',
                email: '$inputs.email',
                acceptTerms: '$inputs.acceptTerms',
              },
            },
            successCriteria: [{ condition: '$statusCode == 201' }],
            outputs: { ref: '$response.body#/ref', total: '$response.body#/total' },
```

Each value is a runtime expression. `$steps.search.outputs.slug` is the cabin the search step found, `$inputs.email` comes from whoever runs the workflow, and `$response.body#/ref` is a JSON Pointer into the response. The success criterion says what "worked" means: a 201, not just any 2xx. And `acceptTerms` is an input of the workflow, never a constant. The first version of this file had `acceptTerms: true` hard-coded in the payload, which is exactly the shortcut I warned about two sections ago. Writing the workflow down made the mistake visible, and that alone is a good argument for Arazzo.

Who reads Arazzo today? Honestly, few agent platforms do, as of November 2026. API tooling vendors use it for testing and documentation, and it is a natural input for the "progressive discovery" work on the MCP roadmap. I add it to Nordlys for two reasons: it costs one file, and it is the most precise recipe I can give to anyone (or any model) who wants to turn the API into a higher-level tool. The API catalog in the next section links to it, so a client that wants it can find it.

## The API catalog: one well-known starting point

We now have four documents that describe the API: the OpenAPI description, the Markdown page for developers, the Arazzo workflow and the health endpoint. How does a client that knows only `nordlys.example` find them?

RFC 9727, published in June 2025, answers this with a well-known URI and a link relation, both named `api-catalog`.[^ch07-13] A publisher serves a catalog document at `/.well-known/api-catalog`, and the catalog points at the APIs and their descriptions. The RFC is short and quite strict about a few things:

- The catalog **must** be in the Linkset format of RFC 9264, served as `application/linkset+json` with the profile parameter `https://www.rfc-editor.org/info/rfc9727`.
- A **HEAD** request to the well-known URI should return a `Link` header with `rel="api-catalog"`, so a client can discover the catalog without downloading it.
- Each API is an entry with an `anchor` (the API's base URL) and link relations that point at its documents. The RFC's examples use `service-desc` (a machine-readable description such as OpenAPI), `service-doc` (documentation for people), `service-meta` (other metadata) and `status` (a health endpoint). These relation types come from RFC 8631.

> **Hands-on:** Two short listings follow, the catalog document and the code that serves it. If you don't write code, the catalog is a small JSON file with four links, and the home page gets one HTTP header that points to it. Pick up again at the note on adoption at the end of this section.

Listing 7.5 is the whole catalog module of the Nordlys layer. Chapter 11 imports it to add one more entry, which is why it lives in its own file.

**Listing 7.5** `nordlys-cabins/layers/07-public-api/catalog.js` — the API catalog document

```js
// The API catalog document (RFC 9727): a Linkset that lists the site's APIs.
// Chapter 7 publishes it for the public API, Chapter 11 adds the MCP server.

export const CATALOG_PATH = '/.well-known/api-catalog';
export const LINKSET_TYPE = 'application/linkset+json; profile="https://www.rfc-editor.org/info/rfc9727"';

export function apiCatalog(origin) {
  return {
    linkset: [
      {
        anchor: `${origin}/api/v1`,
        'service-desc': [{ href: `${origin}/openapi.json`, type: 'application/json' }],
        'service-doc': [{ href: `${origin}/developers.md`, type: 'text/markdown' }],
        'service-meta': [{ href: `${origin}/api/v1/booking.arazzo.json`, type: 'application/json' }],
        status: [{ href: `${origin}/api/v1/health`, type: 'application/json' }],
      },
    ],
  };
}
```

Listing 7.6 shows how the layer serves the catalog and links to it.

**Listing 7.6** `nordlys-cabins/layers/07-public-api/index.js` — serving the catalog and linking to it (excerpt)

```js
    // 5. The API catalog (RFC 9727): a Linkset that points at the API's description, docs and status.
    ctx.staticFile(CATALOG, (c) => JSON.stringify(apiCatalog(origin(c)), null, 2), { contentType: LINKSET });
    // RFC 9727: a HEAD request to the catalog answers with a Link header.
    ctx.headers(CATALOG, { link: `<${CATALOG}>; rel="api-catalog"` });

    // 6. The home page points at the catalog. Append, so Link values from earlier chapters survive.
    ctx.headers('/', (c) => {
      const earlier = c.res.headers.get('link');
      const ours = `<${CATALOG}>; rel="api-catalog"`;
      return { link: earlier ? `${earlier}, ${ours}` : ours };
    });
```

The second `ctx.headers` call is the one that matters most for discovery. It adds `Link: </.well-known/api-catalog>; rel="api-catalog"` to the response of the home page, so any client that fetches `/` learns where the catalog is. Please note the append logic: Chapter 6 and other layers also add `Link` values to the home page, and overwriting them would quietly break their checks. This bug is easy to make and hard to notice, so the Chapter 11 tests check that the `api-catalog` value survives when that chapter appends its own.

Here is the real response to the HEAD request:

```http
HEAD /.well-known/api-catalog

HTTP 200
content-type: application/linkset+json; profile="https://www.rfc-editor.org/info/rfc9727"
link: </.well-known/api-catalog>; rel="api-catalog"
```

> **Note:** Adoption is still tiny. Cloudflare Radar's scan of the top 200,000 domains (115,468 scanned successfully, data dated 2 November 2026) found an API catalog on 0.74% of them.[^ch07-14] That is a reason to add one, not to skip it: the cost is a small JSON file, and the clients that do look for it (isitagentready.com among them) find you immediately.

## Versions, deprecation and who may call what

Two more questions come up in every review of an agent-facing API, and both have short answers for Nordlys.

### Versions and deprecation

Agents do not read your changelog. A platform imports your OpenAPI file once, and a configured agent may call the same operation for months. So the rules for changing an agent-facing API are stricter than for your own front end. Additive changes (a new optional field, a new operation) are safe. Renaming or removing anything breaks somebody silently.

Nordlys puts the major version in the path (`/api/v1`) and promises not to break it. When a v2 is needed one day, v1 keeps running for a published period. Two standard response headers help here. The `Deprecation` header of RFC 9745 (March 2025) tells a client that a resource is or will be deprecated, and the `Sunset` header of RFC 8594 gives the date after which it may stop answering.[^ch07-15] Nordlys v1 has nothing deprecated yet, so the demo does not send them, but I would add both, plus a `Link` to the migration guide, on the first day an operation is scheduled to go away. Agents that log response headers (and the developers who read those logs) get a warning long before the 404.

### Who may call what

Everything in the Nordlys API works without logging in, exactly like the public website: anyone can search, and anyone can book as a guest with a name and an email address. Cancelling needs the booking reference and the email it was made with, the same proof the website asks for. That is a deliberate product decision, and it keeps this chapter focused on API design.

Many real APIs are different. A partner API usually needs an API key, and anything that acts for a signed-in person (see "my bookings", change a reservation, use a stored payment method) needs delegated access, which in 2026 means OAuth. That is a big topic with its own standards for agents, and it has its own chapter: Chapter 14 adds OAuth to the Nordlys MCP server and explains protected resource metadata, scopes and consent. For now, remember one rule from the authorization chapters of every agent protocol I know: never ask an agent to collect a user's password. If an operation needs the user's identity, it needs OAuth.

## What the graders see

Let's check what this layer changes in our scorecard. isitagentready.com has an `apiCatalog` check in its Discovery group, and it passes when `/.well-known/api-catalog` returns `application/linkset+json` with a `linkset` array. Its `linkHeaders` check, in the Discoverability group, looks for RFC 8288 `Link` headers on the home page with relations that are useful to agents, and `api-catalog` is one of them. So a site that had no `Link` header at all now passes `linkHeaders` too.

`apiCatalog` is also one of the four integration checks of isitagentready's Level 4 ("Agent-Integrated", Level 3 plus one of: MCP Server Card, A2A Agent Card, Agent Skills, API Catalog). In other words, if Nordlys already sits at Level 3 thanks to the content work of Part 2, this one file is enough to reach Level 4. Chapter 11 adds the other integration checks and shows the full ladder.

The Lighthouse "Agentic browsing" category does not audit APIs at all as of November 2026. It looks at the page (accessibility, layout stability, WebMCP tools and `llms.txt`). That is not a gap in this chapter, just a reminder that the two graders measure different things.

> **Hands-on:** The rest of this section is about the tests. If you don't write code, here is what they prove: every operation behaves as its description says, the description is valid, and the catalog and the Link header are where clients look for them. Pick up again at "A checklist for an agent-friendly API".

### The Chapter 7 tests

The layer comes with eight tests in `nordlys-cabins/tests/ch07-public-api.test.js`, written with Node's built-in test runner. They call the app in-process (no network, no port), so they run in well under a second:

- search filters and paginates with an opaque cursor,
- availability returns a quote, and field problems come back as RFC 9457 problem details,
- booking needs an `Idempotency-Key` and replays a retry instead of booking twice,
- cancellation checks the email and reports the refund,
- RateLimit headers appear on every call, and the quota ends with a 429 and `Retry-After`,
- the OpenAPI document matches the routes the app actually serves,
- the OpenAPI document is valid according to `@scalar/openapi-parser`,
- the API catalog is Linkset JSON, answers HEAD with a `Link` header, and the home page links to it.

To run them from the demos repository:[^ch07-16]

```bash
cd nordlys-cabins
npm install
node --test tests/ch07-*.test.js
```

The test "the OpenAPI document matches the routes the app serves" deserves a word. It reads every path and method from `/openapi.json`, calls each one, and fails when the app answers 405 or a plain 404 (a 404 problem detail such as `not-found` is fine, it means the route exists). Descriptions drift. Someone renames a route and forgets the description, and every agent that imported the old file now calls a URL that does not exist. A test like this is cheap insurance.

## A checklist for an agent-friendly API

Before we move to MCP, here is the whole chapter in one list. I use it as a review checklist for any API that agents will call, and every item maps to something in the Nordlys layer:

| Item | Why agents need it | Nordlys |
|---|---|---|
| OpenAPI description, valid, served at a stable URL | Platforms and gateways import it as tools | `/openapi.json`, 3.1.2, validated in CI |
| `operationId`, `summary` and `description` on every operation | They become tool names and descriptions | Verb-noun ids, "when to use" descriptions |
| Enums and formats for known values | Fewer invented values | Regions and features generated from data |
| Problem details with stable types and field codes | The agent can explain and fix the problem | Nine types, each with a page under `/problems/` |
| Honest status codes | Frameworks branch on them first | 400, 404, 409, 422, 429 as documented |
| `Idempotency-Key` on operations with side effects | Safe retries after timeouts | Bookings, shared with MCP |
| Opaque cursors with complete `next` links | No invented page numbers, small responses | `links.next`, max 20 items |
| RateLimit headers and `Retry-After` | Agents slow down instead of hammering | Draft 11 syntax, `quota-exceeded` problem |
| A workflow description for multi-step tasks | The order of calls is explicit | Arazzo `bookCabin` |
| API catalog and a `Link` header on the home page | Clients find all of the above | `/.well-known/api-catalog` |

Chapter 10 returns to several of these items (naming, errors, granularity, confirmations) from the angle of tool design, and applies them to MCP and WebMCP as well.

## Summary

- A plain HTTP API is enough when a developer configured the agent and the task is a short sequence of well-defined operations. General assistants used by consumers need MCP or in-page tools, which build on the same logic.
- OpenAPI matters more than ever, but mostly as input: Azure API Management and Amazon Bedrock AgentCore Gateway turn OpenAPI into MCP tools, and Copilot Studio and Google ADK still import it directly. OpenAI lists 11 December 2026 for the retirement of Custom GPTs, whose Actions read OpenAPI.
- Every `operationId`, `summary` and `description` ends up in a model's prompt. Write them as tool names and usage instructions, put warnings on the risky operation itself, and use enums for known values.
- OpenAPI 3.1 is the safer target in November 2026 because tool support for 3.2 is uneven. Validate the description in CI and test that it matches your routes.
- RFC 9457 problem details with stable, resolvable types and per-field codes let an agent explain and fix an error instead of guessing.
- The `Idempotency-Key` header (an IETF draft, version 08 in October 2026) makes bookings safe to retry. Fingerprint the request, refuse reused keys, and return the original result on a replay.
- Opaque cursors and RateLimit headers (draft 11) keep responses small and teach agents to slow down. A 429 should carry `Retry-After` and the registered `quota-exceeded` problem type.
- Arazzo 1.1 writes multi-step flows down. The RFC 9727 API catalog at `/.well-known/api-catalog`, linked from the home page, is the one place where clients find everything, and it passes isitagentready's `apiCatalog` check, one of the four routes to Level 4.

[^ch07-1]: "Custom GPT retirement and migration FAQ," OpenAI Help Center, https://help.openai.com/en/articles/20001519-custom-gpt-retirement-and-migration-faq (read as a search result, the page refused direct requests), and "OpenAI Custom GPT Retirement Puts Integrations on the Migration Checklist," ADTmag, 28 September 2026, https://adtmag.com/articles/2026/09/28/openai-custom-gpt-retirement-puts-integrations-on-the-migration-checklist.aspx (both retrieved November 2026).
[^ch07-2]: "Expose REST API as MCP server," Azure API Management documentation, Microsoft Learn, https://learn.microsoft.com/en-us/azure/api-management/export-rest-mcp-server (retrieved November 2026).
[^ch07-3]: "Amazon Bedrock AgentCore Gateway: A secure AI gateway for agents, tools, and models," AWS documentation, https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html (retrieved November 2026).
[^ch07-4]: "Extend your agent with tools from a REST API (preview)," Microsoft Copilot Studio documentation, https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-extend-action-rest-api, and "OpenAPI tools," Agent Development Kit documentation, https://adk.dev/tools-custom/openapi-tools/ (both retrieved November 2026).
[^ch07-5]: "OpenAPI Specification v3.2.0," 19 September 2025, https://spec.openapis.org/oas/v3.2.0.html, "OpenAPI Specification v3.2.1," 10 September 2026, https://spec.openapis.org/oas/v3.2.1.html, and "OpenAPI Specification v3.1.2," https://spec.openapis.org/oas/v3.1.2.html, OpenAPI Initiative (all retrieved November 2026).
[^ch07-6]: "@scalar/openapi-parser," npm registry, https://registry.npmjs.org/@scalar/openapi-parser (version 0.29.19, retrieved November 2026).
[^ch07-7]: RFC 9457, "Problem Details for HTTP APIs," RFC Editor, https://www.rfc-editor.org/rfc/rfc9457.html (retrieved November 2026).
[^ch07-8]: "Hypertext Transfer Protocol (HTTP) Problem Types," IANA, https://www.iana.org/assignments/http-problem-types (retrieved November 2026).
[^ch07-9]: draft-ietf-httpapi-idempotency-key-header-08, "The Idempotency-Key HTTP Header Field," IETF, https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/ (retrieved November 2026).
[^ch07-10]: "Idempotent requests," Stripe API reference, https://docs.stripe.com/api/idempotent_requests (retrieved November 2026).
[^ch07-11]: draft-ietf-httpapi-ratelimit-headers-11, "RateLimit header fields for HTTP," IETF, https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/ (retrieved November 2026).
[^ch07-12]: "The Arazzo Specification v1.1.0," OpenAPI Initiative, https://spec.openapis.org/arazzo/v1.1.0.html (retrieved November 2026).
[^ch07-13]: RFC 9727, "api-catalog: A Well-Known URI and Link Relation to Help Discovery of APIs," https://www.rfc-editor.org/rfc/rfc9727.html, RFC 9264, "Linkset: Media Types and a Link Relation Type for Link Sets," https://www.rfc-editor.org/rfc/rfc9264.html, and RFC 8631, "Link Relation Types for Web Services," https://www.rfc-editor.org/rfc/rfc8631.html, RFC Editor (all retrieved November 2026).
[^ch07-14]: "AI Insights: Adoption of AI agent standards," Cloudflare Radar, https://radar.cloudflare.com/ai-insights#adoption-of-ai-agent-standards (data dated 2 November 2026, retrieved November 2026).
[^ch07-15]: RFC 9745, "The Deprecation HTTP Response Header Field," https://www.rfc-editor.org/rfc/rfc9745.html, and RFC 8594, "The Sunset HTTP Header Field," https://www.rfc-editor.org/rfc/rfc8594.html, RFC Editor (both retrieved November 2026).
[^ch07-16]: Demos repository, `nordlys-cabins/layers/07-public-api/` and `nordlys-cabins/tests/ch07-public-api.test.js`, https://github.com/webmaxru/agent-ready-web-demos (retrieved November 2026).
