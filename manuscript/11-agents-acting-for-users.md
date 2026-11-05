# Chapter 11: Agents acting for users: delegated access and consent

This chapter covers

- Why an agent acting for a person needs delegated access, not that person's password or session
- OAuth 2.1 for MCP: the discovery chain, client registration, audience-bound tokens, scopes and step-up
- Three kinds of consent, and which steps should bring the person back into the loop
- Human-in-the-loop confirmations on the plain web, in MCP and in WebMCP, and telling the guest what happened
- The agent-safe checkout, and the two ways a shop can let an agent buy: in-page tools or a protocol checkout (UCP)

In Chapter 8 we gave Nordlys Cabins an MCP server. Any agent can search the cabins, check availability, book a stay and cancel a booking if it knows the reference and the email address. All of that works without knowing who the user is, and that was on purpose: a public catalogue and a public booking form need no login.

Now Ingrid Berg, one of our members, asks her assistant a different kind of question: “Which cabins have I booked for next year, and can you cancel the one in February?” To answer, the agent has to be Ingrid on nordlys.example, or at least act with her permission. The question this chapter answers is how a site lets that happen without handing the agent Ingrid’s password, without letting it do more than she wants, and with a way for Ingrid to switch it off.

The answer is OAuth, the same protocol that lets you “Sign in with Google” or connect a calendar app to your email. Nothing here is invented for agents. What is new is that in 2026 the AI platforms agreed on exactly how they use OAuth when they talk to an MCP server, and that agreement now lives in the MCP specification itself.[^ch11-1] If you implement it, ChatGPT, Claude, VS Code and any other compliant client can connect your users’ accounts in a few clicks. If you don’t, they can’t, and your users will find other ways, most of them worse.

This chapter puts the person back into the picture in three steps. First, OAuth, so that a member's agent can act for her with her permission and nothing more. Second, consent and the human in the loop, so that the steps that matter come back to the guest. Third, the moment an agent wants to pay: the agent-safe checkout, and what changes when a shop offers an agent two ways to buy.

## Why “just log in as me” is the wrong answer

The first shortcut is the password. A person gives an agent their username and password, or types them into a browsing agent’s window. The agent then has everything the person has: it can change the email address, read the payment history, book and cancel. It keeps that power until the password changes. And you, the site owner, can’t tell the agent apart from the person.

The second shortcut is the browser session. A browsing agent (Chapter 3) that runs in the person’s own browser is already signed in, because the cookies are there. That is convenient and often fine for a one-off task the person watches. But again the site sees no difference between the person and the agent, there is no limit on what the agent may do, and there is nothing to revoke except the whole session.

Delegated access fixes all three problems at once. When I explain it to a product manager I use four words:

- **Who.** Ingrid, signed in on your own site, with your own login (and her password never leaves your site).
- **To whom.** One specific agent application that the site can name: “Claude”, “ChatGPT”, “Nordlys demo agent”. Not “someone with Ingrid’s password”.
- **What.** A limited set of permissions, called **scopes**, written in words a person understands: “See your Nordlys bookings”, “Cancel your Nordlys bookings”.
- **Until when.** Tokens that expire within minutes, renew only while the permission stands, and stop working the moment Ingrid presses “Disconnect”.

That is what OAuth gives you. In simple words, OAuth is a way for a person to give an application a key to some of their rooms, for a limited time, without giving away the house keys. The rest of this chapter is about the details that make the key safe and the agents able to find the door.

## The cast: four roles

OAuth has four roles, and MCP maps them onto your site like this.[^ch11-1]

- The **resource owner** is the person, Ingrid.
- The **client** is the agent application acting for her: ChatGPT, Claude, Codex, VS Code, or the small command-line agent in the demos (`chapters/11-agents-acting-for-users`). In MCP terms this is the MCP client.
- The **resource server** is what the agent wants to use: our MCP server at `/mcp`. The specification says it plainly: “A protected MCP server acts as an OAuth 2.1 resource server”.[^ch11-1]
- The **authorization server** is the part that signs Ingrid in, asks for her consent and issues tokens. It “may be hosted with the resource server or a separate entity”.[^ch11-1] For a real business this is usually the identity provider you already use for member login. For Nordlys we build a small one, so you can see every step.

![Figure 11.1 — The four OAuth roles on nordlys.example. Ingrid (the resource owner) uses an agent (the client). The agent calls the MCP server at /mcp (the resource server) with an access token. The authorization server at /oauth signs Ingrid in, shows the consent page and issues tokens. Ingrid’s password only ever goes to nordlys.example.](images/figure-11-1.png)

Which version of OAuth? MCP builds on **OAuth 2.1**, a consolidation of OAuth 2.0 and its security best practices. OAuth 2.1 is still an Internet-Draft. In November 2026 the current revision is `draft-ietf-oauth-v2-1-17`, while the MCP specification cites revision 13.[^ch11-2] Don’t let the draft status scare you: what OAuth 2.1 “changes” is mostly that it removes the risky parts of OAuth 2.0 (the implicit flow, the password grant) and makes PKCE mandatory. Every serious identity provider has supported that subset for years.

## How an agent finds your login: the discovery chain

The clever part of MCP authorization is that an agent needs to know nothing about your site in advance except the address of your MCP server. Everything else it discovers. Figure 11.2 shows the whole chain, and we’ll walk through it step by step.

![Figure 11.2 — Discovery and authorization in MCP. (1) The agent calls a member tool without a token and gets 401 with a WWW-Authenticate challenge. (2) It reads the Protected Resource Metadata named in the challenge, which lists the authorization server. (3) It reads the authorization server metadata. (4) It sends Ingrid to the authorization endpoint with PKCE and the resource parameter, Ingrid signs in and allows access. (5) The agent exchanges the code for a token. (6) It repeats the tool call with the token.](images/figure-11-2.png)

### Step 1: the 401 challenge

The agent calls a tool that needs a member, without a token. The server answers with HTTP 401 and a `WWW-Authenticate` header. The MCP specification gives this example:[^ch11-1]

```text
HTTP/1.1 401 Unauthorized
WWW-Authenticate: Bearer resource_metadata="https://mcp.example.com/.well-known/oauth-protected-resource",
                         scope="files:read"
```

