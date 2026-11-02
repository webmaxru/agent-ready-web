# Chapter 14: Agents acting for users: OAuth and delegated access

This chapter covers

- The difference between an agent that reads your site and an agent that acts for one of your users
- Delegated access in four words: who, to whom, what, and until when
- How an MCP client finds your authorization server: Protected Resource Metadata (RFC 9728) and authorization server metadata (RFC 8414)
- Client ID Metadata Documents, pre-registration and the end of Dynamic Client Registration in MCP
- Scopes, audience-bound tokens and step-up authorization
- Building it for Nordlys Cabins: a small authorization server, a consent page, member-only MCP tools and a “Connected agents” page

In Chapter 8 we gave Nordlys Cabins an MCP server. Any agent can search the cabins, check availability, book a stay and cancel a booking if it knows the reference and the email address. All of that works without knowing who the user is, and that was on purpose: a public catalogue and a public booking form need no login.

Now Ingrid Berg, one of our members, asks her assistant a different kind of question: “Which cabins have I booked for next year, and can you cancel the one in February?” To answer, the agent has to be Ingrid on nordlys.example, or at least act with her permission. The question this chapter answers is how a site lets that happen without handing the agent Ingrid’s password, without letting it do more than she wants, and with a way for Ingrid to switch it off.

The answer is OAuth, the same protocol that lets you “Sign in with Google” or connect a calendar app to your email. Nothing here is invented for agents. What is new is that in 2026 the AI platforms agreed on exactly how they use OAuth when they talk to an MCP server, and that agreement now lives in the MCP specification itself.[^ch14-1] If you implement it, ChatGPT, Claude, VS Code and any other compliant client can connect your users’ accounts in a few clicks. If you don’t, they can’t, and your users will find other ways, most of them worse.

## Why “just log in as me” is the wrong answer

Let’s start with the shortcuts, because your users will take them if you give them nothing better.

The first shortcut is the password. A person gives an agent their username and password, or types them into a browsing agent’s window. The agent then has everything the person has: it can change the email address, read the payment history, book and cancel. It keeps that power until the password changes. And you, the site owner, can’t tell the agent apart from the person.

The second shortcut is the browser session. A browsing agent (Chapter 3) that runs in the person’s own browser is already signed in, because the cookies are there. That is convenient and often fine for a one-off task the person watches. But again the site sees no difference between the person and the agent, there is no limit on what the agent may do, and there is nothing to revoke except the whole session.

The third shortcut is an API key that a member copies from a settings page into an agent’s configuration. Better, but the key usually has no expiry, no limits, no record of which agent holds it, and it ends up in configuration files and chat logs.

Delegated access fixes all three problems at once. When I explain it to a product manager I use four words:

- **Who.** Ingrid, signed in on your own site, with your own login (and her password never leaves your site).
- **To whom.** One specific agent application that the site can name: “Claude”, “ChatGPT”, “Nordlys demo agent”. Not “someone with Ingrid’s password”.
- **What.** A limited set of permissions, called **scopes**, written in words a person understands: “See your Nordlys bookings”, “Cancel your Nordlys bookings”.
- **Until when.** Tokens that expire within minutes, renew only while the permission stands, and stop working the moment Ingrid presses “Disconnect”.

And a fifth one for the site owner: **you stay in charge.** The agent never sees a password, every request carries a token you issued, and you can see which agent did what.

That is what OAuth gives you. In simple words, OAuth is a way for a person to give an application a key to some of their rooms, for a limited time, without giving away the house keys. The rest of this chapter is about the details that make the key safe and the agents able to find the door.

## The cast: four roles

OAuth has four roles, and MCP maps them onto your site like this.[^ch14-1]

- The **resource owner** is the person, Ingrid.
- The **client** is the agent application acting for her: ChatGPT, Claude, Codex, VS Code, or the small command-line agent we build later in this chapter. In MCP terms this is the MCP client.
- The **resource server** is what the agent wants to use: our MCP server at `/mcp`. The specification says it plainly: “A protected MCP server acts as an OAuth 2.1 resource server”.[^ch14-1]
- The **authorization server** is the part that signs Ingrid in, asks for her consent and issues tokens. It “may be hosted with the resource server or a separate entity”.[^ch14-1] For a real business this is usually the identity provider you already use for member login. For Nordlys we build a small one, so you can see every step.

![Figure 14.1 — The four OAuth roles on nordlys.example. Ingrid (the resource owner) uses an agent (the client). The agent calls the MCP server at /mcp (the resource server) with an access token. The authorization server at /oauth signs Ingrid in, shows the consent page and issues tokens. Ingrid’s password only ever goes to nordlys.example.](images/figure-14-1.png)

Which version of OAuth? MCP builds on **OAuth 2.1**, a consolidation of OAuth 2.0 and its security best practices. OAuth 2.1 is still an Internet-Draft. In November 2026 the current revision is `draft-ietf-oauth-v2-1-17`, while the MCP specification cites revision 13.[^ch14-3] Don’t let the draft status scare you: what OAuth 2.1 “changes” is mostly that it removes the risky parts of OAuth 2.0 (the implicit flow, the password grant) and makes PKCE mandatory. Every serious identity provider has supported that subset for years.

> **Note:** MCP authorization applies to MCP over HTTP only, and it is optional. The specification says that “Authorization is OPTIONAL for MCP implementations”, and that servers using the local STDIO transport “SHOULD NOT follow this specification” and get credentials from the environment instead.[^ch14-1] A remote server that touches user data needs it.

## How an agent finds your login: the discovery chain

The clever part of MCP authorization is that an agent needs to know nothing about your site in advance except the address of your MCP server. Everything else it discovers. Figure 14.2 shows the whole chain, and we’ll walk through it step by step.

![Figure 14.2 — Discovery and authorization in MCP. (1) The agent calls a member tool without a token and gets 401 with a WWW-Authenticate challenge. (2) It reads the Protected Resource Metadata named in the challenge, which lists the authorization server. (3) It reads the authorization server metadata. (4) It sends Ingrid to the authorization endpoint with PKCE and the resource parameter, Ingrid signs in and allows access. (5) The agent exchanges the code for a token. (6) It repeats the tool call with the token.](images/figure-14-2.png)

### Step 1: the 401 challenge

The agent calls a tool that needs a member, without a token. The server answers with HTTP 401 and a `WWW-Authenticate` header. The MCP specification gives this example:[^ch14-1]

