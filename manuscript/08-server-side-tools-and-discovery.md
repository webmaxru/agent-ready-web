# Chapter 8: Server-side tools and discovery: APIs and MCP servers

This chapter covers

- When a plain HTTP API is all an agent needs, and how to describe it with OpenAPI 3.1
- Errors, retries and limits that agents can act on: problem details, idempotency keys, pagination and RateLimit headers
- An MCP server on the same booking logic, built on the stateless 2026-07-28 revision and tested with a real client
- Announcing what you offer: Link headers, the API catalog, MCP server cards, OAuth metadata, Agent Skills and the ARD manifest
- What the two graders see, and which discovery files Nordlys leaves out

An agent that can read every cabin page on Nordlys Cabins still cannot book anything. To book, it has to fill in a form like a person (Chapter 3 showed how fragile that is), or it needs a door built for software. Chapter 6 chose two such doors for the server side, a public API and an MCP server, and Chapter 7 showed how to design the tools behind them. This chapter builds both, on the same booking logic, and then does the part that is easy to forget: telling agents that the doors exist.

We start with the oldest door, a plain HTTP API. Most of the newer interfaces stand on top of it. The MCP server in the middle of this chapter calls the same functions, and the gateways from Microsoft and AWS that turn existing services into MCP tools read OpenAPI files. The last third of the chapter publishes the small files at predictable addresses that let a machine find all of it from nothing but the domain name.

> **Note:** Product managers and architects, the first section and the opening of each part are for you. The code sections are marked with a Hands-on callout. This chapter builds three layers in the demo app: `08-public-api`, `08-mcp-server` and `08-discovery`.

## When a plain API is enough

In my experience, a plain API is enough when three things are true. First, the agent runs somewhere a developer configured it: an agent framework in your partner's backend, a Copilot Studio agent in a customer's company, a script someone wrote with an LLM in the loop. Somebody decided to integrate with you and pointed the agent at your OpenAPI file. Second, the task is a short sequence of well-defined operations (search, check, book) rather than an open conversation. Third, authentication is either not needed (public data) or handled by that developer.

A booking site like Nordlys fits this quite well for one audience: travel agencies, trip planners and corporate travel tools that want to show Nordlys cabins next to hotels. A plain API is not enough when the agent was not configured for you. A person using a general assistant does not paste your OpenAPI URL anywhere. Those assistants connect to MCP servers, or they use a browser.

The code is the cheap part of a public API: the Nordlys routes are under a hundred lines, because they call domain functions the website already had. The real costs are a contract you keep, documentation that stays true (agents believe a stale description), abuse handling and support.

Please treat the 2023 advice about "ChatGPT reads your OpenAPI file" as history. OpenAI's help center lists 11 December 2026 as the scheduled retirement of Custom GPTs, and their OpenAPI-based actions do not carry over to the plugins that replace them, which are built on MCP.[^ch08-1] At the same time, OpenAPI became more important as the input to gateways. Azure API Management can expose operations of an existing REST API as tools on a remote MCP server, Amazon Bedrock AgentCore Gateway serves OpenAPI-described operations to agents over MCP, Copilot Studio creates REST API tools from an OpenAPI file, and Google's Agent Development Kit generates tools from any OpenAPI 3.x description.[^ch08-2][^ch08-3][^ch08-4] Whatever path an agent takes to your service, there is a good chance that a machine turns each of your operations into something a model chooses from.

## The Nordlys API

The Nordlys public API has five operations under `/api/v1`, plus a health endpoint. Each one maps to a question a guest (or an agent acting for a guest) actually asks:

| Operation | HTTP | What it answers |
|---|---|---|
| `searchCabins` | `GET /api/v1/cabins` | Which cabins fit my group, region, dates and wishes? |
| `getCabin` | `GET /api/v1/cabins/{slug}` | Tell me everything about this cabin. |
| `checkAvailability` | `GET /api/v1/cabins/{slug}/availability` | Is it free for these dates, and what is the total? |
| `createBooking` | `POST /api/v1/bookings` | Book it for this person. |
| `cancelBooking` | `POST /api/v1/bookings/{ref}/cancel` | Cancel my booking. |

Around these sit the files that describe them: `/openapi.json`, a Markdown page for developers at `/developers.md`, an Arazzo workflow, one page per error type under `/problems/`, and the API catalog at `/.well-known/api-catalog`. Figure 8.1 shows how they fit together.

