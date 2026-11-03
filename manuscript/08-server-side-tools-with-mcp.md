# Chapter 8: Server-side tools with the Model Context Protocol

This chapter covers

- What the Model Context Protocol gives a website owner, and which assistants connect to remote MCP servers in November 2026
- The stateless 2026-07-28 revision: `server/discover`, per-request metadata and the new HTTP headers
- Building the Nordlys MCP server with the TypeScript SDK v2, next to the API and on the same booking logic
- Tools with structured output and annotations, resources and prompts
- Testing with a real MCP client and MCP Inspector, and where to host the server
- What to keep in mind when you follow a tutorial written for the 2025 protocol

In Chapter 7 we gave Nordlys Cabins a clean public API. A travel agency's developer can read the OpenAPI description, write a client and book cabins. But a person who opens Claude or ChatGPT and types "find me a cabin with a sauna in Norway for the first week of December" will not get anything from that API. General assistants do not read random OpenAPI files. They connect to MCP servers.

The Model Context Protocol (MCP) is how most AI hosts talk to outside tools in 2026. Anthropic introduced it in November 2024, and in December 2025 it moved to the Agentic AI Foundation, a fund under the Linux Foundation co-founded by Anthropic, Block and OpenAI.[^ch08-1] The TypeScript, Python, Go and C# SDKs are maintained as "Tier 1", and the maintainers reported "close to half-a-billion downloads a month" across those SDKs in July 2026.[^ch08-2] Those numbers come from the project itself, so read them as an order of magnitude. Still, the direction is clear: if you want a general assistant to do something on your site, MCP is the most common door.

This chapter builds that door for Nordlys, from the site owner's point of view. We do not write a desktop plugin or a local tool that reads files on someone's laptop. We write a remote MCP server: an HTTPS endpoint at `/mcp` on our own domain, next to the API, calling the very same booking service. At the end, a real MCP client can search cabins, check prices and book, and the tests prove that a booking made through MCP and a booking made through the API are the same thing.

> **Note:** The first three sections explain MCP for the whole team, without code. Product managers and designers can read them and then jump to "Who sees what: annotations and confirmations" and "Where to host it". The code sections start with a Hands-on callout.

## MCP in five minutes

Let's start with the vocabulary, because MCP has three roles and people mix them up all the time.

- The **host** is the application a person uses: Claude, ChatGPT, Copilot, VS Code, Cursor and others. It runs the model and decides what to show the user.
- The **client** lives inside the host. It keeps one connection to one server and speaks the protocol.
- The **server** is what you build. It offers capabilities to any client that connects.

A server offers three kinds of things:

- **Tools** are functions the model can call: `search_cabins`, `create_booking`. Each tool has a name, a description and a JSON Schema for its input, and optionally for its output.
- **Resources** are data the host can read and put into the model's context: a guide article, a cancellation policy. They are identified by URIs.
- **Prompts** are templates a person can pick in the host's interface ("Plan a cabin trip"). They are the least used of the three, but they are a nice way to show users what your server is good at.

Under the hood, MCP is JSON-RPC 2.0. For a remote server, the transport is called Streamable HTTP: the client sends each request as an HTTP POST to one endpoint, and the server answers with JSON, or with a short Server-Sent Events stream when it has progress to report. Figure 8.1 puts the pieces together for Nordlys.

![Figure 8.1 — The Nordlys MCP server. A host such as Claude or ChatGPT runs an MCP client that sends JSON-RPC requests over HTTPS to /mcp. A fresh server object answers each request, built from a registry of tools, resources and prompts. The tools call the same booking service as the public API of Chapter 7.](images/figure-8-1.png)

What do you get as a site owner? In simple words: your capabilities show up inside the assistant, described in your words, and the assistant calls them instead of scraping your pages or guessing. The user stays in the conversation, and your server stays in control of what actually happens (validation, prices, availability, idempotency). Compared with a browser agent clicking through the booking form, that is faster, cheaper and much more reliable.

What does it cost? Another endpoint to secure, monitor and keep compatible, much like the API of Chapter 7. If you built the API on a shared service layer, as we did, the MCP server is mostly a thin translation layer. The Nordlys tools, resources and prompt are about 230 lines, and most of those lines are descriptions and schemas.

## Who connects to remote MCP servers

A protocol is only as useful as its clients. Here is the situation for remote MCP servers as I found it in November 2026. Plans and limits change often, so treat this as a snapshot and check the vendor pages before you promise anything to your stakeholders.

| Host | Remote MCP support (November 2026) |
|---|---|
| Claude (Anthropic) | "Custom connectors" on all plans, with Free limited to one connector[^ch08-3] |
| ChatGPT and Codex (OpenAI) | MCP servers power plugins (the former "Apps SDK" documentation is now titled "Plugin development for ChatGPT and Codex")[^ch08-4] |
| Microsoft Copilot Studio | An onboarding wizard connects agents to existing MCP servers[^ch08-5] |
| Visual Studio Code | MCP servers can be added for GitHub Copilot in VS Code[^ch08-6] |
| Gemini Enterprise | Custom MCP server connections, Pre-GA and configured by an admin[^ch08-7] |

Two observations. First, in every one of these hosts, somebody still has to add your server: a user pastes a URL, an admin approves a connector, or a developer edits a configuration file. There is no global "MCP search" that assistants consult on their own yet. Chapter 11 covers the discovery files that will help with that (server cards, catalogs and registries), and why they are still in flux.

Second, OpenAI's documentation gives one piece of advice I recommend to everybody: the server's `instructions` (a short text the server sends to describe itself) are read by ChatGPT and Codex, and "the most important details" belong in the first 512 characters. The Nordlys instructions are 309 characters long, and they say what the server is for and the one rule that matters most: book only after the user confirmed.

## What changed in the 2026-07-28 revision