```text
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer resource_metadata="https://mcp.example.com/.well-known/oauth-protected-resource",
                         scope="files:read"
```

Two things are in the challenge. `resource_metadata` says where the agent can read about this protected resource. `scope` says which permission this particular request needs. MCP servers “SHOULD include a scope parameter”, and clients “MUST treat the scopes provided in the challenge as authoritative for the current operation”.[^ch14-1]

### Step 2: Protected Resource Metadata (RFC 9728)

The document behind `resource_metadata` is **OAuth 2.0 Protected Resource Metadata**, RFC 9728, published in April 2025.[^ch14-5] It is a small JSON document where a resource server says who it is (`resource`), which authorization servers issue tokens for it (`authorization_servers`), and which scopes it understands (`scopes_supported`). The MCP specification makes it mandatory on both sides: “MCP servers MUST implement OAuth 2.0 Protected Resource Metadata (RFC9728)”, and clients must use it to find the authorization server.[^ch14-1]

The document lives under `/.well-known/oauth-protected-resource`, and here is a detail that trips people up. RFC 9728 inserts the well-known segment *before* the path of the resource. For a resource at `https://nordlys.example/mcp` the address is `https://nordlys.example/.well-known/oauth-protected-resource/mcp`.[^ch14-5] MCP clients follow the `resource_metadata` pointer from the 401 when there is one. Otherwise they try that path-inserted address first and then fall back to `/.well-known/oauth-protected-resource` at the root.[^ch14-6]

The RFC also asks the client to check the document: when it came through the `WWW-Authenticate` pointer, “the resource value returned MUST be identical to the URL that the client used to make the request to the resource server”.[^ch14-5] That check is what stops another site from claiming to be your MCP server.

### Step 3: authorization server metadata (RFC 8414)

Now the agent knows the issuer of the authorization server, for Nordlys simply `https://nordlys.example`. It reads the server’s own metadata, defined in RFC 8414 (2018) for OAuth and in OpenID Connect Discovery for OpenID providers. MCP clients “MUST support both discovery mechanisms”, and for an issuer without a path they try `/.well-known/oauth-authorization-server` first and `/.well-known/openid-configuration` second.[^ch14-6] After fetching, “the issuer value in the document MUST be identical to the issuer identifier used to construct the well-known URL”. If not, the client must not use it.[^ch14-6]

From this document the agent learns where to send the person (`authorization_endpoint`), where to exchange codes for tokens (`token_endpoint`), and which features the server supports. One field decides whether the journey continues at all: `code_challenge_methods_supported`. The MCP specification says that if it is absent, “the authorization server does not support PKCE and MCP clients MUST refuse to proceed”.[^ch14-7] OpenAI’s documentation for ChatGPT and Codex says the same in practical terms: MCP servers “are unsupported when their authorization server metadata omits this field or does not advertise `S256`“.[^ch14-8]

### Step 4: the person allows access

The agent now sends Ingrid’s browser to the authorization endpoint with a request like this (line breaks added):

```text
GET /oauth/authorize?response_type=code
    &client_id=...
    &redirect_uri=...
    &scope=bookings:read
    &state=...
    &code_challenge=...&code_challenge_method=S256
    &resource=https://nordlys.example/mcp
```

Ingrid signs in on nordlys.example (if she isn’t already), sees a consent page, and presses Allow or Deny. The authorization server then redirects the browser back to the agent’s `redirect_uri` with a short-lived, single-use authorization **code**.

Three parameters in that request carry most of the security:

- **PKCE** (`code_challenge` and later `code_verifier`). The agent makes up a random secret, sends only its SHA-256 hash at the start, and reveals the secret when it exchanges the code. Someone who steals the code from the redirect can’t use it without the secret. MCP clients “MUST use the S256 code challenge method”.[^ch14-7]
- **`resource`** (RFC 8707, Resource Indicators). The agent says which resource the token is for. MCP clients “MUST include the resource parameter in authorization and token requests”.[^ch14-7] We’ll see in a moment why this matters so much.
- **`state`**, and since the 2026-07-28 revision the **`iss`** parameter in the response (RFC 9207). The agent checks that the answer belongs to the request it sent, and that it came from the authorization server it expected. The MCP specification asks authorization servers to include `iss` and to advertise it with `authorization_response_iss_parameter_supported`.[^ch14-1] OpenAI’s hosts rely on it to protect their callbacks against “authorization server mix-up attacks”.[^ch14-8]

### Step 5 and 6: the token, and the call again

The agent sends the code, the PKCE secret and the same `resource` to the token endpoint and gets an **access token** (and usually a **refresh token** to get new access tokens later). Then it repeats the original tool call with `Authorization: Bearer <access token>`. The server checks the token and runs the tool.

That’s the whole chain. It looks like a lot of steps on paper, but all of it happens in a second or two, and from Ingrid’s point of view it is one page: “Claude wants to use your Nordlys account. Allow?”

## Who is the agent? Client registration in 2026

There is one question the discovery chain skipped: what is the `client_id`? OAuth needs to know which application is asking, both to show its name on the consent page and to check where it may send the code. Traditionally a developer registered every application with every authorization server by hand. That obviously doesn’t work when any of thousands of agents may want to connect to any of thousands of MCP servers.

The MCP specification of 28 July 2026 lists three ways, in this order of preference:[^ch14-9]

1. **Pre-registration**, “when client and server have an existing relationship”. The site gives the agent a client ID up front. Fine for your own apps and for partners you sign contracts with.
2. **Client ID Metadata Documents (CIMD)**, “when client and server have no prior relationship (most common)”. The client ID is an HTTPS URL, and at that URL the client publishes a JSON document with its name, logo and redirect URIs. The authorization server fetches it when it sees the client ID for the first time. There is nothing to register.
3. **Dynamic Client Registration (DCR)**, RFC 7591, where the client registers itself through an API on the authorization server. In the 2026-07-28 revision, “Dynamic Client Registration is deprecated”, kept “for backwards compatibility with authorization servers that do not support Client ID Metadata Documents”.[^ch14-9]

Here is the example metadata document from the specification, so you can see how little it takes:[^ch14-9]