![Figure 8.1 — The Nordlys API layer. Five operations share one booking service with the MCP server built later in this chapter. Around them, the description files point at each other, and the API catalog is the entry point that a client finds from the home page's Link header.](images/figure-8-1.png)

Please note the box in the middle of the figure: the booking service. It is a thin module that wraps the shared domain functions of the demo app and adds what machine clients need on top, such as idempotency. The HTTP routes call it, and so do the MCP tools. There is exactly one place where a booking is created, whatever door the request came through.

The description uses OpenAPI 3.1.2. Version 3.2.0 was published on 19 September 2025, but the point of the file is that other tools read it, and in my judgment their support for 3.2 is still uneven in November 2026.[^ch08-5]

### Describing operations so a model chooses well

> **Hands-on:** This section shows the OpenAPI description of the booking operation. If you don't write code, the idea is simple: every name and sentence in the API description is read by a model that has to choose an operation and fill in its fields, so we write them for that reader. Pick up again at "Errors an agent can act on".

When a platform imports an OpenAPI file, each operation becomes a tool. The `operationId` becomes the tool name, the `summary` and `description` become the tool description, and the parameters and request body become the input schema. Chapter 7's craft applies directly: an `operationId` on every operation, written as a verb and a noun, a one-line `summary`, a `description` that says when to use the operation and what to do before it, enumerations wherever the set of values is known, and a description on every non-obvious field. Listing 8.1 shows the booking operation.

**Listing 8.1** `nordlys-cabins/layers/08-public-api/openapi.js` — the createBooking operation (excerpt)

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

The `description` does real work: "Only call this after the user has confirmed the cabin, the dates and the price from checkAvailability." When a platform turns operations into tools, the model sees the description of each tool it might call, while a general "about this API" text may never reach the prompt. So the instruction belongs on the risky operation itself, and Chapter 7's eval is how you test whether models follow it.

An invalid OpenAPI file fails silently in many tools: the import shows fewer operations, or a parameter disappears. So the tests load `/openapi.json` from the app and validate it with `@scalar/openapi-parser` (version 0.29.19), and check that every operation has an `operationId`, a `summary` and a `description`.[^ch08-6] The validator caught one real mistake while I built the layer: a `$ref` to a shared parameter with an extra `required: true` next to it, which OpenAPI 3.1 does not allow.

### Errors an agent can act on

Picture this. An agent asks for Fjellro, a mountain cabin in Rondane, for twelve guests. Fjellro sleeps six. If the API answers `400 Bad Request` with `{"error":"invalid"}`, the agent guesses. A good error for an agent has the same parts as a good error for a person: what went wrong, where, and what to do about it. RFC 9457, "Problem Details for HTTP APIs", defines exactly that: a JSON object with the media type `application/problem+json` and five standard members, `type`, `title`, `status`, `detail` and `instance`, plus your own extensions.[^ch08-7] Here is the real response from the Nordlys API:

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

The status code is honest (422 for invalid content, 404 for a cabin that does not exist, 409 for a conflict with the current state), and agents branch on it before they read anything else. The `type` is stable and resolves to a short Markdown page, so an agent that has never seen the error can learn what it means. The `errors` extension, my own and documented in the OpenAPI description, lists every field problem with a machine-readable `code` to branch on and a `detail` an assistant can pass on word for word.

The booking service returns errors as plain data, `{ field, code, message }`, and each door renders them in its own format. The HTTP API turns them into problem details, and the MCP tools later in this chapter turn them into a tool result marked as an error. A `too_many_guests` is a `too_many_guests` wherever it came from.

### Retries without double bookings

Networks fail. An agent sends `POST /api/v1/bookings`, the connection drops after the server created the booking but before the response arrived, and the agent sees a timeout. If it retries, the guest may get two bookings. If it gives up, the guest may book somewhere else while Nordlys holds a cabin for them. The common answer is an idempotency key: the client sends a unique value for each logical operation, and a server that sees the same key again returns the result of the first attempt instead of repeating it.

The IETF HTTPAPI working group is standardizing the header in draft-ietf-httpapi-idempotency-key-header-08 from October 2026, which defines `Idempotency-Key` as a Structured Field string.[^ch08-8] Payment APIs such as Stripe have used the same header name for years.[^ch08-9] The draft also covers the tricky cases, and Nordlys follows it: no key on a booking is a 400, the same key with a different body is a 422, the same key while the first request is still running is a 409, and the same key with the same body after success returns the original booking with status 200 instead of 201. Here is the real exchange, shortened:

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

Three nights in Fjellro from 2 to 5 December 2026 cost 7,000 NOK plus a 900 NOK cleaning fee, and free cancellation ends on 18 November, 14 days before check-in.

> **Still in flux:** `Idempotency-Key` is an Internet-Draft, not an RFC, as of November 2026. The idea is stable and widely deployed, but details such as the error codes for reused keys may still change. Nordlys follows draft 08 and accepts the value with or without quotes, because many clients send it bare.

> **Warning:** The demo keeps idempotency keys in memory, which works for one server process. With several instances behind a load balancer, the keys must live in shared storage, or a retry that lands on another instance books twice.

Cancelling needs a different kind of care. `POST /api/v1/bookings/{ref}/cancel` takes the email address the booking was made with, a wrong email gets the same `404` as a wrong reference (so nobody can probe which references exist), and a second cancel returns `409` with the type `already-cancelled`. The state does not change and nothing is refunded twice.

### Lists that end, and limits that explain themselves

An agent that asks for "all cabins" should not get a 4 MB response that eats its context window. So `searchCabins` returns at most 20 items, a `total`, and a complete `links.next` URL with an opaque cursor. The OpenAPI description says "Opaque cursor from links.next. Do not build it yourself." Models love to "help" by computing `page=2` themselves, and an opaque cursor removes the temptation.

Agents hit rate limits more often than people because they are fast and they parallelize, and a bare 429 leads to immediate retries. The IETF draft draft-ietf-httpapi-ratelimit-headers-11 (May 2026) defines two response headers: `RateLimit-Policy` describes the quota (`q` requests per `w` seconds), and `RateLimit` says how much is left (`r`) and when it resets (`t`).[^ch08-10] Nordlys sends them on every API response, and when the quota is used up it answers with 429, a `Retry-After` header and a problem detail of the IANA-registered type `quota-exceeded`:

```http
RateLimit-Policy: "default";q=60;w=60
RateLimit: "default";r=57;t=60
```

> **Still in flux:** The RateLimit draft has changed its syntax more than once since 2020 (older versions used separate headers such as `RateLimit-Remaining`), and draft 11 expires on 24 November 2026. Generate the headers in one small function, so a change is a one-line fix.

Real sites limit at the edge, and the contract stays the same wherever the limit is enforced. Two more files complete the API. An Arazzo 1.1.0 workflow (dated 17 May 2026) writes down the order of calls, search, check, book, so that neither a developer nor a model has to guess it, although few agent platforms read Arazzo as of November 2026.[^ch08-11] And the major version lives in the path (`/api/v1`) with a promise not to break it. Appendix B lists the Deprecation and Sunset headers for the day a version has to go.

## An MCP server on the same booking logic

A person who opens Claude or ChatGPT and types "find me a cabin with a sauna in Norway for the first week of December" will not get anything from that API. General assistants connect to MCP servers. The Model Context Protocol (MCP) is how most AI hosts talk to outside tools in 2026. Anthropic introduced it in November 2024, and in December 2025 it moved to the Agentic AI Foundation, a fund under the Linux Foundation.[^ch08-12] If you want a general assistant to do something on your site, MCP is the most common door. We build a remote MCP server: an HTTPS endpoint at `/mcp` on our own domain, next to the API, calling the very same booking service.

### MCP in five minutes

- The **host** is the application a person uses: Claude, ChatGPT, Copilot, VS Code, Cursor and others. It runs the model and decides what to show the user.
- The **client** lives inside the host. It keeps one connection to one server and speaks the protocol.
- The **server** is what you build. It offers capabilities to any client that connects.

A server offers three kinds of things. **Tools** are functions the model can call, each with a name, a description and a JSON Schema for its input and optionally its output. **Resources** are data the host can read, such as a guide article or a cancellation policy, identified by URIs. **Prompts** are templates a person can pick in the host's interface. Under the hood, MCP is JSON-RPC 2.0, and for a remote server the transport is Streamable HTTP: each request is an HTTP POST to one endpoint, and the server answers with JSON, or with a short Server-Sent Events stream when it has progress to report. Figure 8.2 puts the pieces together for Nordlys.

![Figure 8.2 — The Nordlys MCP server. A host such as Claude or ChatGPT runs an MCP client that sends JSON-RPC requests over HTTPS to /mcp. A fresh server object answers each request, built from a registry of tools, resources and prompts. The tools call the same booking service as the public API.](images/figure-8-2.png)

What do you get as a site owner? Your capabilities show up inside the assistant, described in your words, and the assistant calls them instead of scraping your pages or guessing. Your server stays in control of what actually happens: validation, prices, availability, idempotency. If you built the API on a shared service layer, the MCP server is mostly a thin translation layer. The Nordlys tools, resources and prompt are about 230 lines, and most of those lines are descriptions and schemas.

### Who connects to remote MCP servers

| Host | Remote MCP support (November 2026) |
|---|---|
| Claude (Anthropic) | "Custom connectors" on all plans, with Free limited to one connector[^ch08-13] |
| ChatGPT and Codex (OpenAI) | MCP servers power plugins (the former "Apps SDK" documentation is now titled "Plugin development for ChatGPT and Codex")[^ch08-14] |
| Microsoft Copilot Studio | An onboarding wizard connects agents to existing MCP servers[^ch08-15] |
| Visual Studio Code | MCP servers can be added for GitHub Copilot in VS Code[^ch08-16] |
| Gemini Enterprise | Custom MCP server connections, Pre-GA and configured by an admin[^ch08-17] |

In every one of these hosts, somebody still has to add your server: a user pastes a URL, an admin approves a connector, or a developer edits a configuration file. There is no global "MCP search" that assistants consult on their own. The second half of this chapter covers the discovery files that will help with that. One piece of OpenAI's advice I recommend to everybody: the server's `instructions` are read by ChatGPT and Codex, and "the most important details" belong in the first 512 characters. The Nordlys instructions are 309 characters long, and they say what the server is for and the one rule that matters most: book only after the user confirmed.

### The 2026-07-28 revision: stateless MCP

If you read an MCP tutorial from 2025, a lot of what follows will look different. The current specification revision is dated 2026-07-28, and its headline is that MCP is now stateless.[^ch08-18] The `initialize` handshake and the `Mcp-Session-Id` header are gone, and every request carries the protocol version and the client's capabilities in its `_meta` field. `server/discover` is mandatory for servers. Every POST carries `Mcp-Method` (and `Mcp-Name` for calls such as `tools/call`) as HTTP headers, so a gateway or a firewall can route or filter requests without parsing the body. List results carry caching hints. And a tool that needs more input from the user returns a result with `resultType: "input_required"`, and the client sends a new request.

The release post sums up why this matters: "any request can land on any instance behind a plain round-robin load balancer".[^ch08-19] Personally for me, this is the change that makes MCP a normal web workload. You run it on the same infrastructure as your API, and scale and cache it the same way.

> **Hands-on:** Here is one request from the wire. If you don't use a terminal, the takeaway is that a modern MCP request is an ordinary HTTP POST that carries its method in a header and its protocol version in both a header and the body. Continue with "Choosing the tools".

With the demo running (`npm start -- --upto=8 --port=4810`), this asks the Nordlys server what it is:

```bash
curl -s http://localhost:4810/mcp \
  -H 'content-type: application/json' \
  -H 'accept: application/json, text/event-stream' \
  -H 'mcp-protocol-version: 2026-07-28' \
  -H 'mcp-method: server/discover' \
  -d '{"jsonrpc":"2.0","id":1,"method":"server/discover","params":{"_meta":{
        "io.modelcontextprotocol/protocolVersion":"2026-07-28",
        "io.modelcontextprotocol/clientCapabilities":{},
        "io.modelcontextprotocol/clientInfo":{"name":"curl","version":"8"}}}}'
```

The answer carries everything a client needs to start: the supported protocol versions (`2026-07-28`), the capabilities (tools, resources and prompts, each able to announce changes), the instructions and the server's identity in `_meta`. The rules are strict, and the SDK enforces them: a request with the version header but without `_meta` is refused with error -32602, and a `tools/call` whose `Mcp-Name` header disagrees with the body gets -32020, so a firewall that filters on headers cannot be tricked.

> **Still in flux:** Stateless MCP was three months old in November 2026. Not every host supports it yet, which is why the TypeScript SDK serves both protocol eras from one endpoint by default. Nordlys keeps that default, and the tests cover both eras.

### Choosing the tools

Every tool you add costs something: its name, description and schema go into the model's context in every conversation where your server is connected, next to the tools of every other server. "Progressive discovery", loading tools on demand, is on the MCP roadmap exactly because servers with dozens of tools overwhelm models.[^ch08-20]

So I asked one question per API operation: does a guest's conversation need this as a separate step? `searchCabins`, `checkAvailability`, `createBooking` and `cancelBooking` became `search_cabins`, `check_availability`, `create_booking` and `cancel_booking`. `getCabin` did not become a tool, because search results already carry what a model needs to compare cabins. And the tool descriptions talk about the conversation, not about HTTP: the description of `create_booking` says when to call it in a dialogue ("only after the user confirmed the cabin, dates, guests and the total from check_availability"). Same operation, different reader.

### Building the Nordlys server

> **Hands-on:** This section writes the server factory and mounts it at `/mcp`. If you don't write code, here is what it achieves: one function builds the MCP server from a list of tools, the web app hands every request on `/mcp` to that function, and a small check makes sure that only our own web pages (and non-browser clients) can call it. Pick up again at "Annotations and confirmations".

The TypeScript SDK went through a big restructuring in 2026. Version 2 splits the old single package into `@modelcontextprotocol/server`, `@modelcontextprotocol/client` and small framework adapters. It is ESM-only, needs Node 20 or newer, and accepts Zod v4 among other schema libraries.[^ch08-21] On 2 November 2026 the npm registry lists `@modelcontextprotocol/server` 2.4.0 (published 23 October 2026), `@modelcontextprotocol/client` 2.4.0 and `zod` 4.6.7. Those are the versions Nordlys uses. The SDK's `createMcpHandler` returns a handler with a standard `fetch(request)` method, so any framework or runtime that speaks Web `fetch` can mount it in one line.[^ch08-22] Listing 8.2 is the whole server factory.

**Listing 8.2** `nordlys-cabins/layers/08-mcp-server/server.js` — the server factory

```js
// Builds the Nordlys MCP server. createMcpHandler calls this once per HTTP
// request, so the server holds no state between requests and any instance
// behind a load balancer can answer any call.
import { McpServer } from '@modelcontextprotocol/server';
import { mcpRegistry } from './registry.js';

const INSTRUCTIONS =
  'Nordlys Cabins rents holiday cabins in Norway. Use search_cabins to find cabins, check_availability to get the exact price, ' +
  'and create_booking only after the user confirmed the cabin, dates, guests and total. Prices are NOK. Dates are YYYY-MM-DD in Europe/Oslo. ' +
  'Free cancellation ends 14 days before check-in.';

export function createNordlysServer(ctx, { authInfo, requestInfo } = {}) {
  const server = new McpServer({ name: 'nordlys-cabins', title: 'Nordlys Cabins', version: '1.0.0' }, { instructions: INSTRUCTIONS });
  const extra = { auth: authInfo ?? null, request: requestInfo ?? null, ctx, store: ctx.store };
  const { tools, resources, prompts } = mcpRegistry(ctx);

  for (const [name, { config, handler }] of tools) {
    server.registerTool(name, config, (args, sdk) => handler(args, { ...extra, sdk }));
  }
  for (const [name, { uri, metadata, read }] of resources) {
    server.registerResource(name, uri, metadata, (u, vars, sdk) => read(u, vars ?? {}, { ...extra, sdk }));
  }
  for (const [name, { config, build }] of prompts) {
    server.registerPrompt(name, config, (args, sdk) => build(args, { ...extra, sdk }));
  }
  return server;
}
```

The tools, resources and prompts come from a registry that later layers extend without editing this file, which is how Chapter 11 adds tools for signed-in members, and every handler's `extra.auth` stays `null` until Chapter 11 verifies OAuth tokens. Listing 8.3 mounts the handler.

**Listing 8.3** `nordlys-cabins/layers/08-mcp-server/index.js` — mounting the handler at /mcp (excerpt)

```js
    const handler = createMcpHandler((requestContext) => createNordlysServer(ctx, requestContext));

    ctx.mcp(async (c) => {
      // The SDK handler checks no Origin, Host or token itself. Browsers send an
      // Origin header: only our own site may call /mcp from a web page.
      const ownHost = new URL(ctx.absoluteUrl(c, '/')).hostname;
      const rejected = originValidationResponse(c.req.raw, [ownHost, new URL(c.req.url).hostname]);
      if (rejected) return rejected;
      // A later layer (Chapter 11) verifies a bearer token and stores the result
      // with c.set('mcpAuth', authInfo). Until then every caller is anonymous.
      return handler.fetch(c.req.raw, { authInfo: c.get('mcpAuth') ?? undefined });
    });
```

`createMcpHandler` calls the factory once per HTTP request. That is how the SDK implements statelessness: no server object survives between requests, so any instance can answer any request. The SDK documentation is refreshingly direct about what the handler does not do: "it validates no Host header, no Origin header, and no token".[^ch08-22] Those checks are yours. Browsers always send an `Origin` header, and non-browser hosts normally do not, so the layer refuses any request whose `Origin` is not our own site. A malicious page that tries to call `/mcp` from a visitor's browser gets `403 Forbidden` with "Invalid Origin: evil.example".

> **Warning:** "Anonymous" does not mean "unlimited". If you expose MCP publicly, put the same kind of rate limit in front of `/mcp` as in front of the API, at your edge or in your app.

### Tools, results and errors

The four Nordlys tools follow the design from Chapter 7: snake_case names with a verb, described parameters, and the same validation, error codes and idempotency keys as the API, because they call the same booking service. Each tool declares an `outputSchema` and returns its result twice, as `structuredContent` (an object that matches the schema) and as a text block. The text is what most hosts put into the model's context, and the structured content is what code can rely on. The SDK validates `structuredContent` against the `outputSchema`, so the two cannot drift apart silently.

A wrong input comes back as a normal result with `isError: true`, not as a protocol error. For Fjellro with twelve guests, the text is `guests: Fjellro sleeps up to 6 guests. (too_many_guests)`, the same field, message and code that the API returns as a problem detail. One booking service, one set of error codes, two renderings. `create_booking` takes the idempotency key as an `idempotencyKey` argument, because MCP has no request headers for tool arguments, so a booking made through MCP cannot be repeated through the API with the same key.

### Annotations and confirmations

Every Nordlys tool carries annotations, the hints MCP has had since the 2025-03-26 revision.[^ch08-23]

| Tool | readOnly | destructive | idempotent | openWorld | Reasoning |
|---|---|---|---|---|---|
| `search_cabins` | true | | | false | Only reads Nordlys data |
| `check_availability` | true | | | false | Only reads, nothing is held or reserved |
| `create_booking` | false | false | true | false | Creates a booking, but never destroys anything, and the same key returns the same booking |
| `cancel_booking` | false | true | true | false | Cancelling cannot be undone, and a second cancel changes nothing |

Hosts use annotations to decide how much friction to add, for example a confirmation before a destructive tool. But annotations are hints, not security. The specification says clients must treat them as untrusted unless the server itself is trusted, and that "there SHOULD always be a human in the loop with the ability to deny tool invocations".[^ch08-24] So the server checks what it can, and for a cancellation or a payment the confirmation happens in front of the person. Chapter 11 builds that with `input_required` results and a confirmation page.

The server also offers two resources (the guide articles and the cancellation policy as clean Markdown) and one prompt, `plan_cabin_trip`. Hosts use resources very differently, so anything essential belongs in tool results and descriptions. I left out MCP Apps, the extension that lets a tool return an interactive interface inside the host, because it is a second front end to design, test and keep accessible.[^ch08-25]

### Testing with a real client

Unit tests that call tool handlers directly prove very little about MCP. The SDK's client can use a custom `fetch`, and our app has a `fetch` function too, so the tests connect the two in-process, with no network and no port. The seven tests in `nordlys-cabins/tests/ch08-mcp-server.test.js` check that a 2026-07-28 client discovers this chapter's four tools with honest annotations in a stable order, followed by `find_booking` from Chapter 7, that results carry `structuredContent` and errors carry their codes, that `create_booking` is idempotent and books through the same service as the API, that a 2025-11-25 client with the old `initialize` handshake is served from the same endpoint, and that a page from another origin cannot call `/mcp`.[^ch08-26]

For exploring a server by hand, the MCP project maintains MCP Inspector. Version 2.13.0 (28 October 2026) needs Node 22.19 or newer and has a web UI, a CLI and a terminal UI.[^ch08-27] With the demo running, this calls one tool and prints the same total of 7,900 NOK that the API returned:

```bash
npx @modelcontextprotocol/inspector@2.13.0 --cli http://localhost:4810/mcp \
  --method tools/call --tool-name check_availability \
  --tool-arg cabin=fjellro checkIn=2026-12-02 checkOut=2026-12-05 guests=4
```

Remote hosts call your server from the vendor's cloud, so they need a public HTTPS URL. Editors such as VS Code with GitHub Copilot can reach `localhost` and are the easiest place to watch a real model use your tools.[^ch08-16]

> **Note:** Most MCP tutorials were written for the 2025 revisions. In them, `initialize` is now `server/discover`, sessions are gone (pass an ID from one tool result to the next tool instead), and `@modelcontextprotocol/sdk` is the v1 SDK. The SDK team ships a codemod, `npx @modelcontextprotocol/codemod@beta v1-to-v2 .`, and the v2 handler still answers 2025-era clients on the same endpoint.

### Where to host it

The Nordlys MCP server runs inside the same Node process as the website and the API, and thanks to the stateless protocol it scales like the rest of the app. The SDK's `fetch`-style handler also runs on Cloudflare Workers (the `agents` package takes an SDK v2 server factory), in a Next.js project on Vercel (the `mcp-handler` package), on Azure Functions (public preview) and on AWS Bedrock AgentCore Runtime.[^ch08-28][^ch08-29][^ch08-30] And a gateway such as Azure API Management or AgentCore Gateway can generate MCP tools from your OpenAPI file with no MCP code at all. What you lose then is control over the tool layer: names come from `operationId`s and descriptions from your OpenAPI text. For Nordlys I prefer a hand-written server, because the tool descriptions and the booking rules are the product. For a company with fifty internal APIs, a gateway is probably the only realistic start.

Whatever you choose, three things do not change. You check the `Origin` header, you protect anything personal with OAuth (Chapter 11), and you log tool calls with enough detail to answer "what did the agent do, and for whom?" (Chapters 10 and 12).

## Announcing what you offer

Nordlys now has two programmatic doors, and an agent that knows only `nordlys.example` can see neither. Today, in most cases, a human closes that gap by hand. Discovery files try to close it from the site's side. They are small, mostly static documents at predictable addresses that answer three questions for a machine: what can this site do, where are the endpoints, and how do I connect?

This is the least settled layer in the whole book. Three limits are worth keeping in mind. A discovery file is advisory, and the live interface is the truth. A discovery file grants nothing: publishing a card does not make a server public, and hiding it does not make it private. And somebody has to read the file.

Who reads them in November 2026? Scanners first, registries second, agents a distant third. isitagentready.com defines its Level 4 and Level 5 almost entirely by discovery files, and the Lighthouse Agentic Browsing category audits `llms.txt` and the ARD manifest.[^ch08-31][^ch08-32] Cloudflare Radar's data dated 2 November 2026 (115,468 successfully scanned domains) found agent-useful `Link` headers on 9.7% of sites, an API catalog on 0.74%, an MCP server card on 0.61%, an Agent Skills index on 0.59% and an ARD manifest on 0.29%.[^ch08-33] I could not find a mainstream assistant that automatically fetches an MCP server card or an Agent Skills index from an arbitrary domain and connects without a human approving it. So you publish discovery files today mostly for the graders, the registries and the next generation of clients. That is fine, as long as you spend an afternoon on it and not a quarter. Figure 8.3 shows every discovery document Nordlys serves.

![Figure 8.3 — The discovery map of Nordlys Cabins. The home page carries a Link header that points to the Markdown version, llms.txt, the API catalog and the ARD manifest. The API catalog lists the REST API and the MCP endpoint. The ARD manifest lists the MCP server card and the booking skill. The Agent Skills index points to the SKILL.md file. OAuth metadata arrives in Chapter 11.](images/figure-8-3.png)

Most of these documents live under `/.well-known/`, the path prefix RFC 8615 reserves for site-wide metadata. As of the IANA registry update of 26 October 2026, `api-catalog` and `oauth-protected-resource` are permanent entries backed by RFCs, and there are no entries for `ard.json`, `agent-skills` or `mcp/server-card.json`.[^ch08-34] An unregistered name can still work in practice, but it is a hint that the name could still move.

### Link headers: the cheapest signpost

A `Link` header (RFC 8288) points from a response to another resource and says how the two relate.[^ch08-35] It works on any response, and a client can read it with a cheap `HEAD` request. Here is the `Link` header of the Nordlys home page, exactly as the demo server sends it (one line, wrapped here for print):

```http
Link: <https://nordlys.example/index.md>; rel="alternate"; type="text/markdown",
      <https://nordlys.example/llms.txt>; rel="describedby",
      </.well-known/api-catalog>; rel="api-catalog",
      </.well-known/ard.json>; rel="ard"
```

Chapter 5 added the Markdown alternate and `llms.txt`, and this chapter adds the API catalog and the ARD manifest. isitagentready's `linkHeaders` check passes on relations that are useful to agents. `ard` is not in the IANA link relations registry as of 2 November 2026, but Lighthouse looks for it and the ARD specification says a consumer "MUST honour a rel="ard" link", so we use it anyway.[^ch08-36]

One engineering detail is easy to get wrong: several layers contribute a `Link` value to the same response, and if any one of them *sets* the header instead of *appending* to it, the earlier values vanish without an error. Every Nordlys layer reads the current value first and appends its own, and a test checks that the `api-catalog` value survives when the ARD value is added.

### The API catalog, with MCP in it

RFC 9727 (June 2025) defines a well-known URI and a link relation, both named `api-catalog`.[^ch08-37] The catalog at `/.well-known/api-catalog` must be a Linkset (RFC 9264) served as `application/linkset+json` with the RFC's profile parameter, a `HEAD` request should return a `Link` header with `rel="api-catalog"`, and each API is an entry with an `anchor` and links to its machine-readable description (`service-desc`), its documentation (`service-doc`), other metadata (`service-meta`) and a health endpoint (`status`).

> **Hands-on:** Listing 8.4 is the catalog module. If you don't write code, the catalog is a small JSON file with four links per API, and the home page gets one header that points to it. Pick up again at "MCP server cards".

**Listing 8.4** `nordlys-cabins/layers/08-public-api/catalog.js` — The API catalog document

```js
// The API catalog document (RFC 9727): a Linkset that lists the site's APIs.
// Chapter 8 publishes it for the public API, Chapter 8 adds the MCP server.

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

The discovery layer imports this function and pushes one more entry for the MCP endpoint, whose `service-desc` is the server card with the type `application/mcp-server-card+json`. RFC 9727 talks about APIs in general and does not prescribe a description format, so I think an MCP server fits. That is my judgment, not something the RFC or the MCP project asks for. This one file is also what takes Nordlys from Level 3 to Level 4 on isitagentready.com, because Level 4 needs only one of four integration checks.[^ch08-31] Radar found an API catalog on 0.74% of scanned domains, which is a reason to add one: the cost is a small JSON file, and the clients that look for it find you immediately.[^ch08-38]

### MCP server cards: one idea, three addresses

A server card is a static copy of the *connection* part of what `server/discover` returns: there is an MCP server here, it is called this, it lives at this URL, it speaks these versions. A registry or a client learns that from a single `GET` without speaking MCP. The format comes from SEP-2127, "MCP Server Cards - HTTP Server Discovery", which deliberately leaves out the tools, resources and prompts, because a tool list in a static file goes stale the day somebody adds a tool.[^ch08-39]

The confusing part is the address. In November 2026, three are in circulation. `/.well-known/mcp/server-card.json` comes from an earlier proposal, SEP-1649, and it is what isitagentready's `mcpServerCard` check reads first.[^ch08-40][^ch08-31] `/.well-known/mcp.json` is what isitagentready.com publishes for its own server, and it is not in any MCP proposal I could find. And SEP-2127 reserves `server-card` under the server's own endpoint "as the recommended location", for Nordlys `https://nordlys.example/mcp/server-card`, with domain-level discovery through a catalog document (which became the ARD manifest).[^ch08-39] Nordlys serves that last one as the canonical card, mirrors it at the scanner's path and skips `mcp.json`. One mirror is enough.

> **Still in flux:** On 2 November 2026 the SEP-2127 page showed the status "Final", while the extension's own repository said "Status: Experimental. This work is for prototyping and feedback only".[^ch08-41] Treat the server card as a useful convention with a likely future, and keep the code that produces it small.

**Listing 8.5** `nordlys-cabins/layers/08-discovery/index.js` — the MCP server card at two addresses (excerpt)

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

The card is generated from the request's origin, so it is right on staging and in production, and its `remotes` array lists both protocol versions the endpoint answers. A test of the discovery layer sends a real `server/discover` to `/mcp` and fails if the server and the card disagree.

### OAuth metadata is discovery too

An MCP client that wants to call a protected tool on a user's behalf needs to know which authorization server to talk to and which scopes exist. It learns that from OAuth Protected Resource Metadata at `/.well-known/oauth-protected-resource` (RFC 9728) and from the authorization server's own metadata (RFC 8414).[^ch08-42] isitagentready counts these as "auth metadata", one of the three ingredients of its Level 5. Radar put OAuth discovery on 8.1% of top domains and Protected Resource Metadata on 4.1% as of 2 November 2026, much of it published by platforms by default.[^ch08-33] Nordlys adds both in Chapter 11, when it puts OAuth in front of the member tools.

### Agent Skills: instructions an agent can load

The server card tells an agent *where* the MCP server is. It does not tell the agent *how to use it well*: ask for the dates before searching, show the total before booking, never accept the terms on the user's behalf, retry with the same idempotency key. A procedure that spans several tools does not fit into any single tool description. A skill is a folder with a `SKILL.md` file: YAML front matter with a `name` (up to 64 characters) and a `description` (up to 1,024 characters that say "what the skill does and when to use it"), followed by Markdown instructions.[^ch08-43] An agent keeps only the names and descriptions in mind and loads the full instructions when a task matches. Listing 8.6 is the whole skill Nordlys publishes. Please read it as a product manager or a support lead would: it is the booking policy and the booking flow, in plain language.

**Listing 8.6** `nordlys-cabins/layers/08-discovery/skills/book-a-nordlys-cabin/SKILL.md` — the booking skill

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

The description names the regions, because an agent decides whether to load a skill from its description alone. Step 4 says "Never accept the terms on the user's behalf", a good place to state the rule and a bad place to *rely* on it, so the server still refuses a booking without an explicit `acceptTerms: true`.

> **Warning:** A skill is text that an agent will follow, which makes it a prompt-injection surface in both directions. Your own skill must never contain anything you would not want an agent to execute, and an agent should treat a skill from an unknown site with the same suspicion as any other page content (Chapter 10).

To make the file findable, Nordlys publishes an index at `/.well-known/agent-skills/index.json`, following the "Agent Skills Discovery via Well-Known URIs" RFC, a draft maintained by Cloudflare (version 0.2.0, updated on 12 March 2026).[^ch08-44] Each entry has a `name`, a `type`, a `description`, a `url` and a `digest`, the SHA-256 of the file, which lets an agent check that the file it downloaded is the one the index describes. In our scan of 44 sites on 2 November 2026, vercel.com published 9 skills and stripe.com 10, both for developers' coding agents.[^ch08-45] A booking site publishing a skill for travel agents is newer ground, and I think it is one of the more promising ideas in this chapter, because it carries policy and procedure, the things tool schemas are worst at.

### ARD: one manifest for all of them

A card for the server, an index for the skill, a catalog for the APIs: three files, three formats, three paths. The Agentic Resource Discovery specification, ARD, gives the question "what agentic resources does this domain have?" one answer. Google announced it on 17 June 2026, and the current text is version 0.91, status "Proposal", dated 26 August 2026.[^ch08-36] A consumer "MUST fetch /.well-known/ard.json, and MUST honour a rel="ard" link". Each entry carries a domain-anchored `identifier`, a `displayName`, a `type` given as a media type, and a `url` (or the artifact inline). And then there is the term that makes ARD different from a plain list: `representativeQueries`, example requests the resource is good for. The Lighthouse documentation is direct about them: "Add 2 to 5 representativeQueries to each entry to get a perfect score."[^ch08-32]

For a site owner, writing representative queries is a familiar job: keyword research, phrased as things people ask an assistant.

> **Hands-on:** Listing 8.7 builds the Nordlys manifest. If you skip the code, look at the representative queries in it: they are the part a content or SEO person should write. Pick up again at "What the graders see".

**Listing 8.7** `nordlys-cabins/layers/08-discovery/index.js` — the ARD manifest (excerpt)

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

The manifest has two entries, the MCP server (pointing at its card) and the booking skill. The REST API stays in the API catalog. The top-level `specVersion: '1.0'` is there because isitagentready's `ard` check requires it, while ARD says other top-level members are "transport-defined and ignored".[^ch08-31] The two graders also disagree about the address: Lighthouse 13.6.0 (27 October 2026) moved to `/.well-known/ard.json` and warns about the legacy `ai-catalog.json` location, which isitagentready's fix prompt still recommended on the same day.[^ch08-32] The specification sides with Lighthouse, and so does Nordlys.

### What the graders see

Lighthouse 13.6.0 against the demo server with all layers up to this one (headless Chromium 156, 2 November 2026) scored the Agentic Browsing category 1, and the `ard-schema` audit passed. Before the manifest existed, that audit was simply not applicable, so Lighthouse never punished us for not having one.

On isitagentready's rules, the API catalog moved Nordlys from Level 3 to Level 4, and the server card, the skills index and the ARD manifest turned `mcpServerCard`, `agentSkills` and `ard` from fail to pass without changing the level. That is why I recommend tracking checks, not levels (Chapter 12). The MCP server itself moves no check on either grader: isitagentready does not connect to your MCP endpoint and test the tools, and Lighthouse looks only at pages. A grader can verify that a file exists and has the right shape. It cannot verify that your tools are well designed or that a booking made by an agent is safe.

Some files Nordlys leaves out on purpose. An A2A agent card at `/.well-known/agent-card.json` describes an *agent*, and Nordlys has tools, not an agent (Chapter 6 explains what that costs on the level ladder).[^ch08-46] DNS-AID publishes agents in DNS records under an `_agents` label, and its specification is an individual Internet-Draft "not endorsed by the IETF".[^ch08-47] auth.md is one vendor's proposal for agents that register for services on behalf of users, and Nordlys does not let agents create accounts.[^ch08-48] Each is a reasonable item for the watch list, and none is something a small booking site needs in November 2026.

### Keeping discovery honest

Discovery files fail quietly: a stale card or a skill with last year's cancellation policy breaks nothing loudly, and clients just stop using your site, or use it wrongly. Four habits keep that from happening. Generate the files from the request origin and from data the site already has, never from hand-written JSON in a `public/.well-known/` folder. Test the agreement, not just the presence: the five discovery tests in the demos compare the card to `server/discover`, the digest to the file and the catalog to the routes. Keep one canonical copy and few mirrors. And write down why each file exists, because in this layer the next rename will come.

## Summary

- A plain HTTP API is enough when a developer configured the agent and the task is a short sequence of operations. General assistants need an MCP server or a browser.
- Describe the API with OpenAPI 3.1 and write every `operationId`, summary and description for a model. Errors are RFC 9457 problem details with a stable `type` and machine-readable codes, bookings take an `Idempotency-Key`, lists use opaque cursors, and limits explain themselves with RateLimit headers.
- The MCP server calls the same booking service as the API, so both doors share validation, error codes and idempotency keys. The 2026-07-28 revision is stateless, and the TypeScript SDK v2 builds a fresh server per request. Origin, Host and token checks are yours.
- Tools return text and validated `structuredContent`, failures come back as results with `isError`, and annotations are hints for hosts, not security.
- Test with the SDK's real client in-process and with MCP Inspector 2.13.0, and expect somebody to add your server by hand in every host.
- Discovery files are read mostly by graders and registries in November 2026, so keep them cheap: a `Link` header that every layer appends to, an API catalog that lists the API and the MCP endpoint, a server card next to the endpoint plus one mirror, OAuth metadata, an Agent Skills index with digests and an ARD manifest with representative queries.
- Generate discovery files and test that they agree with the live interface. Track checks, not levels, and skip files that would describe something your site does not do.

[^ch08-1]: "Custom GPT retirement and migration FAQ," OpenAI Help Center, https://help.openai.com/en/articles/20001519-custom-gpt-retirement-and-migration-faq (read as a search result, the page refused direct requests), and "OpenAI Custom GPT Retirement Puts Integrations on the Migration Checklist," ADTmag, 28 September 2026, https://adtmag.com/articles/2026/09/28/openai-custom-gpt-retirement-puts-integrations-on-the-migration-checklist.aspx (both retrieved November 2026).
[^ch08-2]: "Expose REST API as MCP server," Azure API Management documentation, Microsoft Learn, https://learn.microsoft.com/en-us/azure/api-management/export-rest-mcp-server (retrieved November 2026).
[^ch08-3]: "Amazon Bedrock AgentCore Gateway: A secure AI gateway for agents, tools, and models," AWS documentation, https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway.html (retrieved November 2026).
[^ch08-4]: "Extend your agent with tools from a REST API (preview)," Microsoft Copilot Studio documentation, https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-extend-action-rest-api, and "OpenAPI tools," Agent Development Kit documentation, https://adk.dev/tools-custom/openapi-tools/ (both retrieved November 2026).
[^ch08-5]: "OpenAPI Specification v3.2.0," 19 September 2025, https://spec.openapis.org/oas/v3.2.0.html, "OpenAPI Specification v3.2.1," 10 September 2026, https://spec.openapis.org/oas/v3.2.1.html, and "OpenAPI Specification v3.1.2," https://spec.openapis.org/oas/v3.1.2.html, OpenAPI Initiative (all retrieved November 2026).
[^ch08-6]: "@scalar/openapi-parser," npm registry, https://registry.npmjs.org/@scalar/openapi-parser (version 0.29.19, retrieved November 2026).
[^ch08-7]: RFC 9457, "Problem Details for HTTP APIs," RFC Editor, https://www.rfc-editor.org/rfc/rfc9457.html (retrieved November 2026).
[^ch08-8]: draft-ietf-httpapi-idempotency-key-header-08, "The Idempotency-Key HTTP Header Field," IETF, https://datatracker.ietf.org/doc/draft-ietf-httpapi-idempotency-key-header/ (retrieved November 2026).
[^ch08-9]: "Idempotent requests," Stripe API reference, https://docs.stripe.com/api/idempotent_requests (retrieved November 2026).
[^ch08-10]: draft-ietf-httpapi-ratelimit-headers-11, "RateLimit header fields for HTTP," IETF, https://datatracker.ietf.org/doc/draft-ietf-httpapi-ratelimit-headers/ (retrieved November 2026).
[^ch08-11]: "The Arazzo Specification v1.1.0," OpenAPI Initiative, https://spec.openapis.org/arazzo/v1.1.0.html (retrieved November 2026).
[^ch08-12]: "MCP joins the Agentic AI Foundation," Model Context Protocol blog, 9 December 2025, https://blog.modelcontextprotocol.io/posts/2025-12-09-mcp-joins-agentic-ai-foundation/ (retrieved November 2026).
[^ch08-13]: "Get started with custom connectors using remote MCP," Claude Help Center, https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp (retrieved November 2026).
[^ch08-14]: "Plugin development for ChatGPT and Codex," OpenAI Developers, https://developers.openai.com/apps-sdk, and "Build an MCP server," https://developers.openai.com/apps-sdk/build/mcp-server (both retrieved November 2026).
[^ch08-15]: "Extend your agent with Model Context Protocol," Microsoft Copilot Studio documentation, https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-extend-action-mcp (retrieved November 2026).
[^ch08-16]: "Add MCP servers in VS Code," Visual Studio Code documentation, https://code.visualstudio.com/docs/copilot/customization/mcp-servers (retrieved November 2026).
[^ch08-17]: "Set up your custom MCP server connection," Gemini Enterprise Business Edition Help, https://support.google.com/g/answer/17106276 (updated 15 September 2026, retrieved November 2026).
[^ch08-18]: "Key changes," Model Context Protocol specification 2026-07-28, https://modelcontextprotocol.io/specification/2026-07-28/changelog (retrieved November 2026).
[^ch08-19]: "The 2026-07-28 Specification," Model Context Protocol blog, https://blog.modelcontextprotocol.io/posts/2026-07-28/ (retrieved November 2026).
[^ch08-20]: "Roadmap," Model Context Protocol, https://modelcontextprotocol.io/development/roadmap (retrieved November 2026).
[^ch08-21]: "Beta SDKs for the 2026-07-28 MCP Spec Release Candidate Are Here," Model Context Protocol blog, https://blog.modelcontextprotocol.io/posts/sdk-betas-2026-07-28/, and the npm registry entries https://registry.npmjs.org/@modelcontextprotocol%2fserver and https://registry.npmjs.org/zod (all retrieved November 2026).
[^ch08-22]: "Serve over HTTP," MCP TypeScript SDK v2 documentation, https://ts.sdk.modelcontextprotocol.io/v2/serving/http (retrieved November 2026).
[^ch08-23]: "Tool Annotations as Risk Vocabulary: What Hints Can and Can't Do," Model Context Protocol blog, 16 March 2026, https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/ (retrieved November 2026).
[^ch08-24]: "Tools," section "Security considerations," Model Context Protocol specification 2026-07-28, https://modelcontextprotocol.io/specification/2026-07-28/server/tools (retrieved November 2026).
[^ch08-25]: "MCP Apps: Bringing UI Capabilities To MCP Clients," Model Context Protocol blog, 26 January 2026, https://blog.modelcontextprotocol.io/posts/2026-01-26-mcp-apps/ (retrieved November 2026).
[^ch08-26]: Demos repository, `nordlys-cabins/layers/08-mcp-server/` and `nordlys-cabins/tests/ch08-mcp-server.test.js`, https://github.com/webmaxru/agent-ready-web-demos (retrieved November 2026).
[^ch08-27]: "@modelcontextprotocol/inspector," npm registry, https://registry.npmjs.org/@modelcontextprotocol%2finspector (version 2.13.0, retrieved November 2026).
[^ch08-28]: "MCP Server," Cloudflare Agents documentation, https://developers.cloudflare.com/agents/model-context-protocol/apis/handler-api/ (retrieved November 2026).
[^ch08-29]: "Deploy MCP servers to Vercel," Vercel documentation, https://vercel.com/docs/mcp/deploy-mcp-servers-to-vercel (retrieved November 2026).
[^ch08-30]: "Self-hosted remote MCP server on Azure Functions (public preview)," Microsoft Learn, https://learn.microsoft.com/en-us/azure/azure-functions/self-hosted-mcp-servers, and "Deploy MCP servers in AgentCore Runtime," AWS documentation, https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-mcp.html (both retrieved November 2026).
[^ch08-31]: "Is Your Site Agent-Ready? (llms-full.txt)," isitagentready.com, Cloudflare, https://isitagentready.com/llms-full.txt (retrieved November 2026).
[^ch08-32]: "ARD manifest is valid," Lighthouse documentation, Chrome for Developers, https://developer.chrome.com/docs/lighthouse/agentic-browsing/ard (retrieved November 2026).
[^ch08-33]: "AI Insights: Adoption of AI agent standards," Cloudflare Radar, https://radar.cloudflare.com/ai-insights#adoption-of-ai-agent-standards (data dated 2 November 2026, retrieved November 2026).
[^ch08-34]: "Well-Known URIs," IANA registry (last updated 26 October 2026), https://www.iana.org/assignments/well-known-uris/well-known-uris.xhtml (retrieved November 2026).
[^ch08-35]: M. Nottingham, "Web Linking," RFC 8288, IETF, https://www.rfc-editor.org/rfc/rfc8288.html (retrieved November 2026).
[^ch08-36]: Junjie Bu, R.V. Guha and Shaun Smith, "Agentic Resource Discovery Specification," version 0.91 (Proposal), 26 August 2026, https://agenticresourcediscovery.org/spec/ (retrieved November 2026).
[^ch08-37]: RFC 9727, "api-catalog: A Well-Known URI and Link Relation to Help Discovery of APIs," https://www.rfc-editor.org/rfc/rfc9727.html, RFC 9264, "Linkset: Media Types and a Link Relation Type for Link Sets," https://www.rfc-editor.org/rfc/rfc9264.html, and RFC 8631, "Link Relation Types for Web Services," https://www.rfc-editor.org/rfc/rfc8631.html, RFC Editor (all retrieved November 2026).
[^ch08-38]: "AI Insights: Adoption of AI agent standards," Cloudflare Radar, https://radar.cloudflare.com/ai-insights#adoption-of-ai-agent-standards (data dated 2 November 2026, retrieved November 2026).
[^ch08-39]: "SEP-2127: MCP Server Cards - HTTP Server Discovery," Model Context Protocol, https://modelcontextprotocol.io/seps/2127-mcp-server-cards (retrieved November 2026).
[^ch08-40]: André Jesus and Vance Morrison, "Introducing the Agent Readiness score. Is your site agent-ready?," The Cloudflare Blog, 17 April 2026, https://blog.cloudflare.com/agent-readiness/ (retrieved November 2026).
[^ch08-41]: "MCP Server Cards (Experimental Extension)," GitHub, https://github.com/modelcontextprotocol/ext-server-card (retrieved November 2026).
[^ch08-42]: M.B. Jones, P. Hunt and A. Parecki, "OAuth 2.0 Protected Resource Metadata," RFC 9728, IETF, https://www.rfc-editor.org/rfc/rfc9728.html (retrieved November 2026).
[^ch08-43]: "Specification," Agent Skills, https://agentskills.io/specification (retrieved November 2026).
[^ch08-44]: "Agent Skills Discovery via Well-Known URIs," version 0.2.0 (Draft), Cloudflare on GitHub, https://github.com/cloudflare/agent-skills-discovery-rfc (retrieved November 2026).
[^ch08-45]: "Is Your Site Agent-Ready?," isitagentready.com, Cloudflare, https://isitagentready.com/ (scans of 44 sites run on 2 November 2026 while researching this book, results in the author's research notes) (retrieved November 2026).
[^ch08-46]: "Agent2Agent (A2A) Protocol Specification," version 1.0, A2A Project, https://a2a-protocol.org/latest/specification/ (retrieved November 2026).
[^ch08-47]: "DNS for AI Discovery," draft-mozleywilliams-dnsop-dnsaid-02, IETF Datatracker, https://datatracker.ietf.org/doc/draft-mozleywilliams-dnsop-dnsaid/ (retrieved November 2026).
[^ch08-48]: "auth.md: An open protocol that lets agents register for services on behalf of users," WorkOS on GitHub, https://github.com/workos/auth.md (retrieved November 2026).