If you read an MCP tutorial from 2025, a lot of what follows will look different. The current specification revision is dated 2026-07-28, and it is the biggest change since remote servers became a thing.[^ch08-8] The headline: MCP is now stateless.

In the 2025 revisions, a client opened a session with an `initialize` handshake, the server returned an `Mcp-Session-Id`, and every later request carried that ID. Servers had to remember sessions, which made load balancing and serverless hosting painful. The 2026-07-28 revision removes all of that:

- **No handshake and no sessions.** The `initialize` request and the `Mcp-Session-Id` header are gone. Every request carries the protocol version, the client's capabilities and (optionally) the client's identity in its `_meta` field.
- **`server/discover` is mandatory.** A client that wants to know what a server supports asks `server/discover`, and servers must implement it.
- **Routing headers.** Every POST carries `Mcp-Method` (and `Mcp-Name` for calls such as `tools/call`) as HTTP headers, so a gateway or a web application firewall can route or filter requests without parsing the JSON body.
- **Caching hints.** List and read results carry `ttlMs` and `cacheScope`, and servers should return `tools/list` in a deterministic order, which helps clients cache and helps models reuse prompt caches.
- **No server-initiated requests.** When a tool needs more input from the user (a confirmation, a missing value), it returns a result with `resultType: "input_required"`, and the client sends a new request. These are called Multi Round-Trip Requests.
- **Deprecations.** Roots, Sampling, Logging and the old HTTP+SSE transport are deprecated, with a minimum twelve-month window. Tasks moved out of the core into an extension.

The release post sums up why this matters for anyone who runs servers: "any request can land on any instance behind a plain round-robin load balancer".[^ch08-9] Personally for me, this is the change that makes MCP a normal web workload. You can run it on the same infrastructure as your API, scale it the same way and cache it the same way.

> **Still in flux:** Stateless MCP is three months old as I write this. The official SDKs support it, but not every host does yet, which is why the TypeScript SDK serves both protocol eras from one endpoint by default. We keep that default in Nordlys, and the tests cover both eras.

### One request, from the wire

> **Hands-on:** Here we look at raw requests with curl. If you don't use a terminal, the takeaway is this: a modern MCP request is an ordinary HTTP POST that carries its method in a header and its protocol version in both a header and the body, and the server answers in one response. Continue with "Building the Nordlys server" or, if you skip all code, with "Who sees what: annotations and confirmations".

Let's ask the running Nordlys server what it is. This is the `server/discover` request with curl (start the demo first with `npm start -- --upto=8 --port=4810`):

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

And the answer, formatted for reading:

```json
{
  "result": {
    "supportedVersions": [
      "2026-07-28"
    ],
    "capabilities": {
      "tools": {
        "listChanged": true
      },
      "resources": {
        "listChanged": true
      },
      "prompts": {
        "listChanged": true
      }
    },
    "instructions": "Nordlys Cabins rents holiday cabins in Norway. Use search_cabins to find cabins, check_availability to get the exact price, and create_booking only after the user confirmed the cabin, dates, guests and total. Prices are NOK. Dates are YYYY-MM-DD in Europe/Oslo. Free cancellation ends 14 days before check-in.",
    "resultType": "complete",
    "ttlMs": 0,
    "cacheScope": "private",
    "_meta": {
      "io.modelcontextprotocol/serverInfo": {
        "name": "nordlys-cabins",
        "title": "Nordlys Cabins",
        "version": "1.0.0"
      }
    }
  },
  "jsonrpc": "2.0",
  "id": 1
}
```

Everything a client needs to start is here: the supported protocol versions, the capabilities (tools, resources and prompts, each able to announce changes), the instructions and the server's identity in `_meta`. `ttlMs: 0` and `cacheScope: "private"` tell the client not to cache this answer, which is the SDK's default.

What happens if a client gets the envelope wrong? The 2026-07-28 rules are strict, and the SDK enforces them. A request with the version header but without `_meta` is refused:

```json
{"jsonrpc":"2.0","error":{"code":-32602,"message":"Invalid params: the MCP-Protocol-Version header names protocol revision 2026-07-28, but the request is missing the required per-request envelope key(s): _meta","data":{"envelope":{"missing":["_meta"]}}},"id":5}
```

And a `tools/call` whose `Mcp-Name` header names one tool while the body names another gets the error code -32020 with the message "the request headers and body disagree". That check exists so a firewall that filters on headers cannot be tricked by a different body. You don't need to implement any of this yourself, but it helps to know these errors when a client author asks why their requests fail.
## Choosing the tools

Before any code, a design question that product people should own: which tools should the server offer? The tempting answer is "one tool per API operation". Gateways do exactly that, and for Nordlys it would give us five tools. I chose four, and the difference is worth a few paragraphs.

Every tool you add costs something. Its name, description and schema go into the model's context in every conversation where your server is connected, next to the tools of every other server the user connected. More tools mean more tokens, and more chances that the model picks the wrong one. The MCP maintainers know this well: "progressive discovery" (letting clients load tools on demand instead of all at once) is on the 2026 roadmap exactly because servers with dozens of tools overwhelm models.[^ch08-10]

So I asked one question per API operation: does a guest's conversation need this as a separate step?

- `searchCabins` becomes `search_cabins`. This is where every conversation starts.
- `getCabin` does not become a tool. Search results already carry what a model needs to compare cabins (region, size, features, prices), and each result links to the cabin page for people. If a conversation needs long descriptions, the host can read the guide resources.
- `checkAvailability` becomes `check_availability`. The exact total, with weekend nights and the cleaning fee, is the number a person must see before they book.
- `createBooking` and `cancelBooking` become `create_booking` and `cancel_booking`.