```json
{
  "client_id": "https://app.example.com/oauth/client-metadata.json",
  "client_name": "Example MCP Client",
  "client_uri": "https://app.example.com",
  "logo_uri": "https://app.example.com/logo.png",
  "redirect_uris": ["http://127.0.0.1:3000/callback", "http://localhost:3000/callback"],
  "grant_types": ["authorization_code"],
  "response_types": ["code"],
  "token_endpoint_auth_method": "none"
}
```

An authorization server that accepts such clients says so with `"client_id_metadata_document_supported": true` in its metadata.[^ch14-9] The idea is an IETF working group draft, “OAuth Client ID Metadata Document”. The MCP specification cites revision 00 and the current one is `draft-ietf-oauth-client-id-metadata-document-02` (July 2026).[^ch14-10]

Why did MCP move away from DCR? With DCR, every agent creates a new client record on every server, nobody can tell those records apart, and the server ends up with thousands of anonymous registrations. With CIMD the client ID *is* a web address the agent’s vendor controls. The consent page can say “chatgpt.com” or “claude.ai” with some confidence, and the same ID works on every server, because “Client IDs based on Client ID Metadata Documents are portable across authorization servers”.[^ch14-9]

What do the big agent platforms support today? OpenAI’s documentation says its hosts use “Client ID Metadata Documents (CIMD), dynamic client registration (DCR), predefined OAuth clients, and PKCE”.[^ch14-8] Claude’s connector setup offers the same three choices under the names “Use Claude’s published identity (Recommended)”, “Register automatically” and “Use your own OAuth client”.[^ch14-11] So in November 2026 both still accept DCR, while the specification and the recommended options point to CIMD.

> **Warning:** CIMD means your authorization server fetches a URL that a stranger chose. That is a classic server-side request forgery (SSRF) risk: someone could use your server to probe your internal network. The MCP specification asks authorization servers to “consider Server-Side Request Forgery (SSRF) risks”, and warns that metadata documents “cannot prevent localhost URL impersonation by themselves”, so servers “MUST clearly display the redirect URI hostname during authorization”.[^ch14-12] Our demo refuses IP addresses and `localhost` names, limits the size and time of the fetch, and shows the redirect host on the consent page. A production server should also check the IP address that the hostname resolves to.

## Tokens that only work in one place

Now back to the `resource` parameter, because it protects against a mistake that is easy to make when you connect several services.

Imagine a token that Ingrid’s agent got for the Nordlys MCP server. If that token were also accepted by, say, the Nordlys payments API (or by any other service that trusts the same identity provider), then a malicious or buggy MCP server could take the token it received and use it somewhere else. That is called a **confused deputy** or **token passthrough** problem, and the MCP specification is strict about it. Servers “MUST validate that access tokens were issued specifically for them as the intended audience”, “MUST only accept tokens that are valid for use with their own resources”, and when an MCP server calls another API, “The MCP server MUST NOT pass through the token it received from the MCP client”.[^ch14-7][^ch14-1]

In practice it means three checks on every request: the token was signed by your authorization server, it is not expired, and its audience (the `aud` claim in a JWT, or the equivalent field your identity provider returns from token introspection) is exactly your MCP server’s URL. If any check fails, the answer is 401: “Invalid or expired tokens MUST receive a HTTP 401 response.”[^ch14-1]

## Scopes and step-up: asking for more only when needed

Scopes are where product thinking meets protocol. A scope is a named permission, and the consent page turns it into a sentence. Good scopes follow what users understand, not what your database tables look like. For Nordlys I chose two:

| Scope | Consent page says | Used by |
|---|---|---|
| `bookings:read` | See your Nordlys bookings | `list_my_bookings` |
| `bookings:write` | Cancel your Nordlys bookings | `cancel_my_booking` |

What about searching cabins and creating a booking? Those stay public, exactly as in Chapter 8. Anyone can book a cabin on the website without an account, so an agent can too. And payment is not a scope at all: as Chapter 12 explained, the guest pays on the site.

Should an agent ask for everything at once? The specification says no. Clients “SHOULD follow the principle of least privilege by requesting only the scopes necessary for their intended operations”, and the `scopes_supported` list “is intended to represent the minimal set of scopes necessary for basic functionality”, with more scopes “requested incrementally through the step-up authorization flow”.[^ch14-1]

**Step-up** works like this. The agent has a token with `bookings:read`. Ingrid asks it to cancel a booking. The agent calls `cancel_my_booking`, and the server answers:

```text
HTTP/1.1 403 Forbidden
WWW-Authenticate: Bearer error="insufficient_scope", scope="bookings:write",
                  resource_metadata="https://nordlys.example/.well-known/oauth-protected-resource/mcp",
                  error_description="This tool needs: Cancel your Nordlys bookings."
```

That’s the response format from the specification: status 403, `error="insufficient_scope"`, the scopes the operation needs, and the metadata address “for consistency with 401 responses”.[^ch14-1] The agent then sends Ingrid through the consent page again, asking for the union of what it already had and what it now needs, gets a new token and retries. Clients acting for a user “SHOULD attempt the step-up authorization flow”, and they should not retry forever.[^ch14-1]

This is a good design for risky actions in general, not only for cancelling. Reading a booking is harmless. Cancelling one costs money. The person sees a second, specific consent at the exact moment the risk appears, which is the kind of confirmation Chapter 17 is about.

One more design question: should the whole MCP server require a login, or only some tools? Both are valid. The specification lets a server decide the required scopes “dynamically based on the specific request arguments and context”.[^ch14-1] Claude’s connector settings even let the person choose between “Sign in now”, “Sign in when needed” and “No sign in”.[^ch14-11] Nordlys keeps its public tools public and challenges only on member tools, which is the “sign in when needed” shape.

## Hands-on: delegated access for Nordlys members

> **Hands-on:** This section builds layer `14-oauth` of the demo app and a small command-line agent in `demos/chapters/14-connect-an-agent`. If you don’t read JavaScript, here is the short version: the site publishes two small JSON files that tell agents where its login is, shows members a consent page, gives agents short-lived tokens, and lets members see and disconnect agents. Pick up again at “Build it or use your identity provider?”.

The layer needs the MCP server from Chapter 8 and adds no dependencies: tokens are signed with Ed25519 from `node:crypto`. Start the app with `npm start -- --upto=14`. These are the new addresses:

- `/.well-known/oauth-protected-resource/mcp` (and the same document at the root)
- `/.well-known/oauth-authorization-server`
- `/oauth/authorize`, `/oauth/token`, `/oauth/revoke` and `/oauth/jwks.json`
- `/account/agents`, the member’s “Connected agents” page
- two new MCP tools, `list_my_bookings` and `cancel_my_booking`

Please note that this is a teaching authorization server. It keeps everything in memory, so a restart signs every agent out, and it supports exactly what MCP clients need: the authorization code flow with PKCE, refresh tokens, public clients, pre-registered clients and Client ID Metadata Documents. The section after this one explains why, for a real business, I would use the identity provider you already have.

### Publishing the metadata

Listing 14.1 publishes the Protected Resource Metadata. The resource is the MCP endpoint, and the authorization server is the site itself.

**Listing 14.1** `nordlys-cabins/layers/14-oauth/resource-server.js` (excerpt) — Protected Resource Metadata
```js
export function resourceServer(ctx, { grants, signer, issuerOf, resourceOf }) {
  const metadataUrl = (c) => `${issuerOf(c)}/.well-known/oauth-protected-resource/mcp`;
  const metadata = (c) => JSON.stringify({
    resource: resourceOf(c),
    authorization_servers: [issuerOf(c)],
    scopes_supported: Object.keys(SCOPES),
    bearer_methods_supported: ['header'],
    resource_name: 'Nordlys Cabins MCP server',
  }, null, 2);
  const json = { contentType: 'application/json; charset=utf-8' };
  // RFC 9728 inserts the well-known segment before the resource path (/mcp).
  // MCP clients fall back to the root, and that is where scanners look.
  ctx.staticFile('/.well-known/oauth-protected-resource/mcp', metadata, json);
  ctx.staticFile('/.well-known/oauth-protected-resource', metadata, json);

```

The same document is also served at the root, `/.well-known/oauth-protected-resource`. MCP clients fall back to that address when there is no pointer, and it is where scanners look for it, as we’ll see at the end of the chapter. Strictly by RFC 9728, a client that builds the root address itself from `https://nordlys.example` expects a document about `https://nordlys.example`, not about `/mcp`, so the root copy helps lenient clients and scanners. The pointer in the 401 challenge is the path every client should rely on, and it points to the path-inserted document.

Here is what an agent sees when it calls a member tool without a token, run against the demo app with `PUBLIC_ORIGIN=https://nordlys.example` (the body of the request is a normal `tools/call` for `list_my_bookings`):

```text
$ curl -s -X POST http://127.0.0.1:4514/mcp \
    -H 'content-type: application/json' -H 'accept: application/json, text/event-stream' \
    -H 'mcp-protocol-version: 2026-07-28' -H 'mcp-method: tools/call' -H 'mcp-name: list_my_bookings' \
    -d @list-my-bookings.json -D - -o /dev/null | grep -i -E '^HTTP|^www-authenticate'
HTTP/1.1 401 Unauthorized
www-authenticate: Bearer scope="bookings:read", resource_metadata="https://nordlys.example/.well-known/oauth-protected-resource/mcp"
```

And this is the metadata the challenge points to:

```text
$ curl -s http://127.0.0.1:4514/.well-known/oauth-protected-resource/mcp
{
  "resource": "https://nordlys.example/mcp",
  "authorization_servers": [
    "https://nordlys.example"
  ],
  "scopes_supported": [
    "bookings:read",
    "bookings:write"
  ],
  "bearer_methods_supported": [
    "header"
  ],
  "resource_name": "Nordlys Cabins MCP server"
}
```

The authorization server metadata follows the same pattern. I show only the fields that matter for this chapter:

```json
{
  "issuer": "https://nordlys.example",
  "authorization_endpoint": "https://nordlys.example/oauth/authorize",
  "token_endpoint": "https://nordlys.example/oauth/token",
  "grant_types_supported": ["authorization_code", "refresh_token"],
  "code_challenge_methods_supported": ["S256"],
  "token_endpoint_auth_methods_supported": ["none"],
  "client_id_metadata_document_supported": true,
  "authorization_response_iss_parameter_supported": true
}
```

What is missing is as important as what is there: no `registration_endpoint`, because Nordlys doesn’t offer Dynamic Client Registration, and no `password` or `implicit` grant, because OAuth 2.1 removed them. `token_endpoint_auth_methods_supported: ["none"]` says that clients are public: an agent running on someone’s laptop can’t keep a secret, so PKCE does the job a client secret would do.

### Checking every call to /mcp

Listing 14.2 is the heart of the resource server: a middleware that runs before the MCP handler from Chapter 8. It verifies a token if there is one, and it challenges when a member tool is called without the right scope.

**Listing 14.2** `nordlys-cabins/layers/14-oauth/resource-server.js` (excerpt) — verifying tokens and challenging
```js
  function verifyBearer(c, header) {
    const m = /^Bearer\s+(\S+)$/i.exec(header ?? '');
    const claims = m && signer.verify(m[1]);
    if (!claims) return null;
    if (claims.iss !== issuerOf(c) || claims.aud !== resourceOf(c) || claims.exp <= Date.now() / 1000) return null;
    const grant = grants.active(claims.gid);
    if (!grant || grant.memberId !== claims.sub) return null;
    grants.touch(grant.id);
    return {
      token: m[1], clientId: claims.client_id, scopes: claims.scope.split(' '), expiresAt: claims.exp,
      resource: new URL(claims.aud), member: ctx.store.getMember(claims.sub), extra: { grantId: grant.id },
    };
  }

  ctx.middleware(async (c, next) => {
    if (c.req.path !== '/mcp' || c.req.method !== 'POST') return next();
    const header = c.req.header('authorization');
    if (header) {
      const auth = verifyBearer(c, header);
      if (!auth) return challenge(c, 401, { error: 'invalid_token', error_description: 'The access token is invalid, expired or withdrawn.' });
      c.set('mcpAuth', auth);
    }
    // Gateways can route on the Mcp-Name header. We read the body, because the body
    // is what the MCP handler executes.
    const body = await c.req.raw.clone().json().catch(() => null);
    const needs = body?.method === 'tools/call' ? MEMBER_TOOLS[body.params?.name] : undefined;
    if (needs) {
      const auth = c.get('mcpAuth');
      if (!auth) return challenge(c, 401, { scope: needs.join(' ') });
      if (!needs.every((s) => auth.scopes.includes(s)))
        return challenge(c, 403, { error: 'insufficient_scope', scope: needs.join(' '),
          error_description: `This tool needs: ${needs.map((s) => SCOPES[s]).join(', ')}.` });
    }
    return next();
  });
```