Two things are in the challenge. `resource_metadata` says where the agent can read about this protected resource. `scope` says which permission this particular request needs. MCP servers “SHOULD include a scope parameter”, and clients “MUST treat the scopes provided in the challenge as authoritative for the current operation”.[^ch11-1]

### Step 2: Protected Resource Metadata (RFC 9728)

The document behind `resource_metadata` is **OAuth 2.0 Protected Resource Metadata**, RFC 9728, published in April 2025.[^ch11-3] It is a small JSON document where a resource server says who it is (`resource`), which authorization servers issue tokens for it (`authorization_servers`), and which scopes it understands (`scopes_supported`). The MCP specification makes it mandatory on both sides: “MCP servers MUST implement OAuth 2.0 Protected Resource Metadata (RFC9728)”, and clients must use it to find the authorization server.[^ch11-1]

### Step 3: authorization server metadata (RFC 8414)

Now the agent knows the issuer of the authorization server, for Nordlys simply `https://nordlys.example`. It reads the server’s own metadata, defined in RFC 8414 (2018) for OAuth and in OpenID Connect Discovery for OpenID providers. MCP clients “MUST support both discovery mechanisms”, and for an issuer without a path they try `/.well-known/oauth-authorization-server` first and `/.well-known/openid-configuration` second.[^ch11-4] After fetching, “the issuer value in the document MUST be identical to the issuer identifier used to construct the well-known URL”. If not, the client must not use it.[^ch11-4]

From this document the agent learns where to send the person (`authorization_endpoint`), where to exchange codes for tokens (`token_endpoint`), and which features the server supports. One field decides whether the journey continues at all: `code_challenge_methods_supported`. The MCP specification says that if it is absent, “the authorization server does not support PKCE and MCP clients MUST refuse to proceed”.[^ch11-5] OpenAI’s documentation for ChatGPT and Codex says the same in practical terms: MCP servers “are unsupported when their authorization server metadata omits this field or does not advertise `S256`“.[^ch11-6]

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

- **PKCE** (`code_challenge` and later `code_verifier`). The agent makes up a random secret, sends only its SHA-256 hash at the start, and reveals the secret when it exchanges the code. Someone who steals the code from the redirect can’t use it without the secret. MCP clients “MUST use the S256 code challenge method”.[^ch11-5]
- **`resource`** (RFC 8707, Resource Indicators). The agent says which resource the token is for. MCP clients “MUST include the resource parameter in authorization and token requests”.[^ch11-5] We’ll see in a moment why this matters so much.
- **`state`**, and since the 2026-07-28 revision the **`iss`** parameter in the response (RFC 9207). The agent checks that the answer belongs to the request it sent, and that it came from the authorization server it expected. The MCP specification asks authorization servers to include `iss` and to advertise it with `authorization_response_iss_parameter_supported`.[^ch11-1] OpenAI’s hosts rely on it to protect their callbacks against “authorization server mix-up attacks”.[^ch11-6]

### Step 5 and 6: the token, and the call again

The agent sends the code, the PKCE secret and the same `resource` to the token endpoint and gets an **access token** (and usually a **refresh token** to get new access tokens later). Then it repeats the original tool call with `Authorization: Bearer <access token>`. The server checks the token and runs the tool.

That’s the whole chain. It looks like a lot of steps on paper, but all of it happens in a second or two, and from Ingrid’s point of view it is one page: “Claude wants to use your Nordlys account. Allow?”

## Who is the agent? Client registration in 2026

There is one question the discovery chain skipped: what is the `client_id`? OAuth needs to know which application is asking, both to show its name on the consent page and to check where it may send the code. Traditionally a developer registered every application with every authorization server by hand. That obviously doesn’t work when any of thousands of agents may want to connect to any of thousands of MCP servers.

The MCP specification of 28 July 2026 lists three ways, in this order of preference:[^ch11-7]

1. **Pre-registration**, “when client and server have an existing relationship”. The site gives the agent a client ID up front. Fine for your own apps and for partners you sign contracts with.
2. **Client ID Metadata Documents (CIMD)**, “when client and server have no prior relationship (most common)”. The client ID is an HTTPS URL, and at that URL the client publishes a JSON document with its name, logo and redirect URIs. The authorization server fetches it when it sees the client ID for the first time. There is nothing to register.
3. **Dynamic Client Registration (DCR)**, RFC 7591, where the client registers itself through an API on the authorization server. In the 2026-07-28 revision, “Dynamic Client Registration is deprecated”, kept “for backwards compatibility with authorization servers that do not support Client ID Metadata Documents”.[^ch11-7]

## Tokens that only work in one place

Now back to the `resource` parameter, because it protects against a mistake that is easy to make when you connect several services.

Imagine a token that Ingrid’s agent got for the Nordlys MCP server. If that token were also accepted by, say, the Nordlys payments API (or by any other service that trusts the same identity provider), then a malicious or buggy MCP server could take the token it received and use it somewhere else. That is called a **confused deputy** or **token passthrough** problem, and the MCP specification is strict about it. Servers “MUST validate that access tokens were issued specifically for them as the intended audience”, “MUST only accept tokens that are valid for use with their own resources”, and when an MCP server calls another API, “The MCP server MUST NOT pass through the token it received from the MCP client”.[^ch11-5][^ch11-1]

In practice it means three checks on every request: the token was signed by your authorization server, it is not expired, and its audience (the `aud` claim in a JWT, or the equivalent field your identity provider returns from token introspection) is exactly your MCP server’s URL. If any check fails, the answer is 401: “Invalid or expired tokens MUST receive a HTTP 401 response.”[^ch11-1]

## Scopes and step-up: asking for more only when needed

Scopes are where product thinking meets protocol. A scope is a named permission, and the consent page turns it into a sentence. Good scopes follow what users understand, not what your database tables look like. For Nordlys I chose two:

| Scope | Consent page says | Used by |
|---|---|---|
| `bookings:read` | See your Nordlys bookings | `list_my_bookings` |
| `bookings:write` | Cancel your Nordlys bookings | `cancel_my_booking` |

What about searching cabins and creating a booking? Those stay public, exactly as in Chapter 8. Anyone can book a cabin on the website without an account, so an agent can too. And payment is not a scope at all: as the agent-safe checkout later in this chapter shows, the guest pays on the site.