There is a second difference from the API: the tool descriptions talk about the conversation, not about HTTP. The OpenAPI description of `createBooking` explains status codes and headers. The tool description of `create_booking` says when to call it in a dialogue ("only after the user confirmed the cabin, dates, guests and the total from check_availability") and what to say afterwards. Same operation, different reader.

> **Tip:** Write the tool list for your site on a whiteboard before you write code, together with a few real requests from customers ("a cabin for six with a sauna near Tromsø in March"). For each request, walk through the tools a model would call. Missing tools and useless tools both become obvious within minutes. Chapter 10 turns this exercise into a repeatable evaluation.

## Building the Nordlys server

> **Hands-on:** This section adds the SDK, writes the server factory and mounts it at `/mcp`. If you don't write code, here is what it achieves: one function builds the MCP server from a list of tools, the web app hands every request on `/mcp` to that function, and a small check makes sure that only our own web pages (and non-browser clients) can call it. Pick up again at "Who sees what: annotations and confirmations".

### The SDK and its versions

The TypeScript SDK went through a big restructuring in 2026. Version 2 splits the old single package into `@modelcontextprotocol/server`, `@modelcontextprotocol/client` and small adapters for Node, Express, Hono and Fastify. It is ESM-only, needs Node 20 or newer (Bun and Deno work too), and accepts any Standard Schema library for input and output schemas, Zod v4 among them.[^ch08-11] On 2 November 2026 the npm registry lists `@modelcontextprotocol/server` 2.4.0 (published 23 October 2026), `@modelcontextprotocol/client` 2.4.0 and `zod` 4.6.7. Those are the versions Nordlys uses.

The demo app runs on Hono, but I did not need the Hono adapter. SDK v2 has a function, `createMcpHandler`, that returns a handler with a standard `fetch(request)` method: a Web `Request` goes in, a `Response` comes out.[^ch08-12] Any framework or runtime that speaks Web `fetch` (Hono, Cloudflare Workers, Deno, Bun, Next.js route handlers) can mount it in one line.

> **Tip:** The old single package `@modelcontextprotocol/sdk` still exists (version 1.32.2 in October 2026) and many tutorials use it. If you have a v1 server, the SDK team ships a codemod: `npx @modelcontextprotocol/codemod@beta v1-to-v2 .`

### A server per request

Listing 8.1 is the whole server factory.

**Listing 8.1** `nordlys-cabins/layers/08-mcp-server/server.js` — the server factory

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

Three things to notice.

The server gets a name, a title, a version and the `instructions` we discussed earlier. These are what `server/discover` returned in the curl example.

The tools, resources and prompts do not live in this file. They come from a registry (`mcpRegistry(ctx)`), which this chapter's layer fills, and which later chapters can extend. We look at the registry in its own section, because it is the part of this layer that other chapters depend on.

And every handler gets an `extra` object with `auth`, `request`, `ctx`, `store` and the SDK's own context. `auth` is `null` in this chapter. In Chapter 14, a layer that verifies OAuth tokens fills it, and tools can then act for a signed-in guest without any change here.

### Mounting it at /mcp

Listing 8.2 shows how the layer mounts the handler.

**Listing 8.2** `nordlys-cabins/layers/08-mcp-server/index.js` — mounting the handler at /mcp (excerpt)

```js
    const handler = createMcpHandler((requestContext) => createNordlysServer(ctx, requestContext));

    ctx.mcp(async (c) => {
      // The SDK handler checks no Origin, Host or token itself. Browsers send an
      // Origin header: only our own site may call /mcp from a web page.
      const ownHost = new URL(ctx.absoluteUrl(c, '/')).hostname;
      const rejected = originValidationResponse(c.req.raw, [ownHost, new URL(c.req.url).hostname]);
      if (rejected) return rejected;
      // A later layer (Chapter 14) verifies a bearer token and stores the result
      // with c.set('mcpAuth', authInfo). Until then every caller is anonymous.
      return handler.fetch(c.req.raw, { authInfo: c.get('mcpAuth') ?? undefined });
    });
```

`createMcpHandler` takes a factory and calls it once per HTTP request. That is how the SDK implements statelessness: no server object survives between requests, so any instance can answer any request. It also means anything registered in the registry is live on the very next request.

The SDK documentation is refreshingly direct about what the handler does not do: "it validates no Host header, no Origin header, and no token".[^ch08-12] Those checks are yours. The Origin check matters because a remote MCP server is an HTTP endpoint like any other, and a malicious web page could try to call it from a visitor's browser. Browsers always send an `Origin` header on such requests. Non-browser clients (the hosts in the table earlier) normally do not. So the layer uses the SDK's helper `originValidationResponse` to refuse any request whose `Origin` is not our own site. Here is what an attacker's page gets:

```http
HTTP/1.1 403 Forbidden
content-type: application/json

{"jsonrpc":"2.0","error":{"code":-32000,"message":"Invalid Origin: evil.example"},"id":null}
```

The token check comes in Chapter 14, through `c.get('mcpAuth')`. Until then, every caller is anonymous, which is fine for a server that offers the same operations as the public website.

> **Warning:** "Anonymous" does not mean "unlimited". The Chapter 7 rate limiter covers only `/api/` paths. If you expose MCP publicly, put the same kind of limit in front of `/mcp` at your edge or in your app. Chapter 15 discusses how to tell good agents from bad bots.

## Tools that agents call correctly

> **Hands-on:** One tool definition in full, then the real exchange. If you don't write code, the idea is that each tool declares what it needs (input schema), what it returns (output schema) and how risky it is (annotations), and the server returns both a text and a structured version of each result. Pick up again at "Who sees what: annotations and confirmations".

Nordlys has four tools, mirroring the API operations a guest needs: `search_cabins`, `check_availability`, `create_booking` and `cancel_booking`. Note the names: snake_case, verb first. The specification only says tool names should be 1 to 128 characters from a restricted character set, and both styles work.[^ch08-13] I use snake_case for MCP tools because it is what most MCP servers I have seen use, and keep camelCase for the OpenAPI `operationId`s of Chapter 7, which is the OpenAPI convention.