Let’s have a look at the details.

- `verifyBearer()` makes the three checks from earlier in the chapter (signature, expiry, audience) and one more that many implementations forget: it looks up the **grant** behind the token. If Ingrid disconnected the agent a second ago, the token stops working now, not when it expires. The verified result goes into `c.set('mcpAuth', ...)`, which is the hook the Chapter 8 layer left for exactly this purpose, and from there it reaches every tool handler as `extra.auth`.
- The middleware reads the tool name from the JSON-RPC **body**, not from the `Mcp-Name` header. Since the 2026-07-28 revision, clients must send `Mcp-Method` and `Mcp-Name` headers “so that intermediaries (load balancers, gateways, observability tooling) can route and inspect requests without parsing the body”, and a server that processes the body must reject requests where headers and body disagree.[^ch14-13] A gateway in front of Nordlys could make the same decision from the header. Inside the server, the body is what will actually run, so the body decides. One of the tests sends a request whose header says `search_cabins` while the body calls `list_my_bookings`, and it gets a 401.
- Public tools never reach the challenge. An agent that doesn’t care about Ingrid’s account can keep using `search_cabins` without a token, exactly as before.

The tools themselves check again. Listing 14.3 shows `cancel_my_booking`: it needs the right scope *and* a booking that belongs to the member behind the token. Defence in depth costs two lines, and it means that a mistake in the middleware can’t turn into cancelling someone else’s stay.

**Listing 14.3** `nordlys-cabins/layers/14-oauth/tools.js` (excerpt) — a member tool that checks again
```js
  registerMcpTool(ctx, 'cancel_my_booking', {
    title: 'Cancel one of my bookings',
    description: 'Cancel a booking of the signed-in member. This cannot be undone: ask the user to confirm the booking reference first. ' +
      'Needs scope bookings:write.',
    inputSchema: z.object({ ref: z.string().regex(/^NC-[0-9A-Z]{6}$/).describe('Booking reference, for example NC-7KQ2MD') }),
    outputSchema: MyBooking.extend({ refund: z.number().int() }),
    annotations: { readOnlyHint: false, destructiveHint: true, idempotentHint: true, openWorldHint: false },
  }, async ({ ref }, { auth }) => {
    if (!allowed(auth, 'cancel_my_booking')) return denied('This needs permission to cancel bookings (scope bookings:write).');
    const booking = ctx.store.getBooking(ref);
    if (!booking || booking.memberId !== auth.member.id) return denied(`${ref} is not one of your bookings.`);
    const r = ctx.store.cancelBooking(ref);
    if (!r.ok) return denied(r.errors.map((e) => e.message).join(' '));
    ctx.events.emit('booking.cancelled', r.booking, { via: 'mcp', agent: auth.clientId });
    const out = { ...view(r.booking), refund: r.booking.refund };
    return { ...text(`Cancelled ${out.ref}. Refund: ${out.refund} NOK.`), structuredContent: out };
  }, OWNER);
```

The tool is annotated as destructive, and its description tells the model to “ask the user to confirm the booking reference first”. Chapter 8 explained why annotations are hints, not guarantees. Here the real protection is the scope: the agent can’t cancel anything until Ingrid has seen a consent page that says “Cancel your Nordlys bookings”.

### The authorization endpoint and the consent page

Before it shows anything to the person, the authorization endpoint validates the request (Listing 14.4). The order matters. The client and its redirect URI are checked first, and if they fail, the error is shown on Nordlys’s own page. Only after the redirect URI is known to belong to the client may errors be sent back to it. Otherwise an attacker could use your authorization server to redirect people anywhere, which the MCP specification calls open redirection and forbids: authorization servers “MUST validate exact redirect URIs against pre-registered values”.[^ch14-12]

**Listing 14.4** `nordlys-cabins/layers/14-oauth/authorization-server.js` (excerpt) — validating an authorization request
```js
  async function validate(c, q) {
    let client;
    try {
      client = await resolveClient(q.client_id);
    } catch (e) {
      return { stop: page(c, 'Unknown application', html`<h1>We could not identify this application</h1><p>${e.message}.</p>`, 400) };
    }
    if (!q.redirect_uri || !redirectAllowed(client, q.redirect_uri))
      return { stop: page(c, 'Unknown application', html`<h1>This redirect address is not registered for ${client.client_name}</h1>`, 400) };
    const fail = (error, description) => ({ stop: back(c, q.redirect_uri, { error, error_description: description, state: q.state }) });
    if (q.response_type !== 'code') return fail('unsupported_response_type', 'Only the authorization code flow is supported.');
    if (!q.code_challenge || q.code_challenge_method !== 'S256') return fail('invalid_request', 'PKCE with S256 is required.');
    if (q.resource !== resourceOf(c)) return fail('invalid_target', `Tokens are only issued for ${resourceOf(c)}.`);
    const scopes = String(q.scope ?? '').split(' ').filter(Boolean);
    if (!scopes.length || scopes.some((s) => !SCOPES[s])) return fail('invalid_scope', `Ask for one or more of: ${Object.keys(SCOPES).join(' ')}.`);
    return { client, scopes };
  }
```

Then, if the member is not signed in, the endpoint redirects to the normal Nordlys login page and comes back afterwards. Ingrid’s password goes into the same form it always does, on nordlys.example.

The consent page is where product and design work matters most. This is the text a member sees, read from the demo with the command-line agent from later in this section asking for access:

```text
Nordlys demo agent (command line) wants to use your Nordlys account
It will be able to:
  See your Nordlys bookings
It cannot see your password or pay for anything. You can disconnect it
at any time on Connected agents.
Application:       nordlys-demo-agent (registered with Nordlys)
Sends you back to: 127.0.0.1:44739
[Allow] [Deny]
```

I tried to follow four rules on this page, and I recommend them to any team:

1. **Name the application** the way the person knows it, and show its client ID. With CIMD the client ID is a web address, which is the most honest name you have.
2. **One sentence per scope**, in the person’s words. “See your Nordlys bookings” beats `bookings:read`.
3. **Say what the agent can’t do.** “It cannot see your password or pay for anything” answers the question people actually have.
4. **Show where the person goes next** (the redirect host), because the MCP specification requires it for metadata-document clients and because it is the one technical detail that helps a careful person spot a fake.