Should an agent ask for everything at once? The specification says no. Clients “SHOULD follow the principle of least privilege by requesting only the scopes necessary for their intended operations”, and the `scopes_supported` list “is intended to represent the minimal set of scopes necessary for basic functionality”, with more scopes “requested incrementally through the step-up authorization flow”.[^ch11-1]

**Step-up** works like this. The agent has a token with `bookings:read`. Ingrid asks it to cancel a booking. The agent calls `cancel_my_booking`, and the server answers:

```text
HTTP/1.1 403 Forbidden
WWW-Authenticate: Bearer error="insufficient_scope", scope="bookings:write",
                  resource_metadata="https://nordlys.example/.well-known/oauth-protected-resource/mcp",
                  error_description="This tool needs: Cancel your Nordlys bookings."
```

That’s the response format from the specification: status 403, `error="insufficient_scope"`, the scopes the operation needs, and the metadata address “for consistency with 401 responses”.[^ch11-1] The agent then sends Ingrid through the consent page again, asking for the union of what it already had and what it now needs, gets a new token and retries. Clients acting for a user “SHOULD attempt the step-up authorization flow”, and they should not retry forever.[^ch11-1]

## Hands-on: delegated access for Nordlys members

> **Hands-on:** This section builds layer `11-oauth` of the demo app and a small command-line agent in `demos/chapters/11-agents-acting-for-users`. If you don’t read JavaScript, here is the short version: the site publishes two small JSON files that tell agents where its login is, shows members a consent page, gives agents short-lived tokens, and lets members see and disconnect agents. Pick up again at “Build it or use your identity provider?”.

The layer needs the MCP server from Chapter 8 and adds no dependencies: tokens are signed with Ed25519 from `node:crypto`. Start the app with `npm start -- --upto=11`, which turns on this chapter's layers and every layer before them. These are the new addresses:

- `/.well-known/oauth-protected-resource/mcp` (and the same document at the root)
- `/.well-known/oauth-authorization-server`
- `/oauth/authorize`, `/oauth/token`, `/oauth/revoke` and `/oauth/jwks.json`
- `/account/agents`, the member’s “Connected agents” page
- two new MCP tools, `list_my_bookings` and `cancel_my_booking`

### Checking every call to /mcp

Listing 11.1 is the heart of the resource server: a middleware that runs before the MCP handler from Chapter 8. It verifies a token if there is one, and it challenges when a member tool is called without the right scope.

**Listing 11.1** `nordlys-cabins/layers/11-oauth/resource-server.js` (excerpt) — verifying tokens and challenging

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

### The authorization endpoint and the consent page

Before it shows anything to the person, the authorization endpoint validates the request. The order matters. The client and its redirect URI are checked first, and if they fail, the error is shown on Nordlys’s own page. Only after the redirect URI is known to belong to the client may errors be sent back to it. Otherwise an attacker could use your authorization server to redirect people anywhere, which the MCP specification calls open redirection and forbids: authorization servers “MUST validate exact redirect URIs against pre-registered values”.[^ch11-8]

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

### “Connected agents”: the page your members need

The last part of the layer is a page that most OAuth tutorials skip, and I think it is the most important one for trust. At `/account/agents`, a signed-in member sees every agent that may act for them, what it may do, when it was connected and when it last did something, with a **Disconnect** button next to each. Disconnecting revokes the grant, deletes its refresh tokens, and (because the resource server checks the grant on every call) stops the current access token immediately. The same happens when an agent calls the RFC 7009 revocation endpoint itself.

If you remember one thing from this chapter for your product backlog, make it this page. People will connect agents to their accounts more easily when they can see them and switch them off.

## Build it or use your identity provider?

We built an authorization server so you can see every moving part. For a real business I would not ship one written for a book. Authorization servers fail in subtle ways, and the identity provider you already use for member login (or a managed one) has been hardened by people who do nothing else.

## Agents at work: Enterprise-Managed Authorization

Everything so far assumed a person who decides, one server at a time. Companies don’t work like that. An employee doesn’t want to press Allow for twenty internal tools, and the security team wants one place to say who may use what.

For a cabin-rental site with consumer members, EMA doesn’t matter. For a SaaS product sold to companies, it will soon be on the checklist of every enterprise buyer, and the authorization server you choose should be able to accept ID-JAG grants.

### Don’t confuse the two kinds of identity

One last distinction before we measure, because readers (and vendors) mix it up all the time. OAuth, as in this chapter, answers: **did this person allow this application to act for them?** It says nothing reliable about which company runs the agent’s servers or whether the traffic really comes from it. That second question, **who operates this agent?**, is answered by Web Bot Auth and HTTP message signatures, and that is Chapter 4. A booking site wants both answers: the signature tells you the request really comes from, say, OpenAI’s agent, and the token tells you that Ingrid allowed that agent to see her bookings.

Delegated access answers whether a person allowed an application to act for them. It does not answer whether the person wanted this particular booking, on these terms, at this price. That is the work of consent, and it is the second half of this chapter.

## Three kinds of consent

The word "consent" causes more confusion in agent discussions than any other, because it is used for three different things. Let's separate them, using Nordlys as the example.

### Consent as a lawful basis

In GDPR language, consent is one of the six lawful bases, with strict conditions (freely given, specific, informed, unambiguous, as easy to withdraw as to give). For a cabin booking, consent is usually the *wrong* basis: the booking is a contract, and Article 6(1)(b) covers the processing it needs. You do not need a "consent checkbox" for processing the guest's name to book the cabin they asked for, whether a person or an agent sent it.

### Consent as authority

The second meaning is "did Astrid actually ask for this?". When a booking arrives through the MCP server with a valid token from the OAuth layer, Astrid has authorised the assistant to act on Nordlys for her, within the scopes she granted. That is real authority, recorded by the authorisation server. When a booking arrives through the public API or an anonymous MCP call, Nordlys only has the agent's word for it.

This is the core problem of agent consent, and no protocol solves it today. The emerging answer in agent commerce is the signed mandate (AP2 and its relatives, listed in Appendix B), where the user's instruction travels with cryptographic proof. Until those are common, a site has two tools: keep a record of what it was told and how (so the question can be answered later), and for consequential steps, bring the person to a page where the site sees their decision with its own eyes. Both are built in this chapter.