Listing 8.3 is the `check_availability` tool.

**Listing 8.3** `nordlys-cabins/layers/08-mcp-server/tools.js` — the check_availability tool (excerpt)

```js
    'check_availability',
    {
      title: 'Check availability and price',
      description:
        'Check if one cabin is free for a stay and get the exact total price. ' +
        'Call this before create_booking and tell the user the total. available=false means the dates are taken.',
      inputSchema: z.object({
        cabin: z.string().describe('Cabin slug from search_cabins, for example fjellro'),
        checkIn: date('Arrival'),
        checkOut: date('Departure'),
        guests: z.number().int().min(1),
      }),
      outputSchema: z.object({
        cabin: z.string(),
        checkIn: z.string(),
        checkOut: z.string(),
        guests: z.number().int(),
        available: z.boolean(),
        conflicts: z.array(z.object({ from: z.string(), to: z.string() })),
        quote: z.object({ currency: z.literal('NOK'), nights: z.number().int(), accommodation: z.number().int(), cleaningFee: z.number().int(), total: z.number().int() }),
      }),
      annotations: { readOnlyHint: true, openWorldHint: false },
    },
    async (args) => {
      const r = service.checkAvailability(args);
      return r.ok ? ok(r.value) : failed(r.errors);
    },
    OWNER
```

The input schema is written with Zod and converted by the SDK into JSON Schema 2020-12, which is what clients see in `tools/list`. The 2026-07-28 revision allows any JSON Schema 2020-12 keyword in input and output schemas, so patterns, enums and descriptions all survive. The `.describe()` texts become `description` fields, and they are part of what the model reads. "Cabin slug from search_cabins, for example fjellro" tells the model where the value comes from, which prevents it from inventing cabin names.

### Structured output

The `outputSchema` declares the shape of the result, and the handler returns the result twice: as `structuredContent` (an object that matches the schema) and as a text block. Here is the real `tools/call` response for Fjellro, 2 to 5 December 2026, four guests:

```json
{
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"cabin\":\"fjellro\",\"checkIn\":\"2026-12-02\",\"checkOut\":\"2026-12-05\",\"guests\":4,\"available\":true,\"conflicts\":[],\"quote\":{\"currency\":\"NOK\",\"nights\":3,\"accommodation\":7000,\"cleaningFee\":900,\"total\":7900}}"
      }
    ],
    "structuredContent": {
      "cabin": "fjellro",
      "checkIn": "2026-12-02",
      "checkOut": "2026-12-05",
      "guests": 4,
      "available": true,
      "conflicts": [],
      "quote": {
        "currency": "NOK",
        "nights": 3,
        "accommodation": 7000,
        "cleaningFee": 900,
        "total": 7900
      }
    },
    "resultType": "complete",
    "_meta": {
      "io.modelcontextprotocol/serverInfo": {
        "name": "nordlys-cabins",
        "title": "Nordlys Cabins",
        "version": "1.0.0"
      }
    }
  },
  "jsonrpc": "2.0",
  "id": 3
}
```

Why both? The text is what most hosts put into the model's context. The structured content is what code can rely on: a host that renders a price card, a test, a workflow engine. The MCP roadmap even calls out that returning both "has confused server and client authors" and plans a redesign of the result shape.[^ch08-10] Until that lands, returning both is the safest choice, and the SDK validates `structuredContent` against your `outputSchema`, so the two cannot drift apart silently.

### Errors the model can act on

What happens when the input is wrong? Let's ask for Fjellro with twelve guests:

```json
{"result":{"content":[{"type":"text","text":"guests: Fjellro sleeps up to 6 guests. (too_many_guests)"}],"isError":true,"resultType":"complete","_meta":{"io.modelcontextprotocol/serverInfo":{"name":"nordlys-cabins","title":"Nordlys Cabins","version":"1.0.0"}}},"jsonrpc":"2.0","id":4}
```

This is a normal result with `isError: true`, not a protocol error. That distinction matters. A JSON-RPC error tells the client that the request was broken (a wrong method, an invalid envelope). A tool result with `isError` tells the model that the call worked but the action failed, and gives it text to reason about. The text is the same field, message and code that the API returns as problem details in Chapter 7: `guests`, "Fjellro sleeps up to 6 guests.", `too_many_guests`. One booking service, one set of error codes, two renderings.

### Booking through MCP, safely

`create_booking` follows the same rules as the API, adapted to a tool:

- **An `idempotencyKey` argument.** MCP has no request headers for tool arguments, so the key travels as an input field. The handler passes it to the same `createBooking` function as the API, so a retry through MCP returns the original booking, and a booking made through MCP with a key cannot be repeated through the API with the same key. The Chapter 8 tests check exactly this.
- **`acceptTerms` as a literal `true`.** The schema accepts only `true`, and the description says "The user accepted the booking terms. Never set this without asking."
- **A result without the guest's name.** The tool returns the booking reference, dates, total and free-cancellation date, and leaves out personal data the model does not need. A model cannot leak what it never saw.
- **A short text summary.** "Booked fjellro from 2026-12-02 to 2026-12-05. Reference NC-…, total 7900 NOK." is what the model reads and repeats to the user.

The description of `create_booking` starts with "Only call this after the user confirmed the cabin, dates, guests and the total from check_availability". That is the same instruction as in the OpenAPI description, and it has the same weakness: a description is a request, not a guarantee. Which brings us to annotations.
## Who sees what: annotations and confirmations

Every Nordlys tool carries annotations, small hints that describe its behavior. MCP has had them since the 2025-03-26 revision, and there are five: `title`, `readOnlyHint`, `destructiveHint`, `idempotentHint` and `openWorldHint`.[^ch08-14] Here is how Nordlys sets them, and why:

| Tool | readOnly | destructive | idempotent | openWorld | Reasoning |
|---|---|---|---|---|---|
| `search_cabins` | true | | | false | Only reads Nordlys data |
| `check_availability` | true | | | false | Only reads, nothing is held or reserved |
| `create_booking` | false | false | true | false | Creates a booking, but never destroys anything, and the same key returns the same booking |
| `cancel_booking` | false | true | true | false | Cancelling cannot be undone, and a second cancel changes nothing |

`openWorldHint: false` says that a tool works within a closed domain (our own booking system) rather than reaching out to the open internet. A web search tool would be `true`.

Hosts use annotations to decide how much friction to add. A host may run read-only tools without asking and show a confirmation before a destructive one. That is useful, and it is the reason I set annotations carefully on every tool. But please read the next sentence twice. Annotations are hints, not security. The specification says clients must treat them as untrusted unless the server itself is trusted, and that "there SHOULD always be a human in the loop with the ability to deny tool invocations".[^ch08-15] A malicious server can label a destructive tool as read-only, and a sloppy host can ignore a correct label.

So who makes sure a booking is confirmed? In this chapter, three layers do, none of them perfect alone: the description that tells the model to confirm first, the `acceptTerms` literal that forces the model to state that the user agreed, and the host's own confirmation UI, triggered by the annotations. For a cancellation or a payment that is not enough, and the 2026-07-28 revision has a better tool for it: a server can answer a call with `resultType: "input_required"` and ask the user directly, through the host, before it acts. Chapter 17 adds a booking tool that uses exactly that pattern, and discusses confirmations and the human in the loop in depth.

### What about interactive UI?

You may have heard of MCP Apps. It is the first official MCP extension (January 2026), built on earlier work from the MCP-UI project and OpenAI's Apps SDK, and it lets a tool return an interactive interface that the host renders in a sandboxed iframe: a map of cabins, a date picker, a price breakdown.[^ch08-16] Claude, Goose, VS Code Insiders and ChatGPT supported it at launch.

For Nordlys I left it out. A booking flow with a custom UI inside the assistant is attractive, but it is a second front end to design, test and keep accessible, and it only works in hosts that support the extension. The plain tools work everywhere. If your product team wants a branded experience inside ChatGPT or Claude, MCP Apps is the standard way to build it, and the server we build here is the right foundation, because an app is just a tool with a UI resource attached.

## Resources and a prompt

> **Hands-on:** One short listing with a resource template. If you don't write code, resources are documents your server offers to the assistant (here, the travel guide and the cancellation policy), and prompts are ready-made starting points a person can pick. Pick up again at "A registry for later chapters".

Tools are what agents call. Resources are what hosts read. Nordlys offers two kinds:

- **The cabin guide articles,** one resource per article, under URIs like `nordlys://guide/northern-lights-from-a-cabin`. They come from a resource template with a `list` function, so a host can show all articles and fetch any of them. Each one is returned as Markdown, converted from the same article data the website renders.
- **The cancellation policy,** a single resource at `nordlys://policies/cancellation`.

Listing 8.4 shows the guide template.

**Listing 8.4** `nordlys-cabins/layers/08-mcp-server/tools.js` — the guide articles as a resource template (excerpt)

```js
  registerMcpResource(
    ctx,
    'guide-article',
    new ResourceTemplate('nordlys://guide/{slug}', {
      list: async () => ({
        resources: ctx.store.articles().map((a) => ({ uri: `nordlys://guide/${a.slug}`, name: a.title, description: a.description, mimeType: 'text/markdown' })),
      }),
    }),
    { title: 'Cabin guide article', description: 'Practical travel advice from the Nordlys Cabins guide', mimeType: 'text/markdown' },
    async (uri, { slug }) => {
      const article = ctx.store.getArticle(String(slug));
      if (!article) throw new Error(`No guide article ${uri.href}`);
      return { contents: [{ uri: uri.href, mimeType: 'text/markdown', text: toMarkdown(article) }] };
    },
    OWNER
```

Why bother with resources when the guide is already on the website? Because a host that reads a resource gets exactly the content, in Markdown, without navigation, cookie banners or the rest of the page chrome that Chapter 6 taught us to strip. And because the policy is the same text the booking code applies, the assistant can quote the real rule instead of a paraphrase from some old travel forum.

How hosts use resources varies a lot. Some let the user attach a resource to the conversation, some let the model request one, and some ignore resources completely. That is one more reason to keep anything essential in tool results and descriptions, and to treat resources as a bonus.

The prompt, `plan_cabin_trip`, takes three arguments (when, how many guests, wishes) and produces a first message: "Help me plan a cabin trip with Nordlys Cabins for 4 people, a long weekend in February. … Use search_cabins and check_availability to suggest two or three cabins with exact prices. Do not book anything until I confirm." In hosts that show prompts (often as slash commands), this is a nice way to tell people what the server is good at, in a form they can use directly.

## A registry for later chapters

> **Hands-on:** The registry is the extension point of the Nordlys MCP server. If you don't write code, here is the idea: later chapters add tools to this server without touching this chapter's files, the same way a plugin system works. Pick up again at "Testing with a real client".

This book adds to the MCP server in three later chapters. Chapter 14 protects `/mcp` with OAuth and adds tools that act for a signed-in guest, Chapter 16 adds guarded tools and a security gateway, and Chapter 17 adds a booking tool that asks the person for confirmation. I did not want any of them to edit Chapter 8 files, because the layer system of the demo app (one folder per chapter, each building on the previous ones) depends on that. So the layer exposes a small registry. Listing 8.5 shows its main function.

**Listing 8.5** `nordlys-cabins/layers/08-mcp-server/registry.js` — registering a tool from any layer (excerpt)

```js
/**
 * Register a tool. Same arguments as McpServer.registerTool, except that the
 * handler receives a second argument: { auth, request, ctx, store, sdk }.
 * auth is whatever a later layer verified (Chapter 14), or null.
 */