When the person presses Allow, the server records a **grant** (this member, this client, these scopes), issues a one-time code that is valid for 60 seconds and bound to everything in the request, and redirects back to the agent with `code`, `state` and `iss`.

### Exchanging the code for tokens

Listing 14.5 is the token endpoint’s code exchange. Every value that was in the authorization request must match: the client, the redirect URI, the PKCE secret and the resource.

**Listing 14.5** `nordlys-cabins/layers/14-oauth/authorization-server.js` (excerpt) — the code exchange
```js
  ctx.route('POST', '/oauth/token', async (c) => {
    const f = await c.req.parseBody();
    if (f.grant_type === 'authorization_code') {
      const code = grants.redeemCode(f.code);
      if (!code) return tokenError(c, 'invalid_grant', 'The code is unknown, used or expired.');
      if (code.clientId !== f.client_id || code.redirectUri !== f.redirect_uri)
        return tokenError(c, 'invalid_grant', 'client_id or redirect_uri does not match the authorization request.');
      const challenge = createHash('sha256').update(String(f.code_verifier ?? '')).digest('base64url');
      if (challenge !== code.codeChallenge) return tokenError(c, 'invalid_grant', 'PKCE verification failed.');
      if (f.resource && f.resource !== code.resource) return tokenError(c, 'invalid_target', 'resource does not match the authorization request.');
      const grant = grants.active(code.grantId);
      if (!grant) return tokenError(c, 'invalid_grant', 'Access was withdrawn.');
      return issueTokens(c, grant, code.scopes, code.resource);
    }
```

The access token is a JSON Web Token in the “JWT profile for OAuth 2.0 access tokens” (RFC 9068), signed with Ed25519, valid for 10 minutes, with the MCP endpoint as its audience. The refresh token is a random string that **rotates**: every use gives a new one, and using an old one a second time withdraws the whole grant. The MCP specification requires rotation for public clients (“authorization servers MUST rotate refresh tokens”) and asks for short-lived access tokens “to reduce the impact of leaked tokens”.[^ch14-7]

### “Connected agents”: the page your members need

The last part of the layer is a page that most OAuth tutorials skip, and I think it is the most important one for trust. At `/account/agents`, a signed-in member sees every agent that may act for them, what it may do, when it was connected and when it last did something, with a **Disconnect** button next to each. Disconnecting revokes the grant, deletes its refresh tokens, and (because the resource server checks the grant on every call) stops the current access token immediately. The same happens when an agent calls the RFC 7009 revocation endpoint itself.

If you remember one thing from this chapter for your product backlog, make it this page. People will connect agents to their accounts more easily when they can see them and switch them off.

### A command-line agent that does the whole dance

To see the flow from the agent’s side, `demos/chapters/14-connect-an-agent/agent.mjs` is a small agent with no dependencies. It is pre-registered at Nordlys as `nordlys-demo-agent`, with a loopback redirect: it starts a one-shot web server on a free port of `127.0.0.1`, which RFC 8252 allows for native apps (the port may change each time).[^ch14-14] Listing 14.6 is its discovery part, steps 1 to 3 of Figure 14.2.

**Listing 14.6** `chapters/14-connect-an-agent/agent.mjs` (excerpt) — discovery from the agent’s side
```text
  // 1. Ask without a token. The challenge says where to read about this resource.
  const first = await callTool(mcpUrl, 'list_my_bookings');
  if (first.status !== 401) throw new Error(`expected 401, got ${first.status}`);
  const { resource_metadata, scope } = params(first.challenge);

  // 2. Protected Resource Metadata (RFC 9728) names the authorization server.
  const prm = await (await fetch(resource_metadata)).json();
  if (prm.resource !== mcpUrl) throw new Error('the metadata describes another resource'); // RFC 9728, section 3.3
  const issuer = prm.authorization_servers[0];

  // 3. Authorization server metadata (RFC 8414). Refuse it if it does not do PKCE S256.
  const as = await (await fetch(new URL('/.well-known/oauth-authorization-server', issuer))).json();
  if (as.issuer !== issuer) throw new Error('issuer mismatch in authorization server metadata');
  if (!as.code_challenge_methods_supported?.includes('S256')) throw new Error('no PKCE S256, refusing to continue');
```

Run the app on port 3000 in one terminal and the agent in another. The agent prints an address, you open it in a browser, sign in as `ingrid@nordlys.example` with the password `nordlys-demo`, press Allow, and the agent continues. This is a real run (I shortened the long query string):

```text
$ node demos/chapters/14-connect-an-agent/agent.mjs http://127.0.0.1:3000
Open this address and sign in:
http://127.0.0.1:3000/oauth/authorize?response_type=code&client_id=nordlys-demo-agent&redirect_uri=http%3A%2F%2F127.0.0.1%3A44739%2Fcallback&scope=bookings%3Aread&...&code_challenge_method=S256

NC-7KQ2MD  lyngen-lysthus  2027-02-10 to 2027-02-14  confirmed
NC-H4WX9P  hardanger-hytte  2027-07-03 to 2027-07-10  confirmed
```

Notice that the agent asked only for `bookings:read`, because that is what the challenge said. It will be asked for more only if it tries to cancel.

### Testing the layer

Two test files cover the layer, with the MCP client from the TypeScript SDK (version 2.4.0, the same as in Chapter 8) and plain `fetch`:

```text
$ node --test tests/ch14-*.test.js 2>&1 | grep -E '^# (tests|pass|fail)'
# tests 11
# pass 11
# fail 0
```

`tests/ch14-oauth.test.js` checks the metadata documents, the 401 and 403 challenges and their exact headers, the full flow with consent, step-up from read to write, that Ingrid can’t cancel Ola’s booking, that an edited token fails, that a lying `Mcp-Name` header changes nothing, that the authorization server refuses requests without PKCE, for another resource or with an unregistered redirect, that codes work once and refresh tokens rotate, a client identified by a Client ID Metadata Document (with `fetch` mocked), and that disconnecting stops a live token. `tests/ch14-agent-cli.test.js` runs the command-line agent against a real server on a free port and plays the person in the browser.

## Build it or use your identity provider?