### Consent as acceptance of the terms

The third meaning is contractual. A booking includes cancellation terms, and the guest has to accept them. Nordlys's form has a checkbox. Chapter 8's `create_booking` tool requires `acceptTerms` to be the literal value `true`, which means the agent has to state, explicitly, that the user accepted. The checkout handoff later in this chapter goes further: the guest accepts the terms on Nordlys's own page.

Both are legitimate designs, and the choice is a business decision. An agent accepting terms on a user's behalf is like a travel agent doing it, and the agent's provider and the user have their own agreement about that. But it is weaker evidence, and when something goes wrong, the dispute is about who said what. For Nordlys, I recommend this split: flexible-rate stays booked by a signed-in member with a `bookings:write` token may go through `create_booking`, and everything else (first-time guests, non-refundable stays, anything without a verified member) goes through `request_booking`, which ends on our page. You can encode this split in the tool descriptions and enforce it in the handler.

### A word on GDPR

The General Data Protection Regulation (GDPR) applies to agent traffic the way it applies to all processing. Two data protection authorities have published early analyses of agentic AI. The UK Information Commissioner's Office (ICO) published a Tech Futures report on agentic AI in January 2026, which it says is not intended as guidance.[^ch11-9] Spain's data protection authority, the AEPD, published "Inteligencia Artificial Agéntica desde la perspectiva de Protección de Datos" in February 2026.[^ch11-10] Its warning about agent memories applies to our logs too: in a law firm's summary, keeping lots of data "just in case" or to "optimize performance" can clash with purpose limitation and data minimisation.[^ch11-11] I read both reports through those summaries (the ICO page sat behind a bot challenge for us), so read the originals before you quote them in a policy.

**Data minimisation, Article 5(1)(c).** Personal data must be "adequate, relevant and limited to what is necessary in relation to the purposes for which they are processed".[^ch11-12] For agents this has a very concrete meaning: a tool returns the fields the task needs. Chapter 10's `get_booking` tool returns the cabin, dates, guests, total and cancellation deadline, and no name, email, phone or free-text requests. An agent planning a trip needs nothing more. The same article's purpose limitation (5(1)(b)) and storage limitation (5(1)(e)) apply to the tool-call log: it exists for security investigations, so it holds what an investigation needs, for as long as one is plausible.

## The human in the loop

Now to the design question that sits under all three kinds of consent. Which steps should an agent be allowed to complete alone, and which should bring the person back? And when the person must come back, how does the agent bring them?

The first question is a product decision. Here is how I would frame it for Nordlys, and the same questions work for most sites:

| Step | Agent alone? | Why |
| --- | --- | --- |
| Search cabins, check availability, read reviews | Yes | Read-only, no personal data |
| Look up one's own booking | Yes, with proof of ownership | Read-only, minimal output (Chapter 10) |
| Book a flexible-rate stay as a signed-in member with a write token | Yes | Verified authority, free cancellation as the safety net |
| Book as a first-time guest, or a non-refundable stay | No, the guest confirms on our page | Weak authority, a mistake costs the guest money |
| Pay, or enter card details | Never through the agent | Payment data belongs on our page (MCP requires this, see below) |
| Cancel a booking | Yes with a write token, otherwise with a confirmation | Hard to undo once the cabin is rebooked |

The second question has three answers, one per kind of agent interface.

### On the plain web: the confirmation page

The oldest human checkpoint is a page. Nordlys has one, and the agent-safe checkout later in this chapter shows how it is built: the agent prepares a booking session, the session's `continue_url` points at `/checkout/{id}` on Nordlys's own site, and the guest reviews the stay and confirms it there. "An assistant prepared this booking for you. Nothing is booked until you confirm it here."

For designers, three details make such a page work. First, show the facts the agent might have gotten wrong: dates in words ("Mon, 8 Feb 2027 to Fri, 12 Feb 2027"), number of guests, total with fees, cancellation deadline. Second, show what the agent sent and let the guest change it, because the name and email came through a machine. Third, make the page expire (the Nordlys booking sessions last 15 minutes) and say so, so a forgotten link cannot be confirmed weeks later at an old price.

This works with every agent, because every agent can hand a link to its user. Its weakness is the gap: after handing over the link, the agent does not know whether the guest confirmed. That is what the protocols below add.

### In MCP: multi round-trip requests

MCP has had a way for servers to ask the user something since 2025: elicitation. In the 2026-07-28 revision, the way it travels changed. Earlier, a server sent an `elicitation/create` request to the client in the middle of a tool call, which needed a stateful connection. The new revision introduced **multi round-trip requests** (MRTR): the tool call itself answers with "input required", the client collects the input, and then it calls the tool again with the answers. The specification is blunt about the change: servers MUST use the MRTR pattern for server-to-client requests, "The previous pattern of server-initiated requests is no longer supported. This is a breaking change."[^ch11-13]

Elicitation has two modes, and the difference is the heart of this section.[^ch11-14]

- **Form mode** collects structured data through the client. The server sends a small JSON Schema, and the client shows a form to the user. Contact details such as a name or email address are allowed, "subject to the user's ability to review and decline".
- **URL mode** sends the user to a page outside the client, for "interactions that must not pass through the MCP client". The spec names auth flows and payment processing as the typical uses. URL mode arrived in the 2025-11-25 revision, and the specification warns that its design "may change in future protocol revisions".

The rule that connects the two is a MUST: "Servers MUST NOT use form mode elicitation to request sensitive information such as passwords, API keys, access tokens, or payment credentials" and "Servers MUST use URL mode for interactions involving such sensitive information". Clients have MUSTs too: they make clear which server is asking, offer decline and cancel, let the user review a form before sending, and for URL mode, "clearly display the target domain/host and gather user consent before navigation to the target URL".

Figure 11.3 shows how `request_booking`, the new Nordlys tool, uses both modes in three rounds.

![Figure 11.3 — request_booking in three rounds. Round 1: the tool opens a booking session and answers input_required with a form-mode request for name and email. Round 2: the client calls again with the answers, and the tool answers input_required with a URL-mode request for the checkout page. The guest confirms there, on Nordlys. Round 3: the client calls again, and the tool returns the booking reference only if the guest confirmed.](images/figure-11-3.png)