export function registerMcpTool(ctx, name, config, handler, { owner = 'unknown' } = {}) {
  add(registry(ctx).tools, 'tool', name, { config, handler, owner });
}
```

A later layer imports `registerMcpTool` from `../08-mcp-server/registry.js` and calls it during its own registration. Because the server factory reads the registry on every request, the new tool appears in the next `tools/list`, after the Chapter 8 tools, in registration order (the specification asks for a deterministic order). A duplicate name throws an error that names the layer that registered it first, which turns a silent conflict into a loud one.

Figure 8.2 shows how the pieces line up, including the seam that Chapter 14 uses.

![Figure 8.2 — Extending the MCP server across chapters. Chapter 8 registers four tools, two resources and a prompt into a registry. Chapters 14, 16 and 17 add their own tools to the same registry. Chapter 14 also verifies the bearer token before the handler runs and passes the result to every tool as extra.auth. The server factory builds a fresh server from the registry on every request.](images/figure-8-2.png)

The `extra.auth` value is the important part of that seam. `createMcpHandler` accepts an `authInfo` option on each `fetch` call and passes it through to the tools. Chapter 8 passes whatever a middleware stored under `mcpAuth`, which is nothing yet. Chapter 14 adds a middleware that verifies the token and stores the result, and `create_booking` already reads `extra.auth?.member` to attach a booking to a signed-in member. No code in this chapter changes when that happens.

## Testing with a real client

> **Hands-on:** The tests and MCP Inspector. If you don't write code, here is what they prove: a real MCP client, the same library hosts use, can discover and call every tool, an old 2025 client still works, a later layer can add a tool, and a web page from another site cannot call the server. Pick up again at "Where to host it".

Unit tests that call tool handlers directly prove very little about MCP. What we want to know is whether a real client, speaking the real protocol, gets what we think it gets. The SDK makes that easy: its client can use a custom `fetch`, and our app has a `fetch` function too. Listing 8.6 connects the two, with no network and no port.

**Listing 8.6** `nordlys-cabins/tests/ch08-mcp-server.test.js` — an in-process MCP client for the tests (excerpt)

```js
/** Connect an SDK client to the app in-process: the transport's fetch goes straight to app.fetch. */
async function connect(app, mode = 'auto') {
  const transport = new StreamableHTTPClientTransport(new URL('http://127.0.0.1/mcp'), {
    fetch: (url, init) => app.fetch(new Request(url, init)),
  });
  const client = new Client({ name: 'nordlys-test', version: '1.0.0' }, mode ? { versionNegotiation: { mode } } : {});
  await client.connect(transport);
  return client;
}
```

`versionNegotiation: { mode: 'auto' }` makes the client probe the server with `server/discover` and pick the modern protocol when it is available. The seven tests in `nordlys-cabins/tests/ch08-mcp-server.test.js` then check:

- a 2026-07-28 client discovers four tools with honest annotations, in a stable order, and gets the instructions,
- search and availability return `structuredContent` next to text, and field problems come back as tool errors with their codes,
- `create_booking` is idempotent per key and books through the same service as the API,
- the guide resources and the prompt work,
- a 2025-11-25 client (with the old `initialize` handshake) is served from the same endpoint,
- a later layer can add a tool without editing Chapter 8,
- a browser page from another origin cannot call `/mcp`.

Run them with `node --test tests/ch08-*.test.js`.[^ch08-17] All seven pass with `@modelcontextprotocol/server` 2.4.0, `@modelcontextprotocol/client` 2.4.0 and Node 22.

### MCP Inspector

For exploring a server by hand, the MCP project maintains MCP Inspector.[^ch08-18] Version 2.13.0 (28 October 2026) needs Node 22.19 or newer and has three modes: a web UI (the default), a CLI and a terminal UI. With the demo running, this lists the tools from the command line:

```bash
npx @modelcontextprotocol/inspector@2.13.0 --cli http://localhost:4810/mcp --method tools/list
```

And this calls one:

```bash
npx @modelcontextprotocol/inspector@2.13.0 --cli http://localhost:4810/mcp \
  --method tools/call --tool-name check_availability \
  --tool-arg cabin=fjellro checkIn=2026-12-02 checkOut=2026-12-05 guests=4
```

The second command printed the same `structuredContent` with the total of 7,900 NOK that you saw earlier. I also ran `tools/list` with the `--strict` flag, which reports schema constructs that some clients cannot handle, and it exited with code 0 (no problems). Without `--cli`, the same command opens the web UI, where you can click through tools, resources and prompts. It is the fastest way to show a product manager what an agent will see.

> **Tip:** Add the Inspector's `--strict` check to CI next to your tests. It catches schemas that work in your SDK but break in a stricter host, and those bugs are otherwise reported by users.
## Trying it in a real host

The tests prove the protocol. At some point you also want to see your tools inside a real assistant, the way a guest would. Three practical notes from doing exactly that kind of setup.

First, remote hosts need a public HTTPS URL. Claude's custom connectors, ChatGPT plugins and Copilot Studio all call your server from the vendor's cloud, so `http://localhost:4810/mcp` does not work for them. For a quick look, a tunnel from your laptop (several vendors offer one, Cloudflare and ngrok among them) gives the local demo a temporary public address. For anything a colleague should try, deploy to a staging environment with a real certificate.

Second, editors are the easiest place to start, because they can reach `localhost`. VS Code with GitHub Copilot, for example, lets you add an HTTP MCP server by URL and then use its tools in agent mode. Configuration formats still move, though: in November 2026 the VS Code documentation describes a portable `.mcp.json` file with a top-level `mcpServers` object and labels the older `.vscode/mcp.json` destinations as deprecated, kept for compatibility.[^ch08-6] Check the current docs instead of copying a configuration from an old blog post.