We built an authorization server so you can see every moving part. For a real business I would not ship one written for a book. Authorization servers fail in subtle ways, and the identity provider you already use for member login (or a managed one) has been hardened by people who do nothing else.

What should you check before you choose? This is the list I would give a security architect, taken from the requirements above and from what ChatGPT and Claude ask for:

- RFC 8414 metadata (or OpenID Connect Discovery) with `code_challenge_methods_supported` containing `S256`
- the `resource` parameter (RFC 8707), and access tokens whose audience is your MCP server
- `iss` in authorization responses (RFC 9207) and `authorization_response_iss_parameter_supported`
- Client ID Metadata Documents, or at least Dynamic Client Registration for the clients that still use it
- refresh token rotation for public clients, short-lived access tokens, and a revocation endpoint
- a consent screen you can word yourself, and a way to list and revoke grants per user

If your identity provider lacks CIMD and DCR, users can’t add your MCP server to Claude or ChatGPT on their own, and each one would need a pre-registered client. That is a buying criterion worth writing down. On Cloudflare Workers, the `@cloudflare/workers-oauth-provider` library (version 1.2.4 in November 2026) is another option for teams that want to host the authorization server next to the MCP server.[^ch14-15] And Cloudflare’s own Agents Week post said that “Cloudflare Access now fully supports this OAuth flow” for agents.[^ch14-16]

## Agents at work: Enterprise-Managed Authorization

Everything so far assumed a person who decides, one server at a time. Companies don’t work like that. An employee doesn’t want to press Allow for twenty internal tools, and the security team wants one place to say who may use what.

For that case MCP has an official extension, **Enterprise-Managed Authorization (EMA)**, which the MCP blog declared stable on 18 June 2026.[^ch14-17] The company’s identity provider becomes “the authoritative decision-maker for MCP server access”. In the blog’s words: “the client obtains an Identity Assertion JWT Authorization Grant (ID-JAG) from the IdP during single sign-on and exchanges it for an access token from the MCP server’s authorization server. The user is never redirected through a per-server consent screen.”[^ch14-17] ID-JAG is an IETF OAuth working group draft (`draft-ietf-oauth-identity-assertion-authz-grant-06`, October 2026).[^ch14-18] The launch adopters named in the post were Okta as the first identity provider (“Cross App Access”), Claude, Claude Code, Cowork and Visual Studio Code as clients, and Asana, Atlassian, Canva, Figma, Granola, Linear and Supabase as servers.[^ch14-17]

For a cabin-rental site with consumer members, EMA doesn’t matter. For a SaaS product sold to companies, it will soon be on the checklist of every enterprise buyer, and the authorization server you choose should be able to accept ID-JAG grants.

Behind EMA there is a busy family of standards about agents and identity. Token exchange (RFC 8693) lets one service trade a token for another with a narrower audience, which is the right tool when your MCP server has to call another API. DPoP (RFC 9449) binds tokens to a key so that a stolen token is useless, and the MCP roadmap lists finalizing a DPoP specification as a goal.[^ch14-19] And several individual Internet-Drafts propose “OAuth for AI agents” profiles, none of them adopted by a working group in November 2026. My advice is to know the names and wait.

> **Note:** **auth.md** is a different idea you’ll meet in the graders. WorkOS proposes a Markdown file at `/auth.md` that “tells agents how to register on behalf of a user”, composing existing standards such as Protected Resource Metadata and ID-JAG assertions. WorkOS says it authors the protocol but that it is “not tied to WorkOS infrastructure”.[^ch14-20] It goes one step further than this chapter: an agent signs a person *up*, not only in. Cloudflare Radar found it on 116 domains of the top 200,000 on 2 November 2026.[^ch14-21] Nordlys doesn’t publish one, because creating member accounts is not something we want agents to do for people yet.

### Don’t confuse the two kinds of identity

One last distinction before we measure, because readers (and vendors) mix it up all the time. OAuth, as in this chapter, answers: **did this person allow this application to act for them?** It says nothing reliable about which company runs the agent’s servers or whether the traffic really comes from it. That second question, **who operates this agent?**, is answered by Web Bot Auth and HTTP message signatures, and that is Chapter 15. A booking site wants both answers: the signature tells you the request really comes from, say, OpenAI’s agent, and the token tells you that Ingrid allowed that agent to see her bookings.

## What the graders see

isitagentready.com has two checks for this chapter’s work and a third related one:[^ch14-22]

- `oauthDiscovery`: “/.well-known/openid-configuration or /.well-known/oauth-authorization-server exists with valid OAuth metadata”
- `oauthProtectedResource`: “/.well-known/oauth-protected-resource exists with resource identifier and authorization_servers”
- `authMd`: “/auth.md exists, PRM is discoverable, and OAuth Authorization Server metadata contains agent_auth registration methods”

These checks matter for the level. Level 5, “Agent-Native”, needs Level 4 plus “2 of 3: Web Bot Auth, all four integration checks, auth metadata (OAuth discovery, OAuth Protected Resource, or Auth.md)”.[^ch14-22] So the auth metadata from this chapter is one of the three ingredients of the top level, provided that the lower levels are in place (Chapter 11 has the ladder). Please note that the scanner checks the root path `/.well-known/oauth-protected-resource`, which is one reason Nordlys serves the document there too.

Adoption is higher than for most agent standards, because every OpenID provider already publishes discovery metadata. Radar counted OAuth discovery documents on 9,323 domains (8.1%) and Protected Resource Metadata on 4,775 domains (4.1%) of the 115,468 it scanned.[^ch14-21]

The Lighthouse Agentic Browsing category has no audit for any of this. It looks at pages, and the only new pages here are the consent page and “Connected agents”, both plain forms with labelled buttons.

Table 14.1 Nordlys after Chapter 14

| Check | Before | After | Why |
|---|---|---|---|
| isitagentready `oauthDiscovery` | fail | pass by the published criteria (not scanned) | `/.well-known/oauth-authorization-server` with issuer, endpoints and grant types |
| isitagentready `oauthProtectedResource` | fail | pass by the published criteria (not scanned) | `/.well-known/oauth-protected-resource` with `resource` and `authorization_servers` |
| isitagentready `authMd` | fail | unchanged | no `/auth.md` |
| isitagentready level | unchanged | one of the three Level 5 ingredients | Level 5 also needs Level 4 and one more ingredient |
| Lighthouse Agentic Browsing | unchanged | unchanged | no authorization audits |