> **Hands-on:** The next page shows `request_booking` from `layers/11-consent/` on the wire (its code and tests are in the demos). If you don't write code, here is what it achieves: an agent can prepare a booking, ask its user for a name and email in its own interface, and then hand the user a link to Nordlys's checkout page. The booking exists only after the guest confirms on that page, and the agent finds out when it asks again. Pick up again at "In WebMCP: an open question".

Here is what the first answer looks like on the wire. The agent called `request_booking` for Fjellro, and instead of a result, it got this.

**Listing 11.2** The first `tools/call` answer from `request_booking` (captured from the demo)

```json
{
  "result": {
    "resultType": "input_required",
    "inputRequests": {
      "guest": {
        "method": "elicitation/create",
        "params": {
          "message": "Who is staying at Fjellro? Nordlys sends the confirmation to this email.",
          "requestedSchema": {
            "type": "object",
            "properties": {
              "name": {
                "type": "string",
                "description": "Full name of the main guest",
                "minLength": 2
              },
              "email": {
                "type": "string",
                "description": "Email address for the confirmation",
                "format": "email"
              }
            },
            "required": [
              "name",
              "email"
            ],
            "$schema": "https://json-schema.org/draft/2020-12/schema"
          },
          "mode": "form"
        }
      }
    },
    "requestState": "eyJzdGVwIjoiZ3Vlc3QiLCJzZXNzaW9uIjoiYmtzXzZSempIN2xLUTBLZ2cwWlMiLCJiaW5kIjoiZ296RUNNeTE1SnpyY0pfTkxDLVlQeG13bmpIeXJsR0hHZnlZbnllcXhxdyIsImV4cCI6MTc5MzY1ODU3ODQ4M30.XhIPeRHStaYf0w6b_XsxBIw8k5bmX6_0tlQ1duDT8M0",
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

Three fields carry the pattern. `resultType: "input_required"` tells the client this is not the end. `inputRequests` is a map of embedded requests, here one form-mode elicitation keyed `guest` (the key is the server's choice). And `requestState` is an opaque string that the client must echo back, byte for byte, on the next call. It is how a stateless server remembers where it was: the client carries the state, and the server does not need a session store.

### In WebMCP: an open question

What about tools inside the page, with WebMCP (Chapter 9)? Here the honest answer is that the human-in-the-loop API is not settled. The WebMCP specification draft of 27 October 2026 has no method for it in its interface definitions.[^ch11-15] An open pull request, "Replace requestUserInteraction with requestUserInput", proposes three modes (interactive, form and url) aligned with MCP elicitation.[^ch11-16] Meanwhile, Chrome's page on WebMCP tool security, updated 1 September 2026, still says "the spec draft includes `requestUserInteraction()`".[^ch11-17] I would not write production code against either name yet.

The good news is that WebMCP needs it less than MCP does. A WebMCP tool runs in a page the user has open, in their browser. The user is already there. So the human-in-the-loop pattern for WebMCP today is the page itself:

- Mark the tool with `consequentialHint: true`, so the agent or browser can ask the user before it runs.
- Let the tool *prepare* the action and show it in the page's own UI (a filled-in booking summary with a "Confirm" button), and return a result that says "waiting for the user to confirm on the page".
- Or return the URL of the confirmation page, exactly like `continue_url`, and let the agent navigate there.

The hint alone leaves the asking to the agent or browser. In the other two, the confirmation is a real page element the person clicks, which is the strongest evidence a site can have that they agreed.

## Telling the guest what happened

Transparency is the cheapest privacy measure and the one guests notice. When an agent books for Astrid, she should hear about it from Nordlys, not only from her assistant. If her assistant misunderstood ("book Fjellro for the winter break" became the wrong week), the email is how she finds out in time to cancel for free.

### The email

For every booking that arrives through an agent channel, the consent layer keeps a record of who agreed to what, and it sends the guest a short notice. In the demo, mail goes to an in-memory outbox so the tests can read it. In production, it would go to your mailer, in the same template as your confirmation email.

**Listing 11.3** The notice Astrid receives (from the demo outbox)

```text
To: astrid@example.no
Subject: Your Nordlys booking NC-UW2KMJ was made with an AI assistant

Hello Astrid,

An AI assistant prepared this booking and you confirmed it on nordlys.example.
The assistant identified itself as "mcp:example-agent".
Fjellro, Mon, 8 Feb 2027 to Fri, 12 Feb 2027, 3 guests.
We received: name, email, dates, guests.