Third, watch what the model does with your descriptions, not only whether the calls succeed. In a real host you see which tool it picks first, whether it asks for dates before searching, whether it repeats the total before booking. Every surprise there is a change to a description or a schema, and Chapter 10 shows how to turn those observations into tests.

> **Warning:** A staging MCP server that books real cabins is a production server. Point test hosts at a copy of your data, or make the booking tools refuse to run outside production unless a test flag is set.

## Where to host it

The Nordlys MCP server runs inside the same Node process as the website and the API. For a small site that is the simplest choice, and thanks to the stateless protocol it scales like the rest of the app: add instances behind a load balancer, and any instance answers any request. But the SDK's `fetch`-style handler runs in many places, and every big platform now documents MCP hosting. Here are the options I would consider in November 2026, with at least two per kind:

| Where | What it looks like | Good for |
|---|---|---|
| Your existing Node app (this chapter) | `createMcpHandler` mounted at `/mcp` | Sites that already run a Node backend |
| Cloudflare Workers | The `agents` package has its own `createMcpHandler` that takes an SDK v2 server factory[^ch08-19] | Edge hosting, sites already on Cloudflare |
| Vercel | The `mcp-handler` package (2.3.0) inside a Next.js App Router project[^ch08-20] | Next.js sites |
| Azure Functions | Hosting for stateless remote MCP servers over Streamable HTTP (public preview)[^ch08-21] | Teams on Azure, serverless |
| AWS | Bedrock AgentCore Runtime deploys MCP servers[^ch08-21] | Teams on AWS |
| An API gateway | Azure API Management or AgentCore Gateway generate MCP tools from your OpenAPI file (Chapter 7) | When you want no MCP code at all |

The last row deserves a comment. If your API is already well described, a gateway can give you an MCP server without writing one. What you lose is control over the tool layer: tool names come from `operationId`s, descriptions from your OpenAPI text, and you cannot easily add resources, prompts, structured output tailored for models, or tools that combine several API calls. For Nordlys I prefer a hand-written server, because the tool descriptions and the booking rules are the product. For a company with fifty internal APIs, a gateway is probably the only realistic start.

Whatever you choose, three things do not change. You check the `Origin` header (or your platform does it for you, check the docs). You protect anything personal with OAuth (Chapter 14). And you log tool calls with enough detail to answer the question "what did the agent do, and for whom?" (Chapters 16 and 19).

## Notes for readers of 2025 tutorials

Most MCP tutorials, blog posts and conference talks you will find were written for the 2025 revisions. They are not wrong, they describe an older protocol. Here is how to translate them.

- **"First the client sends `initialize`."** That was the 2025 handshake. Modern clients send `server/discover` when they need to know what a server supports, and every request carries its version in `_meta`.
- **"Store the `Mcp-Session-Id`."** Sessions are gone. If your tool needs to remember something between calls (a shopping cart, a draft booking), mint an ID in one tool result and have the model pass it back as an argument to the next tool. The release post recommends exactly this.
- **"Open an SSE stream for server messages."** The old HTTP+SSE transport is deprecated. Streamable HTTP still uses a short SSE response when a server streams progress, and a client that wants change notifications opens a single `subscriptions/listen` stream.
- **"Use `server.tool(...)` from `@modelcontextprotocol/sdk`."** That is the v1 SDK, whose later versions also had `registerTool`. In v2, `registerTool` on `McpServer` from `@modelcontextprotocol/server` is the way to go.
- **OpenAI's plugin documentation** still shows the v1 SDK in its MCP server example (as of November 2026). It works, but new servers should start on v2.

The good news is that you do not have to choose. The SDK's handler serves 2025-era clients by default, on the same endpoint. Here is the real response of the Nordlys server to an old-style `initialize` request with protocol version 2025-11-25 (as one Server-Sent Event, the way that revision answered):

```json
{
  "result": {
    "protocolVersion": "2025-11-25",
    "capabilities": {
      "tools": {
        "listChanged": true
      },
      "resources": {
        "listChanged": true
      },
      "prompts": {
        "listChanged": true
      }
    },
    "serverInfo": {
      "name": "nordlys-cabins",
      "title": "Nordlys Cabins",
      "version": "1.0.0"
    },
    "instructions": "Nordlys Cabins rents holiday cabins in Norway. Use search_cabins to find cabins, check_availability to get the exact price, and create_booking only after the user confirmed the cabin, dates, guests and total. Prices are NOK. Dates are YYYY-MM-DD in Europe/Oslo. Free cancellation ends 14 days before check-in."
  },
  "jsonrpc": "2.0",
  "id": 1
}
```

The same instructions, the same capabilities, an older envelope. One of the Chapter 8 tests connects with a 2025 client and calls the tools, so we notice if a future SDK version drops this compatibility.

## What the graders see

Here is the honest part: the MCP server moves no check on either of our two graders by itself. isitagentready.com does not connect to your MCP endpoint and test the tools, and the Lighthouse "Agentic browsing" category looks only at pages. What isitagentready does check is whether your server is *discoverable*, through the `mcpServerCard` check, which looks for an MCP Server Card at a well-known location. That card is a discovery document, and discovery is the topic of Chapter 11, where we publish it for this server.

I find this split quite healthy, by the way. A grader can verify that a file exists and has the right shape. It cannot verify that your tools are well designed, that your descriptions tell the truth or that a booking made by an agent is safe. Those are the things this chapter and Chapter 10 are about, and only your own tests (and, eventually, your users) can verify them.

## Summary