Like in Chapter 12, I couldn’t scan the local demo with the public tool, so these results come from the published criteria and the layer’s own audit, which checks the same fields.

## What to watch

> **Still in flux:** The core of this chapter (OAuth roles, RFC 9728, RFC 8414, PKCE, audience-bound tokens) is stable. These parts are still moving:

- **OAuth 2.1** itself is still a draft (revision 17 in October 2026). Expect it to become an RFC with no changes that affect this chapter, but check.
- **Client ID Metadata Documents** (draft 02) is the registration model MCP recommends. Watch for it becoming an RFC and for your identity provider adding support.
- **DCR’s deprecation** in MCP comes with a migration window. Clients still use it today, so keep it working if your identity provider offers it.
- **DPoP and human-presence signals** are on the MCP roadmap.[^ch14-19]
- **Enterprise-Managed Authorization and ID-JAG** will spread to more identity providers and clients.
- **auth.md** and other proposals for agents that sign people *up* are early. Nice to know, not yet to build.

## Summary

- An agent acting for a user needs delegated access: who (the person), to whom (a named agent), what (scopes in plain words) and until when (short tokens, revocable grants). Passwords, shared browser sessions and copied API keys give none of these.
- MCP uses OAuth 2.1: the MCP server is a resource server, the agent is a client, and an authorization server signs the person in and issues tokens.
- Discovery is a chain: a 401 with `WWW-Authenticate`, Protected Resource Metadata (RFC 9728) at `/.well-known/oauth-protected-resource`, then authorization server metadata (RFC 8414 or OpenID Connect Discovery). A server without PKCE S256 is refused.
- Clients identify themselves with Client ID Metadata Documents (preferred), pre-registration or Dynamic Client Registration (deprecated in MCP 2026-07-28). ChatGPT, Codex and Claude support all three today.
- Tokens must be bound to one audience with the `resource` parameter, and MCP servers must not accept or pass through tokens issued for anything else.
- Ask for the smallest scopes first. Use `403 insufficient_scope` to step up to riskier permissions at the moment they are needed.
- Give members a “Connected agents” page where they can see and disconnect every agent. Make revocation take effect immediately.
- For production, use an identity provider that supports S256, `resource`, `iss`, CIMD (or DCR) and refresh token rotation. Enterprise products should plan for Enterprise-Managed Authorization with ID-JAG.
- isitagentready’s OAuth discovery and Protected Resource checks count toward Level 5. Radar found them on 8.1% and 4.1% of scanned domains.

[^ch14-1]: “Authorization”, Model Context Protocol specification, version 2026-07-28, https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization (retrieved November 2026).
[^ch14-3]: “The OAuth 2.1 Authorization Framework”, draft-ietf-oauth-v2-1-17, IETF Datatracker, https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/ (retrieved November 2026).
[^ch14-5]: M. Jones, P. Hunt, A. Parecki, “OAuth 2.0 Protected Resource Metadata”, RFC 9728, April 2025, https://www.rfc-editor.org/rfc/rfc9728 (retrieved November 2026).
[^ch14-6]: “Authorization Server Discovery”, Model Context Protocol specification, version 2026-07-28, https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/authorization-server-discovery (retrieved November 2026).
[^ch14-7]: “Security Considerations”, Model Context Protocol specification, version 2026-07-28, https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/security-considerations (retrieved November 2026).
[^ch14-8]: “Authentication”, OpenAI developer documentation for plugins, https://developers.openai.com/plugins/build/auth.md (retrieved November 2026).
[^ch14-9]: “Client Registration”, Model Context Protocol specification, version 2026-07-28, https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/client-registration (retrieved November 2026).
[^ch14-10]: “OAuth Client ID Metadata Document”, draft-ietf-oauth-client-id-metadata-document-02, IETF Datatracker, https://datatracker.ietf.org/doc/draft-ietf-oauth-client-id-metadata-document/ (retrieved November 2026).
[^ch14-11]: “Get started with custom connectors using remote MCP”, Claude Help Center, https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp (retrieved November 2026).
[^ch14-12]: “Security Considerations”, sections “Open Redirection” and “Client ID Metadata Document Security”, Model Context Protocol specification, version 2026-07-28, https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/security-considerations (retrieved November 2026).
[^ch14-13]: “Streamable HTTP”, Model Context Protocol specification, version 2026-07-28, https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http (retrieved November 2026).
[^ch14-14]: W. Denniss, J. Bradley, “OAuth 2.0 for Native Apps”, RFC 8252, October 2017, section 7.3, https://www.rfc-editor.org/rfc/rfc8252 (retrieved November 2026).
[^ch14-15]: “@cloudflare/workers-oauth-provider”, npm, https://www.npmjs.com/package/@cloudflare/workers-oauth-provider, version 1.2.4 (retrieved November 2026).
[^ch14-16]: “Introducing the Agent Readiness score. Is your site agent-ready?”, The Cloudflare Blog, https://blog.cloudflare.com/agent-readiness/, 17 April 2026 (retrieved November 2026).
[^ch14-17]: Paul Carleton, “Enterprise-Managed Authorization: Zero-touch OAuth for MCP”, Model Context Protocol Blog, 18 June 2026, https://blog.modelcontextprotocol.io/posts/enterprise-managed-auth/ (retrieved November 2026).
[^ch14-18]: “Identity Assertion JWT Authorization Grant”, draft-ietf-oauth-identity-assertion-authz-grant-06, IETF Datatracker, https://datatracker.ietf.org/doc/draft-ietf-oauth-identity-assertion-authz-grant/ (retrieved November 2026).
[^ch14-19]: “Roadmap”, Model Context Protocol, https://modelcontextprotocol.io/development/roadmap (retrieved November 2026).
[^ch14-20]: “auth.md: Open Protocol for Agent Registration”, WorkOS, https://workos.com/auth-md (retrieved November 2026).
[^ch14-21]: “AI Insights: Adoption of AI agent standards”, Cloudflare Radar, https://radar.cloudflare.com/ai-insights#adoption-of-ai-agent-standards, data dated 2 November 2026 (retrieved November 2026).
[^ch14-22]: “llms-full.txt”, isitagentready.com, https://isitagentready.com/llms-full.txt, checks 14 to 16 and “Levels” (retrieved November 2026).