If you did not ask for this booking, cancel it free of charge until 2027-01-25:
https://nordlys.example/bookings
See everything agents did with your bookings: https://nordlys.example/account/agent-activity
```

Each line has a job. The subject says what happened. The first lines say how, and what the assistant called itself. The data line is the minimisation promise made visible. The last lines give the two ways out: cancel for free (with the deadline), and look at everything agents did.

### What agents did, on one page

The page at `/account/agent-activity` shows a guest the records of their bookings and, for signed-in members, the tool calls made with their account from the Chapter 10 log. A guest without an account proves ownership the same way as on the bookings page, with a reference and its email address.

## The agent-safe checkout

The last thing a guest's agent may want to do is pay. When a person books a cabin on nordlys.example today, four things happen that nobody writes down. The person sees the final price, with the cleaning fee. The person reads (or at least could read) the cancellation terms. The person types their own card details into a payment page, often with a bank app confirming the payment. And Nordlys is the merchant of record: the company the guest pays, the name on the card statement, the one who handles refunds and complaints.

An agent in the middle can break each of these. It can see a price that changed a minute later. It can skip the terms. It can be asked to handle card numbers it should never touch. And it can be run by a company that decides to become the merchant itself, which is exactly what happened with some of the first shopping experiences in AI assistants. That is why I think about agent commerce as four questions, and every protocol in this chapter answers some of them:

1. **What exactly is being bought?** The cabin, the dates, the guests, the total, the cancellation terms. The agent and the site must agree on one authoritative version of this, with an expiry.
2. **Did the person agree to it?** Not “did the person ask an agent to find a cabin”, but “did the person approve this booking at this price”. This is the hardest question and the one with the most new technology.
3. **Who is paying, and with what?** A card, a wallet, a bank transfer, a stablecoin, and who touches the credentials on the way.
4. **Who is the agent?** Is this request really from the assistant it claims to be, run by a company you can hold to account? That question is big enough for its own chapter (Chapter 4), but card networks build on it, so it shows up here too.

Keep these four questions in mind. When a vendor pitches you an agent commerce integration, ask which of the four it answers and which it leaves to you.

### How much of this is real today

Before the details, let’s have a look at adoption, so we keep our feet on the ground. Cloudflare Radar scans the top 200,000 domains for agent standards, and on 2 November 2026 it had results for 115,468 of them.[^ch11-18] The Universal Commerce Protocol profile was on 5,429 domains (4.7%). The Agentic Commerce Protocol discovery file was on 32 domains. MPP was on 13, x402 on 7 and AP2 on 4. Radar’s own footnote reminds us that “x402 is only relevant for sites with paid content”, so a low number there is not a failure.[^ch11-18]

### UCP in brief

UCP is an open standard for the whole shopping journey between an AI platform (the agent’s side) and a business. Its site lists co-developers in three groups. Shopping has Google, Shopify, Etsy, Wayfair, Target, Walmart, Amazon, Microsoft, Meta, Salesforce and Stripe. Lodging has Amadeus, Booking.com, Expedia Group, Google, Hilton, Marriott and Trip.com. Food has DoorDash, Google, Square, Toast and Uber Eats.[^ch11-19] The business stays the merchant of record, and the site describes account linking through OAuth 2.0 and payments through AP2 (this chapter covers the first, and Appendix B lists the second).[^ch11-19]

The core idea is a **business profile** at a well-known address, `/.well-known/ucp`. In the specification’s words, platforms “MUST resolve schemas following this sequence”, and the first step is “Discovery: Fetch business profile from /.well-known/ucp”.[^ch11-20] The profile is a JSON document with one required member, `ucp`, which carries:

The latest released version on 2 November 2026 was 2026-08-25, tagged in the project’s repository on 25 August 2026.[^ch11-21]

Next to UCP there is a crowd of other protocols: ACP for agentic checkout, AP2 for signed mandates, the card networks' agent programmes, and x402 and MPP for paying per request. Appendix B lines them up with their status and date, and Appendix C covers the per-request payments. For a small booking site, the decision is simpler than the acronyms suggest.

## What a small booking site should do in November 2026

**Do now.** Make availability, prices and booking readable and callable, which the earlier chapters already did. Then add a handoff: an agent can prepare a complete booking (cabin, dates, guests, the all-in price, the cancellation terms), and the guest finishes it on your own site. That gives the agent a clear, machine-readable path to “almost done”, and it keeps the four things from the start of this section in your hands: the final price, the terms, the payment page and the merchant-of-record role.

**Never do.** Let an agent type card numbers into your forms on a person’s behalf, or accept card data through an API or tool that an agent calls. UCP’s whole payment design, ACP’s delegated tokens and AP2’s mandates exist precisely so that raw card details do not pass through the agent.

### Five rules for a safe checkout

Strip away the protocols' field names, and the safe way for an agent to buy is a pattern you can apply to any site, with or without a commerce protocol. Nordlys's demo layer `11-commerce` implements it with booking sessions shaped after the UCP Lodging draft, and Figure 11.4 shows the flow:

1. **The agent asks, the server quotes.** The price, the fees and the terms come from your server, computed by the same code your own pages use. Never let an agent send you a price.
2. **The quote has an identity and an expiry.** A session id, a fixed set of terms and an `expires_at`. If prices or availability change, the agent gets a new quote, never a silently different one. The UCP draft calls this out explicitly: when totals change during a session, the business reports a `totals_changed` warning, and the platform must show it.[^ch11-22]
3. **The decision happens on your page.** The person reviews exactly what the agent prepared, on your domain, in your design, under your terms. That page is also where your PSP’s payment step lives.
4. **The form can add, not change.** Whatever the confirmation page accepts must not alter the quote.
5. **The agent learns the outcome.** A machine-readable status (`completed` plus a confirmation, or `canceled`) so the agent can close the loop with the person.

The same pattern works as an MCP tool or a WebMCP tool that returns a link, as a REST endpoint from Chapter 8, or as a plain deep link to your booking form with the dates filled in. The protocol adds discoverability and a shared vocabulary. It does not add safety, because the safety comes from step 3.

![Figure 11.4 — The agent-safe checkout for Nordlys Cabins. The agent creates a booking session and receives the all-in price, the cancellation terms and continue_url. Complete returns the same session. The guest opens continue_url on nordlys.example, reviews and confirms, the store creates the booking, and the agent reads the completed session with its confirmation.](images/figure-11-4.png)

### Can’t a browsing agent just press the button?

Yes, it can, and I want to be honest about it. A browsing agent (Chapter 3) that runs in the person’s own browser can open `continue_url` and click “Confirm and book”. From the server’s point of view it looks exactly like the person doing it. A protocol cannot draw the line between “the person pressed it” and “the person’s agent pressed it” on a web page. Three things still make the design worth it.

First, the browsers already treat sensitive moments as special. Chrome documents defences for its agent such as a second model that vets each action and deterministic confirmations before certain sensitive sites, and every agent vendor writes about prompt injection as an unsolved problem (Chapter 10 has the details and the sources). Second, the payment step is a separate gate. In the European Economic Area, which includes Norway, online card payments generally go through strong customer authentication under the PSD2 rules, and it happens between the cardholder and their bank, often in a banking app.[^ch11-23] How that works when an agent prepared the booking is a question for your PSP, and it is one more reason to keep the payment on your own page. Third, the page shows the person a complete, honest summary at the exact moment they decide, which is the point of the “trusted UI” wording in the draft.

What the site owner owns is making that page impossible to misunderstand: the total with every fee, the dates in words, the cancellation terms, the expiry.

## Two ways to buy: in-page tools or a protocol checkout

A shop that has done everything in this book so far can end up offering an agent two ways to buy. One is in the page: WebMCP tools (Chapter 9) that fill the cart and lead to checkout in the person's own browser. The other is outside the page: a protocol checkout announced at `/.well-known/ucp`, which the agent's platform talks to directly. Nordlys has a small version of both: `start_booking` in the page, which prepares a booking and leaves the commit to the guest (Chapter 9), and the UCP-shaped booking sessions of the demo's commerce layer, which end on Nordlys's own confirmation page. Francesco Marinoni Moretto, who maintains the Agentic Standards Map, asked the questions every commerce team will ask about this pair: which one should an agent use, do the human-in-the-loop guarantees carry over, and which record does a dispute rely on?[^ch11-24]

This is not a thought experiment. On 4 November 2026 I fetched `/.well-known/ucp` from three Shopify stores (allbirds.com, kyliecosmetics.com and www.tentree.com). Each one returned a UCP profile for version 2026-08-25 with a server-side MCP endpoint and cart, checkout and order capabilities.[^ch11-25] Shopify also ships WebMCP tools for its checkout, and on Shopify the two channels are one checkout, not two. Its documentation says that Checkout WebMCP "implements the UCP checkout capability (`dev.ucp.shopping.checkout`) over browser-registered WebMCP tools instead of server-side JSON-RPC", and that both share the checkout object, its statuses and its messages.[^ch11-26]

### Which one should an agent use?

Shopify's answer for its own stores is short: "Use Checkout WebMCP when your agent runs in the buyer's browser. If your agent can run on a server, then use Checkout MCP."[^ch11-26] That is a sensible rule, and it is one platform's guidance. Neither the WebMCP specification nor the UCP specification tells an agent how to choose when a site offers both, or what should happen when the two lead to different checkouts. My advice for your own site follows from the five rules of the agent-safe checkout: let both channels end in the same server-side quote and the same confirmation step, so that the choice doesn't matter for safety.

### Do the human-in-the-loop guarantees carry over?

Not by themselves. In the page, the confirmation is part of the site: the person sees the plan in their own tab, and the page decides when anything is committed. A protocol checkout runs outside the page, so it gets only the guarantees its protocol writes down. UCP writes one down for the base case. Its checkout specification says that the checkout "has to be finalized manually by the user through a trusted UI unless the AP2 Mandates extension is supported", and when the business needs the buyer, the session moves to `requires_escalation` and hands the buyer over through a `continue_url`.[^ch11-27]

None of the three profiles I fetched advertised the AP2 mandates extension. They all list UCP's buyer consent extension, but that one covers data use and marketing preferences, not the purchase itself.[^ch11-25][^ch11-27] So on those stores a person still gives the final yes in both channels. What the specification leaves open is what the "trusted UI" must show. Whether it has the protections of this chapter (the total with every fee, the dates in words, the expiry) depends on who builds it, which is one more reason to make it your own page.

### Which record does a dispute rely on?

Neither specification says. UCP gives the merchant an order that keeps its `checkout_id` "for reconciliation" and records refunds, returns and disputes as adjustments. With AP2 mandates, the signed proofs that the user authorized the checkout "are stored as evidence of user consent".[^ch11-27] WebMCP produces no record of its own, so the page's logs are the only trace of what a tool prepared. And the legal question underneath is still open: whether a confirmation reached through an agent counts as the consumer's explicit acknowledgement of the obligation to pay, the point Marinoni Moretto raised about Article 8(2) of the EU Consumer Rights Directive.[^ch11-28]

Until someone answers it, I would keep one order history for both channels. It records the channel, the tool calls or protocol requests that prepared the order, and the screen where the guest confirmed. For Nordlys, that is the agent booking record and the activity page from earlier in this chapter, extended to protocol sessions. And, as with everything legal in this book, take that half of the question to a lawyer.

## Summary

- An agent acting for a user needs delegated access: who (the person), what (the scopes), where (the audience), for how long, and a way to take it back. Passwords, shared sessions and pasted API keys fail on all of these.
- MCP authorization is OAuth 2.1 with a discovery chain: a 401 challenge points to Protected Resource Metadata (RFC 9728), which points to the authorization server metadata (RFC 8414). The agent needs to know nothing in advance.
- Client ID Metadata Documents let agents with no prior relationship identify themselves without registering. Tokens are bound to one resource, and every request checks the signature, the audience and the expiry.
- Scopes follow what people understand. Ask for little, and step up with a 403 `insufficient_scope` challenge when a risky action needs more. Give members a "Connected agents" page where they can see and disconnect agents.
- OAuth says that a person allowed an application to act. Web Bot Auth (Chapter 4) says who operates the agent. A booking site wants both answers.
- "Consent" means three things: a lawful basis, authority for this action, and acceptance of the terms. Decide per step which ones an agent may complete alone.
- Bring the person back with a confirmation page on your own site, with MCP's URL-mode requests (never form mode for sensitive data), and with `consequentialHint` and the page's own confirmation in WebMCP. Tell the guest what happened, by email and on one page.
- The agent-safe checkout works with or without a protocol: the server quotes, the quote has an identity and an expiry, the decision happens on your page, the form can add but not change, and the agent learns the outcome. Never let an agent handle card numbers.
- A shop can offer two ways to buy, in-page tools and a protocol checkout such as UCP. On Shopify they share one checkout. UCP requires a trusted UI unless AP2 mandates are used, and no specification yet says which record a dispute relies on, so keep one order history across both channels.

[^ch11-1]: “Authorization”, Model Context Protocol specification, version 2026-07-28, https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization (retrieved November 2026).
[^ch11-2]: “The OAuth 2.1 Authorization Framework”, draft-ietf-oauth-v2-1-17, IETF Datatracker, https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/ (retrieved November 2026).
[^ch11-3]: M. Jones, P. Hunt, A. Parecki, “OAuth 2.0 Protected Resource Metadata”, RFC 9728, April 2025, https://www.rfc-editor.org/rfc/rfc9728 (retrieved November 2026).
[^ch11-4]: “Authorization Server Discovery”, Model Context Protocol specification, version 2026-07-28, https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/authorization-server-discovery (retrieved November 2026).
[^ch11-5]: “Security Considerations”, Model Context Protocol specification, version 2026-07-28, https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/security-considerations (retrieved November 2026).
[^ch11-6]: “Authentication”, OpenAI developer documentation for plugins, https://developers.openai.com/plugins/build/auth.md (retrieved November 2026).
[^ch11-7]: “Client Registration”, Model Context Protocol specification, version 2026-07-28, https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/client-registration (retrieved November 2026).
[^ch11-8]: “Security Considerations”, sections “Open Redirection” and “Client ID Metadata Document Security”, Model Context Protocol specification, version 2026-07-28, https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/security-considerations (retrieved November 2026).
[^ch11-9]: "ICO Shares Early Views on Agentic AI & Data Protection," Global Policy Watch, February 2026, https://www.globalpolicywatch.com/2026/02/ico-shares-early-views-on-agentic-ai-data-protection/ (retrieved November 2026).
[^ch11-10]: "Innovación y tecnología," Agencia Española de Protección de Datos, listing "Inteligencia Artificial Agéntica desde la perspectiva de Protección de Datos [feb 2026]," https://www.aepd.es/areas-de-actuacion/innovacion-y-tecnologia (retrieved November 2026).
[^ch11-11]: "Spanish Supervisory Authority Issues Detailed Guidance on Agentic AI and GDPR Compliance," Inside Privacy (Covington), https://www.insideprivacy.com/artificial-intelligence/spanish-supervisory-authority-issues-detailed-guidance-on-agentic-ai-and-gdpr-compliance/ (retrieved November 2026).
[^ch11-12]: "Art. 5 GDPR – Principles relating to processing of personal data," gdpr-info.eu, https://gdpr-info.eu/art-5-gdpr/ (retrieved November 2026).
[^ch11-13]: "Multi Round-Trip Requests," Model Context Protocol specification 2026-07-28, https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/mrtr (retrieved November 2026).
[^ch11-14]: "Elicitation," Model Context Protocol specification 2026-07-28, https://modelcontextprotocol.io/specification/2026-07-28/client/elicitation (retrieved November 2026).
[^ch11-15]: "WebMCP," Draft Community Group Report, 27 October 2026, https://webmachinelearning.github.io/webmcp/ (retrieved November 2026).
[^ch11-16]: "Replace requestUserInteraction with requestUserInput," webmachinelearning/webmcp pull request 204, GitHub, updated 29 October 2026, https://github.com/webmachinelearning/webmcp/pull/204 (retrieved November 2026).
[^ch11-17]: "WebMCP tool security," Chrome for Developers, updated 1 September 2026, https://developer.chrome.com/docs/ai/webmcp/secure-tools (retrieved November 2026).
[^ch11-18]: “AI Insights: Adoption of AI agent standards”, Cloudflare Radar, https://radar.cloudflare.com/ai-insights#adoption-of-ai-agent-standards, data dated 2 November 2026, including the Ecommerce and Travel domain categories (retrieved November 2026).
[^ch11-19]: “Universal Commerce Protocol”, ucp.dev, https://ucp.dev/ (retrieved November 2026).
[^ch11-20]: “Overview”, Universal Commerce Protocol specification, https://ucp.dev/specification/overview/ (retrieved November 2026).
[^ch11-21]: Universal-Commerce-Protocol/ucp, GitHub, https://github.com/Universal-Commerce-Protocol/ucp, release v2026-08-25 and commit c9a1395 “feat: Introduce Lodging Booking Capability and Cancellation Policy Extension (#780)”, 24 September 2026 (retrieved November 2026).
[^ch11-22]: “Booking Capability”, Universal Commerce Protocol specification (draft), https://ucp.dev/draft/specification/lodging/booking/, read at repository commit 58c7ab9 of 31 October 2026 (retrieved November 2026).
[^ch11-23]: “Regulatory Technical Standards on strong customer authentication and secure communication under PSD2”, European Banking Authority, https://www.eba.europa.eu/regulation-and-policy/payment-services-and-electronic-money/regulatory-technical-standards-on-strong-customer-authentication-and-secure-communication-under-psd2 (retrieved November 2026).
[^ch11-24]: Francesco Marinoni Moretto, feedback on this book to the author (November 2026), and his Agentic Standards Map, entries “Universal Commerce Protocol (UCP)” (verified 2 November 2026) <https://frmoretto.github.io/agentic-standards-map/entries/ucp.html> and “Browser vendor positions on WebMCP” (verified 13 October 2026) <https://frmoretto.github.io/agentic-standards-map/entries/browsers-webmcp.html>, used as a secondary source next to the primary sources above.
[^ch11-25]: `/.well-known/ucp` fetched on 4 November 2026 (20:39 UTC) from allbirds.com, kyliecosmetics.com and www.tentree.com: HTTP 200, `application/json`, each a UCP profile for version 2026-08-25 with a `dev.ucp.shopping` service over MCP (an endpoint under `/api/ucp/mcp` on the store’s myshopify.com host) and an embedded transport, and capabilities including `dev.ucp.shopping.checkout`, `.cart`, `.order` and `.buyer_consent`. No AP2 mandates capability in any of the three. A fourth storefront tried the same day returned 404.
[^ch11-26]: Shopify developer changelog, “WebMCP support for checkout” (28 September 2026) <https://shopify.dev/changelog/posts/webmcp-support-for-checkout>, and Shopify documentation, “Checkout WebMCP” <https://shopify.dev/docs/agents/carts-and-checkout/checkout-webmcp>, both read on 4 November 2026.
[^ch11-27]: Universal Commerce Protocol specification, version 2026-08-25, read on 4 November 2026: “Checkout Capability” (overview, status values, `continue_url` handoff, `requires_buyer_review`) <https://ucp.dev/2026-08-25/specification/shopping/checkout/>, “Order” (`checkout_id`, adjustments) <https://ucp.dev/2026-08-25/specification/shopping/order/>, “Buyer Consent Extension” <https://ucp.dev/2026-08-25/specification/shopping/extensions/buyer-consent/> and “AP2 Mandates” <https://ucp.dev/2026-08-25/specification/payment/extensions/ap2-mandates/>.
[^ch11-28]: w3c/strategy issue #576, “Agentic Web Working Group” charter refinement, comments of 26 October 2026 by Ilya Grigorik (Shopify) and by Francesco Marinoni Moretto (GitHub: frmoretto), and webmachinelearning/webmcp issue #365, “Spec & generalize `agentInvoked`: signal events an agent originates” (open on 2 November 2026). <https://github.com/w3c/strategy/issues/576>