- MCP is how general assistants connect to outside tools in 2026. A website offers a remote MCP server over Streamable HTTP, and the host (Claude, ChatGPT and Codex, Copilot Studio, VS Code, Gemini Enterprise) runs the client. In every host, somebody still adds the server by URL or as an admin.
- The 2026-07-28 revision is stateless: no `initialize` handshake and no `Mcp-Session-Id`, `_meta` with version and capabilities on every request, a mandatory `server/discover`, and `Mcp-Method` and `Mcp-Name` headers for routing. Any instance can answer any request.
- The TypeScript SDK v2 (`@modelcontextprotocol/server` 2.4.0) builds a fresh server per request with `createMcpHandler`. The handler checks no Origin, Host or token. Those checks are yours.
- The Nordlys tools call the same booking service as the API: the same validation, the same error codes, the same idempotency keys. Tools return both text and `structuredContent` validated against an `outputSchema`, and failures come back as tool results with `isError` that the model can act on.
- Annotations (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`) help hosts decide when to ask the user, but they are hints, not security. Real confirmations need the host's UI or `input_required` results.
- Resources offer clean Markdown content (the guide, the policy), and a prompt shows people what the server is good for.
- A small registry lets later chapters add tools without editing this layer, and passes the verified caller from Chapter 14 to every tool as `extra.auth`.
- Test with the SDK's real client in-process, and explore with MCP Inspector 2.13.0 (web UI, CLI and terminal UI). The server answers 2025-era clients too, so old tutorials still work against it.

[^ch08-1]: "MCP joins the Agentic AI Foundation," Model Context Protocol blog, 9 December 2025, https://blog.modelcontextprotocol.io/posts/2025-12-09-mcp-joins-agentic-ai-foundation/ (retrieved November 2026).
[^ch08-2]: "The 2026-07-28 Specification," Model Context Protocol blog, https://blog.modelcontextprotocol.io/posts/2026-07-28/ (retrieved November 2026). Download numbers are reported by the maintainers.
[^ch08-3]: "Get started with custom connectors using remote MCP," Claude Help Center, https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp (retrieved November 2026).
[^ch08-4]: "Plugin development for ChatGPT and Codex," OpenAI Developers, https://developers.openai.com/apps-sdk, and "Build an MCP server," https://developers.openai.com/apps-sdk/build/mcp-server (both retrieved November 2026).
[^ch08-5]: "Extend your agent with Model Context Protocol," Microsoft Copilot Studio documentation, https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-extend-action-mcp (retrieved November 2026).
[^ch08-6]: "Add MCP servers in VS Code," Visual Studio Code documentation, https://code.visualstudio.com/docs/copilot/customization/mcp-servers (retrieved November 2026).
[^ch08-7]: "Set up your custom MCP server connection," Gemini Enterprise Business Edition Help, https://support.google.com/g/answer/17106276 (updated 15 September 2026, retrieved November 2026).
[^ch08-8]: "Key changes," Model Context Protocol specification 2026-07-28, https://modelcontextprotocol.io/specification/2026-07-28/changelog (retrieved November 2026).
[^ch08-9]: "The 2026-07-28 Specification," Model Context Protocol blog, https://blog.modelcontextprotocol.io/posts/2026-07-28/ (retrieved November 2026).
[^ch08-10]: "Roadmap," Model Context Protocol, https://modelcontextprotocol.io/development/roadmap (retrieved November 2026).
[^ch08-11]: "Beta SDKs for the 2026-07-28 MCP Spec Release Candidate Are Here," Model Context Protocol blog, https://blog.modelcontextprotocol.io/posts/sdk-betas-2026-07-28/, and the npm registry entries https://registry.npmjs.org/@modelcontextprotocol%2fserver and https://registry.npmjs.org/zod (all retrieved November 2026).
[^ch08-12]: "Serve over HTTP," MCP TypeScript SDK v2 documentation, https://ts.sdk.modelcontextprotocol.io/v2/serving/http (retrieved November 2026).
[^ch08-13]: "Tools," Model Context Protocol specification 2026-07-28, https://modelcontextprotocol.io/specification/2026-07-28/server/tools (retrieved November 2026).
[^ch08-14]: "Tool Annotations as Risk Vocabulary: What Hints Can and Can't Do," Model Context Protocol blog, 16 March 2026, https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/ (retrieved November 2026).
[^ch08-15]: "Tools," section "Security considerations," Model Context Protocol specification 2026-07-28, https://modelcontextprotocol.io/specification/2026-07-28/server/tools (retrieved November 2026).
[^ch08-16]: "MCP Apps: Bringing UI Capabilities To MCP Clients," Model Context Protocol blog, 26 January 2026, https://blog.modelcontextprotocol.io/posts/2026-01-26-mcp-apps/ (retrieved November 2026).
[^ch08-17]: Demos repository, `nordlys-cabins/layers/08-mcp-server/` and `nordlys-cabins/tests/ch08-mcp-server.test.js`, https://github.com/webmaxru/agent-ready-web-demos (retrieved November 2026).
[^ch08-18]: "@modelcontextprotocol/inspector," npm registry, https://registry.npmjs.org/@modelcontextprotocol%2finspector (version 2.13.0, retrieved November 2026).
[^ch08-19]: "MCP Server," Cloudflare Agents documentation, https://developers.cloudflare.com/agents/model-context-protocol/apis/handler-api/ (retrieved November 2026).
[^ch08-20]: "Deploy MCP servers to Vercel," Vercel documentation, https://vercel.com/docs/mcp/deploy-mcp-servers-to-vercel (retrieved November 2026).
[^ch08-21]: "Self-hosted remote MCP server on Azure Functions (public preview)," Microsoft Learn, https://learn.microsoft.com/en-us/azure/azure-functions/self-hosted-mcp-servers, and "Deploy MCP servers in AgentCore Runtime," AWS documentation, https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-mcp.html (both retrieved November 2026).
